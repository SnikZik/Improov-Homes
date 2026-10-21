/* ============================================================
   1057 Bond St, open house page.
   Everything you might change is in the config blocks below.
   ============================================================ */

/* ---------- 1. PHONE (same tracking line as the ads) ---------- */
const phoneConfig = {
  raw: '+15513241057',
  display: '(551) 324-1057'
};

/* ---------- 2. OPEN HOUSE TIMES (Eastern) ----------
   After the last one ends the page switches itself: dates and "Add to
   calendar" go away and it asks for a private showing instead. */
const openHouse = {
  endsAt: '2026-10-25T15:00:00-04:00',
  // the RSVP popup offers only these two; a day drops out once it is over.
  // "value" is what lands in the GHL form (hidden field open_house_day).
  days: {
    sat: { title: 'Saturday, Oct 24, 12 to 3 PM', value: 'Saturday Oct 24, 12 to 3 PM', endsAt: '2026-10-24T15:00:00-04:00' },
    sun: { title: 'Sunday, Oct 25, 1 to 3 PM', value: 'Sunday Oct 25, 1 to 3 PM', endsAt: '2026-10-25T15:00:00-04:00' }
  }
};

/* ---------- 3. ANALYTICS ---------- */
const analyticsConfig = { ga4Id: '' };
const PAGE_ID = 'bond-street-1057-open-house';

/* ============================================================
   TRACKING
     LandingPageView, ScrollDepth, SectionView,
     CallQuestionOpen, CallQuestionAnswer (interest: buy | rto),
     CallButtonClick (+ Meta 'Lead', lead_type call, with the answer),
     RSVPOpen, RSVPDay (day: sat | sun), RSVPBooked (+ Meta 'Lead', lead_type rsvp, fired on thanks.html), VideoPlay, VideoProgress, VideoComplete
   Meta pixel 309890672012145: the campaign optimizes for the standard 'Lead' event.
   A call tap counts once per visit, so repeat taps do not inflate the lead count.
   ?lp_debug=1 prints every event.
   ============================================================ */
(function initGA4() {
  const id = analyticsConfig.ga4Id;
  if (!id) return;
  try {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', id);
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(s);
  } catch (e) { /* analytics must never break the page */ }
})();

const attribution = (() => {
  const out = {};
  try {
    const q = new URLSearchParams(window.location.search);
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'utm_placement']
      .forEach(k => { const v = q.get(k); if (v) out[k] = v.slice(0, 100); });
  } catch (e) { /* ignore */ }
  return out;
})();
const session = { startedAt: Date.now(), maxScroll: 0 };
if (/[?&]lp_debug=1(&|$)/.test(window.location.search)) window.LP_DEBUG = true;

const track = (event, params = {}) => {
  const full = { ...attribution, ...params };
  try {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event, page: PAGE_ID, ...full });
    if (typeof window.gtag === 'function') window.gtag('event', event, full);
    if (typeof window.fbq === 'function') window.fbq('trackCustom', event, full);
    document.dispatchEvent(new CustomEvent('lp:' + event, { detail: full }));
    if (window.LP_DEBUG) console.log('[track]', event, full);
  } catch (e) { /* tracking must never break the page */ }
};
const lead = (type, params) => {
  try {
    const key = 'oh_lead_' + type;
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, '1');
  } catch (e) { /* private mode: count it anyway */ }
  try { if (typeof window.fbq === 'function') window.fbq('track', 'Lead', { lead_type: type, content_name: '1057 Bond open house', ...attribution, ...params }); } catch (e) { /* ignore */ }
};

/* ============================================================
   WIRING
   ============================================================ */
