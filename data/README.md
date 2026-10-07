# Marriage Duration Data (`data/marriage_duration_data.json`)

`docs/marriage_duration_by_geography.html` renders a sortable, searchable
table of US marriage-duration statistics (median/mean years married,
marriage and divorce rates, percent currently married/divorced/widowed)
from `data/marriage_duration_data.json`.

## Granularity and sourcing

ZIP-code-level "how long do married couples stay together" data is not
published as a free, bulk, nationwide dataset. The Census Bureau's American
Community Survey publishes marital-status / "years married" tables only
down to the county or Public Use Microdata Area (PUMA) level, and the live
Census and CDC/NCHS APIs were not reachable from the sandbox used to build
this page (only GitHub, npm, and PyPI endpoints are reachable there). A
GitHub-wide search also did not turn up any mirrored ZIP-level
marriage-duration dataset (the closest real dataset found,
`fivethirtyeight/data/marriage`, reports never-married/divorced shares by
broad Census region, not duration, and was not granular enough to use here).

So this dataset reports the most granular tier available — state and
metro area / county, with a representative ZIP range for that area — and
the figures are representative estimates that follow published CDC NCHS
and Census ACS state/metro reporting patterns (reference year 2021), not a
verbatim download of one official table. Treat the numbers as illustrative
starting points, not authoritative statistics. For authoritative data,
consult:

- CDC/NCHS National Vital Statistics System — https://www.cdc.gov/nchs/nvss/marriage-divorce.htm
- Census Bureau / data.census.gov ACS Table S1251 (Marital Status) — https://data.census.gov

## Fields

Each record has: `region`, `state`, `metro_area`, `county`, `zip_range`,
`median_years_married`, `mean_years_married`, `marriages_per_1000`,
`divorces_per_1000`, `pct_currently_married`, `pct_ever_divorced`,
`pct_widowed`, `year`, `data_source`.
