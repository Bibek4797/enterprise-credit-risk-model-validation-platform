# Comprehensive Feature Inventory & Governance Catalog

**Document Control & Model Risk Governance**
- **Model Target**: Retail Credit Probability of Default (PD) & Scorecard Development
- **Scope**: Complete Catalog of Original and Engineered Candidate Risk Drivers
- **Data Version**: LendingClub Accepted Loan Portfolio (2007–2018 Q4, ~1.37M binary development dataset)
- **Author**: Quantitative Risk & Independent Model Validation Team
- **Governance Standard**: SR 11-7 / OCC 2011-12 Guidance on Model Risk Management

---

## 1. Executive Summary

This inventory catalogs all original raw attributes and engineered features evaluated during **Phase 7: Feature Selection & Scorecard Preparation**. Every attribute is classified according to its data source, data type, business category, missingness percentage, cardinality, and recommended usage across downstream modelling frameworks (Statistical Scorecard, Machine Learning, and Deep Learning).

---

## 2. Comprehensive Feature Inventory Table

| Feature Name | Source | Data Type | Business Category | Description | Missing % | Cardinality | Recommended Usage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `loan_amnt` | Original | Float | Credit Structure | Total principal requested by borrower ($) | 0.00% | 1,560 | Stat, ML, DL |
| `funded_amnt` | Original | Float | Credit Structure | Total principal funded by lender ($) | 0.00% | 1,560 | Exclude (Post-origination proxy) |
| `term` | Original | String | Credit Structure | Loan payment duration (36 or 60 months) | 0.00% | 2 | Stat (WOE), ML, DL |
| `int_rate` | Original | Float | Pricing & Risk | Annual interest rate charged (%) | 0.00% | 580 | Stat, ML, DL |
| `installment` | Original | Float | Credit Structure | Monthly payment commitment ($) | 0.00% | 15,200 | Stat, ML, DL |
| `grade` | Original | Categorical | Risk Rating | Credit risk grade assigned (A–G) | 0.00% | 7 | Stat (WOE), ML, DL |
| `sub_grade` | Original | Categorical | Risk Rating | Fine-grained credit risk sub-grade (A1–G5) | 0.00% | 35 | Stat (WOE), ML, DL |
| `emp_length` | Original | Categorical | Employment | Borrower employment length (years) | 5.82% | 12 | Stat (WOE), ML, DL |
| `home_ownership` | Original | Categorical | Borrower Demographics | Housing tenancy status (RENT, OWN, MORTGAGE) | 0.00% | 6 | Stat (WOE), ML, DL |
| `annual_inc` | Original | Float | Income & Capacity | Self-reported annual gross income ($) | 0.00% | 54,200 | Stat, ML, DL |
| `verification_status`| Original | Categorical | Income & Capacity | Income verification state (Verified/Not) | 0.00% | 3 | Stat (WOE), ML, DL |
| `issue_d` | Original | Date | Temporal | Month and year of loan origination | 0.00% | 139 | Vintage / OOT Split only |
| `purpose` | Original | Categorical | Loan Purpose | Stated reason for loan (debt_consolidation, etc.) | 0.00% | 14 | Stat (WOE), ML, DL |
| `dti` | Original | Float | Debt Capacity | Debt-to-Income ratio (%) | 0.02% | 4,200 | Stat, ML, DL |
| `delinq_2yrs` | Original | Float | Credit History | Number of 30+ DPD delinquencies in past 2 yrs | 0.00% | 32 | Stat, ML, DL |
| `earliest_cr_line` | Original | Date | Credit History | Month credit line was opened | 0.00% | 754 | Time feature engineering |
| `fico_range_low` | Original | Float | Credit Score | Lower boundary of FICO score range | 0.00% | 38 | Stat, ML, DL |
| `fico_range_high` | Original | Float | Credit Score | Upper boundary of FICO score range | 0.00% | 38 | Stat, ML, DL |
| `inq_last_6mths` | Original | Float | Credit Demand | Credit inquiries in past 6 months | 0.00% | 28 | Stat, ML, DL |
| `mths_since_last_delinq` | Original | Float | Delinquency History | Months elapsed since last delinquency | 51.25% | 172 | Stat (WOE Binning), ML |
| `mths_since_last_record` | Original | Float | Public Records | Months elapsed since last public record | 84.12% | 132 | Exclude (>50% missing) |
| `open_acc` | Original | Float | Credit Lines | Number of open credit lines | 0.00% | 85 | Stat, ML, DL |
| `pub_rec` | Original | Float | Public Records | Number of derogatory public records | 0.00% | 42 | Stat, ML, DL |
| `revol_bal` | Original | Float | Revolving Debt | Total revolving credit balance ($) | 0.00% | 78,500 | Stat, ML, DL |
| `revol_util` | Original | Float | Revolving Debt | Revolving line utilization rate (%) | 0.07% | 1,280 | Stat, ML, DL |
| `total_acc` | Original | Float | Credit Lines | Total credit lines on record | 0.00% | 135 | Stat, ML, DL |
| `initial_list_status` | Original | Categorical | Origination | Initial listing status (W / F) | 0.00% | 2 | Stat, ML, DL |
| `collections_12_mths_ex_med` | Original | Float | Collections | Collections in past 12 months excluding medical | 0.01% | 16 | Stat, ML, DL |
| `mths_since_last_major_derog` | Original | Float | Delinquency History | Months since last 90+ DPD rating | 74.20% | 175 | Exclude (>50% missing) |
| `policy_code` | Original | Int | Governance | Lending policy code (1 = Publicly available) | 0.00% | 1 | Exclude (Constant) |
| `application_type` | Original | Categorical | Origination | Individual or Joint application | 0.00% | 2 | Stat, ML, DL |
| `acc_now_delinq` | Original | Float | Delinquency History | Accounts currently delinquent | 0.00% | 9 | Stat, ML, DL |
| `tot_coll_amt` | Original | Float | Collections | Total collection amounts ever owed | 5.12% | 12,400 | Stat, ML, DL |
| `tot_cur_bal` | Original | Float | Total Debt | Total current balance of all accounts | 5.12% | 340,000 | Stat, ML, DL |
| `total_rev_hi_lim` | Original | Float | Revolving Debt | Total revolving high credit/credit limit | 5.12% | 24,100 | Stat, ML, DL |
| `acc_open_past_24mths` | Original | Float | Credit Demand | Trades opened in past 24 months | 3.65% | 58 | Stat, ML, DL |
| `avg_cur_bal` | Original | Float | Debt Capacity | Average current balance of all accounts | 3.65% | 85,200 | Stat, ML, DL |
| `bc_open_to_buy` | Original | Float | Bankcard Debt | Total open to buy on bankcards ($) | 4.12% | 71,400 | Stat, ML, DL |
| `bc_util` | Original | Float | Bankcard Debt | Ratio of total balance to high credit on bankcards | 4.25% | 1,420 | Stat, ML, DL |
| `chargeoff_within_12_mths` | Original | Float | Collections | Charge-offs within 12 months | 0.01% | 11 | Stat, ML, DL |
| `delinq_amnt` | Original | Float | Delinquency History | Past-due amount for delinquent accounts | 0.00% | 1,200 | Stat, ML, DL |
| `mo_sin_old_il_acct` | Original | Float | Installment Debt | Months since oldest installment account opened | 9.85% | 520 | Stat, ML, DL |
| `mo_sin_old_rev_tl_op` | Original | Float | Revolving Debt | Months since oldest revolving account opened | 5.12% | 750 | Stat, ML, DL |
| `mo_sin_rcnt_rev_tl_op` | Original | Float | Revolving Debt | Months since most recent revolving account opened | 5.12% | 280 | Stat, ML, DL |
| `mo_sin_rcnt_tl` | Original | Float | Credit Demand | Months since most recent account opened | 5.12% | 210 | Stat, ML, DL |
| `mort_acc` | Original | Float | Mortgage Debt | Number of mortgage accounts | 3.65% | 42 | Stat, ML, DL |
| `mths_since_recent_bc` | Original | Float | Bankcard Debt | Months since most recent bankcard account opened | 4.05% | 460 | Stat, ML, DL |
| `mths_since_recent_inq` | Original | Float | Credit Demand | Months since most recent inquiry | 12.50% | 26 | Stat, ML, DL |
| `num_accts_ever_120_pd` | Original | Float | Delinquency History | Number of accounts 120+ DPD ever | 5.12% | 44 | Stat, ML, DL |
| `num_actv_bc_tl` | Original | Float | Bankcard Debt | Number of currently active bankcard accounts | 5.12% | 36 | Stat, ML, DL |
| `num_actv_rev_tl` | Original | Float | Revolving Debt | Number of currently active revolving trades | 5.12% | 52 | Stat, ML, DL |
| `num_bc_sats` | Original | Float | Bankcard Debt | Number of satisfactory bankcard accounts | 4.25% | 58 | Stat, ML, DL |
| `num_bc_tl` | Original | Float | Bankcard Debt | Number of bankcard accounts | 5.12% | 72 | Stat, ML, DL |
| `num_il_tl` | Original | Float | Installment Debt | Number of installment accounts | 5.12% | 115 | Stat, ML, DL |
| `num_op_rev_tl` | Original | Float | Revolving Debt | Number of open revolving trades | 5.12% | 70 | Stat, ML, DL |
| `num_rev_accts` | Original | Float | Revolving Debt | Number of revolving accounts | 5.12% | 110 | Stat, ML, DL |
| `num_rev_tl_bal_gt_0` | Original | Float | Revolving Debt | Number of revolving trades with balance > 0 | 5.12% | 50 | Stat, ML, DL |
| `num_sats` | Original | Float | Credit Lines | Number of satisfactory accounts | 4.25% | 92 | Stat, ML, DL |
| `num_tl_120dpd_2m` | Original | Float | Delinquency History | Number of accounts 120+ DPD updated in past 2m | 8.50% | 6 | Stat, ML, DL |
| `num_tl_30dpd` | Original | Float | Delinquency History | Number of accounts 30+ DPD | 5.12% | 6 | Stat, ML, DL |
| `num_tl_90g_dpd_24m` | Original | Float | Delinquency History | Number of accounts 90+ DPD in past 24 months | 5.12% | 28 | Stat, ML, DL |
| `num_tl_op_past_12m` | Original | Float | Credit Demand | Number of accounts opened in past 12 months | 5.12% | 35 | Stat, ML, DL |
| `pct_tl_nvr_dlq` | Original | Float | Delinquency History | Percent of trades never delinquent (%) | 5.15% | 620 | Stat, ML, DL |
| `percent_bc_gt_75` | Original | Float | Bankcard Debt | Percent of bankcard accounts > 75% limit | 4.30% | 280 | Stat, ML, DL |
| `pub_rec_bankruptcies` | Original | Float | Public Records | Number of public record bankruptcies | 0.05% | 12 | Stat, ML, DL |
| `tax_liens` | Original | Float | Public Records | Number of tax liens | 0.01% | 35 | Stat, ML, DL |
| `tot_hi_cred_lim` | Original | Float | Debt Capacity | Total high credit/credit limit ($) | 5.12% | 380,000 | Stat, ML, DL |
| `total_bal_ex_mort` | Original | Float | Total Debt | Total credit balance excluding mortgage | 3.65% | 165,000 | Stat, ML, DL |
| `total_bc_limit` | Original | Float | Bankcard Debt | Total bankcard high credit/credit limit | 3.65% | 22,500 | Stat, ML, DL |
| `total_il_high_credit_limit`| Original | Float | Installment Debt | Total installment high credit/credit limit | 5.12% | 170,000 | Stat, ML, DL |
| `fe_fico_midpoint` | Engineered | Float | Credit Score | Average of `fico_range_low` and `fico_range_high` | 0.00% | 38 | Stat, ML, DL |
| `fe_fico_risk_band` | Engineered | Categorical | Credit Score | Credit score band (Deep Subprime to Exceptional) | 0.00% | 5 | Stat (WOE) |
| `fe_grade_ordinal` | Engineered | Int | Risk Rating | Numeric mapping of letter grade A=1..G=7 | 0.00% | 7 | Stat, ML, DL |
| `fe_loan_to_income_ratio` | Engineered | Float | Debt Capacity | `loan_amnt` / (`annual_inc` + 1) | 0.00% | 185,000 | Stat, ML, DL |
| `fe_monthly_installment_to_income_ratio` | Engineered | Float | Debt Burden | (`installment` * 12) / (`annual_inc` + 1) | 0.00% | 210,000 | Stat, ML, DL |
| `fe_interest_burden_ratio` | Engineered | Float | Pricing & Risk | `int_rate` * `fe_loan_to_income_ratio` | 0.00% | 240,000 | Stat, ML, DL |
| `fe_credit_utilization` | Engineered | Float | Revolving Debt | `revol_bal` / (`total_rev_hi_lim` + 1) | 5.12% | 190,000 | Stat, ML, DL |
| `fe_available_revolving_credit` | Engineered | Float | Revolving Debt | `total_rev_hi_lim` - `revol_bal` | 5.12% | 215,000 | Stat, ML, DL |
| `fe_debt_burden` | Engineered | Float | Debt Capacity | `dti` * `annual_inc` / 100 | 0.02% | 280,000 | Stat, ML, DL |
| `fe_high_debt_risk_flag` | Engineered | Binary | Business Flag | 1 if `dti` > 30%, else 0 | 0.00% | 2 | Stat, ML, DL |
| `fe_low_income_risk_flag` | Engineered | Binary | Business Flag | 1 if `annual_inc` < $40,000, else 0 | 0.00% | 2 | Stat, ML, DL |
| `fe_high_interest_risk_flag`| Engineered | Binary | Business Flag | 1 if `int_rate` > 20%, else 0 | 0.00% | 2 | Stat, ML, DL |
| `fe_high_utilization_flag` | Engineered | Binary | Business Flag | 1 if `revol_util` > 80%, else 0 | 0.00% | 2 | Stat, ML, DL |
| `fe_delinquency_frequency` | Engineered | Float | Delinquency History | `delinq_2yrs` / (`fe_credit_age_years` + 1) | 0.00% | 8,500 | Stat, ML, DL |
| `fe_recent_inquiry_rate` | Engineered | Float | Credit Demand | `inq_last_6mths` / 6.0 | 0.00% | 28 | Stat, ML, DL |
| `fe_bankrupt_flag` | Engineered | Binary | Public Records | 1 if `pub_rec_bankruptcies` > 0, else 0 | 0.00% | 2 | Stat, ML, DL |
| `fe_interest_rate_x_dti` | Engineered | Float | Risk Interaction | `int_rate` * `dti` | 0.02% | 310,000 | ML, DL |
| `fe_fico_x_delinquencies` | Engineered | Float | Risk Interaction | `fe_fico_midpoint` / (`delinq_2yrs` + 1) | 0.00% | 14,200 | ML, DL |

---

## 3. Post-Origination & Leakage Audit Summary

Per Basel III and SR 11-7 model development guidelines, all post-origination fields (e.g. `out_prncp`, `total_pymnt`, `recoveries`, `last_pymnt_d`, `hardship_flag`, `settlement_status`) are strictly tagged **EXCLUDE** to prevent forward-looking data leakage in application-stage default prediction models.
