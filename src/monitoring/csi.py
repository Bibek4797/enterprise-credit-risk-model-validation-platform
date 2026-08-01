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
    res = calculate_array_psi(expected_series, actual_series, num_bins=10)
    return {
        "feature_name": feature_name,
        "csi_value": res["psi_value"],
        "status": res["status"],
        "bin_table": res["bin_table"],
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
            if pd.api.types.is_numeric_dtype(expected_df[feat]):
                res = calculate_feature_csi(expected_df[feat], actual_df[feat], feat)
                records.append({
                    "feature_name": feat,
                    "csi_value": res["csi_value"],
                    "status": res["status"],
                    "drift_level": "High" if res["csi_value"] >= 0.25 else ("Moderate" if res["csi_value"] >= 0.10 else "Low"),
                })

    df_csi = pd.DataFrame(records)
    if not df_csi.empty:
        df_csi = df_csi.sort_values("csi_value", ascending=False).reset_index(drop=True)

    return df_csi
