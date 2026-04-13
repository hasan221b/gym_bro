async function renderSession() {
    const el = document.getElementById('page-session');

    // If there's an active session already, show logging UI
    if (App.activeSession) {
        await renderSessionLogger(App.activeSession.id);
        return;
    }

    el.innerHTML = `
        <div class="section-title" style="margin-bottom:16px">Start Workout</div>
        <div class="card">
            <div class="card-title">Pick a Routine</div>
            <div id="session-routine-list"><div class="loader">Loading...</div></div>
        </div>
        <div style="margin-top:12px">
            <button class="btn btn-secondary" onclick="startFreeSession()">
                🔥 Free Workout (No Routine)
            </button>
        </div>
    `;

    try {
        const routines = await api.getRoutines(App.user.id);
        const listEl = document.getElementById('session-routine-list');
        if (routines.length === 0) {
            listEl.innerHTML = `<div class="empty-state"><div class="empty-state-text">No routines yet.</div></div>`;
        } else {
            listEl.innerHTML = routines.filter(r => r.is_active).map(r => `
                <div class="exercise-item">
                    <div>
                        <div class="exercise-name">${r.name}</div>
                        <div class="exercise-meta">${r.description || ''}</div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="startSessionFromRoutine('${r.id}')">Go</button>
                </div>
            `).join('');
        }
    } catch (e) {
        document.getElementById('session-routine-list').innerHTML = `<div class="empty-state"><div class="empty-state-text">Failed to load.</div></div>`;
    }
}

async function startFreeSession() {
    try {
        const session = await api.startSession(App.user.id, {});
        App.activeSession = session;
        await renderSessionLogger(session.id);
        showToast('Session started!');
    } catch (e) {
        showToast(e.message);
    }
}

async function renderSessionLogger(sessionId) {
    const el = document.getElementById('page-session');
    el.innerHTML = `<div class="loader">Loading session...</div>`;

    try {
        const session = await api.getSession(sessionId);
        App.activeSession = session;

        // Group logs by exercise
        const logsByExercise = {};
        (session.session_logs || []).forEach(log => {
            if (!logsByExercise[log.exercise_id]) logsByExercise[log.exercise_id] = [];
            logsByExercise[log.exercise_id].push(log);
        });

        // Get exercises from routine if available
        let routineExercises = [];
        if (session.routine_id) {
            const routine = await api.getRoutine(session.routine_id);
            routineExercises = routine.routine_exercises || [];
        }

        el.innerHTML = `
            <div class="section-header">
                <div class="section-title">Active Session</div>
                <span class="badge" id="session-timer">00:00</span>
            </div>

            <div id="session-exercises">
                ${routineExercises.length > 0 ? routineExercises.map(re => `
                    <div class="card" id="ex-block-${re.exercise_id}">
                        <div class="exercise-name" style="margin-bottom:8px">${re.exercise.name}</div>
                        <div style="display:grid;grid-template-columns:32px 1fr 1fr 1fr 40px;gap:4px;margin-bottom:4px">
                            <div class="set-num" style="font-size:11px;color:var(--text-muted)">Set</div>
                            <div style="font-size:11px;color:var(--text-muted);text-align:center">Weight</div>
                            <div style="font-size:11px;color:var(--text-muted);text-align:center">Reps</div>
                            <div style="font-size:11px;color:var(--text-muted);text-align:center" title="Rate of Perceived Exertion: 1 (easy) → 10 (max effort). 8 = 2 reps left in tank.">RPE ⓘ</div>
                            <div></div>
                        </div>
                        ${Array.from({length: re.planned_sets}, (_, i) => `
                            <div class="set-row" id="set-${re.exercise_id}-${i+1}">
                                <div class="set-num">${i+1}</div>
                                <input class="set-input" type="number" placeholder="${re.planned_weight || 'kg'}" id="w-${re.exercise_id}-${i+1}" />
                                <input class="set-input" type="number" placeholder="${re.planned_reps}" id="r-${re.exercise_id}-${i+1}" />
                                <input class="set-input" type="number" placeholder="RPE" min="1" max="10" id="rpe-${re.exercise_id}-${i+1}" />
                                <button class="set-done-btn" onclick="logSet('${sessionId}','${re.exercise_id}',${i+1},${re.planned_reps},${re.planned_weight||0},this)">✓</button>
                            </div>
                        `).join('')}
                    </div>
                `).join('') : `
                    <div class="card">
                        <div class="card-title">Log a Set</div>
                        <div id="free-log-area">
                            <button class="btn btn-secondary" onclick="showLogSetModal('${sessionId}')">+ Add Set</button>
                        </div>
                    </div>
                `}
            </div>

            <div style="display:flex;gap:10px;margin-top:16px">
                <button class="btn btn-danger" style="flex:1" onclick="cancelSession('${sessionId}')">Cancel</button>
                <button class="btn btn-success" style="flex:2" onclick="completeSession('${sessionId}')">✓ Complete</button>
            </div>
        `;

        // Start timer
        startTimer(session.started_at);

    } catch (e) {
        el.innerHTML = `<div class="empty-state"><div class="empty-state-text">Failed to load session.</div></div>`;
    }
}

function startTimer(startedAt) {
    const start = startedAt ? new Date(startedAt) : new Date();
    const timerEl = document.getElementById('session-timer');
    if (!timerEl) return;

    const interval = setInterval(() => {
        if (!document.getElementById('session-timer')) { clearInterval(interval); return; }
        const diff = Math.floor((new Date() - start) / 1000);
        const m = String(Math.floor(diff / 60)).padStart(2, '0');
        const s = String(diff % 60).padStart(2, '0');
        timerEl.textContent = `${m}:${s}`;
    }, 1000);
}

async function logSet(sessionId, exerciseId, setNum, plannedReps, plannedWeight, btn) {
    const weight = parseFloat(document.getElementById(`w-${exerciseId}-${setNum}`)?.value) || null;
    const reps = parseInt(document.getElementById(`r-${exerciseId}-${setNum}`)?.value) || plannedReps;
    const rpe = parseInt(document.getElementById(`rpe-${exerciseId}-${setNum}`)?.value) || null;

    try {
        await api.logSet(sessionId, {
            exercise_id: exerciseId,
            set_number: setNum,
            set_type: 'working',
            planned_reps: plannedReps,
            planned_weight: plannedWeight || null,
            actual_reps: reps,
            actual_weight: weight,
            is_skipped: false,
            rpe: rpe,
        });
        btn.classList.add('done');
        btn.disabled = true;
    } catch (e) {
        showToast(e.message);
    }
}

async function completeSession(sessionId) {
    try {
        await api.completeSession(sessionId);
        App.activeSession = null;
        showToast('Workout complete! 🎉');
        navigateTo('home');
    } catch (e) {
        showToast(e.message);
    }
}

async function cancelSession(sessionId) {
    if (!confirm('Cancel this session?')) return;
    try {
        await api.cancelSession(sessionId);
        App.activeSession = null;
        showToast('Session cancelled');
        navigateTo('home');
    } catch (e) {
        showToast(e.message);
    }
}

function showLogSetModal(sessionId) {
    showToast('Select exercise and log your set');
}
