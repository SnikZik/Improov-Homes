"""Voiceover versions of the 1057 Bond open house reel (9:16).

Two variants, same voice, same cut points:
  vo  (default)  walkthrough footage only -> ads/open-house-vo/open-house-vo_reel-9x16.mp4
  b   (--reel-b) "Reel B": the silent reel's footage (the two exterior shots from Imbar's earlier
                 clips plus the walkthrough), cut to fit the voice -> ads/open-house/open-house_reel-9x16_gia.mp4
                 Its intro is two shots under one headline: those clips carry burned-in captions
                 ("10 MIN TO NEWARK AIRPORT" from 9.2 s of pays-for-itself), so every shot stays
                 inside ads/oh-src/build_open_house.py CLEAN and the build stops if one does not.

Reuses the layout of ads/oh-src/build_open_house.py (card in Meta's safe zones, offer on top,
broker line below, end card). One scene per sentence of the voice: the cuts sit in the pause
before the first word of each sentence (word timings from words.json, pause edges from
ffmpeg silencedetect). The end card holds until the voice ends, then about 1.2 s more.

Voice (23 Oct): ads/vo-899k/vo-openhouse-ad-gia.wav, Gia, checked word by word with Whisper:
  "Open house this weekend at 1057 Bond Street in Elizabeth, New Jersey. Price cut one hundred
   thousand, now eight hundred ninety-nine thousand. New roof, new central air, and new kitchens
   in both units. About thirty-three minutes by train to Penn Station. Saturday twelve to three,
   Sunday one to three. Call 551 324 1057."

Usage: python3 ads/open-house-vo/build_open_house_vo.py [voice.wav] [--reel-b]
Word timings are read from ads/vo-899k/words.json or ads/open-house-vo/words-*.json (key = the
voice path relative to the repo); for any other recording they come from mlx_whisper.
Scratch files go to $OH_WORK (default: the system temp folder).
"""
import subprocess, sys, pathlib, shutil, re, json, os, tempfile, importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
VARIANT = 'b' if '--reel-b' in sys.argv else 'vo'
VO = pathlib.Path(ARGS[0]).resolve() if ARGS else ROOT / 'ads/vo-899k/vo-openhouse-ad-gia.wav'
WALK = pathlib.Path('/Users/s/Downloads/WhatsApp Video 2026-10-21 at 16.22.19.mp4')
WORK = pathlib.Path(os.environ.get('OH_WORK', pathlib.Path(tempfile.gettempdir()) / 'bond-oh')) / f'ohvo-{VARIANT}'
FINAL = (ROOT / 'ads/open-house/open-house_reel-9x16_gia.mp4') if VARIANT == 'b' else HERE / 'open-house-vo_reel-9x16.mp4'
WORD_FILES = [ROOT / 'ads/vo-899k/words.json', *sorted(HERE.glob('words-*.json'))]

# shared layout from the silent reel
spec = importlib.util.spec_from_file_location('oh', ROOT / 'ads/oh-src/build_open_house.py')
oh = importlib.util.module_from_spec(spec)
_argv = sys.argv; sys.argv = [sys.argv[0], str(WALK)]
spec.loader.exec_module(oh)
sys.argv = _argv
W, H, CARD_W, CARD_H, CARD_X, CARD_Y, XF = oh.W, oh.H, oh.CARD_W, oh.CARD_H, oh.CARD_X, oh.CARD_Y, oh.XF
SRC_TOP, SRC_BOT = oh.SRC_TOP, oh.SRC_BOT

TEMPO = 1.0           # the 23 Oct takes are used as recorded (they were verified at this speed)
LEAD = 0.0            # the take already starts with half a second of room tone
TAIL = 1.2            # hold after the voice ends
LUFS = -16.0

SMALL = '<span style="font-size:60px">{}</span>'
T_INTRO = ('Open house in<br>Elizabeth, New Jersey', 'Sat, Oct 24 and Sun, Oct 25')
T_PRICE = (oh.WAS_NOW, oh.CFG['cut'])                       # <s>$999,000</s> $899,000
T_WORK = ('Renovated in 2026', oh.CFG['work'])              # the client's five items, in her words
T_TRAIN = ('About 33 min by train<br>to NY Penn Station', 'Elizabeth, NJ station is 0.6 mi away')
T_DAYS = (SMALL.format('Saturday 12 to 3 PM<br>Sunday 1 to 3 PM'), 'Oct 24 and Oct 25 · 1057 Bond St, Elizabeth, NJ')

