"""Page 04: Macro Stress Testing & Scenario Simulator."""

import sys
from pathlib import Path
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
    from utils.ui_helpers import page_header, section_divider, label
    from components.cards import render_kpi_card
    from components.charts import create_stress_testing_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_stress_testing_chart
    from dashboard.components.tables import render_styled_table

from stress_testing.stress_engine import run_portfolio_stress_test

st.set_page_config(page_title="Stress Testing | Credit Risk Platform", page_icon="⚡", layout="wide")

page_header(
    "⚡  Enterprise Macro Stress Testing & Scenario Simulator",
    "SR 11-7 · Basel III · CCAR — Adverse Scenario Analysis",
)

df          = load_credit_data(sample_size=30000)
models      = load_trained_models(df)
feature_cols = models["features"]

# ── Pre-defined Stress Scenarios ──────────────────────────────
label("Macroeconomic Scenario Expansion Response Suite")
stress_summary = run_portfolio_stress_test(models["predict_scorecard"], df, feature_cols, lgd=0.95)

chart_col, table_col = st.columns([1.4, 1], gap="large")
with chart_col:
    fig_stress = create_stress_testing_chart(stress_summary)
    st.plotly_chart(fig_stress, use_container_width=True)
with table_col:
    label("Scenario Response Table")
    render_styled_table(
        stress_summary[["scenario_name", "mean_predicted_pd", "delta_pd_pct_points", "delta_expected_loss"]].head(8)
    )

section_divider()

# ── Interactive Shock Simulator ───────────────────────────────
label("Interactive Custom Macroeconomic Shock Simulator")

cs1, cs2, cs3, cs4 = st.columns(4)
with cs1:
    inc_shift  = st.slider("Income Shock (%)", -50, 20, -20, 5)
with cs2:
    rate_shift = st.slider("Rate Shift (bps)", -300, 800, 300, 50)
with cs3:
    dti_shift  = st.slider("DTI Shift (%)", -20, 50, 15, 5)
with cs4:
    fico_shift = st.slider("FICO Shift (pts)", -100, 50, -30, 5)

stressed = df.copy()
if "annual_inc"    in stressed.columns:
    stressed["annual_inc"]    = stressed["annual_inc"] * (1.0 + inc_shift / 100.0)
if "int_rate"      in stressed.columns:
    stressed["int_rate"]      = stressed["int_rate"] + (rate_shift / 100.0)
if "dti"           in stressed.columns:
    stressed["dti"]           = stressed["dti"] * (1.0 + dti_shift / 100.0)
if "fico_range_low" in stressed.columns:
    stressed["fico_range_low"] = np.maximum(300.0, stressed["fico_range_low"] + fico_shift)

base_pd    = float(np.mean(models["predict_scorecard"](df)))
custom_pd  = float(np.mean(models["predict_scorecard"](stressed)))
total_exp  = float(df["loan_amnt"].sum())
base_el    = total_exp * base_pd * 0.95
custom_el  = total_exp * custom_pd * 0.95

section_divider()
label("Shock Impact Results")
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_kpi_card("Baseline Mean PD", f"{base_pd * 100:.2f}%", icon="📊")
with m2:
    render_kpi_card("Stressed Mean PD", f"{custom_pd * 100:.2f}%", icon="⚡", is_positive_good=False)
with m3:
    render_kpi_card("Baseline EL", f"${base_el / 1e6:,.2f}M", icon="💼")
with m4:
    render_kpi_card("Stressed EL", f"${custom_el / 1e6:,.2f}M", icon="🔥", is_positive_good=False)
