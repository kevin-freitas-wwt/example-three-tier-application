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
    (no end_date) stores in grocery-related categories are plotted:
    Supermarket, Super Store, Large/Medium/Small Grocery Store,
    Combination Grocery/Other.

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

GROCERY_STORE_TYPES = {
    "Supermarket",
    "Super Store",
    "Large Grocery Store",
    "Medium Grocery Store",
    "Small Grocery Store",
    "Combination Grocery/Other",
}

TARGET_COUNTY = "King County"
TARGET_STATE = "WA"


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
    stores = load_grocery_stores()

    king_zip_codes = set(income_by_zip.keys())

    # Also include King County zips that have no income figure, so the
    # boundary still draws (shown in grey) for visual continuity.
    all_king_zips_path = os.path.join(CACHE_DIR, "simple_db.sqlite")
    conn = sqlite3.connect(all_king_zips_path)
    all_king_zips = {
        row[0]
        for row in conn.execute(
            "SELECT zipcode FROM simple_zipcode WHERE county=? AND state=?",
            (TARGET_COUNTY, TARGET_STATE),
        )
    }
    conn.close()

    features = [
        feat
        for feat in geo["features"]
        if feat["properties"]["ZCTA5CE10"] in all_king_zips
    ]
    print(f"Zip boundaries matched: {len(features)}", file=sys.stderr)
    print(f"Grocery stores plotted: {len(stores)}", file=sys.stderr)

    incomes = [v for v in income_by_zip.values() if v]
    norm = Normalize(vmin=min(incomes), vmax=max(incomes))
    cmap = plt.get_cmap("YlGn")
    sm = ScalarMappable(norm=norm, cmap=cmap)

    fig_w, fig_h, dpi = 32, 18, 120  # 3840x2160 px
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor("white")

    def iter_rings(geometry):
        gtype = geometry["type"]
        coords = geometry["coordinates"]
        if gtype == "Polygon":
            yield coords[0]
        elif gtype == "MultiPolygon":
            for poly in coords:
                yield poly[0]

    patches = []
    colors = []
    for feat in features:
        zc = feat["properties"]["ZCTA5CE10"]
        income = income_by_zip.get(zc)
        color = sm.to_rgba(income) if income else (0.85, 0.85, 0.85, 1.0)
        for ring in iter_rings(feat["geometry"]):
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
        "Combination Grocery/Other": "#e377c2",
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

    ax.set_xlim(-122.55, -121.6)
    ax.set_ylim(47.1, 47.85)
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
