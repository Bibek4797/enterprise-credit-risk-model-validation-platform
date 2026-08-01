# Data Understanding Report

## Scope

The review covers the single supplied raw source, `accepted_2007_to_2018Q4.csv`, on a read-only basis. It contains 2,260,701 originated-loan records and 151 source columns. The file is 1.68 GB. No rejected-applicant file or data dictionary was supplied; all classifications below are therefore based on observed field names and LendingClub naming conventions and should be confirmed against authoritative metadata before model development.

## Dataset Overview

The accepted-loan portfolio covers originations from 2007 Q2 to 2018 Q4. It includes application attributes, loan terms, bureau-derived measures, servicing outcomes, collections, recoveries, hardship, and settlement fields. A 20-column analytical read-only view was used for descriptive profiling; the raw file itself remains intact.

## Column and Business Classification

| Classification | Examples | Banking treatment |
| --- | --- | --- |
| Identifiers | `id`, `member_id`, `url` | Traceability only; do not use as predictive drivers. |
| Applicant and financial | `annual_inc`, `emp_length`, `home_ownership`, `verification_status`, `dti` | Potentially available at application, subject to provenance checks. |
| Loan terms | `loan_amnt`, `funded_amnt`, `term`, `int_rate`, `grade`, `sub_grade`, `purpose`, `issue_d` | Decision, pricing, and booking fields. `grade` may reflect LendingClub’s own risk process. |
| Credit history | `fico_range_low`, `fico_range_high`, `inq_last_6mths`, `open_acc`, `revol_bal`, `revol_util`, `delinq_2yrs` | Potential application-time bureau inputs; confirm as-of date. |
| Payment and performance | `loan_status`, `last_pymnt_d`, `last_pymnt_amnt`, `out_prncp`, `total_pymnt` | Post-origination performance; unsuitable for an application scorecard. |
| Recoveries and collections | `recoveries`, `collection_recovery_fee`, `collections_12_mths_ex_med`, settlement and hardship fields | Outcome/servicing fields; not eligible at application. |

## Target Candidates and Recommendation

`loan_status` is the primary outcome candidate. For descriptive EDA, the observed default flag is defined as `Charged Off` or `Default`. This is an unconditional, all-vintage measure—not a production PD target—because the portfolio contains current and immature accounts.

For eventual PD development, a target must use an approved default definition, a fixed performance window, an observation date, appropriate exclusions, and treatment of incomplete outcomes. Current accounts originated near the dataset end should not be treated as non-defaulted mature exposures.

## Leakage Assessment

The following fields are post-decision or post-outcome and must be excluded from any application-time model: `loan_status`, `out_prncp`, `total_pymnt`, `total_pymnt_inv`, `total_rec_prncp`, `total_rec_int`, `total_rec_late_fee`, `recoveries`, `collection_recovery_fee`, `last_pymnt_d`, `last_pymnt_amnt`, `next_pymnt_d`, `last_credit_pull_d`, `last_fico_range_low`, `last_fico_range_high`, hardship fields, payment-plan fields, and debt-settlement fields.

`grade`, `sub_grade`, and `int_rate` require governance judgement. They may encode the lender’s existing underwriting or pricing decisions. They are valid for portfolio EDA but should be challenged carefully as model inputs to avoid circularity or policy leakage.

## Missingness and Data-Type Observations

Within the EDA field set, `emp_length` has 146,940 missing values (6.50%). `revol_util` and `dti` have low missingness (0.081% and 0.077% respectively); all other reviewed fields have negligible missingness. Numeric fields are largely correctly represented. Percentage fields require parsing from percentage text for analysis only, and `issue_d` is a month-year string that requires date parsing for temporal reporting. No values were imputed, corrected, removed, or written back to raw data.

## Initial Portfolio Insights

The portfolio is consumer-installment lending with extensive post-origination servicing detail. It is sufficiently rich for application-risk and behavioural-risk demonstrations, but the co-existence of booking, pricing, servicing, recovery, and hardship fields makes temporal controls central. Any banking-grade use must begin with an approved data dictionary, field-level lineage, and a strict definition of what was known at the decision timestamp.
