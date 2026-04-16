// ─── Chat State ──────────────────────────────────────────────────
const Chat = {
    messages: [],   // { role: 'user'|'rex', text: string }
    busy: false,
    built: false,
    activeTab: 'chat',  // 'chat' | 'review' | 'create'
};

// ─── Render (called once per navigation) ────────────────────────
function renderChat() {
    const page = document.getElementById('page-chat');

    if (!Chat.built) {
        page.innerHTML = `
            <!-- Tab Bar -->
            <div id="chat-tab-bar">
                <button class="chat-tab chat-tab--active" data-tab="chat">
                    <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.03 2 11c0 2.64 1.16 5.01 3 6.71V22l4.5-2.5c.82.16 1.66.25 2.5.25 5.52 0 10-4.03 10-9S17.52 2 12 2z"/></svg>
                    Chat
                </button>
                <button class="chat-tab" data-tab="review">
                    <svg viewBox="0 0 24 24"><path d="M3 20h18M5 20V10m4 10V4m4 16v-7m4 7v-3"/></svg>
                    Review
                </button>
                <button class="chat-tab" data-tab="create">
                    <svg viewBox="0 0 24 24"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/></svg>
                    Create
                </button>
            </div>

            <!-- Chat Panel -->
            <div id="chat-panel">
                <div id="chat-messages"></div>
                <div id="chat-input-bar">
                    <input id="chat-input" class="input" type="text"
                           placeholder="Ask Rex anything…" autocomplete="off" />
                    <button id="chat-send" class="chat-send-btn" aria-label="Send">
                        <svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>
                    </button>
                </div>
            </div>

            <!-- Review Panel -->
            <div id="review-panel" class="hidden">
                <div id="review-controls">
                    <span class="review-label">Analyse last</span>
                    <div id="review-days-group">
                        <button class="review-days-btn" data-days="7">7d</button>
                        <button class="review-days-btn review-days-btn--active" data-days="30">30d</button>
                        <button class="review-days-btn" data-days="90">90d</button>
                    </div>
                    <button id="review-run-btn" class="btn btn--accent">Run Analysis</button>
                </div>
                <div id="review-output"></div>
            </div>

            <!-- Create Panel -->
            <div id="create-panel" class="hidden">
                <div id="create-panel-inner">
                    <div class="create-hero-icon">✨</div>
                    <div class="create-hero-title">AI Routine Builder</div>
                    <div class="create-hero-sub">
                        Answer a few questions and Rex will design a personalised
                        training split using your profile and goals.
                    </div>
                    <button class="btn btn-ai" onclick="showAIWizard()">
                        Build My Split
                    </button>
                    <div class="create-features">
                        <div class="create-feature">
                            <span class="create-feature-icon">🎯</span>
                            <span>Goal-based split selection</span>
                        </div>
                        <div class="create-feature">
                            <span class="create-feature-icon">⚡</span>
                            <span>Matched to your schedule</span>
                        </div>
                        <div class="create-feature">
                            <span class="create-feature-icon">🔄</span>
                            <span>Replaces your current routines</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // ── Tab switching ────────────────────────────────────────
        document.querySelectorAll('.chat-tab').forEach(tab => {
            tab.addEventListener('click', () => switchTab(tab.dataset.tab));
        });

        // ── Chat listeners ───────────────────────────────────────
        document.getElementById('chat-send').addEventListener('click', sendMessage);
        document.getElementById('chat-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
        });

        // ── Review listeners ─────────────────────────────────────
        document.querySelectorAll('.review-days-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.review-days-btn').forEach(b => b.classList.remove('review-days-btn--active'));
                btn.classList.add('review-days-btn--active');
            });
        });
        document.getElementById('review-run-btn').addEventListener('click', runReview);

        Chat.built = true;

        // Welcome bubble
        if (Chat.messages.length === 0) {
            appendBubble('rex', "Hey! I'm Rex, your AI fitness coach. Ask me about your progress, routines, or training — I'll pull your actual data.");
        }
    }

    scrollToBottom();
}

// ─── Tab Switch ──────────────────────────────────────────────────
function switchTab(tab) {
    Chat.activeTab = tab;

    document.querySelectorAll('.chat-tab').forEach(b => b.classList.remove('chat-tab--active'));
    document.querySelector(`[data-tab="${tab}"]`).classList.add('chat-tab--active');

    document.getElementById('chat-panel').classList.toggle('hidden', tab !== 'chat');
    document.getElementById('review-panel').classList.toggle('hidden', tab !== 'review');
    document.getElementById('create-panel').classList.toggle('hidden', tab !== 'create');

    if (tab === 'chat') scrollToBottom();
}

// ─── Send Chat Message ───────────────────────────────────────────
async function sendMessage() {
    if (Chat.busy) return;

    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    appendBubble('user', text);
    showTyping();
    Chat.busy = true;

    try {
        const res = await api.chat(App.user.id, text);
        hideTyping();
        appendBubble('rex', res.response ?? res.reply ?? 'No response.');
    } catch (err) {
        hideTyping();
        appendBubble('rex', `Something went wrong: ${err.message}`);
    } finally {
        Chat.busy = false;
        document.getElementById('chat-input')?.focus();
    }
}

// ─── Run Review ──────────────────────────────────────────────────
async function runReview() {
    if (Chat.busy) return;

    const activeBtn = document.querySelector('.review-days-btn--active');
    const days = activeBtn ? parseInt(activeBtn.dataset.days) : 30;

    const output  = document.getElementById('review-output');
    const runBtn  = document.getElementById('review-run-btn');

    output.innerHTML = `
        <div class="review-loading">
            <div class="chat-typing-indicator" style="justify-content:center">
                <span></span><span></span><span></span>
            </div>
            <p>Analysing your last ${days} days…</p>
        </div>`;

    runBtn.disabled = true;
    Chat.busy = true;

    try {
        const res = await api.review(App.user.id, days);
        const report = res.report ?? 'No report returned.';
        output.innerHTML = `<div class="review-report">${formatMessage(report)}</div>`;
    } catch (err) {
        output.innerHTML = `<div class="review-report review-report--error">Error: ${err.message}</div>`;
    } finally {
        runBtn.disabled = false;
        Chat.busy = false;
        output.scrollTop = 0;
    }
}

// ─── Bubble helpers ──────────────────────────────────────────────
function appendBubble(role, text) {
    Chat.messages.push({ role, text });

    const container = document.getElementById('chat-messages');
    if (!container) return;

    const wrap = document.createElement('div');
    wrap.className = `chat-bubble-wrap ${role === 'user' ? 'chat-bubble-wrap--user' : ''}`;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble chat-bubble--${role}`;
    bubble.innerHTML = formatMessage(text);

    wrap.appendChild(bubble);
    container.appendChild(wrap);
    scrollToBottom();
}

function showTyping() {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    const wrap = document.createElement('div');
    wrap.id = 'chat-typing';
    wrap.className = 'chat-bubble-wrap';
    wrap.innerHTML = `
        <div class="chat-bubble chat-bubble--rex chat-typing-indicator">
            <span></span><span></span><span></span>
        </div>`;
    container.appendChild(wrap);
    scrollToBottom();
}

function hideTyping() {
    document.getElementById('chat-typing')?.remove();
}

function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    if (container) container.scrollTop = container.scrollHeight;
}

// ─── Markdown-lite formatter ─────────────────────────────────────
function formatMessage(text) {
    return text
        .replace(/```[\s\S]*?```/g, m => `<pre>${escHtml(m.slice(3, -3).trim())}</pre>`)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/^## (.+)$/gm, '<p class="chat-heading">$1</p>')
        .replace(/^[-•] (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        .replace(/\n/g, '<br>');
}

function escHtml(str) {
    return str.replace(/[&<>"']/g, c =>
        ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
