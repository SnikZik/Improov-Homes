/* ============================================================
   1057 Bond Street — Improov Homes
   Single source of truth for phone, prices, financing numbers, videos.
   ============================================================ */

/* ---------- 1. PHONE (virtual tracking number) ----------
   Change here only. Every CTA on the page reads from this. */
const phoneConfig = {
  raw: '+15513241057',          // virtual tracking number (E.164)
  display: '(551) 324-1057'     // same number, formatted for display
};

/* ---------- 2. THE HOUSE AND THE RENT ----------
   Checked against GSMLS #4057212, the 2025 tax bill and Improov's own rental
   listings (fact-check run 15 Oct 2026). */
const propertyConfig = {
  price: 999000,
  taxes: 11892                  // 2025 bill. The $14,144 on Roee's sheet was the 2023 bill
};

/* The rent subtracted on the financing cards. Unit 2 is listed at $2,750.
   Unit 1 together with the lower level is listed at $4,500; using that figure
   would mean the buyer lives in Unit 2. Both listings are asking rents on
   vacant units (PadMapper, rent-to-own only), not leases. */
const rentConfig = {
  amount: 2750,
  label: 'Unit 2 asking rent',
  sub: 'If you live in Unit 1. No lease in place.'
};

/* ---------- 3. FINANCING SWITCH (Reg Z, 12 CFR 1026.24) ----------
   Down payment and monthly payment are "triggering terms": once either is on
   the page, the page must also give the APR and the repayment terms. So every
   scenario carries a loan block, and its card is shown only when every field
   of that block is filled from the lender's written quote: kind, apr, rate,
   rateDate, noteAmount, payments, principalInterest.
   While no scenario is complete the section shows the price, the taxes and
   the asking rent only, and no financing number reaches the page at all.
   Preview the financing version on localhost with ?preview_financing=1.
   Effective monthly cost is calculated: monthlyPayment - rentConfig.amount. */
const financingConfig = {
  scenarios: [
    {
      id: 'fha',
      name: 'FHA',
      downPct: '3.5%',
      downPayment: 34965,         // same figures as the NY page (ny/ny.js)
      monthlyPayment: 8288,       // P&I + 0.75% annual MIP + 2025 taxes + homeowners insurance
      badge: null,
      loan: {
        kind: '30-year fixed FHA',
        apr: '',                  // e.g. '7.812%' from the lender, in writing
        rate: '6.875%',
        rateDate: 'Oct 1, 2026',
        noteAmount: 980906,       // $964,035 base loan + 1.75% upfront MIP
        noteAmountNote: 'including 1.75% upfront mortgage insurance',
        payments: 360,
        principalInterest: 6444
      }
    },
    {
      id: 'cra',
      name: 'CRA Conventional',
      downPct: '5%',
      downPayment: 50000,         // August sheet, not re-checked: replace with the lender's quote
      monthlyPayment: 6680,       //  together with the APR and the loan terms below
      badge: 'Best value if you qualify',
      loan: { kind: '', apr: '', rate: '', rateDate: '', noteAmount: null, noteAmountNote: '', payments: 360, principalInterest: null }
    },
    {
      id: 'conventional',
      name: 'Conventional',
      downPct: '20%',
      downPayment: 200000,        // August sheet, not re-checked: replace with the lender's quote
      monthlyPayment: 6608,
      badge: null,
      loan: { kind: '', apr: '', rate: '', rateDate: '', noteAmount: null, noteAmountNote: '', payments: 360, principalInterest: null }
    }
  ]
};

const LOAN_FIELDS = ['kind', 'apr', 'rate', 'rateDate', 'noteAmount', 'payments', 'principalInterest'];
const loanReady = s => Boolean(s.loan) && LOAN_FIELDS.every(k => Boolean(s.loan[k]));
const previewFinancing = () =>
  /^(localhost|127\.0\.0\.1|\[::1\])$/.test(window.location.hostname) &&
  /[?&]preview_financing=1(&|$)/.test(window.location.search);
const shownScenarios = () => financingConfig.scenarios.filter(s => loanReady(s) || previewFinancing());

