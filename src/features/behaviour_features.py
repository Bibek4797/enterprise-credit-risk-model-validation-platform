"""Credit-file behaviour and business-risk indicator features."""
from __future__ import annotations
import pandas as pd

def add_behaviour_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    n = lambda c: pd.to_numeric(df.get(c), errors="coerce")
    delinq, pub_rec, bankrupt = n("delinq_2yrs"), n("pub_rec"), n("pub_rec_bankruptcies")
    df["fe_delinquency_count"] = delinq
    df["fe_months_since_last_delinquency"] = n("mths_since_last_delinq")
    df["fe_recent_inquiry_count"] = n("inq_last_6mths")
    df["fe_public_record_flag"] = (pub_rec > 0).astype("Int8")
    df["fe_bankruptcy_flag"] = (bankrupt > 0).astype("Int8")
    df["fe_recent_credit_activity"] = n("acc_open_past_24mths")
    df["fe_multiple_delinquencies_flag"] = (delinq >= 2).astype("Int8")
    df["fe_recent_bankruptcy_flag"] = ((bankrupt > 0) & (n("mths_since_last_record") <= 24)).astype("Int8")
    df["fe_poor_credit_history_flag"] = ((df.get("fe_credit_history_months", pd.Series(index=df.index)) < 60) | (delinq >= 2) | (bankrupt > 0)).astype("Int8")
    df["fe_credit_stress_flag"] = ((df.get("fe_high_debt_risk_flag", 0) == 1) | (df.get("fe_high_utilization_flag", 0) == 1) | (delinq >= 2) | (bankrupt > 0)).astype("Int8")
    df["fe_aggressive_borrower_flag"] = ((df.get("fe_loan_to_income_ratio", 0) >= 0.35) & (df.get("fe_credit_utilization", 0) >= 50)).astype("Int8")
    return df
