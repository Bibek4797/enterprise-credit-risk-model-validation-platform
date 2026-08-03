"""Page 05: Stress Testing & Scenario Simulator."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.loaders import load_credit_data, load_trained_models
from components.charts import create_stress_testing_chart
from components.tables import render_styled_table
from stress_testing.stress_engine import run_portfolio_stress_test

st.set_page_config(page_title="Stress Testing", page_icon="⚡", layout="wide")

st.title("⚡ Enterprise Stress Testing & Scenario Simulator")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)
feature_cols = models["features"]

# Preset Stress Suite Execution
st.markdown("### 📊 Macro & Borrower Stress Testing Response Suite")
stress_summary = run_portfolio_stress_test(models["predict_scorecard"], df, feature_cols, lgd=0.95)

chart_col, table_col = st.columns([1.3, 1])

with chart_col:
    fig_stress = create_stress_testing_chart(stress_summary)
    st.plotly_chart(fig_stress, use_container_width=True)

with table_col:
    st.markdown("### 📋 Stress Response Table")
    render_styled_table(stress_summary[["scenario_name", "mean_predicted_pd", "delta_pd_pct_points", "delta_expected_loss"]].head(8))

st.markdown("---")

# Interactive Custom Stress Simulator
st.markdown("### 🎛️ Interactive Custom Macro Stress Simulator")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    inc_shift = st.slider("Income Shock (%)", min_value=-50, max_value=20, value=-10, step=5)
with col_s2:
    rate_shift = st.slider("Interest Rate Shift (bps)", min_value=-300, max_value=500, value=200, step=50)
with col_s3:
    dti_shift = st.slider("DTI Shift (%)", min_value=-20, max_value=50, value=15, step=5)
with col_s4:
    fico_shift = st.slider("FICO Shift (Points)", min_value=-100, max_value=50, value=-30, step=5)

# Execute Custom Stress
stressed_custom = df.copy()
if "annual_inc" in stressed_custom.columns:
    stressed_custom["annual_inc"] = stressed_custom["annual_inc"] * (1.0 + inc_shift / 100.0)
if "int_rate" in stressed_custom.columns:
    stressed_custom["int_rate"] = stressed_custom["int_rate"] + (rate_shift / 100.0)
if "dti" in stressed_custom.columns:
    stressed_custom["dti"] = stressed_custom["dti"] * (1.0 + dti_shift / 100.0)
if "fico_range_low" in stressed_custom.columns:
    stressed_custom["fico_range_low"] = np.maximum(300.0, stressed_custom["fico_range_low"] + fico_shift)

base_pd = float(np.mean(models["predict_scorecard"](df)))
custom_pd = float(np.mean(models["predict_scorecard"](stressed_custom)))
delta_pd_pts = (custom_pd - base_pd) * 100.0

total_exp = float(df["loan_amnt"].sum())
base_el = total_exp * base_pd * 0.95
custom_el = total_exp * custom_pd * 0.95
delta_el = custom_el - base_el

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Baseline Mean PD", f"{base_pd*100:.2f}%")
with m2:
    st.metric("Stressed Mean PD", f"{custom_pd*100:.2f}%", delta=f"{delta_pd_pts:+.2f}%")
with m3:
    st.metric("Baseline Expected Loss (EL)", f"${base_el/1e6:,.2f}M")
with m4:
    st.metric("Stressed Expected Loss (EL)", f"${custom_el/1e6:,.2f}M", delta=f"${delta_el/1e6:+,.2f}M")
