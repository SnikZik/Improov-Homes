/* ============================================================
   1057 Bond Street — New York audience page
   Same call-only rules as the main page, plus a two-question
   qualifier between every call button and the phone line.
   Every number on the page lives in the config blocks below.
   ============================================================ */

/* ---------- 1. PHONE ----------
   NY tracking number. Until Imbar's NY line is in, this falls back to the
   main campaign number so the page still works; the CallButtonClick events
   are tagged page=bond-street-1057-ny either way.
   Snir's rule (Oct 2026): this number is shown and dialed only in the
   qualifier's last step, after both questions. Never put it anywhere else. */
const phoneConfig = {
  raw: '+15513241057',          // TODO: replace with the dedicated NY number (E.164)
  display: '(551) 324-1057',    // TODO: same number, formatted
  isPlaceholder: true           // flip to false once the NY number is in
};

/* Brokerage office line. NJ requires a standalone listing page to show the
   brokerage's phone number as large as the page's predominant wording. It is
   shown as plain text so it does not bypass the qualifier. */
const officeConfig = {
  display: '(973) 743-9333'
};

/* ---------- 2. CALL HOURS ----------
   Imbar asked to stop calls coming in too early. Outside these hours the
   qualifier still runs, but the last step shows the number and when to call
   instead of a tap-to-call button. Set enforce:false to allow taps any time. */
const hoursConfig = {
  tz: 'America/New_York',
  open: 9,                      // 9:00 AM
  close: 19,                    // 7:00 PM
  days: [0, 1, 2, 3, 4, 5, 6],  // 0 = Sunday
  enforce: true,
  label: '9 AM to 7 PM Eastern, seven days a week'
};

/* ---------- 3. QUALIFIER ----------
   From the 6 Oct call: two questions before the phone line. "No" to the New
   Jersey question ends at a polite message with the office number and no
   tap-to-call. The rental question is informational and always continues. */
const gateConfig = {
  blockOnNoNJ: true,            // "Would you live in New Jersey?" -> No
  blockOnNoIncome: false,       // "Is rental income part of your plan?" -> Not really. Off: blocking it would
                                //  screen out buyers who want the whole house for their own household (fair housing)
  rememberPass: true            // a visitor who passed goes straight to the call step
};

/* ---------- 4. THE HOUSE ----------
   Checked against GSMLS #4057212, the 2025 tax bill and Improov's own rental
   listings (fact-check run 15 Oct 2026). */
const subject = {
  price: 899000,               // cut from $999,000 (Oct 2026)
  downPercent: '3.5%',
  downPayment: 31465,
  closing: 25000,               // estimate; MLS says the seller will give a concession
  cashToClose: 56465,
  beds: 8,
  baths: 5,
  sqft: '2,700',                // MLS; Roee's sheet said 2,800, no source has that
  taxes: 11892,                 // 2025 bill. Roee's $14,144 was the 2023 bill
  unit2Rent: '$2,750'           // Improov's live listing for Unit 2 (Imbar's video says $2,700 to $3,000)
};

/* ---------- 5. FINANCING SWITCH (Reg Z) ----------
   Down payment, cash to close and monthly payment are "triggering terms":
   once any of them is on the page, the page must also give the APR and the
   repayment terms. Until the lender sends the APR, leave apr empty and the
   page hides every financing number automatically and shows prices only.
   Paste the lender's APR here and the financing rows come back with the
   full disclosure. */
const loanExample = {
  apr: '',                      // e.g. '7.812%' from the lender, in writing
  rate: '6.875%',
  rateDate: 'Oct 1, 2026',
  noteAmount: 882717,           // $867,535 base loan + 1.75% upfront MIP
  payments: 360,
  principalInterest: 5799
};
const showFinancing = () => Boolean(loanExample.apr) ||
  (/^(localhost|127\.0\.0\.1|\[::1\])$/.test(window.location.hostname) && /[?&]preview_financing=1(&|$)/.test(window.location.search));

/* ---------- 6. COMPARISON ----------
   Closed sales, last six months. Two of Roee's three comps are left out:
   203 Essex St, Brooklyn (its $1.25M deed also bought the vacant lot next door)
   and 185 Bennett Ave, Yonkers (3 units and 3,785 sq ft, not like-for-like).
   Ask Roee for clean two-family sales to add back. */
