"""Page 02: Model Performance & Discrimination."""

import sys
from pathlib import Path
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
    from components.charts import create_roc_curve_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_roc_curve_chart
    from dashboard.components.tables import render_styled_table

from validation.model_metrics import evaluate_binary_model

st.set_page_config(page_title="Model Performance", page_icon="🎯", layout="wide")

st.title("🎯 Model Performance & Discrimination Engine")
st.caption("Enterprise Credit Risk Analytics & Model Risk Governance Platform (SR 11-7 / Basel III)")
st.markdown("---")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)

sc_preds = models["predict_scorecard"](df)
lgb_preds = models["predict_lgb"](df)
y_true = df["target"].values

sc_m = evaluate_binary_model(y_true, sc_preds)
lgb_m = evaluate_binary_model(y_true, lgb_preds)

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_kpi_card("Champion ROC-AUC", f"{sc_m['roc_auc']:.4f}")
with col2:
    render_kpi_card("Challenger ROC-AUC", f"{lgb_m['roc_auc']:.4f}")
with col3:
    render_kpi_card("Champion KS Statistic", f"{sc_m['ks_statistic_pct']:.2f}%")
with col4:
    render_kpi_card("Challenger KS Statistic", f"{lgb_m['ks_statistic_pct']:.2f}%")

st.markdown("---")

col_roc, col_table = st.columns([1.5, 1])

with col_roc:
    st.markdown("### 📉 Receiver Operating Characteristic (ROC) Curves")
    fig_roc = create_roc_curve_chart(y_true, sc_preds, lgb_preds)
    st.plotly_chart(fig_roc, use_container_width=True)

with col_table:
    st.markdown("### 📋 Model Comparison Summary")
    comparison_df = pd.DataFrame([
        {
            "Model Name": "Champion Scorecard (Logistic)",
            "ROC-AUC": f"{sc_m['roc_auc']:.4f}",
            "Gini": f"{sc_m['gini_index']:.4f}",
            "KS (%)": f"{sc_m['ks_statistic_pct']:.2f}%",
            "Brier Score": f"{sc_m['brier_score']:.5f}",
        },
        {
            "Model Name": "Challenger LightGBM",
            "ROC-AUC": f"{lgb_m['roc_auc']:.4f}",
            "Gini": f"{lgb_m['gini_index']:.4f}",
            "KS (%)": f"{lgb_m['ks_statistic_pct']:.2f}%",
            "Brier Score": f"{lgb_m['brier_score']:.5f}",
        },
    ])
    render_styled_table(comparison_df)

st.markdown("---")
st.markdown("### 🎛️ Interactive Decision Cutoff Threshold Simulator")

cutoff = st.slider("Select Underwriting Decision Cutoff (Probability of Default)", min_value=0.05, max_value=0.50, value=0.20, step=0.01)

approved_mask = lgb_preds <= cutoff
approval_rate = approved_mask.mean() * 100
bad_rate_approved = (y_true[approved_mask].mean() * 100) if approved_mask.sum() > 0 else 0.0

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    render_kpi_card("Decision Cutoff Threshold", f"{cutoff:.2%}")
with col_c2:
    render_kpi_card("Simulated Approval Rate", f"{approval_rate:.2f}%")
with col_c3:
    render_kpi_card("Approved Portfolio Bad Rate", f"{bad_rate_approved:.2f}%", is_positive_good=False)
