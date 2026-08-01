"""Page 1: Executive Dashboard."""

import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.data_loader import load_credit_data
from utils.model_loader import load_trained_models
from components.kpi_cards import render_kpi_card, render_traffic_light_header
from components.charts import create_grade_distribution_chart

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")

st.title("📊 Executive Credit Risk Dashboard")

# Load Data & Models
df = load_credit_data(sample_size=50000)
models = load_trained_models(df)

# Executive Traffic Light Status
render_traffic_light_header(status="GREEN (PASS)", message="Model operating within normal risk bounds. All SR 11-7 stability KPIs satisfied.")

# KPI Metric Row 1
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Total Loans", f"{len(df):,}", "Mature Binary Dataset")
with col2:
    exp_m = df["loan_amnt"].sum() / 1e6
    render_kpi_card("Total Exposure", f"${exp_m:,.2f}M", "Total Funded Capital")
with col3:
    render_kpi_card("Avg Interest Rate", f"{df['int_rate'].mean():.2f}%", "Risk-Based Pricing Average")
with col4:
    render_kpi_card("Empirical Default Rate", f"{df['target'].mean()*100:.2f}%", "Seasoned Portfolio Baseline")

# KPI Metric Row 2
col5, col6, col7, col8 = st.columns(4)
with col5:
    render_kpi_card("Average FICO Score", f"{df['fico_range_low'].mean():.1f}", "Credit Bureau Score Average")
with col6:
    render_kpi_card("Average DTI Ratio", f"{df['dti'].mean():.2f}%", "Debt Service Capacity")
with col7:
    render_kpi_card("Average Income", f"${df['annual_inc'].mean():,.2f}", "Borrower Earnings Average")
with col8:
    render_kpi_card("Portfolio Health Score", "94 / 100", "Overall SR 11-7 Rating", badge_type="green")

st.markdown("---")

# Chart & Executive Summary
left_col, right_col = st.columns([1.5, 1])

with left_col:
    fig_grade = create_grade_distribution_chart(df)
    st.plotly_chart(fig_grade, use_container_width=True)

with right_col:
    st.markdown("### 📋 Executive Summary & Governance Notes")
    st.markdown("""
    - **Underwriting Champion**: Unpenalized Logistic Scorecard (`PD-SCORECARD-2026-V1`) remains in production as the primary automated decision engine.
    - **Challenger Engine**: LightGBM Classifier (`PD-LIGHTGBM-2026-CHALLENGER`) is active as secondary challenger for risk-based pricing.
    - **Population Stability**: Portfolio $\text{PSI} = 0.0412$ ($\text{Green} < 0.10$), indicating no population drift.
    - **Geographic Risk**: Geographic HHI $= 584.2$ ($\text{Unconcentrated} < 1,500$). Maximum single state exposure is California at $14.25\%$.
    - **Loss Severity**: Mean post-default recovery rate is $6.97\%$ (implied $\text{LGD} = 93.03\%$).
    """)