const comparisonConfig = {
  eyebrow: 'Two-family comparison · October 2026',
  properties: [
    {
      id: 'bond', highlight: true,
      name: '1057 Bond St', area: 'Elizabeth, NJ 07201', status: 'For sale · newly renovated',
      price: 899000, priceNote: 'list price',
      layout: '8 bed · 5 bath', layoutNote: 'Two 3 bed / 2 bath units plus a 2 bed / 1 bath bonus area',
      sqft: '2,700 sq ft', parking: '1-car garage + 2-car driveway',
      taxes: 11892, taxesNote: '2025 bill',
      buyerTaxes: 'No mortgage tax', buyerTaxesNote: 'No buyer transfer or mansion tax at this price',
      // financing rows, shown only when loanExample.apr is set
      down: 31465, closing: 25000, cash: 56465, monthly: 7583,
      income: 138000, incomeNote: 'Counts 75% of Unit 2’s $2,750 asking rent'
    },
    {
      id: 'laurelton',
      name: '144-11 223rd St', area: 'Laurelton, Queens', status: 'Sold Jun 12, 2026',
      price: 1295000, priceNote: 'sold price',
      layout: '6 bed · 5 bath', layoutNote: 'Two 3 bed units, finished basement',
      sqft: '2,271 sq ft', parking: 'Detached 1-car garage + driveway',
      taxes: 10670, taxesEst: true, taxesNote: 'Est. FY2027, now assessed as a two-family',
      buyerTaxes: '1.925% + 1%', buyerTaxesNote: 'NYC mortgage tax plus NY mansion tax',
      down: 45325, closing: 63000, cash: 108000, monthly: 10298,
      income: 192000, incomeNote: 'Counts 75% of ~$3,200 est. rent'
    }
  ]
};

const disclosure = () => {
  const base =
    `Comparables are closed sales from the past six months; sale price from the public deed record (NYC ACRIS) and closed-sale listing data (OneKey MLS via Redfin). ` +
    `Property taxes are the latest bill or published assessment and can change. Rent figures are asking rents; both units are vacant and no lease is in place. ` +
    `Train times are from posted NJ Transit weekday timetables, Elizabeth station to New York Penn Station, and vary by train; the house is about 0.6 miles from Elizabeth station. ` +
    `Information is deemed reliable but not guaranteed.`;
  if (!showFinancing()) return base;
  return `Estimates for illustration only, not a loan offer or a commitment to lend. ` +
    `Example for 1057 Bond St: ${money(subject.price)} purchase price, ${money(subject.downPayment)} (${subject.downPercent}) down payment, ` +
    `30-year fixed FHA loan of ${money(loanExample.noteAmount)} including 1.75% upfront mortgage insurance, ` +
    `to a qualified buyer, ${loanExample.payments} monthly principal and interest payments of ${money(loanExample.principalInterest)} at ${loanExample.rate} interest, ${loanExample.apr || '[APR from lender]'} APR. ` +
    `Monthly payments shown also include 0.75% annual mortgage insurance, property taxes and homeowners insurance, so the actual payment is higher than principal and interest alone. ` +
    `Rate as of ${loanExample.rateDate}; rates change daily. Owner-occupied; not every buyer will qualify; subject to lender approval. ` +
    `Household income figures assume a 56% debt-to-income ratio, no other debts, and 75% of the rental unit's asking rent counted as income; many lenders use a lower ratio. ` +
    `Closing costs are estimates and include lender, title and attorney fees plus state and local taxes. ` + base;
};

/* ---------- 7. COMMUTE ---------- */
const commuteConfig = [
  { t: 'NY Penn Station', d: '29 to 40 minutes on NJ Transit from Elizabeth station, 33 on a typical weekday train' },
  { t: 'Elizabeth station', d: 'About 0.6 miles from the house, a 13 minute walk' },
  { t: 'Midtown at 42nd St, door to door', d: 'About 55 to 65 minutes by train and subway, via Penn Station' },
  { t: 'Newark Liberty Airport', d: 'About 10 minutes by car' }
];

/* ---------- 8. VIDEO ---------- */
const videoConfig = {
  hero: { src: '../videos/web/lead-899.mp4', poster: '../videos/web/lead-899-poster.jpg' }   // 9:16 lead with voiceover, new price, no phone number
  // pays-for-itself is not used here: it says "FROM $35,000 DOWN", a Reg Z triggering term
};

/* ---------- 9. ANALYTICS ---------- */
const analyticsConfig = { ga4Id: '' };
const PAGE_ID = 'bond-street-1057-ny';

/* ============================================================
   helpers
   ============================================================ */
