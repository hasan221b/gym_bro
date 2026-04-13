let allExercises = [];

async function renderExercises() {
    const el = document.getElementById('page-exercises');
    el.innerHTML = `<div class="loader">Loading exercises...</div>`;

    try {
        allExercises = await api.getExercises();

        el.innerHTML = `
            <div class="section-header">
                <div class="section-title">Exercises</div>
                <span class="badge">${allExercises.length}</span>
            </div>

            <input class="input" id="exercise-search" placeholder="Search exercises..." oninput="filterExercises()" style="margin-bottom:12px" />

            <div class="chips" id="muscle-chips">
                <div class="chip active" onclick="filterByMuscle('', this)">All</div>
                <div class="chip" onclick="filterByMuscle('chest', this)">Chest</div>
                <div class="chip" onclick="filterByMuscle('biceps', this)">Biceps</div>
                <div class="chip" onclick="filterByMuscle('triceps', this)">Triceps</div>
                <div class="chip" onclick="filterByMuscle('shoulders', this)">Shoulders</div>
                <div class="chip" onclick="filterByMuscle('lats', this)">Back</div>
                <div class="chip" onclick="filterByMuscle('quadriceps', this)">Quads</div>
                <div class="chip" onclick="filterByMuscle('hamstrings', this)">Hamstrings</div>
                <div class="chip" onclick="filterByMuscle('glutes', this)">Glutes</div>
                <div class="chip" onclick="filterByMuscle('abdominals', this)">Abs</div>
            </div>

            <div id="exercise-list">
                ${renderExerciseList(allExercises)}
            </div>
        `;
    } catch (e) {
        el.innerHTML = `<div class="empty-state"><div class="empty-state-text">Failed to load exercises.</div></div>`;
    }
}

function renderExerciseList(exercises) {
    if (exercises.length === 0) {
        return `<div class="empty-state"><div class="empty-state-text">No exercises found.</div></div>`;
    }
    return exercises.map(e => `
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
        </div>
    `).join('');
}

function filterExercises() {
    const query = document.getElementById('exercise-search').value.toLowerCase();
    const filtered = allExercises.filter(e => e.name.toLowerCase().includes(query));
    document.getElementById('exercise-list').innerHTML = renderExerciseList(filtered);
}

async function filterByMuscle(muscle, chipEl) {
    document.querySelectorAll('#muscle-chips .chip').forEach(c => c.classList.remove('active'));
    chipEl.classList.add('active');

    if (!muscle) {
        document.getElementById('exercise-list').innerHTML = renderExerciseList(allExercises);
        return;
    }

    try {
        const filtered = await api.getExercises(muscle);
        document.getElementById('exercise-list').innerHTML = renderExerciseList(filtered);
    } catch (e) {
        showToast('Failed to filter');
    }
}

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
                ${ex.force ? `<span class="badge">${ex.force}</span>` : ''}
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
                </div>
            ` : ''}
            ${ex.instructions ? `
                <div style="margin-bottom:16px">
                    <div class="form-label">Instructions</div>
                    <div style="color:var(--text-muted);font-size:13px;line-height:1.6">${ex.instructions}</div>
                </div>
            ` : ''}
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
}
