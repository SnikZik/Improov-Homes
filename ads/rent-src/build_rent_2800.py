"""27 Oct 2026: stills for the second unit, 3 bed 2 bath, $2,800 a month, for rent or rent to own.

Same look as the rent-to-own feed still (ads/rto-src/build_rto_video.py still_html): the house on
top, the offer below. We have no photos of the second unit yet, so the photo is the front of the
house: the same straight-on frame of the whole house the open house stills use (the walkthrough at
0.7 s, with a blurred copy behind it). Pass the walkthrough path as the first argument.
Two versions of each size: with the open house line (this week) and without (after 1 Nov).
Usage: python3 ads/rent-src/build_rent_2800.py
"""
import subprocess, pathlib, base64, html, sys, os
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'ads' / 'rent-2800'
WORK = OUT / '_work'
FONT = "'Helvetica Neue',Helvetica,Arial,sans-serif"
WORKLIST = 'New roof. New central air. New kitchens in both units. Updated baths. Refinished wood floors.'
OH_LINE = 'Open house: Sat 10/31, 12 to 2 · Sun 11/1, 1 to 3'
EHO = """<svg viewBox="0 0 64 64" width="60" height="60"><path d="M4 30 32 10l28 20" fill="none" stroke="currentColor" stroke-width="4"/>
<path d="M11 30v22h42V30" fill="none" stroke="currentColor" stroke-width="4"/><rect x="22" y="33" width="20" height="5" fill="currentColor"/>
<rect x="22" y="43" width="20" height="5" fill="currentColor"/></svg>"""

def page(bg_uri, w, h, photo_h, open_house):
    story = h > 1500
    top = 300 if story else 0
    oh = f'<p class="oh">{html.escape(OH_LINE)}</p>' if open_house else ''
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden;font-family:{FONT};-webkit-font-smoothing:antialiased;background:#0F1512}}
.photo{{position:absolute;left:0;top:0;width:{w}px;height:{photo_h}px;background:url('{bg_uri}') center 22%/cover}}
.photo::after{{content:"";position:absolute;inset:auto 0 0 0;height:140px;background:linear-gradient(rgba(15,21,18,0),#0F1512)}}
.pill{{position:absolute;left:56px;top:{52 + top}px;background:#C9A24E;color:#0F1512;font-weight:800;font-size:{34 if story else 30}px;letter-spacing:.08em;text-transform:uppercase;padding:12px 20px 10px;border-radius:10px}}
.body{{position:absolute;left:0;top:{photo_h - 30}px;width:100%;bottom:{250 if story else 0}px;padding:0 56px 44px;color:#fff;display:flex;flex-direction:column}}
.rent{{font-size:{132 if story else 120}px;font-weight:800;letter-spacing:-.045em;line-height:.95}}
.rent small{{font-size:{50 if story else 46}px;font-weight:700;color:#C8D2CC;letter-spacing:-.02em}}
.what{{margin-top:{22 if story else 18}px;font-size:{48 if story else 44}px;font-weight:800;letter-spacing:-.02em;line-height:1.12}}
.addr{{margin-top:8px;font-size:{36 if story else 32}px;font-weight:700;color:#C8D2CC;letter-spacing:-.01em}}
.work{{margin-top:{16 if story else 12}px;font-size:{31 if story else 28}px;color:#fff;font-weight:600;line-height:1.28;letter-spacing:-.01em}}
.oh{{margin-top:{18 if story else 14}px;align-self:flex-start;background:rgba(201,162,78,.16);border:2px solid #C9A24E;color:#fff;border-radius:12px;padding:10px 16px 9px;font-size:{32 if story else 28}px;font-weight:800;letter-spacing:-.01em}}
.ask{{margin-top:{16 if story else 12}px;font-size:{34 if story else 31}px;color:#C8D2CC;font-weight:600;line-height:1.3}}
.ask b{{color:#fff;white-space:nowrap}}
.legal{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;color:#C8D2CC;font-size:{24 if story else 22}px;font-weight:500;line-height:1.35}}
.legal b{{color:#fff;font-size:{29 if story else 27}px;display:block}}
.eho{{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none;color:#C8D2CC}}
.eho i{{font-style:normal;font-size:14px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-align:center;line-height:1.15}}
</style></head><body>
<div class="photo"></div><div class="pill">For rent or rent to own</div>
<div class="body">
<p class="rent">$2,800<small> a month</small></p>
<p class="what">3 bed · 2 bath</p>
<p class="addr">1057 Bond St · Elizabeth, New Jersey</p>
<p class="work">{html.escape(WORKLIST)}</p>
{oh}
<p class="ask">Rent, or rent with an option to buy. <b>Call Roi at (551) 324-1057.</b></p>
<div class="legal"><p><b>Improov Homes, Licensed Real Estate Broker</b>Office (973) 743-9333<br>Terms on request. Subject to application approval.</p><span class="eho">{EHO}<i>Equal Housing<br>Opportunity</i></span></div>
</div></body></html>"""

def main():
    for t in [OH_LINE, WORKLIST]:
        if any(c in t for c in ('—', '–', '--')):
            sys.exit('dash in copy')
    WORK.mkdir(parents=True, exist_ok=True)
    walk = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/s/Downloads/WhatsApp Video 2026-10-21 at 16.22.19.mp4')
    def still_bg(h):
        out = WORK / f'still-{h}.jpg'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '0.7', '-i', str(walk), '-frames:v', '1',
             '-filter_complex', f'[0]split[a][b];[a]scale=1080:-2,crop=1080:{h},boxblur=24:2,eq=brightness=-0.12:saturation=0.85[bg];'
             f'[b]scale=-2:{h}:flags=lanczos,unsharp=5:5:0.7[fg];[bg][fg]overlay=(W-w)/2:0', '-q:v', '2', str(out)], check=True)
        return 'data:image/jpeg;base64,' + base64.b64encode(out.read_bytes()).decode()
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(device_scale_factor=1)
        for oh in (True, False):
            tag = 'rent-2800' + ('_open-house' if oh else '')
            for (w, h, ph, name) in ((1080, 1350, 600, 'feed-4x5'), (1080, 1920, 860, 'story-9x16')):
                pg.set_viewport_size({'width': w, 'height': h})
                pg.set_content(page(still_bg(ph), w, h, ph, oh), wait_until='load')
                pg.screenshot(path=str(OUT / f'{tag}_{name}.png'), full_page=False)
        b.close()
    print('done', sorted(x.name for x in OUT.glob('*.png')))

if __name__ == '__main__':
    main()
