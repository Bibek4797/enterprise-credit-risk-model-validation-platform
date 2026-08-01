"""Interactive Sidebar Filter component for multi-dimensional data filtering."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render interactive sidebar filter controls and return filtered DataFrame."""
    st.sidebar.markdown("### 🎛️ Portfolio Global Filters")

    filtered_df = df.copy()

    # 1. Risk Grade Filter
    if "grade" in df.columns:
        all_grades = sorted(df["grade"].dropna().unique())
        selected_grades = st.sidebar.multiselect("Risk Grade Filter", options=all_grades, default=all_grades)
        if selected_grades:
            filtered_df = filtered_df[filtered_df["grade"].isin(selected_grades)]

    # 2. State Filter
    if "addr_state" in df.columns:
        all_states = sorted(df["addr_state"].dropna().unique())
        selected_states = st.sidebar.multiselect("Geographic State Filter", options=all_states, default=[])
        if selected_states:
            filtered_df = filtered_df[filtered_df["addr_state"].isin(selected_states)]

    # 3. Purpose Filter
    if "purpose" in df.columns:
        all_purposes = sorted(df["purpose"].dropna().unique())
        selected_purposes = st.sidebar.multiselect("Loan Purpose Filter", options=all_purposes, default=[])
        if selected_purposes:
            filtered_df = filtered_df[filtered_df["purpose"].isin(selected_purposes)]

    # 4. FICO Range Filter
    if "fico_range_low" in df.columns:
        min_fico = float(df["fico_range_low"].min())
        max_fico = float(df["fico_range_low"].max())
        selected_fico = st.sidebar.slider("FICO Score Range", min_value=min_fico, max_value=max_fico, value=(min_fico, max_fico))
        filtered_df = filtered_df[(filtered_df["fico_range_low"] >= selected_fico[0]) & (filtered_df["fico_range_low"] <= selected_fico[1])]

    # 5. Loan Amount Range Filter
    if "loan_amnt" in df.columns:
        min_amt = float(df["loan_amnt"].min())
        max_amt = float(df["loan_amnt"].max())
        selected_amt = st.sidebar.slider("Loan Amount ($)", min_value=min_amt, max_value=max_amt, value=(min_amt, max_amt))
        filtered_df = filtered_df[(filtered_df["loan_amnt"] >= selected_amt[0]) & (filtered_df["loan_amnt"] <= selected_amt[1])]

    st.sidebar.markdown(f"**Filtered Portfolio Records**: `{len(filtered_df):,}` / `{len(df):,}`")
    return filtered_df
