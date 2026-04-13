let progressCharts = {};
let _calendarDate = new Date(); // current month shown in calendar

const MUSCLE_LABELS = { abs: 'ABS', legs: 'Legs', arms: 'Arms', shoulders: 'Shoulders', chest: 'Chest', back: 'Back' };

function destroyCharts() {
    Object.values(progressCharts).forEach(c => c.destroy());
    progressCharts = {};
}

function getDateRange(period) {
    const end = new Date();
    const start = new Date();
    if (period === 'week')    start.setDate(end.getDate() - 7);
    else if (period === 'month') start.setDate(end.getDate() - 30);
    else start.setDate(end.getDate() - 90);
    const fmt = d => d.toISOString().split('T')[0];
    return { start: fmt(start), end: fmt(end) };
}

async function renderProgress() {
    destroyCharts();
    _calendarDate = new Date();
    const el = document.getElementById('page-progress');
    el.innerHTML = `
        <div class="section-header">
            <div class="section-title">Progress</div>
        </div>
        <div class="chips" id="period-chips">
            <div class="chip active" onclick="changePeriod('week', this)">Week</div>
            <div class="chip" onclick="changePeriod('month', this)">Month</div>
            <div class="chip" onclick="changePeriod('3months', this)">3 Months</div>
        </div>

        <!-- Summary cards -->
        <div id="summary-cards" style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px">
            <div class="card" style="text-align:center;padding:12px 8px">
                <div style="font-size:22px;font-weight:800;color:var(--primary)" id="sum-sessions">—</div>
                <div style="font-size:11px;color:var(--text-muted)">Sessions</div>
            </div>
            <div class="card" style="text-align:center;padding:12px 8px">
                <div style="font-size:22px;font-weight:800;color:var(--primary)" id="sum-volume">—</div>
                <div style="font-size:11px;color:var(--text-muted)">Volume (kg)</div>
            </div>
            <div class="card" style="text-align:center;padding:12px 8px">
                <div style="font-size:22px;font-weight:800;color:var(--primary)" id="sum-streak">—</div>
                <div style="font-size:11px;color:var(--text-muted)">Day Streak 🔥</div>
            </div>
        </div>

        <!-- Frequency chart -->
        <div class="card">
            <div class="card-title">Workout Frequency</div>
            <div class="chart-container"><canvas id="chart-frequency"></canvas></div>
        </div>

        <!-- Radar chart -->
        <div class="card">
            <div class="card-title">Muscle Balance</div>
            <div class="chart-container"><canvas id="chart-radar"></canvas></div>
        </div>

        <!-- Muscle volume bar -->
        <div class="card">
            <div class="card-title">Muscle Group Volume</div>
            <div class="chart-container"><canvas id="chart-muscles"></canvas></div>
        </div>

        <!-- Exercise PR -->
        <div class="card">
            <div class="card-title">Exercise PR</div>
            <select class="select" id="pr-exercise-select" onchange="loadExercisePR()" style="margin-bottom:12px">
                <option value="">Select exercise...</option>
            </select>
            <div class="chart-container"><canvas id="chart-pr"></canvas></div>
        </div>

        <!-- Calendar -->
        <div class="card">
            <div class="card-title">Workout Calendar</div>
            <div id="calendar-nav" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <button class="btn btn-secondary btn-sm" onclick="shiftCalendar(-1)">‹</button>
                <span id="calendar-month-label" style="font-weight:700"></span>
                <button class="btn btn-secondary btn-sm" onclick="shiftCalendar(1)">›</button>
            </div>
            <div id="calendar-grid"></div>
        </div>

        <!-- Body weight -->
        <div class="card">
            <div class="card-title">Body Weight</div>
            <div style="display:flex;gap:8px;margin-bottom:12px">
                <input class="input" type="number" id="bw-input" placeholder="kg" step="0.1" style="flex:1" />
                <button class="btn btn-primary btn-sm" onclick="logBodyWeight()">Log</button>
            </div>
            <div class="chart-container"><canvas id="chart-body"></canvas></div>
        </div>
    `;

    await loadProgressData('week');
}

async function changePeriod(period, el) {
    document.querySelectorAll('#period-chips .chip').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    destroyCharts();
    await loadProgressData(period);
}

