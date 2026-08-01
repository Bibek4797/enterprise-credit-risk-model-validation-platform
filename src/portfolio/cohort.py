"""Multi-dimensional cohort performance matrix analysis for retail credit portfolios."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_cohort_performance_matrix(
    df: pd.DataFrame,
    cohort_col: str = "grade",
    target_col: str = "target",
    loan_amt_col: str = "loan_amnt",
    int_rate_col: str = "int_rate",
    fico_col: str = "fico_range_low",
    dti_col: str = "dti",
) -> pd.DataFrame:
    """Generate multi-dimensional cohort performance matrix for any categorical attribute."""
    if cohort_col not in df.columns:
        raise ValueError(f"Cohort column {cohort_col} not found in DataFrame.")

    data = df.dropna(subset=[cohort_col]).copy()
    total_exposure = data[loan_amt_col].sum() if loan_amt_col in data.columns else 1.0

    summary = (
        data.groupby(cohort_col, observed=False)
        .agg(
            loan_count=(cohort_col, "count"),
            total_exposure=(loan_amt_col, "sum") if loan_amt_col in data.columns else (cohort_col, lambda x: np.nan),
            avg_loan_amount=(loan_amt_col, "mean") if loan_amt_col in data.columns else (cohort_col, lambda x: np.nan),
            observed_default_rate=(target_col, "mean") if target_col in data.columns else (cohort_col, lambda x: np.nan),
            avg_interest_rate=(int_rate_col, "mean") if int_rate_col in data.columns else (cohort_col, lambda x: np.nan),
            avg_fico=(fico_col, "mean") if fico_col in data.columns else (cohort_col, lambda x: np.nan),
            avg_dti=(dti_col, "mean") if dti_col in data.columns else (cohort_col, lambda x: np.nan),
        )
        .reset_index()
    )

    if loan_amt_col in data.columns:
        summary["exposure_share_pct"] = ((summary["total_exposure"] / total_exposure) * 100.0).round(2)
        summary["avg_loan_amount"] = summary["avg_loan_amount"].round(2)
    if target_col in data.columns:
        summary["observed_default_rate"] = (summary["observed_default_rate"] * 100.0).round(2)
    if int_rate_col in data.columns:
        summary["avg_interest_rate"] = summary["avg_interest_rate"].round(2)
    if fico_col in data.columns:
        summary["avg_fico"] = summary["avg_fico"].round(1)
    if dti_col in data.columns:
        summary["avg_dti"] = summary["avg_dti"].round(2)

    return summary.sort_values("loan_count", ascending=False).reset_index(drop=True)
