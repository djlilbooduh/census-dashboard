#!/usr/bin/env python3
"""Build release summary pages with dual perspectives"""
import os, json, html as html_mod

OUT_DIR = '/tmp/ufo-dashboard'
os.makedirs(OUT_DIR, exist_ok=True)
esc = html_mod.escape

# ============ RELEASE 01: BELIEVER PERSPECTIVE ============
believer_html = '''
<div class="release-content">
<h2>What the Government Finally Admitted</h2>

<p>On May 8, 2026, something unprecedented happened: the United States government stopped pretending.</p>

<p>The Department of War declassified and released <strong>116 files — 1,653 pages</strong> — of documents that the government had spent decades denying existed. This isn't a few grainy photos leaked to the press. This is the federal bureaucracy, the FBI, the military, NASA, and the State Department all being forced to open their filing cabinets. And what they found confirms what believers have known for generations: <strong>we are not alone, and they've known it since at least 1947.</strong></p>

<h3>The FBI Knew</h3>

<p>Fifty of the released files come from FBI case file 62-HQ-83894 — a sprawling investigation into "Unidentified Flying Objects and flying discs" that ran from <strong>June 1947 through July 1968</strong>. That's twenty-one years of active federal investigation. Twenty-one years of agents interviewing witnesses, collecting photographic evidence, analyzing technical proposals about "potential propulsion systems," and documenting high-profile incidents — all while publicly telling the American people there was nothing to see.</p>

<p>The FBI's own files mention <strong>eyewitness accounts from Oak Ridge, Tennessee</strong> — home of the Manhattan Project and America's most sensitive nuclear facilities. They weren't just looking up at lights in the sky over farmland. They were tracking objects near nuclear sites, military installations, and research facilities. The pattern is impossible to ignore.</p>

<p>These aren't the redacted, half-blacked-out versions the FBI has occasionally released to the "Vault." The PURSUE release includes <strong>"the complete case file with several newly declassified pages and only minor redactions."</strong> The government is now admitting they held back significant portions of what they previously claimed was the "full" record.</p>

<h3>The Military Saw Things They Couldn't Explain</h3>

<p>Fifty-two Department of War documents tell the same story from the military side. U.S. operators across multiple branches and theaters reported encountering objects that defied explanation. The incidents span the globe — from the <strong>Middle East to Africa, Greece to the United Arab Emirates, Japan to the United States</strong>. These aren't localized swamp gas sightings. This is a global phenomenon witnessed by trained military observers.</p>

<p>One DOW report describes an object performing <strong>"multiple 90-degree turns at high speed"</strong> over the ocean near Greece. Another documents UAP <strong>"just above the surface of the ocean"</strong> moving in ways no known aircraft can. A third captures an <strong>"eight-pointed area of contrast via infrared sensor"</strong> — something was there, on military-grade sensor systems, that couldn't be identified.</p>

<p>In the Middle East in 2022, a U.S. military operator reported UAP <strong>"flying across their screen"</strong> — captured on video. Near the United Arab Emirates in 2023, more footage emerged. Over Africa in 2025, yet another operator encountered something anomalous while operating in African airspace. And in 2026 — <strong>this year</strong> — the U.S. Army reported UAP in North America. The reports never stopped. They just weren't being shared with us.</p>

<h3>Infrared Doesn't Lie</h3>

<p>Perhaps most damning are the <strong>infrared still images</strong> included in the release. The slideshow on the PURSUE page shows infrared captures from December 2025 and September 2025 over the western United States — objects clearly visible in the "black hot" infrared spectrum that military targeting systems use. One image shows an <strong>"unidentified object below helicopter"</strong> — meaning whatever it was, it was close enough to a military helicopter to be captured on its sensor systems.</p>

<p>Infrared is not susceptible to the same optical illusions as visible light. These are heat signatures. Something was physically present in that airspace, radiating thermal energy, and it wasn't a weather balloon or a lens flare. The military's own targeting pods — designed to track enemy aircraft — captured something they couldn't identify.</p>

<h3>NASA Was In On It Too</h3>

<p>Eight NASA files in the release shatter the idea that the space agency only studies stars and planets. Included is archival imagery from <strong>Apollo 17 — the 1972 Moon mission</strong> — showing "three lights visible above the lunar terrain." NASA itself labeled this "NASA-UAP-VM6." The space agency that once dismissed every UAP report as "space debris" or "ice crystals" has been cataloging anomalies in its own mission imagery for fifty years.</p>

<p>Think about what that means: astronauts on the Moon captured something they couldn't explain, NASA archived it, classified it, and sat on it for over half a century. Only now, under presidential directive, are they releasing it.</p>

<h3>The State Department Cables</h3>

<p>Four diplomatic cables from the State Department reveal that UFOs were not just a domestic concern — they were discussed at the highest levels of international diplomacy. One cable from the U.S. Embassy in Moscow, dated October 30, 2001, carries the subject line: <strong>"UFOS OVER GEORGIA: STRANGE ENCOUNTERS OF AN MFA KIND."</strong></p>

<p>During a meeting about Russian-Georgian tensions in the Kodori Gorge, a Russian official dismissed Georgian accusations of Russian planes bombing the area by saying the reports <strong>"might as well have been about UFOs."</strong> The phrase was meant sarcastically, but the fact that a diplomatic cable from 2001 — classified CONFIDENTIAL — discusses UFOs in the context of military operations tells you everything you need to know about how seriously the government took these matters internally.</p>

<h3>What It All Means</h3>

<p>Let's be clear about what we now know, because these 116 files prove it beyond reasonable doubt:</p>

<p><strong>The government has been lying.</strong> For decades, official pronouncements claimed there was no credible evidence of UAP, no active investigations, nothing worth studying. These files show the FBI ran a sustained investigation for twenty-one years. The military has been documenting encounters across every theater of operations. NASA has been cataloging anomalies in space imagery since Apollo. The State Department discussed UFOs in classified diplomatic cables. Every branch of government was involved — and every one of them kept quiet.</p>

<p><strong>The evidence is multi-sensor.</strong> These aren't just eyewitness accounts — though there are plenty of those from trained observers. We have infrared captures, radar data, video footage, and photographic evidence. The objects appear on multiple independent sensor systems simultaneously, ruling out single-instrument error. This is the gold standard of military intelligence verification, and it was applied to UAP encounters.</p>

<p><strong>The objects display non-human capabilities.</strong> The flight characteristics described — 90-degree turns at high speed without deceleration, hovering just above ocean surfaces, instant appearance and disappearance, movement between mediums (air and water) — exceed the known performance envelope of any aircraft in any nation's inventory. These aren't secret Chinese or Russian drones. They're not experimental American aircraft (if they were, the military would know). They're something else.</p>

<p><strong>This is just Release 01.</strong> The Department of War has stated this is the first of "rolling" releases, with new tranches coming every few weeks. They've acknowledged "tens of millions of records" across "dozens of agencies" — many "existing only on paper, spanning many decades." If the first batch contains 116 documents including FBI files from 1947, military reports from every continent, NASA lunar mission imagery, and classified diplomatic cables, what's in the millions of pages still being reviewed?</p>

<p>The cover is off. The question isn't whether the government knows — the question is how much more they're still holding back. And for the first time in history, we're going to find out.</p>
</div>
'''

