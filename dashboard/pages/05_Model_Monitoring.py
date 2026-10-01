"""Page 05: Model Monitoring & Stability Surveillance."""

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
    from components.cards import render_traffic_light_header, render_kpi_card
    from components.tables import render_styled_table
    from components.charts import create_model_psi_distribution_chart, create_csi_ranking_chart
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.cards import render_traffic_light_header, render_kpi_card
    from dashboard.components.tables import render_styled_table
    from dashboard.components.charts import create_model_psi_distribution_chart, create_csi_ranking_chart

from monitoring.psi import calculate_array_psi
from monitoring.csi import build_portfolio_csi_report
from monitoring.retraining import evaluate_retraining_triggers

st.set_page_config(page_title="Model Monitoring | Credit Risk Platform", page_icon="🛡️", layout="wide")

page_header(
    "🛡️  Enterprise Model Monitoring & Stability Surveillance",
    "SR 11-7 · Basel III · FCRA — Whole Model Population Stability & Feature Characteristic Tracking",
)

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)
features = models["features"]

# ── Temporal Partitioning: Development Baseline vs Production Monitoring Vintage ──
if "issue_d" in df.columns:
    df["year"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce").dt.year
    baseline_df = df[df["year"] <= 2016].copy()
    actual_df = df[df["year"] >= 2017].copy()
    if len(actual_df) < 100 or len(baseline_df) < 100:
        split_idx = int(len(df) * 0.7)
        baseline_df = df.iloc[:split_idx].copy()
        actual_df = df.iloc[split_idx:].copy()
else:
    split_idx = int(len(df) * 0.7)
    baseline_df = df.iloc[:split_idx].copy()
    actual_df = df.iloc[split_idx:].copy()

# ── 1. Whole Model Population Stability Index (PSI) ──────────────────────────
base_preds = models["predict_scorecard"](baseline_df)
actual_preds = models["predict_scorecard"](actual_df)

model_psi_res = calculate_array_psi(base_preds, actual_preds, num_bins=10)
whole_model_psi = float(model_psi_res["psi_value"])
model_psi_status = str(model_psi_res["status"])

# ── 2. Characteristic Stability Index (CSI) for All Individual Features ──────
csi_table = build_portfolio_csi_report(baseline_df, actual_df, features)
max_csi = float(csi_table["csi_value"].max()) if not csi_table.empty else 0.0
worst_feat_row = csi_table.iloc[0] if not csi_table.empty else None
worst_feat_name = worst_feat_row["feature_name"] if worst_feat_row is not None else "N/A"

# ── 3. Multi-Criterion SR 11-7 Governance Retraining Evaluation ──────────────
retrain_res = evaluate_retraining_triggers(
    psi_value=whole_model_psi,
    current_auc=0.7245,
    baseline_auc=0.7285,
    current_ks_pct=34.82,
    max_feature_csi=max_csi,
)

# ── Executive Governance Banner ───────────────────────────────────────────────
render_traffic_light_header(
    status=retrain_res["traffic_light_status"],
    message=retrain_res["governance_action"],
)

# ── KPI Cards Row ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    psi_icon = "🟢" if whole_model_psi < 0.10 else ("🟡" if whole_model_psi < 0.25 else "🔴")
    render_kpi_card(
        "Whole Model PSI",
        f"{whole_model_psi:.4f}",
        delta=f"{model_psi_status.split()[0]} (<0.10 Target)",
        is_positive_good=whole_model_psi < 0.10,
        icon=psi_icon,
    )
with c2:
    base_mean_pd = float(np.mean(base_preds))
    render_kpi_card(
        "Baseline Mean PD",
        f"{base_mean_pd:.2%}",
        delta=f"{len(baseline_df):,} Dev Loans",
        is_positive_good=True,
        icon="📊",
    )
with c3:
    act_mean_pd = float(np.mean(actual_preds))
    pd_shift = act_mean_pd - base_mean_pd
    render_kpi_card(
        "Current Period Mean PD",
        f"{act_mean_pd:.2%}",
        delta=f"{pd_shift:+.2%} vs Baseline",
        is_positive_good=pd_shift <= 0,
        icon="📈",
    )
with c4:
    csi_icon = "🟢" if max_csi < 0.10 else ("🟡" if max_csi < 0.25 else "🔴")
    render_kpi_card(
        "Max Feature CSI",
        f"{max_csi:.4f}",
        delta=f"Top: {worst_feat_name}",
        is_positive_good=max_csi < 0.10,
        icon=csi_icon,
    )

section_divider()

# ── SECTION 1: Whole Model Population Stability (PSI) ─────────────────────────
label("1. Whole Model Population Stability (PSI)")
st.markdown(
    """
    **Regulatory Mandate (OCC 2011-12 / Federal Reserve SR 11-7):**  
    Whole Model PSI evaluates the aggregate stability of the model's output distribution (predicted default probabilities)
    between the developmental baseline vintage ($E$, Expected) and the recent operational monitoring vintage ($A$, Actual):
    $$\\text{PSI} = \\sum_{b=1}^{10} \\left(\\%\\text{Actual}_b - \\%\\text{Expected}_b\\right) \\times \\ln\\left(\\frac{\\%\\text{Actual}_b}{\\%\\text{Expected}_b}\\right)$$
    - **Green ($\\text{PSI} < 0.10$):** Stable population. No material shift in borrower creditworthiness. Model remains fully authorized.
    - **Yellow ($0.10 \\le \\text{PSI} < 0.25$):** Moderate population drift. Heightened monitoring frequency and sensitivity review required.
    - **Red ($\\text{PSI} \\ge 0.25$):** Significant distributional shift. Model recalibration or full retraining is mandatory.
    """
)

fig_model_dist = create_model_psi_distribution_chart(base_preds, actual_preds)
st.plotly_chart(fig_model_dist, use_container_width=True)

section_divider()

# ── SECTION 2: Characteristic Stability Index (CSI) for All Features ──────────
label("2. Characteristic Stability Index (CSI) — All Candidate Features")
st.markdown(
    f"""
    **Feature-Level Distribution Shift Audit:**  
    CSI quantifies drift for all **{len(features)} individual model risk drivers** (both numerical metrics and categorical attributes).
    A stable whole model PSI can occasionally mask compensating feature shifts (e.g., higher borrower debt offset by higher annual incomes).
    Monitoring individual CSI guarantees early detection of structural market drift.
    """
)

col_chart, col_tbl = st.columns([1, 1], gap="large")

with col_chart:
    st.markdown("##### 📊 Top 10 Most Drifted Features")
    fig_csi = create_csi_ranking_chart(csi_table, top_n=10)
    st.plotly_chart(fig_csi, use_container_width=True)

with col_tbl:
    st.markdown(f"##### 📋 Full Feature CSI Surveillance Registry ({len(csi_table)} Features)")
    styled_csi_df = csi_table.rename(columns={
        "feature_name": "Risk Driver",
        "feature_type": "Data Type",
        "csi_value": "CSI (Drift)",
        "status": "Regulatory Status",
        "drift_level": "Drift Severity",
    })
    render_styled_table(styled_csi_df)
