const API_BASE = window.location.origin;
let sessionId = null;
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const newChatBtn = document.getElementById('newChatBtn');

function generateSessionId() {
    return 'sess_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
    });
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

function formatAnswer(text) {
    let formatted = escapeHtml(text);

    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    formatted = '<p>' + formatted + '</p>';

    formatted = formatted.replace(
        /(https?:\/\/[^\s<)]+)/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );

    formatted = formatted.replace(
        /\*\*(.*?)\*\*/g,
        '<strong>$1</strong>'
    );

    return formatted;
}

function addUserMessage(text) {
    const welcome = document.getElementById('welcomeMessage');
    if (welcome) welcome.remove();

    const messageEl = document.createElement('div');
    messageEl.className = 'message user';
    messageEl.innerHTML = `
        <div class="message-avatar">U</div>
        <div class="message-content">
            <div class="message-bubble">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(messageEl);
    scrollToBottom();
}

function addBotMessage(data) {
    const existing = chatMessages.querySelector('.typing-wrapper');
    if (existing) existing.remove();

    const messageEl = document.createElement('div');
    messageEl.className = 'message bot';

    let metaHtml = '';
    if (data.memory_used) {
        const hintText = data.memory_hint ? escapeHtml(data.memory_hint) : 'Using conversation context';
        metaHtml += `
            <span class="memory-badge" title="${hintText}">
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 13l3-3M5 10a5 5 0 119-1"/><circle cx="12" cy="4" r="2"/></svg>
                Memory Active
            </span>
        `;
    }

    let sourcesHtml = '';
    if (data.sources && data.sources.length > 0) {
        const uniqueSources = [];
        const seen = new Set();
        for (const s of data.sources) {
            if (!seen.has(s.faq_id)) {
                seen.add(s.faq_id);
                uniqueSources.push(s);
            }
        }

        const linksHtml = uniqueSources.map(s => `
            <a class="source-link" href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer">
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 10l4-4"/><path d="M8.5 3.5l2.1-.6a2 2 0 012.5 2.5l-.6 2.1M7.5 12.5l-2.1.6a2 2 0 01-2.5-2.5l.6-2.1"/></svg>
                ${escapeHtml(s.title)}
            </a>
        `).join('');

        sourcesHtml = `
            <div class="sources">
                <div class="sources-label">Sources</div>
                ${linksHtml}
            </div>
        `;
    }

    messageEl.innerHTML = `
        <div class="message-avatar">E</div>
        <div class="message-content">
            <div class="message-bubble">${formatAnswer(data.answer)}</div>
            <div class="message-meta">
                ${metaHtml}
            </div>
            ${sourcesHtml}
        </div>
    `;
    chatMessages.appendChild(messageEl);
    scrollToBottom();
}

function addTypingIndicator() {
    const wrapper = document.createElement('div');
    wrapper.className = 'message bot typing-wrapper';
    wrapper.innerHTML = `
        <div class="message-avatar">E</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

function addErrorMessage(text) {
    const existing = chatMessages.querySelector('.typing-wrapper');
    if (existing) existing.remove();

    const messageEl = document.createElement('div');
    messageEl.className = 'message bot';
    messageEl.innerHTML = `
        <div class="message-avatar">E</div>
        <div class="message-content">
            <div class="error-message">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(messageEl);
    scrollToBottom();
}

async function sendMessage(text) {
    if (!text.trim()) return;

    if (!sessionId) {
        sessionId = generateSessionId();
    }

    addUserMessage(text);
    chatInput.value = '';
    sendButton.disabled = true;
    addTypingIndicator();

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                session_id: sessionId,
            }),
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || 'Something went wrong. Please try again.');
        }

        const data = await response.json();
        sessionId = data.session_id;
        addBotMessage(data);
    } catch (error) {
        if (error.name === 'AbortError') {
            addErrorMessage('Request timed out. Please try again.');
        } else {
            addErrorMessage(error.message || "I couldn't process that. Please try again.");
        }
    } finally {
        sendButton.disabled = false;
        chatInput.focus();
    }
}

function sendQuickAction(text) {
    chatInput.value = text;
    sendMessage(text);
}

function startNewChat() {
    sessionId = null;
    chatMessages.innerHTML = '';

    const welcome = document.createElement('div');
    welcome.className = 'welcome-message';
    welcome.id = 'welcomeMessage';
    welcome.innerHTML = `
        <div class="welcome-icon">
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="56" height="56" rx="16" fill="#EEF2FF"/>
                <path d="M16 28C16 22.4772 20.4772 18 26 18H30C35.5228 18 40 22.4772 40 28V33C40 35.7614 37.7614 38 35 38H21C18.2386 38 16 35.7614 16 33V28Z" fill="#4F46E5" opacity="0.15"/>
                <circle cx="24" cy="28" r="2" fill="#4F46E5"/>
                <circle cx="32" cy="28" r="2" fill="#4F46E5"/>
                <path d="M24 33C24 33 26 35 28 35C30 35 32 33 32 33" stroke="#4F46E5" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
        </div>
        <h2>New Conversation</h2>
        <p>Session cleared. Ask me anything about Epic Vendor Services.</p>
        <div class="quick-actions">
            <button class="quick-action" onclick="sendQuickAction('How do I reset my password?')">Password Reset</button>
            <button class="quick-action" onclick="sendQuickAction('How do I view my invoices?')">View Invoices</button>
            <button class="quick-action" onclick="sendQuickAction('How do I generate a usage report?')">Usage Reports</button>
            <button class="quick-action" onclick="sendQuickAction('How do I contact support?')">Contact Support</button>
        </div>
    `;
    chatMessages.appendChild(welcome);
    chatInput.focus();
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(chatInput.value);
});

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

newChatBtn.addEventListener('click', startNewChat);

async function checkHealth() {
    const badge = document.getElementById('statusBadge');
    try {
        const res = await fetch(`${API_BASE}/health`, { cache: 'no-cache' });
        if (res.ok) {
            badge.innerHTML = '<span class="status-dot"></span> Online';
            badge.style.color = 'var(--success)';
            badge.style.background = 'var(--success-bg)';
            badge.style.borderColor = 'rgba(16, 185, 129, 0.15)';
        } else {
            throw new Error();
        }
    } catch {
        badge.innerHTML = '<span class="status-dot" style="background:var(--error);animation:none"></span> Offline';
        badge.style.color = 'var(--error)';
        badge.style.background = 'var(--error-bg)';
        badge.style.borderColor = 'rgba(239, 68, 68, 0.15)';
    }
}

checkHealth();
setInterval(checkHealth, 30000);
chatInput.focus();
