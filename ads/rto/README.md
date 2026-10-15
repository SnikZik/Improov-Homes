# 1057 Bond, rent-to-own creative

Built by `../rto-src/build_rto_video.py` from Imbar's own edited clips. Our top bar
and bottom panel cover the clips' burned-in captions and FOR SALE tags; the
house and Imbar's picture-in-picture show through. No audio track: add licensed
music from Meta's library at upload.

| File | Use |
|---|---|
| `rto-3900_reel-9x16.mp4` | Reels / Stories, 20 s, rent $3,900 (what Imbar said on the 6 Oct call). Use only after the PadMapper listing says $3,900 too. |
| `rto-3900_feed-4x5.png` | Feed image |
| `rto-4500_*` | Same, at $4,500. **Matches the live PadMapper listing today, so this is the one that can run now.** |

Rebuild with other values: edit `CFG` in the builder, then

    python3 ads/rto-src/build_rto_video.py 3900

## Before upload

- One rent number. The call said $3,900, PadMapper says $4,500. The ad and the listing must match.
- Written rent-to-own terms must exist (option fee, rent credit, purchase price, term). The creative promises an option to buy and the written terms on request, nothing more. It does not show the $999,000 sale price, because nobody has confirmed the option covers the whole house at that price.
- The phone on the end card is the 1057 Bond line. Swap in the rent-to-own campaign's own number if Imbar gives one.
- Meta: Special Ad Category = Housing. Ad schedule 9:00 to 19:00 needs a lifetime budget.

## Meta ad copy (rent $4,500 version, matches the live listing)

**Primary text**

> Rent-to-own only. A renovated 5 bed, 3 bath home on the first floor plus a bonus lower level, at 1057 Bond St, Elizabeth, NJ, for $4,500 a month.
>
> Hardwood floors, a new kitchen with stainless appliances, central air, and a bonus lower level with two more bedrooms and a bath. Assigned parking, garage parking available, laundry hookups in the unit. About 33 minutes to NY Penn Station on NJ Transit from Elizabeth station, 0.6 miles from the house.
>
> Rent now with an option to buy. Call for the written terms. Subject to application approval.
>
> Improov Homes, Licensed Real Estate Broker. Equal Housing Opportunity.

**Headline:** Rent-to-own · 5 bed · Elizabeth, NJ
**Description:** $4,500 a month · (551) 324-1057
**Button:** Call Now

No down payment, monthly mortgage payment or rate anywhere in this copy, so no Reg Z disclosure is needed. Keep it that way: adding "$35K down" or a mortgage payment turns it into a credit ad.
