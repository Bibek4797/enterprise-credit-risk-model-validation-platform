"""Within-borrower application-time account and recency aggregates."""
from __future__ import annotations
import numpy as np
import pandas as pd

def add_aggregation_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    n = lambda c: pd.to_numeric(df.get(c), errors="coerce")
    total_acc, open_acc, rev_acc = n("total_acc"), n("open_acc"), n("num_rev_accts")
    df["fe_open_account_share"] = open_acc / total_acc.replace(0, np.nan)
    df["fe_active_revolving_account_share"] = n("num_actv_rev_tl") / rev_acc.replace(0, np.nan)
    df["fe_average_revolving_balance_per_account"] = n("revol_bal") / rev_acc.replace(0, np.nan)
    df["fe_recent_account_opening_rate"] = n("acc_open_past_24mths") / total_acc.replace(0, np.nan)
    df["fe_delinquency_frequency"] = n("num_accts_ever_120_pd") / total_acc.replace(0, np.nan)
    df["fe_recent_inquiry_rate"] = n("inq_last_6mths") / (df.get("fe_credit_history_months", pd.Series(index=df.index)) / 6).clip(lower=1)
    df["fe_bank_card_utilization_gap"] = n("bc_util") - n("revol_util")
    return df
