"""Lead videos for the landing pages (9:16, with Gia's voiceover, NO phone number anywhere).

  sale       -> videos/web/lead-899.mp4  (+ lead-899-poster.jpg)       main page and /ny/
  openhouse  -> open-house/media/lead.mp4 (+ open-house/img/lead-poster.jpg)

Same card layout as the ad reels (ads/oh-src, ads/rto-src). The pages hide the campaign number
until the visitor has answered the call questions, so these videos never show or say it.
Voice: vo-sale-gia.wav / vo-openhouse-gia.wav (Higgsfield Seed Audio, Gia, 22 Oct 2026).
Scene lengths follow the sentence breaks of each take.

Usage: python3 ads/lead-src/build_lead_videos.py [sale|openhouse ...]
"""
import subprocess, sys, pathlib, html, shutil
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
WORK = pathlib.Path('/private/tmp/claude-501/-Users-s/5f9fd08e-11bf-4ca5-9104-a5feeb1b005b/scratchpad/lead/work')
WALK = pathlib.Path('/Users/s/Downloads/WhatsApp Video 2026-10-21 at 16.22.19.mp4')
PAYS, C3 = 'videos/pays-for-itself.mp4', 'ads/C3_separate-everything.mp4'

W, H = 1080, 1920
CARD_W, CARD_X, CARD_Y = 740, 170, 676
SRC_TOP, SRC_BOT = 160, 1300
CARD_H = round((SRC_BOT - SRC_TOP) * CARD_W / 1080)
XF = 0.35
BROKER = 'Improov Homes, Licensed Real Estate Broker'
PERSON = 'Imbar Meidani, Principal Broker'

VIDEOS = {
    'sale': {
        'voice': HERE / 'vo-sale-gia.wav',
        'out': ROOT / 'videos/web/lead-899.mp4',
        'poster': ROOT / 'videos/web/lead-899-poster.jpg', 'poster_t': 5.6,
        'pill': 'Price reduced', 'pill_side': 'Elizabeth, New Jersey', 'addr': '1057 Bond St · $899,000',
        # (source, start, duration, headline, sub); sentence breaks at 6.4, 8.3, 13.3, 16.6, 20.3 s
        'scenes': [
            (PAYS, 3.5, 4.35, 'Price reduced $100,000', 'Two-family in Elizabeth, New Jersey'),
            ('WALK', 77.9, 4.35, 'Now $899,000', 'Legal two-family'),
            ('WALK', 86.2, 5.05, 'New kitchen', 'Renovated in 2026, central air'),
            ('WALK', 98.6, 3.85, 'Live in one unit,<br>rent out the other', '3 bed · 2 bath on the main level'),
            (C3, 3.5, 4.05, 'About 33 min by train<br>to NY Penn Station', 'Elizabeth station is 0.6 mi away'),
        ],
        'end_dur': 3.4,
        'end': {'k': 'Price reduced $100,000', 'price': '$899,000', 'lines': ['Legal two-family, renovated in 2026', '1057 Bond St · Elizabeth, New Jersey'], 'extra': ''},
    },
    'openhouse': {
        'voice': HERE / 'vo-openhouse-gia.wav',
        'out': ROOT / 'open-house/media/lead.mp4',
        'poster': ROOT / 'open-house/img/lead-poster.jpg', 'poster_t': 6.6,
        'pill': 'Open house', 'pill_side': 'Elizabeth, New Jersey', 'addr': 'Sat 10/24 · Sun 10/25 · $899,000',
        # sentence breaks at 5.5, 9.5, 11.6, 14.9, 19.1 s
        'scenes': [
            (PAYS, 3.5, 5.55, 'Open house this weekend', '1057 Bond St, Elizabeth, New Jersey'),
            ('WALK', 79.0, 4.35, 'Price reduced $100,000', 'Now $899,000'),
            ('WALK', 86.6, 2.55, 'Renovated legal two-family', 'New kitchen, central air'),
            (C3, 3.5, 3.55, 'About 33 min by train<br>to NY Penn Station', 'Elizabeth station is 0.6 mi away'),
            ('WALK', 98.6, 4.35, 'Sat, Oct 24 · 12 to 3 PM<br>Sun, Oct 25 · 1 to 3 PM', 'Come see both units'),
        ],
        'end_dur': 3.4,
        'end': {'k': 'Open house', 'price': '$899,000', 'lines': ['Sat, Oct 24 · 12 to 3 PM', 'Sun, Oct 25 · 1 to 3 PM', '1057 Bond St · Elizabeth, New Jersey'],
                'extra': 'Not ready to buy? Rent to own at $4,500 a month.'},
    },
}

