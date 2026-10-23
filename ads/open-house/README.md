# 1057 Bond, open house Oct 24 and 25

Updated 23 Oct with the client's feedback: the old price is shown crossed out before the new
one, the work list is in the client's words, and the call line names Roi.

| File | Use | Built by |
|---|---|---|
| `open-house_feed-4x5.png` | Feed | `../oh-src/build_open_house.py` |
| `open-house_story-9x16.png` | Stories still | `../oh-src/build_open_house.py` |
| `open-house_reel-9x16.mp4` | Reels and Stories, 24 s, no audio (add music from Meta's library at upload) | `../oh-src/build_open_house.py` |
| `open-house_reel-9x16_gia.mp4` | Reel B: the same footage and exterior shots with Gia's voice, 27.6 s | `../open-house-vo/build_open_house_vo.py --reel-b` |
| `../open-house-vo/open-house-vo_reel-9x16.mp4` | Voiceover reel, walkthrough only, 27.6 s | `../open-house-vo/build_open_house_vo.py` |

Footage: Imbar's WhatsApp walkthrough (21 Oct, 464x624) plus two exterior shots from her earlier
clips. Those clips carry burned-in captions ("10 MIN TO NEWARK AIRPORT" from 9.2 s of
`videos/pays-for-itself.mp4`), so every window of them stays inside `CLEAN` in the builder (3.5 to
8.6 s of pays-for-itself, 3.5 to 14.6 s of C3) and the builds stop if one does not. Reel B opens
with two shots under one headline for that reason (23 Oct). Voice: `../vo-899k/vo-openhouse-ad-gia.wav` (ends "Call 551 324 1057", for ads only).

On every creative: <s>$999,000</s> crossed out, then $899,000. The old price never appears
without the strikethrough (the builders stop if it does). Work list, exactly: New roof. New
central air. New kitchens in both units. Updated baths. Refinished wood floors.

Rebuild everything:

    python3 ads/oh-src/build_open_house.py
    python3 ads/open-house-vo/build_open_house_vo.py
    python3 ads/open-house-vo/build_open_house_vo.py --reel-b

## Meta ad text

**Primary text**

> OPEN HOUSE this weekend in Elizabeth, New Jersey.
> 1057 Bond St, Elizabeth, NJ 07201. Price reduced $100,000. Now $899,000.
>
> Saturday, Oct 24 · 12 to 3 PM
> Sunday, Oct 25 · 1 to 3 PM
>
> Legal two-family in New Jersey, renovated in 2026. New roof. New central air. New kitchens in both units. Updated baths. Refinished wood floors. Parking available. Live in one unit and let the rent from the other help pay the mortgage. Low-down-payment financing with no mortgage insurance is available to qualified owner-occupant buyers, subject to lender approval.
>
> From Elizabeth, NJ it is about 33 minutes by train to NYC Penn Station.
>
> Not ready to buy? Rent to own. The first-floor unit plus the finished lower level is $4,500 a month: 3 bedrooms, 2 full baths and the new kitchen on the main level, two bonus rooms and a full bath below. Rent now with the option to buy, and ask for the written terms at the open house.
>
> Call Roi at (551) 324-1057.
> Improov Homes, Licensed Real Estate Broker (New Jersey). Equal Housing Opportunity.

**Headline:** Open House in Elizabeth, New Jersey · $899,000
**Description:** Sat & Sun open house · Call Roi at (551) 324-1057
**Button:** Learn More (to the open house page, so the pixel counts the lead)

Plain text in Meta cannot strike through, so the ad text never names the old
price: it says "Price reduced $100,000. Now $899,000."

No down payment amount or percentage, monthly payment, rate or term anywhere: keep it that way,
or the ad becomes a credit ad that needs the APR (Reg Z).

## Before launch

- $899,000 must already be the price on GSMLS. On 21 Oct the public listing sites still showed the old price.
- The work list is the client's (23 Oct); it was not part of the 15 Oct fact check.
- Meta: Special Ad Category = Housing. End the campaign Sun Oct 25, 3 PM.
