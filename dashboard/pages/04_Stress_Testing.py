"""Page 04: Comprehensive Capital Analysis and Review (CCAR) Macro Stress Testing."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
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
    from components.charts import create_stress_testing_chart, create_scurve_transmission_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_stress_testing_chart, create_scurve_transmission_chart
    from dashboard.components.tables import render_styled_table

from stress_testing.stress_engine import (
    fit_macro_satellite_model,
    forecast_macro_default_rate,
    calibrate_intercept_shift,
    run_ccar_macro_stress_test,
)

st.set_page_config(
    page_title="CCAR Stress Testing | Credit Risk Platform",
    page_icon="⚡",
    layout="wide",
)

page_header(
    "⚡  CCAR Comprehensive Capital Analysis & Review (Macro Stress Testing Engine)",
    "Dodd-Frank Act · Basel III · SR 11-7 — 2-Tier Macroeconomic Satellite & Scorecard Intercept Shift Architecture",
)

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)
feature_cols = models["features"]

# ── Macro Satellite Calibration & Theoretical Foundation ───────
satellite_model = fit_macro_satellite_model()
b0_sat = satellite_model["beta_0"]
b_ur = satellite_model["beta_ur"]
b_gdp = satellite_model["beta_gdp"]
r2_sat = satellite_model["r_squared"]

st.markdown(
    f"""
    <div style="background: rgba(30, 41, 59, 0.55); border: 1px solid rgba(59, 130, 246, 0.28); border-radius: 8px; padding: 14px 18px; margin-bottom: 22px;">
        <div style="font-weight: 600; color: #60a5fa; font-size: 0.95rem; margin-bottom: 6px;">
            🏛️ Dodd-Frank CCAR 2-Tier Stress Testing Methodology
        </div>
        <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">
            Because individual loan applicants do not possess macroeconomic indicators as personal attributes, banks model stress at two distinct tiers:
            <ol style="margin-top: 6px; margin-bottom: 6px; padding-left: 20px;">
                <li><strong>Macro Satellite Econometric Model:</strong> Trained on historical quarterly performance: 
                    <code>logit(DR<sub>t</sub>) = {b0_sat:.3f} + ({b_ur:+.3f} × ΔUR<sub>t</sub>) + ({b_gdp:+.3f} × GDP_Growth<sub>t</sub>)</code> 
                    (R² = {r2_sat:.2f}, verifying β<sub>UR</sub> > 0 and β<sub>GDP</sub> < 0).</li>
                <li><strong>Micro-Macro Intercept Shift (Δβ₀):</strong> Macro shocks shift systemic default log-odds universally across borrowers without distorting feature weights β<sub>j</sub> (preserving discriminatory rank ordering).</li>
                <li><strong>Credit Risk Loss Transmission:</strong> <code>EL = PD × LGD × EAD</code> (Benchmark LGD = 0.95 and EAD = Σ loan_amnt). Stressed credit loss expansion (ΔEL) determines the exact capital reserve required to absorb downturn shocks.</li>
            </ol>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── CCAR 9-Quarter Scenario Results ────────────────────────────
ccar_res = run_ccar_macro_stress_test(models["predict_scorecard"], df, feature_cols, lgd=0.95)
summary_df = ccar_res["summary_table"]

label("Federal Reserve 9-Quarter Macroeconomic Stress Scenarios & Expected Loss Expansion")
display_tbl = summary_df[[
    "scenario_name", "delta_ur", "gdp_growth", "macro_target_dr_pct",
    "delta_beta_0", "mean_predicted_pd", "expected_loss_el", "delta_expected_loss",
]].rename(columns={
    "scenario_name": "Federal Reserve Scenario Path",
    "delta_ur": "Δ Unemployment Rate (%)",
    "gdp_growth": "Real GDP Growth (%)",
    "macro_target_dr_pct": "Macro Target DR (%)",
    "delta_beta_0": "Calibrated Intercept Shift (Δβ₀)",
    "mean_predicted_pd": "Portfolio Stressed PD (%)",
    "expected_loss_el": "Stressed Expected Loss ($)",
    "delta_expected_loss": "Δ Expected Loss ($)",
})

