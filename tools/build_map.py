#!/usr/bin/env python3
"""
Regenerate the map data embedded in index.html.

Source : Natural Earth 1:50m admin-0 countries (public domain, no attribution
         required) — https://www.naturalearthdata.com/
Output : rewrites the `const MAP = …` line in index.html, between the
         /* MAP:BEGIN */ and /* MAP:END */ markers.

Why this exists: city pins must land where the cities actually are. Placing them
by eye on a drawing is what made the first version of this map look wrong. Here
the coastline and the pins go through the same Mercator projection, so a pin is
correct by construction.

It writes straight into index.html rather than leaving a file to copy across,
so the map on the page and the data it came from cannot drift apart.

Usage:
    python3 tools/build_map.py            # uses cached geojson if present
    python3 tools/build_map.py --refetch  # re-download source data
"""

import argparse
import json
import math
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".ne50_cache.geojson")
TARGET = os.path.join(os.path.dirname(HERE), "index.html")
BEGIN = "/* MAP:BEGIN"
END = "/* MAP:END */"

SOURCE = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
    "master/geojson/ne_50m_admin_0_countries.geojson"
)

COUNTRIES = ("Japan", "South Korea")

# Ryukyu / Okinawa stretch ~800 km southwest of Kyushu, and the Ōsumi islands
# sit alone below Kyushu. The trip goes nowhere near them, and keeping them
# stretches the bounding box enough to shrink Honshu noticeably on a phone.
# Everything below this latitude is dropped.
MIN_LAT = 31.0

# Drop specks that are a couple of pixels at most — they add file size and read
# as visual noise rather than as islands.
MIN_POLY_AREA_DEG2 = 0.05

# Anchor cities, real coordinates. `stage` matches an id in the STAGES array in
# index.html; a null stage means the point is drawn for context only.
CITIES = [
    # id,          label,        lat,      lon,      stage
    ("tokyo",      "Tokyo",      35.6812,  139.7671, "tokyo1"),
    ("yufuin",     "Yufuin",     33.2645,  131.3600, "yufuin"),
    ("fukuoka",    "Fukuoka",    33.5904,  130.4017, "fukuoka"),
    ("busan",      "Busan",      35.1796,  129.0756, "busan"),
    ("hiroshima",  "Hiroshima",  34.3853,  132.4553, "hiroshima"),
    ("okayama",    "Okayama",    34.6551,  133.9195, "okayama"),
    ("osaka",      "Osaka",      34.6937,  135.5023, "osaka"),
    ("haneda",     "Haneda",     35.5494,  139.7798, "tokyo2"),
]

# Secondary places worth showing when zoomed into a stage. Not clickable pins,
# but a day's programme can point at one (`place:` in STAGES) to zoom there.
LANDMARKS = [
    ("kamakura",    "Kamakura",    35.3192,  139.5467, "tokyo1"),
    ("mitaka",      "Mitaka",      35.6962,  139.5601, "tokyo1"),
    ("yomiuriland", "PokéPark",    35.6280,  139.5169, "tokyo1"),
    ("kuju",        "Kujū",        33.0833,  131.2500, "yufuin"),
    ("kurokawa",    "Kurokawa",    33.0800,  131.0300, "yufuin"),
    ("aso",         "Aso",         32.8846,  131.0817, "yufuin"),
    ("dazaifu",     "Dazaifu",     33.5150,  130.5350, "fukuoka"),
    ("gamcheon",    "Gamcheon",    35.0975,  129.0106, "busan"),
    ("yonggungsa",  "Yonggungsa",  35.1884,  129.2233, "busan"),
    ("taejongdae",  "Taejongdae",  35.0520,  129.0873, "busan"),
    ("miyajima",    "Miyajima",    34.2959,  132.3197, "hiroshima"),
    ("kurashiki",   "Kurashiki",   34.5850,  133.7720, "okayama"),
    ("himeji",      "Himeji",      34.8154,  134.6854, "osaka"),
    ("kyoto",       "Kyoto",       35.0116,  135.7681, "osaka"),
    ("nara",        "Nara",        34.6851,  135.8048, "osaka"),
    ("usj",         "USJ",         34.6654,  135.4323, "osaka"),
]

# Rendering box. Height follows from the projection's aspect ratio.
WIDTH = 1000.0
PAD = 12.0

# Width of a stage's zoom window, in projected units. Tuned so a stage fills the
# frame with enough surrounding coast to stay recognisable. The matching height
# is derived in the page from the real viewport, not here: the map is now
# full-screen, so only the browser knows the aspect ratio to fill.
ZOOM_WIDTH = 156.0


