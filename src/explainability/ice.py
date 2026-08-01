"""Individual Conditional Expectation (ICE) and Accumulated Local Effects (ALE) engine."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from sklearn.inspection import partial_dependence

logger = logging.getLogger(__name__)


def compute_ice_curves(
    model: object,
    X_sample: pd.DataFrame,
    feature: str,
    num_instances: int = 30,
    grid_resolution: int = 20,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute individual ICE curves for a subset of borrower instances."""
    sub_X = X_sample.iloc[:num_instances]
    pdp_res = partial_dependence(
        model,
        sub_X,
        features=[feature],
        grid_resolution=grid_resolution,
        kind="individual",
    )

    grid_values = pdp_res["grid_values"][0]
    ice_values = pdp_res["individual"][0]  # Shape: (num_instances, grid_resolution)

    return grid_values, ice_values


def compute_ale_approximation(
    model: object,
    X_sample: pd.DataFrame,
    feature: str,
    num_bins: int = 15,
) -> pd.DataFrame:
    """Compute Accumulated Local Effects (ALE) approximation to eliminate correlation bias."""
    clean_series = X_sample[feature].dropna()
    quantiles = np.linspace(0, 1, num_bins + 1)
    bin_edges = np.quantile(clean_series, quantiles)
    bin_edges = np.unique(bin_edges)

    if len(bin_edges) < 2:
        return pd.DataFrame()

    local_effects = []
    bin_centers = []

    for i in range(len(bin_edges) - 1):
        z_low = bin_edges[i]
        z_high = bin_edges[i + 1]
        bin_center = (z_low + z_high) / 2.0
        bin_centers.append(bin_center)

        # Subset instances in bin
        in_bin_mask = (X_sample[feature] >= z_low) & (X_sample[feature] <= z_high)
        X_sub = X_sample[in_bin_mask].copy()

        if len(X_sub) == 0:
            local_effects.append(0.0)
            continue

        X_low = X_sub.copy()
        X_low[feature] = z_low

        X_high = X_sub.copy()
        X_high[feature] = z_high

        if hasattr(model, "predict_proba"):
            p_high = model.predict_proba(X_high)[:, 1]
            p_low = model.predict_proba(X_low)[:, 1]
        else:
            p_high = model.predict(X_high)
            p_low = model.predict(X_low)

        delta = np.mean(p_high - p_low)
        local_effects.append(delta)

    ale_accumulated = np.cumsum(local_effects)
    ale_centered = ale_accumulated - np.mean(ale_accumulated)

    return pd.DataFrame({
        "feature": feature,
        "bin_center": bin_centers,
        "ale_value": ale_centered,
    })
