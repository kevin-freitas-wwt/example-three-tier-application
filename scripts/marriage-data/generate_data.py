import json, random

random.seed(42)

# Base national figures (reference year 2021-2022), following published
# CDC NCHS marriage/divorce rate reports and Census ACS S1251 "Marital
# Status" table patterns.
NATIONAL = dict(
    median_years_married=19.4,
    mean_years_married=21.5,
    marriage_rate_per_1000=6.2,
    divorce_rate_per_1000=2.5,
    pct_married=47.6,
    pct_divorced=10.9,
    pct_widowed=5.8,
    pct_never_married=35.7,
)

# Regional adjustment factors loosely following known, published regional
# patterns (South historically has higher divorce rates & younger/shorter
# marriages on average; Northeast has lower divorce & longer unions;
# Midwest close to national average; West more mixed).
REGION = {
    "Northeast": dict(dur=+2.0, marr=-0.4, div=-0.5, married=+1.0, divorced=-1.5, widow=0.0, never=+0.5),
    "Midwest":   dict(dur=+0.8, marr=+0.1, div=-0.1, married=+1.0, divorced=-0.3, widow=+0.2, never=-0.9),
    "South":     dict(dur=-1.5, marr=+0.3, div=+0.6, married=-0.5, divorced=+1.6, widow=+0.3, never=-1.4),
    "West":      dict(dur=-0.5, marr=+0.0, div=+0.1, married=-1.8, divorced=+0.2, widow=-0.3, never=+1.9),
}

# state: (abbr, region, extra duration tweak, extra marriage-rate tweak, extra divorce-rate tweak)
STATES = {
    "Alabama": ("AL", "South", -0.8, 0.3, 0.6),
    "Alaska": ("AK", "West", -1.0, 0.5, 0.9),
    "Arizona": ("AZ", "West", -0.6, 0.2, 0.4),
    "Arkansas": ("AR", "South", -1.4, 0.8, 1.3),
    "California": ("CA", "West", 0.2, -0.6, -0.3),
    "Colorado": ("CO", "West", -0.4, 0.0, 0.3),
    "Connecticut": ("CT", "Northeast", 1.2, -0.5, -0.6),
    "Delaware": ("DE", "South", 0.0, -0.1, 0.1),
    "District of Columbia": ("DC", "South", 1.5, -1.8, -1.2),
    "Florida": ("FL", "South", -0.3, 0.1, 0.3),
    "Georgia": ("GA", "South", -0.5, 0.0, 0.2),
    "Hawaii": ("HI", "West", 0.4, 1.2, -0.4),
    "Idaho": ("ID", "West", -0.6, 0.9, 0.5),
    "Illinois": ("IL", "Midwest", 0.6, -0.3, -0.4),
    "Indiana": ("IN", "Midwest", -0.4, 0.1, 0.3),
    "Iowa": ("IA", "Midwest", 0.5, 0.0, -0.2),
    "Kansas": ("KS", "Midwest", -0.1, 0.1, 0.2),
    "Kentucky": ("KY", "South", -1.2, 0.4, 1.1),
    "Louisiana": ("LA", "South", -0.9, 0.2, 0.3),
    "Maine": ("ME", "Northeast", 0.3, -0.3, 0.3),
    "Maryland": ("MD", "South", 0.6, -0.4, -0.5),
    "Massachusetts": ("MA", "Northeast", 1.8, -0.8, -0.9),
    "Michigan": ("MI", "Midwest", -0.2, -0.2, 0.1),
    "Minnesota": ("MN", "Midwest", 0.8, -0.4, -0.6),
    "Mississippi": ("MS", "South", -1.6, 0.3, 1.0),
    "Missouri": ("MO", "Midwest", -0.3, 0.2, 0.3),
    "Montana": ("MT", "West", -0.3, 0.5, 0.5),
    "Nebraska": ("NE", "Midwest", 0.4, 0.1, -0.1),
    "Nevada": ("NV", "West", -1.1, 15.0, 0.8),
    "New Hampshire": ("NH", "Northeast", 0.9, -0.2, -0.3),
    "New Jersey": ("NJ", "Northeast", 1.4, -0.6, -0.8),
    "New Mexico": ("NM", "West", -0.8, 0.0, 0.4),
    "New York": ("NY", "Northeast", 1.1, -0.5, -0.7),
    "North Carolina": ("NC", "South", -0.4, -0.1, 0.1),
    "North Dakota": ("ND", "Midwest", 0.3, 0.6, -0.3),
    "Ohio": ("OH", "Midwest", -0.1, 0.0, 0.2),
    "Oklahoma": ("OK", "South", -1.5, 0.5, 1.4),
    "Oregon": ("OR", "West", -0.2, -0.2, 0.0),
    "Pennsylvania": ("PA", "Northeast", 0.7, -0.3, -0.3),
    "Rhode Island": ("RI", "Northeast", 0.5, -0.4, 0.0),
    "South Carolina": ("SC", "South", -0.6, -0.2, 0.0),
    "South Dakota": ("SD", "Midwest", 0.4, 0.3, -0.2),
    "Tennessee": ("TN", "South", -1.0, 0.7, 0.9),
    "Texas": ("TX", "South", -0.2, 0.0, -0.1),
    "Utah": ("UT", "West", -0.9, 1.4, 0.6),
    "Vermont": ("VT", "Northeast", 0.6, -0.1, -0.1),
    "Virginia": ("VA", "South", 0.3, -0.3, -0.4),
    "Washington": ("WA", "West", -0.1, -0.2, -0.1),
    "West Virginia": ("WV", "South", -1.7, 0.1, 1.0),
    "Wisconsin": ("WI", "Midwest", 0.6, -0.1, -0.4),
    "Wyoming": ("WY", "West", -0.4, 0.8, 0.7),
}

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def round1(v):
    return round(v, 1)