def mercator(lat, lon):
    """Web Mercator. Returns unscaled (x, y) with y increasing northward."""
    x = math.radians(lon)
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def ring_area(ring):
    """Shoelace area in square degrees — only used to rank polygons by size."""
    a = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[i + 1][0], ring[i + 1][1]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


def load_source(refetch=False):
    if refetch or not os.path.exists(CACHE):
        print(f"fetching {SOURCE}")
        urllib.request.urlretrieve(SOURCE, CACHE)
    with open(CACHE) as fh:
        return json.load(fh)


def collect_rings(geojson):
    """Outer rings for the countries we care about, filtered and ranked."""
    out = {}
    for feature in geojson["features"]:
        props = feature["properties"]
        name = props.get("NAME") or props.get("ADMIN")
        if name not in COUNTRIES:
            continue
        geom = feature["geometry"]
        polys = (
            geom["coordinates"]
            if geom["type"] == "MultiPolygon"
            else [geom["coordinates"]]
        )
        kept = []
        for poly in polys:
            outer = poly[0]
            if max(pt[1] for pt in outer) < MIN_LAT:
                continue
            if ring_area(outer) < MIN_POLY_AREA_DEG2:
                continue
            kept.append(outer)
        kept.sort(key=ring_area, reverse=True)
        out[name] = kept
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refetch", action="store_true")
    args = ap.parse_args()

    rings = collect_rings(load_source(args.refetch))
    for name in COUNTRIES:
        if name not in rings:
            raise SystemExit(f"country missing from source data: {name}")

    all_points = [pt for country in rings.values() for r in country for pt in r]
    all_points += [(lon, lat) for _, _, lat, lon, _ in CITIES]

    projected = [mercator(lat, lon) for lon, lat in all_points]
    min_x = min(p[0] for p in projected)
    max_x = max(p[0] for p in projected)
    min_y = min(p[1] for p in projected)
    max_y = max(p[1] for p in projected)

    scale = (WIDTH - 2 * PAD) / (max_x - min_x)
    height = (max_y - min_y) * scale + 2 * PAD

    def to_svg(lat, lon):
        x, y = mercator(lat, lon)
        # y is flipped: projection grows north, SVG grows down.
        return (
            round((x - min_x) * scale + PAD, 1),
            round((max_y - y) * scale + PAD, 1),
        )

    def ring_to_path(ring):
        pts = [to_svg(lat, lon) for lon, lat in ring]
        # Drop consecutive duplicates left behind by rounding.
        deduped = [pts[0]]
        for p in pts[1:]:
            if p != deduped[-1]:
                deduped.append(p)
        head = f"M{deduped[0][0]} {deduped[0][1]}"
        tail = "".join(f"L{x} {y}" for x, y in deduped[1:])
        return head + tail + "Z"

    paths = {
        "japan": [ring_to_path(r) for r in rings["Japan"]],
        "korea": [ring_to_path(r) for r in rings["South Korea"]],
    }

    def place(entries):
        out = []
        for cid, label, lat, lon, stage in entries:
            x, y = to_svg(lat, lon)
            out.append({"id": cid, "label": label, "x": x, "y": y, "stage": stage})
        return out

    cities = place(CITIES)
    landmarks = place(LANDMARKS)

    payload = {
        "width": round(WIDTH, 1),
        "height": round(height, 1),
        "zoomWidth": ZOOM_WIDTH,
        "paths": paths,
        "cities": cities,
        "landmarks": landmarks,
    }

    line = "const MAP = " + json.dumps(payload, ensure_ascii=False) + ";"

    with open(TARGET) as fh:
        html = fh.read()
    try:
        i = html.index(BEGIN)
        j = html.index(END, i) + len(END)
    except ValueError:
        raise SystemExit(
            f"markers {BEGIN}…{END} not found in {TARGET} — restore them before rebuilding"
        )
    head = html[i : html.index("\n", i)]  # keep the existing BEGIN comment as-is
    html = html[:i] + head + "\n" + line + "\n" + END + html[j:]
    with open(TARGET, "w") as fh:
        fh.write(html)

    print(f"rewrote MAP block in {TARGET} ({len(line)/1024:.1f} KB of data)")
    print(f"  viewBox 0 0 {WIDTH:.0f} {height:.0f}")
    print(f"  japan: {len(paths['japan'])} rings, korea: {len(paths['korea'])} rings")
    print(f"  cities: {len(cities)}, landmarks: {len(landmarks)}")


if __name__ == "__main__":
    main()
