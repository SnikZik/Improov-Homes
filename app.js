/* ============================================================
   1057 Bond Street — Improov Homes
   Single source of truth for phone, financing numbers, videos.
   ============================================================ */

/* ---------- 1. PHONE (virtual tracking number) ----------
   Change here only. Every CTA on the page reads from this. */
const phoneConfig = {
  raw: '+15513241057',          // virtual tracking number (E.164)
  display: '(551) 324-1057'     // same number, formatted for display
};

/* ---------- 2. FINANCING SCENARIOS ----------
   Update these when the lender sends new figures. Nothing else to touch.
   effectiveMonthly is calculated: monthlyPayment - projectedRent. */
const financingConfig = {
  disclosure: 'Illustrative financing examples for qualified buyers only. Rates, payments, eligibility and rental income may change and are subject to lender approval.',
  scenarios: [
    {
      id: 'fha',
      name: 'FHA',
      downPercent: '3.5% Down',
      downPayment: 35000,
      monthlyPayment: 7933,
      projectedRent: 4500,
      badge: null
    },
    {
      id: 'cra',
      name: 'CRA Conventional',
      downPercent: '5% Down',
      downPayment: 50000,
      monthlyPayment: 6680,
      projectedRent: 4500,
      badge: 'Best value if you qualify'
    },
    {
      id: 'conventional',
      name: 'Conventional',
      downPercent: '20% Down',
      downPayment: 200000,
      monthlyPayment: 6608,
      projectedRent: 4500,
      badge: null
    }
  ]
};

/* ---------- 3. VIDEO SOURCES ----------
   Drop the files into /videos with these names (see README).
   Posters are optional — without them the first frame is used. */
const videoConfig = {
  hero:    { src: 'videos/web/hero-15sec-open.mp4',  poster: 'img/hero-15sec-open-poster.jpg'  }, // C1_15sec-open - טוב.mp4
  pays:    { src: 'videos/web/pays-for-itself.mp4',  poster: 'img/pays-for-itself-poster.jpg'  }, // A3_pays-for-itself.mp4
  million: { src: 'videos/web/almost-a-million.mp4', poster: 'img/almost-a-million-poster.jpg' }  // B4_almost-a-million.mp4
  // unused for now: B2_fha-and-cra.mp4, A9_mortgage-guide.mp4
};

/* ---------- 3b. ANALYTICS ----------
   Google Analytics 4: paste the Measurement ID (G-XXXXXXXXXX) here and it
   switches on. Left empty, nothing from Google loads. Meta Pixel is in index.html. */
const analyticsConfig = {
  ga4Id: ''
};

/* ============================================================
   4. TRACKING
   Every event goes to the dataLayer, to GA4 (when analyticsConfig.ga4Id is
   set), to the Meta Pixel as a custom event, and out as a DOM CustomEvent
   'lp:<Event>' so a call-tracking script can listen without edits.

   Every event also carries the ad attribution from the URL (utm_source,
   utm_campaign, utm_content = ad set, utm_term = ad, utm_placement), so a
   call tap can be traced back to the exact ad that sent the visitor.

   Events
     LandingPageView        page load
     ScrollDepth            25 / 50 / 75 / 90 % of the page
     EngagedTime            15 / 30 / 60 / 120 s with the tab actually visible
     SectionView            a section reaches the middle of the screen (once each)
     HeroVideoPlay          hero video started
     SectionVideoPlay       pays / million video started
     VideoProgress          25 / 50 / 75 % of any video
     HeroVideoComplete      hero video finished
     SectionVideoComplete   section video finished
     CallButtonClick        any call button tapped; also sends the Meta
                            standard event 'Contact' with the same details

   Add ?lp_debug=1 to the URL to print every event in the browser console.
   ============================================================ */

/* ---------- 4a. GA4 loader ---------- */
(function initGA4() {
  const id = analyticsConfig.ga4Id;
  if (!id) return;
  try {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', id);            // page_view + campaign attribution, automatic
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(s);
  } catch (e) { /* analytics must never break the page */ }
})();

/* ---------- 4b. ad attribution, read once from the landing URL ---------- */
const attribution = (() => {
  const out = {};
  try {
    const q = new URLSearchParams(window.location.search);
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'utm_placement']
      .forEach(k => { const v = q.get(k); if (v) out[k] = v.slice(0, 100); });
  } catch (e) { /* ignore */ }
  return out;
})();

/* ---------- 4c. session state, used to enrich the call event ---------- */
const session = {
  startedAt: Date.now(),
  maxScroll: 0,          // deepest point reached, % of the page
  engagedSeconds: 0,     // seconds with the tab visible
  videosStarted: 0
};

if (/[?&]lp_debug=1(&|$)/.test(window.location.search)) window.LP_DEBUG = true;