async function loadProgressData(period) {
    const { start, end } = getDateRange(period);

    // Calendar always shows current visible month
    renderCalendarGrid([]);

    const [summary, frequency, muscles, body] = await Promise.allSettled([
        api.getSummary(App.user.id, start, end),
        api.getWorkoutFrequency(App.user.id, start, end),
        api.getMuscleVolume(App.user.id, start, end),
        api.getBodyMetricTrend(App.user.id, start, end),
    ]);

    if (summary.status === 'fulfilled') {
        const s = summary.value;
        document.getElementById('sum-sessions').textContent = s.total_sessions;
        document.getElementById('sum-volume').textContent = Math.round(s.total_volume).toLocaleString();
        document.getElementById('sum-streak').textContent = s.current_streak;
    }

    if (frequency.status === 'fulfilled') drawFrequencyChart(frequency.value.data);
    if (muscles.status === 'fulfilled') {
        drawMuscleChart(muscles.value.data);
        drawRadarChart(muscles.value.data);
    }
    if (body.status === 'fulfilled') drawBodyChart(body.value.data);

    // Load calendar for visible month
    await refreshCalendar();

    // Populate exercise dropdown for PR chart
    loadPRExerciseList();
}

// ─── Frequency chart ────────────────────────────────────────────────────────

function drawFrequencyChart(data) {
    const ctx = document.getElementById('chart-frequency');
    if (!ctx) return;
    progressCharts.frequency = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.period_start),
            datasets: [{
                label: 'Sessions',
                data: data.map(d => d.session_count),
                backgroundColor: '#ff572288',
                borderColor: '#ff5722',
                borderWidth: 2,
                borderRadius: 6,
            }],
        },
        options: chartDefaults(),
    });
}

// ─── Radar chart ─────────────────────────────────────────────────────────────

function drawRadarChart(data) {
    const ctx = document.getElementById('chart-radar');
    if (!ctx) return;

    const setsMap = {};
    data.forEach(d => { setsMap[d.muscle_group] = (setsMap[d.muscle_group] || 0) + d.total_sets; });

    const keys = Object.keys(MUSCLE_LABELS);
    const labels = keys.map(k => MUSCLE_LABELS[k]);
    const values = keys.map(k => setsMap[k] || 0);

    if (progressCharts.radar) progressCharts.radar.destroy();
    progressCharts.radar = new Chart(ctx, {
        type: 'radar',
        data: {
            labels,
            datasets: [{
                label: 'Sets',
                data: values,
                borderColor: '#ff5722',
                backgroundColor: '#ff572233',
                pointBackgroundColor: '#ff5722',
                pointRadius: 4,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: { color: '#888', font: { size: 9 }, stepSize: 1 },
                    grid: { color: '#2a2a2a' },
                    angleLines: { color: '#2a2a2a' },
                    pointLabels: { color: '#ccc', font: { size: 11 } },
                },
            },
        },
    });
}

// ─── Muscle volume bar ───────────────────────────────────────────────────────

function drawMuscleChart(data) {
    const ctx = document.getElementById('chart-muscles');
    if (!ctx) return;
    const sorted = [...data].sort((a, b) => b.total_volume - a.total_volume).slice(0, 8);
    progressCharts.muscles = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(d => MUSCLE_LABELS[d.muscle_group] || d.muscle_group),
            datasets: [{
                label: 'Volume (kg)',
                data: sorted.map(d => Math.round(d.total_volume)),
                backgroundColor: '#ff572244',
                borderColor: '#ff5722',
                borderWidth: 2,
                borderRadius: 6,
            }],
        },
        options: { ...chartDefaults(), indexAxis: 'y' },
    });
}

// ─── Exercise PR chart ───────────────────────────────────────────────────────

async function loadPRExerciseList() {
    const select = document.getElementById('pr-exercise-select');
    if (!select) return;
    try {
        const exercises = await api.getExercises();
        select.innerHTML = `<option value="">Select exercise...</option>` +
            exercises.map(e => `<option value="${e.id}">${e.name}</option>`).join('');
    } catch (_) {}
}

async function loadExercisePR() {
    const exerciseId = document.getElementById('pr-exercise-select')?.value;
    if (!exerciseId) return;

    const period = document.querySelector('#period-chips .chip.active')?.textContent?.trim();
    const periodKey = period === 'Week' ? 'week' : period === 'Month' ? 'month' : '3months';
    const { start, end } = getDateRange(periodKey);

    try {
        const data = await api.getExerciseProgress(App.user.id, exerciseId, start, end);
        drawPRChart(data);
    } catch (_) {
        showToast('No data for this exercise');
    }
}

