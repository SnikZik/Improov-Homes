# 1057 Bond, open house voiceover reel

`open-house-vo_reel-9x16.mp4`: 29 s, 9:16, with a voiceover. Built by `build_open_house_vo.py`
from the 21 Oct WhatsApp walkthrough only, in the same layout as the silent reel in `../open-house/`.

Current voice: `vo-amanda.mp3` (ElevenLabs via Higgsfield, checked word by word with Whisper).
To use another recording, Imbar's or Snir's, put the file anywhere and run:

    python3 ads/open-house-vo/build_open_house_vo.py /path/to/voice.mp3

The cuts follow the words "price", "renovated", "about", "Saturday" and "call". If the recording
uses different words the remaining cuts are spaced evenly.

Script:

> Open house this weekend at 1057 Bond Street, Elizabeth, New Jersey. Price cut one hundred
> thousand, now eight ninety-nine. A renovated legal two-family, about thirty-three minutes by
> train to Penn Station. Saturday twelve to three, Sunday one to three. Call or text
> 551 324 1057.

Landing page: https://snikzik.github.io/Improov-Homes/open-house/
