/* ==========================================================================
   Riya, Arha's AI receptionist: chat window. Loaded on the launcher's first click.
   Talks to the n8n Chat Trigger webhook with the same request the @n8n/chat
   widget sends: POST { action: 'sendMessage', sessionId, chatInput } -> { output }.
   Nothing is sent until the visitor sends a message or taps a quick reply.
   ========================================================================== */
const WELCOME = 'Hello, I’m Riya. I can answer questions about Arha Dental Care or take an appointment request for you.';
const QUICK = ['Clinic timings', 'Dental implants', 'Request an appointment', 'Visiting from abroad'];
const ICON = '<svg viewBox="0 0 919.25 902.15" aria-hidden="true" focusable="false"><use href="#arha-icon"/></svg>';

export function mountRiya({ webhookUrl, launcher }) {
  const root = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isPhone = () => window.matchMedia('(max-width: 767px)').matches;
  let sessionId = '';
  try { sessionId = sessionStorage.getItem('riya-session') || ''; } catch (e) { /* storage blocked */ }
  if (!sessionId) {
    sessionId = (crypto.randomUUID && crypto.randomUUID()) || String(Date.now()) + Math.random().toString(16).slice(2);
    try { sessionStorage.setItem('riya-session', sessionId); } catch (e) { /* storage blocked */ }
  }

  const panel = document.createElement('section');
  panel.className = 'riya';
  panel.id = 'riya';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-labelledby', 'riya-title');
  panel.hidden = true;
  panel.innerHTML = `
    <header class="riya__head">
      <span class="riya__mark">${ICON}</span>
      <div class="riya__id">
        <p class="riya__name" id="riya-title">Riya</p>
        <p class="riya__status"><span class="riya__dot" aria-hidden="true"></span>Arha Dental Care · Replies instantly</p>
      </div>
      <button class="riya__close" type="button" aria-label="Close chat"></button>
    </header>
    <div class="riya__log" aria-live="polite">
      <div class="riya__welcome">
        <span class="riya__avatar">${ICON}</span>
        <div>
          <p class="riya__msg riya__msg--bot">${WELCOME}</p>
          <div class="riya__quick" role="group" aria-label="Suggested questions">
            ${QUICK.map((q) => `<button type="button">${q}</button>`).join('')}
          </div>
        </div>
      </div>
    </div>
    <form class="riya__form">
      <label class="visually-hidden" for="riya-input">Message</label>
      <textarea id="riya-input" rows="1" placeholder="Ask Riya anything…" autocomplete="off"></textarea>
      <button class="riya__send" type="submit" aria-label="Send message">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>
      </button>
    </form>
    <p class="riya__note">Riya passes your request to the clinic team. Appointments are confirmed by phone.</p>`;
  document.body.append(panel);

  const log = panel.querySelector('.riya__log');
  const quick = panel.querySelector('.riya__quick');
  const form = panel.querySelector('.riya__form');
  const input = panel.querySelector('#riya-input');
  const send = panel.querySelector('.riya__send');
  let busy = false;

  const scrollDown = () => { log.scrollTop = log.scrollHeight; };
  const addMessage = (text, who) => {
    const p = document.createElement('p');
    p.className = `riya__msg riya__msg--${who}`;
    p.textContent = text;
    log.append(p);
    scrollDown();
    return p;
  };

  async function ask(text) {
    text = text.trim();
    if (!text || busy) return;
    busy = true;
    send.disabled = true;
    quick.hidden = true; // quick replies only before the conversation starts
    addMessage(text, 'user');
    const typing = document.createElement('p');
    typing.className = 'riya__typing';
    typing.setAttribute('aria-label', 'Riya is typing');
    typing.innerHTML = '<span></span><span></span><span></span>';
    log.append(typing);
    scrollDown();
    try {
      const res = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'sendMessage', sessionId, chatInput: text }),
      });
      const raw = await res.text();
      let reply = raw;
      try {
        const data = JSON.parse(raw);
        const item = Array.isArray(data) ? data[0] : data;
        reply = item.output ?? item.text ?? item.message ?? raw;
      } catch (e) { /* plain-text reply */ }
      if (!res.ok) throw new Error(res.status);
      typing.remove();
      addMessage(String(reply || '…'), 'bot');
    } catch (e) {
      typing.remove();
      addMessage('Sorry, I couldn’t reach the clinic just now. Please call +91 99755 07714 or message us on WhatsApp.', 'bot');
    }
    busy = false;
    send.disabled = false;
  }

  quick.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (b) ask(b.textContent);
  });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = input.value;
    input.value = '';
    input.style.height = '';
    ask(text);
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });
  input.addEventListener('input', () => {
    input.style.height = '';
    input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
  });

  // Phones: full-height sheet that follows the visual viewport, so the input stays above the keyboard
  const fit = () => { panel.style.height = isPhone() && window.visualViewport ? `${window.visualViewport.height}px` : ''; };
  if (window.visualViewport) window.visualViewport.addEventListener('resize', fit);

  let closeTimer = 0;
  const onKey = (e) => { if (e.key === 'Escape') close(); };
  function open() {
    clearTimeout(closeTimer);
    fit();
    panel.hidden = false;
    launcher.setAttribute('aria-expanded', 'true');
    if (isPhone()) root.classList.add('is-locked');
    requestAnimationFrame(() => {
      panel.classList.add('is-open');
      if (!isPhone()) input.focus({ preventScroll: true });
    });
    document.addEventListener('keydown', onKey);
  }
  function close() {
    panel.classList.remove('is-open');
    launcher.setAttribute('aria-expanded', 'false');
    root.classList.remove('is-locked');
    document.removeEventListener('keydown', onKey);
    closeTimer = setTimeout(() => { panel.hidden = true; }, reduceMotion ? 0 : 300);
    launcher.focus({ preventScroll: true });
  }
  panel.querySelector('.riya__close').addEventListener('click', close);
  launcher.setAttribute('aria-controls', 'riya');
  return { open, close, toggle: () => (panel.classList.contains('is-open') ? close() : open()) };
}
