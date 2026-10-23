# 1057 Bond, open house voiceover reels

Built by `build_open_house_vo.py`, in the same layout as the silent reel in `../open-house/`:

- `open-house-vo_reel-9x16.mp4`: 27.6 s, 9:16, walkthrough footage only (21 Oct WhatsApp video).
- `--reel-b` writes `../open-house/open-house_reel-9x16_gia.mp4`: the silent reel's footage,
  including the two exterior shots, cut to fit the same voice.

Voice (23 Oct): `../vo-899k/vo-openhouse-ad-gia.wav`, Gia, checked word by word with Whisper.
It ends with the phone number, so it is for ads only; the open house page uses its own take.
Its word timings are in `words-openhouse-ad-gia.json` (mlx_whisper large-v3-turbo).

One scene per sentence. In Reel B the intro is two shots under one headline (pays-for-itself
3.5 to 6.5 s, then C3 3.5 to 6.8 s) and the train scene uses C3 from 6.8 s: a longer run of
pays-for-itself would show its burned-in "10 MIN TO NEWARK AIRPORT" (from 9.2 s of the source).
Each cut sits in the pause before the words "price", "new" (roof), "about", "Saturday" and "call"; the end card holds until the voice ends, plus 1.2 s.
Loudness about -16 LUFS, AAC, H.264 1080x1920, faststart.

On screen: <s>$999,000</s> crossed out, then $899,000; the work list in the client's words
(New roof. New central air. New kitchens in both units. Updated baths. Refinished wood floors.);
end card "Call Roi at (551) 324-1057".

Script:

> Open house this weekend at 1057 Bond Street in Elizabeth, New Jersey. Price cut one hundred
> thousand, now eight hundred ninety-nine thousand. New roof, new central air, and new kitchens
> in both units. About thirty-three minutes by train to Penn Station. Saturday twelve to three,
> Sunday one to three. Call 551 324 1057.

To use another recording of the same script:

    python3 ads/open-house-vo/build_open_house_vo.py /path/to/voice.wav [--reel-b]

Older takes (`vo-gia.mp3`, `vo-amanda.mp3`) say "eight ninety-nine"; do not use them.

Landing page: https://snikzik.github.io/Improov-Homes/open-house/
