"""Sensitivity and PD Elasticity Audit Engine."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_pd_elasticity(
    predict_fn: callable,
    X_sample: pd.DataFrame,
    feature: str,
    shock_pct: float = 0.10,
) -> dict[str, float]:
    """Calculate PD elasticity (% change in PD / % change in feature) for a specific risk driver."""
    if feature not in X_sample.columns or not pd.api.types.is_numeric_dtype(X_sample[feature]):
        return {"feature": feature, "elasticity": np.nan, "mean_delta_pd": np.nan}

    baseline_preds = predict_fn(X_sample)
    baseline_mean_pd = float(np.mean(baseline_preds))

    # Apply positive shock
    X_shocked = X_sample.copy()
    X_shocked[feature] = X_shocked[feature] * (1.0 + shock_pct)
    shocked_preds = predict_fn(X_shocked)
    shocked_mean_pd = float(np.mean(shocked_preds))

    delta_pd = shocked_mean_pd - baseline_mean_pd
    pct_change_pd = delta_pd / (baseline_mean_pd + 1e-6)
    elasticity = pct_change_pd / shock_pct

    return {
        "feature": feature,
        "shock_pct": shock_pct,
        "baseline_mean_pd": round(baseline_mean_pd, 4),
        "shocked_mean_pd": round(shocked_mean_pd, 4),
        "mean_delta_pd": round(delta_pd, 4),
        "pd_elasticity": round(float(elasticity), 4),
    }


def rank_variable_sensitivity(
    predict_fn: callable,
    X_sample: pd.DataFrame,
    features: list[str],
    shock_pct: float = 0.10,
) -> pd.DataFrame:
    """Rank all numeric candidate features by PD elasticity and mean delta PD impact."""
    records = []
    for feat in features:
        res = calculate_pd_elasticity(predict_fn, X_sample, feat, shock_pct=shock_pct)
        if not np.isnan(res["pd_elasticity"]):
            records.append(res)

    df_rank = pd.DataFrame(records)
    if not df_rank.empty:
        df_rank["abs_elasticity"] = df_rank["pd_elasticity"].abs()
        df_rank = df_rank.sort_values("abs_elasticity", ascending=False).reset_index(drop=True)

    return df_rank
