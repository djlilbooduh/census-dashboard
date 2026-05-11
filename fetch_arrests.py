#!/usr/bin/env python3
"""Phase 3: Pull FBI arrest data for a state via CDE API (2022 data).
Fetches agency ORIs, matches to census cities by name, pulls arrest totals + race + offense data."""
import json, urllib.request, urllib.error, time, sys, os, re

WORKSPACE = '/home/lilbooduh/.openclaw/workspace'
CDE_BASE = 'https://cde.ucr.cjis.gov/LATEST'
YEAR = '2022'
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

def fetch_agencies(state_code):
    url = f"{CDE_BASE}/agency/byStateAbbr/{state_code.upper()}"
    data = fetch_json(url, retries=5, delay=4)
    if not data:
        return [], []
    
    city_agencies = []
    county_agencies = []
    for county_name, ag_list in data.items():
        if isinstance(ag_list, list):
            for ag in ag_list:
                if not isinstance(ag, dict):
                    continue
                if ag.get('agency_type_name') == 'City':
                    city_agencies.append(ag)
                elif ag.get('agency_type_name') == 'County':
                    county_agencies.append(ag)
    
    return city_agencies, county_agencies

def match_city(city_full_name, city_agencies, county_agencies):
    """Match a census city to a CDE agency ORI."""
    city_clean = re.sub(r'\s+(city|town|CDP|village|borough|municipality),\s*\w+$', '', city_full_name, flags=re.IGNORECASE)
    city_words = city_clean.lower().split()
    if not city_words:
        return None
    
    # Try city agencies first (word overlap scoring)
    best_score = 0
    best_ori = None
    for ag in city_agencies:
        ag_name = ag.get('agency_name', '')
        ag_clean = re.sub(r'\s+(Police Department|Police Dept|Dept of Public Safety)$', '', ag_name, flags=re.IGNORECASE)
        ag_words = ag_clean.lower().split()
        
        matches = sum(1 for w in city_words if w in ag_words)
        score = matches / len(city_words) if city_words else 0
        if city_words and ag_words and city_words[0] == ag_words[0]:
            score += 0.5
        
        if score > best_score:
            best_score = score
            best_ori = ag.get('ori')
    
    if best_score >= 0.5:
        return best_ori
    
    # Fallback: use county sheriff (will be matched by county name in calling code)
    return None

def fetch_arrest(ori):
    url = f"{CDE_BASE}/arrest/agency/{ori}/all?from=01-{YEAR}&to=12-{YEAR}&type=totals"
    return fetch_json(url, retries=2, delay=2)

def parse_arrest(data):
    if not data:
        return None
    r = {
        'total_arrests': 0,
        'sex': data.get('Arrestee Sex', {}),
        'race': data.get('Arrestee Race', {}),
        'offenses': {},
        'offense_categories': {},
        'year': YEAR
    }
    sex = data.get('Arrestee Sex', {})
    if sex:
        r['total_arrests'] = sum(sex.values())
    
    offenses = data.get('Offense Name', {})
    if offenses:
        r['offenses'] = {k: v for k, v in sorted(offenses.items(), key=lambda x: -x[1]) if v > 0}
    
    cats = data.get('Offense Category', {})
    if cats:
        r['offense_categories'] = {k: v for k, v in sorted(cats.items(), key=lambda x: -x[1]) if v > 0}
    
    return r

def main():
    state_code = sys.argv[1]
    sc = state_code.lower()
    output_path = os.path.join(WORKSPACE, f'{sc}_arrests.json')
    checkpoint_path = os.path.join(WORKSPACE, f'{sc}_arrests_checkpoint.json')
    census_path = os.path.join(WORKSPACE, f'{sc}_census.json')
    
    if not os.path.exists(census_path):
        print(f"❌ No census data for {state_code}")
        return
    
    with open(census_path) as f:
        census = json.load(f)
    
    cities = census.get('cities', {})
    if not cities:
        print(f"❌ No cities")
        return
    
    print(f"🔍 {state_code}: {len(cities)} cities")
    
    # Load checkpoint
    cp = {}
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path) as f:
            cp = json.load(f)
    
    results = cp.get('cities', {})
    
    # Fetch agencies
    city_agencies, county_agencies = fetch_agencies(state_code)
    if not city_agencies and not county_agencies:
        print(f"  ❌ No agencies found")
        return
    
    print(f"  {len(city_agencies)} city agencies, {len(county_agencies)} county agencies")
    
    matched = no_match = api_errors = skipped = 0
    city_items = list(cities.items())
    
    for i, (city_name, city_data) in enumerate(city_items):
        pop = city_data.get('population', {}).get('total', 0)
        
        # Skip tiny places (<500 pop) to save API calls
        if pop < 500:
            results[city_name] = {'ori': None, 'total_arrests': 0, 'note': 'skipped_small_population'}
            skipped += 1
            continue
        
        # Skip if already in results
        if city_name in results and results[city_name].get('total_arrests', 0) > 0:
            skipped += 1
            continue
        
        # Match to agency
        ori = match_city(city_name, city_agencies, county_agencies)
        if not ori:
            results[city_name] = {'ori': None, 'total_arrests': 0, 'note': 'no_agency_match'}
            no_match += 1
            continue
        
        # Fetch arrest data
        data = fetch_arrest(ori)
        time.sleep(BATCH_DELAY)
        
        if not data:
            results[city_name] = {'ori': ori, 'total_arrests': 0, 'note': 'api_error'}
            api_errors += 1
        else:
            parsed = parse_arrest(data)
            parsed['ori'] = ori
            parsed['city'] = city_name
            results[city_name] = parsed
            matched += 1
        
        # Progress + checkpoint
        if (i + 1) % 100 == 0:
            pct = (i+1)/len(city_items)*100
            print(f"  [{i+1}/{len(city_items)} {pct:.0f}%] matched={matched} no_match={no_match} err={api_errors} skip={skipped}")
            with open(checkpoint_path, 'w') as f:
                json.dump({'cities': results, 'state': state_code, 'year': YEAR, 'matched': matched, 'total': len(city_items)}, f)
    
    # Final output
    output = {
        'cities': results,
        'metadata': {
            'state': state_code,
            'year': YEAR,
            'source': 'FBI CDE API',
            'matched_cities': matched,
            'total_cities': len(city_items),
            'no_match': no_match,
            'api_errors': api_errors,
            'skipped_small': skipped
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f)
    
    print(f"  ✅ {output_path}: {matched} matched, {no_match} no match, {api_errors} API errors, {skipped} skipped")
    
    # Clean checkpoint
    if api_errors == 0:
        try: os.remove(checkpoint_path)
        except: pass

if __name__ == '__main__':
    main()
