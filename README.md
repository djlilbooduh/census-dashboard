# US Census Dashboard

Interactive dashboard for US Census, voting, and FBI arrest data across all 50 states.

**Live:** https://djlilbooduh.github.io/Census-Dashboard/

## Data Files

- `[state]_census.json` — Census ACS demographics per city (50 states)
- `[state]_voting.json` — County-level presidential election results (50 states)
- `[state]_arrests.json` — FBI CDE arrest data per city (50 states)
- `[state]_map.html` — Interactive Leaflet map per state (49 states)

## Scripts

- `generate_maps.py` — Build interactive maps from census/voting data
- `fetch_arrests.py` — Pull FBI arrest data via CDE API
