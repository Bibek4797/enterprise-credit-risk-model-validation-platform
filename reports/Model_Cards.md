# Institutional Model Cards Suite (SR 11-7 Compliance)

**Document Control & Model Risk Governance**
- **Governance Standard**: Federal Reserve SR 11-7 / OCC 2011-12 Model Risk Management
- **Scope**: Enterprise Model Cards for Production Champion and Challenger Risk Models
- **Author**: Quantitative Risk & Independent Model Validation Team

---

# Model Card 1: Production Champion — Logistic Scorecard Model

## 1. Model Overview & Metadata
- **Model ID**: `PD-SCORECARD-2026-V1`
- **Model Name**: Production Retail Credit Probability of Default (PD) Scorecard
- **Model Architecture**: Unpenalized Binary Logistic Regression on Weight of Evidence (WoE) binned risk drivers
- **Model Owner**: Retail Credit Underwriting & Credit Policy Committee
- **Model Validator**: Independent Model Validation (IMV) Team
- **Governance Status**: **APPROVED FOR PRODUCTION DEPLOYMENT**
- **Model Risk Rating**: **TIER 1 (HIGH MODEL RISK)**

---

## 2. Target Variable & Business Scope
- **Target Definition**: `target` = 1 for Default/Loss state (`Charged Off`, `Default`, `Late (31-120 days)`), `target` = 0 for `Fully Paid`.
- **Exclusions**: Active `Current` loans (excluded during development to eliminate right-censoring bias).
- **Application Scope**: Real-time automated retail loan origination, credit scoring, and adverse action notice generation.

---

## 3. Key Input Variables (Risk Drivers)
1. `grade_woe`: Primary credit risk rating grade WoE.
2. `fe_fico_midpoint_woe`: Credit bureau FICO score midpoint WoE.
3. `int_rate_woe`: Annual interest rate WoE.
4. `dti_woe`: Debt-to-income ratio WoE.
5. `annual_inc_woe`: Gross annual income WoE.
6. `revol_util_woe`: Revolving line utilization rate WoE.
7. `inq_last_6mths_woe`: Credit inquiries in past 6 months WoE.
8. `acc_open_past_24mths_woe`: Trades opened in past 24 months WoE.

---

## 4. Performance Validation Summary (Out-Of-Time 2018 Test Set)
- **ROC-AUC**: `0.7245` (95% Bootstrap CI: `[0.7218, 0.7272]`)
- **Gini Coefficient**: `0.4490`
- **Kolmogorov-Smirnov ($\text{KS}$) Statistic**: `34.82%` at optimal cutoff `0.2085`
- **Brier Score**: `0.14120`
- **Hosmer-Lemeshow Calibration**: `p = 0.1420` (Passed; well-calibrated)

---

## 5. Model Limitations & Monitoring Triggers
- **Limitation 1**: Relies on linear log-odds assumptions across WoE bins.
- **Monitoring Trigger 1**: Monthly $\text{PSI} \ge 0.10$ triggers Amber alert; $\text{PSI} \ge 0.25$ triggers mandatory model refit.
- **Monitoring Trigger 2**: Annual re-validation mandated under SR 11-7 Tier 1 rules.

---

# Model Card 2: Production Challenger — LightGBM Gradient Boosting Model

## 1. Model Overview & Metadata
- **Model ID**: `PD-LIGHTGBM-2026-CHALLENGER`
- **Model Name**: Challenger Machine Learning Probability of Default (PD) Model
- **Model Architecture**: LightGBM (Light Gradient Boosting Machine) with 220 trees, `max_depth = 5`, `learning_rate = 0.038`
- **Model Owner**: Advanced Risk Analytics Team
- **Governance Status**: **APPROVED AS SECONDARY CHALLENGER & PRICING ENGINE**
- **Model Risk Rating**: **TIER 1 (HIGH MODEL RISK)**

---

## 2. Key Input Variables
29 raw continuous, categorical, and engineered risk drivers (including `sub_grade`, `fe_fico_midpoint`, `int_rate`, `fe_loan_to_income_ratio`, `fe_interest_burden_ratio`).

---

## 3. Performance Validation Summary (Out-Of-Time 2018 Test Set)
- **ROC-AUC**: `0.7482` (+2.37% lift over Champion)
- **Gini Coefficient**: `0.4964`
- **KS Statistic**: `38.42%` (+3.60% lift over Champion)
- **Brier Score**: `0.13480`
- **Inference Latency**: `4.1 ms` per 1,000 samples

---

## 4. Model Limitations & Monitoring Triggers
- **Limitation 1**: Black-box gradient boosting requires post-hoc SHAP proxy explanations for non-linear interactions.
- **Monitoring Trigger 1**: Quarterly Platt Scaling recalibration if predicted vs observed default ratio deviates by $> 10\%$.
