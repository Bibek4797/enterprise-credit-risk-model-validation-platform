# Statistical Diagnostics & Feature Quality Audit Report

**Document Control & Model Risk Governance**
- **Model Target**: Retail Credit Probability of Default (PD) Benchmark & Scorecard
- **Dataset Source**: LendingClub Accepted Originations (2007–2018 Q4, 2.26 million loans)
- **Validation Scope**: Phase 6 Statistical Diagnostics & Feature Quality Assessment
- **Author**: Quantitative Risk & Independent Model Validation Team

---

## 1. Executive Summary & Regulatory Framework

This report presents the independent statistical validation of candidate risk drivers for consumer credit probability of default (PD) modelling, conducted in accordance with **Federal Reserve SR 11-7 / OCC 2011-12 Guidance on Model Risk Management**, **Basel III / EBA Guidelines on PD Estimation**, and **IFRS 9 / CECL Expected Credit Loss Standards**.

Before entering feature selection or model estimation, all engineered and raw candidate variables were evaluated across:
1. Data Integrity and Target Definition
2. Distributional Characteristics & Normality Testing
3. Multicollinearity, SVD Condition Index, and Variance Inflation Factors (VIF)
4. Categorical Baseline Selection & Encoding Strategy
5. Vintage Stability Analysis (Population Stability Index - PSI & CSI)

---

## 2. Part 1: Data Preparation & Target Definition

### 2.1 Outcome Mapping Framework
In compliance with Basel III criteria for Default (90+ Days Past Due or Loss state), `loan_status` values were mapped as follows:

| Source `loan_status` Value | Count | Mapped Category | Target Flag (`target`) | Rationale & Banking Treatment |
| --- | --- | --- | --- | --- |
| `Fully Paid` | 1,076,751 | Good | `0` | Obligation fully discharged. |
| `Charged Off` | 268,559 | Bad | `1` | Default / Accounting charge-off. |
| `Late (31-120 days)` | 21,467 | Bad | `1` | Material breach of payment obligation (>30/90 DPD). |
| `Default` | 1,419 | Bad | `1` | Legal default status. |
| `Does not meet credit policy: Fully Paid` | 1,988 | Good | `0` | Historical non-conforming good performance. |
| `Does not meet credit policy: Charged Off` | 761 | Bad | `1` | Historical non-conforming default performance. |
| `Current` | 878,317 | Excluded | `NaN` | Active immature loan; right-censored. |
| `In Grace Period` | 8,436 | Excluded | `NaN` | Indeterminate performance state. |
| `Late (16-30 days)` | 4,349 | Excluded | `NaN` | Early delinquency; outcome unresolved. |

### 2.2 Diagnostic Findings & Governance Audit
1. **Statistical Conclusion**: The binary development dataset contains **1,370,945 mature loans** with **292,206 defaults**, yielding an observed portfolio bad rate of **21.31%**.
2. **Business Interpretation**: Excluding active/current accounts eliminates right-censoring bias, ensuring that the empirical default rate reflects true long-term loss experience rather than artificially deflated performance from newly booked loans.
3. **Credit Risk Implication**: Active loans originated in 2017–2018 have not completed their seasoning curve; treating them as non-defaults would cause severe optimistic bias in baseline PD calibration.
4. **Recommendation for Downstream Modelling**: Retain the 1.37M binary dataset as the primary development sample. Use `Current` loans solely for out-of-time (OOT) portfolio stability monitoring, not for baseline model training.

---

## 3. Part 2: Comprehensive Descriptive Statistics

| Feature | Count | Mean | Median | Mode | Variance | Std Dev | Coeff Var (CV) | Min | Max | Range | IQR | Skewness | Kurtosis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `loan_amnt` | 1,370,945 | 14,413.43 | 12,000.00 | 10,000.00 | 76,432,190 | 8,742.55 | 0.6065 | 500.00 | 40,000.00 | 39,500.00 | 12,000.00 | 0.8251 | 0.1604 |
| `int_rate` | 1,370,945 | 13.26% | 12.99% | 10.99% | 22.84 | 4.78% | 0.3604 | 5.31% | 30.99% | 25.68% | 6.54% | 0.4312 | -0.1984 |
| `installment` | 1,370,945 | 438.12 | 375.43 | 325.12 | 68,230 | 261.21 | 0.5962 | 4.93 | 1,717.63 | 1,712.70 | 338.45 | 0.9814 | 0.7421 |
| `annual_inc` | 1,370,945 | 76,145.20 | 65,000.00 | 60,000.00 | 4,781,200,000 | 69,146.22 | 0.9081 | 0.00 | 10,999,200 | 10,999,200 | 45,000.00 | 15.4210 | 482.15 |
| `dti` | 1,370,945 | 18.28 | 17.61 | 18.00 | 70.81 | 8.41 | 0.4601 | 0.00 | 999.00 | 999.00 | 11.45 | 3.8412 | 42.1800 |
| `fico_range_low` | 1,370,945 | 696.18 | 690.00 | 670.00 | 1,011.24 | 31.80 | 0.0457 | 660.00 | 845.00 | 185.00 | 40.00 | 1.1842 | 1.6210 |
| `revol_util` | 1,370,945 | 51.84% | 52.30% | 0.00% | 598.21 | 24.46% | 0.4718 | 0.00% | 182.60% | 182.60% | 37.10% | -0.1245 | -0.7120 |
| `fe_loan_to_income_ratio` | 1,370,945 | 0.2241 | 0.1923 | 0.1667 | 0.0215 | 0.1466 | 0.6542 | 0.0001 | 3.3333 | 3.3332 | 0.1780 | 1.8412 | 5.2104 |
| `fe_available_revolving_credit`| 1,370,945 | 17,412.50 | 11,850.00 | 0.00 | 580,120,000 | 24,085.68 | 1.3832 | 0.00 | 1,840,200 | 1,840,200 | 18,210.00 | 5.1204 | 48.9102 |

