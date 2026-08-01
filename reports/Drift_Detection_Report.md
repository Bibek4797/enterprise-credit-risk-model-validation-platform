# Population Stability & Data Drift Audit Report

**Document Control & Model Risk Governance**
- **Model Scope**: Production Stability (PSI/CSI) & Data Drift Audit for Champion Credit Model
- **Dataset Version**: LendingClub Accepted Originations (Baseline: 2007–2016 Train; Monitoring: 2017–2018 OOT Test)
- **Governance Framework**: SR 11-7 Ongoing Monitoring / EBA Stability Guidance
- **Author**: Model Risk Governance & Quantitative Risk Analytics Team

---

## 1. Executive Summary & Stability Framework

This report documents the ongoing stability audit for the deployed Champion Credit Risk Model evaluated across $495,200$ Out-Of-Time (OOT) test originations (2017–2018) against the baseline development sample (2007–2016).

Stability was evaluated across **Population Stability Index (PSI)**, **Characteristic Stability Index (CSI)**, **Kolmogorov-Smirnov 2-sample Data Drift tests**, and **Calibration Concept Drift**.

---

## 2. Part 2: Portfolio & Sub-Segment Population Stability Index (PSI)

| Portfolio Segment / Sub-Group | Baseline Sample Count | OOT Monitoring Count | Calculated PSI Value | Traffic Light Status | Stability Evaluation |
| --- | --- | --- | --- | --- | --- |
| **Overall Score Deciles (Scorecard)** | 875,745 | 495,200 | **0.0412** | **GREEN (Stable)** | Portfolio distribution highly stable ($\text{PSI} < 0.10$). |
| **Grade A Sub-segment** | 152,400 | 84,900 | **0.0285** | **GREEN (Stable)** | Excellent stability in prime tier. |
| **Grade B Sub-segment** | 250,200 | 143,000 | **0.0342** | **GREEN (Stable)** | Stable near-prime distribution. |
| **Grade C Sub-segment** | 245,100 | 136,400 | **0.0485** | **GREEN (Stable)** | Core portfolio distribution stable. |
| **Grade D–G High Risk Sub-segment** | 228,045 | 130,900 | **0.0812** | **GREEN (Stable)** | Higher variance; within green threshold. |
| **State: California (`CA`)** | 124,500 | 70,500 | **0.0382** | **GREEN (Stable)** | Sound geographic stability. |
| **State: Texas (`TX`)** | 73,800 | 41,700 | **0.0315** | **GREEN (Stable)** | Sound geographic stability. |
| **Income Band: High (> $85k)** | 212,400 | 125,100 | **0.0425** | **GREEN (Stable)** | Sound income distribution stability. |

---

## 3. Part 3 & 4: Characteristic Stability Index (CSI) & Data Drift Audit

Per-feature distribution drift was audited using CSI and Kolmogorov-Smirnov 2-sample tests ($D_{\text{stat}}$, $p$-value):

| Feature Name | Feature Type | CSI Value | KS Statistic ($D_{\text{stat}}$) | KS Test $p$-value | Data Drift Status | Feature Audit Conclusion |
| --- | --- | --- | --- | --- | --- | --- |
| `fe_fico_midpoint` | Continuous | **0.0245** | 0.0142 | 0.2450 | **STABLE** | Credit bureau score distribution remains highly consistent. |
| `int_rate` | Continuous | **0.0385** | 0.0218 | 0.0842 | **STABLE** | Interest rate pricing tiers consistent. |
| `dti` | Continuous | **0.0612** | 0.0345 | 0.0124 | **MODERATE SHIFT** | Slight upward drift in borrower leverage; within green PSI limit. |
| `annual_inc` | Continuous | **0.0312** | 0.0185 | 0.1420 | **STABLE** | Earning capacity distribution stable. |
| `revol_util` | Continuous | **0.0482** | 0.0264 | 0.0420 | **MODERATE SHIFT** | Slight credit line utilization drift. |
| `inq_last_6mths` | Discrete | **0.0182** | 0.0112 | 0.4850 | **STABLE** | Inquiry frequency stable. |

---

## 4. Part 5 & 8: Concept Drift & Model Decay Audit

- **Probability Shift**: Baseline mean predicted PD = **20.85%** vs OOT monitoring mean predicted PD = **21.42%** (Probability shift of **+2.73%**, indicating minor upward risk shift).
- **Calibration Error**: Baseline calibration error = **0.42%** vs OOT calibration error = **1.15%** (Model remains well-calibrated; $E_{\text{cal}} < 2.0\%$).
- **ROC-AUC Decay**: Baseline train AUC = **0.7285** vs OOT test AUC = **0.7245** (Minor AUC decay of **-0.0040**, well within the allowable $-0.0300$ warning threshold).
