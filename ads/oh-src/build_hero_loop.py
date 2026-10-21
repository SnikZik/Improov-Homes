#!/usr/bin/env python3
"""Silent hero loop for the open house page: front of the house, then the living room bay
windows, the kitchen and a bedroom, cut from Imbar's 21 Oct WhatsApp walkthrough (464x624).

Usage: python3 ads/oh-src/build_hero_loop.py [path/to/walkthrough.mp4]
Writes open-house/media/hero.mp4 and open-house/img/hero-poster.jpg.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
WALK = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('/Users/s/Downloads/WhatsApp Video 2026-10-21 at 16.22.19.mp4')
OUT = ROOT / 'open-house/media/hero.mp4'
POSTER = ROOT / 'open-house/img/hero-poster.jpg'

# (start, end) in seconds of the walkthrough
CLIPS = [(0.0, 4.3), (79.6, 81.0), (87.6, 90.6), (100.2, 102.0)]
FADE = 0.35


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    inputs, chains = [], []
    for i, (a, b) in enumerate(CLIPS):
        inputs += ['-ss', str(a), '-t', str(b - a), '-i', str(WALK)]
        chains.append(f'[{i}:v]fps=30,scale=464:624:flags=lanczos,unsharp=5:5:0.6,setsar=1,format=yuv420p[c{i}]')
    # crossfade the clips in order
    last, offset = 'c0', CLIPS[0][1] - CLIPS[0][0]
    for i in range(1, len(CLIPS)):
        offset -= FADE
        out = f'x{i}'
        chains.append(f'[{last}][c{i}]xfade=transition=fade:duration={FADE}:offset={offset:.3f}[{out}]')
        last, offset = out, offset + (CLIPS[i][1] - CLIPS[i][0])
    run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(chains),
         '-map', f'[{last}]', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '24',
         '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(OUT)])
    # poster = the full front of the house, so the first paint already shows it
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '1.2', '-i', str(WALK), '-frames:v', '1',
         '-vf', 'scale=464:624:flags=lanczos,unsharp=5:5:0.6', '-q:v', '3', str(POSTER)])
    print(OUT, POSTER)


if __name__ == '__main__':
    main()