const money = n => '$' + Math.round(n).toLocaleString('en-US');
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* ============================================================
   TRACKING (same event names as the main page, so reports line up)
     LandingPageView, ScrollDepth, EngagedTime, SectionView,
     HeroVideoPlay, SectionVideoPlay, VideoProgress,
     HeroVideoComplete, SectionVideoComplete,
     QualifierOpen, QualifierAnswer, QualifierPass, QualifierBlocked,
     CallButtonClick (+ Meta 'Contact'), CallOutsideHours
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

const session = { startedAt: Date.now(), maxScroll: 0, engagedSeconds: 0, videosStarted: 0 };
if (/[?&]lp_debug=1(&|$)/.test(window.location.search)) window.LP_DEBUG = true;

const GA4_EVENT = {
  LandingPageView: null, ScrollDepth: 'scroll_depth', EngagedTime: 'engaged_time',
  SectionView: 'section_view', HeroVideoPlay: 'video_start', SectionVideoPlay: 'video_start',
  VideoProgress: 'video_progress', HeroVideoComplete: 'video_complete',
  SectionVideoComplete: 'video_complete', CallButtonClick: 'call_click',
  QualifierOpen: 'qualifier_open', QualifierAnswer: 'qualifier_answer',
  QualifierPass: 'qualifier_pass', QualifierBlocked: 'qualifier_blocked',
  CallOutsideHours: 'call_outside_hours'
};

const track = (event, params = {}) => {
  const full = { ...attribution, ...params };
  const payload = { event, page: PAGE_ID, ...full };
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
    marks.forEach(m => { if (pct >= m && !hit.has(m)) { hit.add(m); track('ScrollDepth', { percent: m }); } });
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { ticking = true; window.requestAnimationFrame(measure); }
  }, { passive: true });
}

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

function wireSectionViews() {
  if (!('IntersectionObserver' in window)) return;
  const ids = ['price', 'compare', 'commute', 'pays', 'property', 'team', 'final'];
  const obs = new IntersectionObserver((entries, o) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      track('SectionView', { section: e.target.id });
      o.unobserve(e.target);
    });
  }, { rootMargin: '-40% 0px -40% 0px', threshold: 0 });
  ids.forEach(id => { const el = document.getElementById(id); if (el) obs.observe(el); });
}

/* ============================================================
   RENDER
   ============================================================ */
function renderFacts() {
  const fin = showFinancing();
  document.documentElement.classList.toggle('fin-on', fin);
  const comps = comparisonConfig.properties.filter(p => !p.highlight);
  const values = {
    price: money(subject.price),
    downPayment: money(subject.downPayment),
    downPercent: subject.downPercent,
    closing: '~' + money(subject.closing),
    cashToClose: '~' + money(subject.cashToClose),
    taxes: money(subject.taxes),
    compPrice: money(comps[0].price),
    beds: subject.beds,
    baths: subject.baths
  };
  document.querySelectorAll('[data-fact]').forEach(el => {
    const k = el.dataset.fact;
    if (k in values) el.textContent = values[k];
  });
  document.querySelectorAll('.h2 [data-fact="cashToClose"]').forEach(el => { el.textContent = money(subject.cashToClose); });
  const ex = document.getElementById('loanExample');
  if (ex) ex.textContent = fin
    ? `Example, to a qualified buyer: ${money(subject.price)} price, ${money(subject.downPayment)} (${subject.downPercent}) down, ` +
      `30-year fixed FHA loan of ${money(loanExample.noteAmount)}, ${loanExample.payments} monthly payments of ${money(loanExample.principalInterest)} ` +
      `principal and interest at ${loanExample.rate} interest, ${loanExample.apr || '[APR from lender]'} APR. Taxes, insurance and mortgage insurance are extra.`
    : '';
  // financing-only blocks
  document.querySelectorAll('[data-fin="on"]').forEach(el => { el.hidden = !fin; });
  document.querySelectorAll('[data-fin="off"]').forEach(el => { el.hidden = fin; });
}

