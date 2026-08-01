"""Page 2: Portfolio Analytics."""

import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.data_loader import load_credit_data
from components.sidebar import render_sidebar_filters
from components.charts import create_vintage_seasoning_chart
from components.tables import render_styled_table, render_download_button
from portfolio.vintage import build_vintage_summary
from portfolio.cohort import build_cohort_performance_matrix
from portfolio.segmentation import compute_geographic_concentration, analyze_recoveries

st.set_page_config(page_title="Portfolio Analytics", page_icon="📈", layout="wide")

st.title("📈 Enterprise Portfolio Risk Analytics")

# Load Data & Apply Sidebar Filters
df = load_credit_data(sample_size=50000)
filtered_df = render_sidebar_filters(df)

# Vintage Seasoning Analysis
st.markdown("### 🗓️ Origination Vintage Seasoning Trend")
vintage_df = build_vintage_summary(filtered_df, issue_date_col="issue_d", loan_amt_col="loan_amnt", target_col="target")
fig_vintage = create_vintage_seasoning_chart(vintage_df)
st.plotly_chart(fig_vintage, use_container_width=True)

st.markdown("---")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 📊 Grade Cohort Performance Matrix")
    cohort_df = build_cohort_performance_matrix(filtered_df, cohort_col="grade", target_col="target")
    render_styled_table(cohort_df)
    render_download_button(cohort_df, "grade_cohort_matrix.csv", "📥 Download Cohort Data")

with col_b:
    st.markdown("### 🗺️ Geographic Concentration Risk (HHI Index)")
    geo_res = compute_geographic_concentration(filtered_df, state_col="addr_state", loan_amt_col="loan_amnt", target_col="target")
    st.info(f"**Herfindahl-Hirschman Index (HHI)**: `{geo_res['hhi_index']}` — *{geo_res['hhi_rating']}*")
    render_styled_table(geo_res["concentration_table"].head(8))

st.markdown("---")

# Recovery Analysis
st.markdown("### 💰 Post-Default Recovery & LGD Analysis")
rec_res = analyze_recoveries(filtered_df, recoveries_col="recoveries", funded_col="funded_amnt", status_col="loan_status")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Charged-Off Loans", f"{rec_res['charged_off_loans_count']:,}")
with c2:
    st.metric("Defaulted Principal Exposure", f"${rec_res['total_charged_off_principal']:,.2f}")
with c3:
    st.metric("Mean Recovery Rate", f"{rec_res['mean_recovery_rate_pct']:.2f}%")
with c4:
    st.metric("Implied Loss Given Default (LGD)", f"{rec_res['implied_lgd_pct']:.2f}%")
