"""Build the 1057 Bond open house creative: a 9:16 reel, a 4:5 feed still and a 9:16 story still.
Same layout as the rent-to-own reel (ads/rto-src): footage in a card inside Meta's safe zones,
offer on top, broker line at the bottom, open house details on the end card.

Footage: Imbar's walkthrough from WhatsApp (464x624, silent) plus two exterior shots from her
earlier 1080x1920 clips. No audio: add music from Meta's library at upload.

Usage: python3 ads/oh-src/build_open_house.py [path/to/walkthrough.mp4]
"""
import subprocess, sys, pathlib, html, shutil, base64
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]          # repo root
OUT = ROOT / 'ads' / 'open-house'
WORK = pathlib.Path('/private/tmp/claude-501/-Users-s/380d5559-9905-4a9f-8ab1-c17ecde0c63a/scratchpad/oh/work')
WALK = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('/Users/s/Downloads/WhatsApp Video 2026-10-21 at 16.22.19.mp4')

CFG = {
    'phone': '(551) 324-1057',
    'address': '1057 Bond St · Elizabeth, NJ',
    'price': '$899,000',
    'cut': 'Price reduced $100,000',
    'dates': [('Sat, Oct 24', '12 to 3 PM'), ('Sun, Oct 25', '1 to 3 PM')],
    'chip': 'Sat 10/24 · Sun 10/25',
    'rto': 'Not ready to buy? Rent to own at $4,500 a month.',
}

W, H = 1080, 1920
CARD_W, CARD_X, CARD_Y = 740, 170, 676
SRC_TOP, SRC_BOT = 160, 1300            # rows of the 1080x1920 clips shown in the card
CARD_H = round((SRC_BOT - SRC_TOP) * CARD_W / 1080)

# (source, start, duration, headline, sub). 'WALK' = the WhatsApp walkthrough.
SCENES = [
    ('videos/pays-for-itself.mp4', 3.5, 3.6, 'Price reduced $100,000', 'Now $899,000'),
    ('WALK', 87.5, 3.0, 'New kitchen', 'Renovated in 2026, central air'),
    ('WALK', 79.0, 2.8, 'Refinished wood floors', 'Legal two-family'),
    ('WALK', 98.6, 3.0, '3 bed · 2 bath', 'On the main level'),
    ('WALK', 33.0, 3.0, 'Finished lower level', 'Two bonus rooms and a full bath'),
    ('ads/C3_separate-everything.mp4', 3.5, 3.4, 'About 33 min by train<br>to NY Penn Station', 'Elizabeth station is 0.6 mi away'),
]
END_DUR = 5.0
XF = 0.35

FONT = "'Helvetica Neue',Helvetica,Arial,sans-serif"
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%dpx;height:%dpx;background:transparent;overflow:hidden;font-family:%s;-webkit-font-smoothing:antialiased}
.pill{position:absolute;left:%dpx;top:318px;display:flex;align-items:center;gap:18px}
.pill b{background:#C9A24E;color:#0F1512;font-weight:800;font-size:30px;letter-spacing:.07em;
  text-transform:uppercase;padding:11px 18px 9px;border-radius:10px}