function renderCompare() {
  const host = document.getElementById('compareTable');
  if (!host) return;
  const fin = showFinancing();
  const props = comparisonConfig.properties;
  const na = 'n/a';
  const opt = (v, f) => (v === null || v === undefined) ? na : f(v);
  const rows = [
    { label: 'Price', v: p => money(p.price), s: p => p.priceNote, big: true, key: true },
    { label: 'Layout', v: p => p.layout, s: p => p.layoutNote },
    { label: 'Living space', v: p => p.sqft },
    { label: 'Parking', v: p => p.parking },
    { label: 'Property taxes', sub: 'estimated, per year', v: p => (p.taxesEst ? '~' : '') + money(p.taxes), s: p => p.taxesNote },
    { label: 'Buyer’s mortgage and transfer taxes', v: p => p.buyerTaxes, s: p => p.buyerTaxesNote },
    { fin: true, label: 'Down payment', sub: '3.5% FHA', v: p => opt(p.down, money) },
    { fin: true, label: 'Est. closing costs', v: p => opt(p.closing, n => '~' + money(n)) },
    { fin: true, label: 'Est. cash to close', v: p => opt(p.cash, n => '~' + money(n)), big: true, key: true },
    { fin: true, label: 'Est. monthly payment', sub: 'Principal, interest, taxes, homeowners and mortgage insurance', v: p => opt(p.monthly, money) },
    { fin: true, label: 'Household income to qualify', sub: 'with rent from the second unit counted', v: p => opt(p.income, n => '~' + money(n)), s: p => p.incomeNote }
  ].filter(r => fin || !r.fin);

  const head = props.map(p => `
      <th scope="col" class="${p.highlight ? 'is-us' : ''}">
        <span class="cmp__status">${esc(p.status)}</span>
        <span class="cmp__name">${esc(p.name)}</span>
        <span class="cmp__area">${esc(p.area)}</span>
      </th>`).join('');

  const body = rows.map(r => `
      <tr class="${r.key ? 'is-key' : ''}">
        <th scope="row"><span class="cmp__k">${esc(r.label)}</span>${r.sub ? `<span class="cmp__ksub">${esc(r.sub)}</span>` : ''}</th>
        ${props.map(p => {
          const sub = r.s ? r.s(p) : '';
          const v = r.v(p);
          return `<td class="${p.highlight ? 'is-us' : ''}${v === na ? ' is-na' : ''}"><span class="cmp__v${r.big ? ' cmp__v--big' : ''}">${esc(v)}</span>${sub ? `<span class="cmp__s">${esc(sub)}</span>` : ''}</td>`;
        }).join('')}
      </tr>`).join('');

  host.style.setProperty('--cmp-min', (140 + props.length * 210) + 'px');
  const fits = props.length <= 2;                 // two columns fit a phone without scrolling
  host.classList.toggle('cmp--fit', fits);
  const hintEl = document.querySelector('.cmp__hint');
  if (hintEl) hintEl.hidden = fits;
  host.innerHTML = `<table><thead><tr><th scope="col" class="cmp__corner"><span class="sr">Compared</span></th>${head}</tr></thead><tbody>${body}</tbody></table>`;

  const eb = document.querySelector('[data-compare-eyebrow]');
  if (eb) eb.textContent = comparisonConfig.eyebrow;
  ['compareDisclosure'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = disclosure();
  });

  const hint = document.querySelector('.cmp__hint');
  host.addEventListener('scroll', () => { if (hint && host.scrollLeft > 20) hint.classList.add('is-gone'); }, { passive: true });
}

function renderLists() {
  const commute = document.getElementById('commuteList');
  if (commute) commute.innerHTML = commuteConfig.map(c =>
    `<li><span class="place__t">${esc(c.t)}</span><span class="place__d">${esc(c.d)}</span></li>`).join('');

  const income = document.getElementById('incomeList');
  if (income) income.innerHTML = [
    `Unit 2 (3 bed, 2 bath) is listed for rent at ${subject.unit2Rent} a month`,
    'Each unit has its own entrance, utilities, heat and AC'
  ].map(t => `<li>${esc(t)}</li>`).join('');

  const specs = document.getElementById('specsList');
  if (specs) specs.innerHTML = [
    ['Two-Family', 'Property type'], [String(subject.beds), 'Bedrooms'], [String(subject.baths), 'Bathrooms'],
    [subject.sqft, 'Sq ft'], ['2026', 'Renovated'], ['Vacant', 'Today'],
    ['Garage', '+ off-street parking'], ['Separate', 'Utilities']
  ].map(([v, k]) => `<li><span class="specs__v">${esc(v)}</span><span class="specs__k">${esc(k)}</span></li>`).join('');

  document.querySelectorAll('[data-hours-text]').forEach(el => { el.textContent = 'We answer ' + hoursConfig.label + '.'; });
  document.querySelectorAll('[data-office-text]').forEach(el => { el.textContent = officeConfig.display; });
}

/* ============================================================
   CALL HOURS
   ============================================================ */
