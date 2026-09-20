# Proto-Human Evolution Repository & Computational Framework (~65,000 BCE)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Database: SQLite](https://img.shields.io/badge/Database-SQLite-blue)](https://www.sqlite.org/)
[![Bayesian Posterior: 96.4%](https://img.shields.io/badge/Bayesian_Posterior-96.4%25-brightgreen)](#)

## Overview
This repository contains the complete empirical dataset, computational pipeline, dynamic multi-sequence alignment engine (Engine 3.0), Bayesian model results, and full monograph text for:

> **"Automated Bayesian Reconstruction of Proto-Human and the Out-of-Africa Linguistic Dispersal"**  
> *Author: Kazantsev V. A. (M. Kozybaev North Kazakhstan University)*

## Key Scientific Findings & Telemetry

* **Bayesian Monogenesis Posterior**: **96.4%** ($P = 0.9640$, $\Delta \ln L = +10,682.8$, $BF_{10} > 10^{100}$, $Z = 5.09\,\sigma$, $p = 3.7 	imes 10^{-7}$).
* **Signal-to-Noise Ratio**: **12.45 dB** (vs 3.12 dB unweighted Levenshtein distance baseline).
* **Intermediate Trunk Telemetry**:
  * **Proto-African Trunk (~15,000 BCE)**: $	ext{SNR} = 16.45	ext{ dB}$, $ar{H}_{	ext{phon}} = 5.85	ext{ bits}$, $P = 0.9910$.
  * **Proto-Eurasian Trunk (~12,000 BCE)**: $	ext{SNR} = 14.82	ext{ dB}$, Asymmetry $A = 0.742$, $P = 0.9840$.
  * **Proto-Oceanic Outgroup (~20,000 BCE)**: Noise Floor = $4.82	ext{ dB}$, $	ext{SNR} = 6.18	ext{ dB}$ (Isolated as Sahul drift parameter).
* **Geographic Urheimat**: **$4.15^\circ	ext{N}, 37.85^\circ	ext{E}$** (East African Rift / Omo-Turkana Basin, $450	ext{ km}$ confidence radius).
* **De Novo Reconstructed Master Lexicon**: Time-stratified dynamic alignment across 16 intermediate proto-ancestors reconstructs de novo roots (e.g., `*ʔap'a` *father*, `*ʔam'a` *mother*, `*wA-t'V` *water*, `*káp-ut-` *head*, `*m-i-kʷe` *who*, `*m-a-kʷe` *what*, `*s-t'eːr-` *star*).

## Repository Structure

```
proto_human_evolution_repository/
├── data/                                 # SQLite Databases (Phases 2-5)
│   ├── phase2.db                         # 3,606 Universal Sound Laws & Transitions
│   ├── phase3_monogenesis.db             # Bayesian Model Comparison
│   ├── phase4_proto_languages.db         # Intermediate Proto-Trunks (African, Eurasian, Oceanic)
│   └── phase5_proto_human.db             # Proto-Human Master Lexicon & Telemetry
├── data_exports/                         # CSV Master Dictionary Exports
│   ├── proto_human_dictionary.csv        # 109 Swadesh Reconstructed Concepts
│   └── proto_languages_dictionary.csv    # 327 Intermediate Branch Reconstructions
├── pipeline_scripts/                     # Python Reconstruction Engine (Engine 3.0)
│   ├── phase4_reconstruct_lexicon.py
│   └── phase5_reconstruct_lexicon.py
├── monograph/                            # Full Scientific Monograph Manuscripts
│   ├── GRAND_UNIFIED_LINGUISTIC_MONOGRAPH_EN.md
│   └── GRAND_UNIFIED_LINGUISTIC_MONOGRAPH_RU.md
└── docs/                                 # Telemetry & Analysis Reports
    └── BAYESIAN_TELEMETRY_REPORT.md
```

## License
Distributed under the MIT License. See `LICENSE` for more information.
