"""High-Density Portfolio Metrics Component Module."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_portfolio_kpi_row(df: pd.DataFrame) -> None:
    """Render high-density top metric row for portfolio overview."""
    total_loans = len(df)
    total_exposure = df["loan_amnt"].sum() if "loan_amnt" in df.columns else 0.0
    avg_int_rate = df["int_rate"].mean() if "int_rate" in df.columns else 0.0
    default_rate = (df["target"].mean() * 100.0) if "target" in df.columns else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Loans", f"{total_loans:,}")
    with c2:
        st.metric("Total Exposure", f"${total_exposure / 1e6:,.2f}M")
    with c3:
        st.metric("Average Interest Rate", f"{avg_int_rate:.2f}%")
    with c4:
        st.metric("Empirical Default Rate", f"{default_rate:.2f}%")
