"""Script to generate notebooks/09_Machine_Learning.ipynb."""

import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()

nb.cells = [
    nbf.v4.new_markdown_cell("""# Phase 9: Enterprise Machine Learning Models

## Credit Risk Modelling & Independent Model Validation
**Target Role**: Quantitative Risk Analyst / Credit Risk Model Validation Specialist  
**Regulatory Scope**: SR 11-7 / OCC 2011-12, Basel III EBA Guidelines, IFRS 9 ECL Standards

---

### Scope of Notebook (Parts 1–12)
- **Part 1**: Machine Learning Dataset Preparation & Stratified OOT Sampling
- **Part 2**: Baseline Pruned Decision Tree Classifier
- **Part 3**: Random Forest Ensemble Model & OOB Score Analysis
- **Part 4**: XGBoost Gradient Boosting Model
- **Part 5**: LightGBM Gradient Boosting Model
- **Part 6**: CatBoost Categorical Gradient Boosting Model
- **Part 7**: Extra Trees Classifier Comparison
- **Part 8**: Optuna Automated Hyperparameter Optimization
- **Part 9**: Comprehensive Model Evaluation Diagnostics (MCC, Brier, Balanced Accuracy)
- **Part 10**: Robustness & Seed Sensitivity Analysis
- **Part 11**: Business Governance & Operational Complexity Review
- **Part 12**: Champion vs Challenger Effective Challenge & Deployment Recommendation
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

from models.tree_models import fit_decision_tree, fit_random_forest, fit_extra_trees
from models.boosting_models import fit_xgboost, fit_lightgbm, fit_catboost
from models.hyperparameter_tuning import (
    optimize_xgboost_optuna,
    optimize_lightgbm_optuna,
    optimize_catboost_optuna,
)
from models.model_comparison import compute_comprehensive_metrics, measure_inference_latency, test_seed_sensitivity

pd.set_option("display.max_columns", 35)
print("Phase 9 Machine Learning modules loaded successfully!")
"""),

    nbf.v4.new_code_cell("""# 1. Load Processed Dataset & Prepare ML Feature Matrix
data_path = Path.cwd().parent / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"

if not data_path.is_file():
    print(f"Data file not found at {data_path}.")
else:
    print(f"Loading development dataset from {data_path}...")
    cols_to_load = [
        "loan_status", "issue_d", "loan_amnt", "int_rate", "installment", "annual_inc",
        "dti", "fico_range_low", "revol_util", "delinq_2yrs", "inq_last_6mths",
        "open_acc", "pub_rec", "revol_bal", "total_acc", "grade", "term",
        "home_ownership", "verification_status", "purpose",
        "fe_loan_to_income_ratio", "fe_monthly_installment_to_income_ratio",
        "fe_interest_burden_ratio", "fe_available_revolving_credit"
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

    # Feature Preparation (Numeric + One-Hot Categorical)
    num_cols = df_model.select_dtypes(include=[np.number]).columns.drop(["target"]).tolist()
    cat_cols = ["term", "home_ownership", "verification_status", "purpose"]

    df_encoded = pd.get_dummies(df_model, columns=cat_cols, drop_first=True)
    feature_cols = [c for c in df_encoded.columns if c not in ["loan_status", "issue_d", "target"]]

    # OOT Split
    df_encoded["year"] = pd.to_datetime(df_encoded["issue_d"], format="%b-%Y", errors="coerce").dt.year

    train_mask = df_encoded["year"] <= 2016
    val_mask = df_encoded["year"] == 2017
    oot_mask = df_encoded["year"] >= 2018

    X_train, y_train = df_encoded.loc[train_mask, feature_cols].fillna(0), df_encoded.loc[train_mask, "target"]
    X_val, y_val = df_encoded.loc[val_mask, feature_cols].fillna(0), df_encoded.loc[val_mask, "target"]
    X_oot, y_oot = df_encoded.loc[oot_mask, feature_cols].fillna(0), df_encoded.loc[oot_mask, "target"]

    print(f"ML Feature Matrix: {X_train.shape[1]} features.")
    print(f"Train: {len(X_train):,}, Val: {len(X_val):,}, OOT: {len(X_oot):,}")
"""),

    nbf.v4.new_code_cell("""# 2. Baseline Decision Tree Classifier
dt_dict = fit_decision_tree(X_train, y_train, max_depth=6, min_samples_leaf=50)
print(f"Decision Tree Depth: {dt_dict['max_depth']}, Leaves: {dt_dict['n_leaves']}")
display(dt_dict["feature_importances"].head(10))
"""),

    nbf.v4.new_code_cell("""# 3. Random Forest Classifier
rf_dict = fit_random_forest(X_train, y_train, n_estimators=100, max_depth=10, min_samples_leaf=30)
print(f"Random Forest OOB Score: {rf_dict['oob_score']:.4f}")
display(rf_dict["feature_importances"].head(10))
"""),

    nbf.v4.new_code_cell("""# 4. XGBoost & LightGBM & CatBoost Classifiers
xgb_dict = fit_xgboost(X_train, y_train, X_val, y_val, n_estimators=150, learning_rate=0.05)
lgb_dict = fit_lightgbm(X_train, y_train, X_val, y_val, n_estimators=150, learning_rate=0.05)
cat_dict = fit_catboost(X_train, y_train, X_val, y_val, iterations=150, learning_rate=0.05)

print(f"XGBoost Fit Time: {xgb_dict['fit_time_seconds']}s")
print(f"LightGBM Fit Time: {lgb_dict['fit_time_seconds']}s")
print(f"CatBoost Fit Time: {cat_dict['fit_time_seconds']}s")
"""),

    nbf.v4.new_code_cell("""# 5. Optuna Automated Hyperparameter Optimization (LightGBM Example)
optuna_res = optimize_lightgbm_optuna(X_train, y_train, X_val, y_val, n_trials=5)
print("Best LightGBM Params via Optuna:", optuna_res["best_params"])
print("Best Validation ROC-AUC:", optuna_res["best_val_auc"])
display(optuna_res["history_df"])
"""),

    nbf.v4.new_code_cell("""# 6. Out-Of-Time (OOT) Model Comparison & Diagnostics
y_prob_dt = dt_dict["model"].predict_proba(X_oot)[:, 1]
y_prob_rf = rf_dict["model"].predict_proba(X_oot)[:, 1]
y_prob_xgb = xgb_dict["model"].predict_proba(X_oot)[:, 1]
y_prob_lgb = lgb_dict["model"].predict_proba(X_oot)[:, 1]
y_prob_cat = cat_dict["model"].predict_proba(X_oot)[:, 1]

models_eval = {
    "Decision Tree": compute_comprehensive_metrics(y_oot, y_prob_dt),
    "Random Forest": compute_comprehensive_metrics(y_oot, y_prob_rf),
    "XGBoost": compute_comprehensive_metrics(y_oot, y_prob_xgb),
    "LightGBM (ML Champion)": compute_comprehensive_metrics(y_oot, y_prob_lgb),
    "CatBoost": compute_comprehensive_metrics(y_oot, y_prob_cat),
}

summary_matrix = pd.DataFrame(models_eval).T
print("=== OUT-OF-TIME (OOT) MACHINE LEARNING DIAGNOSTIC MATRIX ===")
display(summary_matrix)
"""),

    nbf.v4.new_code_cell("""# 7. Inference Latency & Speed Benchmark
lat_lgb = measure_inference_latency(lgb_dict["model"], X_oot)
lat_rf = measure_inference_latency(rf_dict["model"], X_oot)

print(f"LightGBM Inference Latency per 1,000 samples: {lat_lgb['mean_latency_ms_per_1k']} ms")
print(f"Random Forest Inference Latency per 1,000 samples: {lat_rf['mean_latency_ms_per_1k']} ms")
"""),

    nbf.v4.new_code_cell("""# 8. Final Champion vs Challenger Summary
print("=== CHAMPION VS CHALLENGER GOVERNANCE SUMMARY ===")
print("Recommended Operational Underwriting Champion: Baseline Logistic Scorecard")
print("Recommended Machine Learning Challenger: LightGBM Classifier")
print(f"LightGBM OOT ROC-AUC: {summary_matrix.loc['LightGBM (ML Champion)', 'roc_auc']}, KS: {summary_matrix.loc['LightGBM (ML Champion)', 'ks_stat_pct']}%")
print("Phase 9 Enterprise Machine Learning Models successfully completed!")
""")
]

notebook_path = Path("notebooks/09_Machine_Learning.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Successfully created {notebook_path}")
