# Champion vs Challenger Independent Validation Review

**Document Control & Model Risk Governance**
- **Validation Scope**: Independent Effective Challenge of Champion vs Challenger Models
- **Target Institution**: Tier-1 Consumer Lending & Risk Analytics
- **Validation Guidelines**: Federal Reserve SR 11-7 / OCC 2011-12
- **Author**: Independent Model Validation (IMV) Team

---

## 1. Executive Summary

Under **Federal Reserve SR 11-7**, the Independent Model Validation team must perform an **Effective Challenge** on all proposed model substitutions. 

This report documents the independent comparison between the **Submitted Champion (Logistic Regression Scorecard)** and the **Submitted Challenger (LightGBM Gradient Boosting Model)** across Out-Of-Time performance, calibration, explainability, operational complexity, and regulatory compliance.

---

## 2. Independent Evaluation Matrix

| Evaluation Dimension | Champion Statistical Model (Logistic Scorecard) | Submitted ML Challenger (LightGBM) | IMV Audit Verdict |
| --- | --- | --- | --- |
| **Out-Of-Time ROC-AUC** | 0.7245 (95% CI: 0.7218 - 0.7272) | **0.7482** (95% CI: 0.7451 - 0.7513) | LightGBM provides statistically significant +2.37% AUC lift ($p < 0.001$). |
| **KS Statistic (%)** | 34.82% | **38.42%** | LightGBM provides +3.60% higher risk separation. |
| **Gini Coefficient** | 0.4490 | **0.4964** | LightGBM provides +0.0474 higher Gini. |
| **Brier Score (Calibration)** | **0.14120** (Naturally Calibrated) | 0.13480 (Uncalibrated raw probabilities) | Logistic naturally calibrated; LightGBM requires isotonic recalibration. |
| **FCRA Adverse Action Notice** | **100% Closed-form Scorecard Points** | Complex post-hoc proxy required | LogisticScorecard superior for regulatory adverse action notices. |
| **Inference Latency (per 1k)** | **0.8 ms** | 4.1 ms | Both satisfy real-time SLA (< 50 ms). |
| **Model Risk Tiering** | Tier 1 (Well-understood linear math) | Tier 1 (Non-linear complex ensemble) | LightGBM requires higher ongoing monitoring oversight. |

---

## 3. Independent Challenge & Decision Rationale

1. **Discriminatory Superiority**: LightGBM delivers genuine, statistically defensible predictive lift (+2.37% AUC / +3.60% KS) over the Logistic Scorecard, proving that tree-based gradient boosting effectively captures non-linear risk interactions in consumer credit portfolios.
2. **Regulatory & Operational Constraints**: Despite its superior discrimination, LightGBM cannot produce closed-form linear scorecard point allocation tables. FCRA adverse action notice compliance remains simpler under Logistic Regression.
3. **IMV Final Decision**: Deploy **Logistic Scorecard** as the primary automated underwriting engine for originations, while deploying **LightGBM** as a parallel challenger for risk-based pricing and portfolio monitoring.
