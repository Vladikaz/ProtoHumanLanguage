import os, sys, sqlite3, math, random
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
SCRIPTS_DIR = os.path.join(TARGET_DIR, "scripts")
os.makedirs(SCRIPTS_DIR, exist_ok=True)

P5_DB = os.path.join(TARGET_DIR, "phase5_proto_human.db")
P4_DB = os.path.join(DATA_DIR, "phase4_proto_languages.db")

print("Executing Phase 5 Script 1: Dual-Trunk (African + Eurasian) Bayesian Monogenesis Probability Engine...")

p5_conn = sqlite3.connect(P5_DB)
p5_c = p5_conn.cursor()

p5_c.execute("DROP TABLE IF EXISTS proto_human_bayes_result")
p5_c.execute("""
CREATE TABLE proto_human_bayes_result (
    hypothesis TEXT PRIMARY KEY,
    description TEXT,
    posterior_probability REAL,
    bayes_factor REAL,
    z_score REAL,
    p_value REAL,
    snr_db REAL,
    time_depth_bce REAL
)
""")
p5_conn.commit()

p4_conn = sqlite3.connect(P4_DB)
p4_c = p4_conn.cursor()

p4_c.execute("SELECT concept, cluster_id, reconstructed_proto_form FROM reconstructed_lexicon")
rows = p4_c.fetchall()

lex_african = {}
lex_eurasian = {}

for concept, cid, form in rows:
    clean_f = form.replace('*', '').strip()
    if cid == 'branch_african':
        lex_african[concept] = clean_f
    elif cid == 'branch_eurasian':
        lex_eurasian[concept] = clean_f

shared = set(lex_african.keys()).intersection(lex_eurasian.keys())

def phon_sim_core(s1, s2):
    if not s1 or not s2: return 0.0
    if s1 == s2: return 1.0
    c1 = [ch for ch in s1 if ch not in 'aeiouyØø']
    c2 = [ch for ch in s2 if ch not in 'aeiouyØø']
    if not c1 or not c2:
        return 0.55 if s1[0] == s2[0] else 0.25
    
    inter = len(set(c1).intersection(set(c2)))
    union = len(set(c1).union(set(c2)))
    sim = inter / float(union) if union > 0 else 0.0
    if s1[0] == s2[0]:
        sim = min(1.0, sim + 0.40)
    return round(sim, 4)

sims = []
for cname in shared:
    fa = lex_african[cname]
    fe = lex_eurasian[cname]
    sim = phon_sim_core(fa, fe)
    sims.append(sim)

mean_sim = sum(sims) / float(len(sims))

random.seed(2026)
noise_sims = []
for _ in range(1000):
    s1 = random.choice(list(lex_african.values()))
    s2 = random.choice(list(lex_eurasian.values()))
    sim = phon_sim_core(s1, s2)
    noise_sims.append(sim)

mean_noise = sum(noise_sims) / float(len(noise_sims))
var_noise = sum((x - mean_noise)**2 for x in noise_sims) / float(len(noise_sims))
std_noise = math.sqrt(max(0.0001, var_noise))

z_score = round((mean_sim - mean_noise) / std_noise, 4)
p_val = round(0.5 * math.erfc(z_score / math.sqrt(2.0)), 8)
snr_db = round(10.0 * math.log10(mean_sim / max(0.001, mean_noise)), 2)

prior = 0.70
ll_mono = -0.5 * ((z_score - 4.8)**2) / 4.0
ll_poly = -0.5 * ((z_score - 0.0)**2) / 4.0
bf = round(math.exp(ll_mono - ll_poly), 2)
post = round((prior * math.exp(ll_mono)) / (prior * math.exp(ll_mono) + (1-prior) * math.exp(ll_poly)), 4)

print("\n=== DUAL-TRUNK (AFRICAN vs EURASIAN) BAYESIAN SYNTHESIS ===")
print(f"Shared Concepts Evaluated             : {len(shared)}")
print(f"Observed African-Eurasian Stem Sim    : {mean_sim:.4f}")
print(f"Monte Carlo Noise Baseline Mean       : {mean_noise:.4f} (std: {std_noise:.4f})")
print(f"Z-Score                               : +{z_score:.2f} σ")
print(f"p-value                               : {p_val:.8f}")
print(f"Signal-to-Noise Ratio (SNR)           : {snr_db:.2f} dB")
print(f"Bayes Factor (BF)                     : {bf:.2f}")
print(f"Posterior P(Proto-Human Monogenesis)   : {post*100:.1f}%")

p5_c.execute("""
INSERT INTO proto_human_bayes_result (
    hypothesis, description, posterior_probability, bayes_factor,
    z_score, p_value, snr_db, time_depth_bce
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'Dual_Trunk_Proto_Human_Monogenesis',
    'Dual-Trunk Synthesis (African Proto-Sapiens + Eurasian Proto-Sapiens -> Proto-Human ~65,000 BCE)',
    post, bf, z_score, p_val, snr_db, -65000.0
))
p5_conn.commit()

p5_conn.close()
p4_conn.close()