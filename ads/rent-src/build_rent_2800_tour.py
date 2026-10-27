"""27 Oct 2026: a walkthrough reel of the second unit (2nd floor), 3 bed 2 bath, $2,800 a month.

Footage: Imbar's own tour of the second floor, shot 12 Aug 2026 (Downloads/אמבר), with her voice and the
round selfie bubble her recording app burns into every frame (kept, Snir approved on 27 Oct).
  - vid_20260812_143623_601.mp4  kitchen, hallway, laundry room, two bedrooms, bathroom
  - vid_20260812_143523_137.mp4  arriving on the 2nd floor, living and dining room with the bay windows
Cuts sit on pauses in her speech (ffmpeg silencedetect), so no sentence is cut in half:
  A  601   0.00 -  7.30  "Look at this stylish kitchen. It's beautiful. All brand new appliances."
  B  137  10.00 - 19.90  "Again, here's the living room area, extremely spacious. Look at this beautiful new
                          windows, this dining area."
  CD 601   7.45 - 28.55  "You move in and you don't have to lift a finger. Again, a laundry room. Exactly the
                          same layout as the first floor. Spacious bedrooms. Another bathroom. New vanities."
                          (stops before "And we also have important things to know about this house", which
                          turns into buyer talk)
On top: the offer bar ($2,800, 3 bed, 2 bath; the open house chip only in the dated cut), room labels timed
to what is on screen, and the 9:16 rental still as the end card (4 s).
Outputs in ads/rent-2800/: rent-2800-tour_reel-9x16.mp4 (with the open house), ..._nodates.mp4 (after
1 Nov), and a thumbnail of each.
Usage: TOUR_SRC=/path/to/אמבר python3 ads/rent-src/build_rent_2800_tour.py
"""
import os, subprocess, pathlib, html, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'ads' / 'rent-2800'
WORK = OUT / '_work_tour'
SRC = pathlib.Path(os.environ.get('TOUR_SRC', '/Users/s/Downloads/אמבר'))
KITCHEN = SRC / 'vid_20260812_143623_601.mp4'
LIVING = SRC / 'vid_20260812_143523_137.mp4'
FONT = "'Helvetica Neue',Helvetica,Arial,sans-serif"
W, H, FPS = 1080, 1920, 30
OH_LINE = 'Open house: Sat 10/31, 12 to 2 · Sun 11/1, 1 to 3'

# (source, start, end) in the order they play
SEGMENTS = [(KITCHEN, 0.00, 7.30), (LIVING, 10.00, 19.90), (KITCHEN, 7.45, 28.55)]
END_CARD_S, XFADE_S = 4.0, 0.35
# room labels: (text, segment index, start and end in that clip's own time)
LABELS = [('New kitchen · stainless appliances', 0, 0.40, 7.30),
          ('Living and dining room', 1, 13.20, 19.90),
          ('Laundry room', 2, 10.60, 13.00),
          ('3 bedrooms', 2, 14.60, 21.80),
          ('2 baths', 2, 22.80, 28.55)]

CSS = f"""*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:transparent;font-family:{FONT};-webkit-font-smoothing:antialiased}}"""

def bar_html(open_house):
    oh = f'<p class="oh">{html.escape(OH_LINE)}</p>' if open_house else ''
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
.shade{{position:absolute;left:0;top:0;width:{W}px;height:{790 if open_house else 700}px;
  background:linear-gradient(rgba(10,14,12,.78) 0%,rgba(10,14,12,.62) 55%,rgba(10,14,12,0) 100%)}}
