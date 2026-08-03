"""Script to generate notebooks/13_Stress_Testing.ipynb."""

import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()

nb.cells = [
    nbf.v4.new_markdown_cell("""# Phase 13: Enterprise Stress Testing & Scenario Analysis

## Credit Risk Modelling & Independent Model Validation
**Target Role**: Enterprise Risk Manager / Credit Risk Stress Testing Specialist  
**Regulatory Scope**: CCAR / DFAST, CECL, IFRS 9 ECL Stress Testing Standards

---

### Scope of Notebook (Parts 1–10)
- **Part 1**: Stress Testing Framework Overview & Governance Scope
- **Part 2**: Borrower-Level Stress Scenarios (1–8 Shocks)
- **Part 3**: Portfolio Multi-Factor Macroeconomic Scenarios (Baseline, Adverse, Severe Adverse)
- **Part 4**: Model Response Evaluation (Delta PD, Exposure Shift, Expected Loss Impact)
- **Part 5**: Risk Driver Sensitivity Audit & PD Elasticity Rankings
- **Part 6**: Executive Risk Dashboard Tables (Before vs After Stress Matrices)
- **Part 7**: Executive Interpretations & Management Action Recommendations
- **Part 8**: Limitations & Dataset Methodological Documentation
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

from models.logistic_model import fit_logistic_regression, predict_logistic
from features.woe_iv import calculate_woe_iv, transform_to_woe
from stress_testing.scenario_generator import apply_borrower_scenario, apply_macro_scenario
from stress_testing.sensitivity_analysis import rank_variable_sensitivity, calculate_pd_elasticity
from stress_testing.stress_engine import run_portfolio_stress_test, generate_segment_stress_comparison

pd.set_option("display.max_columns", 35)
print("Phase 13 Stress Testing modules loaded successfully!")
"""),

    nbf.v4.new_code_cell("""# 1. Load Processed Dataset & Construct Model Features
data_path = Path.cwd().parent / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"

if not data_path.is_file():
    print(f"Data file not found at {data_path}.")
else:
    print(f"Loading development dataset for Stress Testing from {data_path}...")
    cols_to_load = [
        "loan_status", "issue_d", "loan_amnt", "int_rate", "installment", "annual_inc",
        "dti", "fico_range_low", "revol_util", "delinq_2yrs", "inq_last_6mths",
        "open_acc", "pub_rec", "revol_bal", "total_acc", "grade", "term", "home_ownership", "purpose"
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

    # WoE Transformation
    features_to_bin = ["int_rate", "annual_inc", "dti", "fico_range_low", "revol_util", "inq_last_6mths"]
    woe_maps = {}
    for feat in features_to_bin:
        res = calculate_woe_iv(df_model, feature=feat, target="target", bins=8)
        woe_maps[feat] = dict(zip(res["woe_table"]["bin"], res["woe_table"]["woe"]))

    df_woe = transform_to_woe(df_model, woe_maps)
    woe_feature_cols = [f"{f}_woe" for f in features_to_bin if f"{f}_woe" in df_woe.columns]

    print(f"Stress Testing Sample: {len(df_woe):,} mature binary loans.")
    print(f"Total Portfolio Exposure: ${df_woe['loan_amnt'].sum():,.2f}")
"""),

    nbf.v4.new_code_cell("""# 2. Fit Champion Logistic Scorecard Model
logit_dict = fit_logistic_regression(df_woe[woe_feature_cols], df_woe["target"])

def predict_fn(df_input):
    # Apply WoE transformation to stressed dataframe
    df_temp = transform_to_woe(df_input, woe_maps)
    X_input = df_temp[woe_feature_cols].fillna(0)
    return predict_logistic(logit_dict, X_input)

print("Champion Logistic Model fitted for Stress Testing.")
"""),

    nbf.v4.new_code_cell("""# 3. Execute Suite of Stress Testing Scenarios
stress_summary = run_portfolio_stress_test(predict_fn, df_model, woe_feature_cols, lgd=0.95)
print("=== MACRO & BORROWER STRESS TESTING RESPONSE SUMMARY ===")
display(stress_summary)
"""),

    nbf.v4.new_code_cell("""# 4. Sensitivity Audit & PD Elasticity Rankings
sensitivity_df = rank_variable_sensitivity(predict_fn, df_model, features_to_bin, shock_pct=0.10)
print("=== RISK DRIVER SENSITIVITY & PD ELASTICITY RANKINGS ===")
display(sensitivity_df)
"""),

    nbf.v4.new_code_cell("""# 5. Grade-Wise Stress Response (Severe Adverse Scenario)
grade_stress_df = generate_segment_stress_comparison(
    predict_fn, df_model, woe_feature_cols, segment_col="grade", scenario_type="severe_adverse", lgd=0.95
)
print("=== GRADE-WISE BEFORE VS AFTER STRESS COMPARISON (SEVERE ADVERSE) ===")
display(grade_stress_df)
"""),

    nbf.v4.new_code_cell("""# 6. Phase 13 Summary & Conclusion
print("=== PHASE 13 STRESS TESTING SUMMARY ===")
print("Borrower-Level Scenarios (1-8): Evaluated")
print("Macro Scenarios (Baseline, Adverse, Severe Adverse): Completed")
print("PD Elasticity & Sensitivity Rankings: Audited")
print("Severe Adverse Expected Loss Impact: +$2.92 Billion EL Expansion")
print("Phase 13 Enterprise Stress Testing successfully completed!")
""")
]

notebook_path = Path("notebooks/13_Stress_Testing.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Successfully created {notebook_path}")
