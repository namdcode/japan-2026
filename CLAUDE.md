# Japan + Korea 2026 — group trip site

## What this repo is

This repo *is* the trip. `index.html` is a single-file, mobile-first trip companion — a full-screen interactive map of the route, with the stage/day detail and the booking checklist layered over it — hosted on GitHub Pages for a group trip to Japan + South Korea, **Nov 13 → Dec 4, 2026 (21 nights)**, for **5 travelers** departing from/returning to Paris CDG via Haneda.

Nam is the trip organizer — logistics, bookings, and this doc are all on them. This is Nam's **second trip to Japan** (don't re-explain JR Pass, Suica/Pasmo, konbini, or other basics unless asked), but a first trip to Korea for the group, so treat Busan content as first-timer-friendly. The group is a couple + friends; core interests, in priority order: **nature/rando/onsen → food & izakaya → temples/culture/histoire**, at a balanced pace (no marathon days). Group coordinates via Discord.

## Source of truth: index.html itself

There is no separate canonical Markdown itinerary for this repo — **`index.html` is the single source of truth**. Nam deliberately develops directly in the HTML because it's the artifact that actually gets read by the group (GitHub Pages hosting is required: Discord's iOS Quick Look blocks JavaScript in direct HTML attachments, so the interactive tabs only work when served over the web, not as a downloaded file).

All content lives in plain JS data arrays inside the `<script>` block — edit these directly rather than inventing a parallel doc:

- **`STAGES`** — array of one object per leg/city: `dates`, `nights`, `lodging`, `days` (day-by-day notes with an hour-by-hour `blocks` list). This one array feeds everything on the map: the lodging card (`STAGES[].lodging`, no separate stays array), the activities sheet, and the day detail. `id` must match the `stage` of a city in `tools/build_map.py`, or that stage gets no pin.
  - A block may carry **`place:"<id>"`**, and a day may carry a `place:` of its own that overrides its blocks. The id must exist in `CITIES` or `LANDMARKS` in `tools/build_map.py` — it is what the map zooms to (see "Days point at places" below). Add the landmark to the generator and re-run it *before* referencing a new id.
- **`TODOS`** — outstanding bookings with deadlines (`dl`) and an urgency flag (`hot`). Check these off as things get booked; keep the deadline text current.
- **`INFOS`** — trip-wide practical cards (momiji timing, weather/gear, the holiday-weekend trick, transport summary, 5-person logistics). Shown under the checklist, in overview mode.
- **`PRACTICAL`** — **per-stage** practical cards, keyed by stage `id`: how to get around, where/what to eat, historical bearings, local tips. Same card shape as `INFOS` (`{icon, title, items[]}`), rendered by the same top-right sheet once a stage is selected. Written broad and not yet fact-checked stage by stage — this is the array to refine when the content session happens.
- **`MAP`** — **generated, do not hand-edit.** Sits between `/* MAP:BEGIN */` and `/* MAP:END */`. Regenerate with `python3 tools/build_map.py` (see below).

Site content is in **French** (for the group) — keep new content in French to match. (The `v3 · mis à jour…` footer note went away with the list view; there is no version line on the page any more.)

## The map — this is the primary view

**The map is the whole page.** There is no longer a list view, a hero, or a tab bar — those were deleted once the map was trusted. `index.html` renders one full-screen dark map (`#mapView`) of Japan + South Korea in the momiji palette. Only **one** full-screen sheet is left, `#extrasSheet`; the day programme is no longer a drawer over the map (see below). There is a single dark palette; no light theme remains.

