# Data Quality Assessment

## Scope and Control Objective

This is a read-only initial quality assessment of the 2,260,701-row accepted-loan source. It identifies data-quality risks; it does not clean, impute, deduplicate, or transform the raw dataset.

## Completeness

The reviewed EDA variables are highly complete except for `emp_length` (6.50% missing). `revol_util` (0.081%) and `dti` (0.077%) have low missingness. Missing employment length is materially concentrated enough to require documented treatment, missingness analysis, and business-owner confirmation before any modelling use.

## Validity and Conformance

Loan amounts, income, DTI, FICO bands, and revolving utilisation are stored as numerical fields; interest rate and utilisation require controlled removal of the percent sign for descriptive calculation. `issue_d` is stored as a month-year string and requires controlled date parsing. These are interpretation requirements, not changes to source data.

## Consistency and Temporal Suitability

The dataset combines application data with lifecycle outcomes. The principal quality risk is temporal inconsistency: post-booking fields may appear adjacent to application-time fields and can create data leakage if used without an as-of-date control. The missing data dictionary also prevents authoritative confirmation of units, refresh timing, and business definitions.

## Recommended Controls Before Development

1. Obtain the field-level data dictionary and source lineage.
2. Freeze an application-time extract and explicitly block post-origination fields.
3. Define default, outcome window, maturity rules, and reporting population.
4. Reconcile key balances and loan counts to an independent source where available.
5. Perform outlier, duplicate, invalid-domain, and cross-field rule checks under version-controlled data-quality tests.

No remediation has been performed in this phase.
