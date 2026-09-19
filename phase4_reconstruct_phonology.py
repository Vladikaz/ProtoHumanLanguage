import os, sys, sqlite3, json
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
P4_DB = os.path.join(TARGET_DIR, "phase4_proto_languages.db")

print("Executing Phase 4 Script 2: Reconstruct Ancestral Proto-Phonology Systems...")

conn = sqlite3.connect(P4_DB)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS proto_phonology")
c.execute("""
CREATE TABLE proto_phonology (
    cluster_id TEXT PRIMARY KEY,
    branch_name TEXT,
    consonant_inventory TEXT,
    vowel_inventory TEXT,
    suprasegmental_features TEXT,
    total_phoneme_count INTEGER,
    articulatory_description TEXT
)
""")
conn.commit()

# Reconstructed Phonological Systems based on Proto-Node Evidence + Phase 2 Reversals
phonology_data = [
    (
        'branch_african',
        'Proto-Sapiens Africanus (Праафриканский ярус)',
        json.dumps(['*p', '*t', '*k', '*q', '*b', '*d', '*g', '*p\'', '*t\'', '*k\'', '*s', '*z', '*x', '*h', '*m', '*n', '*ŋ', '*r', '*l', '*w', '*j', '*ʘ', '*ǀ', '*ǃ', '*ǂ', '*ǁ'], ensure_ascii=False),
        json.dumps(['*a', '*e', '*i', '*o', '*u', '*aː', '*eː', '*iː', '*oː', '*uː', '*ã', '*ĩ', '*ũ'], ensure_ascii=False),
        json.dumps(['Tone: High / Low contrastive tone', 'Stress: Initial syllable accent'], ensure_ascii=False),
        39,
        'Rich consonantal system featuring ejectives (p\', t\', k\'), glottalized stops, and ancestral click series (ʘ, ǀ, ǃ, ǂ, ǁ) retained in Khoisan/Southern African lineages. Contrastive vowel length and 2-level tone system.'
    ),
    (
        'branch_eurasian',
        'Proto-Sapiens Eurasiaticus / Borean (Праевразийский / Борейский ярус)',
        json.dumps(['*p', '*t', '*k', '*q', '*b', '*d', '*g', '*gʷ', '*pʰ', '*tʰ', '*kʰ', '*p\'', '*t\'', '*k\'', '*q\'', '*s', '*z', '*ʃ', '*ʒ', '*x', '*ɣ', '*h', '*m', '*n', '*ŋ', '*r', '*l', '*w', '*j'], ensure_ascii=False),
        json.dumps(['*a', '*e', '*i', '*o', '*u', '*ɨ', '*ə', '*aː', '*eː', '*iː', '*oː', '*uː'], ensure_ascii=False),
        json.dumps(['Stress: Pitch-accent / Dynamic pitch accent', 'Syllable Structure: (C)V(C) with initial consonant clusters'], ensure_ascii=False),
        41,
        'Complex plosive contrast (voiceless *p *t *k, voiced *b *d *g, aspirated *pʰ *tʰ *kʰ, ejective *p\' *t\' *k\'). Features labialized velars (*gʷ), palatal/postalveolar fricatives (*ʃ *ʒ), and 7-vowel system (*a *e *i *o *u *ɨ *ə).'
    ),
    (
        'branch_oceanic_amerind',
        'Proto-Sapiens Oceanicus & Americanus (Праокеанический / Праамериндский ярус)',
        json.dumps(['*p', '*t', '*k', '*ʔ', '*b', '*d', '*g', '*s', '*h', '*m', '*n', '*ŋ', '*ɲ', '*r', '*l', '*w', '*j'], ensure_ascii=False),
        json.dumps(['*a', '*e', '*i', '*o', '*u', '*aː', '*iː', '*uː'], ensure_ascii=False),
        json.dumps(['Syllable Structure: Strictly open syllables (CV)', 'Stress: Penultimate accent'], ensure_ascii=False),
        25,
        'Symmetrical, open-syllable phonology. Minimal consonant inventory (stops *p *t *k *b *d *g *ʔ, nasals *m *n *ŋ *ɲ, liquids *r *l, glides *w *j) and classic 5-vowel system (*a *e *i *o *u). High stability of glottal stop *ʔ.'
    )
]

c.executemany("""
INSERT INTO proto_phonology (
    cluster_id, branch_name, consonant_inventory, vowel_inventory,
    suprasegmental_features, total_phoneme_count, articulatory_description
) VALUES (?, ?, ?, ?, ?, ?, ?)
""", phonology_data)
conn.commit()

print("\n=== RECONSTRUCTED ANCESTRAL PHONOLOGY INVENTORIES ===")
for r in phonology_data:
    cons = json.loads(r[2])
    vows = json.loads(r[3])
    print(f"[{r[0]:22}] -> Consonants ({len(cons)}): {', '.join(cons[:12])}...")
    print(f"                        Vowels ({len(vows)}):     {', '.join(vows[:8])}...")
    print(f"                        Total Phonemes: {r[5]}\n")

conn.close()
print("SUCCESS: Script 2 complete.")