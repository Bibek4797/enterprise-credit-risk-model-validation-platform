"""Page 03: Explainable AI & FCRA Compliance."""

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
    from components.charts import create_shap_summary_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_shap_summary_chart
    from dashboard.components.tables import render_styled_table

from explainability.adverse_action import generate_adverse_action_reasons

st.set_page_config(page_title="Explainable AI", page_icon="🔍", layout="wide")

st.title("🔍 Explainable AI (XAI) & Regulatory FCRA Adverse Action")
st.caption("Enterprise Credit Risk Analytics & Model Risk Governance Platform (SR 11-7 / Basel III)")
st.markdown("---")

df = load_credit_data(sample_size=20000)
models = load_trained_models(df)

st.markdown("### 🌐 Global TreeSHAP Feature Importance Ranking")
fig_shap = create_shap_summary_chart(models.get("shap_summary_df"))
st.plotly_chart(fig_shap, use_container_width=True)

st.markdown("---")
st.markdown("### 📄 FCRA Adverse Action Decline Reason Code Generator")

borrower_idx = st.number_input("Select Borrower Index for Individual Evaluation", min_value=0, max_value=len(df)-1, value=42)

borrower_row = df.iloc[borrower_idx]
lgb_pred_pd = models["predict_lgb"](df.iloc[[borrower_idx]])[0]

col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    render_kpi_card("Borrower FICO Score", f"{int(borrower_row.get('fico_range_low', 700))}")
with col_b2:
    render_kpi_card("Borrower DTI Ratio", f"{borrower_row.get('dti', 15.0):.2f}%")
with col_b3:
    render_kpi_card("Predicted Default Prob (PD)", f"{lgb_pred_pd:.2%}", is_positive_good=False)

st.markdown("#### 📋 FCRA Closed-Form Decline Reason Codes")

sample_woe_dict = {
    "dti": 0.45,
    "int_rate": 0.38,
    "revol_util": 0.29,
    "annual_inc": -0.12,
    "fico_range_low": -0.40,
}

reasons = generate_adverse_action_reasons(sample_woe_dict, top_n=4)
reasons_df = pd.DataFrame(reasons)

render_styled_table(reasons_df)
