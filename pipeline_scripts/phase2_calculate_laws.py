import os, sys, sqlite3, math, json
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
PHASE2_DB = os.path.join(TARGET_DIR, "phase2.db")

print("Executing Script 4: Calculate Universal Laws & Transition Matrices...")

VOWELS = set('a e i o u y ø æ œ ɐ ɑ ɒ ɘ ə ɚ ɛ ɜ ɝ ɞ ɨ ɩ ɪ ɤ ɵ ɶ ʉ ʊ ʌ ɘ̃ ã ẽ ĩ õ ũ aː eː iː oː uː yː'.split())
STOPS = set('p t k q b d g pʰ tʰ kʰ qʰ p\' t\' k\' q\' ʈ ɖ ɓ ɗ ɠ'.split())
FRICATIVES = set('f v s z ʃ ʒ x ɣ h θ ð ɕ ʑ χ ʁ ʕ ħ ɸ β'.split())
NASALS = set('m n ŋ ɲ ɳ ɴ'.split())
LIQUIDS = set('r l j w ɹ ɺ ɾ ɼ ɽ ʀ ʁ ʎ ʟ'.split())
AFFRICATES = set('ts dz tʃ dʒ tɕ dʑ pf bv'.split())

def get_phoneme_class(p):
    if not p or p == '∅':
        return 'Empty'
    if p in VOWELS or (len(p)>0 and p[0] in VOWELS):
        return 'Vowel'
    if p in STOPS:
        return 'Plosive/Stop'
    if p in FRICATIVES:
        return 'Fricative'
    if p in NASALS:
        return 'Nasal'
    if p in LIQUIDS:
        return 'Liquid/Approximant'
    if p in AFFRICATES:
        return 'Affricate'
    return 'Consonant'

def classify_process(src, tgt, pos_cls, src_cls, tgt_cls):
    if src == tgt:
        return 'Stability'
    if tgt == '∅':
        return 'Deletion (Apocope/Syncope)'
    if src == '∅':
        return 'Epenthesis/Insertion'
    
    if src_cls == 'Plosive/Stop' and tgt_cls == 'Fricative':
        return 'Spirantization / Lenition'
    if src_cls == 'Plosive/Stop' and tgt_cls == 'Affricate':
        return 'Affrication'
    if src in ('k', 'g', 't', 'd', 'kʷ', 'gʷ') and tgt in ('s', 'z', 'ʃ', 'ʒ', 'tʃ', 'dʒ', 'tɕ', 'dʑ', 'ɕ', 'ʑ'):
        return 'Palatalization'
    if src in ('p', 't', 'k', 's') and tgt in ('b', 'd', 'g', 'z'):
        return 'Voicing (Intervocalic)'
    if src in ('b', 'd', 'g', 'z') and tgt in ('p', 't', 'k', 's'):
        return 'Devoicing (Final/Fortition)'
    if src_cls == 'Vowel' and tgt_cls == 'Vowel':
        return 'Vowel Shift'
    if src_cls == 'Fricative' and tgt == 'h':
        return 'Debuccalization'
    if src == 'h' and tgt == '∅':
        return 'H-Loss'
    
    return f'{src_cls} -> {tgt_cls}'

conn = sqlite3.connect(PHASE2_DB)
c = conn.cursor()

# Prepare tables
c.execute("DROP TABLE IF EXISTS universal_laws")
c.execute("""
CREATE TABLE universal_laws (
    law_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_seg TEXT,
    target_seg TEXT,
    context_class TEXT,
    phonetic_process TEXT,
    source_class TEXT,
    target_class TEXT,
    probability REAL,
    rate_per_1000y REAL,
    asymmetry_index REAL,
    universality_score INTEGER,
    cognate_count INTEGER,
    rule_count INTEGER,
    total_evidence INTEGER,
    attested_families TEXT,
    split_distribution TEXT,
    areal_suspect INTEGER
)
""")

c.execute("DROP TABLE IF EXISTS phoneme_transition_matrix")
c.execute("""
CREATE TABLE phoneme_transition_matrix (
    source_seg TEXT,
    target_seg TEXT,
    marginal_probability REAL,
    total_occurrences INTEGER,
    asymmetry_index REAL
)
""")
conn.commit()

# Load all raw transitions
c.execute("SELECT source_seg, target_seg, position_class, family, time_delta, evidence_source FROM raw_transitions")
raw_data = c.fetchall()

print(f"Analyzing {len(raw_data)} transition events...")

# 1. Total source counts per context
source_context_totals = {} # (src, pos_cls) -> total
source_totals = {}         # src -> total
pair_counts = {}           # (src, tgt, pos_cls) -> {'cog': 0, 'rule': 0, 'families': set(), 'time_deltas': []}
global_pair_counts = {}    # (src, tgt) -> count

for src, tgt, pos_cls, fam, dt, ev_src in raw_data:
    if not src:
        continue
    sc_key = (src, pos_cls)
    source_context_totals[sc_key] = source_context_totals.get(sc_key, 0) + 1
    source_totals[src] = source_totals.get(src, 0) + 1
    
    pair_key = (src, tgt, pos_cls)
    if pair_key not in pair_counts:
        pair_counts[pair_key] = {'cog': 0, 'rule': 0, 'families': set(), 'time_deltas': []}
        
    if ev_src == 'cognate':
        pair_counts[pair_key]['cog'] += 1
        if dt and dt > 0:
            pair_counts[pair_key]['time_deltas'].append(dt)
    else:
        pair_counts[pair_key]['rule'] += 1
        
    if fam:
        # Normalize top-level macrofamily
        top_fam = fam.split('>')[0].split('/')[0].strip()
        pair_counts[pair_key]['families'].add(top_fam)
        
    g_key = (src, tgt)
    global_pair_counts[g_key] = global_pair_counts.get(g_key, 0) + 1

