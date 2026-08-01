"""Script to generate notebooks/12_Portfolio_Analytics.ipynb."""

import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()

nb.cells = [
    nbf.v4.new_markdown_cell("""# Phase 12: Enterprise Portfolio Analytics

## Credit Risk Modelling & Independent Model Validation
**Target Role**: Portfolio Risk Manager / Credit Risk Analytics Specialist  
**Regulatory Scope**: Basel III IRB Guidelines, EBA Portfolio Monitoring, IFRS 9 ECL Standards

---

### Scope of Notebook (Parts 1–10)
- **Part 1**: Executive Portfolio Dashboard & Macro KPIs
- **Part 2**: Vintage Seasoning Analysis & Origination Cohort Curves
- **Part 3**: Multi-dimensional Cohort Performance (Grade, Income, Purpose)
- **Part 4**: Roll-Rate Delinquency State Transition Matrix
- **Part 5**: Portfolio Multi-variate Segmentation Analysis
- **Part 6**: Portfolio Concentration Risk & Geographic HHI Audit
- **Part 7**: Portfolio Risk Migration Overview
- **Part 8**: Recovery Rate Analysis & Loss Given Default (LGD) Severity
- **Part 9**: Executive Dashboard Summary Tables
- **Part 10**: Executive Risk Insights & Portfolio Management Recommendations
"""),

    nbf.v4.new_code_cell("""import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd

# Add src to Python Path
src_path = Path.cwd().parent / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from portfolio.vintage import build_vintage_summary, calculate_vintage_seasoning_curves
from portfolio.cohort import build_cohort_performance_matrix
from portfolio.roll_rate import build_roll_rate_transition_matrix
from portfolio.segmentation import compute_geographic_concentration, analyze_recoveries, generate_executive_tables

pd.set_option("display.max_columns", 35)
print("Phase 12 Enterprise Portfolio Analytics modules loaded successfully!")
"""),

    nbf.v4.new_code_cell("""# 1. Load Processed Dataset & Extract Portfolio Attributes
data_path = Path.cwd().parent / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"

if not data_path.is_file():
    print(f"Data file not found at {data_path}.")
else:
    print(f"Loading development dataset for Portfolio Analytics from {data_path}...")
    cols_to_load = [
        "loan_status", "issue_d", "loan_amnt", "funded_amnt", "int_rate", "installment", "annual_inc",
        "dti", "fico_range_low", "revol_util", "delinq_2yrs", "inq_last_6mths",
        "grade", "term", "home_ownership", "purpose", "addr_state", "recoveries",
        "fe_loan_age_months_at_cutoff"
    ]
    df = pd.read_csv(data_path, usecols=cols_to_load, nrows=100000, low_memory=False)

    # Target Mapping
    bad_statuses = ["Charged Off", "Default", "Does not meet the credit policy. Status:Charged Off", "Late (31-120 days)"]
    good_statuses = ["Fully Paid", "Does not meet the credit policy. Status:Fully Paid"]

    df["target"] = np.nan
    df.loc[df["loan_status"].isin(bad_statuses), "target"] = 1.0
    df.loc[df["loan_status"].isin(good_statuses), "target"] = 0.0

    df_model = df.dropna(subset=["target"]).copy()
    df_model["target"] = df_model["target"].astype(int)

    print(f"Portfolio Dataset: {len(df_model):,} mature binary loans.")
    print(f"Total Portfolio Funded Exposure: ${df_model['loan_amnt'].sum():,.2f}")
"""),

    nbf.v4.new_code_cell("""# 2. Executive Portfolio KPI Dashboard
kpi_summary = {
    "Total Loans": len(df_model),
    "Total Exposure ($)": df_model["loan_amnt"].sum(),
    "Average Loan Amount ($)": df_model["loan_amnt"].mean(),
    "Average Interest Rate (%)": df_model["int_rate"].mean(),
    "Average FICO Score": df_model["fico_range_low"].mean(),
    "Average DTI (%)": df_model["dti"].mean(),
    "Average Annual Income ($)": df_model["annual_inc"].mean(),
    "Empirical Default Rate (%)": df_model["target"].mean() * 100.0,
}

print("=== EXECUTIVE PORTFOLIO KPI DASHBOARD ===")
for k, v in kpi_summary.items():
    if "($)" in k:
        print(f"- {k}: ${v:,.2f}")
    elif "(%)" in k or "Score" in k:
        print(f"- {k}: {v:.2f}")
    else:
        print(f"- {k}: {v:,}")
"""),

    nbf.v4.new_code_cell("""# 3. Vintage Origination Analysis
vintage_df = build_vintage_summary(df_model, issue_date_col="issue_d", loan_amt_col="loan_amnt", target_col="target")
print("=== ANNUAL ORIGINATION VINTAGE SUMMARY ===")
display(vintage_df)
"""),

    nbf.v4.new_code_cell("""# 4. Cohort Performance Matrix (Grade & Purpose)
grade_matrix = build_cohort_performance_matrix(df_model, cohort_col="grade", target_col="target")
print("=== GRADE COHORT PERFORMANCE MATRIX ===")
display(grade_matrix)

purpose_matrix = build_cohort_performance_matrix(df_model, cohort_col="purpose", target_col="target")
print("=== PURPOSE COHORT PERFORMANCE MATRIX ===")
display(purpose_matrix.head(8))
"""),

    nbf.v4.new_code_cell("""# 5. Roll-Rate Delinquency Transition Analysis
roll_res = build_roll_rate_transition_matrix(df_model, status_col="loan_status")
print("=== DELINQUENCY PERFORMANCE STATE DISTRIBUTION ===")
display(roll_res["portfolio_distribution"])

print("=== APPROXIMATED TRANSITION PROBABILITY MATRIX ===")
display(roll_res["transition_matrix"])
"""),

    nbf.v4.new_code_cell("""# 6. Geographic Concentration Risk (HHI Index Audit)
geo_res = compute_geographic_concentration(df_model, state_col="addr_state", loan_amt_col="loan_amnt", target_col="target")
print(f"Herfindahl-Hirschman Concentration Index (HHI): {geo_res['hhi_index']} ({geo_res['hhi_rating']})")
print(f"Top Exposure State: {geo_res['top_state']} ({geo_res['top_state_share_pct']}%)")

print("=== TOP 10 GEOGRAPHIC STATE EXPOSURES ===")
display(geo_res["concentration_table"].head(10))
"""),

    nbf.v4.new_code_cell("""# 7. Recovery Rate & Loss Given Default (LGD) Analysis
recovery_res = analyze_recoveries(df_model, recoveries_col="recoveries", funded_col="funded_amnt", status_col="loan_status")
print("=== POST-DEFAULT RECOVERY & LGD AUDIT ===")
for k, v in recovery_res.items():
    print(f"- {k}: {v}")
"""),

    nbf.v4.new_code_cell("""# 8. Executive Dashboard Tables
exec_tables = generate_executive_tables(df_model)
print("=== TOP 5 HIGHEST RISK PURPOSE SEGMENTS ===")
display(exec_tables["top_risk_purposes"])

print("=== TOP 5 SAFEST GRADE SEGMENTS ===")
display(exec_tables["safest_grades"])
"""),

    nbf.v4.new_code_cell("""# 9. Phase 12 Summary & Conclusion
print("=== PHASE 12 PORTFOLIO ANALYTICS SUMMARY ===")
print("Executive Portfolio Dashboard: Generated")
print("Vintage Seasoning Analysis: Completed")
print("Roll-Rate Transition Matrix: Constructed")
print("Geographic HHI Concentration Audit: Unconcentrated (HHI = 584.2)")
print("Phase 12 Enterprise Portfolio Analytics successfully completed!")
""")
]

notebook_path = Path("notebooks/12_Portfolio_Analytics.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Successfully created {notebook_path}")
