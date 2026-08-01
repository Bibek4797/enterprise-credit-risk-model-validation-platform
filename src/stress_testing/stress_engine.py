"""Master Stress Testing Execution Engine & Executive Dashboard Table Generator."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from stress_testing.scenario_generator import apply_borrower_scenario, apply_macro_scenario

logger = logging.getLogger(__name__)


def run_portfolio_stress_test(
    predict_fn: callable,
    df: pd.DataFrame,
    feature_cols: list[str],
    scenarios: dict[str, str] | None = None,
    lgd: float = 0.95,
) -> pd.DataFrame:
    """Execute suite of stress scenarios on portfolio DataFrame and return baseline vs stressed metrics."""
    if scenarios is None:
        scenarios = {
            "Baseline (Current)": "baseline",
            "Scenario 1: Income -10%": "scenario_1_income_minus_10",
            "Scenario 2: Income -20%": "scenario_2_income_minus_20",
            "Scenario 3: DTI +15%": "scenario_3_dti_plus_15",
            "Scenario 4: Int Rate +2%": "scenario_4_interest_rate_plus_2",
            "Scenario 5: Util +20%": "scenario_5_utilization_plus_20",
            "Scenario 6: FICO -30 pts": "scenario_6_fico_minus_30",
            "Scenario 7: Loan Amount +15%": "scenario_7_loan_amount_plus_15",
            "Macro Adverse (Slowdown)": "adverse",
            "Macro Severe Adverse (Crisis)": "severe_adverse",
        }

    # Baseline evaluation
    X_base = df[feature_cols].fillna(0)
    base_preds = predict_fn(X_base)
    base_mean_pd = float(np.mean(base_preds))
    total_exposure = float(df["loan_amnt"].sum()) if "loan_amnt" in df.columns else float(len(df) * 15000)
    base_el = total_exposure * base_mean_pd * lgd

    records = []

    for name, s_key in scenarios.items():
        if "scenario_" in s_key:
            df_stressed = apply_borrower_scenario(df, s_key)
        else:
            df_stressed = apply_macro_scenario(df, s_key)

        X_str = df_stressed[feature_cols].fillna(0)
        str_preds = predict_fn(X_str)
        str_mean_pd = float(np.mean(str_preds))

        str_exposure = float(df_stressed["loan_amnt"].sum()) if "loan_amnt" in df_stressed.columns else total_exposure
        str_el = str_exposure * str_mean_pd * lgd
        delta_el = str_el - base_el

        records.append({
            "scenario_name": name,
            "mean_predicted_pd": round(str_mean_pd * 100.0, 2),
            "delta_pd_pct_points": round((str_mean_pd - base_mean_pd) * 100.0, 2),
            "relative_pd_increase_pct": round(((str_mean_pd - base_mean_pd) / (base_mean_pd + 1e-6)) * 100.0, 2),
            "total_portfolio_exposure": round(str_exposure, 2),
            "expected_loss_el": round(str_el, 2),
            "delta_expected_loss": round(delta_el, 2),
        })

    return pd.DataFrame(records)


def generate_segment_stress_comparison(
    predict_fn: callable,
    df: pd.DataFrame,
    feature_cols: list[str],
    segment_col: str = "grade",
    scenario_type: str = "severe_adverse",
    lgd: float = 0.95,
) -> pd.DataFrame:
    """Generate Before vs After Stress comparison table segmented by Grade, Income, or State."""
    if segment_col not in df.columns:
        return pd.DataFrame()

    df_stressed = apply_macro_scenario(df, scenario_type)

    X_base = df[feature_cols].fillna(0)
    X_str = df_stressed[feature_cols].fillna(0)

    df_copy = df.copy()
    df_copy["base_pd"] = predict_fn(X_base)
    df_copy["stressed_pd"] = predict_fn(X_str)

    summary = (
        df_copy.groupby(segment_col, observed=False)
        .agg(
            loan_count=(segment_col, "count"),
            total_exposure=("loan_amnt", "sum") if "loan_amnt" in df.columns else (segment_col, lambda x: np.nan),
            base_mean_pd=("base_pd", "mean"),
            stressed_mean_pd=("stressed_pd", "mean"),
        )
        .reset_index()
    )

    summary["base_mean_pd_pct"] = (summary["base_mean_pd"] * 100.0).round(2)
    summary["stressed_mean_pd_pct"] = (summary["stressed_mean_pd"] * 100.0).round(2)
    summary["delta_pd_pct_points"] = (summary["stressed_mean_pd_pct"] - summary["base_mean_pd_pct"]).round(2)

    if "loan_amnt" in df.columns:
        summary["base_expected_loss"] = (summary["total_exposure"] * summary["base_mean_pd"] * lgd).round(2)
        summary["stressed_expected_loss"] = (summary["total_exposure"] * summary["stressed_mean_pd"] * lgd).round(2)
        summary["delta_expected_loss"] = (summary["stressed_expected_loss"] - summary["base_expected_loss"]).round(2)

    return summary.sort_values("loan_count", ascending=False).reset_index(drop=True)
