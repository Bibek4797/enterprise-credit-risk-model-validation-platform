"""Global and Local SHAP (SHapley Additive exPlanations) Analysis Engine.

Computes TreeExplainer SHAP values, global feature rankings, local instance
waterfall/force/decision values, and pairwise SHAP interaction matrices per SR 11-7 and FCRA.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
import shap

logger = logging.getLogger(__name__)


def compute_global_shap(
    model: object,
    X_sample: pd.DataFrame,
) -> dict[str, object]:
    """Compute TreeExplainer SHAP values and global mean absolute SHAP feature rankings."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # For binary classification, shap_values may be a list of 2 arrays or a single array
    if isinstance(shap_values, list):
        vals = shap_values[1]  # Positive class (Default)
        base_val = float(explainer.expected_value[1]) if isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value)
    else:
        vals = shap_values
        base_val = float(explainer.expected_value) if not isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value[0])

    mean_abs_shap = np.abs(vals).mean(axis=0)

    ranking_df = pd.DataFrame({
        "feature": X_sample.columns,
        "mean_abs_shap": mean_abs_shap,
    }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

    return {
        "explainer": explainer,
        "shap_values": vals,
        "base_value": base_val,
        "ranking_table": ranking_df,
    }


def explain_local_borrower(
    explainer: object,
    shap_values: np.ndarray,
    X_sample: pd.DataFrame,
    instance_idx: int,
) -> dict[str, object]:
    """Extract local SHAP feature attribution breakdown for a specific borrower instance."""
    row_data = X_sample.iloc[instance_idx]
    row_shap = shap_values[instance_idx]

    local_df = pd.DataFrame({
        "feature": X_sample.columns,
        "feature_value": row_data.values,
        "shap_value": row_shap,
        "abs_shap": np.abs(row_shap),
    }).sort_values("abs_shap", ascending=False).reset_index(drop=True)

    base_val = float(explainer.expected_value[1]) if isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value)

    return {
        "instance_index": instance_idx,
        "base_value": base_val,
        "total_shap_sum": float(np.sum(row_shap)),
        "predicted_log_odds": float(base_val + np.sum(row_shap)),
        "attribution_table": local_df,
    }


def compute_shap_interaction_matrix(
    explainer: object,
    X_sample: pd.DataFrame,
    max_samples: int = 500,
) -> pd.DataFrame:
    """Compute pairwise SHAP interaction values matrix across features."""
    sub_X = X_sample.iloc[:max_samples]
    try:
        interaction_vals = explainer.shap_interaction_values(sub_X)
        if isinstance(interaction_vals, list):
            interaction_vals = interaction_vals[1]

        # Mean absolute interaction matrix
        mean_inter = np.abs(interaction_vals).mean(axis=0)
        inter_df = pd.DataFrame(mean_inter, index=sub_X.columns, columns=sub_X.columns)
        return inter_df
    except Exception as err:
        logger.warning(f"Could not compute SHAP interaction matrix: {err}")
        return pd.DataFrame(0.0, index=sub_X.columns, columns=sub_X.columns)
