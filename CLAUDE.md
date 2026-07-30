# Japan + Korea 2026 — group trip site

## What this repo is

This repo *is* the trip. `index.html` is a single-file, mobile-first trip companion (tabs: itinéraire / logements / checklist / infos, countdown, falling-maple-leaf animation) hosted on GitHub Pages for a group trip to Japan + South Korea, **Nov 13 → Dec 4, 2026 (21 nights)**, for **5 travelers** departing from/returning to Paris CDG via Haneda.

Nam is the trip organizer — logistics, bookings, and this doc are all on them. This is Nam's **second trip to Japan** (don't re-explain JR Pass, Suica/Pasmo, konbini, or other basics unless asked), but a first trip to Korea for the group, so treat Busan content as first-timer-friendly. The group is a couple + friends; core interests, in priority order: **nature/rando/onsen → food & izakaya → temples/culture/histoire**, at a balanced pace (no marathon days). Group coordinates via Discord.

## Source of truth: index.html itself

There is no separate canonical Markdown itinerary for this repo — **`index.html` is the single source of truth**. Nam deliberately develops directly in the HTML because it's the artifact that actually gets read by the group (GitHub Pages hosting is required: Discord's iOS Quick Look blocks JavaScript in direct HTML attachments, so the interactive tabs only work when served over the web, not as a downloaded file).

All content lives in plain JS data arrays inside the `<script>` block — edit these directly rather than inventing a parallel doc:

- **`STAGES`** — array of one object per leg/city: `dates`, `nights`, `lodging`, `days` (day-by-day notes), `next` (transit to the following stage). This one array also drives the "logements" tab (lodging is rendered straight from `STAGES[].lodging` — there's no separate stays array) and the timeline countdown/highlight logic.
- **`TODOS`** — outstanding bookings with deadlines (`dl`) and an urgency flag (`hot`). Check these off as things get booked; keep the deadline text current.
- **`INFOS`** — practical info cards (momiji timing, weather/gear, the holiday-weekend trick, transport summary, 5-person logistics).
- **`MAP`** — **generated, do not hand-edit.** Sits between `/* MAP:BEGIN */` and `/* MAP:END */`. Regenerate with `python3 tools/build_map.py` (see below).

Site content is in **French** (for the group) — keep new content in French to match. When you make a substantive itinerary change, bump the footer note (currently `v3 · mis à jour juillet 2026`).

## The map — this is the primary view

**Carte is the default view and the point of the page.** It is a full-screen dark map (`#mapView`, `body.mode-carte`) of Japan + South Korea in the momiji palette. Liste is a deliberate fallback that Nam intends to delete once the map is trusted — so when the two disagree, the map wins, and don't invest in Liste.

Layout in Carte:
- **Overview** (no stage selected): the trip summary — kicker, title, dates, chips — sits over the map and fades out on selection.
- **Selecting a stage** (tap a pin, the arrows, or hover on desktop) flies the `viewBox` there and reveals two panels: a **lodging card** and an **activities sheet** listing that stage's days (tapping one opens the existing full-screen day sheet).
- Mobile stacks them (lodging top, activities bottom); at ≥760px they move to the left and right edges. Controls and legend stay bottom in both.

Three things are easy to break here:
- **`freeRect()` / `focusPoint()`** — the panels cover part of the frame, so the selected city is centred in what remains visible, not in the frame. This is why the same code works for both the stacked and side-by-side layouts. If you add or move a panel, teach `freeRect()` about it or cities will end up behind it.
- **`stageView()` scales the zoom by `frameWidth / bandWidth`** so the visible band always shows the same geographic extent. Without it, a wide screen whose panels eat both edges magnifies the coastline until it looks angular.
- **Sizing reads `getBoundingClientRect()`, never `clientWidth`** — the latter returns 0 on `<svg>` in several engines, which silently sizes everything against the fallback. A `ResizeObserver` on `#mapView` refits on rotation, resize, and the list→map switch (the frame has no size until it is displayed).

Tapping a city, or stepping with the arrows, flies the SVG `viewBox` to that stage — pulling back toward the whole country in proportion to how far the two stages are apart, so Busan→Tokyo sweeps out and Okayama→Osaka barely moves.

**Cities are never placed by eye.** `tools/build_map.py` projects both the Natural Earth coastlines and each city's real latitude/longitude through the same Mercator projection, so a pin is correct by construction. An earlier hand-drawn version got thrown away precisely because eyeballing pixel positions produced a map that looked like clip art and put cities in the sea.

To change what the map shows — add a city, add a landmark, adjust the crop or zoom level — edit the constants at the top of `tools/build_map.py` (`CITIES`, `LANDMARKS`, `MIN_LAT`, `ZOOM_HALF_W`) and run:

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
