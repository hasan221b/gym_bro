"""
Dynamically builds the schema section of the Rex prompt
by introspecting the live PostgreSQL database at agent load time.

To add/remove tables from the agent's knowledge, edit WHITELISTED_TABLES.
To hide a column from the agent, add it to HIDDEN_COLUMNS.
"""

import os
import psycopg2

# ── Config ────────────────────────────────────────────────────────────────────

WHITELISTED_TABLES: set[str] = {
    "users",
    "exercises",
    "routines",
    "routine_exercises",
    "workout_sessions",
    "session_logs",
    "user_body_metrics",
}

HIDDEN_COLUMNS: set[str] = set()

# ── Internals ─────────────────────────────────────────────────────────────────

_schema_cache: str | None = None


def _get_raw_url() -> str:
    """Return a psycopg2-compatible URL from the environment."""
    url = os.environ["DATABASE_URL"]
    for prefix in ("postgresql+asyncpg://", "postgresql+psycopg2://"):
        if url.startswith(prefix):
            url = "postgresql://" + url[len(prefix):]
    return url


def _fetch_schema() -> str:
    conn = psycopg2.connect(_get_raw_url())
    try:
        cur = conn.cursor()

        # ── 1. Columns ────────────────────────────────────────────────────────
        cur.execute(
            """
            SELECT
                c.table_name,
                c.column_name,
                c.data_type,
                c.udt_name,
                c.is_nullable,
                c.column_default
            FROM information_schema.columns c
            WHERE c.table_schema = 'public'
              AND c.table_name   = ANY(%s)
            ORDER BY c.table_name, c.ordinal_position
            """,
            (list(WHITELISTED_TABLES),),
        )
        col_rows = cur.fetchall()

        # ── 2. Primary keys ───────────────────────────────────────────────────
        cur.execute(
            """
            SELECT kcu.table_name, kcu.column_name
            FROM information_schema.table_constraints  tc
            JOIN information_schema.key_column_usage   kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema    = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema    = 'public'
              AND kcu.table_name     = ANY(%s)
            """,
            (list(WHITELISTED_TABLES),),
        )
        pk_set: set[tuple] = {(r[0], r[1]) for r in cur.fetchall()}

        # ── 3. Foreign keys ───────────────────────────────────────────────────
        cur.execute(
            """
            SELECT
                kcu.table_name,
                kcu.column_name,
                ccu.table_name  AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints   tc
            JOIN information_schema.key_column_usage    kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema    = kcu.table_schema
            JOIN information_schema.referential_constraints rc
              ON tc.constraint_name = rc.constraint_name
             AND tc.table_schema    = rc.constraint_schema
            JOIN information_schema.constraint_column_usage ccu
              ON rc.unique_constraint_name   = ccu.constraint_name
             AND rc.unique_constraint_schema = ccu.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema    = 'public'
              AND kcu.table_name     = ANY(%s)
            """,
            (list(WHITELISTED_TABLES),),
        )
        fk_map: dict[tuple, str] = {
            (r[0], r[1]): f"{r[2]}.{r[3]}" for r in cur.fetchall()
        }

        # ── 4. Enum values ────────────────────────────────────────────────────
        cur.execute(
            """
            SELECT t.typname, e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            ORDER BY t.typname, e.enumsortorder
            """
        )
        enums: dict[str, list[str]] = {}
        for typname, label in cur.fetchall():
            enums.setdefault(typname, []).append(label)

    finally:
        conn.close()

    # ── Format ────────────────────────────────────────────────────────────────
    tables: dict[str, list] = {}
    for table_name, col_name, data_type, udt_name, is_nullable, col_default in col_rows:
        if col_name in HIDDEN_COLUMNS:
            continue
        tables.setdefault(table_name, []).append(
            (table_name, col_name, data_type, udt_name, is_nullable, col_default)
        )

    lines: list[str] = ["## SCHEMA:"]

    for table_name, cols in tables.items():
        lines.append(f"\nTable: {table_name}")
        for (tbl, col_name, data_type, udt_name, is_nullable, col_default) in cols:
            display_type = udt_name if data_type == "USER-DEFINED" else data_type

            parts: list[str] = [display_type]
            if (tbl, col_name) in pk_set:
                parts.append("PK")
            fk_target = fk_map.get((tbl, col_name))
            if fk_target:
                parts.append(f"FK → {fk_target}")
            if is_nullable == "NO":
                parts.append("NOT NULL")
            if col_default:
                default_clean = col_default.split("::")[0].strip("'")
                parts.append(f"DEFAULT={default_clean}")

            lines.append(f"  {col_name} ({', '.join(parts)})")

    # Only show enums used by whitelisted tables
    used_enum_names = {
        udt_name
        for (_, _, data_type, udt_name, _, _) in col_rows
        if data_type == "USER-DEFINED"
    }
    relevant_enums = {k: v for k, v in enums.items() if k in used_enum_names}

    if relevant_enums:
        lines.append("\n## ENUMS:")
        for enum_name, values in relevant_enums.items():
            lines.append(f"  {enum_name}: {values}")

    return "\n".join(lines)


def build_schema() -> str:
    """Return the full schema string, fetching from DB once and caching."""
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = _fetch_schema()
    return _schema_cache