function wireContacts() {
  const base = () => ({ phone: phoneConfig.raw, seconds_on_page: Math.round((Date.now() - session.startedAt) / 1000), max_scroll: session.maxScroll });

  // every call button asks one question first; the tap-to-call is inside the popup
  const gate = document.getElementById('callGate');
  const tel = gate.querySelector('[data-gate-tel]');
  const sub = gate.querySelector('[data-call-sub]');
  let origin = 'unknown', answer = null, armedAt = 0, lastFocus = null;
  const SUB = {
    buy: 'Ask about the $899,000 price and the open house this weekend.',
    rto: 'Ask for the written rent-to-own terms for the first-floor unit and lower level.'
  };
  const show = step => {
    armedAt = Date.now() + 400;                 // a double tap must not skip the question
    gate.querySelectorAll('.gate__step').forEach(s => { s.hidden = s.dataset.step !== step; });
    const first = gate.querySelector(`.gate__step[data-step="${step}"]`).querySelector('button, a');
    if (first) setTimeout(() => first.focus({ preventScroll: true }), 30);
  };
  const open = loc => {
    origin = loc || 'unknown'; answer = null; lastFocus = document.activeElement;
    gate.hidden = false; document.documentElement.classList.add('gate-open');
    track('CallQuestionOpen', { location: origin });
    show('q');
  };
  const close = () => {
    gate.hidden = true; document.documentElement.classList.remove('gate-open');
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  };
  document.querySelectorAll('[data-call]').forEach(el => {
    el.setAttribute('href', '#call');
    el.setAttribute('aria-haspopup', 'dialog');
    el.addEventListener('click', e => { e.preventDefault(); open(el.dataset.loc); });
  });
  gate.querySelectorAll('[data-answer]').forEach(b => b.addEventListener('click', () => {
    if (Date.now() < armedAt) return;
    answer = b.dataset.answer;
    track('CallQuestionAnswer', { location: origin, interest: answer });
    sub.textContent = SUB[answer];
    show('call');
  }));
  tel.setAttribute('href', 'tel:' + phoneConfig.raw);
  tel.addEventListener('click', () => {
    const p = { location: origin, via: 'call', interest: answer, ...base() };
    track('CallButtonClick', p); lead('call', p);
  });
  gate.querySelectorAll('[data-gate-close]').forEach(el => el.addEventListener('click', close));
  document.addEventListener('keydown', e => {
    if (gate.hidden) return;
    if (e.key === 'Escape') return close();
    if (e.key === 'Tab') {
      const f = [...gate.querySelectorAll('button, a')].filter(n => n.offsetParent !== null);
      if (!f.length) return;
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    }
  });

  document.querySelectorAll('[data-phone-text]').forEach(el => { el.textContent = phoneConfig.display; });
}

function applySchedule() {
  const over = Date.now() > Date.parse(openHouse.endsAt);
  document.querySelectorAll('[data-when="before"]').forEach(el => { el.hidden = over; });
  document.querySelectorAll('[data-when="after"]').forEach(el => { el.hidden = !over; });
  document.documentElement.classList.toggle('oh-over', over);
}

function wireScroll() {
  const marks = [25, 50, 75, 90], hit = new Set();
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      const max = document.documentElement.scrollHeight - innerHeight;
      if (max <= 0) return;
      const pct = Math.min(100, Math.round(scrollY / max * 100));
      session.maxScroll = Math.max(session.maxScroll, pct);
      marks.forEach(m => { if (pct >= m && !hit.has(m)) { hit.add(m); track('ScrollDepth', { percent: m }); } });
    });
  }, { passive: true });
  if (!('IntersectionObserver' in window)) return;
  const obs = new IntersectionObserver((es, o) => es.forEach(e => {
    if (e.isIntersecting) { track('SectionView', { section: e.target.id }); o.unobserve(e.target); }
  }), { rootMargin: '-40% 0px -40% 0px' });
  ['house', 'tour', 'rto', 'visit'].forEach(id => { const el = document.getElementById(id); if (el) obs.observe(el); });
}

function wireVideo() {
  const v = document.getElementById('tourVideo');
  if (!v) return;
  const cover = v.parentElement.querySelector('.vcover');
  let started = false;
  const hit = new Set();
  cover.addEventListener('click', () => {
    v.muted = false;
    v.currentTime = 0;
    v.controls = true;
    v.play().catch(() => { v.muted = true; v.play().catch(() => {}); });
    cover.hidden = true;
    if (!started) { started = true; track('VideoPlay', { video: 'tour' }); }
  });
  v.addEventListener('timeupdate', () => {
    if (!started || !v.duration) return;
    const pct = v.currentTime / v.duration * 100;
    [25, 50, 75].forEach(m => { if (pct >= m && !hit.has(m)) { hit.add(m); track('VideoProgress', { video: 'tour', percent: m }); } });
  });
  v.addEventListener('ended', () => track('VideoComplete', { video: 'tour' }));
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting && !v.paused) v.pause(); }), { threshold: 0.15 }).observe(v);
  }
}

/* RSVP: two big buttons (Saturday / Sunday), then Imbar's open house form from GHL with
   the chosen day in a hidden field. GHL emails Roi, Imbar and Snir on every submission and
   sends the visitor to thanks.html, which offers the calendar links and fires RSVPBooked.
   The form and GHL's resize script load only once a day is picked. */
