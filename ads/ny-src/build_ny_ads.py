"""Static ads for the 1057 Bond New York campaign (sale), feed 4:5 and story 9:16.

No down payment, mortgage payment, rate or term on any creative: those are Reg Z
triggering terms and would force a full credit disclosure inside the ad.
Every number here was verified on 15 Oct 2026 (see ../../ny/README.md). Price cut to $899,000
on 23 Oct 2026: the old $999,000 shows only crossed out. The Laurelton comp ($1,295,000) and
the NYC 1.925% recording tax do not depend on our price, so they stay.

Usage: python3 ads/ny-src/build_ny_ads.py
"""
import subprocess, pathlib, html, base64, re
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'ads' / 'ny'
WORK = pathlib.Path('/private/tmp/claude-501/-Users-s/5f9fd08e-11bf-4ca5-9104-a5feeb1b005b/scratchpad/nyads')

BROKER = 'Improov Homes, Licensed Real Estate Broker'
OFFICE = 'Office (973) 743-9333'

# background frames from Imbar's clips: (source, second, crop y offset). Crops stay
# above the burned-in captions and below the FOR SALE tag.
BGS = {   # (source, second, crop top, crop height): everything above Imbar's picture-in-picture
    'facade':  ('videos/pays-for-itself.mp4', 6.0, 0, 850),
    'bays':    ('ads/C3_separate-everything.mp4', 5.0, 160, 690),
    'door':    ('videos/hero-15sec-open.mp4', 0.0, 0, 850),
    'windows': ('videos/pays-for-itself.mp4', 26.0, 0, 850),
}

# Price cut on 23 Oct 2026: $999,000 -> $899,000. The old price only ever appears
# crossed out ({OLD}) next to the new one ({NEW}); main() refuses to build otherwise.
OLD_PRICE, NEW_PRICE, CUT = '$999,000', '$899,000', '$100,000'

# (id, background, pill, headline, sub, price tag on the photo)
CONCEPTS = [
    ('compare', 'door', f'Price reduced {CUT}',
     '{OLD} {NEW} in Elizabeth, NJ.',
     'A similar two-family in Laurelton, Queens sold for $1,295,000 in June.', False),
    ('train', 'bays', 'For sale · Elizabeth, NJ',
     'A two-family 33 minutes by train from Penn Station.',
     'Elizabeth station is 0.6 miles from the house.', True),
    ('tax', 'windows', 'For sale · Elizabeth, NJ',
     'No mortgage tax for the buyer.',
     'New Jersey has none. In NYC the buyer pays 1.925% of the loan. This two-family is in Elizabeth, NJ.', True),
]

def prices(text):
    """Escape copy, then swap the price tokens for markup (old price always struck)."""
    return (html.escape(text).replace('{OLD}', f'<s class="old">{OLD_PRICE}</s>')
            .replace('{NEW}', f'<span class="new">{NEW_PRICE}</span>'))

EHO = """<svg viewBox="0 0 64 64" width="{s}" height="{s}"><path d="M4 30 32 10l28 20" fill="none" stroke="currentColor" stroke-width="4"/>
<path d="M11 30v22h42V30" fill="none" stroke="currentColor" stroke-width="4"/><rect x="22" y="33" width="20" height="5" fill="currentColor"/>
<rect x="22" y="43" width="20" height="5" fill="currentColor"/></svg>"""

def page_html(w, h, photo_h, bg_uri, pill, head, sub, scale, tag):
    S = lambda px: int(px * scale)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden;background:#0F1512;
  font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}}
.photo{{position:absolute;left:0;top:0;width:{w}px;height:{photo_h}px;background:url('{bg_uri}') center top/cover}}
.pill{{position:absolute;left:{S(56)}px;top:{S(52)}px;background:#C9A24E;color:#0F1512;font-weight:800;font-size:{S(28)}px;
  letter-spacing:.07em;text-transform:uppercase;padding:{S(12)}px {S(20)}px {S(10)}px;border-radius:{S(10)}px}}