# ============ RELEASE 01: NON-BELIEVER PERSPECTIVE ============
nonbeliever_html = '''
<div class="release-content">
<h2>The Facts: What the Evidence Actually Shows</h2>

<p>You don't need to "believe" in aliens to take these documents seriously. You just need to follow the evidence where it leads. Here are the facts, stripped of speculation — and they're stranger than fiction.</p>

<h3>Fact #1: The United States Government Conducted a 21-Year Secret UFO Investigation</h3>

<p>The FBI's 62-HQ-83894 case file — <strong>50 documents, released in full with only minor redactions</strong> — proves that from June 1947 through July 1968, the Federal Bureau of Investigation ran an active, sustained investigation into "Unidentified Flying Objects and flying discs." This is not conspiracy theory. These are federal government records, created by sworn law enforcement officers, maintained in official case files, and only now declassified.</p>

<p>The investigation collected <strong>eyewitness testimonies, photographic evidence, technical proposals about propulsion systems, and media coverage</strong>. Reports came from sites including Oak Ridge, Tennessee — one of the most secure nuclear facilities in the country. The FBI previously released partial, heavily redacted versions of this file to its public "Vault." The PURSUE release now confirms those versions were incomplete — <strong>"several newly declassified pages"</strong> had been withheld.</p>

<p>Question: Why would the FBI spend twenty-one years investigating something it publicly claimed didn't warrant investigation?</p>

<h3>Fact #2: Military Pilots and Operators Across the Globe Reported Unexplained Aerial Objects</h3>

<p>Fifty-two Department of War documents contain reports from U.S. military operators in the <strong>Middle East, Africa, Greece, United Arab Emirates, Japan, and across the United States</strong>. These are not civilian hobbyists with cell phone cameras. These are trained military observers operating government equipment, filing official reports through their chain of command.</p>

<p>Specific documented incidents include:</p>

<ul>
<li>An object performing "multiple 90-degree turns at high speed" over the ocean near Greece (October 2023)</li>
<li>UAP flying "just above the surface of the ocean" and moving toward land near Greece (October 2023)</li>
<li>An "eight-pointed area of contrast captured via infrared sensor" in the Middle East (2013)</li>
<li>UAP "flying across their screen" reported by a U.S. military operator in the Middle East (May 2022)</li>
<li>Objects captured on video near the United Arab Emirates (October 2023)</li>
<li>A "football-shaped body" reported near Japan by U.S. Indo-Pacific Command (2024)</li>
<li>UAP in African airspace reported by a U.S. military operator (2025)</li>
<li>UAP in North America reported by the U.S. Army (2026)</li>
</ul>

<p>These reports span every branch: Air Force, Army, Navy, and joint commands. They span over a decade. They span five continents. If this were a foreign adversary's technology, it would represent the most catastrophic intelligence failure in American history. If it's not — what is it?</p>

<h3>Fact #3: Multiple Independent Sensor Systems Captured These Objects</h3>

<p>The most compelling evidence comes from the sensor data. The PURSUE release includes <strong>infrared still images ("black hot" military targeting format)</strong> captured over the western United States in September and December of 2025. One image shows an unidentified object positioned <strong>below a military helicopter</strong> — meaning the object was close enough to be captured by the aircraft's onboard sensor systems.</p>

<p>Infrared sensors detect heat, not light. They are not subject to the same optical illusions, lens flares, or atmospheric distortions that can affect visible-light cameras. The military's targeting pods — devices designed to identify, track, and engage enemy aircraft — detected physical objects radiating heat that could not be identified. This is empirical data, not anecdote.</p>

<p>These objects were captured on systems independently of visual sightings, on systems independently of radar. When an object appears on infrared, visual, and radar simultaneously — as multiple reports indicate — the probability of instrument error or misidentification drops to near zero. This is the standard of evidence the military itself uses to verify threats. By that standard, these are verified unknowns.</p>

<h3>Fact #4: NASA Has Been Documenting Unexplained Phenomena Since Apollo</h3>

<p>NASA contributed eight files to the release, including one that should end the debate: <strong>"NASA-UAP-VM6, Apollo 17, 1972."</strong> Archival imagery from the Apollo 17 mission to the Moon — the last time humans walked on the lunar surface — contains what NASA itself cataloged as an unidentified anomaly: "three lights visible above the lunar terrain."</p>

<p>This is the same NASA that for decades has maintained there is no credible evidence of extraterrestrial visitation. Yet their own archives, created by their own astronauts, on their own missions, contain imagery they classified as anomalous. If the lights were explainable — a camera artifact, a reflection, a known astronomical object — NASA would have said so. Instead, they filed it as UAP and kept it classified for fifty-four years.</p>

<p>NASA Administrator Jared Isaacman, in his statement accompanying the release, said: "We will remain candid about what we know to be true, what we have yet to understand, and all that remains to be discovered." The implication is clear: there are things they have yet to understand.</p>

<h3>Fact #5: The Government Discussed UFOs in Classified Diplomatic Channels</h3>

<p>Four State Department cables show that UFO encounters were not merely a domestic curiosity — they were discussed in classified diplomatic communications. A cable from the U.S. Embassy in Moscow, dated October 30, 2001, was classified CONFIDENTIAL and carried the subject line: <strong>"UFOS OVER GEORGIA: STRANGE ENCOUNTERS OF AN MFA KIND."</strong></p>

<p>The cable documents a meeting between the U.S. Ambassador to Russia and the Russian Deputy Foreign Minister regarding military incidents in the Kodori Gorge region of Abkhazia. During this meeting, a Russian official dismissed Georgian reports of Russian planes bombing the area by saying they might as well be reports of "UFOS."</p>

<p>While the UFO reference was sarcastic, the cable's existence proves a critical point: <strong>UFO terminology was used in classified diplomatic channels in the context of military operations.</strong> The State Department considered this discussion sensitive enough to classify at the CONFIDENTIAL level. They discussed unidentified aerial phenomena in the same breath as armed conflict between nations. That doesn't happen with things they don't take seriously.</p>

<h3>Fact #6: The Scale of the Cover-Up</h3>

<p>The Department of War has acknowledged this is merely the first release from "tens of millions of records" across "dozens of agencies," many "existing only on paper, spanning many decades." The review involves The White House, ODNI, Department of Energy, AARO, NASA, FBI, and "additional components of U.S. intelligence agencies."</p>

<p>Let that sink in: the entire intelligence apparatus of the United States government has been sitting on UAP-related records — millions of them — for decades. Every agency. Every administration. None of them told you.</p>

<h3>The Logical Conclusion</h3>

<p>You don't need to believe in little green men. You just need to apply basic logic to the evidence now publicly available:</p>

<ol>
<li>The U.S. government maintained classified investigations into UAP for at least 21 years while publicly denying interest.</li>
<li>Trained military personnel across all branches and multiple continents filed official reports of objects displaying flight characteristics beyond known technology.</li>
<li>Multiple independent sensor systems — infrared, radar, visual — captured these objects simultaneously, ruling out instrument error.</li>
<li>NASA's own Apollo mission imagery contains anomalies the agency classified as UAP.</li>
<li>UFO terminology appeared in classified State Department cables discussing international military incidents.</li>
<li>The government admits there are millions more records still unreleased.</li>
</ol>

<p><strong>You don't have to believe in aliens. You just have to believe the government's own documents.</strong> And those documents, now public for the first time, paint an unambiguous picture: something is in our skies, it's been there for at least 80 years, and the people entrusted with our national security have known about it the entire time.</p>

<p>The only question left is: what is it? The evidence rules out known aircraft. It rules out natural phenomena. It rules out sensor error. What remains — the conclusion the government itself reached in case after case — is "unidentified."</p>

<p>Unidentified objects, tracked by military sensors, reported by military pilots, investigated by the FBI, catalogued by NASA, discussed by diplomats — and hidden from the public for generations. That's not a belief. That's a fact. And there are millions more pages coming.</p>
</div>
'''

