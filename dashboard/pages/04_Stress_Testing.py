"""Page 04: Macro Stress Testing."""

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
    from utils.loaders import load_credit_data, load_trained_models
    from components.cards import render_kpi_card
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.tables import render_styled_table

from stress_testing.stress_engine import run_portfolio_stress_test

st.set_page_config(page_title="Stress Testing", page_icon="⚡", layout="wide")

st.title("⚡ Enterprise Macro Stress Testing & Capital Adequacy")
st.caption("Enterprise Credit Risk Analytics & Model Risk Governance Platform (SR 11-7 / Basel III)")
st.markdown("---")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)

predict_fn = models["predict_lgb"]
features = models["features"]

stress_df = run_portfolio_stress_test(predict_fn, df, features)

st.markdown("### 📊 Macroeconomic Scenario Expansion Summary")
render_styled_table(stress_df)

st.markdown("---")
st.markdown("### 🎛️ Interactive Macro Economic Shock Simulator")

income_shock_pct = st.slider("Borrower Income Shock (%)", min_value=-40.0, max_value=10.0, value=-20.0, step=5.0)
int_rate_shock_pts = st.slider("Interest Rate Shift (+ Percentage Points)", min_value=0.0, max_value=8.0, value=3.0, step=0.5)

shocked_df = df.copy()
if "annual_inc" in shocked_df.columns:
    shocked_df["annual_inc"] = shocked_df["annual_inc"] * (1.0 + (income_shock_pct / 100.0))
if "int_rate" in shocked_df.columns:
    shocked_df["int_rate"] = shocked_df["int_rate"] + int_rate_shock_pts

base_pd = predict_fn(df).mean()
shocked_pd = predict_fn(shocked_df).mean()
delta_pd = shocked_pd - base_pd

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    render_kpi_card("Baseline Mean PD", f"{base_pd:.2%}")
with col_s2:
    render_kpi_card("Stressed Mean PD", f"{shocked_pd:.2%}", is_positive_good=False)
with col_s3:
    render_kpi_card("Delta PD Shift", f"{delta_pd * 100:+.2f}% pts", is_positive_good=False)
