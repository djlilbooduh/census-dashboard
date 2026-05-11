#!/usr/bin/env python3
"""Generate interactive Leaflet maps for all 50 states from census/voting data.
Handles multiple voting data formats (FIPS-keyed, name-keyed, list, etc.)."""
import json, sys, os, re, math

WORKSPACE = '/home/lilbooduh/.openclaw/workspace'

def load_json(path):
    with open(path) as f:
        return json.load(f)

def parse_county_gazetteer(path):
    counties = {}
    with open(path) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 10: continue
            geoid = parts[1]
            name = parts[3].replace(' County', '').replace(' Parish', '').replace(' Borough', '').replace(' Census Area', '').replace(' City and Borough', '').replace(' Municipality', '')
            try: lat, lng = float(parts[8]), float(parts[9])
            except ValueError: continue
            counties[geoid] = {'name': name, 'lat': lat, 'lng': lng}
    return counties

def parse_place_gazetteer(path, target_state):
    places = {}
    with open(path) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 12 or parts[0].upper() != target_state.upper(): continue
            try: lat, lng = float(parts[10]), float(parts[11])
            except ValueError: continue
            places[parts[1]] = {'name': parts[3], 'lat': round(lat, 6), 'lng': round(lng, 6)}
    return places

def haversine(lat1, lng1, lat2, lng2):
    R = 3959
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def find_county(city_lat, city_lng, state_counties):
    best = (None, None, float('inf'))
    for fips, c in state_counties.items():
        d = haversine(city_lat, city_lng, c['lat'], c['lng'])
        if d < best[2]: best = (fips, c['name'], d)
    return best if best[0] else None

def classify_lean(dem_pct, gop_pct):
    m = dem_pct - gop_pct
    if m >= 15: return 'D'
    if m >= 5: return 'lean-D'
    if m > -5: return 'swing'
    if m > -15: return 'lean-R'
    return 'R'

# ── Voting data normalization ──

def normalize_voting(voting_json):
    """Convert any voting JSON format into {county_key: {dem_pct, gop_pct}}."""
    out = {}
    
    # Case 1: dict with 'counties' key
    if isinstance(voting_json, dict) and 'counties' in voting_json:
        counties = voting_json['counties']
        if isinstance(counties, dict):
            for ckey, cdata in counties.items():
                if isinstance(cdata, dict):
                    dp, gp = extract_pcts(cdata)
                    if dp is not None:
                        out[ckey] = (dp, gp)
        elif isinstance(counties, list):
            for cdata in counties:
                if isinstance(cdata, dict):
                    ckey = cdata.get('name', cdata.get('county', ''))
                    dp, gp = extract_pcts(cdata)
                    if dp is not None and ckey:
                        out[ckey] = (dp, gp)
    
    # Case 2: list at top level (KY)
    elif isinstance(voting_json, list):
        for entry in voting_json:
            if isinstance(entry, dict):
                ckey = entry.get('county', entry.get('name', ''))
                dp, gp = extract_pcts(entry)
                if dp is not None and ckey:
                    out[ckey] = (dp, gp)
    
    # Case 3: dict with 'borough_results' (AK)
    if not out and isinstance(voting_json, dict) and 'borough_results' in voting_json:
        for entry in voting_json['borough_results']:
            if isinstance(entry, dict):
                ckey = entry.get('name', entry.get('borough', entry.get('county', '')))
                dp, gp = extract_pcts(entry)
                if dp is not None and ckey:
                    out[ckey] = (dp, gp)
    
    # Case 4: dict with 'presidential' at top level (MD, NJ, RI, etc.)
    if not out and isinstance(voting_json, dict):
        for key in ['presidential', 'county_results', 'results', 'counties']:
            val = voting_json.get(key)
            if isinstance(val, dict):
                for ckey, cdata in val.items():
                    if isinstance(cdata, dict):
                        dp, gp = extract_pcts(cdata)
                        if dp is not None:
                            out[ckey] = (dp, gp)
            elif isinstance(val, list):
                for cdata in val:
                    if isinstance(cdata, dict):
                        ckey = cdata.get('name', cdata.get('county', ''))
                        dp, gp = extract_pcts(cdata)
                        if dp is not None and ckey:
                            out[ckey] = (dp, gp)
    
    return out