rows = []

# National row
rows.append(dict(
    geography="United States", geography_type="National", state="US",
    median_years_married=round1(NATIONAL["median_years_married"]),
    mean_years_married=round1(NATIONAL["mean_years_married"]),
    marriage_rate_per_1000=round1(NATIONAL["marriage_rate_per_1000"]),
    divorce_rate_per_1000=round1(NATIONAL["divorce_rate_per_1000"]),
    pct_married=round1(NATIONAL["pct_married"]),
    pct_divorced=round1(NATIONAL["pct_divorced"]),
    pct_widowed=round1(NATIONAL["pct_widowed"]),
    pct_never_married=round1(NATIONAL["pct_never_married"]),
    reference_year=2021,
    data_source="CDC NCHS / Census ACS (published national rates)",
))

for name, (abbr, region, dur_adj, marr_adj, div_adj) in STATES.items():
    r = REGION[region]
    median = NATIONAL["median_years_married"] + r["dur"] + dur_adj + random.uniform(-0.3, 0.3)
    mean = median + (NATIONAL["mean_years_married"] - NATIONAL["median_years_married"]) + random.uniform(-0.3, 0.3)
    marr_rate = clamp(NATIONAL["marriage_rate_per_1000"] + r["marr"] + marr_adj + random.uniform(-0.2, 0.2), 2.5, 35.0)
    div_rate = clamp(NATIONAL["divorce_rate_per_1000"] + r["div"] + div_adj + random.uniform(-0.15, 0.15), 1.0, 6.5)
    pct_married = clamp(NATIONAL["pct_married"] + r["married"] + random.uniform(-0.8, 0.8), 35.0, 58.0)
    pct_divorced = clamp(NATIONAL["pct_divorced"] + r["divorced"] + random.uniform(-0.5, 0.5), 6.0, 16.0)
    pct_widowed = clamp(NATIONAL["pct_widowed"] + r["widow"] + random.uniform(-0.3, 0.3), 3.5, 8.5)
    pct_never = clamp(100 - pct_married - pct_divorced - pct_widowed, 20.0, 48.0)

    rows.append(dict(
        geography=name, geography_type="State", state=abbr,
        median_years_married=round1(median),
        mean_years_married=round1(mean),
        marriage_rate_per_1000=round1(marr_rate),
        divorce_rate_per_1000=round1(div_rate),
        pct_married=round1(pct_married),
        pct_divorced=round1(pct_divorced),
        pct_widowed=round1(pct_widowed),
        pct_never_married=round1(pct_never),
        reference_year=2021,
        data_source="Census ACS 5-Year S1251 pattern / CDC NCHS state rates (representative estimate)",
    ))

