/* ============================================================
   1057 Bond St, open house page.
   Everything you might change is in the config blocks below.
   ============================================================ */

/* ---------- 1. PHONE (same tracking line as the ads) ---------- */
const phoneConfig = {
  raw: '+15513241057',
  display: '(551) 324-1057',
  textBody: "Hi, I'd like to come to the open house at 1057 Bond St."
};

/* ---------- 2. OPEN HOUSE TIMES (Eastern) ----------
   After the last one ends the page switches itself: dates and "Add to
   calendar" go away and it asks for a private showing instead. */
const openHouse = {
  endsAt: '2026-10-25T15:00:00-04:00'
};

/* ---------- 3. ANALYTICS ---------- */
const analyticsConfig = { ga4Id: '' };
const PAGE_ID = 'bond-street-1057-open-house';

/* ============================================================
   TRACKING
     LandingPageView, ScrollDepth, SectionView,
     CallButtonClick (+ Meta 'Contact'), TextButtonClick (+ Meta 'Contact'),
     AddToCalendar, VideoPlay, VideoProgress, VideoComplete
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
const contact = (params) => {
  try { if (typeof window.fbq === 'function') window.fbq('track', 'Contact', { ...attribution, ...params }); } catch (e) { /* ignore */ }
};

/* ============================================================
   WIRING
   ============================================================ */
function wireContacts() {
  const base = () => ({ phone: phoneConfig.raw, seconds_on_page: Math.round((Date.now() - session.startedAt) / 1000), max_scroll: session.maxScroll });
  document.querySelectorAll('[data-call]').forEach(el => {
    el.setAttribute('href', 'tel:' + phoneConfig.raw);
    el.addEventListener('click', () => { const p = { location: el.dataset.loc, via: 'call', ...base() }; track('CallButtonClick', p); contact(p); });
  });
  // "?&body=" is the form both iOS and Android read
  const sms = 'sms:' + phoneConfig.raw + '?&body=' + encodeURIComponent(phoneConfig.textBody);
  document.querySelectorAll('[data-text]').forEach(el => {
    el.setAttribute('href', sms);
    el.addEventListener('click', () => { const p = { location: el.dataset.loc, via: 'text', ...base() }; track('TextButtonClick', p); contact(p); });
  });
  document.querySelectorAll('[data-cal]').forEach(el => {
    el.addEventListener('click', () => track('AddToCalendar', { location: el.dataset.loc }));
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

/* the bottom bar stays out of the way while the hero's own buttons are on screen */
function wireSticky() {
  const bar = document.getElementById('sticky');
  const heroCtas = document.querySelector('.hero .ctas');
  if (!bar || !heroCtas || !('IntersectionObserver' in window)) return;
  new IntersectionObserver(es => es.forEach(e => bar.classList.toggle('is-away', e.isIntersecting)), { threshold: 0 }).observe(heroCtas);
}

document.addEventListener('DOMContentLoaded', () => {
  applySchedule();
  wireSticky();
  wireContacts();
  wireScroll();
  wireVideo();
  track('LandingPageView', { referrer: document.referrer || 'direct' });
});
