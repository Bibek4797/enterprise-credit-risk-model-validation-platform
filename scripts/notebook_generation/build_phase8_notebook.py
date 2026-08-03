"""Script to generate notebooks/08_Baseline_Statistical_Models.ipynb."""

import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()

nb.cells = [
    nbf.v4.new_markdown_cell("""# Phase 8: Baseline Statistical Models

## Credit Risk Modelling & Independent Model Validation
**Target Role**: Quantitative Risk Analyst / Credit Risk Model Validation Specialist  
**Regulatory Scope**: SR 11-7 / OCC 2011-12, Basel III EBA Guidelines, IFRS 9 ECL Standards

---

### Scope of Notebook (Parts 1–8)
- **Part 1**: Data Preparation & Out-Of-Time (OOT) Split Construction
- **Part 2**: Logistic Regression Development, Parameter Inference & Odds Ratios
- **Part 3**: Probit Regression Benchmark & Average Marginal Effects (AME)
- **Part 4**: Regularized Logistic Models (LASSO L1, Ridge L2, Elastic Net CV)
- **Part 5**: Comprehensive Model Diagnostics (ROC-AUC, Gini, KS, Brier, Calibration, Lift/Gain)
- **Part 6**: Statistical Validation (Multicollinearity, Residuals, Hosmer-Lemeshow Test)
- **Part 7**: Business Interpretation & Deployment Review
- **Part 8**: Champion Baseline Model Selection & Recommendation
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

from features.woe_iv import calculate_woe_iv, transform_to_woe
from models.logistic_model import fit_logistic_regression, predict_logistic
from models.probit_model import fit_probit_regression, compare_logistic_probit
from models.regularized_models import fit_penalized_logistic_models, predict_penalized
from validation.model_metrics import evaluate_all_metrics, calculate_lift_gain

pd.set_option("display.max_columns", 35)
print("Phase 8 Statistical Modelling modules loaded successfully!")
"""),

    nbf.v4.new_code_cell("""# 1. Load Processed Dataset & Construct OOT Split
data_path = Path.cwd().parent / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"

if not data_path.is_file():
    print(f"Data file not found at {data_path}.")
else:
    print(f"Loading development dataset from {data_path}...")
    cols_to_load = [
        "loan_status", "issue_d", "loan_amnt", "int_rate", "installment", "annual_inc",
        "dti", "fico_range_low", "revol_util", "delinq_2yrs", "inq_last_6mths",
        "open_acc", "pub_rec", "revol_bal", "total_acc", "grade", "term",
        "home_ownership", "verification_status", "purpose"
    ]
    df = pd.read_csv(data_path, usecols=cols_to_load, nrows=120000, low_memory=False)

    # Target Mapping
    bad_statuses = ["Charged Off", "Default", "Does not meet the credit policy. Status:Charged Off", "Late (31-120 days)"]
    good_statuses = ["Fully Paid", "Does not meet the credit policy. Status:Fully Paid"]

    df["target"] = np.nan
    df.loc[df["loan_status"].isin(bad_statuses), "target"] = 1.0
    df.loc[df["loan_status"].isin(good_statuses), "target"] = 0.0

    df_model = df.dropna(subset=["target"]).copy()
    df_model["target"] = df_model["target"].astype(int)

    # Temporal OOT Split using issue_d
    df_model["year"] = pd.to_datetime(df_model["issue_d"], format="%b-%Y", errors="coerce").dt.year

    train_mask = df_model["year"] <= 2016
    val_mask = df_model["year"] == 2017
    oot_mask = df_model["year"] >= 2018

    print(f"Train Set (2007-2016): {train_mask.sum():,} loans, Default Rate: {df_model.loc[train_mask, 'target'].mean():.2%}")
    print(f"Val Set (2017): {val_mask.sum():,} loans, Default Rate: {df_model.loc[val_mask, 'target'].mean():.2%}")
    print(f"OOT Set (2018): {oot_mask.sum():,} loans, Default Rate: {df_model.loc[oot_mask, 'target'].mean():.2%}")
"""),

    nbf.v4.new_code_cell("""# 2. Build Feature Set for Statistical Modelling (WoE Encoding)
features_to_bin = ["int_rate", "annual_inc", "dti", "fico_range_low", "revol_util", "inq_last_6mths"]

woe_maps = {}
for feat in features_to_bin:
    res = calculate_woe_iv(df_model[train_mask], feature=feat, target="target", bins=8)
    mapping = dict(zip(res["woe_table"]["bin"], res["woe_table"]["woe"]))
    woe_maps[feat] = mapping

df_woe = transform_to_woe(df_model, woe_maps)
woe_feature_cols = [f"{f}_woe" for f in features_to_bin if f"{f}_woe" in df_woe.columns]

X_train = df_woe.loc[train_mask, woe_feature_cols].fillna(0.0)
y_train = df_woe.loc[train_mask, "target"]

X_oot = df_woe.loc[oot_mask, woe_feature_cols].fillna(0.0)
y_oot = df_woe.loc[oot_mask, "target"]

print(f"Statistical Feature Set shape: {X_train.shape}")
"""),

    nbf.v4.new_code_cell("""# 3. Fit Production Logistic Regression Model
logit_dict = fit_logistic_regression(X_train, y_train, add_constant=True)
print("=== LOGISTIC REGRESSION SUMMARY TABLE ===")
display(logit_dict["summary_table"])
print("Fit Metrics:", logit_dict["fit_metrics"])
"""),

    nbf.v4.new_code_cell("""# 4. Fit Probit Regression Model & Compare
probit_dict = fit_probit_regression(X_train, y_train, add_constant=True)
print("=== PROBIT REGRESSION SUMMARY TABLE ===")
display(probit_dict["summary_table"])

comp_df = compare_logistic_probit(logit_dict["summary_table"], probit_dict["summary_table"])
print("=== LOGISTIC VS PROBIT COEFFICIENT RATIOS ===")
display(comp_df)
"""),

    nbf.v4.new_code_cell("""# 5. Fit Regularized Models (LASSO, Ridge, Elastic Net)
penalized_dict = fit_penalized_logistic_models(X_train, y_train, cv=3)
print("=== PENALIZED LOGISTIC REGRESSION COEFFICIENTS ===")
display(penalized_dict["coef_table"])
print("Summary Metrics:", penalized_dict["summary_metrics"])
"""),

    nbf.v4.new_code_cell("""# 6. Comprehensive OOT Model Evaluation & Diagnostics
y_prob_logit = predict_logistic(logit_dict, X_oot)
y_prob_probit = probit_dict["model_result"].predict(sm.add_constant(X_oot) if "const" not in X_oot.columns else X_oot)
y_prob_lasso = predict_penalized(penalized_dict, X_oot, model_type="lasso")

metrics_logit = evaluate_all_metrics(y_oot, y_prob_logit)
metrics_probit = evaluate_all_metrics(y_oot, y_prob_probit)
metrics_lasso = evaluate_all_metrics(y_oot, y_prob_lasso)

diag_summary = pd.DataFrame([
    {"Model": "Logistic Regression (Champion)", **metrics_logit},
    {"Model": "Probit Regression", **metrics_probit},
    {"Model": "LASSO Logistic (L1)", **metrics_lasso},
])
print("=== OUT-OF-TIME (OOT) MODEL DIAGNOSTIC SUMMARY ===")
display(diag_summary)
"""),

    nbf.v4.new_code_cell("""# 7. Lift & Gain Table Construction
lg_table = calculate_lift_gain(y_oot, y_prob_logit, quantiles=10)
print("=== CUMULATIVE LIFT & GAIN TABLE (CHAMPION LOGISTIC MODEL) ===")
display(lg_table)
"""),

    nbf.v4.new_code_cell("""# 8. Champion Baseline Selection Summary
print("=== CHAMPION BASELINE RECOMMENDATION ===")
print("Recommended Model: Unpenalized Logistic Regression (Scorecard Architecture)")
print(f"Key OOT Performance: ROC-AUC = {metrics_logit['roc_auc']}, KS Stat = {metrics_logit['ks_stat']}%, Gini = {metrics_logit['gini']}")
print("Passes Hosmer-Lemeshow Calibration Test:", metrics_logit['hl_is_calibrated'])
print("Phase 8 Baseline Statistical Models successfully completed!")
""")
]

notebook_path = Path("notebooks/08_Baseline_Statistical_Models.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Successfully created {notebook_path}")
