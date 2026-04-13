async function renderHome() {
    const el = document.getElementById('page-home');
    el.innerHTML = `<div class="loader">Loading...</div>`;

    try {
        const today = new Date();
        const weekAgo = new Date(today - 7 * 24 * 60 * 60 * 1000);
        const fmt = d => d.toISOString().split('T')[0];

        const [routines, frequency] = await Promise.all([
            api.getRoutines(App.user.id),
            api.getWorkoutFrequency(App.user.id, fmt(weekAgo), fmt(today)),
        ]);

        const weekSessions = frequency.data.reduce((s, d) => s + d.session_count, 0);
        const weekVolume = frequency.data.reduce((s, d) => s + d.total_volume, 0);
        const activeRoutines = routines.filter(r => r.is_active).length;

        el.innerHTML = `
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-value">${weekSessions}</div>
                    <div class="stat-label">Sessions<br>This Week</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${activeRoutines}</div>
                    <div class="stat-label">Active<br>Routines</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${weekVolume > 0 ? (weekVolume / 1000).toFixed(1) + 'k' : '0'}</div>
                    <div class="stat-label">Volume<br>This Week</div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Your Routines</div>
                ${routines.length === 0 ? `
                    <div class="empty-state">
                        <div class="empty-state-icon">💪</div>
                        <div class="empty-state-text">No routines yet</div>
                        <button class="btn btn-primary" onclick="navigateTo('routines')">Create Routine</button>
                    </div>
                ` : routines.slice(0, 3).map(r => `
                    <div class="exercise-item">
                        <div>
                            <div class="exercise-name">${r.name}</div>
                            <div class="exercise-meta">${r.is_active ? '● Active' : '○ Inactive'}</div>
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="startSessionFromRoutine('${r.id}')">Start</button>
                    </div>
                `).join('')}
            </div>

            <button class="btn btn-secondary" onclick="navigateTo('session')">
                🏋️ Free Workout (No Routine)
            </button>
        `;
    } catch (e) {
        el.innerHTML = `<div class="empty-state"><div class="empty-state-text">Failed to load. Please try again.</div></div>`;
    }
}

async function startSessionFromRoutine(routineId) {
    try {
        const session = await api.startSession(App.user.id, { routine_id: routineId });
        App.activeSession = session;
        navigateTo('session');
        showToast('Session started!');
    } catch (e) {
        showToast(e.message);
    }
}
