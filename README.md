# 1057 Bond Street, Elizabeth NJ — Improov Homes
Call-only landing page. No form, no WhatsApp, no email, no scheduler, no nav, no outbound links.
Every CTA points at one `tel:` number.

## Files
- `index.html` — structure
- `styles.css` — design, mobile-first
- `app.js` — phone, financing numbers, video sources, tracking (all config at top)
- `videos/` — put the mp4s here
- `img/` — posters + Imbar portrait

## Before launch
1. **Phone** — `app.js` → `phoneConfig.raw` + `.display`. Nothing else to change.
2. **Videos** — the real edited files are already in place (downloaded 2026-08-27 from
   Drive folder `אמבר מידיאני - Improv Home / חומרים ערוכים`, byte-for-byte, not re-encoded):

   | file | source | size | length |
   |---|---|---|---|
   | `videos/hero-15sec-open.mp4` | `C1_15sec-open - טוב.mp4` | 11.7 MB | 0:15 |
   | `videos/pays-for-itself.mp4` | `A3_pays-for-itself.mp4` | 33.6 MB | 0:56 |
   | `videos/almost-a-million.mp4` | `B4_almost-a-million.mp4` | 40.5 MB | 1:12 |

   All three are 1080×1920 (9:16). Only the hero loads on page open; the other two
   load when they come near the viewport.

3. **Portrait** — `img/imbar.jpg` (portrait crop, ~720×900).
4. **Posters** — after replacing any mp4, run:

```bash
./make-posters.sh
```

It pulls the first frame of every file in `videos/` into `img/<name>-poster.jpg`.
The poster is what makes the section read as a video before anyone taps it.

## Tracking
`app.js` fires: `LandingPageView`, `HeroVideoPlay`, `HeroVideoComplete`, `CallButtonClick`
(plus `SectionVideoPlay` / `SectionVideoComplete`). Each one goes to `dataLayer`,
`gtag`, `fbq` when present, and always as a DOM event `lp:<EventName>`.
`CallButtonClick` carries `location` (hero, card-fha, sticky, final, …).
Set `window.LP_DEBUG = true` in console to log events.

## Type
Headlines: Instrument Serif. Everything else: Public Sans. Both loaded from Google Fonts
in `index.html`; the two variables `--display` and `--sans` at the top of `styles.css`
are the only place to change them.

## Unused videos (available if needed)
`B2_fha-and-cra.mp4`, `A9_mortgage-guide.mp4`
