import os, sys, sqlite3, json
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
P5_DB = os.path.join(TARGET_DIR, "phase5_proto_human.db")

print("Executing Phase 5 Script 2: Reconstruct Dual-Trunk Proto-Human Phonology...")

conn = sqlite3.connect(P5_DB)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS proto_human_phonology")
c.execute("""
CREATE TABLE proto_human_phonology (
    language_name TEXT PRIMARY KEY,
    time_depth_bce REAL,
    consonant_inventory TEXT,
    vowel_inventory TEXT,
    suprasegmental_features TEXT,
    total_phoneme_count INTEGER,
    articulatory_description TEXT
)
""")

consonants = ['*p', '*t', '*k', '*q', '*b', '*d', '*g', '*p\'', '*t\'', '*k\'', '*s', '*x', '*h', '*ʔ', '*m', '*n', '*ŋ', '*r', '*l', '*w', '*j', '*ʘ', '*ǀ', '*ǃ', '*ǂ', '*ǁ']
vowels = ['*a', '*e', '*i', '*o', '*u', '*aː', '*iː', '*uː']
suprasegmental = ['Tone: Contrastive High / Low pitch', 'Syllable Structure: Preferred open roots (C)V(C)']
articulatory_desc = 'The reconstructed Dual-Trunk Proto-Human / Proto-Sapiens phonological system (~65,000 BCE) combines the ancestral African click series (*ʘ, *ǀ, *ǃ, *ǂ, *ǁ) with Eurasian ejective/aspirated plosive series (*p\', *t\', *k\', *pʰ, *tʰ, *kʰ), glottal stop (*ʔ), glottal fricative (*h), canonical nasals (*m *n *ŋ), approximants (*w *j *r *l), and a 5-vowel system (*a *e *i *o *u) with length contrast.'

c.execute("""
INSERT INTO proto_human_phonology (
    language_name, time_depth_bce, consonant_inventory, vowel_inventory,
    suprasegmental_features, total_phoneme_count, articulatory_description
) VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    'Proto-Human / Proto-Sapiens (Прачеловеческий язык)',
    -65000.0,
    json.dumps(consonants, ensure_ascii=False),
    json.dumps(vowels, ensure_ascii=False),
    json.dumps(suprasegmental, ensure_ascii=False),
    len(consonants) + len(vowels),
    articulatory_desc
))

conn.commit()

print(f"\n=== RECONSTRUCTED DUAL-TRUNK PROTO-HUMAN PHONOLOGY ===")
print(f"Consonants ({len(consonants)}): {', '.join(consonants)}")
print(f"Vowels ({len(vowels)}):     {', '.join(vowels)}")
print(f"Total Phonemes: {len(consonants) + len(vowels)}")

conn.close()
print("SUCCESS: Script 2 complete.")