"""Build the 1057 Bond rent-to-own Facebook/Instagram video (9:16) and feed stills (4:5).

Footage: Imbar's own edited clips. Their burned-in captions and "FOR SALE" tags are
covered by our top bar and bottom panel, so only the house and Imbar's picture-in-
picture show through. No audio: Meta can add licensed music at upload.

Usage: python3 build_rto_video.py [rent ...]   e.g.  python3 build_rto_video.py 3900 4500
"""
import subprocess, sys, pathlib, html, shutil, base64
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]          # repo root
OUT = ROOT / 'ads' / 'rto'
WORK = pathlib.Path('/private/tmp/claude-501/-Users-s/380d5559-9905-4a9f-8ab1-c17ecde0c63a/scratchpad/rto/work')

CFG = {
    'phone': '(551) 324-1057',   # TODO: rent-to-own campaign number from Imbar
    'address': '1057 Bond St · Elizabeth, NJ',
    'beds': 5, 'baths': 3,
    'price': '$999,000',
}

W, H = 1080, 1920
# Feed shows a 9:16 video cropped to 4:5 (about y 285 to 1635); Reels covers the top
# ~270px with its header. So all text lives between y 300 and 1630, and the footage
# sits in a card in the middle. The card shows the clip from y 160 to 1300: below the
# burned-in FOR SALE tag, above the burned-in captions, Imbar's picture-in-picture whole.
CARD_W, CARD_X, CARD_Y = 740, 170, 676
SRC_TOP, SRC_BOT = 160, 1300
CARD_H = round((SRC_BOT - SRC_TOP) * CARD_W / 1080)

# (source, start, duration, headline, sub)
SCENES = [
    ('videos/pays-for-itself.mp4', 3.5, 4.0, '5 bed · 3 bath on two levels', 'First floor plus a bonus lower level'),
    ('ads/C3_separate-everything.mp4', 28.5, 3.5, 'Renovated in 2026', 'Central air and separate utilities'),
    ('ads/C3_separate-everything.mp4', 46.0, 3.5, 'Bonus lower level', 'Two more bedrooms and a bath'),
    ('ads/C3_separate-everything.mp4', 9.5, 3.0, 'Assigned parking', 'Garage available. Laundry hookups in the unit.'),
    ('ads/C3_separate-everything.mp4', 3.5, 3.5, 'About 33 min by train<br>to NY Penn Station', 'Elizabeth station is 0.6 mi away'),
]
END_DUR = 4.5
XF = 0.35            # crossfade between scenes

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%dpx;height:%dpx;background:transparent;overflow:hidden;
  font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.pill{position:absolute;left:%dpx;top:318px;display:flex;align-items:center;gap:18px}
.pill b{background:#C9A24E;color:#0F1512;font-weight:800;font-size:30px;letter-spacing:.07em;
  text-transform:uppercase;padding:11px 18px 9px;border-radius:10px}
