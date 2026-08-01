# Model Development Document (MDD) — Probability of Default (PD) Models

**Document Control & Model Risk Governance**
- **Model Name**: Enterprise Credit Origination & Risk Pricing PD Models
- **Model Identifiers**: `PD-SCORECARD-2026-V1` (Champion) / `PD-LIGHTGBM-2026-CHALLENGER` (Challenger)
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary development records)
- **Target Audience**: Model Risk Management (MRM), Model Risk Committee (MRC), Independent Validators, Regulators
- **Governance Standards**: Federal Reserve SR 11-7 / OCC 2011-12 Guidance, Basel III IRB Standards
- **Author**: Quantitative Risk Analytics & Credit Risk Modelling Team

---

## 1. Executive Summary & Business Objective

This Model Development Document (MDD) presents the end-to-end mathematical, statistical, econometric, and machine learning methodology used to develop Probability of Default ($\text{PD}$) models for retail credit origination and risk-based pricing.

The objective is to establish an interpretable, regulatory-compliant credit scoring system that satisfies:
1. **Underwriting Discrimination**: High bad/good separation power ($\text{KS} \ge 34.0\%$, $\text{ROC-AUC} \ge 0.7200$).
2. **FCRA Adverse Action Notice Compliance**: 100% closed-form score points additivity for automated decline reason generation.
3. **Basel III Capital Alignment**: Well-calibrated Probability of Default for Expected Loss ($\text{EL} = \text{PD} \times \text{LGD} \times \text{EAD}$) calculations.

---

## 2. Dataset Description & Preprocessing

- **Data Source**: LendingClub Accepted Loan Originations (2007–2018 Q4).
- **Binary Target Definition**:
  $$\text{Target} (y_i) = \begin{cases} 1 & \text{if Charged Off, Default, or Late (31-120 days)} \\ 0 & \text{if Fully Paid} \end{cases}$$
- **Sample Count**: $1,370,945$ mature loans.
- **Out-of-Time (OOT) Split**:
  - **Development (Train/Val)**: Originations 2007–2016 ($875,745$ loans).
  - **Out-Of-Time (OOT Test)**: Originations 2017–2018 ($495,200$ loans).

---

## 3. Weight of Evidence (WoE) & Information Value (IV)

To ensure monotonicity and linear log-odds response for statistical modeling, numerical features were binned into Weight of Evidence ($\text{WoE}$) buckets:

$$\text{WoE}_i = \ln \left( \frac{\text{Distribution of Non-Defaults}_i}{\text{Distribution of Defaults}_i} \right)$$

$$\text{IV} = \sum_{i=1}^B (\text{Non-Defaults}_i - \text{Defaults}_i) \times \text{WoE}_i$$

### Top Information Value (IV) Feature Rankings
- `sub_grade` / `grade`: $\text{IV} = 0.8450$ (Extremely Strong Risk Driver)
- `int_rate`: $\text{IV} = 0.6120$ (Extremely Strong Risk Driver)
- `fico_range_low`: $\text{IV} = 0.5240$ (Extremely Strong Risk Driver)
- `dti`: $\text{IV} = 0.4180$ (Strong Risk Driver)
- `annual_inc`: $\text{IV} = 0.3120$ (Strong Risk Driver)

---

## 4. Multi-Stage Feature Selection Framework

Feature selection followed a 9-stage screening audit:
1. Missingness Screening ($< 20\%$)
2. Information Value Screening ($\text{IV} \ge 0.02$)
3. Spearman Correlation Ward-Linkage Clustering ($\rho < 0.70$)
4. Variance Inflation Factor Screening ($\text{VIF} \le 5.0$)
5. LASSO ($L_1$) Penalty Shrinkage
6. Recursive Feature Elimination with Cross-Validation (RFECV)
7. Final Statistical Feature Set (10 Scorecard features) & ML Feature Set (29 features).

---

## 5. Model Development & Master Benchmark Comparison

| Model Architecture | OOT ROC-AUC | Gini Index | KS Stat (%) | Brier Score | Latency (ms) | FCRA Compliance | Operational Role |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Unpenalized Logistic Scorecard** | **0.7245** | **0.4490** | **34.82%** | **0.14120** | **0.5 ms** | **100% Closed-form Points** | **Operational Champion** |
| Probit Regression | 0.7241 | 0.4482 | 34.78% | 0.14125 | 0.5 ms | 100% Analytic AME | Baseline Comparison |
| LASSO ($L_1$) Logistic | 0.7244 | 0.4488 | 34.80% | 0.14122 | 0.5 ms | Closed-form Points | Baseline Comparison |
| LightGBM Classifier | **0.7482** | **0.4964** | **38.42%** | **0.13480** | **4.1 ms** | Tree SHAP Attributions | **Production Challenger** |
| XGBoost Classifier | 0.7475 | 0.4950 | 38.35% | 0.13495 | 4.8 ms | Tree SHAP Attributions | ML Candidate |
| CatBoost Classifier | 0.7480 | 0.4960 | 38.40% | 0.13485 | 5.2 ms | Tree SHAP Attributions | ML Candidate |
| PyTorch MLP (Deep Learning) | 0.7312 | 0.4624 | 35.80% | 0.13950 | 12.8 ms | Black-box / Opacity | Rejected Benchmark |

---

## 6. Final Champion Selection & Governance Rationale

- **Operational Champion**: **Unpenalized Logistic Scorecard** (`PD-SCORECARD-2026-V1`) selected for primary credit origination and automated decline notice generation due to zero operational latency ($0.5\text{ ms}$) and perfect closed-form score point additivity.
- **Production Challenger**: **LightGBM Classifier** (`PD-LIGHTGBM-2026-CHALLENGER`) selected for risk-based pricing optimization and high-exposure portfolio monitoring due to superior discrimination ($\text{AUC} = 0.7482$, $+2.37\%$ lift over Scorecard).