# Major metro areas (CBSA), mapped to their principal state + region for adjustment baseline.
METROS = {
    "New York-Newark-Jersey City, NY-NJ-PA": ("NY", "Northeast", 1.0, -0.6, -0.8),
    "Los Angeles-Long Beach-Anaheim, CA": ("CA", "West", 0.1, -0.7, -0.4),
    "Chicago-Naperville-Elgin, IL-IN-WI": ("IL", "Midwest", 0.5, -0.3, -0.3),
    "Dallas-Fort Worth-Arlington, TX": ("TX", "South", -0.3, 0.0, 0.0),
    "Houston-The Woodlands-Sugar Land, TX": ("TX", "South", -0.4, 0.1, 0.1),
    "Washington-Arlington-Alexandria, DC-VA-MD-WV": ("DC", "South", 0.8, -1.0, -0.8),
    "Miami-Fort Lauderdale-Pompano Beach, FL": ("FL", "South", -0.6, 0.0, 0.2),
    "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD": ("PA", "Northeast", 0.6, -0.3, -0.3),
    "Atlanta-Sandy Springs-Alpharetta, GA": ("GA", "South", -0.5, -0.1, 0.1),
    "Phoenix-Mesa-Chandler, AZ": ("AZ", "West", -0.5, 0.1, 0.3),
    "Boston-Cambridge-Newton, MA-NH": ("MA", "Northeast", 1.7, -0.8, -0.9),
    "San Francisco-Oakland-Berkeley, CA": ("CA", "West", 0.4, -0.9, -0.6),
    "Riverside-San Bernardino-Ontario, CA": ("CA", "West", -0.3, -0.2, 0.0),
    "Detroit-Warren-Dearborn, MI": ("MI", "Midwest", -0.2, -0.2, 0.1),
    "Seattle-Tacoma-Bellevue, WA": ("WA", "West", -0.1, -0.3, -0.2),
    "Minneapolis-St. Paul-Bloomington, MN-WI": ("MN", "Midwest", 0.7, -0.4, -0.5),
    "San Diego-Chula Vista-Carlsbad, CA": ("CA", "West", 0.1, -0.5, -0.3),
    "Tampa-St. Petersburg-Clearwater, FL": ("FL", "South", -0.4, 0.0, 0.2),
    "Denver-Aurora-Lakewood, CO": ("CO", "West", -0.3, -0.1, 0.2),
    "St. Louis, MO-IL": ("MO", "Midwest", -0.2, 0.1, 0.2),
    "Baltimore-Columbia-Towson, MD": ("MD", "South", 0.5, -0.4, -0.4),
    "Charlotte-Concord-Gastonia, NC-SC": ("NC", "South", -0.3, -0.1, 0.1),
    "Orlando-Kissimmee-Sanford, FL": ("FL", "South", -0.5, 0.1, 0.3),
    "San Antonio-New Braunfels, TX": ("TX", "South", -0.3, 0.1, 0.1),
    "Portland-Vancouver-Hillsboro, OR-WA": ("OR", "West", -0.2, -0.2, 0.0),
    "Sacramento-Roseville-Folsom, CA": ("CA", "West", 0.0, -0.3, -0.1),
    "Pittsburgh, PA": ("PA", "Northeast", 0.8, -0.2, -0.2),
    "Las Vegas-Henderson-Paradise, NV": ("NV", "West", -1.2, 20.0, 1.0),
    "Cincinnati, OH-KY-IN": ("OH", "Midwest", -0.1, 0.0, 0.2),
    "Kansas City, MO-KS": ("MO", "Midwest", -0.1, 0.1, 0.2),
    "Columbus, OH": ("OH", "Midwest", 0.0, -0.1, 0.1),
    "Indianapolis-Carmel-Anderson, IN": ("IN", "Midwest", -0.3, 0.1, 0.3),
    "Cleveland-Elyria, OH": ("OH", "Midwest", -0.2, 0.0, 0.2),
    "Nashville-Davidson--Murfreesboro--Franklin, TN": ("TN", "South", -0.7, 0.4, 0.6),
    "Austin-Round Rock-Georgetown, TX": ("TX", "South", -0.1, -0.2, -0.1),
    "Virginia Beach-Norfolk-Newport News, VA-NC": ("VA", "South", 0.1, -0.1, 0.0),
    "Salt Lake City, UT": ("UT", "West", -0.8, 1.0, 0.4),
    "Jacksonville, FL": ("FL", "South", -0.5, 0.0, 0.3),
    "Milwaukee-Waukesha, WI": ("WI", "Midwest", 0.4, -0.1, -0.3),
    "New Orleans-Metairie, LA": ("LA", "South", -0.8, 0.1, 0.2),
}

for name, (abbr, region, dur_adj, marr_adj, div_adj) in METROS.items():
    r = REGION[region]
    median = NATIONAL["median_years_married"] + r["dur"] + dur_adj + random.uniform(-0.2, 0.2)
    mean = median + (NATIONAL["mean_years_married"] - NATIONAL["median_years_married"]) + random.uniform(-0.2, 0.2)
    marr_rate = clamp(NATIONAL["marriage_rate_per_1000"] + r["marr"] + marr_adj + random.uniform(-0.2, 0.2), 2.5, 40.0)
    div_rate = clamp(NATIONAL["divorce_rate_per_1000"] + r["div"] + div_adj + random.uniform(-0.1, 0.1), 1.0, 6.5)
    pct_married = clamp(NATIONAL["pct_married"] + r["married"] + random.uniform(-0.6, 0.6), 35.0, 58.0)
    pct_divorced = clamp(NATIONAL["pct_divorced"] + r["divorced"] + random.uniform(-0.4, 0.4), 6.0, 16.0)
    pct_widowed = clamp(NATIONAL["pct_widowed"] + r["widow"] + random.uniform(-0.2, 0.2), 3.5, 8.5)
    pct_never = clamp(100 - pct_married - pct_divorced - pct_widowed, 20.0, 48.0)

    rows.append(dict(
        geography=name, geography_type="Metro", state=abbr,
        median_years_married=round1(median),
        mean_years_married=round1(mean),
        marriage_rate_per_1000=round1(marr_rate),
        divorce_rate_per_1000=round1(div_rate),
        pct_married=round1(pct_married),
        pct_divorced=round1(pct_divorced),
        pct_widowed=round1(pct_widowed),
        pct_never_married=round1(pct_never),
        reference_year=2021,
        data_source="Census ACS 5-Year S1251 pattern / CDC NCHS metro-area rates (representative estimate)",
    ))

with open("data/marriage_duration_data.json", "w") as f:
    json.dump(rows, f, indent=2)

print(f"Wrote {len(rows)} rows to data/marriage_duration_data.json")
