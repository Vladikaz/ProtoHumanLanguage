import os, sys, sqlite3, math, re
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
SCRIPTS_DIR = os.path.join(TARGET_DIR, "scripts")
os.makedirs(SCRIPTS_DIR, exist_ok=True)

P3_DB = os.path.join(TARGET_DIR, "phase3_monogenesis.db")
UNI_DB = os.path.join(DATA_DIR, "universal_linguistic_database.db")

print("Executing Phase 3 Script 1: Extract Deep Cognate Matches (Optimized)...")

ULTRACONSERVED = {
    'water': 2.5, 'fire': 2.5, 'I': 2.5, 'we': 2.5, 'two': 2.5,
    'eye': 2.5, 'night': 2.5, 'mother': 2.5, 'father': 2.5, 'who': 2.5,
    'name': 2.5, 'tongue': 2.5, 'hand': 2.5, 'star': 2.5, 'sun': 2.5, 'moon': 2.5,
    'dog': 1.8, 'blood': 1.8, 'new': 1.8, 'ear': 1.8, 'tooth': 1.8,
    'bone': 1.8, 'liver': 1.8, 'fish': 1.8, 'stone': 1.8, 'tree': 1.8, 'leaf': 1.8
}

def get_concept_weight(c):
    return ULTRACONSERVED.get(str(c).lower(), 1.0)

def haversine_km(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

def fast_sim(s1, s2):
    if not s1 or not s2: return 0.0
    if s1 == s2: return 1.0
    # Quick prefix match or common char ratio
    set1, set2 = set(s1), set(s2)
    inter = len(set1.intersection(set2))
    union = len(set1.union(set2))
    if union == 0: return 0.0
    jaccard = inter / float(union)
    prefix_bonus = 0.3 if (len(s1)>0 and len(s2)>0 and s1[0] == s2[0]) else 0.0
    return round(min(1.0, jaccard + prefix_bonus), 4)

p3_conn = sqlite3.connect(P3_DB)
p3_c = p3_conn.cursor()

p3_c.execute("DROP TABLE IF EXISTS deep_cognate_matches")
p3_c.execute("""
CREATE TABLE deep_cognate_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lang_a TEXT,
    lang_b TEXT,
    family_a TEXT,
    family_b TEXT,
    concept TEXT,
    form_a TEXT,
    form_b TEXT,
    seg_a TEXT,
    seg_b TEXT,
    phonetic_similarity REAL,
    concept_weight REAL,
    weighted_score REAL,
    geographic_distance_km REAL,
    is_transcontinental INTEGER,
    is_deneyeni INTEGER
)
""")
p3_conn.commit()

uni_conn = sqlite3.connect(UNI_DB)
uni_c = uni_conn.cursor()

uni_c.execute("SELECT name_full, family_lineage, latitude, longitude FROM languages_metadata")
meta_map = {}
for name, fam, lat, lon in uni_c.fetchall():
    meta_map[name] = {'family': fam if fam else '', 'lat': lat, 'lon': lon}

uni_c.execute("PRAGMA table_info(languages_database)")
cols = [c[1] for c in uni_c.fetchall()]
concept_cols = cols[9:]

uni_c.execute("SELECT * FROM languages_database")
db_rows = uni_c.fetchall()

family_langs = {}
for r in db_rows:
    name = r[0]
    raw_fam = r[1]
    top_fam = raw_fam.split('>')[0].split('/')[0].strip() if raw_fam else 'Unclassified'
    meta = meta_map.get(name, {})
    lat = meta.get('lat')
    lon = meta.get('lon')
    vocab = {}
    for idx, cname in enumerate(concept_cols):
        val = r[9 + idx]
        if val and str(val).strip() not in ('—', '-', '?', 'None', ''):
            vocab[cname] = str(val).strip()
    if vocab:
        if top_fam not in family_langs:
            family_langs[top_fam] = []
        family_langs[top_fam].append((name, top_fam, vocab, lat, lon))

# Take top 2 representatives per family for fast execution
macro_representatives = []
for top_fam, l_list in family_langs.items():
    l_list.sort(key=lambda x: len(x[2]), reverse=True)
    macro_representatives.extend(l_list[:2])

print(f"Selected {len(macro_representatives)} key macrofamily representatives.")

batch = []
total_matches = 0
deneyeni_matches = 0

n_rep = len(macro_representatives)
for i in range(n_rep):
    name1, fam1, v1, lat1, lon1 = macro_representatives[i]
    for j in range(i + 1, n_rep):
        name2, fam2, v2, lat2, lon2 = macro_representatives[j]
        if fam1 == fam2:
            continue
            
        shared_concepts = set(v1.keys()).intersection(v2.keys())
        if not shared_concepts:
            continue
            
        dist_km = haversine_km(lat1, lon1, lat2, lon2)
        is_transcont = 1 if dist_km > 3000.0 else 0
        
        is_dy = 1 if (('енисей' in fam1.lower() or 'ket' in name1.lower() or 'yeniseian' in fam1.lower()) and 
                      ('дене' in fam2.lower() or 'navajo' in name2.lower() or 'na-dene' in fam2.lower())) or \
                     (('енисей' in fam2.lower() or 'ket' in name2.lower() or 'yeniseian' in fam2.lower()) and 
                      ('дене' in fam1.lower() or 'navajo' in name1.lower() or 'na-dene' in fam1.lower())) else 0
        
        for cname in shared_concepts:
            f1, f2 = v1[cname], v2[cname]
            sim = fast_sim(f1, f2)
            
            if sim >= 0.40 or is_dy:
                c_weight = get_concept_weight(cname)
                w_score = round(sim * c_weight, 4)
                
                batch.append((
                    name1, name2, fam1, fam2, cname, f1, f2, f1, f2,
                    sim, c_weight, w_score, dist_km, is_transcont, is_dy
                ))
                total_matches += 1
                if is_dy: deneyeni_matches += 1
                
                if len(batch) >= 5000:
                    p3_c.executemany("""
                    INSERT INTO deep_cognate_matches (
                        lang_a, lang_b, family_a, family_b, concept, form_a, form_b,
                        seg_a, seg_b, phonetic_similarity, concept_weight, weighted_score,
                        geographic_distance_km, is_transcontinental, is_deneyeni
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    p3_conn.commit()
                    batch = []

if batch:
    p3_c.executemany("""
    INSERT INTO deep_cognate_matches (
        lang_a, lang_b, family_a, family_b, concept, form_a, form_b,
        seg_a, seg_b, phonetic_similarity, concept_weight, weighted_score,
        geographic_distance_km, is_transcontinental, is_deneyeni
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batch)
    p3_conn.commit()

p3_c.execute("CREATE INDEX IF NOT EXISTS idx_deep_sim ON deep_cognate_matches(phonetic_similarity)")
p3_c.execute("CREATE INDEX IF NOT EXISTS idx_deep_trans ON deep_cognate_matches(is_transcontinental)")
p3_c.execute("CREATE INDEX IF NOT EXISTS idx_deep_dy ON deep_cognate_matches(is_deneyeni)")
p3_conn.commit()

print(f"SUCCESS: Mined {total_matches} deep cross-macrofamily cognate matches.")
print(f"Dené-Yeniseian trans-continental matches flagged: {deneyeni_matches}")

p3_conn.close()
uni_conn.close()