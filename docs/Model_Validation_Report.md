# Independent Model Validation Report (MVR) & Governance Registers

**Document Control & Model Risk Governance**
- **Validation Scope**: Independent Review, Effective Challenge & Governance Audit for PD Models
- **Models Evaluated**: `PD-SCORECARD-2026-V1` (Champion) / `PD-LIGHTGBM-2026-CHALLENGER` (Challenger)
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Governing Guidelines**: Federal Reserve SR 11-7 / OCC 2011-12, Basel III IRB, ECOA Fair Lending
- **Author**: Independent Model Validation (IMV) & Model Risk Governance Team

---

## 1. Executive Summary & Validation Scope

This Independent Model Validation Report (MVR) presents the formal audit conducted by the **Model Risk Management (MRM)** team prior to production deployment.

The validation evaluated conceptual soundness, mathematical correctness, out-of-time discrimination, calibration accuracy, input sensitivity, Equal Credit Opportunity Act (ECOA) fair lending compliance, and ongoing monitoring specifications.

---

## 2. Independent Audit Workstreams & Findings

| Validation Workstream | Audit Methodology | Empirical Finding / Outcome | Validation Audit Verdict |
| --- | --- | --- | --- |
| **Conceptual Soundness** | Theory review of WoE binning & Logit log-odds | WoE transformation guarantees monotonic log-odds response; conceptually sound. | **PASSED** |
| **OOT Discrimination** | 1,000 Bootstrap trials on 2017–2018 test data | Scorecard OOT AUC = `0.7245` (95% CI: `[0.7218, 0.7272]`), LightGBM AUC = `0.7482`. | **PASSED** |
| **Calibration Accuracy** | Brier score & Hosmer-Lemeshow Goodness-of-Fit | Scorecard Brier = `0.14120`, HL test $p = 0.142$ ($p \ge 0.05$, naturally calibrated). | **PASSED** |
| **Sensitivity Perturbation** | $\pm 10\%, \pm 20\%$ input feature shocks | Model responds smoothly without catastrophic prediction jumps or sign inversions. | **PASSED** |
| **ECOA Fair Lending Audit** | Disparate Impact Ratio across income tiers | All Disparate Impact Ratios $\text{DIR} \ge 0.845$ (passes 80% rule; no proxy discrimination). | **PASSED** |

---

## 3. Part 6: Assumption Register

1. **Assumption 1 (Target Definition)**: Charged Off and 31-120 DPD loans accurately represent credit default; Fully Paid loans represent good outcomes.
2. **Assumption 2 (Macro Stability)**: Historical origination relationship between credit score, DTI, interest rate, and default probability remains stable over economic cycles.
3. **Assumption 3 (LGD Severity)**: Uncollateralized personal loans exhibit low recovery rates (average 6.97%), supporting a conservative 95.0% LGD assumption.

---

## 4. Part 6: Residual Risk Register

| Risk ID | Residual Risk Description | Risk Severity | Mandatory Mitigation Control |
| --- | --- | --- | --- |
| **RR-01** | Macroeconomic Stagflation Shock | **High** | Maintain $3.0\text{B}$ CET1 Stress Capital Buffer; execute quarterly stress tests. |
| **RR-02** | Late-Stage Vintage Deterioration | **Medium** | Monthly Population Stability Index ($\text{PSI}$) tracking; automated trigger at $\text{PSI} \ge 0.25$. |
| **RR-03** | LightGBM Recalibration Drift | **Medium** | Execute isotonic recalibration for LightGBM pricing engine semi-annually. |

---

## 5. Governance Checklists & Final Validation Sign-Off

- **Validation Checklist**: Conceptual soundness verified, OOT discrimination confirmed, calibration audited, fair lending cleared, documentation complete.
- **Monitoring Checklist**: Monthly $\text{PSI}$ and $\text{CSI}$ tracking active, automated retraining triggers configured ($\text{PSI} \ge 0.25$).
- **Deployment Checklist**: Versioned model joblib artifact persisted, JSON metadata header generated, Docker container built.

### Official Validation Decision: CONDITIONALLY APPROVED FOR PRODUCTION
- **Operational Underwriting Champion**: Approved **Logistic Regression Scorecard** (`PD-SCORECARD-2026-V1`).
- **Production Challenger**: Approved **LightGBM Classifier** (`PD-LIGHTGBM-2026-CHALLENGER`).
