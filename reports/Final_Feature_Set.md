# Final Feature Set Specification & Model Dataset Architecture

**Document Control & Model Risk Governance**
- **Model Target**: Retail Credit Risk Probability of Default (PD) Models
- **Dataset Scope**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Governance Standard**: Basel III / SR 11-7 / IFRS 9 ECL Standards
- **Author**: Quantitative Risk & Independent Model Validation Team

---

## 1. Executive Summary

Following the multi-stage feature selection framework completed in **Phase 7: Feature Selection & Scorecard Preparation**, three distinct feature subsets were constructed to serve downstream model development phases:

1. **Statistical Model Dataset (Logistic Scorecard)**: Optimized for regulatory transparency, monotonicity, low VIF ($\le 3.0$), linear scorecard points allocation, and Weight of Evidence (WoE) binned representations.
2. **Machine Learning Dataset (Tree Models: XGBoost / LightGBM / Random Forest)**: Optimized for non-linear feature interactions, raw continuous metrics, categorical features, and high-dimensional predictive power.
3. **Deep Learning Dataset (Neural Networks)**: Optimized for standardized/scaled continuous metrics ($Z$-score scaling) and one-hot / dense categorical embeddings.

---

## 2. Statistical Model Dataset (Logistic / Probit Scorecard)

### 2.1 Model Requirements & Constraints
- **Encoding**: Weight of Evidence (WoE) coarse binned transformations.
- **Multicollinearity Constraint**: VIF $< 3.0$, pairwise correlation $< 0.50$.
- **Monotonicity Requirement**: All WoE binned features strictly monotonic across default rates.
- **Parsimony Target**: 8–12 highly interpretable, regulatory-approved risk drivers.

### 2.2 Selected Feature List

| Feature Name | Transformation Format | WoE Monotonicity | VIF | Business Rationale |
| --- | --- | --- | --- | --- |
| `grade_woe` | Categorical WoE (7 bins) | Monotonic | 2.15 | Primary credit risk rating grade. |
| `fe_fico_midpoint_woe` | Numeric Quantile WoE (7 bins) | Monotonic | 1.84 | Primary credit score metric. |
| `int_rate_woe` | Numeric Quantile WoE (10 bins) | Monotonic | 2.10 | Risk-based interest pricing driver. |
| `dti_woe` | Numeric Quantile WoE (10 bins) | Monotonic | 1.32 | Debt-to-income debt service capacity. |
| `annual_inc_woe` | Numeric Quantile WoE (10 bins) | Monotonic | 1.62 | Gross annual earnings capacity. |
| `revol_util_woe` | Numeric Quantile WoE (10 bins) | Monotonic | 1.48 | Revolving credit line utilization. |
| `inq_last_6mths_woe` | Categorical WoE (5 bins) | Monotonic | 1.12 | Recent credit demand inquiries. |
| `acc_open_past_24mths_woe` | Categorical WoE (6 bins) | Monotonic | 1.78 | Recent credit trade velocity. |
| `term_woe` | Categorical WoE (2 bins) | Monotonic | 1.15 | Contractual loan term length (36/60m). |
| `home_ownership_woe` | Categorical WoE (4 bins) | Monotonic | 1.22 | Housing tenancy risk indicator. |

---

## 3. Machine Learning Dataset (XGBoost / LightGBM / Random Forest)

### 3.1 Model Requirements & Constraints
- **Encoding**: Native raw continuous floats, integers, and categorical feature types.
- **Interactions & Non-linearities**: Retained high-order engineered interaction terms (e.g. `fe_interest_burden_ratio`, `fe_loan_to_income_ratio`).
- **Feature Count**: 25–35 risk drivers providing maximum discrimination (ROC-AUC / Gini).

### 3.2 Selected Feature List