const BASE_DISCLOSURE =
  'Property taxes are the 2025 bill and can change. Rent figures are asking rents from current rental listings; ' +
  'both units are vacant and no lease is in place. Information is deemed reliable but not guaranteed.';

const disclosure = () => {
  if (!shownScenarios().length) return BASE_DISCLOSURE;
  return 'Estimates for illustration only, not a loan offer or a commitment to lend. ' +
    'Each loan example is to a qualified buyer who will live in one of the units; not every buyer will qualify; subject to lender approval. ' +
    'Rates change daily. Estimated monthly housing payments include principal and interest, property taxes, homeowners insurance and any mortgage insurance, ' +
    'so the actual payment is higher than principal and interest alone. ' +
    `Estimated effective monthly cost subtracts Unit 2's asking rent of ${money(rentConfig.amount)}; actual rent may be lower and the unit may sit vacant. ` +
    BASE_DISCLOSURE;
};

/* ---------- 3b. VIDEO SOURCES ----------
   Posters are optional; without them the first frame is used. */
const videoConfig = {
  hero: { src: 'videos/web/hero-15sec-open.mp4', poster: 'img/hero-15sec-open-poster.jpg' } // C1_15sec-open - טוב.mp4
  // Off the page on purpose, files kept in /videos:
  //   pays-for-itself.mp4 (A3) says "FROM $35,000 DOWN", a Reg Z triggering term with no APR in the video
  //   almost-a-million.mp4 (B4) says "Built for extended family" (familial status, fair housing)
  //     and "$35,000", "$2,000 / month", "5% down / no PMI" (Reg Z)
};

/* ---------- 3c. ANALYTICS ----------
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
     SectionVideoPlay       a section video started (none on the page now)
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
  CallButtonClick: 'call_click',
  QualifierOpen: 'qualifier_open',
  QualifierAnswer: 'qualifier_answer',
  QualifierBlocked: 'qualifier_blocked'
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
  const ids = ['math', 'pays', 'property', 'multigen', 'location', 'imbar', 'final'];
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
   5. PHONE WIRING: every call button opens two questions first
   (New Jersey, then buy or rent to own), the same as the open house
   page. "No" to New Jersey ends there with no number. The tap-to-call
   is inside the popup, and CallButtonClick + Meta 'Contact' fire only
   on that tap.
   Extra events: QualifierOpen, QualifierAnswer, QualifierBlocked.
   ============================================================ */
