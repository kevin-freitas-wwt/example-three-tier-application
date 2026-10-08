# Marriage Duration Data

`marriage_duration_data.json` is a dataset of US marriage-duration and
marital-status statistics by geography, used by
`docs/marriage_duration_by_geography.html`.

## Granularity

ZIP-code-level marriage duration is **not available** from any free, bulk,
reachable dataset (see "Data sources" below), so this dataset covers:

- 1 National row
- 51 State rows (50 states + District of Columbia)
- 40 Metro-area (CBSA) rows for the largest US metropolitan areas

92 rows total.

## Fields

| Field | Description |
|---|---|
| `geography` | Name of the geographic area |
| `geography_type` | `National`, `State`, or `Metro` |
| `state` | Two-letter state/territory abbreviation (principal state for metro areas) |
| `median_years_married` | Median years married, currently-married population |
| `mean_years_married` | Mean years married, currently-married population |
| `marriage_rate_per_1000` | Marriages per 1,000 population per year |
| `divorce_rate_per_1000` | Divorces per 1,000 population per year |
| `pct_married` | % of population currently married |
| `pct_divorced` | % of population currently divorced |
| `pct_widowed` | % of population currently widowed |
| `pct_never_married` | % of population never married |
| `reference_year` | Reference year for the estimate |
| `data_source` | Origin / basis of the figure |

## Data sources and limitations

- No free, bulk, nationwide dataset publishes marriage duration ("years
  married") down to ZIP code. Census ACS only tabulates marital-status
  "years married" down to county / PUMA level in open tables, and even
  those tables are not reachable from this sandbox (`api.census.gov` and
  `www.cdc.gov` / NCHS are not reachable here — only GitHub, npm, and PyPI
  endpoints are allowed).
- A GitHub-wide search for a mirrored marriage-duration dataset found
  nothing county/ZIP-level. The closest real, reachable dataset is
  `fivethirtyeight/data/marriage` (`both_sexes.csv`, `divorce.csv`, etc.),
  which has genuine Census/ACS/IPUMS-derived never-married/divorced shares
  by broad Census region through ~2012, but it does not report marriage
  *duration* and isn't granular below region, so it wasn't used as the
  final source here.
- Because no verifiable bulk/API source was reachable, the National, State,
  and Metro rows in this file are **representative estimates** that follow
  known, published CDC NCHS marriage/divorce-rate and Census ACS S1251
  "Marital Status" reporting patterns (reference year 2021), not a verbatim
  table download. For example, Northeastern states skew toward longer
  median marriage duration and lower divorce rates, Southern states skew
  shorter/higher-divorce, and Nevada's marriage rate is inflated by
  wedding-tourism as in real published data.
- Regenerate with `scripts/marriage-data/generate_data.py`. Keep this
  disclaimer if the file is regenerated or extended, until a verified
  official dataset becomes reachable.
