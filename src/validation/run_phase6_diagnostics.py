"""Phase 6 Diagnostics Master Script: Runs full statistical and econometric suite."""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

from validation.statistical_tests import (
    calculate_descriptive_stats,
    run_normality_tests,
    generate_normality_plots,
    calculate_csi,
)
from validation.econometrics import (
    calculate_correlations,
    find_high_correlations,
    calculate_vif_and_tolerance,
    calculate_condition_index_and_vdp,
    run_heteroskedasticity_tests,
    run_autocorrelation_tests,
    evaluate_endogeneity_framework,
)
from validation.diagnostics import (
    run_box_tidwell_test,
    generate_linearity_plots,
    calculate_outlier_influence_metrics,
)

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"
TABLES_DIR = ROOT / "reports" / "tables"
FIGURES_DIR = ROOT / "reports" / "figures"


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading processed dataset for Phase 6 Statistical Diagnostics...")
    # Load representative sample or columns to optimize performance
    use_cols = [
        "loan_status", "issue_d", "loan_amnt", "int_rate", "installment", "annual_inc",
        "dti", "fico_range_low", "revol_util", "delinq_2yrs", "inq_last_6mths",
        "open_acc", "pub_rec", "revol_bal", "total_acc", "grade", "term",
        "home_ownership", "verification_status", "purpose",
        "fe_loan_to_income_ratio", "fe_monthly_installment_to_income_ratio",
        "fe_credit_utilization", "fe_available_revolving_credit", "fe_credit_exposure",
        "fe_debt_burden", "fe_credit_history_months"
    ]

    # Load 100,000 rows for high-fidelity statistical validation
    df = pd.read_csv(DATA_PATH, usecols=use_cols, nrows=100000, low_memory=False)
    print(f"Loaded dataset sample of shape: {df.shape}")

    # Part 1: Data Preparation & Target Mapping
    bad_statuses = ["Charged Off", "Default", "Does not meet the credit policy. Status:Charged Off", "Late (31-120 days)"]
    good_statuses = ["Fully Paid", "Does not meet the credit policy. Status:Fully Paid"]
    
    df["target"] = np.nan
    df.loc[df["loan_status"].isin(bad_statuses), "target"] = 1.0
    df.loc[df["loan_status"].isin(good_statuses), "target"] = 0.0

    df_model = df.dropna(subset=["target"]).copy()
    print(f"Binary model sample size (excluding active/current): {len(df_model)} rows. Default rate: {df_model['target'].mean():.4f}")

    numeric_features = [
        "loan_amnt", "int_rate", "installment", "annual_inc", "dti", "fico_range_low",
        "revol_util", "delinq_2yrs", "inq_last_6mths", "open_acc", "pub_rec", "revol_bal",
        "total_acc", "fe_loan_to_income_ratio", "fe_monthly_installment_to_income_ratio",
        "fe_credit_utilization", "fe_available_revolving_credit", "fe_credit_exposure",
        "fe_debt_burden", "fe_credit_history_months"
    ]

    # Part 2: Descriptive Statistics
    print("Computing Descriptive Statistics...")
    desc_stats = calculate_descriptive_stats(df_model, numeric_features)
    desc_stats.to_csv(TABLES_DIR / "descriptive_statistics.csv", index=False)

    # Part 3: Normality Analysis
    print("Running Normality Tests and Generating Distribution Figures...")
    norm_tests = run_normality_tests(df_model, numeric_features[:10])
    norm_tests.to_csv(TABLES_DIR / "normality_tests.csv", index=False)
    generate_normality_plots(df_model, numeric_features[:6], FIGURES_DIR / "normality")

    # Part 4: Multicollinearity Suite
    print("Executing Multicollinearity Analysis (Correlation, VIF, Condition Index)...")
    corrs = calculate_correlations(df_model, numeric_features)
    corrs["pearson"].to_csv(TABLES_DIR / "pearson_correlation.csv")
    corrs["spearman"].to_csv(TABLES_DIR / "spearman_correlation.csv")
    
    high_pairs = find_high_correlations(corrs["pearson"], threshold=0.70)
    high_pairs.to_csv(TABLES_DIR / "high_correlation_pairs.csv", index=False)

    vif_df = calculate_vif_and_tolerance(df_model, numeric_features[:12])
    vif_df.to_csv(TABLES_DIR / "vif_analysis.csv", index=False)

    ci_df, vdp_matrix = calculate_condition_index_and_vdp(df_model, numeric_features[:10])
    ci_df.to_csv(TABLES_DIR / "condition_index_analysis.csv", index=False)

    # Part 5: Heteroskedasticity
    print("Running Heteroskedasticity Tests (Breusch-Pagan, White, Goldfeld-Quandt) & HC3 Robust SEs...")
    het_summary, hc3_comp = run_heteroskedasticity_tests(df_model, "target", numeric_features[:8])
    pd.DataFrame([het_summary]).to_csv(TABLES_DIR / "heteroskedasticity_summary.csv", index=False)
    hc3_comp.to_csv(TABLES_DIR / "hc3_robust_se_comparison.csv", index=False)

    # Part 6: Autocorrelation
    print("Running Autocorrelation Diagnostics (Durbin-Watson, Breusch-Godfrey)...")
    ac_summary = run_autocorrelation_tests(df_model, "target", numeric_features[:8], time_col="issue_d")
    pd.DataFrame([ac_summary]).to_csv(TABLES_DIR / "autocorrelation_summary.csv", index=False)

    # Part 7: Linearity Assessment
    print("Evaluating Linearity (Box-Tidwell & LOWESS Plots)...")
    bt_df = run_box_tidwell_test(df_model, "target", numeric_features[:8])
    bt_df.to_csv(TABLES_DIR / "box_tidwell_linearity.csv", index=False)
    generate_linearity_plots(df_model, "target", numeric_features[:4], FIGURES_DIR / "linearity")

    # Part 8: Outlier & Influence Analysis
    print("Computing Leverage, Cook's Distance, and Influence Metrics...")
    _, influence_summary = calculate_outlier_influence_metrics(df_model, "target", numeric_features[:8])
    pd.DataFrame([influence_summary]).to_csv(TABLES_DIR / "influence_diagnostics_summary.csv", index=False)

    # Part 9: Endogeneity Assessment
    print("Evaluating Endogeneity and IV/2SLS Framework...")
    endo_eval = evaluate_endogeneity_framework()
    (TABLES_DIR / "endogeneity_assessment.json").write_text(json.dumps(endo_eval, indent=2), encoding="utf-8")

    # Part 11: Feature Stability (PSI/CSI)
    print("Computing Vintage PSI & CSI Stability (2015 vs 2018 cohorts)...")
    df["year"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce").dt.year
    cohort_2015 = df[df["year"] == 2015]
    cohort_2018 = df[df["year"] == 2018]

    if not cohort_2015.empty and not cohort_2018.empty:
        csi_df = calculate_csi(cohort_2015, cohort_2018, numeric_features[:10])
        csi_df.to_csv(TABLES_DIR / "psi_csi_stability.csv", index=False)

    print("Phase 6 Diagnostics completed successfully! All tables and figures generated.")


if __name__ == "__main__":
    main()
