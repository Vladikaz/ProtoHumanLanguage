import os, sys, sqlite3, re
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
SCRIPTS_DIR = os.path.join(TARGET_DIR, "scripts")
os.makedirs(SCRIPTS_DIR, exist_ok=True)

P4_DB = os.path.join(TARGET_DIR, "phase4_proto_languages.db")
UNI_DB = os.path.join(DATA_DIR, "universal_linguistic_database.db")

print("Executing Phase 4 Script 1: Cluster Proto-Language Ancestral Branches...")

p4_conn = sqlite3.connect(P4_DB)
p4_c = p4_conn.cursor()

p4_c.execute("DROP TABLE IF EXISTS ancestral_clusters")
p4_c.execute("""
CREATE TABLE ancestral_clusters (
    cluster_id TEXT PRIMARY KEY,
    branch_name TEXT,
    description TEXT,
    proto_languages_count INTEGER,
    top_proto_languages TEXT
)
""")

p4_c.execute("DROP TABLE IF EXISTS proto_language_members")
p4_c.execute("""
CREATE TABLE proto_language_members (
    lang_name TEXT PRIMARY KEY,
    cluster_id TEXT,
    family TEXT,
    year_bce REAL,
    vocab_size INTEGER
)
""")
p4_conn.commit()

uni_conn = sqlite3.connect(UNI_DB)
uni_c = uni_conn.cursor()

uni_c.execute("PRAGMA table_info(languages_database)")
cols = [c[1] for c in uni_c.fetchall()]
concept_cols = cols[9:]

uni_c.execute("SELECT * FROM languages_database")
db_rows = uni_c.fetchall()

proto_langs = []
for r in db_rows:
    name = r[0]
    fam = r[1]
    period = r[2]
    
    is_p = any(k in name.lower() for k in ['пра', 'proto', 'ancient', 'древн', 'борей', 'нострат', 'сино-кавказ'])
    if not is_p and period and ('до н.э' in period.lower() or 'bce' in period.lower()):
        is_p = True
        
    if is_p:
        vocab = {}
        for idx, cname in enumerate(concept_cols):
            val = r[9 + idx]
            if val and str(val).strip() not in ('—', '-', '?', 'None', ''):
                vocab[cname] = str(val).strip()
        proto_langs.append((name, fam, period, vocab))

clusters_def = {
    'branch_african': {
        'name': 'Proto-Sapiens Africanus (Праафриканский ярус)',
        'desc': 'Ancestral radiation of African macrofamilies (Afroasiatic, Niger-Congo, Nilo-Saharan, Khoisan).',
        'members': []
    },
    'branch_eurasian': {
        'name': 'Proto-Sapiens Eurasiaticus / Borean (Праевразийский / Борейский ярус)',
        'desc': 'Ancestral radiation of Eurasian macrofamilies (Indo-European, Uralic, Turkic/Altaic, Kartvelian, Dravidian, Sino-Caucasian, Yeniseian).',
        'members': []
    },
    'branch_oceanic_amerind': {
        'name': 'Proto-Sapiens Oceanicus & Americanus (Праокеанический / Праамериндский ярус)',
        'desc': 'Ancestral radiation of Pacific, Australian, Papuan, and Native American macrofamilies (Austronesian, Trans-New Guinea, Pama-Nyungan, Amerind).',
        'members': []
    }
}

member_batch = []
for name, fam, period, vocab in proto_langs:
    nf = (name + " " + fam).lower()
    
    if any(k in nf for k in ['афрази', 'afroas', 'семит', 'semit', 'кушит', 'cushit', 'чад', 'chadic', 'бербер', 'berber', 'нигер', 'niger', 'нил', 'nilo', 'койсан', 'khois', 'khoe', 'туа', 'ju', 'wi']):
        c_id = 'branch_african'
    elif any(k in nf for k in ['австрон', 'austron', 'папуас', 'papua', 'пама', 'pama', 'австрал', 'austral', 'дене', 'dene', 'навахо', 'на-дене', 'майя', 'mayan', 'астек', 'aztec', 'кечуа', 'quechua', 'тупи', 'tupi', 'америнд', 'amerind', 'cahuap', 'jabuti']):
        c_id = 'branch_oceanic_amerind'
    else:
        c_id = 'branch_eurasian'
        
    clusters_def[c_id]['members'].append(name)
    member_batch.append((name, c_id, fam, -3000.0, len(vocab)))

p4_c.executemany("INSERT INTO proto_language_members (lang_name, cluster_id, family, year_bce, vocab_size) VALUES (?, ?, ?, ?, ?)", member_batch)

cluster_batch = []
for cid, info in clusters_def.items():
    top_m = ", ".join(info['members'][:10])
    cluster_batch.append((cid, info['name'], info['desc'], len(info['members']), top_m))

p4_c.executemany("INSERT INTO ancestral_clusters (cluster_id, branch_name, description, proto_languages_count, top_proto_languages) VALUES (?, ?, ?, ?, ?)", cluster_batch)
p4_conn.commit()

print("\n=== ANCESTRAL PROTO-LANGUAGE BRANCH CLUSTERS ===")
for cid, name, desc, cnt, top_m in cluster_batch:
    print(f"[{cid:22}] -> {name:60} | Proto-Langs: {cnt:3}")
    print(f"     Members: {top_m}\n")

p4_conn.close()
uni_conn.close()