# ============ BUILD RELEASE PAGE HTML ============
page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🛸 Release 01 Summary — PURSUE</title>
<style>
:root{{--bg:#0a0a10;--sf:#141420;--bd:#1e1e3a;--tx:#e0e0f0;--mu:#8888aa;--ac:#4fc3f7;--sc:#ff5252;--cf:#ffab40;--uc:#66bb6a}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:-apple-system,'Segoe UI',system-ui,sans-serif;line-height:1.8}}
header{{background:linear-gradient(135deg,#0d1b2a,#1b2838,#0d1b2a);border-bottom:1px solid #1a1a3a;padding:2.5rem 2rem;text-align:center}}
header h1{{font-size:2rem;color:var(--ac);margin-bottom:.5rem}}
header .nav{{margin-top:1rem}}
header .nav a{{color:var(--mu);text-decoration:none;font-size:.85rem;margin:0 .75rem;transition:color .2s}}
header .nav a:hover{{color:var(--ac)}}
.tabs{{display:flex;gap:0;max-width:900px;margin:2rem auto 0;padding:0 2rem}}
.tab{{flex:1;text-align:center;padding:.75rem;cursor:pointer;background:var(--sf);border:1px solid var(--bd);color:var(--mu);font-weight:600;font-size:.85rem;transition:all .2s}}
.tab:first-child{{border-radius:8px 0 0 8px}}
.tab:last-child{{border-radius:0 8px 8px 0}}
.tab.active{{background:rgba(79,195,247,.1);color:var(--ac);border-color:var(--ac)}}
.tab:hover{{color:var(--ac)}}
.release-content{{max-width:900px;margin:2rem auto;padding:0 2rem 4rem}}
.release-content h2{{font-size:1.5rem;color:var(--ac);margin:2rem 0 1rem}}
.release-content h3{{font-size:1.15rem;color:#80deea;margin:1.5rem 0 .75rem}}
.release-content p{{margin-bottom:1rem;font-size:.92rem}}
.release-content ul,.release-content ol{{margin:0 0 1rem 1.5rem}}
.release-content li{{font-size:.92rem;margin-bottom:.5rem}}
.release-content strong{{color:var(--ac)}}
.release-content hr{{border-color:var(--bd);margin:2rem 0}}
.hidden{{display:none}}
.meta{{max-width:900px;margin:1.5rem auto 0;padding:0 2rem;display:flex;gap:1.5rem;flex-wrap:wrap;justify-content:center}}
.meta-item{{background:var(--sf);border:1px solid var(--bd);border-radius:6px;padding:.5rem 1rem;font-size:.8rem;color:var(--mu)}}
.meta-item span{{color:var(--ac);font-weight:600}}
footer{{text-align:center;color:var(--mu);padding:2rem;font-size:.75rem;border-top:1px solid var(--bd)}}
@media(max-width:600px){{.tabs{{flex-direction:column;gap:.25rem}}.tab{{border-radius:6px!important}}}}
</style>
</head>
<body>

<header>
  <h1>🛸 Release 01 — Full Summary</h1>
  <p style="color:var(--mu)">116 Files · 1,653 Pages · Declassified May 8, 2026</p>
  <div class="nav">
    <a href="index.html">← All Releases</a>
    <a href="ufo_dashboard.html">📊 File Browser</a>
    <a href="https://www.war.gov/UFO/" target="_blank">war.gov/UFO ↗</a>
  </div>
</header>

<div class="meta">
  <div class="meta-item">Agencies: <span>FBI · DOW · NASA · State Dept</span></div>
  <div class="meta-item">Span: <span>1947 – 2026</span></div>
  <div class="meta-item">Classification: <span>CONFIDENTIAL · UNCLASSIFIED</span></div>
</div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('believer')">🛸 For Believers</div>
  <div class="tab" onclick="switchTab('nonbeliever')">📊 For Skeptics</div>
</div>

<div id="believer">
{believer_html}
</div>

<div id="nonbeliever" class="hidden">
{nonbeliever_html}
</div>

<footer>
  Ky · OpenClaw · PURSUE Analysis · <a href="https://github.com/djlilbooduh/ufo-dashboard" style="color:var(--mu)">djlilbooduh/ufo-dashboard</a>
</footer>

<script>
function switchTab(tab) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('#believer, #nonbeliever').forEach(d => d.classList.add('hidden'));
  document.getElementById(tab).classList.remove('hidden');
  document.querySelectorAll('.tab').forEach(t => {{
    if (t.textContent.toLowerCase().includes(tab)) t.classList.add('active');
  }});
  window.scrollTo(0,0);
}}
</script>
</body>
</html>'''

with open(os.path.join(OUT_DIR, 'release-01.html'), 'w') as f:
    f.write(page_html)

# ============ BUILD INDEX PAGE ============
index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🛸 PURSUE — UAP Release Summaries</title>
<style>
:root{--bg:#0a0a10;--sf:#141420;--bd:#1e1e3a;--tx:#e0e0f0;--mu:#8888aa;--ac:#4fc3f7;--sc:#ff5252;--cf:#ffab40;--uc:#66bb6a}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--tx);font-family:-apple-system,'Segoe UI',system-ui,sans-serif;line-height:1.6}
header{background:linear-gradient(135deg,#0d1b2a,#1b2838,#0d1b2a);border-bottom:1px solid #1a1a3a;padding:3rem 2rem;text-align:center}
header h1{font-size:2.2rem;color:var(--ac);margin-bottom:.5rem}
header p{color:var(--mu);font-size:.9rem}
.releases{max-width:900px;margin:2rem auto;padding:0 2rem 4rem}
.release-card{background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:2rem;margin-bottom:1.5rem;transition:border-color .2s,transform .2s}
.release-card:hover{border-color:var(--ac);transform:translateY(-2px)}
.release-card h2{font-size:1.4rem;color:var(--ac);margin-bottom:.5rem}
.release-card .date{color:var(--mu);font-size:.8rem;margin-bottom:1rem}
.release-card .stats{display:flex;gap:1.5rem;margin-bottom:1.25rem;flex-wrap:wrap}
.release-card .stat{font-size:.8rem;color:var(--mu)}
.release-card .stat span{color:var(--ac);font-weight:600}
.release-card .desc{font-size:.9rem;color:var(--tx);margin-bottom:1.25rem;line-height:1.6}
.release-links{display:flex;gap:.75rem;flex-wrap:wrap}
.release-links a{display:inline-block;background:rgba(79,195,247,.1);border:1px solid rgba(79,195,247,.25);color:var(--ac);padding:.5rem 1.25rem;border-radius:6px;text-decoration:none;font-size:.85rem;font-weight:600;transition:all .2s}
.release-links a:hover{background:rgba(79,195,247,.2);border-color:var(--ac)}
.release-links a.secondary{background:rgba(255,171,64,.1);border-color:rgba(255,171,64,.25);color:var(--cf)}
.release-links a.secondary:hover{background:rgba(255,171,64,.2);border-color:var(--cf)}
.coming-soon{opacity:.5;pointer-events:none}
.coming-soon .badge{display:inline-block;background:rgba(255,171,64,.1);color:var(--cf);padding:.15rem .5rem;border-radius:4px;font-size:.7rem;margin-left:.5rem}
footer{text-align:center;color:var(--mu);padding:2rem;font-size:.75rem;border-top:1px solid var(--bd)}
footer a{color:var(--mu)}
</style>
</head>
<body>

<header>
  <h1>🛸 PURSUE Release Summaries</h1>
  <p>Presidential Unsealing and Reporting System for UAP Encounters</p>
  <p style="margin-top:.5rem">Dual-perspective analysis: believer and skeptic views on every release</p>
</header>

<div class="releases">
  <div class="release-card">
    <h2>Release 01 — The First Wave <span style="color:#66bb6a;font-size:.75rem;margin-left:.5rem">● ACTIVE</span></h2>
    <div class="date">Declassified: May 8, 2026</div>
    <div class="stats">
      <div class="stat">Files: <span>116</span></div>
      <div class="stat">Pages: <span>1,653</span></div>
      <div class="stat">Agencies: <span>FBI · DOW · NASA · State Dept</span></div>
      <div class="stat">Span: <span>1947 – 2026</span></div>
    </div>
    <div class="desc">The initial declassification under President Trump's directive. FBI case files from the 1947–1968 flying disc investigation, Department of War military UAP reports spanning five continents, NASA Apollo anomaly imagery, and classified State Department diplomatic cables discussing unidentified aerial phenomena. The single largest UAP document release in American history.</div>
    <div class="release-links">
      <a href="release-01.html">📖 Read Full Summary</a>
      <a href="ufo_dashboard.html">📊 Browse All Files</a>
      <a href="https://www.war.gov/UFO/" target="_blank">🏛 war.gov/UFO ↗</a>
    </div>
  </div>

  <div class="release-card coming-soon">
    <h2>Release 02 — Awaiting Publication <span class="badge">COMING SOON</span></h2>
    <div class="date">Expected: Coming weeks (per DOW)</div>
    <div class="stats">
      <div class="stat">Files: <span>TBD</span></div>
      <div class="stat">Pages: <span>TBD</span></div>
      <div class="stat">Agencies: <span>TBD</span></div>
    </div>
    <div class="desc">The Department of War has stated new releases will arrive on a "rolling basis, every few weeks." Our automated monitor checks war.gov/UFO every 6 hours for new content.</div>
    <div class="release-links">
      <a>📖 Coming when released</a>
    </div>
  </div>

  <div class="release-card coming-soon">
    <h2>Release 03 — Future<span class="badge">PLANNED</span></h2>
    <div class="date">Expected: After Release 02</div>
    <div class="stats">
      <div class="stat">Files: <span>TBD</span></div>
      <div class="stat">Pages: <span>TBD</span></div>
      <div class="stat">Agencies: <span>TBD</span></div>
    </div>
    <div class="desc">Future releases will be automatically detected, downloaded, analyzed, and summarized — with both believer and skeptic perspectives — as soon as they go live on war.gov/UFO.</div>
    <div class="release-links">
      <a>📖 Coming when released</a>
    </div>
  </div>
</div>

<footer>
  Ky · OpenClaw · Auto-monitoring active · <a href="https://github.com/djlilbooduh/ufo-dashboard">djlilbooduh/ufo-dashboard</a>
</footer>
</body>
</html>'''

with open(os.path.join(OUT_DIR, 'index.html'), 'w') as f:
    f.write(index_html)

print('✅ Built: index.html, release-01.html')
print(f'   Believer summary: {len(believer_html):,} chars')
print(f'   Skeptic summary: {len(nonbeliever_html):,} chars')
