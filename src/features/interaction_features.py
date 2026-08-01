"""Business-motivated interaction features; no data-driven feature selection."""
from __future__ import annotations
import pandas as pd

def add_interaction_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    n = lambda c: pd.to_numeric(df.get(c), errors="coerce")
    income, loan, rate, dti, fico = n("annual_inc"), n("loan_amnt"), n("fe_interest_rate_numeric"), n("dti"), n("fe_fico_midpoint")
    util, delinq = n("revol_util"), n("delinq_2yrs")
    df["fe_income_x_loan_amount"] = income * loan
    df["fe_income_x_interest_rate"] = income * rate
    df["fe_grade_x_interest_rate"] = n("fe_grade_ordinal") * rate
    df["fe_grade_x_fico"] = n("fe_grade_ordinal") * fico
    df["fe_loan_amount_x_credit_utilization"] = loan * util
    df["fe_interest_rate_x_dti"] = rate * dti
    df["fe_dti_x_revolving_utilization"] = dti * util
    df["fe_fico_x_delinquencies"] = fico * delinq
    df["fe_employment_known_x_income"] = n("fe_employment_known_flag") * income
    return df
