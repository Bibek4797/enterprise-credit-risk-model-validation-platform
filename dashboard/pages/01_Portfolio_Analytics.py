"""Page 01: Portfolio Analytics."""

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
    from utils.loaders import load_credit_data
    from components.sidebar import render_sidebar_filters
    from components.cards import render_kpi_card
    from components.charts import create_vintage_chart, create_grade_distribution_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data
    from dashboard.components.sidebar import render_sidebar_filters
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_vintage_chart, create_grade_distribution_chart
    from dashboard.components.tables import render_styled_table

from portfolio.segmentation import compute_geographic_concentration, analyze_recoveries

st.set_page_config(page_title="Portfolio Analytics", page_icon="📈", layout="wide")

st.title("📈 Portfolio Analytics & Concentration Engine")
st.caption("Enterprise Credit Risk Analytics & Model Risk Governance Platform (SR 11-7 / Basel III)")
st.markdown("---")

raw_df = load_credit_data(sample_size=40000)
df = render_sidebar_filters(raw_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_kpi_card("Filtered Loans", f"{len(df):,}")
with col2:
    exp_m = df["loan_amnt"].sum() / 1e6 if "loan_amnt" in df.columns else 0.0
    render_kpi_card("Filtered Exposure ($)", f"${exp_m:,.2f}M")
with col3:
    conc_res = compute_geographic_concentration(df)
    render_kpi_card("State HHI Concentration", f"{conc_res['hhi_index']:.1f}")
with col4:
    rec_res = analyze_recoveries(df)
    avg_rec = rec_res.get("avg_recovery_amount", 0.0)
    render_kpi_card("Avg Post-Default Recovery", f"${avg_rec:,.2f}")

st.markdown("---")

col_vint, col_grade = st.columns(2)

with col_vint:
    st.markdown("### 🗓️ Origination Vintage Default Seasoning Curves")
    fig_vint = create_vintage_chart(df)
    st.plotly_chart(fig_vint, use_container_width=True)

with col_grade:
    st.markdown("### 📊 Exposure ($M) by Risk Grade")
    fig_grade = create_grade_distribution_chart(df)
    st.plotly_chart(fig_grade, use_container_width=True)

st.markdown("---")
st.markdown("### 🗺️ Geographic State Exposure Breakdown")

state_summary = (
    df.groupby("addr_state", observed=False)
    .agg(
        loan_count=("addr_state", "count"),
        total_exposure_m=("loan_amnt", lambda x: round(x.sum() / 1e6, 2)),
        observed_default_rate=("target", lambda x: round(x.mean() * 100, 2)),
    )
    .sort_values("total_exposure_m", ascending=False)
    .reset_index()
    .head(15)
)

render_styled_table(state_summary)
