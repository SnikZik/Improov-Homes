"""Voiceover version of the 1057 Bond open house reel (9:16, about 29 s).

Reuses the layout of ads/oh-src/build_open_house.py (card in Meta's safe zones, offer on
top, broker line below, end card). Scene cuts follow the sentence pauses of the voiceover.

Footage: only the 21 Oct WhatsApp walkthrough (no picture-in-picture, no burned-in text).

Usage: python3 ads/open-house-vo/build_open_house_vo.py [voiceover.mp3]
Swap in any voiceover (Imbar reading the same script on her phone works best); the cuts
follow its pauses automatically.
"""
import subprocess, sys, pathlib, shutil, re, importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
VO = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'vo-amanda.mp3'
WALK = pathlib.Path('/Users/s/Downloads/WhatsApp Video 2026-10-21 at 16.22.19.mp4')
WORK = pathlib.Path('/private/tmp/claude-501/-Users-s/380d5559-9905-4a9f-8ab1-c17ecde0c63a/scratchpad/ohvo/work')
OUT = HERE

# shared layout from the silent reel
spec = importlib.util.spec_from_file_location('oh', ROOT / 'ads/oh-src/build_open_house.py')
oh = importlib.util.module_from_spec(spec)
_argv = sys.argv; sys.argv = [sys.argv[0], str(WALK)]
spec.loader.exec_module(oh)
sys.argv = _argv
W, H, CARD_W, CARD_H, CARD_X, CARD_Y, XF = oh.W, oh.H, oh.CARD_W, oh.CARD_H, oh.CARD_X, oh.CARD_Y, oh.XF

TEMPO = 1.06          # voiceover a touch quicker than the raw take
LEAD = 0.3            # silence before the first word
TAIL = 0.7            # hold after the last word

SMALL = '<span style="font-size:60px">{}</span>'
# Only the new WhatsApp walkthrough (Imbar asked for this video). One scene per sentence.
#  (second in the walkthrough, vertical anchor of the card crop 0 = top 1 = bottom, headline, sub)
SCENES = [
    (0.0, 0.25, 'Open house in<br>Elizabeth, New Jersey', 'Sat, Oct 24 and Sun, Oct 25'),
    (3.0, 0.30, 'Price reduced $100,000', 'Now $899,000'),
    (88.0, 0.50, 'Renovated legal two-family', 'New kitchen, central air, refinished wood floors'),
    (79.5, 0.50, 'About 33 min by train<br>to NY Penn Station', 'Elizabeth, NJ station is 0.6 mi away'),
    (6.5, 0.40, SMALL.format('Saturday 12 to 3 PM<br>Sunday 1 to 3 PM'), 'Oct 24 and Oct 25 · 1057 Bond St, Elizabeth, NJ'),
]
END_BG = 1.0          # walkthrough second used, blurred, behind the end card
BAD = re.compile(r'[—–]|--')


def run(cmd, capture=False):
    return subprocess.run(cmd, check=True, capture_output=capture, text=True)


ANCHORS = ['price', 'renovated', 'about', 'saturday', 'call']   # first word of scenes 2 to 5 and the end card


def word_cuts(path):
    """Cut points from word timings: just before each anchor word (or the article before it)."""
    import mlx_whisper
    r = mlx_whisper.transcribe(str(path), path_or_hf_repo='mlx-community/whisper-large-v3-turbo', word_timestamps=True)
    words = [(w['word'].strip().strip('.,').lower(), w['start']) for seg in r['segments'] for w in seg['words']]
    print('heard:', ' '.join(w for w, _ in words))
    cuts, i = [], 0
    for a in ANCHORS:
        while i < len(words) and words[i][0] != a:
            i += 1
        if i == len(words):
            print(f'anchor {a!r} not heard, spacing the rest evenly')
            last = cuts[-1] if cuts else 0.0
            end = words[-1][1]
            left = len(ANCHORS) - len(cuts)
            cuts += [last + (end - last) * (k + 1) / (left + 1) for k in range(left)]
            return cuts
        t = words[i - 1][1] if i and words[i - 1][0] in ('a', 'the') else words[i][1]
        cuts.append(max(0.0, t - 0.22))
        i += 1
    return cuts


def duration(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)], capture=True)
    return float(r.stdout.strip())


