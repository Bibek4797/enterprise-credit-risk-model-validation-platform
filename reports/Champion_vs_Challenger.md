# Champion vs Challenger Governance & Recommendation Report

**Document Control & Model Risk Governance**
- **Model Scope**: Champion (Statistical) vs Challenger (Machine Learning) Selection Audit
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary development records)
- **Regulatory Framework**: Federal Reserve SR 11-7 / OCC 2011-12, Basel III EBA Guidelines, IFRS 9 ECL
- **Author**: Quantitative Risk Analytics & Independent Model Validation Team

---

## 1. Executive Summary & Governance Objective

Model risk governance under **Federal Reserve SR 11-7** requires that any new machine learning model ("Challenger") proposing to replace an established statistical baseline ("Champion") must undergo a rigorous **Effective Challenge**. 

This report benchmarks the **Phase 8 Champion Statistical Model (Logistic Regression Scorecard)** against the **Phase 9 Machine Learning Suite** across five critical banking dimensions:
1. **Predictive Performance** (ROC-AUC, Gini, KS %, MCC)
2. **Calibration & Probability Realism** (Brier Score, Hosmer-Lemeshow Test)
3. **Model Interpretability & Auditability** (Scorecard Points vs SHAP values)
4. **Regulatory & Fair Lending Compliance** (FCRA / SR 11-7 transparency)
5. **Operational Complexity & Deployment Readiness**

---

## 2. Master Champion vs Challenger Comparison Matrix

| Evaluation Dimension | Champion Statistical Model (Logistic Scorecard) | Recommended ML Challenger (LightGBM) | Random Forest | XGBoost | Decision Tree |
| --- | --- | --- | --- | --- | --- |
| **Out-Of-Time ROC-AUC** | 0.7245 | **0.7482** (+2.37%) | 0.7385 (+1.40%) | 0.7476 (+2.31%) | 0.6985 (-2.60%) |
| **Gini Coefficient ($2\text{AUC}-1$)** | 0.4490 | **0.4964** (+0.0474) | 0.4770 | 0.4952 | 0.3970 |
| **KS Separation (%)** | 34.82% | **38.42%** (+3.60%) | 36.85% | 38.15% | 30.12% |
| **Brier Score** | 0.14120 | **0.13480** (Better) | 0.13840 | 0.13520 | 0.14850 |
| **Matthews Corr Coef (MCC)** | 0.3125 | **0.3540** | 0.3340 | 0.3510 | 0.2740 |
| **Interpretability Format** | **1,000-Point Linear Scorecard** ($\text{OR} = e^\beta$) | SHAP / Feature Importances | Tree Gini Importance | SHAP / Feature Importances | Visual Decision Rules |
| **Regulatory Auditability** | **Seamless**: Direct mathematical equation. | **Complex**: Requires SHAP proxy explanations. | Moderate | Complex | High |
| **Inference Latency (per 1k)** | **0.8 ms** | 4.1 ms | 18.5 ms | 8.4 ms | 1.2 ms |
| **Calibration Reliability** | **Passed** (HL $p = 0.142$) | Requires Isotonic Recalibration | Moderate | Passed (HL $p = 0.112$) | Poor |

---

## 3. Detailed Trade-off & Effective Challenge Analysis

### 3.1 Predictive Discrimination Lift (+2.37% AUC / +3.60% KS)
- LightGBM achieves a **+2.37% ROC-AUC lift** (0.7482 vs 0.7245) and a **+3.60% KS lift** (38.42% vs 34.82%) over the Logistic Scorecard.
- **Financial Value**: In a $10 Billion loan portfolio with a 21.3% baseline default rate, a +3.60% KS improvement translates into approximately **$35 Million in annual bad debt reduction** via improved risk tiering.

### 3.2 Explainability & Regulatory Compliance (FCRA / Adverse Action)
- **Logistic Scorecard**: Automatically generates exact reason codes for adverse action notices (e.g. "DTI ratio too high", "FICO score below threshold") directly from scorecard points deduction.
- **LightGBM**: Black-box gradient boosting tree structures cannot produce exact linear points. Adverse action notices must rely on post-hoc **SHAP (SHapley Additive exPlanations)** values, which require validation against SHAP instability risk.

### 3.3 Calibration & Probability Realism
- Logistic Regression outputs naturally well-calibrated probabilities via maximum likelihood log-odds.
- Gradient boosting trees can output uncalibrated probabilities near 0 and 1 due to extreme leaf nodes. LightGBM requires explicit **Platt Scaling** or **Isotonic Regression** recalibration before downstream Loss Given Default (LGD) and Expected Loss (EL) calculations.

---

## 4. Final Recommendation & Governance Decision

### **GOVERNANCE RECOMMENDATION: HYBRID TWO-TIER DEPLOYMENT**

1. **Production Champion (Underwriting & Credit Approval)**: Retain the **Logistic Regression Scorecard** as the primary underwriting decision engine. Its total transparency, FCRA adverse action compliance, instant inference speed (0.8 ms), and linear points table make it optimal for automated real-time credit decisioning.
2. **Challenger & Secondary Risk Rating Engine**: Approve **LightGBM** as the official Machine Learning Challenger model for:
   - Risk-based pricing optimization and secondary underwriting review.
   - High-exposure portfolio segmentation and early warning system (EWS).
   - Benchmark model for annual model risk validation audits under SR 11-7.
