# Seattle-area grocery store / income map

`generate_map.py` builds a single 4K (3840x2160) PNG that shows:

- Every currently SNAP-authorized grocery-type retailer in King County, WA
  (supermarkets, super stores, and large/medium/small grocery stores), plotted
  as points colored by store type.
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

## Usage

```bash
pip install matplotlib
python3 generate_map.py ../../docs/seattle_grocery_stores_income_map.png
```

The output image at `docs/seattle_grocery_stores_income_map.png` was generated
with this script.