function nowInTz(tz) {
  try {
    const parts = new Intl.DateTimeFormat('en-US', { timeZone: tz, hour12: false, weekday: 'short', hour: '2-digit', minute: '2-digit' })
      .formatToParts(new Date()).reduce((a, p) => { a[p.type] = p.value; return a; }, {});
    const day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(parts.weekday);
    const hour = parseInt(parts.hour, 10) % 24;
    return { day, hour, minute: parseInt(parts.minute, 10) };
  } catch (e) { return null; }
}

function isOpenNow() {
  if (!hoursConfig.enforce) return true;
  const n = nowInTz(hoursConfig.tz);
  if (!n) return true;                       // can't tell, don't block
  if (hoursConfig.days.indexOf(n.day) === -1) return false;
  return n.hour >= hoursConfig.open && n.hour < hoursConfig.close;
}

const fmtHour = h => (h % 12 || 12) + (h < 12 ? ' AM' : ' PM');

/* ============================================================
   QUALIFIER
   ============================================================ */
const STORE_KEY = 'bond_ny_gate';
const gate = {
  el: null, origin: 'unknown', lastFocus: null, answers: {}, armedAt: 0,
  passed() { try { return gateConfig.rememberPass && sessionStorage.getItem(STORE_KEY) === 'pass'; } catch (e) { return false; } },
  remember() { try { sessionStorage.setItem(STORE_KEY, 'pass'); } catch (e) { /* private mode */ } }
};

function showStep(name) {
  gate.armedAt = Date.now() + 400;      // a double tap must not answer the next question too
  gate.el.querySelectorAll('.gate__step').forEach(s => { s.hidden = s.dataset.step !== name; });
  if (name === 'pass') preparePassStep();
  const step = gate.el.querySelector(`.gate__step[data-step="${name}"]`);
  const first = (step && [...step.querySelectorAll('button, a')].find(n => !n.hidden)) || gate.el.querySelector('.gate__x');
  if (first) window.setTimeout(() => first.focus({ preventScroll: true }), 30);
}

function preparePassStep() {
  const tel = gate.el.querySelector('[data-gate-tel]');
  const label = gate.el.querySelector('[data-gate-tel-label]');
  const closed = gate.el.querySelector('[data-gate-closed]');
  const sub = gate.el.querySelector('[data-gate-pass-sub]');
  const open = isOpenNow();

  tel.setAttribute('href', 'tel:' + phoneConfig.raw);
  label.textContent = 'Call ' + phoneConfig.display;
  tel.hidden = !open;
  closed.hidden = open;
  sub.textContent = open
    ? 'Tap to call. We answer ' + hoursConfig.label + '.'
    : 'We answer ' + hoursConfig.label + '.';
  if (!open) {
    closed.innerHTML = `Our line opens at ${fmtHour(hoursConfig.open)} Eastern. Call us then at <strong>${esc(phoneConfig.display)}</strong>.`;
    track('CallOutsideHours', { location: gate.origin });
  }
}

function openGate(origin) {
  gate.origin = origin || 'unknown';
  gate.lastFocus = document.activeElement;
  gate.answers = {};
  gate.el.hidden = false;
  document.documentElement.classList.add('gate-open');
  track('QualifierOpen', { location: gate.origin, returning: gate.passed() });
  showStep(gate.passed() ? 'pass' : 'q1');
}

function closeGate() {
  gate.el.hidden = true;
  document.documentElement.classList.remove('gate-open');
  if (gate.lastFocus && typeof gate.lastFocus.focus === 'function') gate.lastFocus.focus({ preventScroll: true });
}

function answer(q, a) {
  gate.answers[q] = a;
  track('QualifierAnswer', { question: q === 'q1' ? 'open_to_nj' : 'rental_income', answer: a, location: gate.origin });

  if (q === 'q1') {
    if (a === 'no' && gateConfig.blockOnNoNJ) {
      track('QualifierBlocked', { reason: 'not_open_to_nj', location: gate.origin });
      return showStep('no-nj');
    }
    return showStep('q2');
  }
  if (a === 'no' && gateConfig.blockOnNoIncome) {
    track('QualifierBlocked', { reason: 'no_rental_income_plan', location: gate.origin });
    return showStep('no-income');
  }
  gate.remember();
  track('QualifierPass', { location: gate.origin, open_to_nj: gate.answers.q1, rental_income: gate.answers.q2 });
  showStep('pass');
}