.pill span{color:#fff;font-size:38px;font-weight:800;letter-spacing:-.02em}
.addr{position:absolute;left:%dpx;top:390px;color:#C8D2CC;font-size:32px;font-weight:600}
.txt{position:absolute;left:%dpx;right:%dpx;top:448px;height:212px;display:flex;flex-direction:column;justify-content:center}
.h{color:#fff;font-size:72px;font-weight:800;line-height:1.02;letter-spacing:-.035em;text-wrap:balance}
.s{margin-top:14px;color:#C8D2CC;font-size:34px;font-weight:500;line-height:1.25;letter-spacing:-.01em;text-wrap:balance}
.broker{position:absolute;left:%dpx;right:%dpx;top:%dpx;display:flex;align-items:center;gap:16px;color:#C8D2CC}
.broker p{font-size:25px;font-weight:600;line-height:1.3}
.broker b{color:#fff}
""" % (W, H, CARD_X, CARD_X, CARD_X, CARD_X, CARD_X, CARD_X, CARD_Y + CARD_H + 26)

def chrome_html(rent):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
.frame{{position:absolute;left:{CARD_X}px;top:{CARD_Y}px;width:{CARD_W}px;height:{CARD_H}px;border-radius:30px;
  box-shadow:0 0 0 2000px #0F1512, inset 0 0 0 2px rgba(255,255,255,.16)}}</style></head><body>
<div class="frame"></div>
<div class="pill"><b>Rent-to-own only</b><span>${rent:,}/mo</span></div>
<div class="addr">{html.escape(CFG['address'])}</div>
<div class="broker">{EHO.replace('width="78" height="78"','width="44" height="44"')}<p><b>Improov Homes, Licensed Real Estate Broker</b><br>Office (973) 743-9333</p></div>
</body></html>"""

def text_html(head, sub):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="txt"><p class="h">{head}</p><p class="s">{html.escape(sub)}</p></div></body></html>"""

EHO = """<svg viewBox="0 0 64 64" width="78" height="78"><path d="M4 30 32 10l28 20" fill="none" stroke="currentColor" stroke-width="4"/>
<path d="M11 30v22h42V30" fill="none" stroke="currentColor" stroke-width="4"/><rect x="22" y="33" width="20" height="5" fill="currentColor"/>
<rect x="22" y="43" width="20" height="5" fill="currentColor"/></svg>"""

def end_html(rent):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{background:rgba(15,21,18,.9)}}
.wrap{{position:absolute;inset:0;padding:330px 72px 330px;display:flex;flex-direction:column;color:#fff}}
.k{{align-self:flex-start;background:#C9A24E;color:#0F1512;font-weight:800;font-size:36px;letter-spacing:.08em;
  text-transform:uppercase;padding:14px 24px 12px;border-radius:10px}}
.rent{{margin-top:40px;font-size:140px;font-weight:800;letter-spacing:-.045em;line-height:.95}}
.rent small{{font-size:56px;font-weight:700;letter-spacing:-.02em;color:#C8D2CC}}
.what{{margin-top:26px;font-size:52px;font-weight:700;letter-spacing:-.02em;line-height:1.15}}
.ask{{margin-top:22px;font-size:42px;font-weight:500;color:#C8D2CC;line-height:1.3}}
.call{{margin-top:50px;align-self:stretch;background:#fff;color:#0F1512;border-radius:999px;height:150px;
  display:flex;align-items:center;justify-content:center;gap:22px;font-size:60px;font-weight:800;letter-spacing:-.02em}}
.legal{{margin-top:auto;display:flex;gap:28px;align-items:center;color:#C8D2CC}}
.legal p{{font-size:28px;line-height:1.4;font-weight:500}}
.legal b{{color:#fff;font-size:34px;font-weight:800;display:block;margin-bottom:4px}}
.eho{{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none}}
.eho i{{font-style:normal;font-size:17px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-align:center;line-height:1.15}}
</style></head><body><div class="wrap">
<div class="k">Rent-to-own only</div>
<p class="rent">${rent:,}<small> a month</small></p>
<p class="what">{CFG['beds']} bed · {CFG['baths']} bath on two levels<br>{html.escape(CFG['address'])}</p>
<p class="ask">Rent now with an option to buy.<br>Call for the written terms.</p>
<div class="call"><svg viewBox="0 0 24 24" width="58" height="58" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>{CFG['phone']}</div>
<div class="legal"><span class="eho">{EHO}<i>Equal Housing<br>Opportunity</i></span><p><b>Improov Homes, Licensed Real Estate Broker</b>Imbar Meidani, Principal Broker · Office (973) 743-9333<br>Terms on request. Subject to application approval.</p></div>
</div></body></html>"""

def still_html(rent, bg_uri):
    """4:5 feed still: house photo on top, the offer below."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;background:#0F1512}}
.photo{{position:absolute;left:0;top:0;width:1080px;height:700px;background:url('{bg_uri}') center 22%/cover}}
.pill{{position:absolute;left:56px;top:52px;background:#C9A24E;color:#0F1512;font-weight:800;font-size:30px;letter-spacing:.08em;text-transform:uppercase;padding:12px 20px 10px;border-radius:10px}}
.body{{position:absolute;left:0;top:700px;width:100%;height:650px;padding:52px 56px 44px;color:#fff;display:flex;flex-direction:column}}
.rent{{font-size:120px;font-weight:800;letter-spacing:-.045em;line-height:.95}}
.rent small{{font-size:46px;font-weight:700;color:#C8D2CC;letter-spacing:-.02em}}
.what{{margin-top:22px;font-size:44px;font-weight:700;letter-spacing:-.02em;line-height:1.15}}
.ask{{margin-top:16px;font-size:34px;color:#C8D2CC;font-weight:500;line-height:1.3}}
.legal{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;color:#C8D2CC;font-size:24px;font-weight:500;line-height:1.35}}
.legal b{{color:#fff;font-size:30px;display:block}}
.legal svg{{flex:none}}
.eho{{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none;color:#C8D2CC}}
.eho i{{font-style:normal;font-size:14px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-align:center;line-height:1.15}}
</style></head><body>
<div class="photo"></div><div class="pill">Rent-to-own only</div>
<div class="body">
<p class="rent">${rent:,}<small> a month</small></p>
<p class="what">{CFG['beds']} bed · {CFG['baths']} bath on two levels<br>{html.escape(CFG['address'])}</p>
<p class="ask">Rent now with an option to buy. Call {CFG['phone']} for the written terms.</p>
<div class="legal"><p><b>Improov Homes, Licensed Real Estate Broker</b>Office (973) 743-9333<br>Terms on request. Subject to application approval.</p><span class="eho">{EHO.replace('width="78" height="78"','width="64" height="64"')}<i>Equal Housing<br>Opportunity</i></span></div>
</div></body></html>"""

def run(cmd):
    subprocess.run(cmd, check=True)

def render(page, markup, path, w=W, h=H, transparent=True):
    page.set_viewport_size({'width': w, 'height': h})
    page.set_content(markup, wait_until='load')
    page.screenshot(path=str(path), omit_background=transparent, full_page=False)

def build(rent):
    tag = f'rto-{rent}'
    wd = WORK / tag
    if wd.exists(): shutil.rmtree(wd)
    wd.mkdir(parents=True)
    OUT.mkdir(parents=True, exist_ok=True)

    # background for end card + still: the cleanest facade frame, captions sit below the crop
    bg = wd / 'bg.jpg'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '6', '-i', str(ROOT / 'videos/pays-for-itself.mp4'),
         '-frames:v', '1', '-q:v', '2', str(bg)])
    facade = wd / 'facade.jpg'      # top 820px of the frame: house only, no captions, no PIP
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(bg), '-vf',
         f'crop=1080:820:0:0,scale=-2:{H},crop={W}:{H}', '-q:v', '2', str(facade)])

    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(device_scale_factor=1)
        render(page, chrome_html(rent), wd / 'chrome.png')
        for i, (_, _, _, head, sub) in enumerate(SCENES):
            render(page, text_html(head, sub), wd / f'text{i}.png')
        render(page, end_html(rent), wd / 'end.png')
        # 4:5 still: crop top of the facade frame
        crop = wd / 'still-bg.jpg'
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(bg), '-vf', 'crop=1080:860:0:0', '-q:v', '2', str(crop)])
        uri = 'data:image/jpeg;base64,' + base64.b64encode(crop.read_bytes()).decode()
        render(page, still_html(rent, uri), OUT / f'{tag}_feed-4x5.png', 1080, 1350, transparent=False)
        b.close()

    # scenes: clip + chrome + text fading in
    parts = []
    for i, (src, start, dur, _, _) in enumerate(SCENES):
        out = wd / f's{i}.mp4'
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(start), '-t', str(dur), '-i', str(ROOT / src),
             '-loop', '1', '-t', str(dur), '-i', str(wd / 'chrome.png'),
             '-loop', '1', '-t', str(dur), '-i', str(wd / f'text{i}.png'),
             '-filter_complex',
             f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},'
             f'crop={W}:{SRC_BOT - SRC_TOP}:0:{SRC_TOP},scale={CARD_W}:{CARD_H},fps=30,setsar=1[v];'
             f'color=c=0x0F1512:s={W}x{H}:r=30:d={dur}[bg];[bg][v]overlay={CARD_X}:{CARD_Y}[bv];'
             f'[2:v]format=rgba,fade=t=in:st=0.15:d=0.35:alpha=1[t];'
             f'[bv][1:v]overlay=0:0[c];[c][t]overlay=0:0,format=yuv420p[o]',
             '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(out)])
        parts.append((out, dur))
    # end card over a slow push on the facade
    end = wd / 'end.mp4'
    frames = int(END_DUR * 30)
    # one still frame in, `frames` frames out: zoompan must not see a looped input
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(facade),
         '-loop', '1', '-t', str(END_DUR), '-i', str(wd / 'end.png'),
         '-filter_complex',
         f"[0:v]scale={int(W*1.25)}:{int(H*1.25)},zoompan=z='min(zoom+0.0005,1.06)':d={frames}:s={W}x{H}:fps=30,"
         f"gblur=sigma=6,setsar=1,trim=duration={END_DUR}[bgz];"
         f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1[e];[bgz][e]overlay=0:0:shortest=1,format=yuv420p[o]",
         '-map', '[o]', '-an', '-t', str(END_DUR), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(end)])
    parts.append((end, END_DUR))

    # chain with crossfades
    inputs, fc, prev, offset = [], [], '0:v', 0.0
    for k, (path, dur) in enumerate(parts):
        inputs += ['-i', str(path)]
    acc = parts[0][1]
    for k in range(1, len(parts)):
        offset = acc - XF
        label = f'x{k}'
        fc.append(f'[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[{label}]')
        prev = label
        acc = offset + parts[k][1]
    final = OUT / f'{tag}_reel-9x16.mp4'
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc),
         '-map', f'[{prev}]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-movflags', '+faststart', '-r', '30', str(final)])
    # contact sheet for review
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(final), '-vf', 'fps=1/2,scale=270:-2,tile=6x2',
         '-frames:v', '1', str(WORK / f'{tag}_sheet.jpg')])
    print(final, f'{acc:.1f}s')

if __name__ == '__main__':
    for r in (sys.argv[1:] or ['3900']):
        build(int(r))