| Feature Name | Feature Type | Engine / Source | Purpose in ML Pipeline |
| --- | --- | --- | --- |
| `sub_grade` | Categorical | Original | Fine-grained 35-level risk rating. |
| `fe_fico_midpoint` | Continuous Float | Engineered | Midpoint FICO score. |
| `int_rate` | Continuous Float | Original | Annual interest rate percentage. |
| `loan_amnt` | Continuous Float | Original | Requested loan principal amount ($). |
| `installment` | Continuous Float | Original | Monthly payment amount ($). |
| `annual_inc` | Continuous Float | Original | Self-reported annual income ($). |
| `dti` | Continuous Float | Original | Debt-to-income percentage. |
| `revol_util` | Continuous Float | Original | Revolving utilization rate. |
| `revol_bal` | Continuous Float | Original | Total revolving balance ($). |
| `total_rev_hi_lim` | Continuous Float | Original | Revolving high credit limit ($). |
| `tot_cur_bal` | Continuous Float | Original | Total current balance of all accounts. |
| `bc_open_to_buy` | Continuous Float | Original | Bankcard open-to-buy amount ($). |
| `bc_util` | Continuous Float | Original | Bankcard line utilization rate. |
| `inq_last_6mths` | Discrete Int | Original | Inquiries in past 6 months. |
| `acc_open_past_24mths` | Discrete Int | Original | Accounts opened in past 24 months. |
| `mort_acc` | Discrete Int | Original | Number of mortgage accounts. |
| `mo_sin_old_rev_tl_op` | Continuous Float | Original | Months since oldest revolving line. |
| `mo_sin_rcnt_rev_tl_op`| Continuous Float | Original | Months since recent revolving line. |
| `pct_tl_nvr_dlq` | Continuous Float | Original | Percent of trades never delinquent. |
| `fe_loan_to_income_ratio` | Continuous Float | Engineered | Loan amount divided by annual income. |
| `fe_monthly_installment_to_income_ratio` | Continuous Float | Engineered | Monthly payment to income ratio. |
| `fe_interest_burden_ratio` | Continuous Float | Engineered | Interest rate times loan-to-income ratio. |
| `fe_available_revolving_credit` | Continuous Float | Engineered | Available revolving headroom ($). |
| `fe_delinquency_frequency` | Continuous Float | Engineered | Delinquencies divided by credit age. |
| `fe_high_debt_risk_flag` | Binary Flag | Engineered | DTI > 30% risk indicator flag. |
| `term` | Categorical | Original | Loan tenure (36 or 60 months). |
| `home_ownership` | Categorical | Original | Housing tenure (RENT/OWN/MORTGAGE). |
| `purpose` | Categorical | Original | Stated loan purpose. |
| `verification_status` | Categorical | Original | Income verification status. |

---

## 4. Deep Learning Dataset (Neural Networks)

### 4.1 Model Requirements & Constraints
- **Preprocessing**: Robust Standardized Continuous Variables ($Z$-score scaling) and Dense Categorical Embeddings / One-Hot Encoding.
- **Imputation**: Median imputation for missing numeric values; dedicated 'Missing' level for categoricals.

### 4.2 Selected Feature List
- **Continuous Scaled Features (22)**: `fe_fico_midpoint`, `int_rate`, `loan_amnt`, `installment`, `annual_inc`, `dti`, `revol_util`, `revol_bal`, `total_rev_hi_lim`, `tot_cur_bal`, `bc_open_to_buy`, `bc_util`, `inq_last_6mths`, `acc_open_past_24mths`, `mort_acc`, `mo_sin_old_rev_tl_op`, `pct_tl_nvr_dlq`, `fe_loan_to_income_ratio`, `fe_monthly_installment_to_income_ratio`, `fe_interest_burden_ratio`, `fe_available_revolving_credit`, `fe_delinquency_frequency`.
- **One-Hot Categorical Features (5 Variables, 52 Columns)**: `term` (2), `grade` (7), `home_ownership` (4), `verification_status` (3), `purpose` (14), `initial_list_status` (2).

---

## 5. Summary Matrix of Dataset Architectural Differences

| Dimension | Statistical Scorecard Dataset | Machine Learning Dataset | Deep Learning Dataset |
| --- | --- | --- | --- |
| **Primary Model Type** | Logistic Regression / Scorecard Points | XGBoost / LightGBM / Random Forest | Multi-Layer Perceptron (MLP) / TabNet |
| **Representation** | Weight of Evidence (WoE) Binned | Raw Continuous & Categorical | $Z$-score Scaled + Dense Embeddings |
| **VIF Constraint** | Strict ($\text{VIF} < 3.0$) | Relaxed ($\text{VIF} < 10.0$) | Relaxed |
| **Feature Count** | 10 Risk Drivers | 29 Risk Drivers | 27 Base (52 One-Hot Encoded) |
| **Non-Linearities** | Captured via WoE Bins | Captured via Tree Splits & Interactions | Captured via Dense Neural Layers |
| **Interpretability** | Maximum (Scorecard Points Table) | High (SHAP Values & Feature Importance) | Moderate (SHAP / Integrated Gradients) |
| **Regulatory Fit** | Baseline Regulatory Credit Scorecard | Advanced Model Benchmarking | Challenger AI/ML Model |
