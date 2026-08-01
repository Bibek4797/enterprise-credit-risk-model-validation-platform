# Enterprise Feature Selection & Variable Governance Report

**Document Control & Model Risk Governance**
- **Model Scope**: Retail Credit Risk Probability of Default (PD) & Scorecard Binning Strategy
- **Development Dataset**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Regulatory Framework**: SR 11-7 / OCC 2011-12 Model Risk Management, Basel III EBA Guidelines, IFRS 9 ECL
- **Author**: Quantitative Risk & Independent Model Validation Team

---

## 1. Executive Summary

This report documents the multi-stage statistical and business feature selection framework conducted for **Phase 7: Feature Selection & Scorecard Preparation**.

Out of 211 candidate attributes (raw + engineered), features were subjected to a rigorous 9-stage screening pipeline:
1. **Missing Value Screening** (Remove $>50\%$ missing unless business-critical)
2. **Correlation & Redundancy Clustering** (Spearman hierarchical linkage clustering at $\rho \ge 0.70$)
3. **Multicollinearity Diagnostics** ($\text{VIF} \le 5.0$, Tolerance $\ge 0.20$, Condition Index $\le 30$)
4. **Information Value Screening** ($\text{IV} \ge 0.02$, screening out uninformative risk drivers)
5. **Statistical Relevance Screening** (Mutual Information, ANOVA F-test, Univariate Logistic AUC)
6. **LASSO Regularization Selection** (L1 penalty shrinkage path with 5-fold CV)
7. **Recursive Feature Elimination** (RFECV stepwise pruning)
8. **Vintage Stability Screening** ($\text{PSI} < 0.25$ across historical origination years 2007–2018)
9. **Business & Regulatory Audit** (Leakage audit, monotonicity verification, regulatory compliance)

---

## 2. Part 2: Missing Value Screening Audit

Every feature was evaluated for missingness across the 1.37M binary development sample. Features exceeding 50% missingness were screened out for baseline scorecard development unless dedicated WoE missing bins were assigned.

| Feature Name | Missing Count | Missing % | Audit Decision | Business Justification |
| --- | --- | --- | --- | --- |
| `mths_since_last_record` | 1,153,248 | 84.12% | **REMOVE** | Severe missingness; non-reporting creates unstable imputation. |
| `mths_since_last_major_derog` | 1,017,241 | 74.20% | **REMOVE** | Severe missingness; low population coverage. |
| `mths_since_last_delinq` | 702,609 | 51.25% | **RETAIN (WoE)** | Retained via WoE coarse classing into 'No Prior Delinquency' bin. |
| `emp_length` | 79,789 | 5.82% | **RETAIN** | Moderate missingness; mapped to 'Missing / Unknown' bin. |
| `tot_cur_bal` | 70,192 | 5.12% | **RETAIN** | Low missingness; median imputed for ML models. |
| `total_rev_hi_lim` | 70,192 | 5.12% | **RETAIN** | Low missingness; median imputed for ML models. |
| `revol_util` | 959 | 0.07% | **RETAIN** | Negligible missingness. |
| `dti` | 274 | 0.02% | **RETAIN** | Negligible missingness. |

---

## 3. Part 3: Correlation & Redundancy Clustering

Using Spearman rank correlation and hierarchical Ward linkage clustering at a threshold of $\rho = 0.70$, highly redundant feature clusters were identified. One exemplar feature was retained per cluster based on business interpretability and higher Information Value:

| Cluster ID | Correlated Features in Cluster | Representative Selected | Action | Business Rationale |
| --- | --- | --- | --- | --- |
| **Cluster 1** | `fico_range_low`, `fico_range_high`, `fe_fico_midpoint` | `fe_fico_midpoint` | Retain `fe_fico_midpoint` | `fico_range_low` and `high` are collinear ($\rho = 1.0$). |
| **Cluster 2** | `grade`, `sub_grade`, `fe_grade_ordinal` | `grade` (Scorecard) / `sub_grade` (ML) | Retain `grade` | `grade` provides robust 7-bin scorecard structure. |
| **Cluster 3** | `loan_amnt`, `funded_amnt`, `installment` | `loan_amnt` & `installment` | Retain `loan_amnt` | `funded_amnt` is a post-approval proxy; `loan_amnt` captures credit request. |
| **Cluster 4** | `revol_bal`, `total_rev_hi_lim`, `tot_hi_cred_lim` | `total_rev_hi_lim` | Retain `total_rev_hi_lim` | Captures borrower total credit line capacity. |
| **Cluster 5** | `open_acc`, `num_sats`, `num_op_rev_tl` | `open_acc` | Retain `open_acc` | Captures overall active trade capacity. |

---

## 4. Part 4: Multicollinearity Diagnostics (VIF & Condition Index)

Reusing Phase 6 statistical diagnostics, Variance Inflation Factor (VIF) and Condition Index analyses were executed on candidate continuous risk drivers:

| Feature Name | Variance Inflation Factor (VIF) | Tolerance (1/VIF) | SVD Condition Index | Multicollinearity Audit |
| --- | --- | --- | --- | --- |
| `fe_fico_midpoint` | 1.84 | 0.543 | 12.4 | **PASS** (Low Multicollinearity) |
| `int_rate` | 2.15 | 0.465 | 14.2 | **PASS** (Low Multicollinearity) |
| `dti` | 1.32 | 0.758 | 8.6 | **PASS** (Low Multicollinearity) |
| `fe_loan_to_income_ratio` | 1.95 | 0.513 | 15.1 | **PASS** (Low Multicollinearity) |
| `annual_inc` | 1.62 | 0.617 | 11.2 | **PASS** (Low Multicollinearity) |
| `revol_util` | 1.48 | 0.676 | 9.8 | **PASS** (Low Multicollinearity) |
| `inq_last_6mths` | 1.12 | 0.893 | 5.4 | **PASS** (Low Multicollinearity) |
| `acc_open_past_24mths` | 1.78 | 0.562 | 13.8 | **PASS** (Low Multicollinearity) |
| `installment` | 4.82 | 0.207 | 24.6 | **PASS** (Below VIF 5.0 Threshold) |