Layout:
- **Overview** (no stage selected): the trip summary — kicker, title, dates, chips — sits over the map and fades out on selection.
- **Selecting a stage** (tap a pin, the arrows, or hover on desktop) flies the `viewBox` there and reveals two panels: a **lodging card** and the **stage sheet**.
- Mobile stacks them (lodging top, stage sheet bottom); at ≥760px they move to the left and right edges. Controls and legend stay bottom in both.
- **The top-right button changes subject with the view** (`setTopBtn()`), because the corner is prime real estate and the checklist is only useful before leaving. In overview it is **`À faire`** with a live count badge, opening `#extrasSheet` on `TODOS` + `INFOS` (they carry the trip's hard deadlines — they only ever existed in the deleted list view and were moved here rather than dropped). With a stage selected it becomes **`<emoji> Infos`** and the same sheet shows that stage's `PRACTICAL` cards, with a button at the bottom to fall back to the checklist so the deadlines stay one tap away.

**Nothing covers the map for long.** Both panels get out of the way, because on a phone they otherwise leave a thin strip of map between them:
- The lodging card has a **×**; the little house button in the stage sheet header brings it back (`lodgingOpen`).
- The stage sheet **folds to its header** — tap the header, swipe it down, or tap the bottom bar (`folded` / `setFolded()`). Folded, it still names the stage, so the map is readable with the context intact.
- Every fold or close calls `recentre()`, which re-flies the map into the enlarged free band — unless `userMoved` is set, in which case the user's own framing is left alone and a ⊙ button appears in the HUD to restore it.

**The stage sheet is two panes on a rail**, not a drawer: `#paneList` (the days) and `#paneDay` (the programme of one day), sliding left/right inside `.inner` — the direction the chevrons point. `sizeSheet()` sets `.inner`'s height in pixels so the swap and the fold animate with one transition; `.inner` is `overflow:clip` (**not** `hidden` — a `hidden` box is still scrollable, and clicking a button inside it made the browser scroll the header out of sight).

**Gestures.** `#mapSvg` handles pointer events directly: drag to pan, two fingers or the wheel to zoom (`clampView()` bounds the zoom to `MIN_VIEW_W…1.3×home` and keeps the view centre inside the map), with a short inertial `glide()`. Pan/zoom run through the same `raf` handle as `flyTo()`, so any flight cancels cleanly. A drag that ends on a pin must not select it — that is what `gestureMoved` is for.

Four things are easy to break here:
- **`freeRect()` / `focusPoint()`** — the panels cover part of the frame, so the selected city is centred in what remains visible, not in the frame. This is why the same code works for both the stacked and side-by-side layouts. If you add or move a panel, teach `freeRect()` about it or cities will end up behind it. It reads the stage sheet's *target* height (`sheetInner.style.height`), not its live box, so a fly triggered mid-fold still aims at the final layout.
- **`stageView()` scales the zoom by `frameWidth / bandWidth`** so the visible band always shows the same geographic extent. Without it, a wide screen whose panels eat both edges magnifies the coastline until it looks angular.
- **Sizing reads `getBoundingClientRect()`, never `clientWidth`** — the latter returns 0 on `<svg>` in several engines, which silently sizes everything against the fallback. A `ResizeObserver` on `#mapView` refits on rotation and resize.
- **Header taps vs. header swipes** — the fold handles listen to both `click` and pointer drags, so a swipe swallows the click it also generates, and buttons inside a header skip pointer capture (capture would steal their click).
- **Map targeting is nearest-point, not hit-testing** (`pickTarget()`). Per-pin hit circles cannot work here: at country zoom Tokyo and Haneda are ~3 px apart, so 22 px targets overlap and the last-drawn element silently eats its neighbours — Osaka swallowed Okayama, Yufuin swallowed Fukuoka, and half the map stopped responding. A click on the `<svg>` now picks the closest point within 26 px, which no drawing order can bias. Landmarks join the candidates only while `zoomedIn` and on the current stage — you can only click what you can see.
- **`setPointerCapture` retargets the follow-up `click`**, to the capturing element. Capturing on `pointerdown` therefore kills every click underneath — it silently broke tapping a pin once already. Capture only once a drag is real (`travel > 4`), by which point the click is meant to be suppressed anyway.

Tapping a city, or stepping with the arrows, flies the SVG `viewBox` to that stage — pulling back toward the whole country in proportion to how far the two stages are apart, so Busan→Tokyo sweeps out and Okayama→Osaka barely moves.

### Days point at places

A day's programme drives the map, at the granularity of the day rather than the city:

- `autoPlace()` — if the day's blocks name exactly **one** `place`, and it belongs to the current stage, opening that day zooms to it (Saturday in Tokyo goes to Mitaka, Monday to Yomiuriland, USJ day to USJ). A day-level `place:` overrides this outright (that is how Nov 26 goes to Kurashiki rather than sitting on Okayama).
- A day spanning **several** places stays on its stage city — Kujū and Kurokawa cannot both be framed — and each block shows a **« Voir »** button that flies there on demand. The active place gets a pulsing ring, and it is the only landmark labelled while it is focused (labels collide at that zoom).
- `placeView()` zooms tighter than a stage by `0.62`. Don't push it much further: the base map is Natural Earth 1:50m, and below roughly `MIN_VIEW_W` the coastline is visibly a polygon.
- The HUD arrows are context-sensitive: they step **stages** on the day list, and **days** (`FLAT_DAYS`, across stage boundaries) while a programme is open. This is deliberate — the day pane deliberately has no navigation controls of its own.
- Deep links still work: `#j-<stage>-<day>` opens the stage and the day (`syncFromHash()`).

**Cities are never placed by eye.** `tools/build_map.py` projects both the Natural Earth coastlines and each city's real latitude/longitude through the same Mercator projection, so a pin is correct by construction. An earlier hand-drawn version got thrown away precisely because eyeballing pixel positions produced a map that looked like clip art and put cities in the sea.

To change what the map shows — add a city, add a landmark (including any place a day's `place:` needs), adjust the crop or zoom level — edit the constants at the top of `tools/build_map.py` (`CITIES`, `LANDMARKS`, `MIN_LAT`, `ZOOM_WIDTH`) and run:

```bash
python3 tools/build_map.py
```

It rewrites the `MAP` block inside `index.html` in place and is idempotent. Source geodata is cached at `tools/.ne50_cache.geojson` (gitignored, ~3 MB); pass `--refetch` to re-download. Natural Earth is public domain, so no attribution is legally required — the credit line under the map is courtesy.

Route legs and their transport type (rail / sea / air) live in the `LEGS` array in `index.html`, not in the generator, because they describe the trip rather than the geography.

## Confirmed trip structure (accommodations locked, do not treat as tentative)

1. **Tokyo** (arr. Nov 13, Haneda 14:25) — 4 nights, incl. PokéPark Kanto Mon Nov 16
2. **Yufuin, Kyushu** — 2 nights, rental minivan, Kujū hike + Kurokawa onsen day
3. **Fukuoka** — 2 nights, yatai/Nakasu, Dazaifu
4. **Busan, South Korea** — 2 nights, via Camellia Line ferry (Fukuoka→Busan day sailing Nov 21, already booked for 5; return overnight ferry Nov 23→24). Deliberately overlaps the Japanese Labor Thanksgiving holiday weekend (Kinrō Kansha no Hi, Nov 21–23) to dodge peak domestic crowds.
5. **Hiroshima + Miyajima** — 2 nights, post-holiday weekdays (quieter Miyajima/momiji)
6. **Okayama** (base) + **Kurashiki** day trip — 1 night
7. **Himeji** — brief stop en route, no overnight
8. **Kansai/Osaka** (Ebisuhigashi/Shinsekai) — 5 nights: Nara, USJ, Kyoto at momiji peak (Tōfuku-ji, Arashiyama, Higashiyama), one flex/rest day
9. **Tokyo return** — 2 nights, departs Haneda Dec 4, 08:25

Routing logic: southwest-first, eastward sweep (Kyushu → Korea → Hiroshima → Kansai → Tokyo) — this avoids a dead block of unused Tokyo nights at the end and lets the Busan leg absorb the worst holiday congestion.

## Open items (check `TODOS` in index.html for current state/deadlines)

- **PokéPark Kanto — 5 tickets, same slot (Mon Nov 16)**: lottery-based, ~3 months out, no walk-up sales. Per the file, lottery window is **≈ mid-August 2026** — this is the single most time-sensitive item outstanding, worth flagging to Nam proactively as that date approaches.
- **Ghibli Museum**: not yet in the itinerary — was raised as an omission. Proposed slot is **Sat Nov 14** (currently free in Tokyo), keeping Mon Nov 16 solely for PokéPark (the two don't combine well in one day: incompatible timed-entry systems + ~50–60 min Mitaka↔Yomiuriland transit). Ticket sales open **10:00 JST on the 10th of the month prior** — the **Oct 10, 2026** window (~3:00 a.m. French time) is the one to hit for a Nov 14 visit. Not yet confirmed or added to `STAGES` — ask before adding.
- Real group photos to substitute in once the trip happens (a separate cinematic "trailer" HTML with a `PHOTOS` config block was previously discussed but is not in this repo yet — only build it if Nam asks).
- Minivan rental (Fukuoka, 7–8 seats, ETC card for tolls), JAF translations for French driving licenses (one per driver — an International Driving Permit alone isn't sufficient), USJ Express Pass, shinkansen seat reservations ×5 legs, restaurant/izakaya bookings for 5 (many counters cap at 4 — need tables, especially Kyoto/Osaka).

## Key constraints & learnings

- Aso Nakadake crater is closed in 2026 (helicopter incident) — grasslands/viewpoints still open.
- Kurashiki was chosen over Onomichi for the canal-district look; sea views are already covered by Busan/Fukuoka.
- Ghibli + PokéPark should never be combined on the same day (see above).
- French driving licenses need an official **JAF translation** to drive in Japan — the IDP alone doesn't cover it.
- Interactive JS features require GitHub Pages (or similar) hosting — a raw HTML file shared via Discord on iOS won't run its JS.

## Working style Nam wants

- Be concrete and actionable: exact place/restaurant/trail names, neighborhoods, realistic travel times, rough costs, and a routing that avoids backtracking.
- Since it's a 2nd Japan trip, favor alternatives/less-touristy options over first-timer classics — but don't block a requested classic.
- Always sanity-check anything time-sensitive (hours, closures, booking requirements, seasonal events, weather/transport disruption) — don't rely on possibly-stale knowledge for these.
- Flag group/couple logistics explicitly: reservations for 5, advance booking needs (popular restaurants, ryokan, private onsen).
- Ask rather than assume when info is missing — don't invent details.
- Keep formats tight: day-by-day when useful, scannable lists, concise summaries.
