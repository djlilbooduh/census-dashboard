# 📖 Data Dictionary — US Census Dashboard

> Comprehensive schema reference for all data files in the [US Census Dashboard](https://djlilbooduh.github.io/census-dashboard/).
>  
> **Last updated:** May 11, 2026
>
> **Coverage:** All 50 states · 50 census files · 50 voting files · 50 arrest files · 50 map files

---

## File Types

| File Pattern | Count | Description |
|-------------|-------|-------------|
| `[state]_census.json` | 50 | City-level demographics from Census ACS |
| `[state]_voting.json` | 50 | County-level election results (2016–2024) |
| `[state]_arrests.json` | 50 | City-level FBI arrest data |
| `[state]_map.html` | 50 | Interactive Leaflet maps |
| `city_county_maps.json` | 1 | City→county lookup for all states |
| `census_dashboard.html` | 1 | Main dashboard application |

---

## 1. Census Data: `[state]_census.json`

**Source:** US Census Bureau, American Community Survey (ACS) 5-Year Estimates, 2023  
**Collection method:** Census API via per-state subagent pipeline  
**Coverage:** All incorporated places and CDPs with population ≥ 500

### Schema

```json
{
  "cities": {
    "<city_name>, <state>": {
      "state": "CA",
      "fips": "0606000",
      "year": "2023",
      "source": "US Census Bureau ACS 5-Year Estimates",
      "population": {
        "total": 1385051,
        "voting_age": 1125769,
        "voting_age_pct": 81.3
      },
      "race": [
        {
          "group": "White (non-Hispanic)",
          "count": 573281,
          "pct": 41.4,
          "color": "#4fc3f7"
        }
      ],
      "economics": {
        "median_household_income": 104321,
        "poverty_count": 29040,
        "poverty_pct": 2.1
      },
      "education": {
        "bachelors_or_higher": 487109,
        "bachelors_only": 281352,
        "masters": 132824,
        "professional": 35379,
        "doctorate": 37554
      }
    }
  }
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `cities` | object | Keyed by full census place name (e.g., "Anaheim city, California") |
| `state` | string | 2-letter state postal code |
| `fips` | string | 7-digit Census place FIPS code |
| `year` | string | Data year ("2023") |
| `population.total` | integer | Total population |
| `population.voting_age` | integer | Population age 18+ |
| `population.voting_age_pct` | float | VAP as percentage of total |
| `race[].group` | string | Race/ethnicity group name |
| `race[].count` | integer | Population in this group |
| `race[].pct` | float | Percentage of total population |
| `race[].color` | string | (Optional) Hex color for visualization |
| `economics.median_household_income` | integer | Median household income (inflation-adjusted USD) |
| `economics.poverty_count` | integer | Residents below poverty line |
| `economics.poverty_pct` | float | Poverty rate as percentage |
| `education.bachelors_or_higher` | integer | Population 25+ with bachelor's degree or higher |
| `education.bachelors_only` | integer | Bachelor's degree only |
| `education.masters` | integer | Master's degree |
| `education.professional` | integer | Professional degree (JD, MD, etc.) |
| `education.doctorate` | integer | Doctoral degree (PhD, EdD, etc.) |

### Notes
- `color` field present in CA; may be absent in other states
- IN uses a list-of-lists format (header row + data rows) instead of the standard dict
- City names always include place type suffix and state: "Anaheim **city**, California"
- FIPS codes are 7-digit Census place codes, not county codes

---

## 2. Voting Data: `[state]_voting.json`

**Source:** Multiple — MIT Election Data + Science Lab, state election boards, CNN exit polls  
**Coverage:** All counties/boroughs/parishes within each state  
**Elections:** 2016, 2020, 2024 presidential

### Schema (Standard Format)

Most states use this format with FIPS-keyed or name-keyed counties:

```json
{
  "counties": {
    "06073": {
      "name": "San Diego County",
      "presidential": {
        "2016": {
          "dem_votes": 735000,
          "dem_pct": 56.3,
          "gop_votes": 472000,
          "gop_pct": 36.1,
          "other_votes": 99000,
          "other_pct": 7.6,
          "total_votes": 1306000,
          "turnout_pct": 79.0
        },
        "2020": { "...": "..." },
        "2024": { "...": "..." }
      },
      "registration": {
        "total_registered": 1920000,
        "eligible_voters": 2400000,
        "dem_pct": 39.0,
        "gop_pct": 26.0,
        "npp_pct": 28.0,
        "other_pct": 7.0
      }
    }
  }
}
```

### Format Variants

| Variant | States | Structure |
|---------|--------|-----------|
| Standard (FIPS keys) | CA, TX, FL, NY, IL, PA, OH, MI, NC, GA + most | `counties["SSCCC"]` with `presidential.{year}` |
| Standard (name keys) | AL, AZ, CT, GA, HI, IA, ID, MA, MS, MT, ND, NE, NH, NM, NV, OK, OR, SD, TN, UT, VT, WA, WI, WV, WY | `counties["CountyName"]` with same structure |
| List format | ID, KY | `counties` or top-level is a list of county objects |
| `president_2024` | SC, MO, IN, AR, KS, LA, MN, CO | Single-year field instead of nested `presidential` object |
| `borough_results` | AK | Alaska uses boroughs; stored in `borough_results` list |
| Nested `presidential.counties` | MD, RI | County data nested under `presidential.counties` |
| State-level only | NJ, DE, ME | No county breakdown; statewide totals only |
| Registration race breakdown | SC, VA, NC | Additional `registration_by_race` and demographic fields |

### Presidential Result Fields

| Field | Type | Description |
|-------|------|-------------|
| `dem_pct` / `harris_pct` | float | Democratic candidate vote percentage |
| `gop_pct` / `trump_pct` | float | Republican candidate vote percentage |
| `other_pct` | float | Third-party/write-in percentage |
| `total_votes` | integer | Total ballots cast |
| `turnout_pct` | float | Voter turnout percentage |

### Registration Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_registered` | integer | Total registered voters |
| `eligible_voters` | integer | Voting-eligible population (when available) |
| `dem_pct` | float | Registered Democrats (%) |
| `gop_pct` | float | Registered Republicans (%) |
| `npp_pct` | float | No Party Preference / Independent (%) |
| `other_pct` | float | Other party registration (%) |

### Notes
- Texas does not have party registration; `npp_pct` ≈ 100% with a note
- Some states use `harris_pct`/`trump_pct` instead of `dem_pct`/`gop_pct`
- AK, HI, and some others may have fewer than 3 election years available
- County keys may be uppercase, lowercase, or mixed case depending on source

---

## 3. Arrest Data: `[state]_arrests.json`

**Source:** FBI Crime Data Explorer (CDE) API, 2022 data  
**Collection method:** Per-agency API calls via `fetch_arrests.py`  
**API base:** `https://cde.ucr.cjis.gov/LATEST/arrest/agency/{ORI}/all`

### Schema (Current Format — most states)

```json
{
  "cities": {
    "Chicago city, Illinois": {
      "ori": "ILCPD0000",
      "city": "Chicago city, Illinois",
      "total_arrests": 14597,
      "year": "2022",
      "sex": {
        "Male": 11882,
        "Female": 2715
      },
      "race": {
        "White": 4428,
        "Black or African American": 9947,
        "Asian": 163,
        "American Indian or Alaska Native": 9,
        "Unknown": 50
      },
      "offenses": {
        "Simple Assault": 5957,
        "All Other Offenses": 3794,
        "Larceny": 1531,
        "Aggravated Assault": 806,
        "Drug Possession": 451
      },
      "offense_categories": {
        "Simple Assault": 5957,
        "All Other Offenses": 3794,
        "Larceny": 1531
      }
    }
  },
  "metadata": {
    "state": "IL",
    "year": "2022",
    "source": "FBI CDE API",
    "matched_cities": 440,
    "total_cities": 1294,
    "no_match": 151
  }
}
```

### Schema (Legacy Format — CA, TX)

```json
{
  "Anaheim city, California": {
    "ori": "CA0361300",
    "total_arrests": 3123,
    "arrest_rate_per_1k": 9.1,
    "population": 344553,
    "arrests_by_race": {
      "White": 1561,
      "Black or African American": 892,
      "Hispanic or Latino": 512
    },
    "offense_categories": {
      "Violent Crime": 445,
      "Property Crime": 1230,
      "Drug Abuse Violations": 678
    },
    "arrests_by_sex": {
      "Male": 2340,
      "Female": 783
    },
    "source": "FBI CDE Arrest API 2023"
  }
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `cities` | object | Keyed by full census place name |
| `ori` | string | FBI Originating Agency Identifier (9 chars) |
| `total_arrests` | integer | Total arrests in data year |
| `year` | string | Data year ("2022" or "2023") |
| `sex.Male` | integer | Male arrestees |
| `sex.Female` | integer | Female arrestees |
| `race` | object | Arrest counts by race category |
| `offenses` | object | Arrest counts by specific offense name |
| `offense_categories` | object | Arrest counts by offense category |
| `metadata` | object | Summary statistics for the entire state |

### Notes
- **Two formats exist**: The flat format (CA, TX) stores cities directly at top level; newer states use `cities` wrapper with `metadata`
- Cities with `"total_arrests": 0` and `"note": "no_agency_match"` could not be matched to any law enforcement agency
- Cities with `"note": "skipped_small_population"` were skipped due to population < 500
- Some cities share the same ORI (e.g., all Honolulu CDPs match to Honolulu PD)
- 2022 data was used because 2023 FBI CDE data was incomplete during collection (May 2026)

---

## 4. Maps: `[state]_map.html`

**Type:** Self-contained HTML files  
**Size range:** 17–245 KB per state  
**Library:** Leaflet 1.9.4 with CartoDB dark tiles

### Embedded Data

Each map contains a `CITIES` JavaScript array with these fields per city:

```javascript
{
  "name": "Los Angeles, CA",
  "lat": 33.94,
  "lng": -118.41,
  "population": 3821000,
  "income": 76577,
  "county": "Los Angeles",
  "lean": "D",
  "dem_pct_2024": 68.5,
  "gop_pct_2024": 30.2,
  "county_fips": "06037"
}
```

### Features
- Circle markers sized by population, colored by political lean
- City search with real-time filtering
- Population, income, and political lean range filters
- Click popups with census stats + county vote bars + link to main dashboard

---

## 5. City-County Map: `city_county_maps.json`

**Size:** ~791 KB  
**Generated from:** State map HTML files (extracted CITIES arrays)  
**Coverage:** All 50 states

```json
{
  "CA": {
    "Los Angeles, CA": {
      "county": "Los Angeles",
      "county_fips": "06037"
    },
    "San Diego, CA": {
      "county": "San Diego",
      "county_fips": "06073"
    }
  }
}
```

Used by the Voting tab to match selected cities to their county's election results.

---

## 6. Dashboard: `census_dashboard.html`

**Size:** ~36 KB (self-contained, no build step)  
**Dependencies:** None (Leaflet only in maps, not dashboard)

### Architecture
- Single HTML file with embedded CSS and JavaScript
- Loads per-state JSON files on state selection
- Three tabs: Census Demographics, Crime & Safety, Voting
- City search with autocomplete dropdown
- CSV export for any selected city

### Data Flow
1. User selects state → `loadStateData()` fetches `{state}_census.json`, `{state}_voting.json`
2. Crime tab → `loadCrimeData()` fetches `{state}_arrests.json` on first access
3. Voting tab → uses `city_county_maps.json` (preloaded) to match city→county

---

## Data Quality Notes

| Aspect | Detail |
|--------|--------|
| **Census coverage** | 100% for all 50 states (ACS 2023 5-year) |
| **Voting coverage** | County-level for ~45 states; state-level only for NJ, DE, ME |
| **Arrest coverage** | 50–90% city match rate per state; varies by local law enforcement structure |
| **Arrest year** | 2022 (most complete year in FBI CDE at time of collection) |
| **City-county matching** | County centroid proximity (average ~10 mi accuracy) |
| **Known gaps** | HI (county-level policing), independent cities (St. Louis, Baltimore, VA cities) |
| **API reliability** | FBI CDE API experienced a sustained outage during initial collection; recoverable via `fetch_arrests.py` |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `fetch_arrests.py` | Pull FBI arrest data for one state via CDE API |
| `generate_maps.py` | Build interactive Leaflet map for one state |
| `build_dashboard.py` | Regenerate `census_dashboard.html` (Python build script) |

---

*For development history and commit log, see the [ky-memory repo](https://github.com/djlilbooduh/ky-memory).*
