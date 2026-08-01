"""Cached Data Loader utility for Dashboard pages."""

from __future__ import annotations

import os
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data(ttl=3600)
def load_credit_data(sample_size: int = 50000) -> pd.DataFrame:
    """Load credit dataset with cached memory management."""
    # Find repository root
    root = Path.cwd()
    data_path = root / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"

    cols_to_load = [
        "loan_status", "issue_d", "loan_amnt", "funded_amnt", "int_rate", "installment",
        "annual_inc", "dti", "fico_range_low", "revol_util", "delinq_2yrs", "inq_last_6mths",
        "grade", "sub_grade", "term", "home_ownership", "purpose", "addr_state", "recoveries",
        "fe_loan_to_income_ratio", "fe_monthly_installment_to_income_ratio", "fe_interest_burden_ratio",
        "fe_available_revolving_credit"
    ]

    if data_path.is_file():
        try:
            df = pd.read_csv(data_path, usecols=lambda c: c in cols_to_load, nrows=sample_size, low_memory=False)
        except Exception:
            df = pd.read_csv(data_path, nrows=sample_size, low_memory=False)
    else:
        # Fallback synthetic dataset generator if data path is unavailable
        np.random.seed(42)
        n = sample_size
        df = pd.DataFrame({
            "loan_amnt": np.random.uniform(1000, 40000, n),
            "funded_amnt": np.random.uniform(1000, 40000, n),
            "int_rate": np.random.uniform(5, 25, n),
            "annual_inc": np.random.uniform(20000, 150000, n),
            "dti": np.random.uniform(1, 35, n),
            "fico_range_low": np.random.uniform(660, 850, n),
            "revol_util": np.random.uniform(5, 95, n),
            "inq_last_6mths": np.random.choice([0, 1, 2, 3, 4], size=n),
            "grade": np.random.choice(["A", "B", "C", "D", "E", "F", "G"], size=n, p=[0.18, 0.28, 0.28, 0.15, 0.07, 0.03, 0.01]),
            "sub_grade": np.random.choice(["A1", "B2", "C3", "D4", "E5"], size=n),
            "term": np.random.choice([" 36 months", " 60 months"], size=n, p=[0.7, 0.3]),
            "home_ownership": np.random.choice(["MORTGAGE", "RENT", "OWN"], size=n),
            "purpose": np.random.choice(["debt_consolidation", "credit_card", "home_improvement", "small_business"], size=n),
            "addr_state": np.random.choice(["CA", "TX", "NY", "FL", "IL"], size=n),
            "issue_d": np.random.choice(["Jan-2015", "Jun-2016", "Mar-2017", "Oct-2018"], size=n),
            "loan_status": np.random.choice(["Fully Paid", "Charged Off", "Current"], size=n, p=[0.75, 0.20, 0.05]),
            "recoveries": np.random.uniform(0, 500, n),
        })

    # Target Mapping
    bad_statuses = ["Charged Off", "Default", "Does not meet the credit policy. Status:Charged Off", "Late (31-120 days)"]
    good_statuses = ["Fully Paid", "Does not meet the credit policy. Status:Fully Paid"]

    df["target"] = np.nan
    df.loc[df["loan_status"].isin(bad_statuses), "target"] = 1.0
    df.loc[df["loan_status"].isin(good_statuses), "target"] = 0.0

    df_clean = df.dropna(subset=["target"]).copy()
    df_clean["target"] = df_clean["target"].astype(int)

    # Feature Engineering defaults
    if "fe_fico_midpoint" not in df_clean.columns and "fico_range_low" in df_clean.columns:
        df_clean["fe_fico_midpoint"] = df_clean["fico_range_low"] + 2.5
    if "fe_loan_to_income_ratio" not in df_clean.columns and "annual_inc" in df_clean.columns:
        df_clean["fe_loan_to_income_ratio"] = df_clean["loan_amnt"] / (df_clean["annual_inc"] + 1.0)

    return df_clean
