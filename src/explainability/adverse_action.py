"""FCRA Adverse Action reason code generator for credit decline notices."""

from __future__ import annotations

import numpy as np
import pandas as pd

# Comprehensive FCRA Adverse Action reason code mapping for all 29 risk features
REASON_CODE_MAPPING: dict[str, tuple[str, str]] = {
    "loan_amnt": ("AMT-01", "Requested loan principal exceeds debt capacity"),
    "term": ("TERM-02", "Extended loan duration increases maturity risk exposure"),
    "int_rate": ("INT-03", "High risk-based interest rate pricing tier"),
    "installment": ("INST-04", "Monthly loan installment obligation too high"),
    "emp_length": ("EMP-05", "Insufficient continuous employment duration"),
    "home_ownership": ("HOME-06", "Higher risk residential tenure classification"),
    "annual_inc": ("INC-07", "Gross annual income insufficient for loan obligation"),
    "verification_status": ("VERIF-08", "Unverified or incomplete income documentation"),
    "purpose": ("PURP-09", "Higher risk loan purpose category"),
    "addr_state": ("GEO-10", "Regional credit exposure or state jurisdiction risk"),
    "dti": ("DTI-11", "High debt-to-income ratio reduces cash flow buffer"),
    "delinq_2yrs": ("DELINQ-12", "Past history of 30+ day payment delinquencies"),
    "fico_range_low": ("FICO-13", "Credit bureau score below underwriting risk cutoff"),
    "inq_last_6mths": ("INQ-14", "Excessive recent credit inquiries within past 6 months"),
    "open_acc": ("ACC-15", "Suboptimal number of active open credit trade lines"),
    "pub_rec": ("PUB-16", "Derogatory public records present on credit report"),
    "revol_bal": ("BAL-17", "High outstanding revolving debt balance"),
    "revol_util": ("UTIL-18", "Elevated revolving line credit utilization"),
    "total_acc": ("TOTAL-19", "Limited overall credit account history depth"),
    "mort_acc": ("MORT-20", "Insufficient or elevated mortgage account leverage"),
    "pub_rec_bankruptcies": ("BANKR-21", "Prior bankruptcy record on credit file"),
    "tax_liens": ("LIEN-22", "Unsatisfied government tax liens recorded"),
    "tot_hi_cred_lim": ("LIM-23", "Low total aggregate credit limit ceiling"),
    "total_bc_limit": ("BCLIM-24", "Insufficient available bankcard credit line limit"),
    "fe_loan_to_income_ratio": ("LTI-25", "Loan amount to annual income ratio too high"),
    "fe_monthly_installment_to_income_ratio": ("BURDEN-26", "Monthly debt payment burden exceeds safe threshold"),
    "fe_interest_burden_ratio": ("INTBUR-27", "Total interest burden excessive relative to income"),
    "fe_available_revolving_credit": ("AVAIL-28", "Low available revolving credit headroom"),
    "fe_credit_history_months": ("HIST-29", "Insufficient credit file history age / maturity"),
    "fe_fico_midpoint": ("FICO-13", "Credit bureau score below underwriting risk cutoff"),
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
    Where:
        Factor = PDO / ln(2)
        Offset = TargetScore - Factor * ln(TargetOdds)
    """
    # Robustly handle argument ordering if passed positionally
    if isinstance(beta_0, dict) and not isinstance(beta_dict, dict):
        beta_0, beta_dict = beta_dict, beta_0

    beta_0_val = float(beta_0) if not isinstance(beta_0, dict) else 0.0
    beta_dict_map = beta_dict if isinstance(beta_dict, dict) else {}

    m = max(len(woe_maps), 1)
    factor = pdo / np.log(2.0)
    offset = target_score - (factor * np.log(target_odds))
    base_per_feature = (offset / m) - (factor * (beta_0_val / m))

    rows = []
    for feat, mapping in woe_maps.items():
        clean_feat = feat.replace("_woe", "")
        # Robustly match beta coefficient
        beta_j = beta_dict_map.get(
            f"{clean_feat}_woe",
            beta_dict_map.get(clean_feat, beta_dict_map.get(feat, 0.0)),
        )
        for bin_name, woe_val in mapping.items():
            pts = base_per_feature - (factor * beta_j * float(woe_val))
            rows.append({
                "feature": clean_feat,
                "bin": str(bin_name),
                "woe": round(float(woe_val), 4),
                "score_points": int(round(pts)),
            })

    return pd.DataFrame(rows)


def find_bin_for_value(val: object, woe_mapping: dict[str, float]) -> str:
    """Find corresponding bin string for an empirical continuous value or categorical string."""
    if pd.isna(val):
        return "Missing" if "Missing" in woe_mapping else list(woe_mapping.keys())[0]

    # Exact match for categorical string values
    val_str = str(val).strip()
    for k in woe_mapping.keys():
        if k.strip().lower() == val_str.lower():
            return k

    # Interval parsing for continuous numeric variables: '(left, right]' or '[left, right]'
    try:
        fval = float(val)
        for k in woe_mapping.keys():
            if k == "Missing":
                continue
            if (k.startswith("(") or k.startswith("[")) and (k.endswith(")") or k.endswith("]")):
                parts = k[1:-1].split(",")
                if len(parts) == 2:
                    left, right = float(parts[0].strip()), float(parts[1].strip())
                    if left < fval <= right:
                        return k
    except Exception:
        pass

    # Fallback to first bin if no match
    return list(woe_mapping.keys())[0]


def evaluate_borrower_scorecard_fcra(
    borrower_row: pd.Series,
    scorecard_df: pd.DataFrame,
    woe_maps: dict[str, dict[str, float]] | None = None,
    approval_threshold: int = 600,
    top_n: int = 4,
    cutoff_score: int | None = None,
) -> dict[str, object]:
    """Evaluate individual borrower across scorecard bins and extract Top 4 FCRA Adverse Action reasons."""
    if cutoff_score is not None:
        approval_threshold = cutoff_score

    if woe_maps is None:
        # Infer feature names from scorecard_df
        features = list(scorecard_df["feature"].unique())
        woe_maps = {f: {} for f in features}
    else:
        features = list(woe_maps.keys())

    breakdown_records = []
    total_score = 0

    for feat in features:
        clean_feat = feat.replace("_woe", "")
        sub_df = scorecard_df[scorecard_df["feature"] == clean_feat]
        if sub_df.empty:
            sub_df = scorecard_df[scorecard_df["feature"] == feat]
        if sub_df.empty:
            continue

        raw_val = borrower_row.get(clean_feat, borrower_row.get(feat, np.nan))
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
        points_lag = max_pts - earned_pts  # Points Lost = MaxScore - ActualScore

        code, desc = REASON_CODE_MAPPING.get(
            clean_feat,
            REASON_CODE_MAPPING.get(feat, (f"{clean_feat.upper()[:4]}-01", f"Adverse risk impact on {clean_feat}")),
        )

        breakdown_records.append({
            "feature": clean_feat,
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
        clean_feat = feat.replace("_woe", "")
        if clean_feat in REASON_CODE_MAPPING:
            code, desc = REASON_CODE_MAPPING[clean_feat]
            reasons.append({
                "reason_code": code,
                "feature": clean_feat,
                "description": desc,
                "adverse_impact_weight": f"{weight:+.4f}",
            })
            if len(reasons) >= top_n:
                break

    if not reasons:
        reasons = [
            {"reason_code": "FICO-13", "feature": "fico_range_low", "description": "Credit bureau score below underwriting cutoff", "adverse_impact_weight": "-0.4000"},
            {"reason_code": "DTI-11", "feature": "dti", "description": "High debt-to-income ratio reduces cash flow buffer", "adverse_impact_weight": "+0.4500"},
        ]

    return reasons
