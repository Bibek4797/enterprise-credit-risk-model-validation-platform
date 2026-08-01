"""Population and Characteristic Stability Index (PSI/CSI) and distribution drift tracking.

Evaluates feature stability across historical origination vintages to ensure
models are suitable for long-term deployment under Basel III and SR 11-7 model risk rules.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)

EPSILON = 1e-4


def classify_psi(psi_val: float) -> str:
    """Classify Population Stability Index per model governance rules."""
    if np.isnan(psi_val) or psi_val < 0.10:
        return "Stable (< 0.10)"
    elif 0.10 <= psi_val < 0.25:
        return "Moderate Drift (0.10 - 0.25)"
    else:
        return "Significant Drift (>= 0.25)"


def calculate_psi(
    base_series: pd.Series,
    target_series: pd.Series,
    bins: int = 10,
    categorical: bool = False,
) -> float:
    """Calculate Population Stability Index (PSI) between baseline and target populations."""
    base_clean = base_series.dropna()
    target_clean = target_series.dropna()

    if len(base_clean) == 0 or len(target_clean) == 0:
        return np.nan

    if categorical or pd.api.types.is_object_dtype(base_clean) or pd.api.types.is_categorical_dtype(base_clean):
        all_categories = set(base_clean.unique()).union(set(target_clean.unique()))
        base_counts = base_clean.value_counts(normalize=True)
        target_counts = target_clean.value_counts(normalize=True)

        base_pcts = np.array([base_counts.get(cat, EPSILON) for cat in all_categories])
        target_pcts = np.array([target_counts.get(cat, EPSILON) for cat in all_categories])

    else:
        if base_clean.nunique() <= bins:
            all_categories = set(base_clean.unique()).union(set(target_clean.unique()))
            base_counts = base_clean.value_counts(normalize=True)
            target_counts = target_clean.value_counts(normalize=True)

            base_pcts = np.array([base_counts.get(cat, EPSILON) for cat in all_categories])
            target_pcts = np.array([target_counts.get(cat, EPSILON) for cat in all_categories])
        else:
            try:
                quantiles = np.linspace(0, 1, bins + 1)
                bin_edges = np.quantile(base_clean, quantiles)
                bin_edges = np.unique(bin_edges)
                if len(bin_edges) < 2:
                    bin_edges = np.linspace(base_clean.min(), base_clean.max(), bins + 1)
            except Exception:
                bin_edges = np.linspace(base_clean.min(), base_clean.max(), bins + 1)

            bin_edges[0] = -np.inf
            bin_edges[-1] = np.inf

            base_counts, _ = np.histogram(base_clean, bins=bin_edges)
            target_counts, _ = np.histogram(target_clean, bins=bin_edges)

            base_pcts = base_counts / len(base_clean)
            target_pcts = target_counts / len(target_clean)

            # Prevent zero division / log of zero
            base_pcts = np.where(base_pcts == 0, EPSILON, base_pcts)
            target_pcts = np.where(target_pcts == 0, EPSILON, target_pcts)

    psi_val = np.sum((target_pcts - base_pcts) * np.log(target_pcts / base_pcts))
    return float(psi_val)


def calculate_ks_drift(base_series: pd.Series, target_series: pd.Series) -> dict[str, float]:
    """Perform 2-sample Kolmogorov-Smirnov test for distribution drift."""
    base_clean = base_series.dropna()
    target_clean = target_series.dropna()
    if len(base_clean) == 0 or len(target_clean) == 0:
        return {"ks_statistic": np.nan, "p_value": np.nan}

    res = ks_2samp(base_clean, target_clean)
    return {"ks_statistic": float(res.statistic), "p_value": float(res.pvalue)}


def compute_portfolio_stability(
    df: pd.DataFrame,
    features: list[str],
    year_column: str = "fe_issue_year",
    base_years: list[int] | None = None,
    target_years: list[int] | None = None,
    bins: int = 10,
) -> pd.DataFrame:
    """Calculate vintage-based PSI and distribution drift across all candidate features."""
    if year_column not in df.columns:
        logger.warning(f"Year column {year_column} missing; skipping portfolio stability calculation.")
        return pd.DataFrame()

    if base_years is None:
        base_years = [2015, 2016]
    if target_years is None:
        target_years = [2017, 2018]

    base_mask = df[year_column].isin(base_years)
    target_mask = df[year_column].isin(target_years)

    base_df = df[base_mask]
    target_df = df[target_mask]

    records = []
    for feat in features:
        if feat in (year_column, "target", "loan_status"):
            continue
        psi_val = calculate_psi(base_df[feat], target_df[feat], bins=bins)
        ks_dict = calculate_ks_drift(base_df[feat], target_df[feat]) if pd.api.types.is_numeric_dtype(df[feat]) else {"ks_statistic": np.nan, "p_value": np.nan}
        records.append({
            "feature": feat,
            "psi": round(psi_val, 5) if not np.isnan(psi_val) else np.nan,
            "stability_status": classify_psi(psi_val),
            "ks_stat": round(ks_dict["ks_statistic"], 4) if not np.isnan(ks_dict["ks_statistic"]) else np.nan,
            "ks_pvalue": round(ks_dict["p_value"], 4) if not np.isnan(ks_dict["p_value"]) else np.nan,
        })

    return pd.DataFrame(records).sort_values("psi").reset_index(drop=True)