FONT = "'Helvetica Neue',Helvetica,Arial,sans-serif"
CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;background:transparent;overflow:hidden;font-family:{FONT};-webkit-font-smoothing:antialiased}}
.pill{{position:absolute;left:{CARD_X}px;top:318px;display:flex;align-items:center;gap:18px}}
.pill b{{background:#C9A24E;color:#0F1512;font-weight:800;font-size:30px;letter-spacing:.07em;text-transform:uppercase;padding:11px 18px 9px;border-radius:10px}}
.pill span{{color:#fff;font-size:34px;font-weight:800;letter-spacing:-.01em}}
.addr{{position:absolute;left:{CARD_X}px;top:390px;color:#C8D2CC;font-size:32px;font-weight:600}}
.txt{{position:absolute;left:{CARD_X}px;right:{CARD_X}px;top:448px;height:212px;display:flex;flex-direction:column;justify-content:center}}
.h{{color:#fff;font-size:66px;font-weight:800;line-height:1.04;letter-spacing:-.035em;text-wrap:balance}}
.s{{margin-top:14px;color:#C8D2CC;font-size:34px;font-weight:500;line-height:1.25;letter-spacing:-.01em;text-wrap:balance}}
.broker{{position:absolute;left:{CARD_X}px;right:{CARD_X}px;top:{CARD_Y + CARD_H + 26}px;display:flex;align-items:center;gap:16px;color:#C8D2CC}}
.broker p{{font-size:25px;font-weight:600;line-height:1.3}}
.broker b{{color:#fff}}
"""
EHO = """<svg viewBox="0 0 64 64" width="78" height="78"><path d="M4 30 32 10l28 20" fill="none" stroke="currentColor" stroke-width="4"/>
<path d="M11 30v22h42V30" fill="none" stroke="currentColor" stroke-width="4"/><rect x="22" y="33" width="20" height="5" fill="currentColor"/>
<rect x="22" y="43" width="20" height="5" fill="currentColor"/></svg>"""
TAP = """<svg viewBox="0 0 24 24" width="54" height="54" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7 7 7-7"/></svg>"""


def chrome_html(v):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
.frame{{position:absolute;left:{CARD_X}px;top:{CARD_Y}px;width:{CARD_W}px;height:{CARD_H}px;border-radius:30px;
  box-shadow:0 0 0 2000px #0F1512, inset 0 0 0 2px rgba(255,255,255,.16)}}</style></head><body>
<div class="frame"></div>
<div class="pill"><b>{v['pill']}</b><span>{v['pill_side']}</span></div>
<div class="addr">{html.escape(v['addr'])}</div>
<div class="broker">{EHO.replace('width="78" height="78"', 'width="44" height="44"')}<p><b>{BROKER}</b><br>{PERSON}</p></div>
</body></html>"""


def text_html(head, sub):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="txt"><p class="h">{head}</p><p class="s">{html.escape(sub)}</p></div></body></html>"""


def end_html(e):
    lines = ''.join(f'<p class="l">{html.escape(x)}</p>' for x in e['lines'])
    extra = f'<p class="rto">{html.escape(e["extra"])}</p>' if e['extra'] else ''
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{background:rgba(15,21,18,.9)}}
.wrap{{position:absolute;inset:0;padding:330px 72px 300px;display:flex;flex-direction:column;color:#fff}}
.k{{align-self:flex-start;background:#C9A24E;color:#0F1512;font-weight:800;font-size:36px;letter-spacing:.06em;text-transform:uppercase;padding:14px 24px 12px;border-radius:10px}}
.price{{margin-top:36px;font-size:156px;font-weight:800;letter-spacing:-.045em;line-height:.95}}
.ls{{margin-top:30px;display:grid;gap:10px}}
.l{{font-size:46px;font-weight:700;letter-spacing:-.02em;color:#E8ECE8}}
.cta{{margin-top:44px;align-self:stretch;background:#fff;color:#0F1512;border-radius:999px;height:136px;display:flex;align-items:center;justify-content:center;gap:20px;font-size:52px;font-weight:800;letter-spacing:-.02em}}
.rto{{margin-top:26px;font-size:36px;font-weight:600;color:#fff;text-align:center}}
.legal{{margin-top:auto;display:flex;gap:28px;align-items:center;color:#C8D2CC}}
.legal p{{font-size:28px;line-height:1.4;font-weight:500}}
.legal b{{color:#fff;font-size:32px;font-weight:800;display:block;margin-bottom:4px}}
.eho{{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none}}
.eho i{{font-style:normal;font-size:17px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-align:center;line-height:1.15}}
</style></head><body><div class="wrap">
<div class="k">{e['k']}</div>
<p class="price">{e['price']}</p>
<div class="ls">{lines}</div>
<div class="cta">{TAP}Tap Call on this page</div>
{extra}
<div class="legal"><span class="eho">{EHO}<i>Equal Housing<br>Opportunity</i></span><p><b>{BROKER}</b>{PERSON}</p></div>
</div></body></html>"""


def run(cmd):
    subprocess.run(cmd, check=True)


def render(page, markup, path):
    page.set_viewport_size({'width': W, 'height': H})
    page.set_content(markup, wait_until='load')
    page.screenshot(path=str(path), omit_background=True)


def guard(v):
    texts = [v['pill'], v['pill_side'], v['addr'], v['end']['k'], v['end']['price'], v['end']['extra'], *v['end']['lines']]
    texts += [s[3] + s[4] for s in v['scenes']]
    for t in texts:
        if any(c in t for c in ('—', '–', '--')):
            sys.exit(f'dash in copy: {t}')
        if '551' in t or '324-1057' in t or '743-9333' in t or '999' in t:
            sys.exit(f'number or old price in copy: {t}')


def build(name):
    v = VIDEOS[name]
    guard(v)
    wd = WORK / name
    if wd.exists():
        shutil.rmtree(wd)
    wd.mkdir(parents=True)

    bg = wd / 'bg.jpg'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '6', '-i', str(ROOT / PAYS), '-frames:v', '1', '-q:v', '2', str(bg)])
    facade = wd / 'facade.jpg'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(bg), '-vf', f'crop=1080:820:0:0,scale=-2:{H},crop={W}:{H}', '-q:v', '2', str(facade)])

    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(device_scale_factor=1)
        render(page, chrome_html(v), wd / 'chrome.png')
        for i, s in enumerate(v['scenes']):
            render(page, text_html(s[3], s[4]), wd / f'text{i}.png')
        render(page, end_html(v['end']), wd / 'end.png')
        b.close()

    parts = []
    for i, (src, start, dur, _, _) in enumerate(v['scenes']):
        out = wd / f's{i}.mp4'
        path = WALK if src == 'WALK' else ROOT / src
        if src == 'WALK':
            fit = (f'[0:v]crop=iw:iw*{CARD_H}/{CARD_W}:0:(ih-iw*{CARD_H}/{CARD_W})/2,'
                   f'scale={CARD_W}:{CARD_H}:flags=lanczos,unsharp=5:5:0.6,fps=30,setsar=1[v];')
        else:
            fit = (f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},'
                   f'crop={W}:{SRC_BOT - SRC_TOP}:0:{SRC_TOP},scale={CARD_W}:{CARD_H},fps=30,setsar=1[v];')
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(start), '-t', str(dur), '-i', str(path),
             '-loop', '1', '-t', str(dur), '-i', str(wd / 'chrome.png'),
             '-loop', '1', '-t', str(dur), '-i', str(wd / f'text{i}.png'),
             '-filter_complex', fit +
             f'color=c=0x0F1512:s={W}x{H}:r=30:d={dur}[bg];[bg][v]overlay={CARD_X}:{CARD_Y}[bv];'
             f'[2:v]format=rgba,fade=t=in:st=0.15:d=0.35:alpha=1[t];'
             f'[bv][1:v]overlay=0:0[c];[c][t]overlay=0:0,format=yuv420p[o]',
             '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(out)])
        parts.append((out, dur))

    end, ed = wd / 'end.mp4', v['end_dur']
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(facade), '-loop', '1', '-t', str(ed), '-i', str(wd / 'end.png'),
         '-filter_complex',
         f"[0:v]scale={int(W*1.25)}:{int(H*1.25)},zoompan=z='min(zoom+0.0005,1.06)':d={int(ed*30)}:s={W}x{H}:fps=30,"
         f"gblur=sigma=6,setsar=1,trim=duration={ed}[bgz];"
         f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1[e];[bgz][e]overlay=0:0:shortest=1,format=yuv420p[o]",
         '-map', '[o]', '-an', '-t', str(ed), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(end)])
    parts.append((end, ed))

    inputs, fc, prev = [], [], '0:v'
    for path, _ in parts:
        inputs += ['-i', str(path)]
    acc = parts[0][1]
    for k in range(1, len(parts)):
        off = acc - XF
        fc.append(f'[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{k}]')
        prev, acc = f'x{k}', off + parts[k][1]
    vid = wd / 'video.mp4'
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', f'[{prev}]',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', str(vid)])

    # voice: cut the trailing silence, -16 LUFS, pad to the picture, short fade out
    v['out'].parent.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(vid), '-i', str(v['voice']), '-filter_complex',
         f"[1:a]areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad,atrim=0:{acc:.3f},afade=t=out:st={acc-0.4:.3f}:d=0.4[a]",
         '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(v['out'])])
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(v['poster_t']), '-i', str(v['out']), '-frames:v', '1', '-vf', 'scale=720:-2', '-q:v', '3', str(v['poster'])])
    print(v['out'], f'{acc:.1f}s')


if __name__ == '__main__':
    for n in (sys.argv[1:] or list(VIDEOS)):
        build(n)
