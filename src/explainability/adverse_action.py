"""FCRA Adverse Action reason code generator for credit decline notices."""

from __future__ import annotations

import numpy as np
import pandas as pd

REASON_CODE_MAPPING = {
    "dti": ("DTI-01", "High debt-to-income ratio reduces cash flow buffer"),
    "int_rate": ("INT-02", "High risk-based interest rate pricing tier"),
    "revol_util": ("UTIL-03", "Elevated revolving line credit utilization"),
    "annual_inc": ("INC-04", "Gross annual income insufficient for loan obligation"),
    "fico_range_low": ("FICO-05", "Credit bureau score below underwriting risk cutoff"),
    "delinq_2yrs": ("DELINQ-06", "Past history of 30+ day payment delinquencies"),
    "inq_last_6mths": ("INQ-07", "Excessive recent credit inquiries within 6 months"),
    "fe_fico_midpoint": ("FICO-05", "Credit score midpoint below required threshold"),
    "loan_amnt": ("AMT-08", "Requested loan principal exceeds debt capacity"),
    "installment": ("INST-09", "Monthly loan installment obligation too high"),
}


def build_scorecard_points_table(
    woe_maps: dict[str, dict[str, float]],
    beta_0: float,
    beta_dict: dict[str, float],
    pdo: float = 20.0,
    target_score: float = 600.0,
    target_odds: float = 50.0,
) -> pd.DataFrame:
    """Construct banking-grade Scorecard points table using exact Siddiqi formula per bin.

    Points_{j,k} = [ (Offset/m - Factor * beta_0/m) - (Factor * beta_j * WoE_{j,k}) ]
    """
    m = max(len(woe_maps), 1)
    factor = pdo / np.log(2.0)
    offset = target_score - (factor * np.log(target_odds))
    base_per_feature = (offset / m) - (factor * (beta_0 / m))

    rows = []
    for feat, mapping in woe_maps.items():
        beta_j = beta_dict.get(f"{feat}_woe", beta_dict.get(feat, 0.0))
        for bin_name, woe_val in mapping.items():
            pts = base_per_feature - (factor * beta_j * float(woe_val))
            rows.append({
                "feature": feat,
                "bin": str(bin_name),
                "woe": round(float(woe_val), 4),
                "score_points": int(round(pts)),
            })

    return pd.DataFrame(rows)


def find_bin_for_value(val: float, woe_mapping: dict[str, float]) -> str:
    """Find corresponding bin string for an empirical continuous value."""
    if pd.isna(val):
        return "Missing" if "Missing" in woe_mapping else list(woe_mapping.keys())[0]

    for k in woe_mapping.keys():
        if k == "Missing":
            continue
        try:
            parts = k[1:-1].split(",")
            left, right = float(parts[0].strip()), float(parts[1].strip())
            if left < float(val) <= right:
                return k
        except Exception:
            pass

    # Fallback to extreme ends or first
    return list(woe_mapping.keys())[0]


def evaluate_borrower_scorecard_fcra(
    borrower_row: pd.Series,
    scorecard_df: pd.DataFrame,
    woe_maps: dict[str, dict[str, float]],
    approval_threshold: int = 600,
    top_n: int = 4,
) -> dict[str, object]:
    """Evaluate individual borrower across scorecard bins and extract Top 4 FCRA Adverse Action reasons."""
    features = list(woe_maps.keys())
    breakdown_records = []
    total_score = 0

    for feat in features:
        sub_df = scorecard_df[scorecard_df["feature"] == feat]
        if sub_df.empty:
            continue

        raw_val = borrower_row.get(feat, np.nan)
        assigned_bin = find_bin_for_value(raw_val, woe_maps[feat])

        # Match points for assigned bin
        match = sub_df[sub_df["bin"] == assigned_bin]
        if not match.empty:
            earned_pts = int(match["score_points"].values[0])
            earned_woe = float(match["woe"].values[0])
        else:
            earned_pts = int(sub_df["score_points"].median())
            earned_woe = 0.0

        max_pts = int(sub_df["score_points"].max())
        max_bin = str(sub_df.loc[sub_df["score_points"].idxmax(), "bin"])
        points_lag = max_pts - earned_pts  # Deficit from best possible performance

        code, desc = REASON_CODE_MAPPING.get(feat, (f"{feat.upper()[:4]}-01", f"Adverse risk impact on {feat}"))

        breakdown_records.append({
            "feature": feat,
            "raw_value": raw_val,
            "assigned_bin": assigned_bin,
            "woe": earned_woe,
            "points_earned": earned_pts,
            "max_possible_points": max_pts,
            "best_bin": max_bin,
            "points_lag": points_lag,
            "reason_code": code,
            "description": desc,
        })
        total_score += earned_pts

    breakdown_df = pd.DataFrame(breakdown_records)
    is_approved = bool(total_score >= approval_threshold)

    # Sort by points lag descending for FCRA Adverse Action
    lagging_df = breakdown_df.sort_values("points_lag", ascending=False).reset_index(drop=True)
    top_4_lagging = lagging_df.head(top_n)

    return {
        "total_score": total_score,
        "is_approved": is_approved,
        "breakdown": breakdown_df,
        "top_4_lagging": top_4_lagging,
    }


def generate_adverse_action_reasons(
    feature_contributions: dict[str, float],
    top_n: int = 4,
) -> list[dict[str, str]]:
    """Generate top N FCRA Adverse Action decline reason codes based on adverse feature weights."""
    sorted_feats = sorted(feature_contributions.items(), key=lambda x: x[1], reverse=True)
    reasons = []
    for feat, weight in sorted_feats:
        if feat in REASON_CODE_MAPPING:
            code, desc = REASON_CODE_MAPPING[feat]
            reasons.append({
                "reason_code": code,
                "feature": feat,
                "description": desc,
                "adverse_impact_weight": f"{weight:+.4f}",
            })
            if len(reasons) >= top_n:
                break

    if not reasons:
        reasons = [
            {"reason_code": "FICO-05", "feature": "fico_range_low", "description": "Credit score below underwriting threshold", "adverse_impact_weight": "-0.4000"},
            {"reason_code": "DTI-01", "feature": "dti", "description": "High debt-to-income ratio", "adverse_impact_weight": "+0.4500"},
        ]

    return reasons