# One scene per sentence: ([shots], (headline, sub)). A shot is (source, second in source, vertical
# anchor of the card crop for the walkthrough 0 = top 1 = bottom, seconds or None = the rest of the
# scene). 'WALK' = the 21 Oct WhatsApp walkthrough. The 1080x1920 clips carry burned-in captions:
# every shot must stay inside oh.CLEAN (the build stops otherwise).
SCENES = {
    'vo': [                                   # walkthrough only (Imbar asked for this video)
        ([('WALK', 0.0, 0.25, None)], T_INTRO),    # front of the house
        ([('WALK', 6.0, 0.40, None)], T_PRICE),    # porch and front door
        ([('WALK', 86.2, 0.50, None)], T_WORK),    # kitchen
        ([('WALK', 78.7, 0.50, None)], T_TRAIN),   # living room, wood floors
        ([('WALK', 98.6, 0.50, None)], T_DAYS),    # main level bedroom
    ],
    'b': [                                    # the silent reel's footage
        # intro (6.3 s) in two shots under one headline: pays-for-itself alone would run past 9.2 s
        # of its source into "10 MIN TO NEWARK AIRPORT"
        ([('videos/pays-for-itself.mp4', 3.5, None, 3.0),        # porch, then up to the facade
          ('ads/C3_separate-everything.mp4', 3.5, None, None)],  # the whole house from the street
         T_INTRO),
        ([('WALK', 0.0, 0.25, None)], T_PRICE),
        ([('WALK', 86.2, 0.50, None)], T_WORK),
        ([('ads/C3_separate-everything.mp4', 6.8, None, None)], T_TRAIN),   # porch to garage, after the intro's part of C3
        ([('WALK', 78.7, 0.50, None)], T_DAYS),
    ],
}[VARIANT]
ANCHORS = ['price', 'new', 'about', 'saturday', 'call']   # first word of sentences 2 to 5 and the end card
BAD = re.compile(r'[—–]|--')


def run(cmd, capture=False):
    return subprocess.run(cmd, check=True, capture_output=capture, text=True)


def duration(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)], capture=True)
    return float(r.stdout.strip())


def words_for(path):
    """[(word, start, end)] for the raw take: from a words file when we have it, else Whisper."""
    try:
        key = str(path.resolve().relative_to(ROOT))
    except ValueError:
        key = None
    for f in WORD_FILES:
        if key and f.exists():
            d = json.loads(f.read_text())
            if key in d:
                print('word timings from', f.relative_to(ROOT))
                return [(w['w'].strip().strip('.,').lower(), w['s'], w['e']) for w in d[key]]
    import mlx_whisper
    r = mlx_whisper.transcribe(str(path), path_or_hf_repo='mlx-community/whisper-large-v3-turbo', word_timestamps=True)
    return [(w['word'].strip().strip('.,').lower(), w['start'], w['end']) for seg in r['segments'] for w in seg['words']]


def silences(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-af', 'silencedetect=noise=-40dB:d=0.12',
                        '-f', 'null', '-'], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    return list(zip(st, en))


def sentence_cuts(words, gaps):
    """Cut 0.22 s before each anchor word starts, inside the pause that precedes it."""
    print('heard:', ' '.join(w for w, _, _ in words))
    cuts, i = [], 0
    for a in ANCHORS:
        while i < len(words) and words[i][0] != a:
            i += 1
        if i == len(words):
            sys.exit(f'anchor {a!r} not heard in the voice; check the script')
        prev_end = words[i - 1][2] / TEMPO + LEAD if i else 0.0
        start = words[i][1] / TEMPO + LEAD
        # Whisper puts a word's start at the end of the pause before it, often early: the real onset
        # is the end of the detected silence that overlaps [previous word end, this word start].
        gap = [g for g in gaps if g[0] <= start + 0.4 and g[1] >= prev_end - 0.1]
        lo, onset = max(gap, key=lambda g: g[1] - g[0]) if gap else (prev_end, start)
        cuts.append(max(lo + 0.05, onset - 0.22))
        i += 1
    return cuts


def prep_voice(out):
    """Tempo, lead-in and two-pass loudness normalisation to about -16 LUFS."""
    pre = f'atempo={TEMPO},' if TEMPO != 1.0 else ''
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(VO), '-af',
                        f'{pre}loudnorm=I={LUFS}:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    ln = (f"loudnorm=I={LUFS}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    delay = f',adelay={int(LEAD * 1000)}|{int(LEAD * 1000)}' if LEAD else ''
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(VO), '-af', f'{pre}{ln}{delay}',
         '-ar', '48000', '-ac', '2', str(out)])


