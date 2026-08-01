# Feature Engineering Report

## Purpose and Control Framework

This phase creates reusable application-time candidate features for consumer-credit analysis. Raw data remains immutable; the processed dataset retains every original source field and appends only `fe_`-prefixed features. No feature selection, variable removal, target construction, or predictive modelling is performed.

Post-origination fields—payments, recoveries, collections, later credit pulls, hardship, settlement, and current loan status—are explicitly excluded as source inputs for engineered features. Their inclusion would create application-time data leakage.

## Financial and Affordability Features

| Feature | Formula | Interpretation / expected default relationship | Risk or limitation |
| --- | --- | --- | --- |
| `fe_loan_to_income_ratio` | loan amount / annual income | Higher leverage may increase repayment strain and default risk. | Income quality and co-borrower treatment must be confirmed. |
| `fe_monthly_installment_to_income_ratio` | installment / (annual income / 12) | Direct monthly payment burden; higher values are expected to worsen affordability. | Does not include all external obligations. |
| `fe_interest_burden_ratio` | (installment × term months − loan amount) / loan amount | Total contractual finance burden proxy. | Assumes scheduled payments; not realised cost. |
| `fe_credit_utilization`, `fe_available_revolving_credit` | revol utilisation; credit limit − revol balance | High utilisation and limited unused credit indicate liquidity stress. | Limits may be stale or missing. |
| `fe_credit_exposure`, `fe_debt_burden` | loan + revolving balance; DTI | Larger exposure and DTI can amplify loss risk. | DTI definition must be confirmed. |
| Bands and burden categories | Controlled bins of income, loan, rate, utilisation, payment burden, DTI | Permit portfolio segmentation and nonlinear inspection. | Thresholds are policy-style monitoring bands, not optimised cut-offs. |

## Credit Behaviour and Aggregation Features

| Feature | Formula | Interpretation / expected default relationship | Risk or limitation |
| --- | --- | --- | --- |
| `fe_delinquency_count`, `fe_months_since_last_delinquency` | Existing bureau fields | More/recent delinquency generally implies elevated risk. | Timing must be verified as application-time. |
| `fe_public_record_flag`, `fe_bankruptcy_flag`, `fe_recent_bankruptcy_flag` | Indicator from public records and months since record | Adverse public records may signal stressed repayment capacity. | Legal/fair-lending governance and data accuracy are essential. |
| `fe_recent_inquiry_rate` | inquiries in six months / max(credit history months / 6, 1) | High recent search intensity can indicate credit demand. | Thin files can make ratios unstable. |
| `fe_open_account_share`, `fe_active_revolving_account_share` | open accounts / total; active revolving / revolving accounts | Portfolio breadth and active credit usage proxies. | Zero denominators become missing by design. |
| `fe_average_revolving_balance_per_account`, `fe_recent_account_opening_rate`, `fe_delinquency_frequency` | balances, recent openings, severe delinquent accounts scaled by account counts | Captures depth, recency, and adverse credit history. | Not a replacement for bureau-tradeline analysis. |
| `fe_bank_card_utilization_gap` | bank-card utilisation − revolving utilisation | Highlights concentration of utilisation in bank cards. | This is a point-in-time proxy, not a true utilisation trend. |

## Time and Seasonality Features

| Feature | Formula | Interpretation / expected default relationship | Risk or limitation |
| --- | --- | --- | --- |
| `fe_issue_year`, `fe_issue_quarter`, `fe_issue_month` | Parsed `issue_d` components | Captures vintage, seasonality, and policy regime. | Must be controlled in out-of-time validation. |
| `fe_issue_month_sin`, `fe_issue_month_cos` | cyclical month encoding | Represents annual seasonality continuously. | Not an economic causal variable. |
| `fe_loan_age_months_at_cutoff` | months between issue date and 2018-12-31 | Supports maturity and vintage reporting. | Must not be used in application PD unless as-of rules permit. |
| `fe_credit_history_months`, `fe_credit_age_years` | issue date − earliest credit line | Longer established credit history may be stabilising. | Earliest-line dates may be incomplete. |
| `fe_year_end_origination_flag`, `fe_economic_cycle_proxy` | calendar period indicators | Supports originations and policy-cycle analysis. | Proxy is not a macroeconomic variable. |

## Interaction Features and Business Flags

| Feature | Formula / purpose | Expected relationship with default | Possible risk |
| --- | --- | --- | --- |
| `fe_income_x_loan_amount`, `fe_income_x_interest_rate` | Joint affordability and pricing context | Large exposures at constrained income may elevate risk. | Scale-sensitive; assess later, not selected now. |
| `fe_grade_x_interest_rate`, `fe_grade_x_fico` | Links lender risk grade to coupon and bureau strength | Captures risk/pricing alignment. | Grade may embed an existing model or policy. |
| `fe_loan_amount_x_credit_utilization`, `fe_interest_rate_x_dti`, `fe_dti_x_revolving_utilization`, `fe_fico_x_delinquencies` | Joint leverage, liquidity, and credit-history stress | Higher stress combinations are expected to correlate with elevated risk. | Interactions can be unstable and require later validation. |
| `fe_high_debt_risk_flag`, `fe_low_income_risk_flag`, `fe_high_interest_risk_flag`, `fe_high_utilization_flag` | Transparent threshold flags | Indicate affordability or liquidity stress. | Thresholds require policy approval. |
| `fe_poor_credit_history_flag`, `fe_multiple_delinquencies_flag`, `fe_credit_stress_flag`, `fe_aggressive_borrower_flag` | Composite transparent flags | Support operational segmentation and challenge. | Composite flags must be assessed for redundancy and fairness. |

## Validation Controls

The pipeline produces `reports/feature_validation_summary.csv` with data type, missingness, infinity counts, range extrema, and chunk-level uniqueness diagnostics for every engineered feature. Division-by-zero results are deliberately represented as missing rather than infinite. Validation does not impute, winsorise, cap, or delete values.
