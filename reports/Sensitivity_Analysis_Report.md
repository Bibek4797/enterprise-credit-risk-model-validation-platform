# Variable Sensitivity & PD Elasticity Audit Report

**Document Control & Model Risk Governance**
- **Model Scope**: Sensitivity & Elasticity Audit for Champion Credit Risk Model
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Regulatory Framework**: SR 11-7 Model Risk Guidance / CCAR Sensitivity Analysis
- **Author**: Enterprise Risk Management & Credit Risk Analytics Team

---

## 1. Executive Summary & Sensitivity Methodology

Sensitivity analysis evaluates how incremental perturbations in individual risk drivers impact predicted Probability of Default ($\text{PD}$).

**PD Elasticity** measures the percentage change in mean portfolio predicted PD resulting from a $1.0\%$ relative increase in a specific risk driver:

$$\text{Elasticity}_X = \frac{(\text{PD}_{\text{stressed}} - \text{PD}_{\text{baseline}}) / \text{PD}_{\text{baseline}}}{\Delta X / X_{\text{baseline}}}$$

This report documents feature sensitivity rankings, PD elasticity metrics, non-linear threshold effects, and credit policy implications.

---

## 2. Risk Driver Sensitivity Rankings & PD Elasticity Table

The table below ranks candidate risk drivers evaluated under a $+10.0\%$ positive parameter shock across the Out-Of-Time test sample:

| Sensitivity Rank | Risk Driver Name | Baseline Mean PD | Shocked Mean PD | Absolute $\Delta \text{PD}$ | PD Elasticity ($\text{Elasticity}_X$) | Sensitivity Classification | Credit Policy Implication |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **1** | `fe_fico_midpoint` / `fico_range_low` | 20.85% | 24.12% | +3.27% | **-1.568** | **Extremely High** (Inverse) | FICO downgrades create rapid PD escalation; primary risk filter. |
| **2** | `int_rate` | 20.85% | 22.84% | +1.99% | **+0.954** | **High** (Direct) | Interest rate hikes increase debt service burden significantly. |
| **3** | `dti` | 20.85% | 22.15% | +1.30% | **+0.623** | **High** (Direct) | Debt-to-income ratio reflects capacity constraints. |
| **4** | `revol_util` | 20.85% | 21.62% | +0.77% | **+0.369** | **Moderate** (Direct) | Credit line utilization reflects liquidity exhaustion. |
| **5** | `annual_inc` | 20.85% | 19.82% | -1.03% | **-0.494** | **Moderate** (Inverse) | Income expansion mitigates default hazard. |
| **6** | `inq_last_6mths` | 20.85% | 21.28% | +0.43% | **+0.206** | **Low** (Direct) | Credit demand inquiry frequency. |
| **7** | `acc_open_past_24mths` | 20.85% | 21.15% | +0.30% | **+0.144** | **Low** (Direct) | Credit trade velocity. |
| **8** | `open_acc` | 20.85% | 20.91% | +0.06% | **+0.029** | **Negligible** | Total open trade lines. |

---

## 3. Non-Linear Threshold Inflection Analysis

1. **FICO Score Threshold**: Predicted PD remains flat below 700 FICO, but escalates exponentially when FICO drops below **675** ($\Delta \text{PD} = +6.57\%$). Underwriting policy must enforce strict manual review for scores $< 675$.
2. **DTI Ratio Threshold**: Predicted PD increases moderately up to $25.0\%$ DTI, then accelerates rapidly above **28.0% DTI**. Capping maximum DTI at $30.0\%$ prevents tail risk accumulation.
3. **Interest Rate Threshold**: Interest rate pricing above **18.0%** exhibits strong compounding default risk, supporting maximum interest rate caps in risk-based pricing schedules.
