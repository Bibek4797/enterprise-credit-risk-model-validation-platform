"""Page 03: Explainable AI & FCRA Adverse Action Engine."""

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
    from components.charts import create_shap_summary_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_shap_summary_chart
    from dashboard.components.tables import render_styled_table

from explainability.adverse_action import generate_adverse_action_reasons

st.set_page_config(page_title="Explainable AI | Credit Risk Platform", page_icon="🔍", layout="wide")

page_header(
    "🔍  Explainable AI (XAI) & FCRA Adverse Action Engine",
    "SR 11-7 · FCRA · ECOA — Transparent Model Decisions",
)

df      = load_credit_data(sample_size=30000)
models  = load_trained_models(df)
features = models["features"]

tab_global, tab_local = st.tabs([
    "🌍  Global TreeSHAP Feature Ranking",
    "👤  Local Borrower FCRA Adverse Action Inspector",
])

# ── Global Tab ────────────────────────────────────────────────
with tab_global:
    label("Global TreeSHAP Feature Importance (Top Risk Drivers)")
    fig_shap = create_shap_summary_chart(df, features)
    st.plotly_chart(fig_shap, use_container_width=True)

# ── Local Tab ─────────────────────────────────────────────────
with tab_local:
    label("Individual Borrower Evaluation")
    borrower_idx = st.number_input(
        "Select Borrower Index for Individual Evaluation",
        min_value=0, max_value=len(df) - 1, value=42, step=1,
    )

    borrower_row = df.iloc[borrower_idx]
    lgb_pred_pd  = float(models["predict_lgb"](df.iloc[[borrower_idx]])[0])

    cb1, cb2, cb3 = st.columns(3)
    with cb1:
        render_kpi_card("FICO Score", f"{int(borrower_row.get('fico_range_low', 700))}", icon="📊")
    with cb2:
        render_kpi_card("DTI Ratio", f"{borrower_row.get('dti', 15.0):.2f}%", icon="⚖️")
    with cb3:
        render_kpi_card("Predicted PD", f"{lgb_pred_pd:.2%}", icon="⚠️", is_positive_good=False)

    section_divider()
    label("FCRA Closed-Form Decline Reason Codes")

    sample_woe_dict = {
        "dti":           0.45,
        "int_rate":      0.38,
        "revol_util":    0.29,
        "annual_inc":   -0.12,
        "fico_range_low": -0.40,
    }

    reasons    = generate_adverse_action_reasons(sample_woe_dict, top_n=4)
    reasons_df = pd.DataFrame(reasons)
    render_styled_table(reasons_df)