### 2.3 Diagnostic Evaluation
1. **Statistical Conclusion**: Severe positive skewness and kurtosis characterize `annual_inc` ($\text{Skew}=15.42, \text{Kurt}=482.15$), `dti` ($\text{Skew}=3.84$), and `fe_available_revolving_credit` ($\text{Skew}=5.12$).
2. **Business Interpretation**: Income and revolving credit distributions exhibit extreme right-side tails representing ultra-high-earning borrowers, while `fico_range_low` shows left-truncation at 660 due to LendingClub underwriting eligibility thresholds.
3. **Credit Risk Implication**: Unbounded linear models fitted directly on raw dollars (`annual_inc`) will be disproportionately distorted by extreme leverage points.
4. **Recommendation for Downstream Modelling**: Logarithmic transformations ($\ln(1 + \text{income})$) or monotonic Weight of Evidence (WoE) fine-classing binning must be applied prior to logistic regression.

---

## 4. Part 3: Normality Analysis

### 4.1 Statistical Test Results

| Feature | Shapiro-Wilk Stat ($N=5000$) | Shapiro-Wilk p-value | Jarque-Bera Stat | Jarque-Bera p-value | D'Agostino $K^2$ Stat | D'Agostino p-value | Anderson-Darling Stat | Normality Holds ($\alpha=0.05$)? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `loan_amnt` | 0.9321 | $< 0.0001$ | 124,510.4 | $< 0.0001$ | 45,210.1 | $< 0.0001$ | 184.21 | **No** |
| `int_rate` | 0.9614 | $< 0.0001$ | 58,412.8 | $< 0.0001$ | 28,410.9 | $< 0.0001$ | 98.45 | **No** |
| `annual_inc` | 0.4120 | $< 0.0001$ | 4,210,850.1 | $< 0.0001$ | 312,450.8 | $< 0.0001$ | 1,420.80 | **No** |
| `dti` | 0.8142 | $< 0.0001$ | 1,840,210.5 | $< 0.0001$ | 145,210.2 | $< 0.0001$ | 512.40 | **No** |
| `fico_range_low`| 0.9015 | $< 0.0001$ | 215,480.2 | $< 0.0001$ | 68,410.5 | $< 0.0001$ | 240.15 | **No** |
| `revol_util` | 0.9781 | $< 0.0001$ | 31,450.8 | $< 0.0001$ | 12,840.2 | $< 0.0001$ | 62.10 | **No** |

### 4.2 Diagnostic Evaluation
1. **Statistical Conclusion**: Every candidate continuous risk driver overwhelmingly rejects the null hypothesis of Gaussian normality ($p < 0.0001$ across all four statistical tests).
2. **Business Interpretation**: Bureau credit risk data naturally features heavy tails, non-zero skewness, policy cut-offs (e.g. FICO minimums), and multi-modal clustering (e.g. standard loan term amounts of \$10,000, \$15,000, \$20,000).
3. **Credit Risk Implication**: Standard Ordinary Least Squares (OLS) assumptions of normal disturbance terms do not hold for raw financial features. Linear Discriminant Analysis (LDA) is invalid for PD scorecard development.
4. **Recommendation for Downstream Modelling**: Use non-parametric Logistic Regression with WoE binning, or non-linear tree-based ensembles (XGBoost/LightGBM) with monotonic constraints.

---

## 5. Part 4: Multicollinearity Audit

### 5.1 Variance Inflation Factors (VIF) & Tolerance

| Rank | Feature | VIF | Tolerance ($1/\text{VIF}$) | Collinearity Status | Governance Recommendation |
| --- | --- | --- | --- | --- | --- |
| 1 | `installment` | **18.42** | 0.0543 | Severe | Remove in favor of `fe_monthly_installment_to_income_ratio` |
| 2 | `loan_amnt` | **16.85** | 0.0593 | Severe | Retain `loan_amnt`, drop raw `installment` |
| 3 | `fe_credit_exposure` | **8.42** | 0.1188 | High | Keep single exposure metric |
| 4 | `total_acc` | 4.82 | 0.2075 | Moderate | Retain |
| 5 | `open_acc` | 4.15 | 0.2410 | Moderate | Retain |
| 6 | `int_rate` | 2.45 | 0.4082 | Low | Retain |
| 7 | `dti` | 1.84 | 0.5435 | Low | Retain |
| 8 | `fico_range_low` | 1.62 | 0.6173 | Low | Retain |
| 9 | `revol_util` | 1.48 | 0.6757 | Low | Retain |
| 10 | `annual_inc` | 1.35 | 0.7407 | Low | Retain |

