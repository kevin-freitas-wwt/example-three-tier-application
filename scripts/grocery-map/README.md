# Seattle-area grocery store / income map

`generate_map.py` builds a single 4K (3840x2160) PNG that shows:

- Every currently SNAP-authorized grocery store in King County, WA
  (supermarkets, super stores, and large/medium/small grocery stores), plotted
  as points colored by store type. USDA's "Combination Grocery/Other"
  category (pharmacies, dollar stores, and other small retailers that sell
  some food) is intentionally excluded, since those aren't grocery stores.
- A choropleth of median household income by zip code (ZCTA) across King
  County, from US Census ACS data.

## Data sources

- Zip code boundaries: [OpenDataDE/State-zip-code-GeoJSON](https://github.com/OpenDataDE/State-zip-code-GeoJSON)
- Median household income by zip: the `simple_db.sqlite` extract bundled by
  [uszipcode-project](https://github.com/MacHu-GWU/uszipcode-project)
- Grocery retailer locations: the USDA SNAP historical retailer dataset
  maintained at [jshannon75/snap_retailers](https://github.com/jshannon75/snap_retailers)

All three are public datasets fetched over HTTPS. Downloaded files are cached
under `cache/` (gitignored) so re-running the script doesn't re-download them.

The map's axis limits are computed automatically from the actual extent of
the zip boundaries and store points (plus a small margin), so nothing is cut
off at the edge of the picture.

## Usage

```bash
pip install matplotlib
python3 generate_map.py ../../docs/seattle_grocery_stores_income_map.png
```

The output image at `docs/seattle_grocery_stores_income_map.png` was generated
with this script.
