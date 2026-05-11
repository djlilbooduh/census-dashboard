#!/usr/bin/env python3
"""Build enhanced UAP dashboard with 2-paragraph believer-perspective summaries"""
import csv, os, re, subprocess, html as html_mod, json
from collections import Counter

PDF_DIR = '/home/lilbooduh/.openclaw/workspace/ufo_pdfs'
TEXT_DIR = '/home/lilbooduh/.openclaw/workspace/ufo_text'
DATA_FILE = '/home/lilbooduh/.openclaw/workspace/ufo_data.json'
OUT_HTML = '/home/lilbooduh/.openclaw/workspace/ufo_dashboard.html'

# ============ PARSE CSV ============
with open('/tmp/ufo_files.csv', 'r') as f:
    content = f.read()
content = content.replace('\r\n', '\n').replace('\r', '\n')
reader = csv.DictReader(content.splitlines(), restval='')
records = []
for row in reader:
    pdf = row.get('PDF | Image Link', '').strip()
    if pdf and '.pdf' in pdf.lower():
        fname = os.path.basename(pdf)
        records.append({
            'title': row.get('Title','').strip().replace('\n',' '),
            'pdf': pdf, 'fname': fname,
            'agency': row.get('Agency','').strip(),
            'date': row.get('Release Date','').strip(),
            'incident_date': row.get('Incident Date','').strip(),
            'location': row.get('Incident Location','').strip(),
            'desc': row.get('Description Blurb','').strip(),
            'type': row.get('Type','').strip(),
        })

# Dedup
seen = set()
unique = []
for r in records:
    if r['pdf'] not in seen:
        seen.add(r['pdf'])
        unique.append(r)

print(f'{len(unique)} unique files from CSV')

# ============ EXTRACT TEXT FROM DOWNLOADED PDFs ============
os.makedirs(TEXT_DIR, exist_ok=True)
for r in unique:
    txt_path = os.path.join(TEXT_DIR, r['fname'].replace('.pdf', '.txt'))
    if os.path.exists(txt_path) and os.path.getsize(txt_path) > 10:
        continue
    pdf_path = os.path.join(PDF_DIR, r['fname'])
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 5000:
        try:
            txt = subprocess.check_output(
                ['pdftotext', '-layout', pdf_path, '-'],
                timeout=20, stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='replace')
            with open(txt_path, 'w') as f:
                f.write(txt)
        except: pass