function wireRsvp() {
  const gate = document.getElementById('rsvpGate');
  if (!gate) return;
  const frame = gate.querySelector('iframe');
  const title = gate.querySelector('[data-rsvp-title]');
  let scriptLoaded = false, origin = 'unknown', lastFocus = null;
  const show = step => {
    gate.querySelectorAll('.gate__step').forEach(s => { s.hidden = s.dataset.step !== step; });
    gate.querySelector('.gate__panel').scrollTop = 0;
    if (step !== 'day') return;
    const first = gate.querySelector('[data-day]:not([hidden])');
    if (first) setTimeout(() => first.focus({ preventScroll: true }), 30);
  };
  const store = (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) { /* private mode */ } };
  const open = loc => {
    origin = loc || 'unknown'; lastFocus = document.activeElement;
    const now = Date.now();
    gate.querySelectorAll('[data-day]').forEach(b => { b.hidden = now > Date.parse(openHouse.days[b.dataset.day].endsAt); });
    gate.hidden = false; document.documentElement.classList.add('gate-open');
    track('RSVPOpen', { location: origin });
    show('day');
  };
  const close = () => {
    gate.hidden = true; document.documentElement.classList.remove('gate-open');
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  };
  gate.querySelectorAll('[data-day]').forEach(b => b.addEventListener('click', () => {
    const day = b.dataset.day, d = openHouse.days[day];
    track('RSVPDay', { location: origin, day });
    store('oh_day', day); store('oh_loc', origin); store('oh_utm', JSON.stringify(attribution));
    title.textContent = d.title;
    // the ad's UTM tags ride along so GHL files the RSVP contact under the right ad
    const q = new URLSearchParams({ open_house_day: d.value, ...attribution });
    const src = frame.dataset.src + '?' + q.toString();
    if (frame.getAttribute('src') !== src) frame.src = src;
    if (!scriptLoaded) {
      scriptLoaded = true;
      const s = document.createElement('script');
      s.src = 'https://link.msgsndr.com/js/form_embed.js';
      s.async = true;
      document.body.appendChild(s);
    }
    show('form');
  }));
  gate.querySelector('[data-rsvp-back]').addEventListener('click', () => show('day'));
  // Tab out of the GHL iframe never reaches our keydown handler, so focus lands on these instead
  const focusables = () => [...gate.querySelectorAll('button, a, iframe')].filter(n => n.offsetParent !== null);
  gate.querySelector('[data-trap-end]').addEventListener('focus', () => gate.querySelector('.gate__x').focus());
  gate.querySelector('[data-trap-start]').addEventListener('focus', () => { const f = focusables(); f[f.length - 1].focus(); });
  document.querySelectorAll('[data-cal]').forEach(el => {
    el.setAttribute('aria-haspopup', 'dialog');
    el.addEventListener('click', e => { e.preventDefault(); open(el.dataset.loc); });
  });
  gate.querySelectorAll('[data-rsvp-close]').forEach(el => el.addEventListener('click', close));
  document.addEventListener('keydown', e => {
    if (gate.hidden) return;
    if (e.key === 'Escape') return close();
    if (e.key === 'Tab') {
      const f = [...gate.querySelectorAll('button, a, iframe')].filter(n => n.offsetParent !== null);
      if (!f.length) return;
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    }
  });
}

/* hero loop: silent, plays only while on screen, and stays on the poster for reduced motion */
function wireHeroVideo() {
  const v = document.getElementById('heroVideo');
  if (!v) return;
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) { v.removeAttribute('autoplay'); v.pause(); return; }
  v.muted = true;
  const play = () => v.play().catch(() => { /* autoplay blocked: the poster stays */ });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(es => es.forEach(e => (e.isIntersecting ? play() : v.pause())), { threshold: 0.1 }).observe(v);
  } else play();
}

/* the bottom bar (RSVP left, Call right) ships hidden and stays out of the way while the
   hero's own buttons are fully on screen; anywhere else it is there. It only starts to
   animate after the first check, so a page load never shows it sliding away. */
function wireSticky() {
  const bar = document.getElementById('sticky');
  const heroCtas = document.querySelector('.hero .ctas');
  if (!bar) return;
  if (!heroCtas || !('IntersectionObserver' in window)) { bar.classList.remove('is-away'); return; }
  new IntersectionObserver(es => es.forEach(e => {
    bar.classList.toggle('is-away', e.intersectionRatio >= 0.98);
    if (!bar.classList.contains('is-ready')) requestAnimationFrame(() => bar.classList.add('is-ready'));
  }), { threshold: [0, 0.98, 1] }).observe(heroCtas);
}

document.addEventListener('DOMContentLoaded', () => {
  applySchedule();
  wireHeroVideo();
  wireSticky();
  wireRsvp();
  wireContacts();
  wireScroll();
  wireVideo();
  track('LandingPageView', { referrer: document.referrer || 'direct' });
});
