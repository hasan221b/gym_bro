async function renderRoutines() {
    const el = document.getElementById('page-routines');
    el.innerHTML = `<div class="loader">Loading...</div>`;

    try {
        const routines = await api.getRoutines(App.user.id);
        el.innerHTML = `
            <div class="section-header">
                <div class="section-title">My Routines</div>
                <button class="btn btn-primary btn-sm" onclick="showCreateRoutineModal()">+ New</button>
            </div>
            ${routines.length === 0 ? `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <div class="empty-state-text">No routines yet.<br>Create your first split!</div>
                    <button class="btn btn-primary" onclick="showCreateRoutineModal()">Create Routine</button>
                </div>
            ` : routines.map(r => `
                <div class="routine-card" onclick="showRoutineDetail('${r.id}')">
                    <div class="routine-card-name">${r.name}</div>
                    <div class="routine-card-meta">${r.description || 'No description'} &nbsp;·&nbsp; ${r.is_active ? '● Active' : '○ Inactive'}</div>
                </div>
            `).join('')}
        `;
    } catch (e) {
        el.innerHTML = `<div class="empty-state"><div class="empty-state-text">Failed to load routines.</div></div>`;
    }
}

function showCreateRoutineModal() {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
        <div class="modal">
            <div class="modal-title">New Routine</div>
            <div class="form-group">
                <label class="form-label">Name</label>
                <input class="input" id="routine-name" placeholder="e.g. Chest Day" />
            </div>
            <div class="form-group">
                <label class="form-label">Description (optional)</label>
                <input class="input" id="routine-desc" placeholder="e.g. Push muscles focus" />
            </div>
            <div style="display:flex;gap:10px;margin-top:8px">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="createRoutine(this)">Create</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

async function createRoutine(btn) {
    const name = document.getElementById('routine-name').value.trim();
    if (!name) { showToast('Name is required'); return; }
    const desc = document.getElementById('routine-desc').value.trim();

    try {
        btn.disabled = true;
        await api.createRoutine(App.user.id, { name, description: desc || null });
        document.querySelector('.modal-overlay').remove();
        showToast('Routine created!');
        renderRoutines();
    } catch (e) {
        showToast(e.message);
        btn.disabled = false;
    }
}

async function showRoutineDetail(routineId) {
    const el = document.getElementById('page-routines');
    el.innerHTML = `<div class="loader">Loading...</div>`;

    try {
        const routine = await api.getRoutine(routineId);
        const exercises = routine.routine_exercises || [];

        el.innerHTML = `
            <div class="section-header">
                <button class="btn btn-secondary btn-sm" onclick="renderRoutines()">← Back</button>
                <button class="btn btn-danger btn-sm" onclick="deleteRoutine('${routine.id}')">Delete</button>
            </div>

            <div class="card" style="margin-bottom:16px">
                <div style="font-size:20px;font-weight:800;margin-bottom:4px">${routine.name}</div>
                <div style="color:var(--text-muted);font-size:13px">${routine.description || ''}</div>
            </div>

            <div class="section-header">
                <div class="section-title">Exercises</div>
                <button class="btn btn-primary btn-sm" onclick="showAddExerciseModal('${routine.id}')">+ Add</button>
            </div>

            <div id="routine-exercises">
                ${exercises.length === 0 ? `
                    <div class="empty-state">
                        <div class="empty-state-text">No exercises yet.<br>Add your first exercise!</div>
                    </div>
                ` : exercises.map(re => `
                    <div class="card">
                        <div class="exercise-item" style="padding:0">
                            <div>
                                <div class="exercise-name">${re.exercise.name}</div>
                                <div class="exercise-meta">${re.planned_sets} sets × ${re.planned_reps} reps ${re.planned_weight ? `@ ${re.planned_weight}kg` : '(bodyweight)'}</div>
                            </div>
                            <button class="btn btn-danger btn-sm" onclick="removeExercise('${routine.id}','${re.id}')">✕</button>
                        </div>
                    </div>
                `).join('')}
            </div>

            <div style="margin-top:16px">
                <button class="btn btn-primary" onclick="startSessionFromRoutine('${routine.id}')">
                    🏋️ Start This Workout
                </button>
            </div>
        `;
    } catch (e) {
        el.innerHTML = `<div class="empty-state"><div class="empty-state-text">Failed to load routine.</div></div>`;
    }
}

async function removeExercise(routineId, reId) {
    try {
        await api.removeExerciseFromRoutine(routineId, reId);
        showToast('Exercise removed');
        showRoutineDetail(routineId);
    } catch (e) {
        showToast(e.message);
    }
}

async function deleteRoutine(routineId) {
    if (!confirm('Delete this routine?')) return;
    try {
        await api.deleteRoutine(routineId);
        showToast('Routine deleted');
        renderRoutines();
    } catch (e) {
        showToast(e.message);
    }
}

const MUSCLES = ['abs', 'legs', 'arms', 'shoulders', 'chest', 'back'];

async function showAddExerciseModal(routineId) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
        <div class="modal">
            <div class="modal-title">Add Exercise</div>

            <div class="form-group">
                <label class="form-label">Filter by Muscle</label>
                <select class="select" id="add-ex-muscle" onchange="filterModalExercises('${routineId}')">
                    <option value="">All muscles</option>
                    ${MUSCLES.map(m => `<option value="${m}">${m.replace(/_/g, ' ')}</option>`).join('')}
                </select>
            </div>

            <div class="form-group">
                <label class="form-label">Select Exercise</label>
                <select class="select" id="add-ex-select">
                    <option value="">Loading...</option>
                </select>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">
                <div class="form-group">
                    <label class="form-label">Sets</label>
                    <input class="input" id="add-ex-sets" type="number" value="3" min="1" />
                </div>
                <div class="form-group">
                    <label class="form-label">Reps</label>
                    <input class="input" id="add-ex-reps" type="number" value="10" min="1" />
                </div>
                <div class="form-group">
                    <label class="form-label">Weight (kg)</label>
                    <input class="input" id="add-ex-weight" type="number" placeholder="BW" />
                </div>
            </div>

            <div style="display:flex;gap:10px;margin-top:8px">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="addExerciseToRoutine('${routineId}', this)">Add</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    await loadModalExercises();
}