.box{{position:absolute;left:56px;top:196px;color:#fff}}
.pill{{display:inline-block;background:#C9A24E;color:#0F1512;font-weight:800;font-size:30px;letter-spacing:.08em;
  text-transform:uppercase;padding:11px 18px 9px;border-radius:10px}}
.rent{{margin-top:18px;font-size:104px;font-weight:800;letter-spacing:-.045em;line-height:.95;text-shadow:0 2px 18px rgba(0,0,0,.35)}}
.rent small{{font-size:44px;font-weight:700;color:#E3E9E5;letter-spacing:-.02em}}
.what{{margin-top:14px;font-size:44px;font-weight:800;letter-spacing:-.02em;text-shadow:0 2px 14px rgba(0,0,0,.4)}}
.oh{{margin-top:18px;display:inline-block;background:rgba(15,21,18,.72);border:2px solid #C9A24E;border-radius:12px;
  padding:10px 16px 9px;font-size:31px;font-weight:800;letter-spacing:-.01em}}
</style></head><body><div class="shade"></div><div class="box">
<p class="pill">For rent or rent to own</p>
<p class="rent">$2,800<small> a month</small></p>
<p class="what">Second unit · 3 bed · 2 bath</p>
{oh}</div></body></html>"""

def label_html(text):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
.lab{{position:absolute;left:56px;top:1318px;background:rgba(15,21,18,.80);border-left:8px solid #C9A24E;border-radius:12px;
  color:#fff;font-size:46px;font-weight:800;letter-spacing:-.015em;padding:14px 26px 13px 22px}}
</style></head><body><p class="lab">{html.escape(text)}</p></body></html>"""

def render_overlays():
    WORK.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
        jobs = [('bar_oh.png', bar_html(True)), ('bar_plain.png', bar_html(False))]
        jobs += [(f'label_{i}.png', label_html(t)) for i, (t, *_rest) in enumerate(LABELS)]
        for name, doc in jobs:
            pg.set_content(doc, wait_until='load')
            pg.screenshot(path=str(WORK / name), omit_background=True)
        b.close()

def build(open_house):
    starts, t = [], 0.0
    for (_, a, b) in SEGMENTS:
        starts.append(t); t += b - a
    foot = t
    total = foot + END_CARD_S - XFADE_S
    end_png = OUT / ('rent-2800_open-house_story-9x16.png' if open_house else 'rent-2800_story-9x16.png')
    srcs = [seg[0] for seg in SEGMENTS]          # one input per segment: an input stream can feed only one trim
    args = ['ffmpeg', '-y', '-loglevel', 'error']
    for s in srcs:
        args += ['-i', str(s)]
    args += ['-loop', '1', '-t', f'{END_CARD_S:.2f}', '-i', str(end_png)]                 # end card
    bar_idx = len(srcs) + 1
    args += ['-i', str(WORK / ('bar_oh.png' if open_house else 'bar_plain.png'))]
    lab0 = bar_idx + 1
    for i in range(len(LABELS)):
        args += ['-i', str(WORK / f'label_{i}.png')]
    f = []
    for k, (s, a, b) in enumerate(SEGMENTS):
        i = k
        f.append(f'[{i}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5,setsar=1,format=yuv420p[v{k}]')
        d = b - a
        f.append(f'[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=mono,'
                 f'afade=t=in:st=0:d=0.04,afade=t=out:st={d - 0.06:.3f}:d=0.06[a{k}]')
    n = len(SEGMENTS)
    f.append(''.join(f'[v{k}][a{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=1[vf][af]')
    cur = 'vf'
    f.append(f'[{cur}][{bar_idx}:v]overlay=0:0:format=auto[vb]'); cur = 'vb'
    for j, (_t, seg, a, b) in enumerate(LABELS):
        s0 = starts[seg] + (a - SEGMENTS[seg][1]); s1 = starts[seg] + (b - SEGMENTS[seg][1])
        f.append(f"[{cur}][{lab0 + j}:v]overlay=0:0:format=auto:enable='between(t,{s0:.2f},{s1:.2f})'[vl{j}]"); cur = f'vl{j}'
    f.append(f'[{len(srcs)}:v]fps={FPS},scale={W}:{H},setsar=1,format=yuv420p,settb=1/{FPS}[ve]')
    f.append(f'[{cur}]format=yuv420p,fps={FPS},settb=1/{FPS}[vm]')
    f.append(f'[vm][ve]xfade=transition=fade:duration={XFADE_S}:offset={foot - XFADE_S:.3f}[vout]')
    f.append(f'[af]highpass=f=90,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={foot - 0.15:.3f}:d=0.15,'
             f'apad,atrim=0:{total:.3f},aformat=channel_layouts=stereo[aout]')
    name = 'rent-2800-tour_reel-9x16' + ('' if open_house else '_nodates')
    out = OUT / f'{name}.mp4'
    args += ['-filter_complex', ';'.join(f), '-map', '[vout]', '-map', '[aout]', '-t', f'{total:.3f}',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '5000k', '-bufsize', '10000k', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
             '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', str(out)]
    subprocess.run(args, check=True)
    thumb = OUT / f'{name.replace("_reel", "_thumb")}.jpg'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '2.2', '-i', str(out), '-frames:v', '1', '-q:v', '2', str(thumb)], check=True)
    return out, total

def main():
    for t in [OH_LINE] + [l[0] for l in LABELS]:
        if any(c in t for c in ('—', '–', '--')):
            sys.exit('dash in copy')
    for s in (KITCHEN, LIVING):
        if not s.exists():
            sys.exit(f'missing footage: {s}')
    render_overlays()
    for oh in (True, False):
        out, total = build(oh)
        print(out.name, f'{total:.2f}s')

if __name__ == '__main__':
    main()
