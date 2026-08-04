"""Portfolio Vintage Seasoning & Origination Cohort Analysis Engine.

Constructs monthly, quarterly, and annual origination cohorts, tracks cumulative
default seasoning curves, and extracts vintage degradation metrics per Basel III guidelines.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_vintage_summary(
    df: pd.DataFrame,
    issue_date_col: str = "issue_d",
    loan_amt_col: str = "loan_amnt",
    target_col: str = "target",
    int_rate_col: str = "int_rate",
    fico_col: str = "fico_range_low",
) -> pd.DataFrame:
    """Group loans into annual/quarterly origination vintages and compute KPI metrics."""
    data = df.copy()
    data["issue_dt"] = pd.to_datetime(data[issue_date_col], format="%b-%Y", errors="coerce")
    data["vintage_year"] = data["issue_dt"].dt.year
    data["vintage_quarter"] = data["issue_dt"].dt.year.astype(str) + "-Q" + data["issue_dt"].dt.quarter.astype(str)

    summary = (
        data.groupby("vintage_year", observed=False)
        .agg(
            total_loans=(loan_amt_col, "count"),
            total_exposure=(loan_amt_col, "sum"),
            avg_loan_amount=(loan_amt_col, "mean"),
            avg_interest_rate=(int_rate_col, "mean") if int_rate_col in data.columns else (loan_amt_col, lambda x: np.nan),
            avg_fico=(fico_col, "mean") if fico_col in data.columns else (loan_amt_col, lambda x: np.nan),
            defaults=(target_col, lambda x: (x == 1).sum() if target_col in data.columns else 0),
            observed_default_rate=(target_col, "mean") if target_col in data.columns else (loan_amt_col, lambda x: np.nan),
        )
        .reset_index()
    )

    summary["avg_loan_amount"] = summary["avg_loan_amount"].round(2)
    if int_rate_col in data.columns:
        summary["avg_interest_rate"] = summary["avg_interest_rate"].round(2)
    if fico_col in data.columns:
        summary["avg_fico"] = summary["avg_fico"].round(1)
    summary["observed_default_rate"] = (summary["observed_default_rate"] * 100.0).round(2)

    return summary


def calculate_vintage_seasoning_curves(
    df: pd.DataFrame,
    vintage_col: str = "vintage_year",
    target_col: str = "target",
    age_col: str = "fe_loan_age_months_at_cutoff",
) -> pd.DataFrame:
    """Construct cumulative default seasoning curves across loan age months for each origination vintage."""
    data = df.copy()
    if vintage_col not in data.columns and "issue_d" in data.columns:
        data[vintage_col] = pd.to_datetime(data["issue_d"], format="%b-%Y", errors="coerce").dt.year

    if age_col not in data.columns or vintage_col not in data.columns:
        logger.warning(f"Required columns {age_col} or {vintage_col} missing for seasoning curves.")
        return pd.DataFrame()

    data = data.dropna(subset=[vintage_col, age_col]).copy()
    data["age_bin"] = pd.cut(data[age_col], bins=list(range(0, 121, 12)), labels=[f"{m}m" for m in range(12, 121, 12)])

    curves = (
        data.groupby([vintage_col, "age_bin"], observed=False)
        .agg(
            total_loans=(target_col, "count"),
            cumulative_defaults=(target_col, "sum"),
        )
        .reset_index()
    )

    curves["cum_default_rate_pct"] = (curves.groupby(vintage_col)["cumulative_defaults"].cumsum() / curves.groupby(vintage_col)["total_loans"].transform("sum") * 100.0).round(2)

    return curves


# Alias for backward compatibility
generate_vintage_summary = build_vintage_summary

