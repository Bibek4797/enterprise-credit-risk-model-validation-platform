"""Counterfactual sensitivity engine, error profile auditor, and feature importance triangulation."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def generate_counterfactual_explanation(
    predict_fn: callable,
    borrower_row: pd.Series,
    target_pd: float = 0.15,
    mutable_features: list[str] | None = None,
) -> dict[str, object]:
    """Find minimum required changes (counterfactuals) for a high-risk borrower to reach approval threshold."""
    if mutable_features is None:
        mutable_features = ["fico_range_low", "dti", "revol_util", "annual_inc"]

    baseline_df = pd.DataFrame([borrower_row])
    current_pd = float(predict_fn(baseline_df)[0])

    if current_pd <= target_pd:
        return {
            "initial_pd": round(current_pd, 4),
            "target_pd": target_pd,
            "status": "APPROVED",
            "required_changes": "Borrower already meets approval threshold.",
        }

    cf_row = borrower_row.copy()
    changes = {}

    # Stepwise counterfactual search
    for feat in mutable_features:
        if feat not in borrower_row.index:
            continue

        val = float(borrower_row[feat])
        if "fico" in feat or "income" in feat:
            # Positive direction adjustment
            for step in np.linspace(0, 0.5, 20):
                new_val = val * (1.0 + step)
                temp_df = pd.DataFrame([cf_row])
                temp_df[feat] = new_val
                temp_pd = float(predict_fn(temp_df)[0])
                if temp_pd <= target_pd:
                    cf_row[feat] = new_val
                    changes[feat] = f"Increase from {val:.2f} to {new_val:.2f} (+{step*100:.1f}%)"
                    break
        else:
            # Negative direction adjustment (dti, revol_util)
            for step in np.linspace(0, 0.5, 20):
                new_val = max(0.0, val * (1.0 - step))
                temp_df = pd.DataFrame([cf_row])
                temp_df[feat] = new_val
                temp_pd = float(predict_fn(temp_df)[0])
                if temp_pd <= target_pd:
                    cf_row[feat] = new_val
                    changes[feat] = f"Decrease from {val:.2f} to {new_val:.2f} (-{step*100:.1f}%)"
                    break

    final_pd = float(predict_fn(pd.DataFrame([cf_row]))[0])

    return {
        "initial_pd": round(current_pd, 4),
        "achieved_pd": round(final_pd, 4),
        "target_pd": target_pd,
        "is_counterfactual_found": bool(final_pd <= target_pd),
        "required_changes": changes,
    }


def analyze_prediction_errors(
    y_true: pd.Series | np.ndarray,
    y_prob: pd.Series | np.ndarray,
    X_sample: pd.DataFrame,
    threshold: float = 0.20,
) -> dict[str, pd.DataFrame]:
    """Group instances into TP, FP, TN, FN and return feature mean profiles across categories."""
    y_arr = np.asarray(y_true, dtype=int)
    prob_arr = np.asarray(y_prob, dtype=float)
    pred_binary = (prob_arr >= threshold).astype(int)

    data = X_sample.copy()
    data["_target"] = y_arr
    data["_prob"] = prob_arr
    data["_pred"] = pred_binary

    tp = data[(data["_target"] == 1) & (data["_pred"] == 1)]
    fp = data[(data["_target"] == 0) & (data["_pred"] == 1)]
    tn = data[(data["_target"] == 0) & (data["_pred"] == 0)]
    fn = data[(data["_target"] == 1) & (data["_pred"] == 0)]

    numeric_cols = [c for c in X_sample.select_dtypes(include=[np.number]).columns if not c.startswith("_")]

    profile_df = pd.DataFrame({
        "True Positives (Default Correct)": tp[numeric_cols].mean(),
        "False Positives (False Alarm)": fp[numeric_cols].mean(),
        "True Negatives (Approval Correct)": tn[numeric_cols].mean(),
        "False Negatives (Missed Default)": fn[numeric_cols].mean(),
    })

    counts = {
        "TP_count": len(tp),
        "FP_count": len(fp),
        "TN_count": len(tn),
        "FN_count": len(fn),
    }

    return {
        "error_counts": pd.DataFrame([counts]),
        "feature_profiles": profile_df,
    }


def triangulate_feature_importances(
    tree_importance_df: pd.DataFrame,
    shap_importance_df: pd.DataFrame,
    logit_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge and align feature rankings across Tree Gini, SHAP, and Logistic Scorecard coefficients."""
    m1 = pd.merge(tree_importance_df, shap_importance_df, on="feature", how="outer")
    # Clean feature names for logit matching
    logit_clean = logit_summary_df.copy()
    logit_clean["feature"] = logit_clean["feature"].str.replace("_woe", "")

    merged = pd.merge(m1, logit_clean[["feature", "odds_ratio"]], on="feature", how="left")
    merged = merged.fillna(0.0)

    # Rank columns
    merged["tree_rank"] = merged["importance"].rank(ascending=False, method="min").astype(int)
    merged["shap_rank"] = merged["mean_abs_shap"].rank(ascending=False, method="min").astype(int)

    return merged.sort_values("shap_rank").reset_index(drop=True)
