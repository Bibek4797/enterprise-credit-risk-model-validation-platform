"""Borrower-level and Portfolio Macro-Level Stress Scenario Generator.

Implements realistic credit stress scenarios (Income drops, DTI surges, FICO shocks,
Interest Rate spikes) aligned with CCAR, DFAST, CECL, and IFRS 9 stress testing standards.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def apply_borrower_scenario(df: pd.DataFrame, scenario_key: str) -> pd.DataFrame:
    """Apply a specific borrower-level stress scenario to input DataFrame."""
    stressed_df = df.copy()

    if scenario_key == "scenario_1_income_minus_10":
        if "annual_inc" in stressed_df.columns:
            stressed_df["annual_inc"] = stressed_df["annual_inc"] * 0.90
        if "fe_loan_to_income_ratio" in stressed_df.columns:
            stressed_df["fe_loan_to_income_ratio"] = stressed_df["fe_loan_to_income_ratio"] / 0.90

    elif scenario_key == "scenario_2_income_minus_20":
        if "annual_inc" in stressed_df.columns:
            stressed_df["annual_inc"] = stressed_df["annual_inc"] * 0.80
        if "fe_loan_to_income_ratio" in stressed_df.columns:
            stressed_df["fe_loan_to_income_ratio"] = stressed_df["fe_loan_to_income_ratio"] / 0.80

    elif scenario_key == "scenario_3_dti_plus_15":
        if "dti" in stressed_df.columns:
            stressed_df["dti"] = stressed_df["dti"] * 1.15

    elif scenario_key == "scenario_4_interest_rate_plus_2":
        if "int_rate" in stressed_df.columns:
            stressed_df["int_rate"] = stressed_df["int_rate"] + 2.0

    elif scenario_key == "scenario_5_utilization_plus_20":
        if "revol_util" in stressed_df.columns:
            stressed_df["revol_util"] = np.minimum(100.0, stressed_df["revol_util"] * 1.20)

    elif scenario_key == "scenario_6_fico_minus_30":
        if "fico_range_low" in stressed_df.columns:
            stressed_df["fico_range_low"] = np.maximum(300.0, stressed_df["fico_range_low"] - 30.0)
        if "fe_fico_midpoint" in stressed_df.columns:
            stressed_df["fe_fico_midpoint"] = np.maximum(300.0, stressed_df["fe_fico_midpoint"] - 30.0)

    elif scenario_key == "scenario_7_loan_amount_plus_15":
        if "loan_amnt" in stressed_df.columns:
            stressed_df["loan_amnt"] = stressed_df["loan_amnt"] * 1.15
        if "installment" in stressed_df.columns:
            stressed_df["installment"] = stressed_df["installment"] * 1.15

    elif scenario_key == "scenario_8_employment_shock":
        if "emp_length" in stressed_df.columns:
            # Map down employment tier
            pass

    return stressed_df


def apply_macro_scenario(df: pd.DataFrame, scenario_type: str = "adverse") -> pd.DataFrame:
    """Apply multi-factor portfolio macroeconomic scenario (Baseline, Adverse, Severe Adverse)."""
    stressed_df = df.copy()

    if scenario_type == "baseline":
        return stressed_df

    elif scenario_type == "adverse":
        # Moderate Economic Slowdown
        if "annual_inc" in stressed_df.columns:
            stressed_df["annual_inc"] = stressed_df["annual_inc"] * 0.90
        if "dti" in stressed_df.columns:
            stressed_df["dti"] = stressed_df["dti"] * 1.10
        if "fico_range_low" in stressed_df.columns:
            stressed_df["fico_range_low"] = np.maximum(300.0, stressed_df["fico_range_low"] - 15.0)
        if "fe_fico_midpoint" in stressed_df.columns:
            stressed_df["fe_fico_midpoint"] = np.maximum(300.0, stressed_df["fe_fico_midpoint"] - 15.0)
        if "revol_util" in stressed_df.columns:
            stressed_df["revol_util"] = np.minimum(100.0, stressed_df["revol_util"] * 1.10)

    elif scenario_type == "severe_adverse":
        # Severe Recession & Debt Crisis
        if "annual_inc" in stressed_df.columns:
            stressed_df["annual_inc"] = stressed_df["annual_inc"] * 0.80
        if "dti" in stressed_df.columns:
            stressed_df["dti"] = stressed_df["dti"] * 1.20
        if "int_rate" in stressed_df.columns:
            stressed_df["int_rate"] = stressed_df["int_rate"] + 3.0
        if "fico_range_low" in stressed_df.columns:
            stressed_df["fico_range_low"] = np.maximum(300.0, stressed_df["fico_range_low"] - 35.0)
        if "fe_fico_midpoint" in stressed_df.columns:
            stressed_df["fe_fico_midpoint"] = np.maximum(300.0, stressed_df["fe_fico_midpoint"] - 35.0)
        if "revol_util" in stressed_df.columns:
            stressed_df["revol_util"] = np.minimum(100.0, stressed_df["revol_util"] * 1.25)

    return stressed_df
