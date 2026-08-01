"""Application-time affordability, exposure, and banding features."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _num(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(frame.get(column), errors="coerce")

def _percent(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(frame.get(column, pd.Series(index=frame.index, dtype="object")).astype(str).str.replace("%", "", regex=False), errors="coerce")


def add_financial_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add financial features without mutating the caller's frame."""
    df = frame.copy()
    loan, income = _num(df, "loan_amnt"), _num(df, "annual_inc")
    installment, rate = _num(df, "installment"), _percent(df, "int_rate")
    revol_bal, revol_limit, dti = _num(df, "revol_bal"), _num(df, "total_rev_hi_lim"), _num(df, "dti")
    term = pd.to_numeric(df.get("term", pd.Series(index=df.index, dtype="object")).astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    df["fe_loan_to_income_ratio"] = loan / income.replace(0, np.nan)
    df["fe_interest_rate_numeric"] = rate
    df["fe_monthly_installment_to_income_ratio"] = installment / (income / 12).replace(0, np.nan)
    df["fe_interest_burden_ratio"] = ((installment * term) - loan) / loan.replace(0, np.nan)
    df["fe_credit_utilization"] = _percent(df, "revol_util")
    df["fe_available_revolving_credit"] = revol_limit - revol_bal
    df["fe_credit_exposure"] = loan + revol_bal.fillna(0)
    df["fe_debt_burden"] = dti
    df["fe_income_band"] = pd.cut(income, [-np.inf, 40000, 60000, 80000, 120000, np.inf], labels=["low", "lower_middle", "middle", "upper_middle", "high"])
    df["fe_loan_size_band"] = pd.cut(loan, [-np.inf, 5000, 10000, 20000, 30000, np.inf], labels=["very_small", "small", "medium", "large", "very_large"])
    df["fe_interest_rate_band"] = pd.cut(rate, [-np.inf, 8, 12, 16, 20, np.inf], labels=["low", "moderate", "elevated", "high", "very_high"])
    df["fe_revolving_utilization_category"] = pd.cut(df["fe_credit_utilization"], [-np.inf, 25, 50, 75, 100, np.inf], labels=["low", "moderate", "elevated", "high", "over_limit"])
    df["fe_payment_burden_category"] = pd.cut(df["fe_monthly_installment_to_income_ratio"], [-np.inf, 0.05, 0.10, 0.20, np.inf], labels=["low", "moderate", "high", "very_high"])
    df["fe_dti_category"] = pd.cut(dti, [-np.inf, 10, 20, 30, 40, np.inf], labels=["low", "moderate", "elevated", "high", "very_high"])
    df["fe_high_debt_risk_flag"] = ((dti >= 30) | (df["fe_monthly_installment_to_income_ratio"] >= 0.20)).astype("Int8")
    df["fe_low_income_risk_flag"] = (income < 40000).astype("Int8")
    df["fe_high_interest_risk_flag"] = (rate >= 16).astype("Int8")
    df["fe_high_utilization_flag"] = (df["fe_credit_utilization"] >= 75).astype("Int8")
    df["fe_high_risk_borrower_flag"] = ((df["fe_high_debt_risk_flag"] + df["fe_low_income_risk_flag"] + df["fe_high_interest_risk_flag"] + df["fe_high_utilization_flag"]) >= 2).astype("Int8")
    return df
