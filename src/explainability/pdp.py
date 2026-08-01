"""Partial Dependence Plot (PDP) calculation engine for non-linear risk driver response analysis."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from sklearn.inspection import partial_dependence

logger = logging.getLogger(__name__)


def compute_feature_pdp(
    model: object,
    X_sample: pd.DataFrame,
    feature: str,
    grid_resolution: int = 20,
) -> pd.DataFrame:
    """Compute 1D Partial Dependence response curve for a specific feature."""
    if feature not in X_sample.columns:
        raise ValueError(f"Feature {feature} not found in sample DataFrame.")

    pdp_res = partial_dependence(
        model,
        X_sample,
        features=[feature],
        grid_resolution=grid_resolution,
        kind="average",
    )

    grid_values = pdp_res["grid_values"][0]
    pdp_values = pdp_res["average"][0]

    return pd.DataFrame({
        "feature": feature,
        "grid_value": grid_values,
        "partial_dependence_pd": pdp_values,
    })


def compute_portfolio_pdp_summary(
    model: object,
    X_sample: pd.DataFrame,
    features: list[str],
    grid_resolution: int = 15,
) -> dict[str, pd.DataFrame]:
    """Compute PDP summary curves for all key features in the portfolio."""
    pdp_results = {}
    for feat in features:
        if feat in X_sample.columns and pd.api.types.is_numeric_dtype(X_sample[feat]):
            try:
                pdp_df = compute_feature_pdp(model, X_sample, feat, grid_resolution=grid_resolution)
                pdp_results[feat] = pdp_df
            except Exception as err:
                logger.warning(f"Failed PDP for {feat}: {err}")
    return pdp_results
