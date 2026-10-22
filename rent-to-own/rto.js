/* ============================================================
   1057 Bond St, rent-to-own page.
   Everything you might change is in the config blocks below.
   ============================================================ */

/* ---------- 1. PHONE (same tracking line as the ads) ----------
   Shown and dialable ONLY on the popup's last step, after both questions are answered.
   No other button on the page carries the number or a tel: link. */
const phoneConfig = {
  raw: '+15513241057',
  display: '(551) 324-1057'
};

/* ---------- 2. ANALYTICS ---------- */
const analyticsConfig = { ga4Id: '' };
const PAGE_ID = 'bond-street-1057-rent-to-own';

/* ============================================================
   TRACKING
     LandingPageView, ScrollDepth, SectionView,
     CallQuestionOpen, CallQuestionAnswer (open_to_nj yes | no, then interest rto | buy), CallBlocked (not open to NJ),
     CallButtonClick (+ Meta 'Lead', lead_type call, with the answer),
     VideoPlay, VideoProgress, VideoComplete
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
    const key = 'rto_lead_' + type;
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, '1');
  } catch (e) { /* private mode: count it anyway */ }
  try { if (typeof window.fbq === 'function') window.fbq('track', 'Lead', { lead_type: type, content_name: '1057 Bond rent to own', ...attribution, ...params }); } catch (e) { /* ignore */ }
};

/* ============================================================
   WIRING
   ============================================================ */
function wireContacts() {
  const base = () => ({ phone: phoneConfig.raw, seconds_on_page: Math.round((Date.now() - session.startedAt) / 1000), max_scroll: session.maxScroll });

  // every call button asks two questions first (New Jersey, then rent to own or buy now); the
  // tap-to-call is inside the popup. "No" to New Jersey ends there with no number.
  const gate = document.getElementById('callGate');
  const tel = gate.querySelector('[data-gate-tel]');
  const sub = gate.querySelector('[data-call-sub]');
  const phoneText = gate.querySelectorAll('[data-phone-text]');
  let origin = 'unknown', answer = null, armedAt = 0, lastFocus = null;
  const SUB = {
    rto: 'Ask for the written rent-to-own terms for the first-floor unit and the lower level.',
    buy: 'Ask about the $899,000 price.'
  };
  const show = step => {
    armedAt = Date.now() + 400;                 // a double tap must not skip the question
    gate.querySelectorAll('.gate__step').forEach(s => { s.hidden = s.dataset.step !== step; });
    const first = gate.querySelector(`.gate__step[data-step="${step}"]`).querySelector('button, a');
    if (first) setTimeout(() => first.focus({ preventScroll: true }), 30);
  };
  const disarm = () => {                        // no number and no tel: link until both answers are in
    answer = null;
    tel.setAttribute('href', '#');
    phoneText.forEach(el => { el.textContent = ''; });
    sub.textContent = '';
  };
  const open = loc => {
    origin = loc || 'unknown'; lastFocus = document.activeElement;
    disarm();
    gate.hidden = false; document.documentElement.classList.add('gate-open');
    track('CallQuestionOpen', { location: origin });
    show('nj');
  };
  const close = () => {
    gate.hidden = true; document.documentElement.classList.remove('gate-open');
    disarm();
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  };
  document.querySelectorAll('[data-call]').forEach(el => {
    el.setAttribute('href', '#call');
    el.setAttribute('aria-haspopup', 'dialog');
    el.addEventListener('click', e => { e.preventDefault(); open(el.dataset.loc); });
  });
  gate.querySelectorAll('[data-nj]').forEach(b => b.addEventListener('click', () => {
    if (Date.now() < armedAt) return;
    const yes = b.dataset.nj === 'yes';
    track('CallQuestionAnswer', { location: origin, question: 'open_to_nj', answer: b.dataset.nj });
    if (!yes) track('CallBlocked', { location: origin, reason: 'not_open_to_nj' });
    show(yes ? 'q' : 'no-nj');
  }));
  gate.querySelectorAll('[data-answer]').forEach(b => b.addEventListener('click', () => {
    if (Date.now() < armedAt) return;
    answer = b.dataset.answer;
    track('CallQuestionAnswer', { location: origin, question: 'interest', interest: answer });
    sub.textContent = SUB[answer];
    tel.setAttribute('href', 'tel:' + phoneConfig.raw);
    phoneText.forEach(el => { el.textContent = phoneConfig.display; });
    show('call');
  }));
  tel.addEventListener('click', e => {
    if (!answer) { e.preventDefault(); return; }
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

  // a link to this page ending in #call opens the questions
  if (window.location.hash === '#call') {
    try { history.replaceState(null, '', window.location.pathname + window.location.search); } catch (e) { /* ignore */ }
    open('link');
  }
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
  ['tour', 'home', 'rto', 'sale', 'visit'].forEach(id => { const el = document.getElementById(id); if (el) obs.observe(el); });
}

function wireVideo() {
  const v = document.getElementById('tourVideo');
  if (!v) return;
  const cover = v.parentElement.querySelector('.vcover');
  let started = false;
  const hit = new Set();
  const name = () => v.dataset.video || 'lead';
  cover.addEventListener('click', () => {
    v.muted = false;
    v.currentTime = 0;
    v.controls = true;
    v.play().catch(() => { v.muted = true; v.play().catch(() => {}); });
    cover.hidden = true;
    if (!started) { started = true; track('VideoPlay', { video: name() }); }
  });
  v.addEventListener('timeupdate', () => {
    if (!started || !v.duration) return;
    const pct = v.currentTime / v.duration * 100;
    [25, 50, 75].forEach(m => { if (pct >= m && !hit.has(m)) { hit.add(m); track('VideoProgress', { video: name(), percent: m }); } });
  });
  v.addEventListener('ended', () => track('VideoComplete', { video: name() }));
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting && !v.paused) v.pause(); }), { threshold: 0.15 }).observe(v);
  }
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

/* the bottom bar (one Call button) ships hidden and stays out of the way while the
   hero's own button is fully on screen, and while the last section's Call button is on
   screen; anywhere else it is there. It only starts to animate after the first check,
   so a page load never shows it sliding away. */
function wireSticky() {
  const bar = document.getElementById('sticky');
  const heroCtas = document.querySelector('.hero .ctas');
  if (!bar) return;
  const visitCtas = document.querySelector('#visit .ctas');
  if (!heroCtas || !('IntersectionObserver' in window)) { bar.classList.remove('is-away'); return; }
  let heroIn = false, visitIn = false;
  new IntersectionObserver(es => {
    es.forEach(e => { heroIn = e.intersectionRatio >= 0.98; });
    bar.classList.toggle('is-away', heroIn || visitIn);
    if (!bar.classList.contains('is-ready')) requestAnimationFrame(() => bar.classList.add('is-ready'));
  }, { threshold: [0, 0.98, 1] }).observe(heroCtas);
  if (visitCtas) new IntersectionObserver(es => es.forEach(e => {
    visitIn = e.isIntersecting;
    bar.classList.toggle('is-away', heroIn || visitIn);
  }), { threshold: 0 }).observe(visitCtas);
}

document.addEventListener('DOMContentLoaded', () => {
  wireHeroVideo();
  wireSticky();
  wireContacts();
  wireScroll();
  wireVideo();
  track('LandingPageView', { referrer: document.referrer || 'direct' });
});
