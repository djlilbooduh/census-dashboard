#!/usr/bin/env python3
"""Fetch multi-year FBI arrest data (2020-2023) for a state and output combined format."""
import json, urllib.request, urllib.error, time, sys, os, re

WORKSPACE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '/home/lilbooduh/.openclaw/workspace'
CDE_BASE = 'https://cde.ucr.cjis.gov/LATEST'
YEARS = ['2020', '2021', '2022', '2023']
BATCH_DELAY = 0.35

def fetch_json(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (503, 429):
                time.sleep(delay * (attempt + 2))
                continue
            return None
        except Exception:
            time.sleep(delay)
    return None

def parse_arrest(data, year):
    if not data: return None
    r = {'total_arrests': 0, 'sex': data.get('Arrestee Sex', {}),
         'race': data.get('Arrestee Race', {}), 'offenses': {},
         'offense_categories': {}, 'year': year}
    sex = data.get('Arrestee Sex', {})
    if sex: r['total_arrests'] = sum(sex.values())
    offenses = data.get('Offense Name', {})
    if offenses:
        r['offenses'] = {k: v for k, v in sorted(offenses.items(), key=lambda x: -x[1]) if v > 0}
    cats = data.get('Offense Category', {})
    if cats:
        r['offense_categories'] = {k: v for k, v in sorted(cats.items(), key=lambda x: -x[1]) if v > 0}
    return r

def fetch_arrest(ori, year):
    url = f"{CDE_BASE}/arrest/agency/{ori}/all?from=01-{year}&to=12-{year}&type=totals"
    return fetch_json(url, retries=2, delay=2)

def match_city(city_full_name, city_agencies, county_agencies, county_name=None):
    """Match a census city to a CDE agency ORI (same logic as fetch_arrests.py)."""
    # Check manual overrides
    MANUAL_ORIS_TOP = {
        "Chicago city, Illinois": "ILCPD0000", "New York city, New York": "NY0303000",
        "Los Angeles city, California": "CA0194200", "Houston city, Texas": "TX1012100",
        "Philadelphia city, Pennsylvania": "PA0511800", "Phoenix city, Arizona": "AZ0072300",
        "San Diego city, California": "CA0371100", "Dallas city, Texas": "TX0571300",
        "San Jose city, California": "CA0430900", "Austin city, Texas": "TX2270100",
    }
    if city_full_name in MANUAL_ORIS_TOP:
        return MANUAL_ORIS_TOP[city_full_name]
    
    city_clean = re.sub(r'\s+(city|town|CDP|village|borough|municipality),\s*\w+$', '', city_full_name, flags=re.IGNORECASE)
    city_words = city_clean.lower().split()
    if not city_words: return None
    
    best_score, best_ori = 0, None
    for ag in city_agencies:
        ag_clean = re.sub(r'\s+(Police Department|Police Dept|Dept of Public Safety)$', '', ag.get('agency_name', ''), flags=re.IGNORECASE)
        ag_words = ag_clean.lower().split()
        score = sum(1 for w in city_words if w in ag_words) / len(city_words) if city_words else 0
        if city_words and ag_words and city_words[0] == ag_words[0]: score += 0.5
        if score > best_score: best_score, best_ori = score, ag.get('ori')
    if best_score >= 0.5: return best_ori
    
    if county_name:
        cl = county_name.lower()
        for ag in county_agencies:
            if cl in ag.get('agency_name', '').lower(): return ag.get('ori')
        for ag in city_agencies:
            if cl in ag.get('agency_name', '').lower(): return ag.get('ori')
    return None

def main():
    state_code = sys.argv[1]
    sc = state_code.lower()
    output_path = os.path.join(WORKSPACE, f'{sc}_arrests_multi.json')
    census_path = os.path.join(WORKSPACE, f'{sc}_census.json')
    
    # Check if existing single-year data is available (use as base for ORIs)
    existing_path = os.path.join(WORKSPACE, f'{sc}_arrests.json')
    
    with open(census_path) as f:
        census = json.load(f)
    cities = census.get('cities', {})
    
    print(f"📊 {state_code}: {len(cities)} cities × {len(YEARS)} years")
    
    # Get agencies
    url = f"{CDE_BASE}/agency/byStateAbbr/{state_code.upper()}"
    data = fetch_json(url, retries=5, delay=4)
    if not data:
        print("  ❌ Failed to fetch agencies"); return
    
    city_ag = [ag for ag_list in data.values() for ag in ag_list if ag.get('agency_type_name') == 'City']
    county_ag = [ag for ag_list in data.values() for ag in ag_list if ag.get('agency_type_name') == 'County']
    print(f"  {len(city_ag)} city agencies, {len(county_ag)} county agencies")
    
    # Load city_county_maps for county fallback
    ccm_path = os.path.join(WORKSPACE, 'city_county_maps.json')
    ccm = {}
    if os.path.exists(ccm_path):
        with open(ccm_path) as f: ccm = json.load(f)
    
    results = {}
    matched = 0
    no_match = 0
    city_items = list(cities.items())
    
    for i, (city_name, city_data) in enumerate(city_items):
        pop = city_data.get('population', {}).get('total', 0)
        if pop < 500:
            results[city_name] = {'years': {}, 'note': 'skipped_small'}
            continue
        
        # Get county name
        short = re.sub(r'\s+(city|town|CDP|village|borough|municipality),\s*\w+$', '', city_name) + ', ' + state_code
        info = ccm.get(state_code, {}).get(short, ccm.get(state_code, {}).get(city_name, {}))
        county_name = info.get('county', None) if info else None
        
        ori = match_city(city_name, city_ag, county_ag, county_name)
        if not ori:
            results[city_name] = {'years': {}, 'note': 'no_agency_match'}
            no_match += 1
            continue
        
        city_years = {'ori': ori, 'years': {}}
        
        for year in YEARS:
            arrest_data = fetch_arrest(ori, year)
            time.sleep(BATCH_DELAY)
            if arrest_data:
                city_years['years'][year] = parse_arrest(arrest_data, year)
        
        results[city_name] = city_years
        matched += 1
        
        if (i + 1) % 50 == 0:
            pct = (i+1)/len(city_items)*100
            print(f"  [{i+1}/{len(city_items)} {pct:.0f}%] matched={matched} no_match={no_match}")
            # Save checkpoint
            with open(output_path + '.tmp', 'w') as f:
                json.dump({'cities': results, 'metadata': {'state': state_code, 'years': YEARS, 'matched': matched, 'total': len(city_items)}}, f)
    
    output = {
        'cities': results,
        'metadata': {'state': state_code, 'years': YEARS, 'source': 'FBI CDE API',
                     'matched_cities': matched, 'total_cities': len(city_items), 'no_match': no_match}
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f)
    
    print(f"  ✅ {matched} matched, {no_match} no match → {output_path}")
    try: os.remove(output_path + '.tmp')
    except: pass

if __name__ == '__main__':
    main()
