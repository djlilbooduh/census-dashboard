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

---

## Git History

This repo was created as a clean migration of census dashboard files from two source repos:

- **`djlilbooduh/ky-memory`** — Contains the full development history including all census pipeline commits, subagent runs, and build iterations
- **`djlilbooduh/ufo-dashboard`** — Original deployment repo (now cleaned to UFO content only)

Key historical commits from ky-memory:
- `bd0dc31` — Fixed voting-age population from Census B01001 API (467 CA cities)
- `a5c86ef` — Added crime tab with FBI UCR arrest data for 450 CA cities  
- `a2301bc` — Phase 4: generated 49 state interactive Leaflet maps
- `f8f7da8` — Phase 3: 11 states processed overnight before FBI API outage

For full commit history and development narrative, see the [ky-memory repo](https://github.com/djlilbooduh/ky-memory).
