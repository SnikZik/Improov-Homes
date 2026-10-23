"""Lead videos for the landing pages (9:16, with Gia's voiceover, NO phone number anywhere).

  sale       -> videos/web/lead-899.mp4  (+ lead-899-poster.jpg)       main page and /ny/
  openhouse  -> open-house/media/lead.mp4 (+ open-house/img/lead-poster.jpg)

Same card layout as the ad reels (ads/oh-src, ads/rto-src). The pages hide the campaign number
until the visitor has answered the call questions, so these videos never show or say it.

Voice (23 Oct 2026, Gia, says "eight hundred ninety-nine thousand", checked word by word with Whisper):
  ads/vo-899k/vo-sale-page-gia.wav / ads/vo-899k/vo-openhouse-page-gia.wav
Scene cuts sit in the middle of the pauses between sentences. words.json (Whisper) gives the order
of the words; the exact pause positions come from ffmpeg silencedetect (-40 dB, 80 ms) on the same takes,
because Whisper's word times run 0.1 to 0.7 s early on these files.

Price rule (client, 23 Oct): the old price only ever appears crossed out, written <s>$999,000</s>.
Work list in the client's words: New roof. New central air. New kitchens in both units.
Updated baths. Refinished wood floors.

The exterior clips (pays-for-itself, C3) carry burned-in text at the top ("FOR SALE · $999,000" ends at
y=156) and Imbar's face bubble from y=870 down, so they are cut to the clean band y 175..865.

Usage: python3 ads/lead-src/build_lead_videos.py [sale|openhouse ...]
       (each build also writes a frame every 1.5 s + a contact sheet to WORK/<name>/check/)
"""
import subprocess, sys, pathlib, html, shutil, json, re
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
VO = ROOT / 'ads/vo-899k'
WORK = pathlib.Path('/private/tmp/claude-501/-Users-s/5f9fd08e-11bf-4ca5-9104-a5feeb1b005b/scratchpad/lead/work')
WALK = pathlib.Path('/Users/s/Downloads/WhatsApp Video 2026-10-21 at 16.22.19.mp4')
SRC = {'PAYS': ROOT / 'videos/pays-for-itself.mp4', 'C3': ROOT / 'ads/C3_separate-everything.mp4', 'WALK': WALK}
FACADE_STILL = ROOT / 'open-house/img/facade.jpg'   # clean 1080x690 still of the upper facade and roof line

W, H = 1080, 1920
CARD_W, CARD_X, CARD_Y = 740, 170, 676
SRC_TOP, SRC_BOT = 160, 1300
CARD_H = round((SRC_BOT - SRC_TOP) * CARD_W / 1080)
# clean band of the 1080x1920 exterior clips: below the burned-in top label, above Imbar's face bubble
EXT_Y0, EXT_Y1 = 175, 865
EXT_H = EXT_Y1 - EXT_Y0
EXT_W = round(EXT_H * CARD_W / CARD_H)
EXT_X = 313                                          # keeps the bay windows and the arched window in frame
XF = 0.35
TAIL = 1.2                                           # picture runs this long after the last word
BROKER = 'Improov Homes, Licensed Real Estate Broker'
PERSON = 'Imbar Meidani, Principal Broker'           # legal line, stays exactly as is
WAS = '<s>$999,000</s>'                              # the only allowed form of the old price
NOW = '$899,000'