function wirePhone() {
  const gate = document.getElementById('callGate');
  const tel = gate.querySelector('[data-gate-tel]');
  const sub = gate.querySelector('[data-call-sub]');
  const SUB = {
    buy: 'Ask about the price and a private showing.',
    rto: 'Ask for the written rent-to-own terms for the first-floor unit and lower level.'
  };
  let origin = 'unknown', interest = null, armedAt = 0, lastFocus = null;

  const show = step => {
    armedAt = Date.now() + 400;                 // a double tap must not answer the next question too
    gate.querySelectorAll('.gate__step').forEach(st => { st.hidden = st.dataset.step !== step; });
    const first = gate.querySelector(`.gate__step[data-step="${step}"]`).querySelector('button, a');
    if (first) setTimeout(() => first.focus({ preventScroll: true }), 30);
  };
  const open = loc => {
    origin = loc || 'unknown'; interest = null; lastFocus = document.activeElement;
    gate.hidden = false; document.documentElement.classList.add('gate-open');
    track('QualifierOpen', { location: origin });
    show('nj');
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
  gate.querySelectorAll('[data-nj]').forEach(b => b.addEventListener('click', () => {
    if (Date.now() < armedAt) return;
    const yes = b.dataset.nj === 'yes';
    track('QualifierAnswer', { location: origin, question: 'open_to_nj', answer: b.dataset.nj });
    if (!yes) track('QualifierBlocked', { location: origin, reason: 'not_open_to_nj' });
    show(yes ? 'q' : 'no-nj');
  }));
  gate.querySelectorAll('[data-answer]').forEach(b => b.addEventListener('click', () => {
    if (Date.now() < armedAt) return;
    interest = b.dataset.answer;
    track('QualifierAnswer', { location: origin, question: 'interest', answer: interest });
    sub.textContent = SUB[interest];
    show('call');
  }));
  gate.querySelectorAll('[data-gate-close]').forEach(el => el.addEventListener('click', close));
  document.addEventListener('keydown', e => {
    if (gate.hidden) return;
    if (e.key === 'Escape') return close();
    if (e.key === 'Tab') {                      // keep focus inside the dialog
      const f = [...gate.querySelectorAll('button, a')].filter(n => n.offsetParent !== null);
      if (!f.length) return;
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    }
  });

  tel.setAttribute('href', 'tel:' + phoneConfig.raw);
  tel.addEventListener('click', () => {
    const params = {
      location: origin,
      via: 'qualifier',
      interest,
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

  document.querySelectorAll('[data-phone-text]').forEach(el => {
    el.textContent = phoneConfig.display;
  });
}

/* ============================================================
   6. THE NUMBERS: prices only, or financing cards with their loan example
   ============================================================ */
const blank = v => v || '[from lender]';

function loanExampleText(s) {
  const L = s.loan;
  return `Example, to a qualified buyer: ${money(propertyConfig.price)} price, ${money(s.downPayment)} (${s.downPct}) down, ` +
    `${blank(L.kind)} loan of ${L.noteAmount ? money(L.noteAmount) : '[from lender]'}${L.noteAmountNote ? ' ' + L.noteAmountNote : ''}, ` +
    `${L.payments || '[from lender]'} monthly payments of ${L.principalInterest ? money(L.principalInterest) : '[from lender]'} principal and interest ` +
    `at ${blank(L.rate)} interest, ${L.apr || '[APR from lender]'} APR, rate as of ${blank(L.rateDate)}. ` +
    `The monthly housing payment above also includes property taxes and insurance.`;
}

function renderCards() {
  const shown = shownScenarios();
  const fin = shown.length > 0;
  document.documentElement.classList.toggle('fin-on', fin);
  document.querySelectorAll('[data-fin="on"]').forEach(el => { el.hidden = !fin; });
  document.querySelectorAll('[data-fin="off"]').forEach(el => { el.hidden = fin; });

  const facts = {
    price: money(propertyConfig.price),
    taxes: money(propertyConfig.taxes),
    rent: money(rentConfig.amount)
  };
  document.querySelectorAll('[data-fact]').forEach(el => {
    const k = el.dataset.fact;
    if (k in facts) el.textContent = facts[k];
  });

  const host = document.getElementById('financingCards');
  if (host) {
    // without a complete lender quote nothing is rendered, not even hidden
    host.hidden = !fin;
    host.innerHTML = shown.map(s => {
      const effective = s.monthlyPayment - rentConfig.amount;
      return `
      <article class="card${s.badge ? ' card--best' : ''}">
        ${s.badge ? `<span class="card__badge">${s.badge}</span>` : ''}
        <h3 class="card__name">${s.name}</h3>
        <p class="card__down">${s.downPct} Down</p>
        <div class="card__rows">
          <div class="card__row">
            <span class="card__k">Est. down payment</span>
            <span class="card__v">${money(s.downPayment)}</span>
          </div>
          <div class="card__row">
            <span class="card__k">Est. monthly housing payment</span>
            <span class="card__v">${money(s.monthlyPayment)}</span>
          </div>
          <div class="card__row card__row--rent">
            <span class="card__k">${rentConfig.label}<span class="card__ksub">${rentConfig.sub}</span></span>
            <span class="card__v">&minus;${money(rentConfig.amount)}</span>
          </div>
        </div>
        <div class="card__net">
          <p class="card__net-k">Estimated effective monthly cost</p>
          <p class="card__net-v">${money(effective)}</p>
          <p class="card__net-sub">per month, estimated</p>
        </div>
        <p class="card__loan">${loanExampleText(s)}</p>
        <a class="btn btn--call" href="#" data-call data-loc="card-${s.id}">Call Imbar</a>
      </article>`;
    }).join('');
  }

  const text = disclosure();
  const note = document.getElementById('mathDisclosure');
  if (note) note.textContent = text;
  document.querySelectorAll('[data-disclosure-copy]').forEach(el => { el.textContent = text; });
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