print(f"Aggregated {len(pair_counts)} unique (source, target, context) triples.")

# Compute split distributions per (source, context)
split_dists = {} # (src, pos_cls) -> {tgt: prob}
for (src, tgt, pos_cls), data in pair_counts.items():
    sc_total = source_context_totals.get((src, pos_cls), 1)
    tot = data['cog'] + data['rule']
    prob = tot / float(sc_total)
    sc_key = (src, pos_cls)
    if sc_key not in split_dists:
        split_dists[sc_key] = {}
    split_dists[sc_key][tgt] = round(prob, 4)

# 2. Insert Universal Laws
laws_batch = []
for (src, tgt, pos_cls), data in pair_counts.items():
    if src == tgt:
        continue # Focus laws on non-identical shifts (changes)
    
    cog_c = data['cog']
    rule_c = data['rule']
    tot_ev = cog_c + rule_c
    if tot_ev < 2: # Filter out single isolated glitches
        continue
        
    sc_total = source_context_totals.get((src, pos_cls), tot_ev)
    prob = round(tot_ev / float(sc_total), 4)
    
    # Calculate Asymmetry Index: A(X->Y) = (N(X->Y) - N(Y->X)) / (N(X->Y) + N(Y->X))
    reverse_key = (tgt, src, pos_cls)
    rev_data = pair_counts.get(reverse_key, {'cog': 0, 'rule': 0})
    rev_tot = rev_data['cog'] + rev_data['rule']
    asym = round((tot_ev - rev_tot) / float(tot_ev + rev_tot), 4) if (tot_ev + rev_tot) > 0 else 1.0
    
    # Calculate Rate per 1000 years: P_1000y = 1 - exp(-lambda * 1000)
    rate_1000y = None
    if data['time_deltas']:
        avg_dt = sum(data['time_deltas']) / len(data['time_deltas'])
        if avg_dt > 0 and prob < 1.0:
            # lambda = -ln(1 - P_change) / dt
            # Here P_change from src = 1 - P(src->src) ~ prob of this specific path
            lmbda = -math.log(max(0.0001, 1.0 - prob)) / avg_dt
            rate_1000y = round(1.0 - math.exp(-lmbda * 1000.0), 4)
            
    fams = sorted(list(data['families']))
    universality = len(fams)
    
    src_cls = get_phoneme_class(src)
    tgt_cls = get_phoneme_class(tgt)
    process = classify_process(src, tgt, pos_cls, src_cls, tgt_cls)
    
    split_json = json.dumps(split_dists.get((src, pos_cls), {}), ensure_ascii=False)
    fams_str = ", ".join(fams[:15])
    areal = 1 if (universality == 1 and tot_ev > 20) else 0
    
    laws_batch.append((
        src, tgt, pos_cls, process, src_cls, tgt_cls, prob, rate_1000y, asym,
        universality, cog_c, rule_c, tot_ev, fams_str, split_json, areal
    ))

c.executemany("""
INSERT INTO universal_laws (
    source_seg, target_seg, context_class, phonetic_process, source_class, target_class,
    probability, rate_per_1000y, asymmetry_index, universality_score,
    cognate_count, rule_count, total_evidence, attested_families, split_distribution, areal_suspect
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", laws_batch)
conn.commit()

print(f"Inserted {len(laws_batch)} universal phonetic laws into universal_laws table.")

# 3. Insert Global Phoneme Transition Matrix
matrix_batch = []
for (src, tgt), tot in global_pair_counts.items():
    s_tot = source_totals.get(src, tot)
    m_prob = round(tot / float(s_tot), 4)
    rev_tot = global_pair_counts.get((tgt, src), 0)
    asym = round((tot - rev_tot) / float(tot + rev_tot), 4) if (tot + rev_tot) > 0 else 1.0
    matrix_batch.append((src, tgt, m_prob, tot, asym))

c.executemany("""
INSERT INTO phoneme_transition_matrix (
    source_seg, target_seg, marginal_probability, total_occurrences, asymmetry_index
) VALUES (?, ?, ?, ?, ?)
""", matrix_batch)
conn.commit()

c.execute("CREATE INDEX IF NOT EXISTS idx_laws_src ON universal_laws(source_seg)")
c.execute("CREATE INDEX IF NOT EXISTS idx_laws_proc ON universal_laws(phonetic_process)")
c.execute("CREATE INDEX IF NOT EXISTS idx_laws_univ ON universal_laws(universality_score)")
c.execute("CREATE INDEX IF NOT EXISTS idx_laws_ev ON universal_laws(total_evidence)")
conn.commit()

print("=== TOP 15 MOST UNIVERSAL PHONETIC LAWS DISCOVERED ===")
c.execute("SELECT source_seg, target_seg, context_class, phonetic_process, universality_score, total_evidence, probability, asymmetry_index FROM universal_laws ORDER BY universality_score DESC, total_evidence DESC LIMIT 15")
for r in c.fetchall():
    print(f"  [{r[0]:4}] -> [{r[1]:4}] ({r[2]:6}) | {r[3]:28} | Univ: {r[4]:2} fams | Ev: {r[5]:4} | P: {r[6]:.2f} | Asym: {r[7]:+.2f}")

conn.close()
print("SUCCESS: Script 4 complete.")