.pill span{color:#fff;font-size:34px;font-weight:800;letter-spacing:-.01em}
.addr{position:absolute;left:%dpx;top:390px;color:#C8D2CC;font-size:32px;font-weight:600}
.txt{position:absolute;left:%dpx;right:%dpx;top:448px;height:212px;display:flex;flex-direction:column;justify-content:center}
.h{color:#fff;font-size:72px;font-weight:800;line-height:1.02;letter-spacing:-.035em;text-wrap:balance}
.s{margin-top:14px;color:#C8D2CC;font-size:34px;font-weight:500;line-height:1.25;letter-spacing:-.01em;text-wrap:balance}
.broker{position:absolute;left:%dpx;right:%dpx;top:%dpx;display:flex;align-items:center;gap:16px;color:#C8D2CC}
.broker p{font-size:25px;font-weight:600;line-height:1.3}
.broker b{color:#fff}
""" % (W, H, FONT, CARD_X, CARD_X, CARD_X, CARD_X, CARD_X, CARD_X, CARD_Y + CARD_H + 26)

EHO = """<svg viewBox="0 0 64 64" width="78" height="78"><path d="M4 30 32 10l28 20" fill="none" stroke="currentColor" stroke-width="4"/>
<path d="M11 30v22h42V30" fill="none" stroke="currentColor" stroke-width="4"/><rect x="22" y="33" width="20" height="5" fill="currentColor"/>
<rect x="22" y="43" width="20" height="5" fill="currentColor"/></svg>"""
PHONE = """<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>"""
BROKER = 'Improov Homes, Licensed Real Estate Broker'
OFFICE = 'Imbar Meidani, Principal Broker · Office (973) 743-9333'


def chrome_html():
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
.frame{{position:absolute;left:{CARD_X}px;top:{CARD_Y}px;width:{CARD_W}px;height:{CARD_H}px;border-radius:30px;
  box-shadow:0 0 0 2000px #0F1512, inset 0 0 0 2px rgba(255,255,255,.16)}}</style></head><body>
<div class="frame"></div>
<div class="pill"><b>Open house</b><span>{CFG['chip']}</span></div>
<div class="addr">{html.escape(CFG['address'])} · {CFG['price']}</div>
<div class="broker">{EHO.replace('width="78" height="78"','width="44" height="44"')}<p><b>{BROKER}</b><br>Office (973) 743-9333</p></div>
</body></html>"""


def text_html(head, sub):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="txt"><p class="h">{head}</p><p class="s">{html.escape(sub)}</p></div></body></html>"""


def dates_html(size):
    return ''.join(f'<p class="d"><b>{d}</b> · {t}</p>' for d, t in CFG['dates'])


def end_html():
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{background:rgba(15,21,18,.9)}}
.wrap{{position:absolute;inset:0;padding:320px 72px 300px;display:flex;flex-direction:column;color:#fff}}
.k{{align-self:flex-start;background:#C9A24E;color:#0F1512;font-weight:800;font-size:36px;letter-spacing:.08em;
  text-transform:uppercase;padding:14px 24px 12px;border-radius:10px}}
.cut{{margin-top:34px;font-size:40px;font-weight:700;color:#E6C77E;letter-spacing:-.01em}}
.price{{margin-top:6px;font-size:150px;font-weight:800;letter-spacing:-.045em;line-height:.95}}
.dates{{margin-top:34px;display:grid;gap:10px}}
.d{{font-size:50px;font-weight:600;letter-spacing:-.02em;color:#C8D2CC}}
.d b{{color:#fff;font-weight:800}}
.addr2{{margin-top:22px;font-size:40px;font-weight:600;color:#C8D2CC}}
.call{{margin-top:40px;align-self:stretch;background:#fff;color:#0F1512;border-radius:999px;height:140px;
  display:flex;align-items:center;justify-content:center;gap:22px;font-size:56px;font-weight:800;letter-spacing:-.02em}}
.rto{{margin-top:26px;font-size:36px;font-weight:600;color:#fff;text-align:center}}
.legal{{margin-top:auto;display:flex;gap:28px;align-items:center;color:#C8D2CC}}
.legal p{{font-size:28px;line-height:1.4;font-weight:500}}
.legal b{{color:#fff;font-size:32px;font-weight:800;display:block;margin-bottom:4px}}
.eho{{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none}}
.eho i{{font-style:normal;font-size:17px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-align:center;line-height:1.15}}
</style></head><body><div class="wrap">
<div class="k">Open house</div>
<p class="cut">{CFG['cut']}</p>
<p class="price">{CFG['price']}</p>
<div class="dates">{dates_html(50)}</div>
<p class="addr2">{html.escape(CFG['address'])}</p>
<div class="call">{PHONE.format(s=54)}Call {CFG['phone']}</div>
<p class="rto">{CFG['rto']}</p>
<div class="legal"><span class="eho">{EHO}<i>Equal Housing<br>Opportunity</i></span><p><b>{BROKER}</b>{OFFICE}</p></div>
</div></body></html>"""


def still_html(bg_uri, w, h, photo_h):
    """Feed (4:5) and story (9:16) stills: house photo on top, the open house below."""
    story = h > 1500
    pad_top = 300 if story else 0          # story: keep clear of the top 14% (profile bar)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden;font-family:{FONT};-webkit-font-smoothing:antialiased;background:#0F1512}}
.photo{{position:absolute;left:0;top:0;width:{w}px;height:{photo_h}px;background:url('{bg_uri}') center 22%/cover}}
.photo::after{{content:"";position:absolute;inset:auto 0 0 0;height:140px;background:linear-gradient(rgba(15,21,18,0),#0F1512)}}
.pill{{position:absolute;left:56px;top:{52 + pad_top}px;background:#C9A24E;color:#0F1512;font-weight:800;font-size:{34 if story else 30}px;letter-spacing:.08em;text-transform:uppercase;padding:12px 20px 10px;border-radius:10px}}
.body{{position:absolute;left:0;top:{photo_h - 40}px;width:100%;bottom:{250 if story else 0}px;padding:0 56px 44px;color:#fff;display:flex;flex-direction:column}}
.cut{{font-size:{38 if story else 34}px;font-weight:700;color:#E6C77E}}
.price{{margin-top:4px;font-size:{136 if story else 116}px;font-weight:800;letter-spacing:-.045em;line-height:.95}}
.dates{{margin-top:{30 if story else 22}px;display:grid;gap:8px}}
.d{{font-size:{46 if story else 40}px;font-weight:600;letter-spacing:-.02em;color:#C8D2CC}}
.d b{{color:#fff;font-weight:800}}
.addr2{{margin-top:{18 if story else 14}px;font-size:{36 if story else 32}px;font-weight:600;color:#C8D2CC}}
.call{{margin-top:{30 if story else 22}px;font-size:{44 if story else 36}px;font-weight:800;display:flex;align-items:center;gap:14px}}
.rto{{margin-top:{14 if story else 10}px;font-size:{32 if story else 28}px;font-weight:500;color:#C8D2CC}}
.legal{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;color:#C8D2CC;font-size:{24 if story else 22}px;font-weight:500;line-height:1.35}}
.legal b{{color:#fff;font-size:{29 if story else 27}px;display:block}}
.eho{{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none;color:#C8D2CC}}
.eho i{{font-style:normal;font-size:14px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-align:center;line-height:1.15}}
</style></head><body>
<div class="photo"></div><div class="pill">Open house</div>
<div class="body">
<p class="cut">{CFG['cut']}</p>
<p class="price">{CFG['price']}</p>
<div class="dates">{dates_html(40)}</div>
<p class="addr2">{html.escape(CFG['address'])}</p>
<p class="call">{PHONE.format(s=40 if story else 34)}Call {CFG['phone']}</p>
<p class="rto">{CFG['rto']}</p>
<div class="legal"><p><b>{BROKER}</b>{OFFICE}</p><span class="eho">{EHO.replace('width="78" height="78"','width="60" height="60"')}<i>Equal Housing<br>Opportunity</i></span></div>
</div></body></html>"""


def run(cmd):
    subprocess.run(cmd, check=True)


def render(page, markup, path, w=W, h=H, transparent=True):
    page.set_viewport_size({'width': w, 'height': h})
    page.set_content(markup, wait_until='load')
    page.screenshot(path=str(path), omit_background=transparent, full_page=False)


def guard():
    """No em dash, en dash or double hyphen in anything a viewer reads."""
    texts = [v for v in CFG.values() if isinstance(v, str)] + [d + t for d, t in CFG['dates']]
    texts += [s[3] + s[4] for s in SCENES] + [BROKER, OFFICE]
    bad = [t for t in texts if any(c in t for c in ('—', '–', '--'))]
    if bad:
        sys.exit(f'dash in copy: {bad}')


def build():
    guard()
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    OUT.mkdir(parents=True, exist_ok=True)

    bg = WORK / 'bg.jpg'            # cleanest facade frame from the 1080x1920 clip
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '6', '-i', str(ROOT / 'videos/pays-for-itself.mp4'),
         '-frames:v', '1', '-q:v', '2', str(bg)])
    facade = WORK / 'facade.jpg'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(bg), '-vf',
         f'crop=1080:820:0:0,scale=-2:{H},crop={W}:{H}', '-q:v', '2', str(facade)])
    crop = WORK / 'still-bg.jpg'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(bg), '-vf', 'crop=1080:860:0:0', '-q:v', '2', str(crop)])
    uri = 'data:image/jpeg;base64,' + base64.b64encode(crop.read_bytes()).decode()

    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(device_scale_factor=1)
        render(page, chrome_html(), WORK / 'chrome.png')
        for i, s in enumerate(SCENES):
            render(page, text_html(s[3], s[4]), WORK / f'text{i}.png')
        render(page, end_html(), WORK / 'end.png')
        render(page, still_html(uri, 1080, 1350, 720), OUT / 'open-house_feed-4x5.png', 1080, 1350, transparent=False)
        render(page, still_html(uri, 1080, 1920, 1000), OUT / 'open-house_story-9x16.png', 1080, 1920, transparent=False)
        b.close()

    parts = []
    for i, (src, start, dur, _, _) in enumerate(SCENES):
        out = WORK / f's{i}.mp4'
        path = WALK if src == 'WALK' else ROOT / src
        if src == 'WALK':
            # 464x624 portrait: take a card-shaped window from the middle, upscale into the card
            fit = (f'[0:v]crop=iw:iw*{CARD_H}/{CARD_W}:0:(ih-iw*{CARD_H}/{CARD_W})/2,'
                   f'scale={CARD_W}:{CARD_H}:flags=lanczos,unsharp=5:5:0.6,fps=30,setsar=1[v];')
        else:
            fit = (f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},'
                   f'crop={W}:{SRC_BOT - SRC_TOP}:0:{SRC_TOP},scale={CARD_W}:{CARD_H},fps=30,setsar=1[v];')
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(start), '-t', str(dur), '-i', str(path),
             '-loop', '1', '-t', str(dur), '-i', str(WORK / 'chrome.png'),
             '-loop', '1', '-t', str(dur), '-i', str(WORK / f'text{i}.png'),
             '-filter_complex',
             fit +
             f'color=c=0x0F1512:s={W}x{H}:r=30:d={dur}[bg];[bg][v]overlay={CARD_X}:{CARD_Y}[bv];'
             f'[2:v]format=rgba,fade=t=in:st=0.15:d=0.35:alpha=1[t];'
             f'[bv][1:v]overlay=0:0[c];[c][t]overlay=0:0,format=yuv420p[o]',
             '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(out)])
        parts.append((out, dur))

    end = WORK / 'end.mp4'
    frames = int(END_DUR * 30)
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(facade),
         '-loop', '1', '-t', str(END_DUR), '-i', str(WORK / 'end.png'),
         '-filter_complex',
         f"[0:v]scale={int(W*1.25)}:{int(H*1.25)},zoompan=z='min(zoom+0.0005,1.06)':d={frames}:s={W}x{H}:fps=30,"
         f"gblur=sigma=6,setsar=1,trim=duration={END_DUR}[bgz];"
         f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1[e];[bgz][e]overlay=0:0:shortest=1,format=yuv420p[o]",
         '-map', '[o]', '-an', '-t', str(END_DUR), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(end)])
    parts.append((end, END_DUR))

    inputs, fc, prev = [], [], '0:v'
    for path, _ in parts:
        inputs += ['-i', str(path)]
    acc = parts[0][1]
    for k in range(1, len(parts)):
        offset = acc - XF
        fc.append(f'[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[x{k}]')
        prev = f'x{k}'
        acc = offset + parts[k][1]
    final = OUT / 'open-house_reel-9x16.mp4'
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc),
         '-map', f'[{prev}]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-movflags', '+faststart', '-r', '30', str(final)])
    print(final, f'{acc:.1f}s')


if __name__ == '__main__':
    build()
