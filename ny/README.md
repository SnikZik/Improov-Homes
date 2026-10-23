# 1057 Bond St, New York audience page

`/ny/` on the same site as the main page. Same call-only rules (no form, no
WhatsApp, no navigation, no outbound links), plus a two-question qualifier
between every call button and the phone line, agreed on the 6 Oct 2026 call.

Live URL once pushed: `https://snikzik.github.io/Improov-Homes/ny/`

## Everything you might change lives at the top of `ny.js`

| Block | What it controls |
|---|---|
| `phoneConfig` | NY tracking number. **Still the main campaign number** until Imbar's NY line is in; flip `isPlaceholder` to false when it is. It appears only in the qualifier's last step, after both questions, never on the page itself. |
| `officeConfig` | Brokerage office number, shown as text (NJ display rule), never a tap target, so it does not bypass the qualifier. |
| `hoursConfig` | Call hours, Eastern. Outside them the qualifier shows the number and the opening time instead of a tap-to-call button. `enforce:false` turns this off. |
| `gateConfig` | Which "no" answers stop the call. Only the New Jersey question does. The rental-income question is informational: blocking it would screen out buyers who want the whole house for their own household, a fair-housing risk. |
| `subject` | The house. List price $899,000, cut from $999,000 in Oct 2026 (`oldPrice`). The old price is shown only struck through (`<s>`): hero line, price band, comparison table note. The page never prints $999,000 on its own. Verified against GSMLS #4057212 and the 2025 tax bill on 15 Oct 2026. |
| `workDone` | The work done, in the client's words: New roof. New central air. New kitchens in both units. Updated baths. Refinished wood floors. Shown under The property. |
| `answererName` | Roi. He answers every call on this line, so the popup's last button reads "Call Roi" plus the number and the team section says Roi answers this line for Improov Homes. No title for Roi. The broker lines ("Improov Homes, Licensed Real Estate Broker", Imbar Meidani as Principal Broker) stay as they are. |
| `loanExample.apr` | **Reg Z switch.** Empty = the page shows prices only and no financing numbers. Paste the lender's APR and the down payment, cash to close, monthly payment and income rows come back with the full disclosure. Preview the financing version with `?preview_financing=1`. |
| `comparisonConfig` | The comps. Only 144-11 223rd St, Laurelton is in. 203 Essex St is out (its deed also bought the vacant lot next door) and 185 Bennett Ave, Yonkers is out (3 units, 3,785 sq ft). |
| `commuteConfig` | Only verified figures (NJ Transit timetables). |
| `videoConfig` | Hero video: `../videos/web/lead-899.mp4` with poster `../videos/web/lead-899-poster.jpg` (9:16 lead, voiceover, says the $899,000 price, no phone number). |

## Events (same names as the main page, page id `bond-street-1057-ny`)

`QualifierOpen`, `QualifierAnswer`, `QualifierPass`, `QualifierBlocked`,
`CallOutsideHours`, plus everything the main page sends. `CallButtonClick` and
the Meta `Contact` event fire only on the tap-to-call inside the qualifier.
`?lp_debug=1` prints every event.

## Before ads point here

1. Imbar's NY number into `phoneConfig`.
2. Lender's APR into `loanExample.apr`, in writing, dated. Without it the page stays in prices-only mode, which is compliant.
3. Confirm the brokerage's exact registered name on the DOBI licensee search and use it in the broker block and footer.
4. Ask Roee for two more clean two-family sales (Brooklyn and Queens, 2 legal units, about 2,000 to 3,000 sq ft, closed in the last six months). Add them to `comparisonConfig`; the table switches back to sideways scrolling by itself at 3+ columns.
