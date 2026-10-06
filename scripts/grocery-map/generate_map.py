#!/usr/bin/env python3
"""Build a 4K PNG map of Seattle-area (King County, WA) grocery stores,
overlaid on a choropleth of median household income by zip code.

Data sources (all public):
  - Zip Code Tabulation Area (ZCTA) boundaries for Washington State:
    https://github.com/OpenDataDE/State-zip-code-GeoJSON
    (wa_washington_zip_codes_geo.min.json)
  - Median household income by zip code:
    uszipcode project's bundled SQLite extract of US Census ACS data
    https://github.com/MacHu-GWU/uszipcode-project
    (simple_db.sqlite, released asset 1.0.1.db)
  - Grocery/food retailer locations: USDA SNAP historical retailer
    locator dataset, maintained at https://github.com/jshannon75/snap_retailers
    (hist_snap_retailer_final2022.csv). Only currently-authorized
    (no end_date) stores in actual grocery categories are plotted:
    Supermarket, Super Store, Large/Medium/Small Grocery Store.
    "Combination Grocery/Other" (e.g. pharmacies, dollar stores, and other
    small retailers that also sell some food) is deliberately excluded,
    since those are not grocery stores.

The script downloads these files into ./cache (gitignored) on first run,
then renders a single PNG at 3840x2160 (4K) to the given output path.

Usage:
    python3 generate_map.py [output_path]
"""
import csv
import io
import json
import os
import sqlite3
import sys
import urllib.request
import zipfile

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

ZIP_GEOJSON_URL = (
    "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/"
    "master/wa_washington_zip_codes_geo.min.json"
)
INCOME_DB_URL = (
    "https://github.com/MacHu-GWU/uszipcode-project/releases/download/"
    "1.0.1.db/simple_db.sqlite"
)
SNAP_RETAILERS_ZIP_URL = (
    "https://github.com/jshannon75/snap_retailers/raw/master/data/"
    "hist_snap_retailer_final2022_csv.zip"
)

# Only genuine grocery stores. "Combination Grocery/Other" is excluded on
# purpose: USDA uses that category for small retailers (pharmacies, dollar
# stores, etc.) that sell some food but are not grocery stores.
GROCERY_STORE_TYPES = {
    "Supermarket",
    "Super Store",
    "Large Grocery Store",
    "Medium Grocery Store",
    "Small Grocery Store",
}

TARGET_COUNTY = "King County"
TARGET_STATE = "WA"

# Degrees of padding added around the data extent so points/polygons at the
# edge of the data are not clipped by the axis limits.
MAP_PADDING_DEGREES = 0.03


def _download(url, dest):
    if os.path.exists(dest):
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"Downloading {url} ...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=120) as resp:
        data = resp.read()
    with open(dest, "wb") as f:
        f.write(data)


def load_zip_boundaries():
    path = os.path.join(CACHE_DIR, "wa_zips.geojson")
    _download(ZIP_GEOJSON_URL, path)
    with open(path, encoding="utf-8") as f:
        geo = json.load(f)
    return geo


def load_income_by_zip():
    path = os.path.join(CACHE_DIR, "simple_db.sqlite")
    _download(INCOME_DB_URL, path)
    conn = sqlite3.connect(path)
    rows = conn.execute(
        "SELECT zipcode, median_household_income FROM simple_zipcode "
        "WHERE county=? AND state=?",
        (TARGET_COUNTY, TARGET_STATE),
    ).fetchall()
    conn.close()
    return {z: income for z, income in rows}


def load_all_king_zip_codes():
    path = os.path.join(CACHE_DIR, "simple_db.sqlite")
    _download(INCOME_DB_URL, path)
    conn = sqlite3.connect(path)
    zips = {
        row[0]
        for row in conn.execute(
            "SELECT zipcode FROM simple_zipcode WHERE county=? AND state=?",
            (TARGET_COUNTY, TARGET_STATE),
        )
    }
    conn.close()
    return zips


def load_grocery_stores():
    zip_path = os.path.join(CACHE_DIR, "snap_retailers.zip")
    _download(SNAP_RETAILERS_ZIP_URL, zip_path)
    csv_path = os.path.join(CACHE_DIR, "hist_snap_retailer_final2022.csv")
    if not os.path.exists(csv_path):
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(CACHE_DIR)

    stores = []
    with open(csv_path, encoding="latin-1") as f:
        for row in csv.DictReader(f):
            if row.get("state") != TARGET_STATE:
                continue
            if row.get("cty_name") != "King":
                continue
            if row.get("end_date") != "NA":
                continue  # only currently-authorized retailers
            if row.get("store_type") not in GROCERY_STORE_TYPES:
                continue
            try:
                x = float(row["x"])
                y = float(row["y"])
            except (TypeError, ValueError):
                continue
            stores.append(
                {
                    "name": row["store_name"],
                    "type": row["store_type"],
                    "lon": x,
                    "lat": y,
                }
            )
    return stores