async function loadModalExercises(muscle = null) {
    const select = document.getElementById('add-ex-select');
    if (!select) return;
    select.innerHTML = `<option value="">Loading...</option>`;
    try {
        const exercises = await api.getExercises(muscle);
        if (exercises.length === 0) {
            select.innerHTML = `<option value="">No exercises found</option>`;
        } else {
            select.innerHTML = exercises.map(e => `<option value="${e.id}">${e.name}</option>`).join('');
        }
    } catch (e) {
        select.innerHTML = `<option value="">Failed to load</option>`;
        showToast('Failed to load exercises');
    }
}

async function filterModalExercises() {
    const muscle = document.getElementById('add-ex-muscle').value;
    await loadModalExercises(muscle || null);
}

async function addExerciseToRoutine(routineId, btn) {
    const exerciseId = document.getElementById('add-ex-select').value;
    const sets = parseInt(document.getElementById('add-ex-sets').value);
    const reps = parseInt(document.getElementById('add-ex-reps').value);
    const weight = document.getElementById('add-ex-weight').value;

    if (!exerciseId) { showToast('Select an exercise'); return; }

    try {
        btn.disabled = true;
        await api.addExerciseToRoutine(routineId, {
            exercise_id: exerciseId,
            planned_sets: sets,
            planned_reps: reps,
            planned_weight: weight ? parseFloat(weight) : null,
        });
        document.querySelector('.modal-overlay').remove();
        showToast('Exercise added!');
        showRoutineDetail(routineId);
    } catch (e) {
        showToast(e.message);
        btn.disabled = false;
    }
}
