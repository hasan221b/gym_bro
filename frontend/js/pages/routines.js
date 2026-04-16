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
                    <div>
                        <div class="routine-card-name">${r.name}</div>
                        <div class="routine-card-meta">${r.is_active ? '● Active' : '○ Inactive'}</div>
                    </div>
                    <div class="routine-card-arrow">›</div>
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

// ─── AI Routine Wizard ───────────────────────────────────────────
const AI_WIZARD_STEPS = [
    {
        key: 'primary_goal',
        question: "What is your primary goal right now?",
        hint: "e.g. build muscle, lose fat, improve endurance — and your deadline if any",
        type: 'text',
    },
    {
        key: 'age',
        question: "How old are you?",
        hint: "Enter your age in years, e.g. 25",
        type: 'text',
    },
    {
        key: 'height_cm',
        question: "What is your height?",
        hint: "Enter in cm, e.g. 178",
        type: 'text',
    },
    {
        key: 'weight_kg',
        question: "What is your current body weight?",
        hint: "Enter in kg, e.g. 82",
        type: 'text',
    },
    {
        key: 'training_availability',
        question: "How many days per week can you train, and for how long per session?",
        hint: "e.g. 4 days/week, 60 min each",
        type: 'text',
    },
    {
        key: 'recovery_and_sleep',
        question: "On a scale of 1–10, how beat up do you feel after a hard workout? And how many hours of sleep do you average?",
        hint: "e.g. 7/10 recovery, 7.5 hrs sleep",
        type: 'text',
    },
    {
        key: 'injuries',
        question: "Any past injuries, joint pain, or movement restrictions?",
        hint: "e.g. bad lower back, bad knees — or type 'None'",
        type: 'text',
    },
    {
        key: 'training_background',
        question: "What type of training have you done in the last 6 months?",
        hint: "e.g. bodybuilding 3x/week, CrossFit, running, nothing",
        type: 'text',
    },
    {
        key: 'training_preference',
        question: "Do you prefer training for performance, appearance, or fun?",
        hint: "",
        type: 'choice',
        choices: ['Performance', 'Appearance', 'Fun / Enjoyment'],
    },
];

const AIWizard = { step: 0, answers: {} };

function showAIWizard() {
    AIWizard.step = 0;
    AIWizard.answers = {};

    const overlay = document.createElement('div');
    overlay.id = 'ai-wizard-overlay';
    overlay.className = 'wizard-overlay';
    document.body.appendChild(overlay);

    renderWizardStep();
}

function renderWizardStep() {
    const overlay = document.getElementById('ai-wizard-overlay');
    const step = AI_WIZARD_STEPS[AIWizard.step];
    const total = AI_WIZARD_STEPS.length;
    const isLast = AIWizard.step === total - 1;

    overlay.innerHTML = `
        <div class="wizard">
            <button class="wizard-close" onclick="closeAIWizard()">✕</button>

            <div class="wizard-progress">
                <div class="wizard-progress-bar" style="width:${((AIWizard.step + 1) / total) * 100}%"></div>
            </div>
            <div class="wizard-step-label">Step ${AIWizard.step + 1} of ${total}</div>

            <div class="wizard-question">${step.question}</div>
            ${step.hint ? `<div class="wizard-hint">${step.hint}</div>` : ''}

            <div class="wizard-input-wrap">
                ${step.type === 'choice'
                    ? step.choices.map(c => `
                        <button class="wizard-choice-btn" onclick="selectWizardChoice(this, '${c}')">
                            ${c}
                        </button>`).join('')
                    : `<textarea class="wizard-textarea" id="wizard-input"
                            placeholder="Type your answer…"
                            rows="3">${AIWizard.answers[step.key] || ''}</textarea>`
                }
            </div>

            <div class="wizard-actions">
                ${AIWizard.step > 0
                    ? `<button class="btn btn-secondary" onclick="wizardBack()">← Back</button>`
                    : `<div></div>`
                }
                ${step.type !== 'choice'
                    ? `<button class="btn btn-primary" onclick="wizardNext()">
                            ${isLast ? 'Generate ✨' : 'Next →'}
                       </button>`
                    : ''
                }
            </div>
        </div>
    `;

    // Re-select saved choice if returning to a choice step
    if (step.type === 'choice' && AIWizard.answers[step.key]) {
        document.querySelectorAll('.wizard-choice-btn').forEach(btn => {
            if (btn.textContent.trim() === AIWizard.answers[step.key]) {
                btn.classList.add('wizard-choice-btn--active');
            }
        });
    }

    // Auto-focus textarea
    const ta = document.getElementById('wizard-input');
    if (ta) setTimeout(() => ta.focus(), 50);
}

function selectWizardChoice(btn, value) {
    document.querySelectorAll('.wizard-choice-btn').forEach(b => b.classList.remove('wizard-choice-btn--active'));
    btn.classList.add('wizard-choice-btn--active');
    AIWizard.answers[AI_WIZARD_STEPS[AIWizard.step].key] = value;

    // Auto-advance after short delay
    setTimeout(() => wizardNext(), 300);
}

function wizardNext() {
    const step = AI_WIZARD_STEPS[AIWizard.step];

    if (step.type === 'text') {
        const val = (document.getElementById('wizard-input')?.value || '').trim();
        if (!val) { showToast('Please enter an answer'); return; }
        AIWizard.answers[step.key] = val;
    }

    if (!AIWizard.answers[step.key]) { showToast('Please answer before continuing'); return; }

    if (AIWizard.step < AI_WIZARD_STEPS.length - 1) {
        AIWizard.step++;
        renderWizardStep();
    } else {
        runAIGeneration();
    }
}

