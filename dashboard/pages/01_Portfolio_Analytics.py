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

from portfolio.segmentation import analyze_recoveries

st.set_page_config(page_title="Portfolio Analytics | Credit Risk Platform", page_icon="📈", layout="wide")

page_header(
    "📈  Portfolio Analytics & Concentration Engine",
    "SR 11-7 · Basel III IRB — Enterprise Credit Risk Analytics",
)

raw_df = load_credit_data(sample_size=40000)
df = render_sidebar_filters(raw_df)

# ── KPI Row ───────────────────────────────────────────────────
label("Portfolio Credit Exposure & Expected Loss Metrics")
total_loans = len(df)
total_ead = float(df["loan_amnt"].sum()) if "loan_amnt" in df.columns else float(total_loans * 15000.0)
exp_m = total_ead / 1e6
mean_pd_dec = float(df["target"].mean()) if "target" in df.columns else 0.20
lgd_benchmark = 0.95
portfolio_el = total_ead * mean_pd_dec * lgd_benchmark
el_m = portfolio_el / 1e6

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Active Loans", f"{total_loans:,}", icon="📋")
with c2:
    render_kpi_card("Total Exposure (EAD)", f"${exp_m:,.1f}M", icon="💰")
with c3:
    render_kpi_card("Observed Default Rate (PD)", f"{mean_pd_dec:.2%}", icon="⚠️", is_positive_good=False)
with c4:
    render_kpi_card("Expected Loss (EL)", f"${el_m:,.2f}M", delta="LGD = 95.0% Benchmark", is_positive_good=False, icon="🔥")

st.markdown(
    f"""
    <div style="background: rgba(15, 30, 60, 0.6); border: 1px solid rgba(96, 165, 250, 0.2); border-radius: 10px; padding: 12px 18px; margin-top: 10px; margin-bottom: 20px;">
        <span style="font-weight: 700; color: #60a5fa; font-size: 0.88rem;">🏛️ Basel III Credit Risk Decomposition:</span>
        <span style="color: #cbd5e1; font-size: 0.86rem; margin-left: 8px;">
            <code>Expected Loss (EL) = PD × LGD × EAD</code> = 
            <code>{mean_pd_dec:.2%} × 95.0% × ${exp_m:,.1f}M = ${el_m:,.2f}M</code>
        </span>
        <div style="color: #94a3b8; font-size: 0.80rem; margin-top: 4px;">
            • <strong>EAD (Exposure at Default):</strong> Total principal commitment outstanding across portfolio loans (&Sigma; loan_amnt).<br>
            • <strong>PD (Probability of Default):</strong> Portfolio empirical default frequency.<br>
            • <strong>LGD (Loss Given Default):</strong> Benchmark 95.0% economic loss severity on unsecured consumer personal loans (accounting for net post-default recoveries).
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
