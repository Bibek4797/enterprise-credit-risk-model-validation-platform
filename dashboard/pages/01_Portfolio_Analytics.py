"""Page 01: Portfolio Analytics & Concentration Engine."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

file_path = Path(__file__).resolve()
dash_dir = file_path.parent.parent if file_path.parent.name == "pages" else file_path.parent
root_dir = dash_dir.parent
for d in [str(root_dir), str(dash_dir), str(root_dir / "src")]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from utils.loaders import load_credit_data
    from utils.ui_helpers import page_header, section_divider, label, inject_css
    from components.sidebar import render_sidebar_filters
    from components.cards import render_kpi_card
    from components.charts import create_vintage_chart, create_grade_distribution_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data
    from dashboard.utils.ui_helpers import page_header, section_divider, label, inject_css
    from dashboard.components.sidebar import render_sidebar_filters
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_vintage_chart, create_grade_distribution_chart
    from dashboard.components.tables import render_styled_table

from portfolio.segmentation import compute_geographic_concentration, analyze_recoveries

st.set_page_config(page_title="Portfolio Analytics | Credit Risk Platform", page_icon="📈", layout="wide")

page_header(
    "📈  Portfolio Analytics & Concentration Engine",
    "SR 11-7 · Basel III IRB — Enterprise Credit Risk Analytics",
)

raw_df = load_credit_data(sample_size=40000)
df = render_sidebar_filters(raw_df)

# ── KPI Row ───────────────────────────────────────────────────
label("Portfolio Metrics")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Filtered Loans", f"{len(df):,}", icon="📋")
with c2:
    exp_m = df["loan_amnt"].sum() / 1e6 if "loan_amnt" in df.columns else 0.0
    render_kpi_card("Filtered Exposure", f"${exp_m:,.1f}M", icon="💰")
with c3:
    conc_res = compute_geographic_concentration(df)
    render_kpi_card("State HHI Index", f"{conc_res['hhi_index']:.1f}", icon="🗺️")
with c4:
    rec_res = analyze_recoveries(df)
    avg_rec = rec_res.get("avg_recovery_amount", 0.0)
    render_kpi_card("Avg Post-Default Recovery", f"${avg_rec:,.2f}", icon="🔄")

section_divider()

# ── Charts ────────────────────────────────────────────────────
col_vint, col_grade = st.columns(2, gap="large")

with col_vint:
    label("Origination Vintage Default Seasoning Curves")
    fig_vint = create_vintage_chart(df)
    st.plotly_chart(fig_vint, use_container_width=True)

with col_grade:
    label("Portfolio Exposure ($M) by Risk Grade")
    fig_grade = create_grade_distribution_chart(df)
    st.plotly_chart(fig_grade, use_container_width=True)

section_divider()

# ── Geographic Table ──────────────────────────────────────────
label("Top 15 States — Geographic Exposure Breakdown")
state_summary = (
    df.groupby("addr_state", observed=False)
    .agg(
        Loans=("addr_state", "count"),
        Exposure_M=("loan_amnt", lambda x: round(x.sum() / 1e6, 2)),
        Default_Rate_Pct=("target", lambda x: round(x.mean() * 100, 2)),
    )
    .sort_values("Exposure_M", ascending=False)
    .reset_index()
    .rename(columns={"addr_state": "State", "Exposure_M": "Exposure ($M)", "Default_Rate_Pct": "Default Rate (%)"})
    .head(15)
)
render_styled_table(state_summary)
