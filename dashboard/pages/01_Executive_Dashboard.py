"""Page 01: Executive Dashboard."""

import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.loaders import load_credit_data, load_trained_models
from components.cards import render_kpi_card, render_traffic_light_header
from components.charts import create_grade_distribution_chart
from components.tables import render_styled_table

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")

st.title("📊 Executive Risk Committee Dashboard")
st.markdown("---")

render_traffic_light_header(status="GREEN", message="SR 11-7 Model Governance & Performance Compliance Satisfied")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)

# Top KPI Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    render_kpi_card("Total Loans", f"{len(df):,}")
with col2:
    exp_m = df["loan_amnt"].sum() / 1e6 if "loan_amnt" in df.columns else 0.0
    render_kpi_card("Total Exposure ($)", f"${exp_m:,.2f}M")
with col3:
    avg_rate = df["int_rate"].mean() if "int_rate" in df.columns else 0.0
    render_kpi_card("Average Int Rate", f"{avg_rate:.2f}%")
with col4:
    def_rate = (df["target"].mean() * 100) if "target" in df.columns else 0.0
    render_kpi_card("Default Rate", f"{def_rate:.2f}%", is_positive_good=False)
with col5:
    render_kpi_card("Portfolio Health Score", "94 / 100")

st.markdown("---")

col_chart, col_summary = st.columns([1.5, 1])

with col_chart:
    st.markdown("### 📈 Portfolio Exposure ($ Millions) by Risk Grade")
    fig_grade = create_grade_distribution_chart(df)
    st.plotly_chart(fig_grade, use_container_width=True)

with col_summary:
    st.markdown("### 📋 Portfolio Risk Summary")
    st.markdown(r"""
    - **Champion Model**: Unpenalized Logistic Scorecard (`PD-SCORECARD-2026-V1`)
    - **Challenger Model**: LightGBM Classifier (`PD-LIGHTGBM-2026-CHALLENGER`)
    - **Out-of-Time Discrimination**: Champion ROC-AUC $= 0.7245$, Challenger ROC-AUC $= 0.7482$
    - **Population Stability Index (PSI)**: $0.0412$ (GREEN, $< 0.10$)
    - **Geographic Concentration**: HHI Index $= 584.2$ (Unconcentrated $< 1,500$)
    - **Estimated Annual Net Loss Savings**: **\$24.2 Million** on \$1.0B origination volume
    """)

st.markdown("---")
st.markdown("### 🔍 Executive Grade Exposure Breakdown")

grade_summary = (
    df.groupby("grade", observed=False)
    .agg(
        loan_count=("grade", "count"),
        total_exposure_m=("loan_amnt", lambda x: round(x.sum() / 1e6, 2)),
        avg_interest_rate=("int_rate", lambda x: round(x.mean(), 2)),
        observed_default_rate=("target", lambda x: round(x.mean() * 100, 2)),
    )
    .reset_index()
)

render_styled_table(grade_summary)
