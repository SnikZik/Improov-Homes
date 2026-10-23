# 1057 Bond, rent-to-own creative

Built by `../rto-src/build_rto_video.py` from Imbar's own edited clips. Our top bar
and bottom panel cover the clips' burned-in captions and FOR SALE tags; the
house and Imbar's picture-in-picture show through. The reels in this folder are
silent; the $4,500 reel with the Gia voiceover is in `../rto-vo/`.

| File | Use |
|---|---|
| `rto-3900_reel-9x16.mp4` | Reels / Stories, 20 s, rent $3,900 (what Imbar said on the 6 Oct call). Use only after the PadMapper listing says $3,900 too. |
| `rto-3900_feed-4x5.png` | Feed image |
| `rto-4500_*` | Same, at $4,500. **Matches the live PadMapper listing today, so this is the one that can run now.** |
| `../rto-vo/rto-4500_reel-9x16_gia.mp4` | The $4,500 reel with the Gia voiceover (22.4 s). This is the file to upload. |

Rebuild with other values: edit `CFG` in the builder, then

    python3 ads/rto-src/build_rto_video.py 4500

For 4500 the builder also lays the Gia voice under the silent reel (150 ms in,
loudnorm -16 LUFS in two passes, AAC, faststart) and writes `../rto-vo/rto-4500_reel-9x16_gia.mp4`.
The page version (`../rto-page-src/build_rto_page_video.py`, no phone number on any frame)
does the same into `rent-to-own/media/lead.mp4` and `rent-to-own/img/lead-poster.jpg`.

## Before upload

- One rent number. The call said $3,900, PadMapper says $4,500. The ad and the listing must match.
- Written rent-to-own terms must exist (option fee, rent credit, purchase price, term). The creative promises an option to buy and the written terms on request, nothing more. It does not show the sale price (now $899,000, reduced from $999,000), because nobody has confirmed the option covers the whole house at that price.
- The phone on the end card is the 1057 Bond line. Swap in the rent-to-own campaign's own number if Imbar gives one.
- Meta: Special Ad Category = Housing. Ad schedule 9:00 to 19:00 needs a lifetime budget.

## Meta ad copy (rent $4,500 version, matches the live listing)

**Primary text**

> Rent-to-own only. A renovated 5 bed, 3 bath home on the first floor plus a bonus lower level, at 1057 Bond St, Elizabeth, NJ, for $4,500 a month.
>
> New roof. New central air. New kitchens in both units. Updated baths. Refinished wood floors. The bonus lower level adds two more bedrooms and a bath. Assigned parking, garage parking available, laundry hookups in the unit. About 33 minutes to NY Penn Station on NJ Transit from Elizabeth station, 0.6 miles from the house.
>
> Rent now with an option to buy. Call Roi for the written terms. Subject to application approval.
>
> Improov Homes, Licensed Real Estate Broker. Equal Housing Opportunity.

**Headline:** Rent-to-own · 5 bed · Elizabeth, NJ
**Description:** $4,500 a month · Call Roi (551) 324-1057
**Button:** Call Now

No down payment, monthly mortgage payment or rate anywhere in this copy, so no Reg Z disclosure is needed. Keep it that way: adding "$35K down" or a mortgage payment turns it into a credit ad.

## Update 23 Oct 2026 (client feedback)

- The work done is listed in the client's words everywhere: New roof. New central air.
  New kitchens in both units. Updated baths. Refinished wood floors.
  - Reel scene 2: "New roof, new central air" / "New kitchens in both units, updated baths, refinished wood floors".
  - $4,500 feed still: the five items as one line, plus "Call Roi at (551) 324-1057".
  - Meta ad text above: "New kitchens in both units" replaces "New kitchen with stainless appliances".
- The end card says "Call Roi for the written terms."
- The reel is cut on the Gia voice (Whisper large-v3-turbo, checked against silencedetect).
  Video clock, voice 150 ms in:

  | Voice | Time | On screen |
  |---|---|---|
  | Rent to own at 1057 Bond Street in Elizabeth, New Jersey. | 0.6 to 5.2 s | 5 bed · 3 bath on two levels (facade) |
  | Five bedrooms and three baths on two levels. | 6.0 to 9.1 s | same text, lower level footage |
  | Renovated in 2026. | 9.5 to 11.5 s | New roof, new central air (cut at 9.1 s) |
  | Assigned parking | 11.9 to 12.9 s | Assigned parking (cut at 11.6 s) |
  | and about 33 minutes by train to Penn Station. | 13.3 to 16.1 s | About 33 min by train (cut at 13.0 s) |
  | $4,500 a month with an option to buy. Call for the written terms. | 16.8 to 21.2 s | end card (from 16.2 s), held to 22.4 s |

  The separate "Bonus lower level" scene is gone; its footage now plays under the beds/baths
  line, whose sub line already says "First floor plus a bonus lower level".
- The Gia voice was not regenerated (no credits). It still says "Renovated in 2026" and
  "Call for the written terms"; the screen carries the work list and Roi's name.
- The $3,900 files were not rebuilt and are stale (old scene 2, no voice).