def extract_pcts(data):
    """Extract (dem_pct, gop_pct) from a county record using multiple format attempts."""
    # Try 'presidential' with year subkeys (TX, FL style)
    pres = data.get('presidential', {})
    if isinstance(pres, dict):
        for yr in ['2024', '2020', '2016']:
            yrdata = pres.get(yr, {})
            if yrdata:
                dp = yrdata.get('dem_pct') or yrdata.get('democrat_pct')
                gp = yrdata.get('gop_pct') or yrdata.get('republican_pct')
                if dp is not None and gp is not None:
                    return (dp, gp)
    
    # Try 'results' with year subkeys (GA style)
    results = data.get('results', {})
    if isinstance(results, dict):
        for yr in ['2024', '2020', '2016']:
            yrdata = results.get(yr, {})
            if yrdata:
                dp = yrdata.get('democrat_pct') or yrdata.get('dem_pct')
                gp = yrdata.get('republican_pct') or yrdata.get('gop_pct')
                if dp is not None and gp is not None:
                    return (dp, gp)
    
    # Try 'president_2024' or 'presidential_2024' (AZ, NM, KY style)
    for pres_key in ['president_2024', 'presidential_2024', 'presidential']:
        pdata = data.get(pres_key, {})
        if isinstance(pdata, dict):
            # Check for harris/trump sub-objects
            harris = pdata.get('harris', {})
            trump = pdata.get('trump', {})
            if isinstance(harris, dict) and isinstance(trump, dict):
                hp = harris.get('pct')
                tp = trump.get('pct')
                if hp is not None and tp is not None:
                    return (hp, tp)
            # Check for flat keys
            dp = pdata.get('dem_pct') or pdata.get('harris_pct') or pdata.get('democrat_pct')
            gp = pdata.get('gop_pct') or pdata.get('trump_pct') or pdata.get('republican_pct')
            if dp is not None and gp is not None:
                return (dp, gp)
    
    # Try direct keys (KY style: data has 'dem_pct' and 'gop_pct' at top)
    dp = data.get('dem_pct') or data.get('harris_pct') or data.get('democrat_pct')
    gp = data.get('gop_pct') or data.get('trump_pct') or data.get('republican_pct')
    if dp is not None and gp is not None:
        return (dp, gp)
    
    return (None, None)

# ── City building ──

STATE_FIPS_MAP = {
    'AL':'01','AK':'02','AZ':'04','AR':'05','CA':'06','CO':'08','CT':'09',
    'DE':'10','DC':'11','FL':'12','GA':'13','HI':'15','ID':'16','IL':'17',
    'IN':'18','IA':'19','KS':'20','KY':'21','LA':'22','ME':'23','MD':'24',
    'MA':'25','MI':'26','MN':'27','MS':'28','MO':'29','MT':'30','NE':'31',
    'NV':'32','NH':'33','NJ':'34','NM':'35','NY':'36','NC':'37','ND':'38',
    'OH':'39','OK':'40','OR':'41','PA':'42','RI':'44','SC':'45','SD':'46',
    'TN':'47','TX':'48','UT':'49','VT':'50','VA':'51','WA':'53','WV':'54',
    'WI':'55','WY':'56'
}

def normalize_census(census_json):
    """Convert census data to standard {city_name: {fips, population, income}} dict."""
    cities = {}
    
    # Standard dict format: {'cities': {...}}
    if isinstance(census_json, dict) and 'cities' in census_json:
        return census_json['cities']
    
    # List of lists format (IN): [header, row1, row2, ...]
    if isinstance(census_json, list) and len(census_json) > 1:
        header = [h.lower() for h in census_json[0]] if isinstance(census_json[0], list) else []
        # Find column indices
        try:
            name_idx = header.index('name')
        except ValueError:
            # Try common name column patterns
            name_idx = 0  # NAME is usually first
        
        # Find population column (B01003_001E)
        pop_idx = None
        for i, h in enumerate(header):
            if 'b01003' in h or 'population' in h or 'total_pop' in h:
                pop_idx = i
                break
        
        # Find income column (B19013_001E)
        income_idx = None
        for i, h in enumerate(header):
            if 'b19013' in h or 'median_income' in h or 'income' in h:
                income_idx = i
                break
        
        for row in census_json[1:]:
            if not isinstance(row, list) or len(row) < max(name_idx, pop_idx or 0, income_idx or 0) + 1:
                continue
            name = str(row[name_idx]) if name_idx < len(row) else ''
            pop = int(float(row[pop_idx])) if pop_idx is not None and pop_idx < len(row) and row[pop_idx] not in ('-666666666', '', None) else 0
            income = int(float(row[income_idx])) if income_idx is not None and income_idx < len(row) and row[income_idx] not in ('-666666666', '', None) else 0
            if name:
                # Generate a pseudo-fips from name hash (won't match gazetteer but we can try)
                cities[name] = {
                    'fips': '',  # List format doesn't have FIPS, match by name
                    'population': {'total': pop},
                    'economics': {'median_household_income': income}
                }
        return cities
    
    return {}