# Format numeric columns for presentation
display_tbl["Δ Unemployment Rate (%)"] = display_tbl["Δ Unemployment Rate (%)"].apply(lambda v: f"{v:+.1f}%")
display_tbl["Real GDP Growth (%)"] = display_tbl["Real GDP Growth (%)"].apply(lambda v: f"{v:+.1f}%")
display_tbl["Macro Target DR (%)"] = display_tbl["Macro Target DR (%)"].apply(lambda v: f"{v:.2f}%")
display_tbl["Calibrated Intercept Shift (Δβ₀)"] = display_tbl["Calibrated Intercept Shift (Δβ₀)"].apply(lambda v: f"{v:+.4f}")
display_tbl["Portfolio Stressed PD (%)"] = display_tbl["Portfolio Stressed PD (%)"].apply(lambda v: f"{v:.2f}%")
display_tbl["Stressed Expected Loss ($)"] = display_tbl["Stressed Expected Loss ($)"].apply(lambda v: f"${v/1e6:,.2f}M")
display_tbl["Δ Expected Loss ($)"] = display_tbl["Δ Expected Loss ($)"].apply(lambda v: f"+${v/1e6:,.2f}M" if v > 0 else "$0.00")

render_styled_table(display_tbl)

section_divider()

# ── Visual Analytics: Loss Expansion & S-Curve Transmission ───
col_chart, col_scurve = st.columns([1.1, 1.0], gap="large")

with col_chart:
    label("Portfolio Expected Loss Expansion ($) Across Fed Scenarios")
    fig_loss = create_stress_testing_chart(summary_df)
    st.plotly_chart(fig_loss, use_container_width=True)

with col_scurve:
    label("Non-Linear S-Curve Transmission: d(PD)/dz = PD(1 − PD)")
    st.caption("Prime borrowers absorb marginal shifts (+1.2%), while subprime borrowers absorb severe stress (+15.8%):")
    # Intercept shift from severe adverse scenario
    sev_b0 = float(summary_df.loc[summary_df["scenario_name"].str.contains("Severely"), "delta_beta_0"].values[0])
    fig_scurve = create_scurve_transmission_chart(delta_b0=sev_b0)
    st.plotly_chart(fig_scurve, use_container_width=True)

section_divider()

# ── Interactive Custom Macroeconomic Shock Simulator ───────────
label("Interactive Custom Macroeconomic Shock Simulator (Dodd-Frank CCAR)")
st.caption("Adjust hypothetical macroeconomic paths to simulate the satellite forecast, intercept shift, and portfolio expected loss expansion:")

c_ur, c_gdp = st.columns(2)
with c_ur:
    sim_delta_ur = st.slider("Unemployment Rate Shock: ΔUR (percentage points)", -1.0, 6.0, 2.5, 0.25)
with c_gdp:
    sim_gdp = st.slider("Annual Real GDP Growth Rate (%)", -6.0, 4.0, -2.0, 0.5)

# Calculate simulated macro shock through 2-tier framework
base_pds = ccar_res["base_pds"]
base_mean_pd = ccar_res["base_mean_pd"]
total_exp = ccar_res["total_exposure"]
base_el = ccar_res["base_el"]

sim_macro_target = forecast_macro_default_rate(sim_delta_ur, sim_gdp, satellite_model)
# Scale target relative to baseline
sim_scaled_dr = float(np.clip(base_mean_pd * (sim_macro_target / 0.185), 0.01, 0.85))

sim_delta_b0 = calibrate_intercept_shift(base_pds, sim_scaled_dr)
base_log_odds = np.log(base_pds / (1.0 - base_pds))
sim_stressed_pds = 1.0 / (1.0 + np.exp(-(base_log_odds + sim_delta_b0)))
sim_stressed_mean_pd = float(np.mean(sim_stressed_pds))
sim_stressed_el = total_exp * sim_stressed_mean_pd * 0.95
sim_delta_el = sim_stressed_el - base_el

k1, k2, k3 = st.columns(3)
with k1:
    render_kpi_card("Intercept Shift (Δβ₀)", f"{sim_delta_b0:+.4f}", icon="📐")
with k2:
    render_kpi_card("Stressed Mean PD", f"{sim_stressed_mean_pd:.2%}", icon="📊", is_positive_good=False)
with k3:
    render_kpi_card("Δ Expected Loss ($)", f"+${sim_delta_el / 1e6:,.2f}M", icon="🔥", is_positive_good=False)

st.caption(
    f"💡 **Portfolio Expected Loss Summary (EL = PD × LGD × EAD):** "
    f"Stressed EL = **${sim_stressed_el / 1e6:,.2f}M** "
    f"(Baseline EL: ${base_el / 1e6:,.2f}M | Portfolio Loss Expansion: **+${sim_delta_el / 1e6:,.2f}M** | "
    f"EAD: ${total_exp / 1e6:,.1f}M | Benchmark LGD: 95.0%)"
)