.body{{position:absolute;left:0;top:{photo_h}px;width:100%;height:{h-photo_h}px;padding:{S(50)}px {S(56)}px {S(44)}px;color:#fff;display:flex;flex-direction:column}}
.h{{font-size:{S(84)}px;font-weight:800;letter-spacing:-.035em;line-height:1.02;text-wrap:balance}}
.s{{margin-top:{S(22)}px;font-size:{S(38)}px;font-weight:500;color:#C8D2CC;line-height:1.3;letter-spacing:-.01em;text-wrap:balance}}
.legal{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:{S(24)}px;color:#C8D2CC}}
.legal p{{font-size:{S(24)}px;line-height:1.35;font-weight:500}}
.legal b{{display:block;color:#fff;font-size:{S(28)}px;font-weight:800}}
.eho{{display:flex;flex-direction:column;align-items:center;gap:{S(5)}px;flex:none}}
.eho i{{font-style:normal;font-size:{S(13)}px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-align:center;line-height:1.15}}
s{{position:relative;text-decoration:none}}
s::after{{content:'';position:absolute;left:-.05em;right:-.05em;top:43%;height:.09em;margin-top:-.045em;
  background:#C9A24E;border-radius:.05em}}   /* drawn strike: the font's own sits too low */
.h s.old{{font-size:.6em;font-weight:700;color:#9AA9A0;letter-spacing:-.02em;margin-right:.12em}}
.tag{{position:absolute;left:{S(56)}px;top:{photo_h - S(40)}px;transform:translateY(-100%);background:rgba(15,21,18,.92);
  border-radius:{S(18)}px;padding:{S(18)}px {S(28)}px {S(16)}px;color:#fff}}
.tag i{{display:block;font-style:normal;color:#C9A24E;font-weight:800;font-size:{S(24)}px;letter-spacing:.07em;text-transform:uppercase}}
.tag p{{display:flex;align-items:baseline;gap:{S(22)}px;margin-top:{S(4)}px}}
.tag s{{font-size:{S(50)}px;font-weight:700;color:#C8D2CC;letter-spacing:-.02em}}
.tag b{{font-size:{S(92)}px;font-weight:800;letter-spacing:-.04em;line-height:1}}
</style></head><body>
<div class="photo"></div><div class="pill">{html.escape(pill)}</div>
{f'<div class="tag"><i>Price reduced {CUT}</i><p><s>{OLD_PRICE}</s><b>{NEW_PRICE}</b></p></div>' if tag else ''}
<div class="body"><p class="h">{prices(head)}</p><p class="s">{prices(sub)}</p>
<div class="legal"><p><b>{BROKER}</b>{OFFICE}</p>
<span class="eho">{EHO.format(s=S(60))}<i>Equal Housing<br>Opportunity</i></span></div></div>
</body></html>"""

BAD = re.compile(r'[—–]|--')

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    uris = {}
    for k, (src, t, y, ch) in BGS.items():
        f = WORK / f'{k}.jpg'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(t), '-i', str(ROOT / src),
                        '-vf', f'crop=1080:{ch}:0:{y}', '-frames:v', '1', '-q:v', '2', str(f)], check=True)
        uris[k] = 'data:image/jpeg;base64,' + base64.b64encode(f.read_bytes()).decode()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        for cid, bg, pill, head, sub, tag in CONCEPTS:
            for text in (pill, head, sub, BROKER, OFFICE):
                assert not BAD.search(text), f'dash in copy: {text!r}'
                # the old price may only appear struck through
                assert '999' not in re.sub(r'<s class="old">\$999,000</s>', '', prices(text)), f'unstruck old price: {text!r}'
            assert tag or '{NEW}' in head + sub, f'{cid}: new price missing'
            for fmt, (w, h, ph, sc) in {'feed-4x5': (1080, 1350, 700, 1.0), 'story-9x16': (1080, 1920, 1000, 1.12)}.items():
                pg.set_viewport_size({'width': w, 'height': h})
                pg.set_content(page_html(w, h, ph, uris[bg], pill, head, sub, sc, tag), wait_until='load')
                out = OUT / f'ny-{cid}_{fmt}.png'
                pg.screenshot(path=str(out))
                print(out.name)
        b.close()

if __name__ == '__main__':
    main()
