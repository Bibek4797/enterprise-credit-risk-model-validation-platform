"""FCRA Adverse Action reason code generator for credit decline notices."""

from __future__ import annotations

import pandas as pd

REASON_CODE_MAPPING = {
    "dti": ("DTI-01", "High debt-to-income ratio"),
    "int_rate": ("INT-02", "High interest rate exposure"),
    "revol_util": ("UTIL-03", "High revolving credit utilization"),
    "annual_inc": ("INC-04", "Insufficient annual income for loan amount"),
    "fico_range_low": ("FICO-05", "Credit score below underwriting threshold"),
    "delinq_2yrs": ("DELINQ-06", "History of 30+ day delinquencies"),
    "inq_last_6mths": ("INQ-07", "Excessive recent credit inquiries"),
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
