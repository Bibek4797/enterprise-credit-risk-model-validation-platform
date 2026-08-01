# Production Model Monitoring Architecture & Governance Framework

**Document Control & Model Risk Governance**
- **Model Scope**: Production Model Monitoring & Governance Specifications for Deployed Champion Credit Model
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Governance Framework**: Federal Reserve SR 11-7 / OCC 2011-12 Guidance / EBA Ongoing Model Monitoring
- **Author**: Model Risk Governance & Quantitative Risk Analytics Team

---

## 1. Executive Summary & Monitoring Architecture

Under **SR 11-7** guidelines, ongoing model monitoring is essential to verify that a deployed credit risk model continues to perform as intended and operates within established risk limits.

This document establishes the technical architecture, monitoring frequencies, ownership roles, key performance indicators (KPIs), alert thresholds, and escalation pathways for the production **Champion Credit Risk Model**.

---

## 2. Model Governance Roles & Ownership Matrix

| Governance Role | Department / Team | Primary Monitoring Responsibilities | Escalation Authority |
| --- | --- | --- | --- |
| **Model Owner** | Head of Retail Credit Underwriting | Business operational performance, approval rates, underwriting policy alignment. | Approves policy threshold adjustments. |
| **Model Developer** | Quantitative Risk Analytics | Ongoing statistical monitoring, PSI/CSI calculation, model retraining execution. | Submits Model Change Requests (MCR). |
| **Independent Validator** | Model Risk Management (MRM) | Independent audit of monitoring reports, annual re-validation, challenger benchmarking. | Grants independent validation sign-off. |
| **Model Risk Committee** | Executive CRO & Risk Committee | Oversight of Tier 1 model risks, approval of model replacement/retraining. | Final approval for production cutover. |

---

## 3. Monitoring Frequencies & KPI Threshold Specifications

| Monitoring Domain | Key Performance Indicator (KPI) | Target Benchmark | Warning Threshold (Yellow) | Action Threshold (Red) | Frequency |
| --- | --- | --- | --- | --- | --- |
| **Population Stability** | Population Stability Index ($\text{PSI}$) | $\text{PSI} < 0.10$ | $0.10 \le \text{PSI} < 0.25$ | $\text{PSI} \ge 0.25$ | Monthly |
| **Characteristic Stability** | Characteristic Stability Index ($\text{CSI}$) | $\text{CSI} < 0.10$ | $0.10 \le \text{CSI} < 0.25$ | $\text{CSI} \ge 0.25$ | Monthly |
| **Discrimination Power** | Out-of-Time ROC-AUC | $\text{AUC} \ge 0.7200$ | $\Delta \text{AUC} \le -0.0300$ | $\Delta \text{AUC} \le -0.0500$ | Quarterly |
| **Risk Separation** | Kolmogorov-Smirnov ($\text{KS} \%$) | $\text{KS} \ge 34.0\%$ | $30.0\% \le \text{KS} < 34.0\%$ | $\text{KS} < 30.0\%$ | Quarterly |
| **Calibration Accuracy** | Brier Score / Obs vs Pred PD Error | $E_{\text{cal}} \le 2.0\%$ | $2.0\% < E_{\text{cal}} \le 5.0\%$ | $E_{\text{cal}} > 5.0\%$ | Monthly |
| **Data Integrity** | Feature Missingness Rate | Missing $< 1.0\%$ | $1.0\% \le \text{Missing} < 5.0\%$ | $\text{Missing} \ge 5.0\%$ | Daily / Batch |