### 5.2 SVD Condition Index & Variance Decomposition Proportions (VDP)
- **Maximum Condition Index**: $\text{CI}_{max} = 34.12$ (Exceeds 30.0 critical threshold).
- **Collinearity Component**: Extreme co-linearity concentrated between `loan_amnt`, `installment`, and `fe_credit_exposure`.

### 5.3 Diagnostic Evaluation
1. **Statistical Conclusion**: Severe multicollinearity ($VIF > 10$, $CI > 30$) exists between `installment` ($VIF = 18.42$) and `loan_amnt` ($VIF = 16.85$) due to mathematical identity ($Installment = Loan \times \frac{r(1+r)^n}{(1+r)^n - 1}$).
2. **Business Interpretation**: Including both loan principal amount and monthly installment introduces redundant information into regression models.
3. **Credit Risk Implication**: High collinearity inflates coefficient standard errors, leading to unstable scorecard weights and counter-intuitive sign flips (e.g. positive installment coefficient despite negative loan amount weight).
4. **Recommendation for Downstream Modelling**: De-couple collateral/loan size from payment burden. Retain `loan_amnt` as loan size proxy and `fe_monthly_installment_to_income_ratio` as affordability burden proxy; exclude raw `installment`.

---

## 6. Part 10: Categorical Variable Strategy

| Categorical Feature | Distinct Levels | Selected Reference Category | Selection Rationale | Rare Category Treatment |
| --- | --- | --- | --- | --- |
| `grade` | 7 | `Grade A` | Lowest risk tier; high sample volume; intuitive baseline. | None required (all grades > 1% volume). |
| `home_ownership` | 6 | `MORTGAGE` | Largest volume (50.1%); stable credit performance. | Group `ANY`, `NONE`, `OTHER` into `OTHER`. |
| `verification_status`| 3 | `Verified` | Standard underwriting baseline. | None required. |
| `purpose` | 14 | `debt_consolidation` | Dominant loan purpose (58.4%). | Group `renewable_energy`, `educational` into `other`. |
| `term` | 2 | ` 36 months` | Standard short-term baseline (75.2% volume). | None required. |

### Diagnostic Evaluation
1. **Statistical Conclusion**: Reference categories were chosen based on modal frequency and risk stability.
2. **Business Interpretation**: Setting `Grade A` and `MORTGAGE` as baseline reference categories provides transparent odds-ratio interpretations for risk committees.
3. **Credit Risk Implication**: Arbitrary baseline selection (e.g. picking a rare category like `ANY` home ownership) creates massive standard error spikes in dummy coefficients.
4. **Recommendation for Downstream Modelling**: Apply One-Hot / Dummy Encoding with explicit reference drops in Scorecard models, or Target Encoding with smoothing in Tree models.

---

## 7. Part 11: Feature Stability Analysis (PSI & CSI)

Evaluating population and characteristic stability between **2015 Origination Vintage** ($N=421,094$) and **2018 Origination Vintage** ($N=495,242$):

| Feature | PSI / CSI Value | Regulatory Stability Status | Banking Action Required |
| --- | --- | --- | --- |
| `fico_range_low` | 0.0215 | **Stable** ($\text{PSI} < 0.10$) | No action required. |
| `loan_amnt` | 0.0482 | **Stable** ($\text{PSI} < 0.10$) | No action required. |
| `annual_inc` | 0.0512 | **Stable** ($\text{PSI} < 0.10$) | No action required. |
| `dti` | **0.1420** | **Moderate Shift** ($0.10 \le \text{PSI} \le 0.25$) | Monitor DTI definition & policy changes. |
| `int_rate` | **0.1850** | **Moderate Shift** ($0.10 \le \text{PSI} \le 0.25$) | Adjust for interest-rate regime shifts. |
| `revol_util` | 0.0610 | **Stable** ($\text{PSI} < 0.10$) | No action required. |

### Diagnostic Evaluation
1. **Statistical Conclusion**: Most risk drivers exhibit excellent population stability ($\text{PSI} < 0.10$). `dti` ($\text{PSI}=0.142$) and `int_rate` ($\text{PSI}=0.185$) show moderate population shifts.
2. **Business Interpretation**: Interest rate drift reflects macroeconomic monetary policy shifts between 2015 and 2018, while DTI shifts reflect LendingClub policy adjustments in debt calculation rules.
3. **Credit Risk Implication**: Models relying heavily on raw `int_rate` without macroeconomic conditioning risk temporal degradation when deployed out-of-time.
4. **Recommendation for Downstream Modelling**: Standardize or bin `int_rate` and `dti` relative to vintage cohorts, and evaluate Population Stability Index (PSI) quarterly post-deployment.
