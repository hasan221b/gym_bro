// ─── State ───────────────────────────────────────────────────────
let allExercises   = [];       // full list fetched once
let activeMuscleFiler = '';    // current muscle chip selection
const PAGE_SIZE    = 40;       // cards rendered per batch
let renderedCount  = 0;

// ─── Main render (called on every nav tap) ───────────────────────
async function renderExercises() {
    const el = document.getElementById('page-exercises');

    // First visit — fetch and build the full UI
    if (allExercises.length === 0) {
        el.innerHTML = `<div class="loader">Loading exercises...</div>`;
        try {
            allExercises = await api.getExercises();
        } catch (e) {
            el.innerHTML = `<div class="empty-state"><div class="empty-state-text">Failed to load exercises.</div></div>`;
            return;
        }
        buildExerciseUI(el);
        return;
    }

    // Subsequent visits — already rendered, just reset the search box
    const searchInput = document.getElementById('exercise-search');
    if (searchInput) searchInput.value = '';
    applyFilters();
}

// ─── Build the full UI skeleton once ─────────────────────────────
function buildExerciseUI(el) {
    activeMuscleFiler = '';
    el.innerHTML = `
        <div class="section-header">
            <div class="section-title">Exercises</div>
            <span class="badge" id="exercise-count">${allExercises.length}</span>
        </div>

        <input class="input" id="exercise-search"
               placeholder="Search exercises…"
               style="margin-bottom:12px"
               oninput="applyFilters()" />

        <div class="chips" id="muscle-chips">
            <div class="chip active"        onclick="setMuscleFilter('', this)">All</div>
            <div class="chip" onclick="setMuscleFilter('chest', this)">Chest</div>
            <div class="chip" onclick="setMuscleFilter('back', this)">Back</div>
            <div class="chip" onclick="setMuscleFilter('shoulders', this)">Shoulders</div>
            <div class="chip" onclick="setMuscleFilter('arms', this)">Arms</div>
            <div class="chip" onclick="setMuscleFilter('legs', this)">Legs</div>
            <div class="chip" onclick="setMuscleFilter('abs', this)">Abs</div>
        </div>

        <div id="exercise-list"></div>
        <button id="load-more-btn" class="btn btn-secondary" style="margin-top:8px;display:none"
                onclick="renderMoreExercises()">Load more</button>
    `;

    applyFilters();
}

// ─── Filter (search + muscle) — runs client-side only ────────────
function applyFilters() {
    const query  = (document.getElementById('exercise-search')?.value ?? '').toLowerCase();
    const muscle = activeMuscleFiler;

    const filtered = allExercises.filter(e => {
        const matchesSearch = !query || e.name.toLowerCase().includes(query);
        const matchesMuscle = !muscle || e.primary_muscles.includes(muscle);
        return matchesSearch && matchesMuscle;
    });

    document.getElementById('exercise-count').textContent = filtered.length;

    // Store filtered list on the DOM so renderMoreExercises can reach it
    document.getElementById('exercise-list')._filtered = filtered;
    renderedCount = 0;
    renderMoreExercises();
}

// ─── Chip selection ───────────────────────────────────────────────
function setMuscleFilter(muscle, chipEl) {
    document.querySelectorAll('#muscle-chips .chip').forEach(c => c.classList.remove('active'));
    chipEl.classList.add('active');
    activeMuscleFiler = muscle;
    applyFilters();
}

// ─── Paginated render ─────────────────────────────────────────────
function renderMoreExercises() {
    const listEl   = document.getElementById('exercise-list');
    const moreBtn  = document.getElementById('load-more-btn');
    const filtered = listEl._filtered ?? allExercises;

    if (renderedCount === 0) listEl.innerHTML = '';

    const slice = filtered.slice(renderedCount, renderedCount + PAGE_SIZE);
    listEl.insertAdjacentHTML('beforeend', slice.map(exerciseCard).join(''));
    renderedCount += slice.length;

    if (filtered.length === 0) {
        listEl.innerHTML = `<div class="empty-state"><div class="empty-state-text">No exercises found.</div></div>`;
    }

    moreBtn.style.display = renderedCount < filtered.length ? 'flex' : 'none';
}

// ─── Single card HTML ─────────────────────────────────────────────
function exerciseCard(e) {
    return `
        <div class="card" onclick="showExerciseDetail('${e.id}')">
            <div class="exercise-item" style="padding:0">
                <div>
                    <div class="exercise-name">${e.name}</div>
                    <div class="exercise-meta">
                        ${e.primary_muscles.map(m => m.replace('_', ' ')).join(', ')}
                        ${e.equipment ? ` · ${e.equipment.replace('_', ' ')}` : ''}
                    </div>
                </div>
                <span class="badge">${e.level}</span>
            </div>
        </div>`;
}

// ─── Detail modal ─────────────────────────────────────────────────
function showExerciseDetail(exerciseId) {
    const ex = allExercises.find(e => e.id === exerciseId);
    if (!ex) return;

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
        <div class="modal">
            <div class="modal-title">${ex.name}</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
                <span class="badge badge-accent">${ex.level}</span>
                ${ex.force    ? `<span class="badge">${ex.force}</span>` : ''}
                ${ex.equipment ? `<span class="badge">${ex.equipment.replace('_',' ')}</span>` : ''}
            </div>
            <div style="margin-bottom:10px">
                <div class="form-label">Primary Muscles</div>
                <div style="color:var(--text)">${ex.primary_muscles.map(m => m.replace('_',' ')).join(', ')}</div>
            </div>
            ${ex.secondary_muscles?.length ? `
                <div style="margin-bottom:10px">
                    <div class="form-label">Secondary Muscles</div>
                    <div style="color:var(--text-muted)">${ex.secondary_muscles.map(m => m.replace('_',' ')).join(', ')}</div>
                </div>` : ''}
            ${ex.instructions ? `
                <div style="margin-bottom:16px">
                    <div class="form-label">Instructions</div>
                    <div style="color:var(--text-muted);font-size:13px;line-height:1.6">${ex.instructions}</div>
                </div>` : ''}
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
}