def _iter_rings(geometry):
    gtype = geometry["type"]
    coords = geometry["coordinates"]
    if gtype == "Polygon":
        yield coords[0]
    elif gtype == "MultiPolygon":
        for poly in coords:
            yield poly[0]


def _data_bounds(features, stores):
    """Compute the lon/lat bounding box covering every zip polygon vertex
    and every store point, so nothing is clipped by the axis limits."""
    minx = miny = float("inf")
    maxx = maxy = float("-inf")
    for feat in features:
        for ring in _iter_rings(feat["geometry"]):
            for x, y in ring:
                minx, maxx = min(minx, x), max(maxx, x)
                miny, maxy = min(miny, y), max(maxy, y)
    for s in stores:
        minx, maxx = min(minx, s["lon"]), max(maxx, s["lon"])
        miny, maxy = min(miny, s["lat"]), max(maxy, s["lat"])
    return (
        minx - MAP_PADDING_DEGREES,
        maxx + MAP_PADDING_DEGREES,
        miny - MAP_PADDING_DEGREES,
        maxy + MAP_PADDING_DEGREES,
    )


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "grocery_stores_income_map.png"

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon
    from matplotlib.collections import PatchCollection
    from matplotlib.colors import Normalize
    from matplotlib.cm import ScalarMappable

    geo = load_zip_boundaries()
    income_by_zip = load_income_by_zip()
    all_king_zips = load_all_king_zip_codes()
    stores = load_grocery_stores()

    # Include King County zips with no income figure too, so the boundary
    # still draws (shown in grey) for visual continuity.
    features = [
        feat
        for feat in geo["features"]
        if feat["properties"]["ZCTA5CE10"] in all_king_zips
    ]
    print(f"Zip boundaries matched: {len(features)}", file=sys.stderr)
    print(f"Grocery stores plotted: {len(stores)}", file=sys.stderr)

    xmin, xmax, ymin, ymax = _data_bounds(features, stores)
    out_of_frame = [
        s
        for s in stores
        if not (xmin <= s["lon"] <= xmax and ymin <= s["lat"] <= ymax)
    ]
    if out_of_frame:
        print(
            f"WARNING: {len(out_of_frame)} store(s) fall outside the computed "
            "map frame and would be clipped",
            file=sys.stderr,
        )

    incomes = [v for v in income_by_zip.values() if v]
    norm = Normalize(vmin=min(incomes), vmax=max(incomes))
    cmap = plt.get_cmap("YlGn")
    sm = ScalarMappable(norm=norm, cmap=cmap)

    fig_w, fig_h, dpi = 32, 18, 120  # 3840x2160 px
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor("white")

    patches = []
    colors = []
    for feat in features:
        zc = feat["properties"]["ZCTA5CE10"]
        income = income_by_zip.get(zc)
        color = sm.to_rgba(income) if income else (0.85, 0.85, 0.85, 1.0)
        for ring in _iter_rings(feat["geometry"]):
            patches.append(MplPolygon(ring, closed=True))
            colors.append(color)

    pc = PatchCollection(patches, facecolor=colors, edgecolor="#555555", linewidths=0.6)
    ax.add_collection(pc)

    type_colors = {
        "Supermarket": "#1f77b4",
        "Super Store": "#9467bd",
        "Large Grocery Store": "#17becf",
        "Medium Grocery Store": "#2ca02c",
        "Small Grocery Store": "#8c564b",
    }
    by_type = {}
    for s in stores:
        by_type.setdefault(s["type"], {"lon": [], "lat": []})
        by_type[s["type"]]["lon"].append(s["lon"])
        by_type[s["type"]]["lat"].append(s["lat"])

    for stype, pts in by_type.items():
        ax.scatter(
            pts["lon"],
            pts["lat"],
            s=28,
            color=type_colors.get(stype, "black"),
            edgecolor="white",
            linewidths=0.3,
            label=f"{stype} ({len(pts['lon'])})",
            zorder=3,
        )

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect(1.4)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        "Grocery Stores and Median Household Income by Zip Code\nKing County / Seattle Area, WA",
        fontsize=30,
        fontweight="bold",
        pad=24,
    )

    cbar = fig.colorbar(sm, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Median household income (US$)", fontsize=18)
    cbar.ax.tick_params(labelsize=14)

    legend = ax.legend(
        loc="lower left",
        fontsize=14,
        title="Grocery store type (currently SNAP-authorized)",
        title_fontsize=15,
        frameon=True,
        facecolor="white",
        framealpha=0.9,
    )
    legend.get_frame().set_edgecolor("#999999")

    ax.text(
        0.5,
        -0.02,
        "Sources: USDA SNAP Retailer Locator (via jshannon75/snap_retailers), "
        "US Census ACS via uszipcode-project, zip boundaries via OpenDataDE/State-zip-code-GeoJSON",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=11,
        color="#444444",
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, facecolor="white")
    print(f"Saved {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