VIDEOS = {
    'sale': {
        'voice': VO / 'vo-sale-page-gia.wav',
        'out': ROOT / 'videos/web/lead-899.mp4',
        'poster': ROOT / 'videos/web/lead-899-poster.jpg', 'poster_t': 7.0,
        'pill': 'Price reduced', 'pill_side': 'Elizabeth, New Jersey', 'addr': f'1057 Bond St · {WAS} {NOW}',
        # "This two-family in Elizabeth, New Jersey just dropped one hundred thousand dollars." |5.07-5.57|
        # "Now eight hundred ninety-nine thousand." |7.65-8.25| "New roof, new central air," |10.21-10.60|
        # "and new kitchens in both units." |12.31-12.52| "Live in one unit and rent out the other." |14.45-14.90|
        # "About thirty-three minutes by train to Penn Station." |17.50-18.31| "Tap call below to set up a visit." ends 20.03
        'cuts': [5.32, 7.95, 10.40, 12.41, 14.68, 17.90],
        'scenes': [
            ('PAYS', 3.4, 'Price reduced $100,000', 'Two-family in Elizabeth, New Jersey'),
            ('WALK', 78.3, f'<span class="was">{WAS}</span>Now {NOW}', 'Refinished wood floors', 0.9),
            ('STILL', 0, 'New roof<br>New central air', 'Legal two-family'),
            ('WALK', 87.4, 'New kitchens in both units', 'Renovated in 2026'),
            ('WALK', 40.3, 'Live in one unit,<br>rent out the other', 'Updated baths'),
            ('C3', 4.4, 'About 33 min by train<br>to NY Penn Station', 'Elizabeth station is 0.6 mi away'),
        ],
        'end': {'k': 'Price reduced $100,000', 'was': WAS, 'price': NOW,
                'lines': ['New roof · new central air', 'New kitchens in both units', 'Updated baths · refinished wood floors',
                          '1057 Bond St · Elizabeth, New Jersey'], 'extra': ''},
    },
    'openhouse': {
        'voice': VO / 'vo-openhouse-page-gia.wav',
        'out': ROOT / 'open-house/media/lead.mp4',
        'poster': ROOT / 'open-house/img/lead-poster.jpg', 'poster_t': 9.8,
        'pill': 'Open house', 'pill_side': 'Elizabeth, New Jersey', 'addr': f'Sat 10/24 · Sun 10/25 · {WAS} {NOW}',
        # "Open house this weekend at 1057 Bond Street in Elizabeth, New Jersey." |5.51-6.15|
        # "Price cut one hundred thousand," |7.86-8.11| "now eight hundred ninety-nine thousand." |10.40-11.41|
        # "New roof, new central air," |13.21-13.40| "and new kitchens in both units." |15.31-16.08|
        # "About thirty-three minutes by train to Penn Station." |18.58-19.24| "Saturday twelve to three,
        # Sunday one to three." |22.34-22.87| "Tap call below to plan your visit." ends 25.17
        'cuts': [5.83, 7.98, 10.90, 13.30, 15.70, 18.90, 22.60],
        'scenes': [
            ('C3', 3.5, 'Open house this weekend', '1057 Bond St, Elizabeth, New Jersey'),
            ('WALK', 40.35, 'Price reduced $100,000', 'Updated baths'),
            ('WALK', 78.2, f'<span class="was">{WAS}</span>Now {NOW}', 'Refinished wood floors', 0.85),
            ('STILL', 0, 'New roof<br>New central air', 'Legal two-family'),
            ('WALK', 87.4, 'New kitchens in both units', 'Renovated in 2026'),
            ('PAYS', 4.6, 'About 33 min by train<br>to NY Penn Station', 'Elizabeth station is 0.6 mi away'),
            ('WALK', 100.1, 'Sat, Oct 24 · 12 to 3 PM<br>Sun, Oct 25 · 1 to 3 PM', 'Come see both units', 0.87),
        ],
        'end': {'k': 'Open house', 'was': WAS, 'price': NOW,
                'lines': ['Sat, Oct 24 · 12 to 3 PM', 'Sun, Oct 25 · 1 to 3 PM', '1057 Bond St · Elizabeth, New Jersey'],
                'extra': 'Not ready to buy? Rent to own at $4,500 a month.'},
    },
}