function wireGate() {
  gate.el = document.getElementById('gate');
  if (!gate.el) return;

  document.querySelectorAll('[data-call]').forEach(el => {
    el.setAttribute('href', '#call');
    el.addEventListener('click', e => { e.preventDefault(); openGate(el.dataset.loc); });
  });

  gate.el.querySelectorAll('[data-answer]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (Date.now() < gate.armedAt) return;
      const [q, a] = btn.dataset.answer.split(':');
      answer(q, a);
    });
  });

  gate.el.querySelectorAll('[data-gate-close]').forEach(el => el.addEventListener('click', closeGate));
  document.addEventListener('keydown', e => {
    if (gate.el.hidden) return;
    if (e.key === 'Escape') { closeGate(); return; }
    if (e.key === 'Tab') {                      // keep focus inside the dialog
      const f = [...gate.el.querySelectorAll('button:not([hidden]), a:not([hidden])')].filter(n => n.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  const tel = gate.el.querySelector('[data-gate-tel]');
  tel.addEventListener('click', () => {
    const params = {
      location: gate.origin,
      via: 'qualifier',
      phone: phoneConfig.raw,
      seconds_on_page: Math.round((Date.now() - session.startedAt) / 1000),
      engaged_seconds: session.engagedSeconds,
      max_scroll: session.maxScroll,
      videos_started: session.videosStarted
    };
    track('CallButtonClick', params);
    try {
      if (typeof window.fbq === 'function') window.fbq('track', 'Contact', { ...attribution, ...params });
    } catch (e) { /* tracking must never break the page */ }
  });

  if (phoneConfig.isPlaceholder && window.LP_DEBUG) console.warn('[ny] phone is still the main campaign number');
}

/* ============================================================
   VIDEO — first frame + overlay, tap plays from 0 with sound
   ============================================================ */
const players = [];

function setupVideo(video, cover, key) {
  const cfg = videoConfig[key];
  if (cfg) { if (cfg.src) video.src = cfg.src; if (cfg.poster) video.poster = cfg.poster; }
  video.playsInline = true;
  video.setAttribute('webkit-playsinline', '');
  video.muted = true;
  if (key === 'hero') video.preload = 'metadata';
  video.controls = false;

  let started = false;
  players.push(video);

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
    const frame = video.closest('[data-vframe]');
    if (frame) frame.style.aspectRatio = w + ' / ' + h;
  };
  ['loadedmetadata', 'resize', 'loadeddata', 'durationchange'].forEach(ev => {
    video.addEventListener(ev, () => { applyRatio(); applyMeta(); });
  });

  const start = () => {
    players.forEach(v => { if (v !== video && !v.paused) v.pause(); });
    video.muted = false;
    video.volume = 1;
    video.currentTime = 0;
    video.controls = key !== 'hero';
    const p = video.play();
    if (p && typeof p.catch === 'function') {
      p.catch(() => { video.muted = true; video.controls = true; video.play().catch(() => {}); });
    }
    if (cover) cover.hidden = true;
    if (!started) {
      started = true;
      session.videosStarted += 1;
      track(key === 'hero' ? 'HeroVideoPlay' : 'SectionVideoPlay', { video: key });
      if (key === 'hero') document.querySelector('.hero').classList.add('is-playing');
    }
  };
  if (cover) cover.addEventListener('click', start);

  if (key === 'hero') {
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
      if (pct >= m && !progressHit.has(m)) { progressHit.add(m); track('VideoProgress', { video: key, percent: m }); }
    });
  });
  video.addEventListener('ended', () => {
    track(key === 'hero' ? 'HeroVideoComplete' : 'SectionVideoComplete', { video: key });
  });
}

function wireVideos() {
  document.querySelectorAll('video[data-video]').forEach(video => {
    setupVideo(video, video.parentElement.querySelector('.vcover'), video.dataset.video);
  });
  if (!('IntersectionObserver' in window)) return;
  const preloader = new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      if (e.target.preload === 'none') { e.target.preload = 'metadata'; e.target.load(); }
      obs.unobserve(e.target);
    });
  }, { rootMargin: '300px 0px' });
  const pauser = new IntersectionObserver(entries => {
    entries.forEach(e => { if (!e.isIntersecting && !e.target.paused) e.target.pause(); });
  }, { threshold: 0.15 });
  players.forEach(v => { preloader.observe(v); pauser.observe(v); });
}

/* ============================================================
   BOOT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  renderFacts();
  renderCompare();
  renderLists();
  wireGate();
  wireVideos();
  wireScrollDepth();
  wireEngagedTime();
  wireSectionViews();
  track('LandingPageView', { referrer: document.referrer || 'direct' });
});
