"""Cached Data Loader utility for Dashboard pages."""

from __future__ import annotations

import os
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

# Authoritative set of 29 origination risk features per credit policy & syllabus
SELECTED_29_FEATURES: list[str] = [
    "loan_amnt", "term", "int_rate", "installment", "emp_length",
    "home_ownership", "annual_inc", "verification_status", "purpose", "addr_state",
    "dti", "delinq_2yrs", "fico_range_low", "inq_last_6mths", "open_acc",
    "pub_rec", "revol_bal", "revol_util", "total_acc", "mort_acc",
    "pub_rec_bankruptcies", "tax_liens", "tot_hi_cred_lim", "total_bc_limit",
    "fe_loan_to_income_ratio", "fe_monthly_installment_to_income_ratio",
    "fe_interest_burden_ratio", "fe_available_revolving_credit", "fe_credit_history_months",
]


@st.cache_data(ttl=3600)
def load_credit_data(sample_size: int = 50000) -> pd.DataFrame:
    """Load credit dataset with cached memory management across 29 risk features."""
    root = Path.cwd()
    data_path = root / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"

    cols_to_load = list(set(SELECTED_29_FEATURES + [
        "loan_status", "issue_d", "grade", "sub_grade", "recoveries",
    ]))

    if data_path.is_file():
        try:
            df = pd.read_csv(data_path, usecols=lambda c: c in cols_to_load, nrows=sample_size, low_memory=False)
        except Exception:
            df = pd.read_csv(data_path, nrows=sample_size, low_memory=False)
    else:
        # Demonstration Mode for Streamlit Cloud
        st.info("💡 **Demonstration Mode**: Generating portfolio sample across 29 credit features for dashboard interactivity.")
        np.random.seed(42)
        n = sample_size

        loan_amnt = np.random.uniform(2000, 40000, n).round()
        int_rate = np.random.uniform(5.5, 26.0, n).round(2)
        annual_inc = np.random.lognormal(mean=11.1, sigma=0.55, size=n).clip(20000, 300000).round()
        dti = np.random.uniform(2.0, 38.0, n).round(2)
        fico = np.random.normal(loc=705, scale=45, size=n).clip(620, 845).round()
        revol_util = np.random.uniform(3.0, 98.0, n).round(1)
        tot_hi_lim = np.random.uniform(25000, 350000, n).round()
        total_bc = np.random.uniform(3000, 65000, n).round()
        revol_bal = (total_bc * (revol_util / 100.0)).clip(0, total_bc).round()
        installment = ((loan_amnt * (1 + int_rate / 100.0 * 3.0)) / 36.0).round(2)

        # Correlated default generation (simulates empirical loan underwriting)
        linear_risk = (
            -0.018 * (fico - 700)
            + 0.12 * (int_rate - 12.0)
            + 0.04 * (dti - 18.0)
            - 0.000015 * (annual_inc - 70000)
            + 0.015 * (revol_util - 50.0)
            - 1.45
        )
        prob_default = 1.0 / (1.0 + np.exp(-linear_risk))
        is_bad = np.random.binomial(1, prob_default)

        df = pd.DataFrame({
            "loan_amnt": loan_amnt,
            "term": np.random.choice([" 36 months", " 60 months"], size=n, p=[0.72, 0.28]),
            "int_rate": int_rate,
            "installment": installment,
            "emp_length": np.random.choice(["< 1 year", "2 years", "4 years", "6 years", "10+ years"], size=n),
            "home_ownership": np.random.choice(["MORTGAGE", "RENT", "OWN"], size=n, p=[0.48, 0.42, 0.10]),
            "annual_inc": annual_inc,
            "verification_status": np.random.choice(["Verified", "Source Verified", "Not Verified"], size=n),
            "purpose": np.random.choice(["debt_consolidation", "credit_card", "home_improvement", "major_purchase", "small_business"], size=n),
            "addr_state": np.random.choice(["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "NJ"], size=n),
            "dti": dti,
            "delinq_2yrs": np.random.choice([0, 1, 2, 3], size=n, p=[0.82, 0.12, 0.04, 0.02]),
            "fico_range_low": fico,
            "inq_last_6mths": np.random.choice([0, 1, 2, 3, 4], size=n, p=[0.55, 0.25, 0.12, 0.05, 0.03]),
            "open_acc": np.random.choice(range(4, 25), size=n),
            "pub_rec": np.random.choice([0, 1, 2], size=n, p=[0.86, 0.11, 0.03]),
            "revol_bal": revol_bal,
            "revol_util": revol_util,
            "total_acc": np.random.choice(range(8, 45), size=n),
            "mort_acc": np.random.choice([0, 1, 2, 3, 4], size=n, p=[0.42, 0.28, 0.16, 0.09, 0.05]),
            "pub_rec_bankruptcies": np.random.choice([0, 1, 2], size=n, p=[0.89, 0.09, 0.02]),
            "tax_liens": np.random.choice([0, 1], size=n, p=[0.97, 0.03]),
            "tot_hi_cred_lim": tot_hi_lim,
            "total_bc_limit": total_bc,
            "fe_loan_to_income_ratio": (loan_amnt / (annual_inc + 1.0)).round(4),
            "fe_monthly_installment_to_income_ratio": (installment / ((annual_inc / 12.0) + 1.0)).round(4),
            "fe_interest_burden_ratio": (((installment * 36.0) - loan_amnt) / (annual_inc + 1.0)).round(4),
            "fe_available_revolving_credit": np.maximum(0, total_bc - revol_bal),
            "fe_credit_history_months": np.random.choice(range(48, 360), size=n),
            "issue_d": np.random.choice(["Jan-2015", "Jun-2016", "Mar-2017", "Oct-2018"], size=n),
            "loan_status": np.where(is_bad == 1, "Charged Off", "Fully Paid"),
            "grade": np.random.choice(["A", "B", "C", "D", "E"], size=n),
            "sub_grade": np.random.choice(["A1", "B2", "C3", "D4", "E5"], size=n),
            "recoveries": np.where(is_bad == 1, np.random.uniform(50, 800, n), 0.0),
        })

    # Target Mapping
    bad_statuses = ["Charged Off", "Default", "Does not meet the credit policy. Status:Charged Off", "Late (31-120 days)"]
    good_statuses = ["Fully Paid", "Does not meet the credit policy. Status:Fully Paid"]

    if "target" not in df.columns:
        df["target"] = np.nan
        df.loc[df["loan_status"].isin(bad_statuses), "target"] = 1.0
        df.loc[df["loan_status"].isin(good_statuses), "target"] = 0.0

    df_clean = df.dropna(subset=["target"]).copy()
    df_clean["target"] = df_clean["target"].astype(int)

    # Ensure all 29 features exist in the returned dataframe
    if "fe_loan_to_income_ratio" not in df_clean.columns and "annual_inc" in df_clean.columns and "loan_amnt" in df_clean.columns:
        df_clean["fe_loan_to_income_ratio"] = df_clean["loan_amnt"] / (df_clean["annual_inc"] + 1.0)
    if "fe_monthly_installment_to_income_ratio" not in df_clean.columns and "annual_inc" in df_clean.columns and "installment" in df_clean.columns:
        df_clean["fe_monthly_installment_to_income_ratio"] = df_clean["installment"] / ((df_clean["annual_inc"] / 12.0) + 1.0)
    if "fe_interest_burden_ratio" not in df_clean.columns and "annual_inc" in df_clean.columns:
        df_clean["fe_interest_burden_ratio"] = (df_clean.get("installment", 300) * 36 - df_clean.get("loan_amnt", 10000)) / (df_clean["annual_inc"] + 1.0)
    if "fe_available_revolving_credit" not in df_clean.columns:
        df_clean["fe_available_revolving_credit"] = np.maximum(0, df_clean.get("total_bc_limit", 15000) - df_clean.get("revol_bal", 5000))
    if "fe_credit_history_months" not in df_clean.columns:
        df_clean["fe_credit_history_months"] = 120

    return df_clean
