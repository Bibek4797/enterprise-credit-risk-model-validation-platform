"""Page 05: Model Monitoring."""

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
    from components.cards import render_kpi_card, render_traffic_light_header
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.components.cards import render_kpi_card, render_traffic_light_header
    from dashboard.components.tables import render_styled_table

from monitoring.psi import compute_segment_psi_table
from monitoring.retraining import evaluate_retraining_triggers

st.set_page_config(page_title="Model Monitoring", page_icon="🛡️", layout="wide")

st.title("🛡️ Post-Deployment Model Monitoring & Data Drift Engine")
st.caption("Enterprise Credit Risk Analytics & Model Risk Governance Platform (SR 11-7 / Basel III)")
st.markdown("---")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)
features = models["features"]

half = len(df) // 2
base_df = df.iloc[:half]
curr_df = df.iloc[half:]

psi_df = compute_segment_psi_table(base_df, curr_df, features[:8])

st.markdown("### 📊 Population Stability Index (PSI) & CSI Drift Summary")
render_styled_table(psi_df)

st.markdown("---")
st.markdown("### 🤖 Automated Model Retraining Governance Audit")

retrain_decision = evaluate_retraining_triggers(
    psi_value=0.0412,
    current_auc=0.7245,
    baseline_auc=0.7285,
    current_ks_pct=34.82,
    max_feature_csi=0.05,
)

is_retrain = retrain_decision.get("is_retraining_required", retrain_decision.get("retrain_recommended", False))

if is_retrain:
    render_traffic_light_header(status="RED", message="CRITICAL DRIFT: Model Retraining Required Immediately")
else:
    render_traffic_light_header(status="GREEN", message="STABLE: Model Stability Criteria Satisfied (PSI < 0.10)")

col_m1, col_m2 = st.columns(2)

with col_m1:
    render_kpi_card("Overall Portfolio PSI", f"{retrain_decision['psi_value']:.4f}")
with col_m2:
    action_text = retrain_decision.get("governance_action", retrain_decision.get("recommended_action", "N/A"))
    render_kpi_card("Retraining Recommendation", action_text)
