# Dataset Limitations & Institutional Banking Reality Report

**Document Control & Model Risk Governance**
- **Dataset Scope**: LendingClub Accepted Consumer Loan Originations (2007–2018 Q4, $N = 1,370,945$ mature loans)
- **Target Audience**: Model Risk Management (MRM), Model Risk Committee (MRC), Independent Validators, Regulators
- **Author**: Quantitative Risk Analytics & Model Risk Governance Team

---

## 1. Executive Overview & Scope Statement

This document provides a candid, transparent evaluation of what the public LendingClub dataset can empirically support, what it cannot support, which analytical components represent approximations, and what additional data structures would be required for full production deployment within a Tier-1 financial institution.

Adhering to **Federal Reserve SR 11-7** guidelines, model validators must distinguish between genuine empirical findings and dataset-imposed approximations to prevent false precision or unsupported regulatory claims.

---

## 2. Capability Matrix: Supported vs. Unsupported Analyses

| Analytical Workstream | LendingClub Dataset Support Level | Technical & Econometric Rationale | Real Banking Data Requirement for Production |
| --- | --- | --- | --- |
| **Binary PD Underwriting Modelling** | **Fully Supported** | $1.37\text{M}$ mature binary outcomes (`Charged Off` vs `Fully Paid`) provide sufficient statistical power for WoE/IV, Logit, LightGBM, and ROC-AUC evaluation. | Production loan origination application data. |
| **FCRA Adverse Action Reason Generation** | **Fully Supported** | Closed-form score point additivity derived from WoE coefficients enables exact ranking of negative point deductions. | Standard credit bureau inquiry & applicant attribute feeds. |
| **Population Stability Index (PSI)** | **Fully Supported** | Out-of-Time (OOT) temporal split across origination years (2007–2016 Dev vs 2017–2018 Test) enables decile-level PSI and CSI tracking. | Monthly production scoring snapshots. |
| **ECOA Fair Lending Disparate Impact** | **Supported with Approximations** | Demographic attributes (race, gender) are excluded; income tier proxies are used for Disparate Impact Ratio ($\text{DIR}$) audits. | Anonymized HMDA / CFPB demographic benchmark data. |
| **Loss Given Default (LGD) Modelling** | **Approximated (Static 95.0%)** | LendingClub provides post-default recovery amounts ($6.97\%$ mean recovery), but lacks collateral appraisals or workout timeline panels. | Borrower-level recovery panels, collateral valuations, and workout cost data. |
| **IFRS 9 / CECL Multi-State Staging** | **Unsupported (Approximated)** | Dataset lacks monthly multi-year panel tracking of individual loans moving between 0, 30, 60, 90 DPD buckets over time. | Monthly loan-level repayment history panel tables. |
| **Macroeconomic VAR Stress Testing** | **Approximated (Feature Shocks)** | Origination records contain macro proxy features (`annual_inc`, `int_rate`), but lack dynamic regional macro time series linkage. | Federal Reserve CCAR / DAST macroeconomic scenario series (GDP, Unemployment, HPI). |

---

## 3. Explicit Dataset Limitations & Approximations

1. **Uncollateralized Personal Loan Bias**: LendingClub origination data reflects uncollateralized peer-to-peer consumer loans. Findings cannot be generalized to mortgages, auto loans, or commercial credit.
2. **Self-Reported Income**: Applicant income (`annual_inc`) is self-reported at origination and may contain unverified income noise, unlike verified bank paystubs or tax returns.
3. **Absence of Credit Bureau Panel Data**: The dataset provides static snapshots at origination rather than dynamic monthly credit bureau bureau-pull panel updates (e.g., FICO trend over 24 months).
4. **Static LGD Assumption**: In the absence of collateral workout timelines, LGD is modeled as a static $95.0\%$ parameter ($\text{Recovery Rate} = 6.97\%$).

---

## 4. Production Deployment Prerequisites in a Tier-1 Bank

To transition this platform from a benchmark prototype to a Tier-1 production credit engine:
- **Data Pipeline**: Connect feature engineering modules to an enterprise Data Lake / Snowflake warehouse via an automated Feature Store (Feast).
- **Bureau Integration**: Integrate real-time Equifax / Experian / TransUnion API feeds for automated credit score pulling.
- **Dynamic LGD & EAD Engines**: Replace static LGD with a two-stage fractional logit or beta regression LGD model trained on internal recovery workout data.
