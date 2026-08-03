"""Multi-variate Sidebar Filter Controls Component Module."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> dict[str, object]:
    """Render interactive sidebar filter controls for portfolio segmentation."""
    st.sidebar.markdown("### 🎛️ Portfolio Filters")

    # Grade Filter
    grades = sorted(df["grade"].dropna().unique().tolist()) if "grade" in df.columns else []
    selected_grades = st.sidebar.multiselect("Risk Grade (A-G)", options=grades, default=grades)

    # State Filter
    states = sorted(df["addr_state"].dropna().unique().tolist()) if "addr_state" in df.columns else []
    selected_states = st.sidebar.multiselect("US State", options=states, default=states[:10] if len(states) > 10 else states)

    # Purpose Filter
    purposes = sorted(df["purpose"].dropna().unique().tolist()) if "purpose" in df.columns else []
    selected_purposes = st.sidebar.multiselect("Loan Purpose", options=purposes, default=purposes)

    # FICO Score Slider
    min_fico = int(df["fico_range_low"].min()) if "fico_range_low" in df.columns else 600
    max_fico = int(df["fico_range_low"].max()) if "fico_range_low" in df.columns else 850
    selected_fico = st.sidebar.slider("FICO Score Range", min_value=min_fico, max_value=max_fico, value=(min_fico, max_fico))

    # Apply Filters
    filtered_df = df.copy()
    if selected_grades and "grade" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["grade"].isin(selected_grades)]
    if selected_states and "addr_state" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["addr_state"].isin(selected_states)]
    if selected_purposes and "purpose" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["purpose"].isin(selected_purposes)]
    if "fico_range_low" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["fico_range_low"] >= selected_fico[0]) & (filtered_df["fico_range_low"] <= selected_fico[1])
        ]

    return {
        "filtered_df": filtered_df,
        "selected_grades": selected_grades,
        "selected_states": selected_states,
        "selected_purposes": selected_purposes,
        "selected_fico": selected_fico,
    }