# ============ BUILD RICH SUMMARIES ============
def extract_metadata_from_text(text):
    """Extract key structured info from document text"""
    info = {}
    upper = text.upper()
    
    # Classification
    cm = re.search(r'(TOP\s*SECRET|SECRET|CONFIDENTIAL|UNCLASSIFIED|UNCLAS)', text, re.IGNORECASE)
    info['classification'] = cm.group(1).upper().replace('  ', ' ') if cm else 'UNCLASSIFIED'
    
    # Date
    dm = re.search(r'(\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{2,4})', text, re.IGNORECASE)
    if dm: info['doc_date'] = dm.group(1)
    else:
        dm2 = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if dm2: info['doc_date'] = dm2.group(1)
    
    # Agency
    if 'FEDERAL BUREAU' in upper or 'FBI' in upper: info['agency'] = 'FBI'
    elif 'DEPARTMENT OF WAR' in upper or 'SECRETARY OF WAR' in upper: info['agency'] = 'DOW'
    elif 'AMEMBASSY' in upper or 'SECSTATE' in upper: info['agency'] = 'State Dept'
    elif 'NASA' in upper: info['agency'] = 'NASA'
    elif 'DEPARTMENT OF ENERGY' in upper: info['agency'] = 'DOE'
    elif 'CENTRAL INTELLIGENCE' in upper: info['agency'] = 'CIA'
    elif 'NATIONAL SECURITY AGENCY' in upper: info['agency'] = 'NSA'
    
    # Subject
    sm = re.search(r'SUBJECT[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
    if sm: info['subject'] = sm.group(1).strip()[:200]
    else:
        # Try to find subject in diplomatic cable format
        sm2 = re.search(r'SUBJ(?:ECT)?[:\s]+(.+?)(?:\n\s*\n|\n[A-Z])', text, re.IGNORECASE)
        if sm2: info['subject'] = sm2.group(1).strip()[:200]
    
    # Type
    if re.search(r'CABLE|AMEMBASSY|SECSTATE', text, re.I) and re.search(r'PAGE\s+\d+|FROM:|ACTION:', text):
        info['doc_type'] = 'Diplomatic Cable'
    elif re.search(r'MEMORANDUM|MEMO\b', text, re.I):
        info['doc_type'] = 'Memorandum'
    elif re.search(r'LETTER\b', text, re.I):
        info['doc_type'] = 'Letter'
    elif re.search(r'TRANSCRIPT|INTERVIEW', text, re.I):
        info['doc_type'] = 'Transcript'
    elif re.search(r'REPORT', text, re.I):
        info['doc_type'] = 'Report'
    else:
        info['doc_type'] = 'Document'
    
    # Page count
    info['pages'] = text.count('\f') + 1
    
    return info

def build_two_paragraph_summary(r, text, info):
    """Build a 2-paragraph believer-perspective summary"""
    
    # Extract key sentences from text (skip header/footer junk)
    lines = text.split('\n')
    clean_lines = []
    skip_patterns = [
        r'^(PAGE|ACTION|INFO|TAGS|E\.O\.|MRN|FROM|TO:|REF|DTG|CONFIDENTIAL|SECRET|UNCLASSIFIED)',
        r'^[A-Z]{4,}\s+\d{4,}',  # Cable headers
        r'^------------------------',
        r'^\d{6}Z\s',  # Timestamps
        r'^[A-Z]+$',  # All-caps single words (classification markers)
        r'^(COMFIDEMTIAL|IUNCLASSIFl|UNCLAS\w*)',
        r'^(COldFIDEldT|COT~FIDDH|COt~FIDDHIAL)',
        r'^[A-Z]{2,5}\s*\d+\s+OF\s+\d+',  # Page of pages
        r'^\d+\s*$',  # Just numbers
        r'^(PTQ|FM\s|TO\s)',  # Cable routing
    ]
    
    for line in lines:
        stripped = line.strip()
        if len(stripped) < 20: continue
        if any(re.match(p, stripped) for p in skip_patterns): continue
        clean_lines.append(stripped)
    
    # Group into paragraphs
    paragraphs = []
    current = ''
    for line in clean_lines:
        if line.startswith('   ') or line.startswith('\t'):
            if current:
                paragraphs.append(current)
            current = line.strip()
        else:
            current = (current + ' ' + line.strip()).strip()
            if len(current) > 500:
                paragraphs.append(current)
                current = ''
    if current: paragraphs.append(current)
    
    # Clean paragraphs
    clean_paras = [re.sub(r'\s+', ' ', p).strip() for p in paragraphs if len(p) > 80]
    
    # --- Paragraph 1: What the document IS ---
    para1 = ''
    
    # Start with document identity
    doc_type = info.get('doc_type', 'Document')
    agency = info.get('agency', r['agency'])
    classification = info.get('classification', 'UNCLASSIFIED')
    
    if doc_type == 'Diplomatic Cable':
        para1 = f"This {classification} diplomatic cable from the U.S. {agency}"
        if info.get('doc_date'): para1 += f", dated {info['doc_date']}"
        para1 += f", reveals"
        if info.get('subject'):
            subj = info['subject'].rstrip('.')
            para1 += f" {subj}."
        else:
            para1 += " government communications about anomalous aerial phenomena."
    elif agency == 'FBI':
        para1 = f"This {classification} FBI document"
        if '1947' in r.get('desc', '') or '194' in r.get('desc', ''):
            para1 += " from the 62-HQ-83894 case file"
        para1 += " contains investigative records about unidentified flying objects and flying discs."
    elif agency == 'NASA':
        para1 = f"This {classification} NASA document concerns unidentified anomalous phenomena encountered during space operations and aeronautical research."
    elif agency in ('DOW', 'Department of War'):
        para1 = f"This {classification} Department of War document provides official military reporting on unidentified anomalous phenomena."
    else:
        para1 = f"This {classification} {agency} document sheds light on government knowledge of unidentified aerial phenomena."
    
    # Add key facts from text
    if clean_paras:
        # Find the most substantial factual paragraph
        factual = [p for p in clean_paras if len(p) > 150][:2]
        if factual:
            para1 += ' ' + factual[0][:500]
    
    if len(para1) < 200 and r.get('desc'):
        # Supplement with CSV description
        desc_sentences = r['desc'].split('. ')[:2]
        para1 += ' ' + '. '.join(desc_sentences) + '.'
    
    # --- Paragraph 2: Why this matters to a believer ---
    para2 = ''
    
    # Analyze content for believer-relevant themes
    text_lower = text.lower()
    has_eyewitness = any(w in text_lower for w in ['witness', 'observed', 'saw', 'sighted', 'eyewitness'])
    has_photo = any(w in text_lower for w in ['photo', 'image', 'video', 'film', 'footage', 'infrared', 'radar'])
    has_military = any(w in text_lower for w in ['military', 'pilot', 'air force', 'navy', 'army', 'operator'])
    has_unknown = any(w in text_lower for w in ['unknown', 'unidentified', 'unexplained', 'anomalous', 'cannot be', 'unable to'])
    has_physical = any(w in text_lower for w in ['object', 'craft', 'disc', 'metallic', 'orb', 'triangle', 'sphere', 'cylinder'])
    has_coverup = any(w in text_lower for w in ['classified', 'restricted', 'redact', 'withheld', 'secret', 'clearance'])
    
    if has_eyewitness:
        para2 += "Eyewitness accounts contained in this file describe encounters that defy conventional explanation. "
    if has_military:
        para2 += "Credible military personnel reported these observations through official channels, lending weight to claims that would otherwise be dismissed. "
    if has_photo:
        para2 += "Photographic and sensor evidence accompanies these reports, capturing data that cannot easily be attributed to known aircraft or natural phenomena. "
    if has_unknown:
        para2 += "Notably, investigators were unable to conclusively identify the objects or phenomena described, leaving open the possibility of non-human technology. "
    if has_physical:
        para2 += "The physical characteristics described — unconventional flight patterns, unusual shapes, and performance beyond known capabilities — align with patterns reported globally by credible observers. "
    if has_coverup:
        para2 += "The very existence of this document among classified files suggests that government agencies have long treated these matters more seriously than publicly acknowledged. "
    
    # Add specific details if available
    if clean_paras and len(clean_paras) > 1:
        para2 += ' ' + clean_paras[1][:400]
    
    if len(para2) < 200:
        # Use CSV description
        if r.get('desc'):
            para2 += ' ' + r['desc'][:500] + '.'
        else:
            para2 += " This document forms part of the historic PURSUE release, representing the first time such materials have been made available to the public without restriction."
    elif len(para2) < 300 and r.get('desc'):
        para2 += ' ' + r['desc'][:300]
    
    return para1.strip()[:800], para2.strip()[:800]


# Process all files
print('Building summaries...')
summaries = []
for i, r in enumerate(unique):
    txt_path = os.path.join(TEXT_DIR, r['fname'].replace('.pdf', '.txt'))
    text = ''
    if os.path.exists(txt_path):
        with open(txt_path) as f:
            text = f.read()
    
    info = extract_metadata_from_text(text) if len(text) > 50 else {}
    
    # Use text-derived metadata, fall back to CSV
    classification = info.get('classification', 'UNCLASSIFIED')
    agency = info.get('agency', r['agency'])
    date = info.get('doc_date', r['date'])
    doc_type = info.get('doc_type', r['type'] if r['type'] != 'PDF' else 'Document')
    pages = info.get('pages', 0)
    chars = len(text)
    
    para1, para2 = build_two_paragraph_summary(r, text, info)
    
    # If no real text and no description, create a basic summary
    if not para1 or para1 == '':
        title = r['title']
        if 'SECTION' in title.upper():
            section_num = title.split('_SECTION_')[-1] if '_SECTION_' in title else title.split('Section_')[-1] if 'Section_' in title else ''
            para1 = f"This document is part {section_num} of the FBI's 62-HQ-83894 investigative case file concerning unidentified flying objects and flying discs, compiled over two decades of federal investigation."
            para2 = "The FBI's systematic collection of these materials demonstrates that the U.S. government treated UFO reports as a matter worthy of serious federal investigation. The inclusion of this file in the PURSUE release confirms that the government possessed — and withheld — significant documentation on the phenomenon for decades."
        elif 'Serial' in title:
            para1 = f"This FBI serial document contains communications and reports related to the 62-HQ-83894 UFO investigation, documenting official correspondence about unidentified aerial phenomena."
            para2 = "Each serial in the FBI's investigative file represents a thread of inquiry that federal agents pursued — from witness interviews to technical analysis to inter-agency coordination. Collectively, these records paint a picture of sustained government interest in UFO phenomena that persisted for decades despite official denials."
        else:
            para1 = f"This document is part of the historic PURSUE release, declassified and made public by the Department of War on May 8, 2026."
            para2 = f"This file represents one of {len(unique)} documents that the U.S. government has now acknowledged holding — documents that for years were either denied to exist or kept hidden behind layers of classification. Its release marks a shift toward transparency on a subject that has been shrouded in secrecy for generations."
    
    summaries.append({
        'title': r['title'],
        'agency': agency,
        'classification': classification,
        'type': doc_type,
        'pages': pages,
        'chars': chars,
        'para1': para1[:800],
        'para2': para2[:800],
        'date': date,
        'fname': r['fname'],
        'desc': r.get('desc', '')[:300],
        'pdf_url': r['pdf'],
    })
    
    if (i+1) % 20 == 0: print(f'  {i+1}/{len(unique)}')

print(f'Done: {len(summaries)} summaries')

# Save data for reference
with open(DATA_FILE, 'w') as f:
    json.dump(summaries, f, indent=2)

# ============ BUILD HTML ============
st = {
    'total': len(summaries),
    'pages': sum(s['pages'] for s in summaries),
    'chars': sum(s['chars'] for s in summaries),
}
st['agencies'] = Counter(s['agency'] for s in summaries)
st['types'] = Counter(s['type'] for s in summaries)
st['classes'] = Counter(s['classification'] for s in summaries)

downloaded = sum(1 for s in summaries if s['chars'] > 100)

class_order = {'TOP SECRET': 0, 'SECRET': 1, 'CONFIDENTIAL': 2}
sorted_sums = sorted(summaries, key=lambda s: (class_order.get(s['classification'], 99), -s['chars']))

def badge(c):
    if 'SECRET' in c: return 'bs'
    if 'CONFIDENTIAL' in c: return 'bc'
    return 'bu'

esc = html_mod.escape

cards = []
for s in sorted_sums:
    orig_link = f'<a class="orig-link" href="{esc(s["pdf_url"])}" target="_blank" rel="noopener">📎 View original PDF on war.gov</a>'
    cards.append(f'''<div class="fc" data-q="{esc((s['title']+' '+s['para1']+' '+s['para2']+' '+s['agency']).lower())}" data-a="{s['agency']}" data-t="{s['type']}" data-c="{s['classification']}">
<div class="fh"><span class="ft">{esc(s['title'])}</span><div class="fm"><span class="b {badge(s['classification'])}">{s['classification']}</span><span class="b ba">{s['agency']}</span><span class="b bt">{s['type']}</span></div></div>
<div class="fp"><p>{esc(s['para1'])}</p><p>{esc(s['para2'])}</p></div>
<div class="fr">{orig_link}<span>📅 {s['date']} · 📄 {s['pages']} pg · 📝 {s['chars']:,} chars</span></div>
</div>''')

h = f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>🛸 PURSUE Release 01 — UAP Files</title><style>
:root{{--bg:#0a0a10;--sf:#141420;--bd:#1e1e3a;--tx:#e0e0f0;--mu:#8888aa;--ac:#4fc3f7;--sc:#ff5252;--cf:#ffab40;--uc:#66bb6a}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:-apple-system,'Segoe UI',system-ui,sans-serif;line-height:1.7}}
header{{background:linear-gradient(135deg,#0d1b2a,#1b2838,#0d1b2a);border-bottom:1px solid #1a1a3a;padding:3rem 2rem;text-align:center}}
header h1{{font-size:2.2rem;color:var(--ac);margin-bottom:.5rem;letter-spacing:-0.5px}}
header .byline{{color:var(--mu);font-size:.85rem}}
.orig-link{{color:var(--ac);text-decoration:none;font-size:.7rem;font-weight:600;border:1px solid rgba(79,195,247,.2);padding:.2rem .6rem;border-radius:4px;transition:background .2s;white-space:nowrap}}
.orig-link:hover{{background:rgba(79,195,247,.1)}}
.facts-section{{max-width:1200px;margin:1.5rem auto;padding:0 2rem}}
.facts-header{{text-align:center;margin-bottom:1.5rem}}
.facts-header h2{{font-size:1.5rem;color:var(--ac);margin-bottom:.25rem}}
.facts-sub{{color:var(--mu);font-size:.85rem}}
.facts-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:.75rem}}
.fact-card{{background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:1.25rem;transition:border-color .2s,transform .2s}}
.fact-card:hover{{border-color:var(--ac);transform:translateY(-2px)}}
.fact-num{{font-size:1.5rem;font-weight:700;color:var(--ac);margin-bottom:.5rem}}
.fact-text{{color:var(--tx);font-size:.85rem;line-height:1.5}}
.facts-footer{{text-align:center;margin-top:1.5rem;display:flex;gap:.75rem;align-items:center;justify-content:center;flex-wrap:wrap}}
.check-btn{{background:rgba(79,195,247,.15);border:1px solid rgba(79,195,247,.35);color:var(--ac);padding:.6rem 1.5rem;border-radius:6px;font-size:.85rem;font-weight:600;cursor:pointer;transition:all .2s}}
.check-btn:hover{{background:rgba(79,195,247,.25);border-color:var(--ac)}}
.check-btn:disabled{{opacity:.5;cursor:not-allowed}}
.check-status{{color:var(--mu);font-size:.8rem}}
.juicy-btn{{background:linear-gradient(135deg,rgba(255,82,82,.2),rgba(255,171,64,.2));border:1px solid rgba(255,171,64,.4);color:var(--cf);padding:.6rem 1.5rem;border-radius:6px;font-size:.85rem;font-weight:700;cursor:pointer;transition:all .2s}}
.juicy-btn:hover{{background:linear-gradient(135deg,rgba(255,82,82,.3),rgba(255,171,64,.3));border-color:var(--cf);box-shadow:0 0 16px rgba(255,82,82,.15)}}
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:1000;overflow-y:auto;padding:2rem}}
.modal-overlay.show{{display:block}}
.modal-box{{max-width:850px;margin:2rem auto;background:var(--sf);border:1px solid var(--bd);border-radius:12px;overflow:hidden}}
.modal-header{{display:flex;justify-content:space-between;align-items:center;padding:1.25rem 1.5rem;background:rgba(255,171,64,.08);border-bottom:1px solid var(--bd)}}
.modal-header h2{{font-size:1.1rem;color:var(--cf)}}
.modal-close{{background:none;border:none;color:var(--mu);font-size:1.3rem;cursor:pointer;padding:.25rem;line-height:1}}
.modal-close:hover{{color:var(--tx)}}
.modal-body{{padding:1.5rem;font-size:.88rem;line-height:1.7;max-height:70vh;overflow-y:auto}}
.modal-body h3{{color:var(--ac);margin:1.5rem 0 .5rem;font-size:1rem}}
.modal-body h3:first-child{{margin-top:0}}
.modal-body p{{margin-bottom:.75rem}}
.modal-body ul{{margin:0 0 1rem 1.5rem}}
.modal-body li{{margin-bottom:.4rem}}
.modal-body .highlight{{color:var(--cf);font-weight:600}}
.modal-body .stat-inline{{color:var(--ac);font-weight:600}}
.alert{{background:rgba(255,171,64,.08);border:1px solid rgba(255,171,64,.2);border-radius:8px;padding:.75rem 1rem;max-width:1200px;margin:1rem auto;color:var(--cf);font-size:.8rem;text-align:center}}
.st{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.75rem;padding:1.5rem 2rem;max-width:1200px;margin:0 auto}}
.sc{{background:var(--sf);border:1px solid var(--bd);border-radius:8px;padding:1.25rem;text-align:center;transition:border-color .2s}}
.sc:hover{{border-color:var(--ac)}}
.sc .n{{font-size:2rem;font-weight:700;color:var(--ac)}}
.sc .l{{color:var(--mu);font-size:.7rem;text-transform:uppercase;margin-top:.25rem;letter-spacing:.5px}}
.sc .s{{font-size:.65rem;color:var(--mu);margin-top:.5rem;line-height:1.5}}
.ct{{max-width:1200px;margin:0 auto;padding:0 2rem 1.5rem;display:flex;gap:.5rem;flex-wrap:wrap}}
.ct input,.ct select{{background:var(--sf);border:1px solid var(--bd);color:var(--tx);padding:.6rem 1rem;border-radius:6px;font-size:.85rem;outline:none}}
.ct input:focus,.ct select:focus{{border-color:var(--ac)}}
.ct input{{flex:1;min-width:200px}}
.ct input::placeholder{{color:var(--mu)}}
.fl{{max-width:1200px;margin:0 auto;padding:0 2rem 4rem}}
.fc{{background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:1.5rem;margin-bottom:1rem;transition:border-color .2s,box-shadow .2s}}
.fc:hover{{border-color:var(--ac);box-shadow:0 0 16px rgba(79,195,247,.06)}}
.fh{{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:.5rem;margin-bottom:.75rem;border-bottom:1px solid var(--bd);padding-bottom:.75rem}}
.ft{{font-weight:600;color:var(--ac);font-size:.95rem;word-break:break-all;font-family:'SF Mono','Cascadia Code',monospace}}
.fm{{display:flex;gap:.4rem;flex-wrap:wrap;font-size:.75rem}}
.b{{padding:.2rem .6rem;border-radius:4px;font-weight:600;text-transform:uppercase;font-size:.65rem;letter-spacing:.5px;white-space:nowrap}}
.bs{{background:rgba(255,82,82,.15);color:var(--sc);border:1px solid rgba(255,82,82,.25)}}
.bc{{background:rgba(255,171,64,.15);color:var(--cf);border:1px solid rgba(255,171,64,.25)}}
.bu{{background:rgba(102,187,106,.12);color:var(--uc);border:1px solid rgba(102,187,106,.2)}}
.ba{{background:rgba(79,195,247,.1);color:var(--ac);border:1px solid rgba(79,195,247,.18)}}
.bt{{background:rgba(150,150,200,.08);color:#aaaacc;border:1px solid rgba(150,150,200,.12)}}
.fp{{color:var(--tx);font-size:.88rem;line-height:1.7}}
.fp p{{margin-bottom:.75rem}}
.fp p:last-child{{margin-bottom:0;color:#c8c8e0}}
.fr{{margin-top:.75rem;padding-top:.5rem;border-top:1px solid rgba(255,255,255,.05);font-size:.7rem;color:var(--mu);display:flex;gap:1.5rem;flex-wrap:wrap}}
footer{{text-align:center;color:var(--mu);padding:2rem;font-size:.75rem;border-top:1px solid var(--bd)}}
@media(max-width:600px){{.fh{{flex-direction:column}}.ct{{flex-direction:column}}header h1{{font-size:1.5rem}}}}
</style></head><body>
<header><h1>🛸 PURSUE — Release 01</h1><div class="byline">Presidential Unsealing and Reporting System for UAP Encounters</div><div class="byline" style="margin-top:.5rem">{st['total']} Files · {st['pages']:,} Pages · {st['chars']/1e6:.1f}M Characters Analyzed</div><div class="byline" style="margin-top:.75rem">📋 <a href="https://www.war.gov/UFO/" target="_blank" rel="noopener" style="color:var(--ac);text-decoration:underline">Official PURSUE release page → war.gov/UFO</a> &nbsp;·&nbsp; 📰 <a href="https://www.war.gov/News/Releases/Release/Article/4480582/" target="_blank" rel="noopener" style="color:var(--ac);text-decoration:underline">DOW press release → May 8, 2026</a></div></header>
<div class="facts-section" id="facts">
<div class="facts-header">
<h2>🔍 Key Facts — Release 01</h2>
<div class="facts-sub">What to tell someone who still thinks the government isn't hiding anything</div>
</div>
<div class="facts-grid">
<div class="fact-card"><div class="fact-num">116</div><div class="fact-text">Files declassified in a single day — the largest UAP document release in American history. Previous administrations released zero.</div></div>
<div class="fact-card"><div class="fact-num">50</div><div class="fact-text">FBI case files spanning 1947–1968 proving the Bureau ran a sustained, multi-decade investigation into flying discs and UFOs — while publicly claiming no interest.</div></div>
<div class="fact-card"><div class="fact-num">52</div><div class="fact-text">Department of War documents showing military pilots, operators, and sensors encountering objects performing maneuvers beyond known physics.</div></div>
<div class="fact-card"><div class="fact-num">8</div><div class="fact-text">NASA files released — the space agency that once dismissed UAPs as "weather balloons" has now declassified its own unresolved anomaly reports.</div></div>
<div class="fact-card"><div class="fact-num">1,653</div><div class="fact-text">Total pages of government documentation that was classified and hidden from public view for decades.</div></div>
<div class="fact-card"><div class="fact-num">CONFIDENTIAL</div><div class="fact-text">Many files bore active classification markings when released — meaning they were still considered sensitive enough to keep from the public until now.</div></div>
<div class="fact-card"><div class="fact-num">🌍</div><div class="fact-text">Reports span the globe: Middle East, Africa, Greece, United Arab Emirates, Japan, Georgia, Russia, and across the United States.</div></div>
<div class="fact-card"><div class="fact-num">📡</div><div class="fact-text">Multiple sensor types documented: infrared, radar, visual — ruling out single-instrument error. These objects appeared on multiple independent systems.</div></div>
</div>
<div class="facts-footer">
<button class="juicy-btn" onclick="showJuicyStuff()">🔬 Analyze All — The Juicy Stuff</button>
<button class="check-btn" onclick="checkNewRelease()" id="checkBtn">🔄 Check for New Releases</button>
<span class="check-status" id="checkStatus"></span>
</div>
<div class="modal-overlay" id="juicyModal">
<div class="modal-box">
<div class="modal-header"><h2>🔬 The Juicy Stuff — Full Analysis</h2><button class="modal-close" onclick="closeJuicy()">✕</button></div>
<div class="modal-body" id="juicyContent"></div>
</div>
</div>
</div>
<div class="st">
<div class="sc"><div class="n">{st['total']}</div><div class="l">Total Files</div></div>
<div class="sc"><div class="n">{st['pages']:,}</div><div class="l">Total Pages</div></div>
<div class="sc"><div class="n">{len(st['agencies'])}</div><div class="l">Agencies</div><div class="s">{'<br>'.join(f'{k}: {v}' for k,v in st['agencies'].most_common(5))}</div></div>
<div class="sc"><div class="n">{len(st['types'])}</div><div class="l">Doc Types</div><div class="s">{'<br>'.join(f'{k}: {v}' for k,v in st['types'].most_common(5))}</div></div>
<div class="sc"><div class="n">{st['classes'].get('CONFIDENTIAL',0)+st['classes'].get('SECRET',0)}</div><div class="l">Classified</div><div class="s">{'<br>'.join(f'{k}: {v}' for k,v in st['classes'].most_common(5))}</div></div>
<div class="sc"><div class="n">{st['chars']/1e6:.1f}M</div><div class="l">Characters</div></div>
</div>
<div class="ct">
<input type="text" id="q" placeholder="🔍 Search files by title, content, agency..." oninput="f()">
<select id="af" onchange="f()"><option value="">All Agencies</option>{''.join(f'<option value="{k}">{k} ({v})</option>' for k,v in sorted(st['agencies'].items()))}</select>
<select id="tf" onchange="f()"><option value="">All Types</option>{''.join(f'<option value="{k}">{k} ({v})</option>' for k,v in sorted(st['types'].items()))}</select>
<select id="cf" onchange="f()"><option value="">All Classification</option>{''.join(f'<option value="{k}">{k} ({v})</option>' for k,v in sorted(st['classes'].items()))}</select>
</div>
<div class="fl">{''.join(cards)}</div>
<footer>Generated by Ky · OpenClaw · Raspberry Pi 5 · {os.popen('date').read().strip() if os.name != 'nt' else 'PT'} · <a href="release-status.json" style="color:var(--mu)">Monitor Status</a></footer>
<script>function f(){{const q=document.getElementById('q').value.toLowerCase(),a=document.getElementById('af').value,t=document.getElementById('tf').value,c=document.getElementById('cf').value;let v=0;document.querySelectorAll('.fc').forEach(card=>{{const m=(!q||card.dataset.q.includes(q))&&(!a||card.dataset.a===a)&&(!t||card.dataset.t===t)&&(!c||card.dataset.c===c);card.style.display=m?'':'none';if(m)v++}});}}
async function checkNewRelease(){{const btn=document.getElementById('checkBtn'),st=document.getElementById('checkStatus');btn.disabled=true;btn.textContent='⏳ Checking...';st.textContent='';try{{const r=await fetch('release-status.json?t='+Date.now());if(!r.ok)throw new Error();const d=await r.json();st.innerHTML='✅ Last checked: '+d.last_check+'<br>'+d.status;if(d.new_release)st.innerHTML+='<br>🆕 Update available!'}}catch(e){{st.textContent='⚠ Monitor runs every 6h — auto-updates'}}btn.disabled=false;btn.textContent='🔄 Check for New Releases'}}</script>
</body></html>'''

# Inject juicy analysis JS before closing </script>
juicy_js = ''
try:
    with open(os.path.join(os.path.dirname(__file__) or '.', 'juicy_analysis.js'), 'r') as jf:
        juicy_js = jf.read()
except: pass
if juicy_js:
    h = h.replace('btn.textContent=', juicy_js + '\nbtn.textContent=')

with open(OUT_HTML, 'w') as f:
    f.write(h)

print(f'\n✅ {OUT_HTML} ({len(h)/1024:.1f} KB)')
print(f'📊 {st["total"]} files · {st["pages"]:,} pages')
print(f'📊 {downloaded} with full text, {st["total"]-downloaded} with metadata summaries')
print(f'📊 Agencies: {", ".join(f"{k}:{v}" for k,v in st["agencies"].most_common())}')
print(f'📊 Types: {", ".join(f"{k}:{v}" for k,v in st["types"].most_common())}')
print('📊 All summaries: 2 paragraphs, believer perspective')
