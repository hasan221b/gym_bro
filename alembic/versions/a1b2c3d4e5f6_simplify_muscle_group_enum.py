"""simplify_muscle_group_enum

Revision ID: a1b2c3d4e5f6
Revises: 836059c6807c
Create Date: 2026-04-09 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '836059c6807c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert ARRAY columns to text[] first so we can drop the old enum
    op.execute("ALTER TABLE exercises ALTER COLUMN primary_muscles TYPE text[] USING primary_muscles::text[]")
    op.execute("ALTER TABLE exercises ALTER COLUMN secondary_muscles TYPE text[] USING secondary_muscles::text[]")

    # Drop old enum
    op.execute("DROP TYPE IF EXISTS muscle_group_enum CASCADE")

    # Create new simplified enum
    op.execute("CREATE TYPE muscle_group_enum AS ENUM ('abs', 'legs', 'arms', 'shoulders', 'chest', 'back')")

    # Convert columns back (exercises table is empty at this point)
    op.execute("ALTER TABLE exercises ALTER COLUMN primary_muscles TYPE muscle_group_enum[] USING primary_muscles::muscle_group_enum[]")
    op.execute("ALTER TABLE exercises ALTER COLUMN secondary_muscles TYPE muscle_group_enum[] USING secondary_muscles::muscle_group_enum[]")


def downgrade() -> None:
    op.execute("ALTER TABLE exercises ALTER COLUMN primary_muscles TYPE text[] USING primary_muscles::text[]")
    op.execute("ALTER TABLE exercises ALTER COLUMN secondary_muscles TYPE text[] USING secondary_muscles::text[]")
    op.execute("DROP TYPE IF EXISTS muscle_group_enum CASCADE")
    op.execute("""
        CREATE TYPE muscle_group_enum AS ENUM (
            'abdominals','hamstrings','adductors','quadriceps','biceps',
            'shoulders','chest','middle_back','calves','glutes','lower_back',
            'lats','triceps','traps','forearms','neck','abductors'
        )
    """)
    op.execute("ALTER TABLE exercises ALTER COLUMN primary_muscles TYPE muscle_group_enum[] USING primary_muscles::muscle_group_enum[]")
    op.execute("ALTER TABLE exercises ALTER COLUMN secondary_muscles TYPE muscle_group_enum[] USING secondary_muscles::muscle_group_enum[]")