function wizardBack() {
    if (AIWizard.step > 0) {
        AIWizard.step--;
        renderWizardStep();
    }
}

function closeAIWizard() {
    document.getElementById('ai-wizard-overlay')?.remove();
}

async function runAIGeneration() {
    const overlay = document.getElementById('ai-wizard-overlay');
    overlay.innerHTML = `
        <div class="wizard wizard--loading">
            <div class="wizard-loading-icon">✨</div>
            <div class="wizard-loading-title">Building your split…</div>
            <div class="wizard-loading-sub">Rex is analysing your profile and selecting exercises</div>
            <div class="chat-typing-indicator" style="justify-content:center;margin-top:16px">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;

    try {
        const res = await api.createRoutineAI(App.user.id, AIWizard.answers);
        const routine  = res?.routine;
        const days     = Array.isArray(routine?.days) ? routine.days
                       : Array.isArray(routine)       ? routine
                       : null;
        const fallback = res?.response || null;
        renderWizardResult(days, fallback);
    } catch (e) {
        renderWizardResult(null, null, e.message || 'Request failed');
    }
}

function renderWizardResult(days, fallback, error) {
    const overlay = document.getElementById('ai-wizard-overlay');

    if (error || (!days && !fallback)) {
        overlay.innerHTML = `
            <div class="wizard">
                <button class="wizard-close" onclick="closeAIWizard()">✕</button>
                <div class="wizard-question" style="color:var(--danger)">Something went wrong</div>
                <div class="wizard-hint">${error || 'No routine was generated. Please try again.'}</div>
                <div class="wizard-actions" style="margin-top:24px">
                    <div></div>
                    <button class="btn btn-primary" onclick="closeAIWizard(); showAIWizard()">Try Again</button>
                </div>
            </div>`;
        return;
    }

    AIWizard.generatedDays = days || [];

    const content = AIWizard.generatedDays.length
        ? AIWizard.generatedDays.map(d => `
            <div class="wizard-day-block">
                <div class="wizard-day-label">Day ${d.day} — ${d.focus}</div>
                ${d.exercises.map((ex, i) => `
                    <div class="wizard-ex-card">
                        <div class="wizard-ex-order">${i + 1}</div>
                        <div class="wizard-ex-info">
                            <div class="wizard-ex-name">${ex.name}</div>
                            <div class="wizard-ex-meta">
                                ${ex.planned_sets} sets × ${ex.planned_reps} reps
                                ${ex.planned_weight ? `@ ${ex.planned_weight}kg` : '· bodyweight'}
                                &nbsp;·&nbsp; ${ex.primary_muscles?.join(', ') || ''}
                            </div>
                        </div>
                    </div>`).join('')}
            </div>`).join('')
        : `<div class="wizard-hint" style="white-space:pre-wrap">${fallback}</div>`;

    overlay.innerHTML = `
        <div class="wizard wizard--result">
            <button class="wizard-close" onclick="closeAIWizard()">✕</button>
            <div class="wizard-result-title">Your AI Split ✨</div>
            <div class="wizard-ex-list">${content}</div>
            <div class="wizard-save-row">
                <input class="input" id="wizard-routine-name" placeholder="Name this split… e.g. Summer Cut" />
            </div>
            <div class="wizard-actions">
                <button class="btn btn-secondary" onclick="closeAIWizard(); showAIWizard()">Regenerate</button>
                <button class="btn btn-ai" onclick="saveAIRoutine(this)">Save Split</button>
            </div>
        </div>
    `;
}

async function saveAIRoutine(btn) {
    const splitName = document.getElementById('wizard-routine-name').value.trim();
    if (!splitName) { showToast('Give your split a name first'); return; }

    const days = AIWizard.generatedDays;
    if (!days?.length) { showToast('No days to save'); return; }

    btn.disabled = true;
    btn.textContent = 'Saving…';

    try {
        // 1. Delete old routines + fetch exercise map in parallel
        const [existing, allExercises] = await Promise.all([
            api.getRoutines(App.user.id),
            api.getExercises(),
        ]);
        await Promise.all(existing.map(r => api.deleteRoutine(r.id)));

        const nameToId = {};
        allExercises.forEach(e => { nameToId[e.name.toLowerCase()] = e.id; });

        // 2. Create all day routines in parallel
        const routines = await Promise.all(
            days.map(d => api.createRoutine(App.user.id, {
                name: `${splitName} — Day ${d.day} ${d.focus}`,
            }))
        );

        // 3. Add exercises to each routine in parallel
        let totalSkipped = 0;
        const addOps = [];
        routines.forEach((routine, i) => {
            for (const ex of days[i].exercises) {
                const exerciseId = nameToId[ex.name.toLowerCase()];
                if (!exerciseId) { totalSkipped++; continue; }
                addOps.push(api.addExerciseToRoutine(routine.id, {
                    exercise_id: exerciseId,
                    planned_sets: ex.planned_sets,
                    planned_reps: ex.planned_reps,
                    planned_weight: ex.planned_weight ?? null,
                }));
            }
        });
        await Promise.all(addOps);

        closeAIWizard();
        showToast(totalSkipped > 0
            ? `Split saved! (${totalSkipped} exercise${totalSkipped > 1 ? 's' : ''} not matched)`
            : `Split saved — ${days.length} day${days.length > 1 ? 's' : ''} created!`);
        renderRoutines();

    } catch (e) {
        showToast(e.message);
        btn.disabled = false;
        btn.textContent = 'Save Split';
    }
}