/* GA4 prefers snake_case names. null = GA4 already records it by itself. */
const GA4_EVENT = {
  LandingPageView: null,
  ScrollDepth: 'scroll_depth',
  EngagedTime: 'engaged_time',
  SectionView: 'section_view',
  HeroVideoPlay: 'video_start',
  SectionVideoPlay: 'video_start',
  VideoProgress: 'video_progress',
  HeroVideoComplete: 'video_complete',
  SectionVideoComplete: 'video_complete',
  CallButtonClick: 'call_click'
};

const track = (event, params = {}) => {
  const full = { ...attribution, ...params };
  const payload = { event, page: 'bond-street-1057', ...full };
  try {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(payload);
    if (typeof window.gtag === 'function') {
      const name = Object.prototype.hasOwnProperty.call(GA4_EVENT, event) ? GA4_EVENT[event] : event;
      if (name) window.gtag('event', name, full);
    }
    if (typeof window.fbq === 'function') window.fbq('trackCustom', event, full);
    document.dispatchEvent(new CustomEvent('lp:' + event, { detail: full }));
    if (window.LP_DEBUG) console.log('[track]', event, full);
  } catch (e) { /* tracking must never break the page */ }
};

/* ---------- 4d. scroll depth ---------- */
function wireScrollDepth() {
  const marks = [25, 50, 75, 90];
  const hit = new Set();
  let ticking = false;
  const measure = () => {
    ticking = false;
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollable <= 0) return;
    const pct = Math.min(100, Math.round((window.scrollY / scrollable) * 100));
    if (pct > session.maxScroll) session.maxScroll = pct;
    marks.forEach(m => {
      if (pct >= m && !hit.has(m)) { hit.add(m); track('ScrollDepth', { percent: m }); }
    });
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { ticking = true; window.requestAnimationFrame(measure); }
  }, { passive: true });
}

/* ---------- 4e. engaged time (only counts while the tab is visible) ---------- */
function wireEngagedTime() {
  const marks = [15, 30, 60, 120];
  let next = 0;
  window.setInterval(() => {
    if (document.visibilityState !== 'visible') return;
    session.engagedSeconds += 1;
    if (next < marks.length && session.engagedSeconds >= marks[next]) {
      track('EngagedTime', { seconds: marks[next] });
      next += 1;
    }
  }, 1000);
}

/* ---------- 4f. section views ---------- */
function wireSectionViews() {
  if (!('IntersectionObserver' in window)) return;
  const ids = ['math', 'pays', 'property', 'million', 'multigen', 'location', 'imbar', 'final'];
  // fires when any part of the section crosses the middle fifth of the screen,
  // which works for sections taller than the viewport too
  const obs = new IntersectionObserver((entries, o) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      track('SectionView', { section: e.target.id });
      o.unobserve(e.target);
    });
  }, { rootMargin: '-40% 0px -40% 0px', threshold: 0 });
  ids.forEach(id => { const el = document.getElementById(id); if (el) obs.observe(el); });
}

/* ---------- helpers ---------- */
const money = n => '$' + Math.round(n).toLocaleString('en-US');

/* ============================================================
   5. PHONE WIRING — every CTA, one number
   ============================================================ */
function wirePhone() {
  const href = 'tel:' + phoneConfig.raw;

  document.querySelectorAll('[data-call]').forEach(el => {
    el.setAttribute('href', href);
    el.addEventListener('click', () => {
      const params = {
        location: el.dataset.loc || 'unknown',
        phone: phoneConfig.raw,
        seconds_on_page: Math.round((Date.now() - session.startedAt) / 1000),
        engaged_seconds: session.engagedSeconds,
        max_scroll: session.maxScroll,
        videos_started: session.videosStarted
      };
      track('CallButtonClick', params);
      // Meta standard event too, so a campaign can optimise toward calls
      try {
        if (typeof window.fbq === 'function') window.fbq('track', 'Contact', { ...attribution, ...params });
      } catch (e) { /* tracking must never break the page */ }
    });
  });

  document.querySelectorAll('[data-phone-text]').forEach(el => {
    el.textContent = phoneConfig.display;
  });
}

/* ============================================================
   6. FINANCING CARDS
   ============================================================ */
function renderCards() {
  const host = document.getElementById('financingCards');
  if (!host) return;

  host.innerHTML = financingConfig.scenarios.map(s => {
    const effective = s.monthlyPayment - s.projectedRent;
    return `
      <article class="card${s.badge ? ' card--best' : ''}">
        ${s.badge ? `<span class="card__badge">${s.badge}</span>` : ''}
        <h3 class="card__name">${s.name}</h3>
        <p class="card__down">${s.downPercent}</p>
        <div class="card__rows">
          <div class="card__row">
            <span class="card__k">Approx. down payment</span>
            <span class="card__v">${money(s.downPayment)}</span>
          </div>
          <div class="card__row">
            <span class="card__k">Estimated monthly housing payment</span>
            <span class="card__v">${money(s.monthlyPayment)}</span>
          </div>
          <div class="card__row card__row--rent">
            <span class="card__k">Projected rent from other unit</span>
            <span class="card__v">&minus;${money(s.projectedRent)}</span>
          </div>
        </div>
        <div class="card__net">
          <p class="card__net-k">Estimated effective monthly cost</p>
          <p class="card__net-v">${money(effective)}</p>
          <p class="card__net-sub">per month, estimated</p>
        </div>
        <a class="btn btn--call" href="#" data-call data-loc="card-${s.id}">Call Imbar</a>
      </article>`;
  }).join('');

  const note = document.getElementById('mathDisclosure');
  if (note) note.textContent = financingConfig.disclosure;
  document.querySelectorAll('[data-disclosure-copy]').forEach(el => {
    el.textContent = financingConfig.disclosure;
  });
}

