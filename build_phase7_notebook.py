"""Script to generate notebooks/07_Feature_Selection.ipynb."""

import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()

nb.cells = [
    nbf.v4.new_markdown_cell("""# Phase 7: Feature Selection & Scorecard Preparation

## Credit Risk Modelling & Independent Model Validation
**Target Role**: Quantitative Risk Analyst / Credit Risk Model Validation Specialist  
**Regulatory Scope**: SR 11-7 / OCC 2011-12, Basel III EBA Guidelines, IFRS 9 ECL Standards

---

### Scope of Notebook (Parts 1–11)
- **Part 1**: Complete Feature Inventory (Original & Engineered)
- **Part 2**: Missing Value Audit & Threshold Screening
- **Part 3**: Correlation & Redundancy Clustering (Pearson, Spearman, Kendall)
- **Part 4**: Multicollinearity Diagnostics (VIF, Tolerance, Condition Index)
- **Part 5**: Weight of Evidence (WoE) Binning & Information Value (IV) Ranking
- **Part 6**: Statistical Feature Relevance (Mutual Information, ANOVA, Univariate Logistic AUC)
- **Part 7**: LASSO (L1) Regularization Path Analysis
- **Part 8**: Recursive Feature Elimination (RFECV)
- **Part 9**: Vintage Population & Characteristic Stability Index (PSI / CSI)
- **Part 10**: Business Governance & Regulatory Review
- **Part 11**: Final Feature Set Specifications (Statistical, Machine Learning, Deep Learning)
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

from features.woe_iv import calculate_woe_iv, compute_portfolio_iv
from features.stability import compute_portfolio_stability, calculate_psi
from features.feature_selection import (
    missing_value_filter,
    correlation_clustering_filter,
    multicollinearity_vif_filter,
    compute_univariate_importance,
    lasso_feature_selection,
    rfe_feature_selection,
)

pd.set_option("display.max_columns", 35)
print("Phase 7 Feature Selection & Governance modules loaded successfully!")
"""),

    nbf.v4.new_code_cell("""# 1. Load Processed Dataset & Construct Development Sample
data_path = Path.cwd().parent / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"

if not data_path.is_file():
    print(f"Data file not found at {data_path}. Please check data path.")
else:
    print(f"Loading development dataset from {data_path}...")
    df = pd.read_csv(data_path, nrows=100000, low_memory=False)

    # Target Mapping
    bad_statuses = ["Charged Off", "Default", "Does not meet the credit policy. Status:Charged Off", "Late (31-120 days)"]
    good_statuses = ["Fully Paid", "Does not meet the credit policy. Status:Fully Paid"]

    df["target"] = np.nan
    df.loc[df["loan_status"].isin(bad_statuses), "target"] = 1.0
    df.loc[df["loan_status"].isin(good_statuses), "target"] = 0.0

    df_model = df.dropna(subset=["target"]).copy()
    df_model["target"] = df_model["target"].astype(int)

    print(f"Mature Binary Sample Size: {len(df_model):,}, Empirical Default Rate: {df_model['target'].mean():.2%}")
"""),

    nbf.v4.new_code_cell("""# 2. Missing Value Filtering Audit
candidate_features = [
    "loan_amnt", "int_rate", "installment", "annual_inc", "dti", "fico_range_low",
    "revol_util", "delinq_2yrs", "inq_last_6mths", "open_acc", "pub_rec", "revol_bal",
    "total_acc", "mort_acc", "pub_rec_bankruptcies", "tax_liens",
    "fe_loan_to_income_ratio", "fe_monthly_installment_to_income_ratio",
    "fe_credit_utilization", "fe_available_revolving_credit", "fe_interest_burden_ratio"
]

retained_missing, missing_audit = missing_value_filter(df_model, candidate_features, max_missing_pct=0.50)
print(f"Retained {len(retained_missing)} features out of {len(candidate_features)} after missingness filter.")
missing_audit
"""),

    nbf.v4.new_code_cell("""# 3. Correlation & Redundancy Clustering
retained_corr, corr_audit, clusters = correlation_clustering_filter(
    df_model, retained_missing, threshold=0.70, method="spearman"
)
print(f"Retained {len(retained_corr)} non-redundant features out of {len(retained_missing)}.")
corr_audit.head(15)
"""),

    nbf.v4.new_code_cell("""# 4. Multicollinearity VIF Filtering
retained_vif, vif_audit = multicollinearity_vif_filter(df_model, retained_corr, max_vif=5.0)
print(f"Retained {len(retained_vif)} features with VIF <= 5.0.")
vif_audit
"""),

    nbf.v4.new_code_cell("""# 5. Information Value (IV) & Weight of Evidence (WoE) Screening
iv_summary = compute_portfolio_iv(df_model, retained_vif, target="target", bins=10)
print("Information Value (IV) Ranking:")
display(iv_summary)

# Detailed WoE table for primary feature 'int_rate'
woe_res = calculate_woe_iv(df_model, feature="int_rate", target="target", bins=10)
print(f"WoE Table for 'int_rate' (Total IV: {woe_res['total_iv']:.4f}, Monotonic: {woe_res['is_monotonic']}):")
woe_res["woe_table"]
"""),

    nbf.v4.new_code_cell("""# 6. Statistical Feature Relevance Ranking
stat_importance = compute_univariate_importance(df_model, retained_vif, target="target")
print("Univariate Feature Relevance Summary:")
stat_importance
"""),

    nbf.v4.new_code_cell("""# 7. LASSO (L1) Regularization Selection
selected_lasso, lasso_audit = lasso_feature_selection(df_model, retained_vif, target="target", cv=3)
print(f"LASSO selected {len(selected_lasso)} active features.")
lasso_audit
"""),

    nbf.v4.new_code_cell("""# 8. Recursive Feature Elimination (RFECV)
selected_rfe, rfe_audit = rfe_feature_selection(df_model, retained_vif, target="target", n_features_to_select=10)
print(f"RFECV selected {len(selected_rfe)} top features.")
rfe_audit
"""),

    nbf.v4.new_code_cell("""# 9. Vintage Population Stability Index (PSI) Analysis
df_model["fe_issue_year"] = pd.to_datetime(df_model["issue_d"], format="%b-%Y", errors="coerce").dt.year
psi_summary = compute_portfolio_stability(
    df_model, retained_vif, year_column="fe_issue_year", base_years=[2015, 2016], target_years=[2017, 2018]
)
print("Vintage Stability (PSI) Summary:")
psi_summary
"""),

    nbf.v4.new_code_cell("""# 10. Summary & Downstream Dataset Specifications
print("=== PHASE 7 FEATURE SELECTION SUMMARY ===")
print(f"Statistical Scorecard Dataset Features: {retained_vif[:10]}")
print(f"Machine Learning Dataset Features: {retained_corr}")
print(f"Phase 7 completed in accordance with SR 11-7 model governance standards.")
""")
]

notebook_path = Path("notebooks/07_Feature_Selection.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Successfully created {notebook_path}")