def build():
    for s in SCENES:
        for t in s[2:]:
            if BAD.search(re.sub(r'<[^>]+>', '', t)):
                sys.exit(f'dash in copy: {t!r}')
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    # 1. voiceover: tempo, loudness for social, lead-in
    vo = WORK / 'vo.wav'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(VO), '-af',
         f'atempo={TEMPO},loudnorm=I=-14:TP=-1.5:LRA=9,adelay={int(LEAD*1000)}|{int(LEAD*1000)}',
         '-ar', '48000', '-ac', '2', str(vo)])
    vo_len = duration(vo)
    total = vo_len + TAIL
    c = word_cuts(vo)
    starts = [0.0] + c[:4]
    end_start = c[4]
    print('cuts at', [round(x, 2) for x in starts + [end_start]], 'total', round(total, 2))

    # 2. overlays
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page(device_scale_factor=1)
        oh.render(page, oh.chrome_html(), WORK / 'chrome.png')
        for i, s in enumerate(SCENES):
            oh.render(page, oh.text_html(s[2], s[3]), WORK / f'text{i}.png')
        oh.render(page, oh.end_html(), WORK / 'end.png')
        br.close()

    # 3. scenes, each long enough to cover its crossfade
    bounds = starts + [end_start]
    parts = []
    for i, (sec, anchor, _, _) in enumerate(SCENES):
        dur = bounds[i + 1] - bounds[i] + XF
        out = WORK / f's{i}.mp4'
        inp = ['-ss', str(sec), '-t', str(dur), '-i', str(WALK)]
        fit = (f'[0:v]crop=iw:iw*{CARD_H}/{CARD_W}:0:(ih-iw*{CARD_H}/{CARD_W})*{anchor},'
               f'scale={CARD_W}:{CARD_H}:flags=lanczos,unsharp=5:5:0.6,fps=30,setsar=1[v];')
        run(['ffmpeg', '-y', '-loglevel', 'error', *inp,
             '-loop', '1', '-t', str(dur), '-i', str(WORK / 'chrome.png'),
             '-loop', '1', '-t', str(dur), '-i', str(WORK / f'text{i}.png'),
             '-filter_complex',
             fit + f'color=c=0x0F1512:s={W}x{H}:r=30:d={dur}[bg];[bg][v]overlay={CARD_X}:{CARD_Y}:shortest=1[bv];'
             f'[2:v]format=rgba,fade=t=in:st=0.12:d=0.3:alpha=1[t];[bv][1:v]overlay=0:0[c];[c][t]overlay=0:0,format=yuv420p[o]',
             '-map', '[o]', '-an', '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(out)])
        parts.append((out, dur))

    end_dur = total - end_start
    facade = WORK / 'facade.jpg'
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(END_BG), '-i', str(WALK), '-frames:v', '1',
         '-vf', f'scale=-2:{H}:flags=lanczos,crop={W}:{H}', '-q:v', '2', str(facade)])
    end = WORK / 'end.mp4'
    frames = int(end_dur * 30) + 2
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(facade),
         '-loop', '1', '-t', str(end_dur), '-i', str(WORK / 'end.png'),
         '-filter_complex',
         f"[0:v]scale={int(W*1.25)}:{int(H*1.25)},zoompan=z='min(zoom+0.0005,1.06)':d={frames}:s={W}x{H}:fps=30,"
         f"gblur=sigma=6,setsar=1,trim=duration={end_dur}[bgz];"
         f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1[e];[bgz][e]overlay=0:0:shortest=1,format=yuv420p[o]",
         '-map', '[o]', '-an', '-t', str(end_dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(end)])
    parts.append((end, end_dur))

    # 4. chain with crossfades so each cut lands on its pause, then lay the voice on
    inputs, fc, prev = [], [], '0:v'
    for path, _ in parts:
        inputs += ['-i', str(path)]
    acc = parts[0][1]
    for k in range(1, len(parts)):
        offset = acc - XF
        fc.append(f'[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[x{k}]')
        prev = f'x{k}'
        acc = offset + parts[k][1]
    final = OUT / 'open-house-vo_reel-9x16.mp4'
    n = len(parts)
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-i', str(vo), '-filter_complex',
         ';'.join(fc) + f';[{n}:a]apad[a]',
         '-map', f'[{prev}]', '-map', '[a]', '-t', f'{acc:.3f}',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-r', '30', str(final)])
    print(final, f'{acc:.2f}s')


if __name__ == '__main__':
    build()