/* ============================================================
   7. VIDEO — first frame + overlay, tap plays from 0 with sound.
   No modal, no navigation, stays inline. One video plays at a time.
   ============================================================ */
const players = [];

function setupVideo(video, cover, key) {
  const cfg = videoConfig[key];
  if (cfg) {
    if (cfg.src) video.src = cfg.src;
    if (cfg.poster) video.poster = cfg.poster;
  }
  video.playsInline = true;
  video.setAttribute('webkit-playsinline', '');
  video.muted = true;              // lets the browser render the first frame
  if (key === 'hero') video.preload = 'metadata';   // others load on approach
  video.controls = false;

  let started = false;
  players.push(video);

  // match the frame to the real aspect ratio of whatever file is dropped in
  const shell = video.closest('[data-vframe]') || video.parentElement;
  const chipTime = shell && shell.querySelector('[data-duration]');

  const applyMeta = () => {
    if (!chipTime || !isFinite(video.duration) || !video.duration) return;
    const s = Math.round(video.duration);
    chipTime.textContent = Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
  };

  const applyRatio = () => {
    const w = video.videoWidth, h = video.videoHeight;
    if (!w || !h) return;
    const ar = w + ' / ' + h;
    const frame = video.closest('[data-vframe]');
    if (frame) frame.style.aspectRatio = ar;
    if (key === 'hero') document.documentElement.style.setProperty('--hero-ar', ar);
  };
  ['loadedmetadata', 'resize', 'loadeddata', 'durationchange'].forEach(ev => {
    video.addEventListener(ev, () => { applyRatio(); applyMeta(); });
  });

  const start = () => {
    players.forEach(v => { if (v !== video && !v.paused) v.pause(); });

    video.muted = false;
    video.volume = 1;
    video.currentTime = 0;
    video.controls = key !== 'hero';   // hero stays clean; tap toggles play/pause

    const p = video.play();
    if (p && typeof p.catch === 'function') {
      p.catch(() => {                 // hard block: fall back to muted playback
        video.muted = true;
        video.controls = true;        // give the visitor a way to turn sound on
        video.play().catch(() => {});
      });
    }

    if (cover) cover.hidden = true;
    if (!started) {
      started = true;
      session.videosStarted += 1;
      track(key === 'hero' ? 'HeroVideoPlay' : 'SectionVideoPlay', { video: key });
      // the clip carries its own burned-in titles: clear our chrome out of their way
      if (key === 'hero') document.querySelector('.hero').classList.add('is-playing');
    }
  };

  if (cover) cover.addEventListener('click', start);

  if (key === 'hero') {               // tap the hero video itself to pause / resume
    video.addEventListener('click', () => {
      if (!started) return;
      if (video.paused) video.play().catch(() => {}); else video.pause();
    });
  }

  const progressHit = new Set();
  video.addEventListener('timeupdate', () => {
    if (!started || !isFinite(video.duration) || !video.duration) return;
    const pct = (video.currentTime / video.duration) * 100;
    [25, 50, 75].forEach(m => {
      if (pct >= m && !progressHit.has(m)) {
        progressHit.add(m);
        track('VideoProgress', { video: key, percent: m });
      }
    });
  });

  video.addEventListener('ended', () => {
    track(key === 'hero' ? 'HeroVideoComplete' : 'SectionVideoComplete', { video: key });
  });
}

function wireVideos() {
  document.querySelectorAll('video[data-video]').forEach(video => {
    const key = video.dataset.video;
    const cover = video.parentElement.querySelector('.vcover');
    setupVideo(video, cover, key);
  });

  if (!('IntersectionObserver' in window)) return;

  // load the first frame only when a video comes close to the viewport
  const preloader = new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      if (e.target.preload === 'none') { e.target.preload = 'metadata'; e.target.load(); }
      obs.unobserve(e.target);
    });
  }, { rootMargin: '300px 0px' });

  // pause any playing video once it scrolls out of view
  const pauser = new IntersectionObserver(entries => {
    entries.forEach(e => { if (!e.isIntersecting && !e.target.paused) e.target.pause(); });
  }, { threshold: 0.15 });

  players.forEach(v => { preloader.observe(v); pauser.observe(v); });
}

/* ============================================================
   8. BOOT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  renderCards();
  wirePhone();      // after renderCards so injected card CTAs get wired
  wireVideos();
  wireScrollDepth();
  wireEngagedTime();
  wireSectionViews();
  track('LandingPageView', { referrer: document.referrer || 'direct' });
});