def build_cities(state_code, census_json, voting_json, places, all_counties):
    cities = []
    state_fips = STATE_FIPS_MAP.get(state_code.upper(), '')
    state_counties = {k: v for k, v in all_counties.items() if k.startswith(state_fips)}
    
    # Normalize voting and census data
    norm_voting = normalize_voting(voting_json)
    has_voting = len(norm_voting) > 0
    norm_census = normalize_census(census_json)
    
    total = len(norm_census)
    matched = no_coords = no_voting = 0
    county_distances = {}
    
    for city_name, city_data in norm_census.items():
        fips = city_data.get('fips', '') if isinstance(city_data, dict) else ''
        pop = city_data.get('population', {}).get('total', 0) if isinstance(city_data, dict) else 0
        income = city_data.get('economics', {}).get('median_household_income', 0) if isinstance(city_data, dict) else 0
        
        # Look up coordinates
        place = places.get(fips) if fips else None
        if not place:
            # Try name-based matching for list-format census (no FIPS)
            city_base = re.sub(r',\s*\w+$', '', city_name).strip().lower()
            for geoid, pdata in places.items():
                pname = pdata.get('name', '').lower() if isinstance(pdata, dict) else ''
                if pname and (city_base in pname or pname in city_base):
                    place = pdata
                    fips = geoid
                    break
        if not place:
            no_coords += 1
            continue
        
        # Find county
        cr = find_county(place['lat'], place['lng'], state_counties)
        if not cr: continue
        county_fips, county_name, distance = cr
        county_distances[county_fips] = distance
        
        # Look up voting data - try FIPS first, then name
        dem_pct, gop_pct = 50, 50
        lean = 'swing'
        
        vote = norm_voting.get(county_fips)
        if vote is None:
            vote = norm_voting.get(county_name)
            if vote is None:
                # Try with/without 'County' suffix
                vote = norm_voting.get(f"{county_name} County")
        
        if vote:
            dem_pct, gop_pct = vote
            lean = classify_lean(dem_pct, gop_pct)
        elif has_voting:
            no_voting += 1
        
        short_name = re.sub(r'\s+(city|town|CDP|village|borough|municipality),\s+\w+$', '', city_name)
        
        cities.append({
            'name': f"{short_name}, {state_code.upper()}",
            'lat': place['lat'], 'lng': place['lng'],
            'population': pop, 'income': income,
            'county': county_name, 'lean': lean,
            'dem_pct_2024': round(dem_pct, 1),
            'gop_pct_2024': round(gop_pct, 1),
            'county_fips': county_fips
        })
        matched += 1
    
    if county_distances:
        avg_d = sum(county_distances.values()) / len(county_distances)
        max_d = max(county_distances.values())
        print(f"  County: {len(county_distances)} matched, avg={avg_d:.1f}mi, max={max_d:.1f}mi")
    print(f"  Cities: {matched}/{total} (no_coords={no_coords}, no_voting={no_voting})")
    
    return sorted(cities, key=lambda c: c['population'], reverse=True)

# ── HTML generation ──

def generate_html(state_code, state_name, cities):
    cities_json = json.dumps(cities, separators=(',', ':'))
    n = len(cities)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>📍 US Census — {state_name} City Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
