"""Banking-grade Weight of Evidence (WoE) and Information Value (IV) transformation module.

Implements fine/coarse classing, missing bin handling, Laplace smoothing,
monotonicity checking, and predictive strength classification according to
Basel III and SR 11-7 model development guidelines.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

EPSILON = 1e-6


def categorize_iv_strength(iv: float) -> str:
    """Classify Information Value strength per standard credit risk scorecard rules."""
    if np.isnan(iv) or iv < 0.02:
        return "Uninformative (< 0.02)"
    elif 0.02 <= iv < 0.10:
        return "Weak (0.02 - 0.10)"
    elif 0.10 <= iv < 0.30:
        return "Medium (0.10 - 0.30)"
    elif 0.30 <= iv <= 0.50:
        return "Strong (0.30 - 0.50)"
    else:
        return "Suspicious / Leakage Risk (> 0.50)"


def check_monotonicity(woe_series: pd.Series) -> bool:
    """Check if Weight of Evidence is strictly monotonic (excluding Missing bin if present)."""
    clean_woe = woe_series.dropna()
    if len(clean_woe) <= 2:
        return True
    diffs = np.diff(clean_woe)
    return bool(np.all(diffs >= 0) or np.all(diffs <= 0))


def calculate_woe_iv(
    df: pd.DataFrame,
    feature: str,
    target: str = "target",
    bins: int = 10,
    categorical: bool = False,
    min_bin_pct: float = 0.05,
) -> dict[str, object]:
    """Compute WoE table, total IV, monotonicity, and strength category for a single feature.

    Target assumption: target == 1 for Default/Bad, target == 0 for Non-default/Good.
    """
    valid_data = df[[feature, target]].dropna(subset=[target]).copy()
    valid_data[target] = valid_data[target].astype(int)

    total_bads = (valid_data[target] == 1).sum()
    total_goods = (valid_data[target] == 0).sum()

    if total_bads == 0 or total_goods == 0:
        raise ValueError(f"Feature {feature} has zero goods or bads in target series.")

    # Create Bins / Groups
    if categorical or pd.api.types.is_object_dtype(valid_data[feature]) or pd.api.types.is_categorical_dtype(valid_data[feature]):
        valid_data["bin"] = valid_data[feature].fillna("Missing").astype(str)
    else:
        # Numeric coarse classing using quantiles, fallback to uniform cut if quantiles duplicate
        series_clean = valid_data[feature].dropna()
        if series_clean.nunique() <= bins:
            valid_data["bin"] = valid_data[feature].fillna("Missing").astype(str)
        else:
            try:
                valid_data["bin"] = pd.qcut(series_clean, q=bins, duplicates="drop").astype(str)
            except ValueError:
                valid_data["bin"] = pd.cut(series_clean, bins=bins).astype(str)
            valid_data["bin"] = valid_data["bin"].fillna("Missing")

    # Aggregate counts
    grouped = (
        valid_data.groupby("bin", observed=False)[target]
        .agg(
            total_count="count",
            bads="sum",
            goods=lambda x: (x == 0).sum(),
            default_rate="mean",
        )
        .reset_index()
    )

    # Bin percentage of total population
    grouped["bin_pct"] = grouped["total_count"] / len(valid_data)

    # Calculate Goods% and Bads% with Laplace smoothing to prevent division by 0
    grouped["good_pct"] = (grouped["goods"] + 0.5) / (total_goods + 1.0)
    grouped["bad_pct"] = (grouped["bads"] + 0.5) / (total_bads + 1.0)

    # Weight of Evidence: ln(%Goods / %Bads)
    grouped["woe"] = np.log(grouped["good_pct"] / grouped["bad_pct"])

    # Information Value component: (%Goods - %Bads) * WoE
    grouped["iv_component"] = (grouped["good_pct"] - grouped["bad_pct"]) * grouped["woe"]

    total_iv = float(grouped["iv_component"].sum())
    strength_category = categorize_iv_strength(total_iv)

    # Monotonicity check (excluding 'Missing' if present)
    non_missing_woe = grouped[grouped["bin"] != "Missing"]["woe"]
    is_monotonic = check_monotonicity(non_missing_woe)

    return {
        "feature": feature,
        "woe_table": grouped,
        "total_iv": total_iv,
        "strength_category": strength_category,
        "is_monotonic": is_monotonic,
        "bin_count": len(grouped),
    }


def compute_portfolio_iv(
    df: pd.DataFrame,
    features: list[str],
    target: str = "target",
    bins: int = 10,
) -> pd.DataFrame:
    """Calculate Information Value across a list of candidate features and return a ranked audit summary."""
    records = []
    for feat in features:
        if feat == target:
            continue
        try:
            res = calculate_woe_iv(df, feature=feat, target=target, bins=bins)
            records.append({
                "feature": feat,
                "information_value": round(res["total_iv"], 5),
                "strength_category": res["strength_category"],
                "is_monotonic": res["is_monotonic"],
                "bin_count": res["bin_count"],
            })
        except Exception as err:
            logger.warning(f"Skipping {feat} during IV calculation: {err}")
            records.append({
                "feature": feat,
                "information_value": np.nan,
                "strength_category": "Error / Skipped",
                "is_monotonic": False,
                "bin_count": 0,
            })

    iv_df = pd.DataFrame(records).sort_values("information_value", ascending=False).reset_index(drop=True)
    return iv_df


def transform_to_woe(
    df: pd.DataFrame,
    woe_maps: dict[str, dict[str, float]],
) -> pd.DataFrame:
    """Transform dataframe feature columns into their calculated WoE numeric values."""
    res_df = df.copy()
    for feat, mapping in woe_maps.items():
        if feat in res_df.columns:
            res_df[f"{feat}_woe"] = res_df[feat].astype(str).map(mapping).fillna(0.0)
    return res_df
