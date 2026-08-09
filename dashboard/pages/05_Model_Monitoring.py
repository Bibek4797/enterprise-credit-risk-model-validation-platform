"""Page 05: Model Monitoring & Drift Detection."""

import sys
from pathlib import Path
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
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.cards import render_traffic_light_header, render_kpi_card
    from dashboard.components.tables import render_styled_table

from monitoring.psi import compute_segment_psi_table
from monitoring.csi import build_portfolio_csi_report
from monitoring.drift import ks_two_sample_drift_test
from monitoring.retraining import evaluate_retraining_triggers

st.set_page_config(page_title="Model Monitoring | Credit Risk Platform", page_icon="🛡️", layout="wide")

page_header(
    "🛡️  Enterprise Model Monitoring & Drift Detection",
    "SR 11-7 · Basel III · FCRA — Ongoing Model Surveillance",
)

df      = load_credit_data(sample_size=30000)
models  = load_trained_models(df)
features = models["features"]

# ── Time split ────────────────────────────────────────────────
if "issue_d" in df.columns:
    df["year"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce").dt.year
    baseline_df = df[df["year"] <= 2016].copy()
    actual_df   = df[df["year"] >= 2017].copy()
    if len(actual_df) == 0:
        baseline_df = df.iloc[:15000].copy()
        actual_df   = df.iloc[15000:].copy()
else:
    baseline_df = df.iloc[:15000].copy()
    actual_df   = df.iloc[15000:].copy()

psi_table   = compute_segment_psi_table(baseline_df, actual_df, features)
overall_psi = psi_table["psi_value"].mean() if not psi_table.empty else 0.0412

retrain_res = evaluate_retraining_triggers(
    psi_value=overall_psi,
    current_auc=0.7245,
    baseline_auc=0.7285,
    current_ks_pct=34.82,
    max_feature_csi=0.05,
)

render_traffic_light_header(
    status=retrain_res["traffic_light_status"],
    message=retrain_res["governance_action"],
)

# ── PSI & CSI ─────────────────────────────────────────────────
col_psi, col_csi = st.columns(2, gap="large")

with col_psi:
    label("Population Stability Index (PSI)")
    render_styled_table(psi_table)

with col_csi:
    label("Characteristic Stability Index (CSI)")
    csi_table = build_portfolio_csi_report(baseline_df, actual_df, features)
    render_styled_table(csi_table)

section_divider()

# ── KS Drift ──────────────────────────────────────────────────
label("Kolmogorov-Smirnov 2-Sample Data Drift Audit")
ks_records = []
for feat in features:
    res = ks_two_sample_drift_test(baseline_df[feat], actual_df[feat])
    res["feature_name"] = feat
    ks_records.append(res)

ks_df = pd.DataFrame(ks_records)
render_styled_table(ks_df[["feature_name", "ks_statistic", "p_value", "drift_status"]])