:root {{--bg:#0a0a10;--sf:#141420;--bd:#1e1e3a;--tx:#e0e0f0;--mu:#8888aa;--ac:#4fc3f7;--sc:#ff5252;--cf:#ffab40;--uc:#66bb6a;--pl:#ce93d8}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;width:100%;overflow:hidden}}
body{{font-family:-apple-system,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--tx);display:flex;flex-direction:column}}
#topbar{{background:linear-gradient(135deg,#0d1b2a,#1b2838,#0d1b2a);border-bottom:1px solid #1a1a3a;padding:0.6rem 1.5rem;display:flex;align-items:center;justify-content:space-between;z-index:1000;flex-shrink:0}}
#topbar h1{{font-size:1.2rem;color:var(--ac);display:flex;align-items:center;gap:0.4rem}}
#topbar .nav-link{{color:var(--mu);text-decoration:none;font-size:0.78rem;padding:0.35rem 0.9rem;border:1px solid var(--bd);border-radius:5px;transition:all 0.15s;background:var(--sf)}}
#topbar .nav-link:hover{{color:var(--ac);border-color:var(--ac);background:rgba(79,195,247,0.08)}}
#map{{flex:1;width:100%;background:var(--bg)}}
#legend{{position:absolute;bottom:28px;right:12px;background:rgba(10,10,16,0.92);border:1px solid var(--bd);border-radius:10px;padding:12px 16px;z-index:900;font-size:0.72rem;backdrop-filter:blur(8px)}}
#legend h3{{color:var(--ac);font-size:0.72rem;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px}}
.legend-row{{display:flex;align-items:center;gap:8px;margin-bottom:4px}}
.legend-dot{{width:12px;height:12px;border-radius:50%;flex-shrink:0}}
.legend-label{{color:var(--mu)}}
#info-panel{{position:absolute;bottom:28px;left:12px;background:rgba(10,10,16,0.92);border:1px solid var(--bd);border-radius:10px;padding:10px 14px;z-index:900;font-size:0.7rem;color:var(--mu);backdrop-filter:blur(8px)}}
.leaflet-popup-content-wrapper{{background:rgba(20,20,32,0.96)!important;border:1px solid var(--bd)!important;border-radius:10px!important;color:var(--tx)!important;backdrop-filter:blur(10px)}}
.leaflet-popup-content{{margin:0;min-width:220px}}
.leaflet-popup-tip{{background:rgba(20,20,32,0.96)!important}}
.popup-card{{padding:10px 0}}
.popup-header{{font-size:0.95rem;font-weight:700;color:var(--ac);margin-bottom:2px;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.08)}}
.popup-stat{{display:flex;justify-content:space-between;align-items:center;gap:14px;font-size:0.74rem;padding:3px 0}}
.popup-stat-label{{color:var(--mu);font-size:0.7rem}}
.popup-stat-val{{font-weight:600;font-family:'SF Mono','Cascadia Code',monospace}}
.popup-vote-bar{{margin-top:6px}}
.popup-vote-labels{{display:flex;justify-content:space-between;font-size:0.66rem;margin-bottom:3px}}
.popup-vote-labels .dem-label{{color:#4fc3f7}}
.popup-vote-labels .gop-label{{color:#ff5252}}
.popup-bar-track{{height:6px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden;display:flex;margin-bottom:2px}}
.popup-bar-dem{{background:#4fc3f7;height:100%;border-radius:3px 0 0 3px}}
.popup-bar-gop{{background:#ff5252;height:100%;border-radius:0 3px 3px 0}}
.popup-lean{{text-align:right;font-size:0.7rem;font-weight:700;margin-top:4px;font-family:'SF Mono','Cascadia Code',monospace}}
.popup-lean.lean-D{{color:#4fc3f7}}.popup-lean.lean-R{{color:#ff5252}}
.popup-lean.lean-lean-D{{color:#81d4fa}}.popup-lean.lean-lean-R{{color:#ff8a80}}
.popup-link-btn{{display:block;text-align:center;margin-top:8px;padding:6px 10px;background:rgba(79,195,247,0.12);border:1px solid rgba(79,195,247,0.3);border-radius:6px;color:var(--ac);text-decoration:none;font-size:0.72rem;font-weight:600;transition:all 0.15s}}
.popup-link-btn:hover{{background:rgba(79,195,247,0.22);border-color:var(--ac);color:#fff}}
#map-search{{background:var(--sf);border:1px solid var(--bd);color:var(--tx);padding:0.3rem 0.7rem;border-radius:5px;font-size:0.72rem;outline:none;width:160px;transition:border-color 0.15s}}
#map-search:focus{{border-color:var(--ac)}}
#map-search::placeholder{{color:var(--mu)}}
#map-search-clear{{background:none;border:none;color:var(--mu);cursor:pointer;font-size:0.85rem;padding:0 2px 0 6px;display:none}}
#map-search-clear.visible{{display:inline}}
#map-search-clear:hover{{color:var(--sc)}}
#filter-toggle{{position:absolute;top:12px;right:12px;z-index:950;background:rgba(10,10,16,0.92);border:1px solid var(--bd);border-radius:8px;color:var(--ac);padding:0.45rem 0.85rem;font-size:0.72rem;font-family:inherit;cursor:pointer;backdrop-filter:blur(8px);transition:all 0.15s;display:flex;align-items:center;gap:6px;font-weight:600}}
#filter-toggle:hover{{background:rgba(20,20,40,0.95);border-color:var(--ac)}}
#filter-toggle .arrow{{transition:transform 0.2s;font-size:0.6rem}}
#filter-panel{{position:absolute;top:52px;right:12px;z-index:940;background:rgba(10,10,16,0.94);border:1px solid var(--bd);border-radius:10px;padding:14px 18px;backdrop-filter:blur(10px);font-size:0.7rem;color:var(--tx);width:270px;transition:all 0.25s ease;overflow:hidden}}
#filter-panel.collapsed{{opacity:0;pointer-events:none;transform:translateX(20px);max-height:0;padding-top:0;padding-bottom:0;margin:0;border-width:0}}
#filter-panel h3{{font-size:0.72rem;color:var(--ac);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center}}
.filter-group{{margin-bottom:12px}}
.filter-group:last-of-type{{margin-bottom:10px}}
.filter-label{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}}
.filter-label .name{{font-weight:600;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.3px;color:var(--mu)}}
.filter-label .range-val{{font-family:'SF Mono','Cascadia Code',monospace;font-size:0.68rem;color:var(--ac);font-weight:600}}
.dual-range{{position:relative;height:24px;margin:2px 0}}
.dual-range .track-bg{{position:absolute;top:10px;left:0;right:0;height:4px;background:rgba(255,255,255,0.08);border-radius:2px}}
.dual-range .track-active{{position:absolute;top:10px;height:4px;background:var(--ac);border-radius:2px}}
.dual-range input[type=range]{{position:absolute;top:0;width:100%;height:24px;-webkit-appearance:none;background:transparent;pointer-events:none;margin:0}}
.dual-range input[type=range]::-webkit-slider-thumb{{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;background:var(--ac);border:2px solid var(--sf);cursor:pointer;pointer-events:auto;box-shadow:0 0 6px rgba(79,195,247,0.4)}}
.filter-btn{{display:block;width:100%;margin-top:8px;padding:6px;background:rgba(79,195,247,0.15);border:1px solid var(--bd);border-radius:5px;color:var(--mu);font-size:0.68rem;cursor:pointer;transition:all 0.15s}}
.filter-btn:hover{{color:var(--ac);border-color:var(--ac)}}
</style>
</head>
<body>
<div id="topbar">
<h1>📍 {state_name}</h1>
<div style="display:flex;align-items:center;gap:10px">
<input type="text" id="map-search" placeholder="🔍 Search cities..."/>
<button id="map-search-clear">✕</button>
<a class="nav-link" href="census_dashboard.html">📊 Census Dashboard</a>
</div>
</div>
<div id="map"></div>
<div id="legend">
<h3>Political Lean</h3>
<div class="legend-row"><div class="legend-dot" style="background:#4fc3f7"></div><span class="legend-label">Democrat</span></div>
<div class="legend-row"><div class="legend-dot" style="background:#81d4fa"></div><span class="legend-label">Lean Dem</span></div>
<div class="legend-row"><div class="legend-dot" style="background:#ce93d8"></div><span class="legend-label">Swing</span></div>
<div class="legend-row"><div class="legend-dot" style="background:#ff8a80"></div><span class="legend-label">Lean GOP</span></div>
<div class="legend-row"><div class="legend-dot" style="background:#ff5252"></div><span class="legend-label">Republican</span></div>
</div>
<div id="info-panel">
<span id="city-count">{n} cities</span>
<span style="margin:0 6px;opacity:0.3">|</span>
<span id="visible-count">{n} visible</span>
</div>
<button id="filter-toggle">⚙ Filters <span class="arrow">▼</span></button>
<div id="filter-panel" class="collapsed">
<h3>Filters <span id="filter-reset" style="cursor:pointer;font-size:0.65rem;color:var(--mu)">Reset</span></h3>
<div class="filter-group">
<div class="filter-label"><span class="name">Population</span><span class="range-val" id="pop-range-label">All</span></div>
<div class="dual-range">
<div class="track-bg"></div><div class="track-active" id="pop-track"></div>
<input type="range" id="pop-min" min="0" max="100" value="0" step="1">
<input type="range" id="pop-max" min="0" max="100" value="100" step="1">
</div></div>
<div class="filter-group">
<div class="filter-label"><span class="name">Income</span><span class="range-val" id="income-range-label">All</span></div>
<div class="dual-range">
<div class="track-bg"></div><div class="track-active" id="income-track"></div>
<input type="range" id="income-min" min="0" max="100" value="0" step="1">
<input type="range" id="income-max" min="0" max="100" value="100" step="1">
</div></div>
<div class="filter-group">
<div class="filter-label"><span class="name">Lean (D+ / R+)</span><span class="range-val" id="lean-range-label">All</span></div>
<div class="dual-range">
<div class="track-bg"></div><div class="track-active" id="lean-track"></div>
<input type="range" id="lean-min" min="-100" max="100" value="-100" step="1">
<input type="range" id="lean-max" min="-100" max="100" value="100" step="1">
</div></div>
<button class="filter-btn" id="filter-reset-btn">↺ Reset All Filters</button>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const CITIES={cities_json};
const map=L.map('map',{{center:[39.8,-98.5],zoom:5,zoomControl:false,attributionControl:false}});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{maxZoom:18,attribution:'&copy;<a href="https://carto.com/">CartoDB</a>'}}).addTo(map);
L.control.zoom({{position:'bottomleft'}}).addTo(map);
function leanColor(l){{return l==='D'?'#4fc3f7':l==='lean-D'?'#81d4fa':l==='swing'?'#ce93d8':l==='lean-R'?'#ff8a80':l==='R'?'#ff5252':'#888'}}
function popRadius(p){{const m=CITIES.length>0?CITIES[0].population:2300000;return 3+12*Math.sqrt(p/Math.max(m,1))}}
const markers=[];
CITIES.forEach(c=>{{const color=leanColor(c.lean);const radius=popRadius(c.population);
const m=L.circleMarker([c.lat,c.lng],{{radius,fillColor:color,color:'rgba(255,255,255,0.15)',weight:1,fillOpacity:0.85}}).addTo(map);
m._cityData=c;
const cityEnc=encodeURIComponent(c.name);
const demPct=c.dem_pct_2024||50,gopPct=c.gop_pct_2024||50;
const margin=demPct-gopPct;
const leanVal=margin>0?'D+'+margin.toFixed(1):'R+'+Math.abs(margin).toFixed(1);
const lcc=c.lean==='D'?'lean-D':c.lean==='R'?'lean-R':c.lean==='lean-D'?'lean-lean-D':c.lean==='lean-R'?'lean-lean-R':'';
const tv=demPct+gopPct,dbw=tv>0?(demPct/tv)*100:50,gbw=tv>0?(gopPct/tv)*100:50;
m.bindPopup(`<div class="popup-card"><div class="popup-header">${{c.name}}</div>
<div class="popup-stat"><span class="popup-stat-label">Population</span><span class="popup-stat-val">${{c.population.toLocaleString()}}</span></div>
<div class="popup-stat"><span class="popup-stat-label">Median Income</span><span class="popup-stat-val">$${{c.income.toLocaleString()}}</span></div>
<div class="popup-stat"><span class="popup-stat-label">County</span><span class="popup-stat-val">${{c.county}}</span></div>
<div class="popup-vote-bar"><div class="popup-vote-labels"><span class="dem-label">🟦 Dem ${{demPct.toFixed(1)}}%</span><span class="gop-label">🟥 GOP ${{gopPct.toFixed(1)}}%</span></div>
<div class="popup-bar-track"><div class="popup-bar-dem" style="width:${{dbw}}%"></div><div class="popup-bar-gop" style="width:${{gbw}}%"></div></div></div>
<div class="popup-lean ${{lcc}}">${{leanVal}} • ${{c.lean.replace('lean-','lean ')}}</div>
<a class="popup-link-btn" href="census_dashboard.html?city=${{cityEnc}}" target="_blank">📊 View Full Report →</a></div>`,{{maxWidth:280,className:'dark-popup'}});
markers.push(m);}});
function updateInfo(){{const t=markers.length,v=markers.filter(m=>!m._filtered).length;document.getElementById('city-count').textContent=t+' cities';document.getElementById('visible-count').textContent=v+' visible'}}
updateInfo();
const fs={{sq:'',pMin:0,pMax:Infinity,iMin:0,iMax:Infinity,lMin:-100,lMax:100}};
function applyFilters(){{markers.forEach(m=>{{const c=m._cityData;const nm=!fs.sq||c.name.toLowerCase().includes(fs.sq);const pm=c.population>=fs.pMin&&c.population<=fs.pMax;const im=c.income>=fs.iMin&&c.income<=fs.iMax;const mg=(c.dem_pct_2024||50)-(c.gop_pct_2024||50);const lm=mg>=fs.lMin&&mg<=fs.lMax;if(nm&&pm&&im&&lm){{if(m._filtered){{m.addTo(map);m._filtered=false}}}}else{{if(!m._filtered){{m.remove();m._filtered=true}}}}}});updateInfo()}}
const si=document.getElementById('map-search'),sc=document.getElementById('map-search-clear');
si.addEventListener('input',()=>{{fs.sq=si.value.toLowerCase().trim();sc.classList.toggle('visible',fs.sq.length>0);applyFilters()}});
sc.addEventListener('click',()=>{{si.value='';fs.sq='';sc.classList.remove('visible');applyFilters();si.focus()}});
const ft=document.getElementById('filter-toggle'),fp=document.getElementById('filter-panel'),fa=ft.querySelector('.arrow');
ft.addEventListener('click',()=>{{const s=fp.classList.toggle('collapsed');fa.textContent=s?'▼':'▲'}});
const pmin=document.getElementById('pop-min'),pmax=document.getElementById('pop-max'),plab=document.getElementById('pop-range-label'),ptrack=document.getElementById('pop-track');
function upf(){{let mn=parseInt(pmin.value),mx=parseInt(pmax.value);if(mn>mx){{const t=mn;mn=mx;mx=t}};const mp=mn===0?0:Math.round(Math.pow(10,2+(mn/100)*5));const xp=mx===100?Infinity:Math.round(Math.pow(10,2+(mx/100)*5));fs.pMin=mp;fs.pMax=xp;plab.textContent=mp===0&&xp===Infinity?'All':mp.toLocaleString()+' - '+(xp===Infinity?'∞':xp.toLocaleString());ptrack.style.left=mn+'%';ptrack.style.right=(100-mx)+'%';applyFilters()}}
[pmin,pmax].forEach(e=>e.addEventListener('input',upf));upf();
const imin=document.getElementById('income-min'),imax=document.getElementById('income-max'),ilab=document.getElementById('income-range-label'),itrack=document.getElementById('income-track');
function uif(){{let mn=parseInt(imin.value),mx=parseInt(imax.value);if(mn>mx){{const t=mn;mn=mx;mx=t}};const mi=Math.round((mn/100)*250000);const xi=mx===100?Infinity:Math.round((mx/100)*250000);fs.iMin=mi;fs.iMax=xi;ilab.textContent=mi===0&&xi===Infinity?'All':'$'+mi.toLocaleString()+' - '+(xi===Infinity?'∞':'$'+xi.toLocaleString());itrack.style.left=mn+'%';itrack.style.right=(100-mx)+'%';applyFilters()}}
[imin,imax].forEach(e=>e.addEventListener('input',uif));uif();
const lmin=document.getElementById('lean-min'),lmax=document.getElementById('lean-max'),llab=document.getElementById('lean-range-label'),ltrack=document.getElementById('lean-track');
function ulf(){{let mn=parseInt(lmin.value),mx=parseInt(lmax.value);if(mn>mx){{const t=mn;mn=mx;mx=t}};fs.lMin=mn;fs.lMax=mx;llab.textContent=(mn<=-100&&mx>=100)?'All':(mn>=0?'D+'+mn:'R+'+Math.abs(mn))+' to '+(mx>=0?'D+'+mx:'R+'+Math.abs(mx));ltrack.style.left=((mn+100)/200*100)+'%';ltrack.style.right=(100-(mx+100)/200*100)+'%';applyFilters()}}
[lmin,lmax].forEach(e=>e.addEventListener('input',ulf));ulf();
function rf(){{fs.sq='';si.value='';sc.classList.remove('visible');pmin.value=0;pmax.value=100;upf();imin.value=0;imax.value=100;uif();lmin.value=-100;lmax.value=100;ulf()}}
document.getElementById('filter-reset').addEventListener('click',rf);
document.getElementById('filter-reset-btn').addEventListener('click',rf);
</script>
</body>
</html>'''

STATE_NAMES = {
    'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California',
    'CO':'Colorado','CT':'Connecticut','DE':'Delaware','DC':'District of Columbia',
    'FL':'Florida','GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois',
    'IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana',
    'ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota',
    'MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada',
    'NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York',
    'NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma',
    'OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina',
    'SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont',
    'VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming'
}

def generate_state_map(state_code, all_counties):
    state_name = STATE_NAMES.get(state_code.upper(), state_code)
    sc = state_code.lower()
    
    census_path = os.path.join(WORKSPACE, f'{sc}_census.json')
    voting_path = os.path.join(WORKSPACE, f'{sc}_voting.json')
    place_gaz_path = os.path.join(WORKSPACE, '2023_Gaz_place_national.txt')
    output_path = os.path.join(WORKSPACE, f'{sc}_map.html')
    
    if not os.path.exists(census_path):
        print(f"  ❌ No census data")
        return False
    if not os.path.exists(voting_path):
        print(f"  ❌ No voting data")
        return False
    
    census = load_json(census_path)
    voting = load_json(voting_path)
    places = parse_place_gazetteer(place_gaz_path, state_code)
    
    cities = build_cities(state_code, census, voting, places, all_counties)
    if not cities:
        print(f"  ❌ No cities matched")
        return False
    
    html = generate_html(state_code, state_name, cities)
    with open(output_path, 'w') as f:
        f.write(html)
    
    size_kb = os.path.getsize(output_path) / 1024
    print(f"  ✅ {len(cities)} cities, {size_kb:.0f}KB")
    return True

def main():
    county_gaz_path = os.path.join(WORKSPACE, 'county_gazetteer.txt')
    print("Loading county gazetteer...")
    all_counties = parse_county_gazetteer(county_gaz_path)
    print(f"  {len(all_counties)} counties loaded\n")
    
    # Only generate states that have both census and voting data
    state_codes = []
    for st in sorted(STATE_NAMES.keys()):
        sc = st.lower()
        if os.path.exists(os.path.join(WORKSPACE, f'{sc}_census.json')) and \
           os.path.exists(os.path.join(WORKSPACE, f'{sc}_voting.json')):
            state_codes.append(st)
    
    # Skip existing maps unless they're from old broken runs
    to_generate = []
    for st in state_codes:
        p = os.path.join(WORKSPACE, f'{st.lower()}_map.html')
        if not os.path.exists(p):
            to_generate.append(st)
    
    if len(sys.argv) > 1:
        to_generate = [st for st in sys.argv[1:] if st.upper() in STATE_NAMES]
    
    print(f"Generating {len(to_generate)} maps\n")
    
    success = 0
    for i, st in enumerate(to_generate):
        print(f"[{i+1}/{len(to_generate)}] {st}:")
        if generate_state_map(st, all_counties):
            success += 1
    
    print(f"\nDone: {success}/{len(to_generate)}")

if __name__ == '__main__':
    main()
