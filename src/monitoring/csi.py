"""Characteristic Stability Index (CSI) tracking engine for feature-level distribution drift."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from monitoring.psi import calculate_array_psi

logger = logging.getLogger(__name__)


def calculate_feature_csi(
    expected_series: pd.Series,
    actual_series: pd.Series,
    feature_name: str,
) -> dict[str, object]:
    """Calculate Characteristic Stability Index (CSI) for a single feature."""
    is_num = pd.api.types.is_numeric_dtype(expected_series)
    if is_num:
        res = calculate_array_psi(expected_series, actual_series, num_bins=10)
        return {
            "feature_name": feature_name,
            "feature_type": "Numeric",
            "csi_value": res["psi_value"],
            "status": res["status"],
            "bin_table": res["bin_table"],
        }
    else:
        # Categorical CSI based on frequency distribution drift
        exp_s = expected_series.dropna().astype(str)
        act_s = actual_series.dropna().astype(str)
        if len(exp_s) == 0 or len(act_s) == 0:
            return {
                "feature_name": feature_name,
                "feature_type": "Categorical",
                "csi_value": 0.0,
                "status": "GREEN (Stable)",
                "bin_table": pd.DataFrame(),
            }
        exp_pct = exp_s.value_counts(normalize=True)
        act_pct = act_s.value_counts(normalize=True)
        all_cats = sorted(list(set(exp_pct.index).union(set(act_pct.index))))

        exp_vec = np.array([exp_pct.get(c, 1e-4) for c in all_cats])
        act_vec = np.array([act_pct.get(c, 1e-4) for c in all_cats])

        csi_val = float(np.sum((act_vec - exp_vec) * np.log(act_vec / exp_vec)))

        if csi_val < 0.10:
            status = "GREEN (Stable)"
        elif 0.10 <= csi_val < 0.25:
            status = "YELLOW (Moderate Drift)"
        else:
            status = "RED (Significant Drift)"

        bin_table = pd.DataFrame({
            "category": all_cats,
            "expected_pct": (exp_vec * 100.0).round(2),
            "actual_pct": (act_vec * 100.0).round(2),
            "csi_contribution": ((act_vec - exp_vec) * np.log(act_vec / exp_vec)).round(4),
        })

        return {
            "feature_name": feature_name,
            "feature_type": "Categorical",
            "csi_value": round(csi_val, 4),
            "status": status,
            "bin_table": bin_table,
        }


def build_portfolio_csi_report(
    expected_df: pd.DataFrame,
    actual_df: pd.DataFrame,
    features: list[str],
) -> pd.DataFrame:
    """Build a comprehensive CSI report ranking all candidate features by distribution drift severity."""
    records = []
    for feat in features:
        if feat in expected_df.columns and feat in actual_df.columns:
            res = calculate_feature_csi(expected_df[feat], actual_df[feat], feat)
            csi_val = float(res["csi_value"])
            records.append({
                "feature_name": feat,
                "feature_type": res.get("feature_type", "Numeric"),
                "csi_value": csi_val,
                "status": res["status"],
                "drift_level": "High Drift (>=0.25)" if csi_val >= 0.25 else ("Moderate Drift (0.10-0.25)" if csi_val >= 0.10 else "Stable (<0.10)"),
            })

    df_csi = pd.DataFrame(records)
    if not df_csi.empty:
        df_csi = df_csi.sort_values("csi_value", ascending=False).reset_index(drop=True)

    return df_csi