def scene_fit(src, anchor, k, secs, label):
    """Input k fitted into the card, trimmed to secs, as [label]."""
    if src == 'WALK':      # 464x624 portrait: a card-shaped window, upscaled into the card
        fit = (f'crop=iw:iw*{CARD_H}/{CARD_W}:0:(ih-iw*{CARD_H}/{CARD_W})*{anchor},'
               f'scale={CARD_W}:{CARD_H}:flags=lanczos,unsharp=5:5:0.6')
    else:
        fit = (f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},'
               f'crop={W}:{SRC_BOT - SRC_TOP}:0:{SRC_TOP},scale={CARD_W}:{CARD_H}')
    return f'[{k}:v]{fit},fps=30,setsar=1,trim=duration={secs:.4f},setpts=PTS-STARTPTS[{label}];'


def shot_lengths(shots, dur):
    """Seconds of each shot: the fixed ones as given (whole frames), the last one takes the rest."""
    fixed = [round(s[3] * 30) / 30 for s in shots[:-1]]
    return fixed + [dur - sum(fixed)]


def build():
    for s in SCENES:
        for t in s[1]:
            plain = re.sub(r'<[^>]+>', '', t)
            if BAD.search(plain):
                sys.exit(f'dash in copy: {t!r}')
            if '999' in t.replace(oh.WAS_NOW, ''):
                sys.exit(f'old price without the strikethrough: {t!r}')
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    # 1. voice and cut points
    vo = WORK / 'vo.wav'
    prep_voice(vo)
    vo_len = duration(vo)
    total = vo_len + TAIL
    c = sentence_cuts(words_for(VO), silences(vo))
    starts = [0.0] + c[:4]
    end_start = c[4]
    print('cuts at', [round(x, 2) for x in starts + [end_start]], 'voice', round(vo_len, 2), 'total', round(total, 2))

    # 2. overlays
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page(device_scale_factor=1)
        oh.render(page, oh.chrome_html(), WORK / 'chrome.png')
        for i, s in enumerate(SCENES):
            oh.render(page, oh.text_html(*s[1]), WORK / f'text{i}.png')
        oh.render(page, oh.end_html(), WORK / 'end.png')
        br.close()

    # 3. scenes, each long enough to cover its crossfade
    bounds = starts + [end_start]
    parts = []
    for i, (shots, _) in enumerate(SCENES):
        dur = bounds[i + 1] - bounds[i] + XF
        out = WORK / f's{i}.mp4'
        lens = shot_lengths(shots, dur)
        inputs, fit = [], ''
        for k, ((src, sec, anchor, _), secs) in enumerate(zip(shots, lens)):
            oh.check_window(src, sec, secs)
            print(f'scene {i}: {src} {sec:.2f} to {sec + secs:.2f} s')
            path = WALK if src == 'WALK' else ROOT / src
            inputs += ['-ss', str(sec), '-t', f'{secs + 0.1:.3f}', '-i', str(path)]
            fit += scene_fit(src, anchor, k, secs, 'v' if len(shots) == 1 else f'v{k}')
        n = len(shots)
        if n > 1:                     # hard cut inside the card, the headline stays put
            fit += ''.join(f'[v{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0[v];'
        run(['ffmpeg', '-y', '-loglevel', 'error', *inputs,
             '-loop', '1', '-t', str(dur), '-i', str(WORK / 'chrome.png'),
             '-loop', '1', '-t', str(dur), '-i', str(WORK / f'text{i}.png'),
             '-filter_complex',
             fit + f'color=c=0x0F1512:s={W}x{H}:r=30:d={dur}[bg];[bg][v]overlay={CARD_X}:{CARD_Y}:shortest=1[bv];'
             f'[{n + 1}:v]format=rgba,fade=t=in:st=0.12:d=0.3:alpha=1[t];[bv][{n}:v]overlay=0:0[c];[c][t]overlay=0:0,format=yuv420p[o]',
             '-map', '[o]', '-an', '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30', str(out)])
        parts.append((out, dur))

    # end card: blurred front of the house behind it (walkthrough for vo, the silent reel's facade for b)
    end_dur = total - end_start
    facade = WORK / 'facade.jpg'
    if VARIANT == 'b':
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '6', '-i', str(ROOT / 'videos/pays-for-itself.mp4'), '-frames:v', '1',
             '-vf', f'crop=1080:820:0:0,scale=-2:{H},crop={W}:{H}', '-q:v', '2', str(facade)])
    else:
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '1.0', '-i', str(WALK), '-frames:v', '1',
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
    n = len(parts)
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-i', str(vo), '-filter_complex',
         ';'.join(fc) + f';[{n}:a]apad[a]',
         '-map', f'[{prev}]', '-map', '[a]', '-t', f'{acc:.3f}',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-r', '30', str(FINAL)])
    print(FINAL, f'{acc:.2f}s')


if __name__ == '__main__':
    build()
