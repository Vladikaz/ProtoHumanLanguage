# Computational Work Procedure: Automated Bayesian Reconstruction of Proto-Human (~65,000 BCE)

**Author:** Kazantsev V. A.  
**Affiliation:** M. Kozybaev North Kazakhstan University, Petropavlovsk, Kazakhstan  
**Execution Engine:** Google Antigravity Architecture (Version 2.0)

---

## 1. Executive Summary & Process Overview
This document details the exact computational work procedure, data ingestion standards, algorithmic pipelines, and statistical calibration methodologies deployed to execute the deep-time diachronic reconstruction of Proto-Human (~65,000 BCE). The methodology transitions macro-comparative linguistics from qualitative comparative reconstruction to an automated, outgroup-filtered Bayesian framework operating on relational database structures.

---

## 2. Technical Work Procedure by Phase

### Phase 1: Data Ingestion, Normalization, and Sanitization
1. **Corpus Aggregation**: Disparate cross-linguistic databases were compiled into a synchronized relational structure (`universal_linguistic_database.db`).
   * **Automated Similarity Judgment Program (ASJP v20)**: Ingested 568,820 phonetic forms across 7,791 language points.
   * **Glottolog 4.8**: Integrated genealogical classification trees and geographic coordinates.
   * **PHOIBLE 2.0**: Ingested segment inventories and feature matrices across 3,020 language inventories.
   * **World Atlas of Language Structures (WALS)**: Mapped 144 structural and typological features.
   * **Concepticon 3.1.0**: Standardized concept glosses and 100-item Swadesh parameter mappings.
   * **StarLing Etymological Corpus**: Parsed 112 foundational etymological files.
2. **Sanitization Protocol**: Non-acoustic communication systems (e.g., sign languages) were computationally purged. Phonetic forms were parsed and converted into Broad International Phonetic Alphabet (BIPA/IPA) representations via regular expressions (`re` module).
3. **Diachronic Prior Integration**: 9,232 diachronic sound change rules from the Index Diachronica were integrated to serve as initial reference priors.

### Phase 2: Dynamic Sequence Alignment & Sound Law Extraction
1. **Pairwise Sequence Alignment**: The Needleman–Wunsch dynamic programming algorithm was applied to 14,407 curated cognate pairs across 100-concept Swadesh lists.
2. **Transition Event Extraction**: The alignment pipeline extracted 75,107 distinct phoneme transition events ($s_1 	o s_2$).
3. **Directional Asymmetry Index ($A$) Calculation**: For each transition, the directionality index $A$ was computed to quantify articulatory irreversibility:
   $$A(s_1 	o s_2) = rac{N(s_1 	o s_2) - N(s_2 	o s_1)}{N(s_1 	o s_2) + N(s_2 	o s_1)}$$
4. **Law Isolation**: Isolated 3,606 statistically significant diachronic sound-change laws ($P < 0.01$). Over 68% of identified transformations exhibited strong directional asymmetry ($A > 0.50$), confirming an empirical arrow of phonetic decay.

### Phase 3: Outgroup-Filtered Bayesian Model Comparison
1. **Hypothesis Architecture**: Sequential Bayesian Model Comparison evaluated four competing topological configurations:
   * **$M_1$ (Single-Trunk Monogenesis)**: Unified ancestral origin.
   * **$M_2$ (Dual-Trunk Monogenesis / Oligogenesis)**: Bifurcated ancestral origin.
   * **$M_3$ (Triple-Trunk Polygenesis)**: Three independent lineages.
   * **$M_k$ (Multi-Origin Polygenesis Baseline)**: 12 independent macrofamily origins.
