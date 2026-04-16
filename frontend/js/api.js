const API_BASE = '/api/v1';

async function request(method, path, body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(API_BASE + path, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || 'Request failed');
    }
    if (res.status === 204) return null;
    return res.json();
}

const api = {
    // Users
    upsertUser: (data) => request('POST', '/users', data),
    getUser: (id) => request('GET', `/users/${id}`),

    // Exercises
    getExercises: (muscle = null, equipment = null) => {
        const params = new URLSearchParams();
        if (muscle) params.append('muscle', muscle);
        if (equipment) params.append('equipment', equipment);
        return request('GET', `/exercises?${params}`);
    },
    getExercise: (id) => request('GET', `/exercises/${id}`),
    createExercise: (userId, data) => request('POST', `/exercises?user_id=${userId}`, data),

    // Routines
    getRoutines: (userId) => request('GET', `/routines/user/${userId}`),
    getRoutine: (id) => request('GET', `/routines/${id}`),
    createRoutine: (userId, data) => request('POST', `/routines?user_id=${userId}`, data),
    updateRoutine: (id, data) => request('PATCH', `/routines/${id}`, data),
    deleteRoutine: (id) => request('DELETE', `/routines/${id}`),
    addExerciseToRoutine: (routineId, data) => request('POST', `/routines/${routineId}/exercises`, data),
    removeExerciseFromRoutine: (routineId, reId) => request('DELETE', `/routines/${routineId}/exercises/${reId}`),

    // Sessions
    startSession: (userId, data) => request('POST', `/sessions/start?user_id=${userId}`, data),
    getSession: (id) => request('GET', `/sessions/${id}`),
    logSet: (sessionId, data) => request('POST', `/sessions/${sessionId}/log`, data),
    completeSession: (id) => request('POST', `/sessions/${id}/complete`),
    cancelSession: (id) => request('POST', `/sessions/${id}/cancel`),

    // Progress
    getSummary: (userId, start, end) =>
        request('GET', `/progress/summary?user_id=${userId}&start_date=${start}&end_date=${end}`),
    getWorkoutCalendar: (userId, start, end) =>
        request('GET', `/progress/calendar?user_id=${userId}&start_date=${start}&end_date=${end}`),
    getExerciseProgress: (userId, exerciseId, start, end) =>
        request('GET', `/progress/exercise/${exerciseId}?user_id=${userId}&start_date=${start}&end_date=${end}`),
    getWorkoutFrequency: (userId, start, end) =>
        request('GET', `/progress/frequency?user_id=${userId}&start_date=${start}&end_date=${end}`),
    getMuscleVolume: (userId, start, end) =>
        request('GET', `/progress/muscles?user_id=${userId}&start_date=${start}&end_date=${end}`),
    getBodyMetricTrend: (userId, start, end) =>
        request('GET', `/progress/body?user_id=${userId}&start_date=${start}&end_date=${end}`),
    logBodyMetric: (userId, data) =>
        request('POST', `/progress/body?user_id=${userId}`, data),

    // Agent
    chat: (userId, message) =>
        request('POST', '/agent/chat', { user_id: userId, message }),

    review: (userId, days = 30) =>
        request('POST', '/agent/review', { user_id: userId, days }),

    createRoutineAI: (userId, answers) =>
        request('POST', '/agent/create-routine', { user_id: userId, answers }),
};
