import os, sys, sqlite3, re
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
PHASE2_DB = os.path.join(TARGET_DIR, "phase2.db")
UNI_DB = os.path.join(DATA_DIR, "universal_linguistic_database.db")

print("Executing Script 3: Mine Phonetic Transitions...")

VOWELS = set('a e i o u y ø æ œ ɐ ɑ ɒ ɘ ə ɚ ɛ ɜ ɝ ɞ ɨ ɩ ɪ ɤ ɵ ɶ ʉ ʊ ʌ ɘ̃ ã ẽ ĩ õ ũ aː eː iː oː uː yː'.split())

def is_vowel(seg):
    if not seg or seg in ('#', '∅'):
        return False
    return seg[0] in VOWELS

def align_sequences(seq_a, seq_b):
    m, n = len(seq_a), len(seq_b)
    score = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): score[i][0] = i * -1
    for j in range(n + 1): score[0][j] = j * -1
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            sa, sb = seq_a[i-1], seq_b[j-1]
            if sa == sb:
                match = score[i-1][j-1] + 2
            elif is_vowel(sa) == is_vowel(sb):
                match = score[i-1][j-1] + 1
            else:
                match = score[i-1][j-1] - 1
            score[i][j] = max(match, score[i-1][j] - 1, score[i][j-1] - 1)
            
    i, j = m, n
    aligned_a, aligned_b = [], []
    while i > 0 and j > 0:
        curr = score[i][j]
        sa, sb = seq_a[i-1], seq_b[j-1]
        diag_val = 2 if sa == sb else (1 if is_vowel(sa) == is_vowel(sb) else -1)
        if curr == score[i-1][j-1] + diag_val:
            aligned_a.append(sa); aligned_b.append(sb)
            i -= 1; j -= 1
        elif curr == score[i-1][j] - 1:
            aligned_a.append(sa); aligned_b.append('∅')
            i -= 1
        else:
            aligned_a.append('∅'); aligned_b.append(sb)
            j -= 1
            
    while i > 0:
        aligned_a.append(seq_a[i-1]); aligned_b.append('∅'); i -= 1
    while j > 0:
        aligned_a.append('∅'); aligned_b.append(seq_b[j-1]); j -= 1
        
    aligned_a.reverse(); aligned_b.reverse()
    return aligned_a, aligned_b

p2_conn = sqlite3.connect(PHASE2_DB)
p2_c = p2_conn.cursor()

p2_c.execute("DROP TABLE IF EXISTS raw_transitions")
p2_c.execute("""
CREATE TABLE raw_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_seg TEXT,
    target_seg TEXT,
    left_context TEXT,
    right_context TEXT,
    position_class TEXT,
    concept TEXT,
    family TEXT,
    year_ancestor REAL,
    year_descendant REAL,
    time_delta REAL,
    evidence_source TEXT
)
""")
p2_conn.commit()

# 1. Process Cognate Pairs from Phase 2 DB
p2_c.execute("SELECT ancestor_lang, descendant_lang, concept, segments_ancestor, segments_descendant, year_ancestor, year_descendant, time_delta_years, family FROM cognate_pairs")
cog_rows = p2_c.fetchall()

print(f"Aligning {len(cog_rows)} cognate pairs...")

insert_batch = []
total_transitions = 0

for anc, desc, concept, sa_str, sd_str, y_anc, y_desc, dt, fam in cog_rows:
    if not sa_str or not sd_str:
        continue
    seq_a = sa_str.split()
    seq_b = sd_str.split()
    if not seq_a or not seq_b:
        continue
        
    al_a, al_b = align_sequences(seq_a, seq_b)
    n = len(al_a)
    
    for idx in range(n):
        src = al_a[idx]
        tgt = al_b[idx]
        
        left_ctx = al_a[idx-1] if idx > 0 else '#'
        right_ctx = al_a[idx+1] if idx < n-1 else '#'
        
        if left_ctx == '#':
            pos_cls = '#_'
        elif right_ctx == '#':
            pos_cls = '_#'
        elif is_vowel(left_ctx) and is_vowel(right_ctx):
            pos_cls = 'V_V'
        elif not is_vowel(left_ctx) and not is_vowel(right_ctx) and left_ctx != '#' and right_ctx != '#':
            pos_cls = 'C_C'
        else:
            pos_cls = 'medial'
            
        insert_batch.append((
            src, tgt, left_ctx, right_ctx, pos_cls, concept, fam, y_anc, y_desc, dt, 'cognate'
        ))
        total_transitions += 1
        
        if len(insert_batch) >= 20000:
            p2_c.executemany("""
            INSERT INTO raw_transitions (
                source_seg, target_seg, left_context, right_context, position_class,
                concept, family, year_ancestor, year_descendant, time_delta, evidence_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insert_batch)
            p2_conn.commit()
            insert_batch = []

if insert_batch:
    p2_c.executemany("""
    INSERT INTO raw_transitions (
        source_seg, target_seg, left_context, right_context, position_class,
        concept, family, year_ancestor, year_descendant, time_delta, evidence_source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, insert_batch)
    p2_conn.commit()
    insert_batch = []

print(f"Extracted {total_transitions} transitions from cognate pairs.")

# 2. Process Diachronic Rules from Universal DB
uni_conn = sqlite3.connect(UNI_DB)
uni_c = uni_conn.cursor()

uni_c.execute("SELECT language, source_sound, target_sound, environment, raw_rule FROM diachronic_rules")
rule_rows = uni_c.fetchall()
print(f"Processing {len(rule_rows)} diachronic rules...")

rule_count = 0
for lang, src, tgt, env, raw in rule_rows:
    if not src or not tgt:
        continue
    src_clean = str(src).strip()
    tgt_clean = str(tgt).strip()
    env_str = str(env).strip() if env else ""
    
    pos_cls = 'medial'
    left_ctx = ''
    right_ctx = ''
    
    if '#_' in env_str or 'initial' in env_str.lower() or env_str.startswith('#'):
        pos_cls = '#_'
        left_ctx = '#'
    elif '_#' in env_str or 'final' in env_str.lower() or env_str.endswith('#'):
        pos_cls = '_#'
        right_ctx = '#'
    elif 'V_V' in env_str or 'intervocalic' in env_str.lower():
        pos_cls = 'V_V'
    
    insert_batch.append((
        src_clean, tgt_clean, left_ctx, right_ctx, pos_cls, '', lang, 0.0, 2000.0, 1000.0, 'diachronica'
    ))
    rule_count += 1

if insert_batch:
    p2_c.executemany("""
    INSERT INTO raw_transitions (
        source_seg, target_seg, left_context, right_context, position_class,
        concept, family, year_ancestor, year_descendant, time_delta, evidence_source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, insert_batch)
    p2_conn.commit()

p2_c.execute("CREATE INDEX IF NOT EXISTS idx_trans_src ON raw_transitions(source_seg)")
p2_c.execute("CREATE INDEX IF NOT EXISTS idx_trans_src_tgt ON raw_transitions(source_seg, target_seg)")
p2_c.execute("CREATE INDEX IF NOT EXISTS idx_trans_pos ON raw_transitions(position_class)")
p2_conn.commit()

print(f"Extracted {rule_count} transitions from diachronic rules.")

p2_c.execute("SELECT COUNT(*) FROM raw_transitions")
total_in_db = p2_c.fetchone()[0]
print(f"SUCCESS: Total transitions in raw_transitions: {total_in_db}")

p2_conn.close()
uni_conn.close()