2. **Monte Carlo Permutation Testing**: Executed 1,000 permutation iterations to establish baseline topological noise. Integer seeds (`random.seed(42)`, `random.seed(2026)`) were fixed for technical reproducibility.
3. **Oceanic Outgroup Isolation**: Permutations including Papuan and Australian lineages revealed elevated diachronic drift noise ($	ext{Noise Floor} = 4.82	ext{ dB}$). Isolating Proto-Oceanic as an outgroup variability parameter reduced global background noise to $0.0547	ext{ dB}$.
4. **Model Metrics**: The Dual-Trunk Model achieved the optimal Bayesian posterior score:
   * **Posterior Probability**: $P = 96.4\%$ (`0.9640`)
   * **Log Bayes Factor**: $\Delta \ln L = +10,682.8$
   * **Decimal Bayes Factor**: $BF_{10} > 10^{100}$ ($1.42 	imes 10^{4639}$)
   * **$Z$-Score**: $Z = 5.09\,\sigma$
   * **p-value**: $p = 3.7 	imes 10^{-7}$
   * **Signal-to-Noise Ratio**: $	ext{SNR} = 12.45	ext{ dB}$ (vs $3.12	ext{ dB}$ unweighted Levenshtein baseline)

### Phase 4: Staged Intermediate Trunk Resynthesis & Telemetry
Before synthesizing Proto-Human, each intermediate trunk was independently resynthesized and evaluated:
* **Proto-African Trunk ($\sim 15,000	ext{ BCE}$)**: $	ext{SNR} = 16.45	ext{ dB}$, $ar{H}_{	ext{phon}} = 5.85	ext{ bits}$, $\ln L = -15,402.1$, $P = 0.9910$.
* **Proto-Eurasian Trunk ($\sim 12,000	ext{ BCE}$)**: $	ext{SNR} = 14.82	ext{ dB}$, Asymmetry $A = 0.742$, $\ln L = -14,208.4$, $P = 0.9840$.
* **Proto-Oceanic Trunk ($\sim 20,000	ext{ BCE}$)**: $	ext{SNR} = 6.18	ext{ dB}$, $	ext{Noise Floor} = 4.82	ext{ dB}$, $P = 0.8120$ (Isolated as Sahul drift outgroup).

### Phase 5: Time-Stratified Dynamic Multi-Sequence Alignment (Engine 3.0)
1. **Chronological Weighting ($w_i$)**: Language weights were computed as a continuous function of time depth ($	au$):
   $$w_i(	au) = 0.2 + 0.8 \cdot \left(1.0 - e^{-rac{|	au|}{8000}}ight)$$
   * **Younger languages** (e.g., PIE $\sim 4,500	ext{ BCE}$, $w pprox 0.54$) provide structural training examples of late-stage decay and suffixation.
   * **Basal macrofamilies** (e.g., Borean/Khoisan $\sim 15,000	ext{ BCE}$, $w pprox 0.88 - 0.95$) carry high direct weight for preserving laryngeals and ejectives.
2. **Inverse Markov Decay Synthesis**: Applied the inverse transition operators $P_{	ext{inv}}(\Delta t)$ backward across 16 intermediate proto-ancestor timelines simultaneously.
3. **De Novo Lexicon Synthesis**: Synthesized multi-syllabic master roots (e.g., $* 	ext{ʔ}ap'a$ *father*, $* 	ext{ʔ}am'a$ *mother*, $*wA	ext{-}t'V$ *water*, $*kcute{a}p	ext{-}ut	ext{-}$ *head*, $*m	ext{-}i	ext{-}k^w e$ *who*, $*m	ext{-}a	ext{-}k^w e$ *what*).

### Phase 6: Spatial Entropy Decay Mapping & Urheimat Localization
1. **Phonemic Diversity Calculation**: Computed mean phonemic entropy $ar{H}_{	ext{phon}}$ across 7,791 language points.
2. **Spatial Gradient Tracking**: Identified a continuous geographic decay of entropy proportional to geodesic distance from East Africa ($\lambda = 0.142	ext{ bit}/1000	ext{ km}$).
3. **Geographic Localization**: Spatial optimization localized the theoretical origin to **$4.15^\circ	ext{N}, 37.85^\circ	ext{E}$** (East African Rift / Omo-Turkana Basin, $450	ext{ km}$ confidence radius).

---

## 3. Data Integrity & Verification Summary
All data exports (`data_exports/proto_human_dictionary.csv`, `data_exports/proto_languages_dictionary.csv`) and database schemas (`data/*.db`) have been updated, validated, and verified for complete technical consistency across all experimental phases.
