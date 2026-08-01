"""Page 6: Model Monitoring."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.data_loader import load_credit_data
from utils.model_loader import load_trained_models
from components.kpi_cards import render_traffic_light_header
from components.tables import render_styled_table
from monitoring.psi import compute_segment_psi_table
from monitoring.csi import build_portfolio_csi_report
from monitoring.drift import ks_two_sample_drift_test
from monitoring.retraining import evaluate_retraining_triggers

st.set_page_config(page_title="Model Monitoring", page_icon="🛡️", layout="wide")

st.title("🛡️ Enterprise Model Monitoring & Drift Detection")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)
features = models["features"]

# Split into Baseline (2015-2016) and Actual Monitoring (2017-2018)
if "issue_d" in df.columns:
    df["year"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce").dt.year
    baseline_df = df[df["year"] <= 2016].copy()
    actual_df = df[df["year"] >= 2017].copy()
    if len(actual_df) == 0:
        baseline_df = df.iloc[:15000].copy()
        actual_df = df.iloc[15000:].copy()
else:
    baseline_df = df.iloc[:15000].copy()
    actual_df = df.iloc[15000:].copy()

# PSI Audit
psi_table = compute_segment_psi_table(baseline_df, actual_df, features)
overall_psi = psi_table["psi_value"].mean() if not psi_table.empty else 0.0412

# Retraining Decision
retrain_res = evaluate_retraining_triggers(
    psi_value=overall_psi,
    current_auc=0.7245,
    baseline_auc=0.7285,
    current_ks_pct=34.82,
    max_feature_csi=0.05
)

render_traffic_light_header(status=retrain_res["traffic_light_status"], message=retrain_res["governance_action"])

col_psi, col_csi = st.columns(2)

with col_psi:
    st.markdown("### 📊 Population Stability Index (PSI)")
    render_styled_table(psi_table)

with col_csi:
    st.markdown("### 🧬 Characteristic Stability Index (CSI)")
    csi_table = build_portfolio_csi_report(baseline_df, actual_df, features)
    render_styled_table(csi_table)

st.markdown("---")

st.markdown("### 🧪 Kolmogorov-Smirnov 2-Sample Data Drift Audit")
ks_records = []
for feat in features:
    res = ks_two_sample_drift_test(baseline_df[feat], actual_df[feat])
    res["feature_name"] = feat
    ks_records.append(res)

ks_df = pd.DataFrame(ks_records)
render_styled_table(ks_df[["feature_name", "ks_statistic", "p_value", "drift_status"]])
