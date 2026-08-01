"""Origination and credit-history timing features with a fixed portfolio cut-off."""
from __future__ import annotations
import pandas as pd

PORTFOLIO_CUTOFF = pd.Timestamp("2018-12-31")

def add_time_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    issue = pd.to_datetime(df.get("issue_d"), format="%b-%Y", errors="coerce")
    earliest = pd.to_datetime(df.get("earliest_cr_line"), format="%b-%Y", errors="coerce")
    df["fe_issue_year"] = issue.dt.year.astype("Int16")
    df["fe_issue_quarter"] = issue.dt.quarter.astype("Int8")
    df["fe_issue_month"] = issue.dt.month.astype("Int8")
    df["fe_issue_month_sin"] = (2 * 3.14159265 * df["fe_issue_month"] / 12).apply(__import__("numpy").sin)
    df["fe_issue_month_cos"] = (2 * 3.14159265 * df["fe_issue_month"] / 12).apply(__import__("numpy").cos)
    df["fe_loan_age_months_at_cutoff"] = ((PORTFOLIO_CUTOFF.year - issue.dt.year) * 12 + PORTFOLIO_CUTOFF.month - issue.dt.month).astype("Int16")
    df["fe_credit_history_months"] = ((issue.dt.year - earliest.dt.year) * 12 + issue.dt.month - earliest.dt.month).astype("Int16")
    df["fe_credit_age_years"] = df["fe_credit_history_months"] / 12
    df["fe_year_end_origination_flag"] = df["fe_issue_month"].isin([10, 11, 12]).astype("Int8")
    df["fe_economic_cycle_proxy"] = pd.cut(df["fe_issue_year"], [2006, 2009, 2013, 2016, 2018], labels=["crisis", "recovery", "expansion", "late_cycle"])
    return df
