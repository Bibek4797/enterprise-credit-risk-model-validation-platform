# Independent Model Validation Report (IMV Audit)

**Document Control & Model Risk Governance**
- **Validation Scope**: Enterprise Retail Credit Risk Probability of Default (PD) Models
- **Target Institution**: Tier-1 Retail Banking & Consumer Credit Operations
- **Governing Guidelines**: Federal Reserve SR 11-7 / OCC 2011-12, Basel III EBA Guidelines, IFRS 9 ECL
- **Validation Authority**: Independent Model Validation (IMV) / Model Risk Management (MRM) Team
- **Validation Decision**: **CONDITIONALLY APPROVED FOR PRODUCTION DEPLOYMENT**

---

## 1. Executive Summary

This report documents the independent review, statistical audit, stress test, and effective challenge performed by the **Independent Model Validation (IMV)** team on the Probability of Default (PD) models submitted by the Model Development team.

### Validation Scope
The validation evaluated eleven submitted candidate models across two primary development tracks:
- **Baseline Statistical Track**: Unpenalized Logistic Scorecard (Submitted Champion), Probit, LASSO, Ridge, Elastic Net.
- **Machine Learning Track**: Decision Tree, Random Forest, Extra Trees, XGBoost, LightGBM (Submitted ML Challenger), CatBoost.

---

## 2. Methodology & Independent Validation Tests

IMV conducted six independent validation workstreams:
1. **Data Lineage & Pipeline Reproducibility Audit**: Verified data transformation scripts, random seeds, and leakage controls.
2. **Out-Of-Time (OOT) Performance Validation**: Independent performance verification on 204,283 mature loans originated in 2018.
3. **Bootstrap Confidence Interval Estimation**: 1,000 non-parametric bootstrap trials to establish statistical bounds on ROC-AUC, Gini, and KS statistics.
4. **Input Sensitivity Perturbation Stress Testing**: Measured prediction stability ($\Delta \text{PD}$) under $\pm 10\%$ and $\pm 20\%$ input shocks.
5. **Vintage Population Stability Index ($\text{PSI}$) Audit**: Historical stability assessment across 2007–2018 origination vintages.
6. **Fair Lending & Equal Credit Opportunity Act (ECOA) Audit**: Disparate impact ratio evaluation across income and demographic proxy tiers.

---

## 3. Independent Validation Findings Summary

| Validation Workstream | IMV Audit Finding | Empirical Result / Metric | Validation Status |
| --- | --- | --- | --- |
| **Pipeline Reproducibility** | All feature engineering and WoE transformation pipelines executed cleanly without data leakage. | 100% Code & Seed Reproducibility | **PASSED** |
| **OOT Discrimination** | Champion Logistic Scorecard achieved robust OOT separation. | $\text{AUC} = 0.7245 \pm 0.0028$, $\text{KS} = 34.82\%$ | **PASSED** |
| **Bootstrap Bounds** | 95% Bootstrap CI for Logistic AUC: `[0.7218, 0.7272]`. | Tight 95% Confidence Bounds | **PASSED** |
| **Sensitivity Stress Test** | Predictable monotonic response to input shocks; no unstable inflection points. | Max $\Delta \text{PD} = +3.82\%$ under +20% rate shock | **PASSED** |
| **Vintage Stability ($\text{PSI}$)** | All core risk drivers displayed stable population distributions. | $\text{PSI} < 0.10$ across 2015–2018 vintages | **PASSED** |
| **Fair Lending (ECOA)** | Disparate Impact Ratios across income tiers met regulatory standards. | All ratios $\ge 0.84$ (Passes 80% Rule) | **PASSED** |

---

## 4. IMV Approval Decision & Governance Mandate

### **OFFICIAL VALIDATION DECISION: CONDITIONAL APPROVAL**

1. **Production Underwriting Champion**: Approved **Unpenalized Logistic Regression Scorecard** for production deployment as the primary automated credit decision engine.
2. **Challenger & Risk Pricing Engine**: Approved **LightGBM** as a secondary Challenger model for risk-based pricing optimization and portfolio early warning monitoring.

---

## 5. Mandatory Monitoring & Control Requirements

1. **Monthly $\text{PSI}$ Monitoring**: Implemented automated alerts: $\text{PSI} \ge 0.10$ triggers Amber review; $\text{PSI} \ge 0.25$ mandates immediate model refit.
2. **Quarterly Recalibration Audit**: Requires quarterly Platt Scaling intercept adjustment if observed portfolio default rate shifts by $> 10\%$ from baseline.
3. **Annual Re-validation**: Mandates a comprehensive independent re-validation 12 months post-deployment under SR 11-7 Tier 1 requirements.
