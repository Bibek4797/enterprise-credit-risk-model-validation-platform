"""Page 02: Model Performance & Discrimination Engine."""

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
    from utils.ui_helpers import page_header, section_divider, label
    from components.cards import render_kpi_card
    from components.charts import create_roc_curve_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_roc_curve_chart
    from dashboard.components.tables import render_styled_table

from validation.model_metrics import evaluate_binary_model

st.set_page_config(page_title="Model Performance | Credit Risk Platform", page_icon="🎯", layout="wide")

page_header(
    "🎯  Model Performance & Discrimination Engine",
    "SR 11-7 · Basel III IRB — Champion vs Challenger Evaluation",
)

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)

sc_preds  = models["predict_scorecard"](df)
lgb_preds = models["predict_lgb"](df)
y_true    = df["target"].values

sc_m  = evaluate_binary_model(y_true, sc_preds)
lgb_m = evaluate_binary_model(y_true, lgb_preds)

# ── KPI Row ───────────────────────────────────────────────────
label("Model Performance Metrics (Discrimination, Calibration & Pseudo-R²)")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Champion ROC-AUC", f"{sc_m['roc_auc']:.4f}", icon="🏆")
with c2:
    render_kpi_card("Champion KS Stat", f"{sc_m['ks_statistic_pct']:.2f}%", icon="📊")
with c3:
    hl_status = "Calibrated" if sc_m['hl_is_calibrated'] else "Miscalibrated"
    render_kpi_card("Hosmer-Lemeshow p-val", f"{sc_m['hl_p_value']:.4f} ({hl_status})", icon="📐")
with c4:
    render_kpi_card("Champion McFadden R²", f"{sc_m['mcfadden_pseudo_r2']:.4f}", icon="📈")

c5, c6, c7, c8 = st.columns(4)
with c5:
    render_kpi_card("Challenger ROC-AUC", f"{lgb_m['roc_auc']:.4f}", icon="🤖")
with c6:
    render_kpi_card("Challenger KS Stat", f"{lgb_m['ks_statistic_pct']:.2f}%", icon="📊")
with c7:
    chl_status = "Calibrated" if lgb_m['hl_is_calibrated'] else "Miscalibrated"
    render_kpi_card("Challenger H-L p-val", f"{lgb_m['hl_p_value']:.4f} ({chl_status})", icon="📐")
with c8:
    render_kpi_card("Challenger McFadden R²", f"{lgb_m['mcfadden_pseudo_r2']:.4f}", icon="📈")

section_divider()

# ── ROC + Comparison ──────────────────────────────────────────
col_roc, col_table = st.columns([1.6, 1], gap="large")

with col_roc:
    label("Receiver Operating Characteristic (ROC) Curves")
    fig_roc = create_roc_curve_chart(y_true, sc_preds, lgb_preds)
    st.plotly_chart(fig_roc, use_container_width=True)

with col_table:
    label("Model Comparison Summary")
    comparison_df = pd.DataFrame([
        {
            "Model": "Champion Scorecard (Logit)",
            "ROC-AUC": f"{sc_m['roc_auc']:.4f}",
            "KS (%)": f"{sc_m['ks_statistic_pct']:.2f}%",
            "Hosmer-Lemeshow (p-value)": f"{sc_m['hl_p_value']:.4f}",
            "McFadden Pseudo-R²": f"{sc_m['mcfadden_pseudo_r2']:.4f}",
            "Calibration Status": "Calibrated" if sc_m['hl_is_calibrated'] else "Miscalibrated",
        },
        {
            "Model": "Challenger LightGBM",
            "ROC-AUC": f"{lgb_m['roc_auc']:.4f}",
            "KS (%)": f"{lgb_m['ks_statistic_pct']:.2f}%",
            "Hosmer-Lemeshow (p-value)": f"{lgb_m['hl_p_value']:.4f}",
            "McFadden Pseudo-R²": f"{lgb_m['mcfadden_pseudo_r2']:.4f}",
            "Calibration Status": "Calibrated" if lgb_m['hl_is_calibrated'] else "Miscalibrated",
        },
    ])
    render_styled_table(comparison_df)

section_divider()

# ── Cutoff Simulator ──────────────────────────────────────────
label("Interactive Decision Cutoff Threshold Simulator")
cutoff = st.slider(
    "Underwriting Decision Cutoff — Probability of Default",
    min_value=0.05, max_value=0.50, value=0.20, step=0.01,
)

approved_mask      = lgb_preds <= cutoff
approval_rate      = approved_mask.mean() * 100
bad_rate_approved  = (y_true[approved_mask].mean() * 100) if approved_mask.sum() > 0 else 0.0

cc1, cc2, cc3 = st.columns(3)
with cc1:
    render_kpi_card("Decision Cutoff", f"{cutoff:.2%}", icon="🎚️")
with cc2:
    render_kpi_card("Simulated Approval Rate", f"{approval_rate:.2f}%", icon="✅")
with cc3:
    render_kpi_card("Approved Bad Rate", f"{bad_rate_approved:.2f}%", icon="❗", is_positive_good=False)