FONT = "'Helvetica Neue',Helvetica,Arial,sans-serif"
STRIKE = '#E0533D'
CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;background:transparent;overflow:hidden;font-family:{FONT};-webkit-font-smoothing:antialiased}}
s{{text-decoration:line-through;text-decoration-color:{STRIKE};text-decoration-thickness:.12em;text-decoration-skip-ink:none;color:#A7B1AB}}
.pill{{position:absolute;left:{CARD_X}px;top:318px;display:flex;align-items:center;gap:18px}}
.pill b{{background:#C9A24E;color:#0F1512;font-weight:800;font-size:30px;letter-spacing:.07em;text-transform:uppercase;padding:11px 18px 9px;border-radius:10px}}
.pill span{{color:#fff;font-size:34px;font-weight:800;letter-spacing:-.01em}}
.addr{{position:absolute;left:{CARD_X}px;top:390px;color:#C8D2CC;font-size:32px;font-weight:600;white-space:nowrap}}
.addr s{{font-weight:600}}
.txt{{position:absolute;left:{CARD_X}px;right:{CARD_X}px;top:448px;height:212px;display:flex;flex-direction:column;justify-content:center}}
.h{{color:#fff;font-size:66px;font-weight:800;line-height:1.04;letter-spacing:-.035em;text-wrap:balance}}
.h .was{{display:block;font-size:48px;letter-spacing:-.02em;margin-bottom:8px}}
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
<div class="addr">{v['addr']}</div>
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
.wrap{{position:absolute;inset:0;padding:300px 72px 290px;display:flex;flex-direction:column;color:#fff}}
.k{{align-self:flex-start;background:#C9A24E;color:#0F1512;font-weight:800;font-size:36px;letter-spacing:.06em;text-transform:uppercase;padding:14px 24px 12px;border-radius:10px}}
.was{{margin-top:34px;font-size:76px;font-weight:800;letter-spacing:-.035em;line-height:1}}
.price{{margin-top:6px;font-size:156px;font-weight:800;letter-spacing:-.045em;line-height:.95}}
.ls{{margin-top:30px;display:grid;gap:10px}}
.l{{font-size:44px;font-weight:700;letter-spacing:-.02em;color:#E8ECE8}}
.cta{{margin-top:40px;align-self:stretch;background:#fff;color:#0F1512;border-radius:999px;height:136px;display:flex;align-items:center;justify-content:center;gap:20px;font-size:52px;font-weight:800;letter-spacing:-.02em}}
.rto{{margin-top:26px;font-size:36px;font-weight:600;color:#fff;text-align:center}}
.legal{{margin-top:auto;display:flex;gap:28px;align-items:center;color:#C8D2CC}}
.legal p{{font-size:28px;line-height:1.4;font-weight:500}}
.legal b{{color:#fff;font-size:32px;font-weight:800;display:block;margin-bottom:4px}}
.eho{{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none}}
.eho i{{font-style:normal;font-size:17px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-align:center;line-height:1.15}}
</style></head><body><div class="wrap">
<div class="k">{e['k']}</div>
<p class="was">{e['was']}</p>
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


PHONE = re.compile(r'551|324[\s.\-]?1057|743[\s.\-]?9333|\(973\)|\d{3}[\s.\-]\d{3}[\s.\-]\d{4}')


def guard(v):
    """Stops the build on: a phone number, the old price without its strikethrough, a dash,
    Imbar outside the legal broker line, or a financing term (Reg Z)."""
    texts = [v['pill'], v['pill_side'], v['addr'], v['end']['k'], v['end']['was'], v['end']['price'], v['end']['extra'],
             *v['end']['lines'], BROKER, *(s[2] + ' ' + s[3] for s in v['scenes'])]
    for t in texts:
        if any(c in t for c in ('—', '–', '--')):
            sys.exit(f'dash in copy: {t}')
        if PHONE.search(t):
            sys.exit(f'phone number in copy: {t}')
        if '999' in t.replace(WAS, ''):
            sys.exit(f'old price without strikethrough: {t}')
        if 'imbar' in t.lower():
            sys.exit(f'Imbar outside the broker line: {t}')
        if re.search(r'down\b|%|\bAPR\b|interest|mortgage|loan|financ|/mo\b', t, re.I):
            sys.exit(f'financing term in copy: {t}')
    if WAS not in v['addr'] or v['end']['was'] != WAS:
        sys.exit('crossed-out old price missing from the header or the end card')
    if len(v['cuts']) != len(v['scenes']):
        sys.exit('need one cut per scene (the last cut starts the end card)')


def voice_end(path):
    """Time of the last word: start of the trailing silence (-45 dB)."""
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                               capture_output=True, text=True).stdout)
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-af', 'silencedetect=noise=-45dB:d=0.05', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    if starts and (len(ends) < len(starts) or ends[-1] >= dur - 0.02):
        return starts[-1]
    return dur


def scene_clip(src, start, dur, wd, i, speed=1.0):
    """speed < 1 plays the source slower: dur*speed seconds of it fill the scene."""
    out = wd / f's{i}.mp4'
    slow = f'setpts=PTS/{speed},' if speed != 1 else ''
    need = round(dur * speed + 0.05, 3)
    if src == 'STILL':
        # slow push-in on the clean facade still (roof line, arched window, bay)
        n = int(round(dur * 30)) + 2
        cw = round(690 * CARD_W / CARD_H)
        inputs = ['-i', str(FACADE_STILL)]
        fit = (f'[0:v]crop={cw}:690:300:0,scale={CARD_W*2}:{CARD_H*2}:flags=lanczos,'
               f"zoompan=z='1+0.0008*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={CARD_W}x{CARD_H}:fps=30,"
               f'trim=duration={dur},setsar=1[v];')
    elif src == 'WALK':
        inputs = ['-ss', str(start), '-t', str(need), '-i', str(WALK)]
        fit = (f'[0:v]{slow}crop=iw:iw*{CARD_H}/{CARD_W}:0:(ih-iw*{CARD_H}/{CARD_W})/2,'
               f'scale={CARD_W}:{CARD_H}:flags=lanczos,unsharp=5:5:0.6,fps=30,setsar=1[v];')
    else:
        inputs = ['-ss', str(start), '-t', str(need), '-i', str(SRC[src])]
        fit = (f'[0:v]{slow}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},'
               f'crop={EXT_W}:{EXT_H}:{EXT_X}:{EXT_Y0},scale={CARD_W}:{CARD_H}:flags=lanczos,fps=30,setsar=1[v];')
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs,
         '-loop', '1', '-t', str(dur), '-i', str(wd / 'chrome.png'),
         '-loop', '1', '-t', str(dur), '-i', str(wd / f'text{i}.png'),
         '-filter_complex', fit +
         f'color=c=0x0F1512:s={W}x{H}:r=30:d={dur}[bg];[bg][v]overlay={CARD_X}:{CARD_Y}:eof_action=repeat[bv];'
         f'[2:v]format=rgba,fade=t=in:st=0.15:d=0.35:alpha=1[t];'
         f'[bv][1:v]overlay=0:0[c];[c][t]overlay=0:0,format=yuv420p[o]',
         '-map', '[o]', '-an', '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(out)])
    return out


def build(name):
    v = VIDEOS[name]
    guard(v)
    wd = WORK / name
    if wd.exists():
        shutil.rmtree(wd)
    wd.mkdir(parents=True)

    vend = voice_end(v['voice'])
    total = round(vend + TAIL, 2)
    cuts = v['cuts']
    if not all(0 < a < b for a, b in zip(cuts, cuts[1:])) or cuts[-1] > vend:
        sys.exit(f'bad cuts {cuts} for a voice that ends at {vend:.2f}')
    # each crossfade is centred on its cut
    edges = [0, *cuts, total]
    durs = []
    for k in range(len(edges) - 1):
        d = edges[k + 1] - edges[k]
        d += (XF / 2 if k > 0 else 0) + (XF / 2 if k < len(edges) - 2 else 0)
        durs.append(round(d, 3))

    bg = wd / 'bg.jpg'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '6', '-i', str(SRC['PAYS']), '-frames:v', '1', '-q:v', '2', str(bg)])
    facade = wd / 'facade.jpg'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(bg), '-vf', f'crop=1080:820:0:0,scale=-2:{H},crop={W}:{H}', '-q:v', '2', str(facade)])

    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(device_scale_factor=1)
        render(page, chrome_html(v), wd / 'chrome.png')
        for i, s in enumerate(v['scenes']):
            render(page, text_html(s[2], s[3]), wd / f'text{i}.png')
        render(page, end_html(v['end']), wd / 'end.png')
        b.close()

    parts = []
    for i, (src, start, *_rest) in enumerate(v['scenes']):
        speed = _rest[2] if len(_rest) > 2 else 1.0
        parts.append((scene_clip(src, start, durs[i], wd, i, speed), durs[i]))

    end, ed = wd / 'end.mp4', durs[-1]
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(facade), '-loop', '1', '-t', str(ed), '-i', str(wd / 'end.png'),
         '-filter_complex',
         f"[0:v]scale={int(W*1.25)}:{int(H*1.25)},zoompan=z='min(zoom+0.0005,1.06)':d={int(ed*30)+2}:s={W}x{H}:fps=30,"
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

    # voice: cut the trailing silence, two-pass loudnorm to -16 LUFS, pad to the picture, short fade out
    pre = "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(v['voice']), '-af',
                          f'{pre},loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    m = json.loads(err[err.rindex('{'):err.rindex('}') + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    v['out'].parent.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(vid), '-i', str(v['voice']), '-filter_complex',
         f"[1:a]{pre},aresample=48000,{ln},aresample=48000,apad,atrim=0:{acc:.3f},afade=t=out:st={acc-0.4:.3f}:d=0.4[a]",
         '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
         '-movflags', '+faststart', str(v['out'])])
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(v['poster_t']), '-i', str(v['out']), '-frames:v', '1', '-vf', 'scale=720:-2', '-q:v', '3', str(v['poster'])])

    # frames for the eye check: one every 1.5 s, plus a contact sheet
    ck = wd / 'check'
    ck.mkdir()
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(v['out']), '-vf', 'fps=2/3,scale=540:-2', '-q:v', '3', str(ck / 'f%02d.jpg')])
    n = len(list(ck.glob('f*.jpg')))
    cols = 6
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(ck / 'f%02d.jpg'), '-vf',
         f'scale=270:-2,tile={cols}x{(n + cols - 1) // cols}', '-frames:v', '1', str(ck / 'sheet.jpg')])
    print(v['out'], f'{acc:.2f}s', 'voice ends', f'{vend:.2f}s', 'scene durations', durs)


if __name__ == '__main__':
    for n in (sys.argv[1:] or list(VIDEOS)):
        build(n)
