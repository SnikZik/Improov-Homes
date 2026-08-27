/* ============================================================
   1057 Bond Street — Improov Homes
   Single source of truth for phone, financing numbers, videos.
   ============================================================ */

/* ---------- 1. PHONE (virtual tracking number) ----------
   Change here only. Every CTA on the page reads from this. */
const phoneConfig = {
  raw: '+15555550123',          // TODO: replace with the real virtual number (E.164)
  display: '(555) 555-0123'     // TODO: replace with the same number, formatted
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
  hero:    { src: 'videos/hero-15sec-open.mp4',  poster: 'img/hero-15sec-open-poster.jpg'  }, // C1_15sec-open - טוב.mp4
  pays:    { src: 'videos/pays-for-itself.mp4',  poster: 'img/pays-for-itself-poster.jpg'  }, // A3_pays-for-itself.mp4
  million: { src: 'videos/almost-a-million.mp4', poster: 'img/almost-a-million-poster.jpg' }  // B4_almost-a-million.mp4
  // unused for now: B2_fha-and-cra.mp4, A9_mortgage-guide.mp4
};

/* ============================================================
   4. TRACKING HOOKS
   Events: LandingPageView, HeroVideoPlay, HeroVideoComplete, CallButtonClick
   Fans out to dataLayer / gtag / fbq if present, and always fires a
   DOM CustomEvent so a call-tracking script can listen without edits.
   ============================================================ */
const track = (event, params = {}) => {
  const payload = { event, page: 'bond-street-1057', ...params };
  try {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(payload);
    if (typeof window.gtag === 'function') window.gtag('event', event, params);
    if (typeof window.fbq === 'function') window.fbq('trackCustom', event, params);
    document.dispatchEvent(new CustomEvent('lp:' + event, { detail: params }));
    if (window.LP_DEBUG) console.log('[track]', event, params);
  } catch (e) { /* tracking must never break the page */ }
};

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
      track('CallButtonClick', {
        location: el.dataset.loc || 'unknown',
        phone: phoneConfig.raw
      });
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
  track('LandingPageView', { referrer: document.referrer || 'direct' });
});