---

## 5. Part 6: Statistical Importance Ranking

Univariate feature relevance was evaluated across multiple statistical metrics:

| Feature Name | Mutual Information | ANOVA F-Statistic | Univariate Logistic AUC | Overall Statistical Rank |
| --- | --- | --- | --- | --- |
| `grade` / `sub_grade` | 0.0485 | 18,420.5 | 0.684 | **Rank 1** |
| `int_rate` | 0.0412 | 16,840.2 | 0.672 | **Rank 2** |
| `fe_fico_midpoint` | 0.0245 | 9,850.4 | 0.628 | **Rank 3** |
| `dti` | 0.0152 | 5,420.1 | 0.598 | **Rank 4** |
| `fe_loan_to_income_ratio` | 0.0118 | 4,110.8 | 0.584 | **Rank 5** |
| `inq_last_6mths` | 0.0094 | 3,250.6 | 0.568 | **Rank 6** |
| `revol_util` | 0.0082 | 2,840.2 | 0.562 | **Rank 7** |
| `annual_inc` | 0.0065 | 2,120.4 | 0.554 | **Rank 8** |

---

## 6. Part 7 & 8: LASSO Regularization & RFE Comparison

L1 (LASSO) cross-validated logistic regression and Recursive Feature Elimination (RFECV) were executed on standardized continuous candidate features.

- **LASSO Selection**: 18 out of 35 numeric continuous features retained non-zero L1 coefficients at optimal $\lambda$. Features shrunk to zero included redundant sub-scores and noisy interaction terms.
- **RFECV Selection**: Optimal CV ROC-AUC peaked at 16 features, displaying 94% feature overlap with LASSO selections.
- **Consensus Retained Features**: `fe_fico_midpoint`, `int_rate`, `grade`, `dti`, `annual_inc`, `fe_loan_to_income_ratio`, `inq_last_6mths`, `revol_util`, `acc_open_past_24mths`, `mort_acc`, `home_ownership`, `term`, `purpose`, `bc_util`, `tot_cur_bal`.

---

## 7. Part 9: Vintage Stability Analysis (PSI / CSI)

Feature stability was tracked across origination years (2007–2016 Baseline vs 2017–2018 Target) to evaluate deployment suitability:

| Feature Name | Baseline Period | Target Period | Population Stability Index (PSI) | Stability Status | Long-term Deployment Audit |
| --- | --- | --- | --- | --- | --- |
| `fe_fico_midpoint` | 2007–2016 | 2017–2018 | 0.0214 | **Stable (< 0.10)** | Approved for deployment. |
| `grade` | 2007–2016 | 2017–2018 | 0.0345 | **Stable (< 0.10)** | Approved for deployment. |
| `int_rate` | 2007–2016 | 2017–2018 | 0.0482 | **Stable (< 0.10)** | Approved for deployment. |
| `dti` | 2007–2016 | 2017–2018 | 0.0612 | **Stable (< 0.10)** | Approved for deployment. |
| `revol_util` | 2007–2016 | 2017–2018 | 0.0384 | **Stable (< 0.10)** | Approved for deployment. |
| `annual_inc` | 2007–2016 | 2017–2018 | 0.0428 | **Stable (< 0.10)** | Approved for deployment. |
| `inq_last_6mths` | 2007–2016 | 2017–2018 | 0.0815 | **Stable (< 0.10)** | Approved for deployment. |
| `acc_open_past_24mths` | 2007–2016 | 2017–2018 | 0.0912 | **Stable (< 0.10)** | Approved for deployment. |

---

## 8. Part 10: Business & Regulatory Governance Review

| Selected Feature | Business Meaning | Expected Default Relationship | Regulatory & Fair Lending Concern | Temporal Leakage Risk | Ongoing Monitoring Plan |
| --- | --- | --- | --- | --- | --- |
| `fe_fico_midpoint` | Overall creditworthiness score | Monotonic Negative (Higher FICO = Lower Default) | None (Standard FCRA compliant credit bureau metric) | None (Application time) | Monthly PSI & CSI tracking |
| `grade` | Risk rating grade | Monotonic Positive (Lower Grade A->G = Higher Default) | None (Underwriting risk band) | None (Application time) | Quarterly migration matrix audit |
| `int_rate` | Risk-based interest pricing | Monotonic Positive (Higher Rate = Higher Default) | Monitor risk-based pricing compliance | None (Application time) | Monthly rate distribution check |
| `dti` | Debt-to-income capacity ratio | Monotonic Positive (Higher DTI = Higher Default) | Ability-to-repay regulation (CFPB) | None (Application time) | Quarterly income verification audit |
| `annual_inc` | Gross annual earnings | Monotonic Negative (Higher Income = Lower Default) | Income verification standards | None (Application time) | Monthly extreme value screening |
| `revol_util` | Revolving credit line utilization | Monotonic Positive (Higher Util = Higher Default) | None | None (Application time) | Monthly PSI tracking |
| `inq_last_6mths` | Recent credit seeking behavior | Monotonic Positive (Higher Inquiries = Higher Default) | FCRA compliance | None (Application time) | Monthly distribution audit |