function drawPRChart(data) {
    const ctx = document.getElementById('chart-pr');
    if (!ctx) return;
    if (progressCharts.pr) progressCharts.pr.destroy();

    progressCharts.pr = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.data.map(d => d.period_start),
            datasets: [{
                label: `${data.exercise_name} — Max Weight (kg)`,
                data: data.data.map(d => d.max_weight),
                borderColor: '#ff5722',
                backgroundColor: '#ff572222',
                tension: 0.3,
                fill: true,
                pointRadius: 5,
                pointBackgroundColor: '#ff5722',
            }],
        },
        options: chartDefaults(),
    });
}

// ─── Calendar ────────────────────────────────────────────────────────────────

async function refreshCalendar() {
    const y = _calendarDate.getFullYear();
    const m = _calendarDate.getMonth();
    const start = `${y}-${String(m + 1).padStart(2, '0')}-01`;
    const lastDay = new Date(y, m + 1, 0).getDate();
    const end = `${y}-${String(m + 1).padStart(2, '0')}-${lastDay}`;

    try {
        const cal = await api.getWorkoutCalendar(App.user.id, start, end);
        renderCalendarGrid(cal.workout_dates);
    } catch (_) {
        renderCalendarGrid([]);
    }
}

async function shiftCalendar(delta) {
    _calendarDate.setMonth(_calendarDate.getMonth() + delta);
    await refreshCalendar();
}

function renderCalendarGrid(workoutDates) {
    const monthLabel = document.getElementById('calendar-month-label');
    const grid = document.getElementById('calendar-grid');
    if (!grid) return;

    const y = _calendarDate.getFullYear();
    const m = _calendarDate.getMonth();
    const workoutSet = new Set(workoutDates);

    if (monthLabel) {
        monthLabel.textContent = _calendarDate.toLocaleString('default', { month: 'long', year: 'numeric' });
    }

    const firstDay = new Date(y, m, 1).getDay(); // 0=Sun
    const daysInMonth = new Date(y, m + 1, 0).getDate();
    const today = new Date().toISOString().split('T')[0];

    const dayNames = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
    let html = `<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;text-align:center">`;

    // Day headers
    dayNames.forEach(d => {
        html += `<div style="font-size:10px;color:var(--text-muted);padding:2px 0">${d}</div>`;
    });

    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
        html += `<div></div>`;
    }

    // Day cells
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${y}-${String(m + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const isWorkout = workoutSet.has(dateStr);
        const isToday = dateStr === today;

        let style = `font-size:12px;padding:4px 2px;border-radius:6px;`;
        if (isWorkout) style += `background:var(--primary);color:#fff;font-weight:700;`;
        else if (isToday) style += `border:1px solid var(--primary);color:var(--primary);`;
        else style += `color:var(--text-muted);`;

        html += `<div style="${style}">${day}</div>`;
    }

    html += `</div>`;
    grid.innerHTML = html;
}

// ─── Body weight ─────────────────────────────────────────────────────────────

async function logBodyWeight() {
    const val = parseFloat(document.getElementById('bw-input')?.value);
    if (!val || val <= 0) { showToast('Enter a valid weight'); return; }
    try {
        await api.logBodyMetric(App.user.id, { weight_kg: val });
        document.getElementById('bw-input').value = '';
        showToast('Weight logged!');
        // Refresh body chart
        const period = document.querySelector('#period-chips .chip.active')?.textContent?.trim();
        const periodKey = period === 'Week' ? 'week' : period === 'Month' ? 'month' : '3months';
        const { start, end } = getDateRange(periodKey);
        const body = await api.getBodyMetricTrend(App.user.id, start, end);
        if (progressCharts.body) progressCharts.body.destroy();
        drawBodyChart(body.data);
    } catch (e) {
        showToast(e.message);
    }
}

function drawBodyChart(data) {
    const ctx = document.getElementById('chart-body');
    if (!ctx) return;
    progressCharts.body = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.recorded_at),
            datasets: [{
                label: 'Weight (kg)',
                data: data.map(d => d.weight_kg),
                borderColor: '#ff5722',
                backgroundColor: '#ff572222',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: '#ff5722',
            }],
        },
        options: chartDefaults(),
    });
}

// ─── Shared chart options ─────────────────────────────────────────────────────

function chartDefaults() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#888', font: { size: 11 } } } },
        scales: {
            x: { ticks: { color: '#888', font: { size: 10 } }, grid: { color: '#2a2a2a' } },
            y: { ticks: { color: '#888', font: { size: 10 } }, grid: { color: '#2a2a2a' } },
        },
    };
}
