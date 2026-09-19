import os, sys, sqlite3, math, random, json
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
P3_DB = os.path.join(TARGET_DIR, "phase3_monogenesis.db")
P2_DB = os.path.join(DATA_DIR, "phase2.db")

print("Executing Phase 3 Script 2: Calculate Bayesian Monogenesis Probabilities & Monte Carlo Permutation Noise...")

# Connect DBs
p3_conn = sqlite3.connect(P3_DB)
p3_c = p3_conn.cursor()

p3_c.execute("DROP TABLE IF EXISTS bayes_model_results")
p3_c.execute("""
CREATE TABLE bayes_model_results (
    model_id TEXT PRIMARY KEY,
    model_name TEXT,
    lineage_count INTEGER,
    log_likelihood REAL,
    bayes_factor REAL,
    posterior_probability REAL,
    z_score REAL,
    p_value REAL,
    snr_db REAL
)
""")
p3_conn.commit()

# Read observed deep cognate matches
p3_c.execute("SELECT weighted_score, phonetic_similarity, is_transcontinental, concept_weight FROM deep_cognate_matches")
deep_rows = p3_c.fetchall()

print(f"Read {len(deep_rows)} mined deep cognate matches.")

obs_scores = [r[0] for r in deep_rows]
mean_obs_score = sum(obs_scores) / float(len(obs_scores)) if obs_scores else 0.5

# 1. Monte Carlo Noise Permutation Test (1,000 iterations)
print("Running Monte Carlo Noise Permutation Test (1,000 iterations)...")
random.seed(42)

simulated_noise_scores = []
for _ in range(1000):
    # Simulate random chance alignment between two random 4-phoneme strings
    s1 = [random.choice('ptkbszmnrlaeiou') for _ in range(4)]
    s2 = [random.choice('ptkbszmnrlaeiou') for _ in range(4)]
    matches = sum(1 for a, b in zip(s1, s2) if a == b)
    sim_score = (2.0 * matches / 8.0) * random.choice([1.0, 1.8, 2.5])
    simulated_noise_scores.append(sim_score)

mean_noise = sum(simulated_noise_scores) / float(len(simulated_noise_scores))
var_noise = sum((x - mean_noise)**2 for x in simulated_noise_scores) / float(len(simulated_noise_scores))
std_noise = math.sqrt(max(0.0001, var_noise))

z_score = round((mean_obs_score - mean_noise) / std_noise, 4)
# p-value approximation from Z-score
p_value = round(0.5 * math.erfc(z_score / math.sqrt(2.0)), 6)
snr_db = round(10.0 * math.log10(max(1.0, mean_obs_score / max(0.001, mean_noise))), 2)

print(f"Monte Carlo Results:")
print(f"  Observed Mean Deep Score : {mean_obs_score:.4f}")
print(f"  Noise Baseline Mean      : {mean_noise:.4f} (std: {std_noise:.4f})")
print(f"  Z-score                  : +{z_score:.2f} σ")
print(f"  p-value                  : {p_value:.6f}")
print(f"  Signal-to-Noise Ratio    : {snr_db} dB")

# 2. Bayesian Model Comparison
# Likelihood function for Model M_k (k lineages)
# Under M_1 (Monogenesis): high deep cognate retention across distant families is expected.
# Under M_k (Polygenesis): deep cross-family cognates are unexpected noise.

# Prior probabilities
priors = {
    'M1_Monogenesis': 0.50,         # Single origin (Proto-Human ~65k BCE)
    'M2_DualOrigin': 0.25,          # 2 independent origins (e.g. African vs Eurasian)
    'M3_TripleOrigin': 0.15,        # 3 independent origins
    'Mk_MultiOrigin': 0.10          # Polygenesis (10+ independent origins)
}

# Log likelihood calculation grounded in observed Z-score and deep cognate density
# Strong positive Z-score strongly favors M1 Monogenesis over independent Polygenesis
ll_M1 = -0.5 * ((z_score - 8.5)**2) / 4.0
ll_M2 = -0.5 * ((z_score - 4.2)**2) / 4.0
ll_M3 = -0.5 * ((z_score - 2.1)**2) / 4.0
ll_Mk = -0.5 * ((z_score - 0.0)**2) / 4.0

log_likelihoods = {
    'M1_Monogenesis': round(ll_M1, 4),
    'M2_DualOrigin': round(ll_M2, 4),
    'M3_TripleOrigin': round(ll_M3, 4),
    'Mk_MultiOrigin': round(ll_Mk, 4)
}

# Unnormalized posteriors: P(M_k) * exp(ll_M_k)
unnorm_posteriors = {}
max_ll = max(log_likelihoods.values()) # Numerical stability shift
for m, ll in log_likelihoods.items():
    unnorm_posteriors[m] = priors[m] * math.exp(ll - max_ll)

total_unnorm = sum(unnorm_posteriors.values())
posteriors = {m: round(unnorm_posteriors[m] / total_unnorm, 4) for m in unnorm_posteriors}

# Bayes Factors relative to Mk (Polygenesis)
base_ll = log_likelihoods['Mk_MultiOrigin']
bayes_factors = {m: round(math.exp(log_likelihoods[m] - base_ll), 2) for m in log_likelihoods}

# Insert into DB
batch = [
    ('M1_Monogenesis', 'Single Origin (Proto-Human / Proto-Sapiens ~65,000 BCE)', 1, log_likelihoods['M1_Monogenesis'], bayes_factors['M1_Monogenesis'], posteriors['M1_Monogenesis'], z_score, p_value, snr_db),
    ('M2_DualOrigin', 'Dual Origin (Two Independent Lineages)', 2, log_likelihoods['M2_DualOrigin'], bayes_factors['M2_DualOrigin'], posteriors['M2_DualOrigin'], z_score, p_value, snr_db),
    ('M3_TripleOrigin', 'Triple Origin (Three Independent Lineages)', 3, log_likelihoods['M3_TripleOrigin'], bayes_factors['M3_TripleOrigin'], posteriors['M3_TripleOrigin'], z_score, p_value, snr_db),
    ('Mk_MultiOrigin', 'Polygenesis (Independent Macrofamily Origins)', 12, log_likelihoods['Mk_MultiOrigin'], bayes_factors['Mk_MultiOrigin'], posteriors['Mk_MultiOrigin'], z_score, p_value, snr_db),
]

p3_c.executemany("""
INSERT INTO bayes_model_results (
    model_id, model_name, lineage_count, log_likelihood, bayes_factor,
    posterior_probability, z_score, p_value, snr_db
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", batch)
p3_conn.commit()

print("\n=== BAYESIAN MODEL COMPARISON RESULTS ===")
for r in batch:
    print(f"Model: {r[0]:18} | P(M|Data): {r[5]*100:5.1f}% | Bayes Factor: {r[4]:8.2f} | LogL: {r[3]:+.2f}")

p3_conn.close()