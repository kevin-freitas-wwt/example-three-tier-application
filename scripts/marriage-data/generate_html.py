#!/usr/bin/env python3
"""Generate docs/marriage_duration_by_geography.html from
data/marriage_duration_data.json. The page embeds the data directly so it
is a single self-contained file that works when opened locally (no fetch/
CORS issues) as well as when served from GitHub Pages or similar.
"""
import json

with open("data/marriage_duration_data.json") as f:
    DATA = json.load(f)

COLUMNS = [
    ("geography", "Geography", "text"),
    ("geography_type", "Type", "text"),
    ("state", "State", "text"),
    ("median_years_married", "Median Yrs Married", "num"),
    ("mean_years_married", "Mean Yrs Married", "num"),
    ("marriage_rate_per_1000", "Marriage Rate /1000", "num"),
    ("divorce_rate_per_1000", "Divorce Rate /1000", "num"),
    ("pct_married", "% Married", "num"),
    ("pct_divorced", "% Divorced", "num"),
    ("pct_widowed", "% Widowed", "num"),
    ("pct_never_married", "% Never Married", "num"),
    ("reference_year", "Ref. Year", "num"),
    ("data_source", "Data Source", "text"),
]

data_json = json.dumps(DATA)
columns_json = json.dumps(COLUMNS)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>US Marriage Duration by Geography</title>
<style>
  :root {{
    --bg: #0f172a;
    --panel: #1e293b;
    --border: #334155;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --row-alt: #16213a;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 24px;
  }}
  h1 {{
    margin: 0 0 4px 0;
    font-size: 1.6rem;
  }}
  p.subtitle {{
    margin: 0 0 20px 0;
    color: var(--muted);
    max-width: 900px;
    line-height: 1.5;
  }}
  .controls {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
    align-items: center;
  }}
  #search {{
    flex: 1;
    min-width: 220px;
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--panel);
    color: var(--text);
    font-size: 1rem;
  }}
  #search:focus {{ outline: 2px solid var(--accent); }}
  select {{
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--panel);
    color: var(--text);
    font-size: 0.95rem;
  }}
  .count {{
    color: var(--muted);
    font-size: 0.9rem;
    white-space: nowrap;
  }}
  .table-wrap {{
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 10px;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    min-width: 1100px;
    font-size: 0.92rem;
  }}
  thead th {{
    position: sticky;
    top: 0;
    background: #111c33;
    color: var(--text);
    text-align: left;
    padding: 10px 12px;
    border-bottom: 2px solid var(--border);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
  }}
  thead th:hover {{ background: #16213a; }}
  thead th .arrow {{
    display: inline-block;
    width: 1em;
    color: var(--accent);
  }}
  tbody td {{
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }}
  tbody tr:nth-child(even) {{ background: var(--row-alt); }}
  tbody tr:hover {{ background: #22304f; }}
  td.data-source {{
    white-space: normal;
    min-width: 260px;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  footer {{
    margin-top: 20px;
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.5;
    max-width: 900px;
  }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }}
  .badge.National {{ background: #7c3aed; color: #fff; }}
  .badge.State {{ background: #0ea5e9; color: #082f49; }}
  .badge.Metro {{ background: #f59e0b; color: #451a03; }}
</style>
</head>
<body>

<h1>US Marriage Duration by Geography</h1>
<p class="subtitle">
  Median/mean years married, marriage &amp; divorce rates, and marital-status
  breakdown for the United States, each state (plus DC), and the largest US
  metro areas. Click a column header to sort; use the search box or type
  filter to narrow the list.
  <strong>Note:</strong> no free, bulk, reachable dataset publishes marriage
  duration down to ZIP code (Census ACS only tabulates it to county/PUMA,
  and the Census/CDC APIs are not reachable from this environment), so the
  figures below are representative estimates that follow published
  CDC NCHS / Census ACS regional patterns for reference year 2021, not a
  verbatim table download. See <code>data/README.md</code> for details.
</p>

<div class="controls">
  <input id="search" type="text" placeholder="Search geography, state, source..." autocomplete="off">
  <select id="typeFilter">
    <option value="">All types</option>
    <option value="National">National</option>
    <option value="State">State</option>
    <option value="Metro">Metro</option>
  </select>
  <span class="count" id="count"></span>
</div>

<div class="table-wrap">
  <table id="dataTable">
    <thead>
      <tr id="headerRow"></tr>
    </thead>
    <tbody id="tableBody"></tbody>
  </table>
</div>

<footer>
  Reference year 2021. Source basis: CDC NCHS marriage/divorce rate reporting
  and Census ACS 5-Year Estimates, table S1251 "Marital Status" (regional
  patterns). Dataset: <code>data/marriage_duration_data.json</code>
  (92 rows: 1 national + 51 states/DC + 40 metro areas). Regenerate with
  <code>scripts/marriage-data/generate_data.py</code> and
  <code>scripts/marriage-data/generate_html.py</code>.
</footer>

<script>
const COLUMNS = {columns_json};
const DATA = {data_json};

let sortKey = "geography";
let sortDir = 1;

const headerRow = document.getElementById("headerRow");
const tableBody = document.getElementById("tableBody");
const searchInput = document.getElementById("search");
const typeFilter = document.getElementById("typeFilter");
const countEl = document.getElementById("count");

function buildHeader() {{
  headerRow.innerHTML = "";
  COLUMNS.forEach(([key, label]) => {{
    const th = document.createElement("th");
    th.dataset.key = key;
    th.innerHTML = `${{label}} <span class="arrow"></span>`;
    th.addEventListener("click", () => {{
      if (sortKey === key) {{
        sortDir *= -1;
      }} else {{
        sortKey = key;
        sortDir = 1;
      }}
      render();
    }});
    headerRow.appendChild(th);
  }});
}}

function updateArrows() {{
  headerRow.querySelectorAll("th").forEach(th => {{
    const arrow = th.querySelector(".arrow");
    if (th.dataset.key === sortKey) {{
      arrow.textContent = sortDir === 1 ? "\\u25B2" : "\\u25BC";
    }} else {{
      arrow.textContent = "";
    }}
  }});
}}

function matchesSearch(row, term) {{
  if (!term) return true;
  const haystack = Object.values(row).join(" ").toLowerCase();
  return haystack.includes(term);
}}

function render() {{
  const term = searchInput.value.trim().toLowerCase();
  const typeVal = typeFilter.value;

  let rows = DATA.filter(r => matchesSearch(r, term) && (!typeVal || r.geography_type === typeVal));

  const colType = COLUMNS.find(c => c[0] === sortKey)[2];
  rows.sort((a, b) => {{
    let av = a[sortKey];
    let bv = b[sortKey];
    if (colType === "num") {{
      return (av - bv) * sortDir;
    }}
    av = String(av).toLowerCase();
    bv = String(bv).toLowerCase();
    if (av < bv) return -1 * sortDir;
    if (av > bv) return 1 * sortDir;
    return 0;
  }});

  tableBody.innerHTML = "";
  rows.forEach(row => {{
    const tr = document.createElement("tr");
    COLUMNS.forEach(([key]) => {{
      const td = document.createElement("td");
      if (key === "geography_type") {{
        td.innerHTML = `<span class="badge ${{row[key]}}">${{row[key]}}</span>`;
      }} else if (key === "data_source") {{
        td.textContent = row[key];
        td.classList.add("data-source");
      }} else {{
        td.textContent = row[key];
      }}
      tr.appendChild(td);
    }});
    tableBody.appendChild(tr);
  }});

  countEl.textContent = `${{rows.length}} of ${{DATA.length}} rows`;
  updateArrows();
}}

buildHeader();
searchInput.addEventListener("input", render);
typeFilter.addEventListener("change", render);
render();
</script>

</body>
</html>
"""

with open("docs/marriage_duration_by_geography.html", "w") as f:
    f.write(html)

print(f"Wrote docs/marriage_duration_by_geography.html ({len(html)} bytes) with {len(DATA)} rows")
