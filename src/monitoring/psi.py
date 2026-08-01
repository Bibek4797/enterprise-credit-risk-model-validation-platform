"""Population Stability Index (PSI) calculation engine for retail credit risk portfolios."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_array_psi(
    expected: np.ndarray | pd.Series,
    actual: np.ndarray | pd.Series,
    num_bins: int = 10,
) -> dict[str, object]:
    """Calculate Population Stability Index (PSI) between baseline expected array and current actual array."""
    exp_clean = np.asarray(expected, dtype=float)
    act_clean = np.asarray(actual, dtype=float)

    exp_clean = exp_clean[~np.isnan(exp_clean)]
    act_clean = act_clean[~np.isnan(act_clean)]

    if len(exp_clean) == 0 or len(act_clean) == 0:
        return {"psi_value": np.nan, "status": "INDETERMINATE", "bin_table": pd.DataFrame()}

    # Bin edges based on expected quantiles
    quantiles = np.linspace(0, 100, num_bins + 1)
    bin_edges = np.percentile(exp_clean, quantiles)
    bin_edges = np.unique(bin_edges)

    if len(bin_edges) < 2:
        return {"psi_value": 0.0, "status": "GREEN (Stable)", "bin_table": pd.DataFrame()}

    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    exp_counts, _ = np.histogram(exp_clean, bins=bin_edges)
    act_counts, _ = np.histogram(act_clean, bins=bin_edges)

    exp_pct = exp_counts / (len(exp_clean) + 1e-6)
    act_pct = act_counts / (len(act_clean) + 1e-6)

    # Avoid zero division
    exp_pct = np.maximum(exp_pct, 1e-4)
    act_pct = np.maximum(act_pct, 1e-4)

    psi_bin = (act_pct - exp_pct) * np.log(act_pct / exp_pct)
    total_psi = float(np.sum(psi_bin))

    if total_psi < 0.10:
        status = "GREEN (Stable)"
    elif 0.10 <= total_psi < 0.25:
        status = "YELLOW (Moderate Drift)"
    else:
        status = "RED (Significant Drift)"

    bin_table = pd.DataFrame({
        "bin_index": range(1, len(exp_counts) + 1),
        "expected_count": exp_counts,
        "actual_count": act_counts,
        "expected_pct": (exp_pct * 100.0).round(2),
        "actual_pct": (act_pct * 100.0).round(2),
        "psi_contribution": psi_bin.round(4),
    })

    return {
        "psi_value": round(total_psi, 4),
        "status": status,
        "bin_table": bin_table,
    }


def compute_segment_psi_table(
    expected_df: pd.DataFrame,
    actual_df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """Compute PSI across multiple numerical and categorical risk drivers or score deciles."""
    records = []
    for col in columns:
        if col in expected_df.columns and col in actual_df.columns:
            if pd.api.types.is_numeric_dtype(expected_df[col]):
                res = calculate_array_psi(expected_df[col], actual_df[col])
                records.append({
                    "column_name": col,
                    "psi_value": res["psi_value"],
                    "status": res["status"],
                })
            else:
                # Categorical PSI
                exp_pct = expected_df[col].value_counts(normalize=True)
                act_pct = actual_df[col].value_counts(normalize=True)
                all_cats = list(set(exp_pct.index).union(set(act_pct.index)))

                exp_vec = np.array([exp_pct.get(c, 1e-4) for c in all_cats])
                act_vec = np.array([act_pct.get(c, 1e-4) for c in all_cats])

                psi_val = float(np.sum((act_vec - exp_vec) * np.log(act_vec / exp_vec)))

                if psi_val < 0.10:
                    status = "GREEN (Stable)"
                elif 0.10 <= psi_val < 0.25:
                    status = "YELLOW (Moderate Drift)"
                else:
                    status = "RED (Significant Drift)"

                records.append({
                    "column_name": col,
                    "psi_value": round(psi_val, 4),
                    "status": status,
                })

    return pd.DataFrame(records).sort_values("psi_value", ascending=False).reset_index(drop=True)
