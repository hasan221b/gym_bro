// ─── State ──────────────────────────────────────────────────────
const App = {
    user: null,
    currentPage: 'home',
};

// ─── Toast ──────────────────────────────────────────────────────
function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
}

// ─── Navigation ─────────────────────────────────────────────────
function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    document.getElementById(`page-${page}`).classList.remove('hidden');
    document.querySelector(`[data-page="${page}"]`).classList.add('active');

    App.currentPage = page;

    // Render the page
    const renders = {
        home: renderHome,
        routines: renderRoutines,
        session: renderSession,
        progress: renderProgress,
        exercises: renderExercises,
        chat: renderChat,
    };
    if (renders[page]) renders[page]();
}

// ─── Bottom Nav Listeners ────────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => navigateTo(btn.dataset.page));
});

// ─── Init ────────────────────────────────────────────────────────
async function init() {
    const tg = window.Telegram?.WebApp;

    if (tg) {
        tg.ready();
        tg.expand();

        const tgUser = tg.initDataUnsafe?.user;
        if (tgUser) {
            try {
                await api.upsertUser({
                    id: tgUser.id,
                    username: tgUser.username || null,
                    first_name: tgUser.first_name || null,
                    last_name: tgUser.last_name || null,
                });
                App.user = { id: tgUser.id, first_name: tgUser.first_name };
            } catch (e) {
                console.error('Failed to upsert user:', e);
            }
        }
    } else {
        // Dev fallback — use a test user
        App.user = { id: 123456789, first_name: 'Dev' };
        try {
            await api.upsertUser({ id: App.user.id, first_name: App.user.first_name });
        } catch (e) {}
    }

    if (App.user) {
        document.getElementById('header-user').textContent = `Hi, ${App.user.first_name || 'Athlete'} 👋`;
    }

    navigateTo('home');
}

init();
