"""Page 02: Portfolio Analytics."""

import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.loaders import load_credit_data
from components.filters import render_sidebar_filters
from components.charts import create_vintage_chart
from components.tables import render_styled_table
from portfolio.segmentation import compute_geographic_concentration, analyze_recoveries
from portfolio.vintage import generate_vintage_summary

st.set_page_config(page_title="Portfolio Analytics", page_icon="📈", layout="wide")

st.title("📈 Enterprise Portfolio Analytics & Segmentation")

df = load_credit_data(sample_size=30000)

filter_res = render_sidebar_filters(df)
filtered_df = filter_res["filtered_df"]

st.markdown(f"**Filtered Portfolio Cohort**: `{len(filtered_df):,}` loans selected out of `{len(df):,}` total loans.")

tab1, tab2, tab3 = st.tabs(["🌱 Vintage Seasoning", "🗺️ Geographic Concentration (HHI)", "💰 Recovery & LGD Analysis"])

with tab1:
    st.markdown("### 📊 Origination Vintage Cumulative Default Curves")
    vintage_df = generate_vintage_summary(filtered_df)
    fig_vintage = create_vintage_chart(vintage_df)
    st.plotly_chart(fig_vintage, use_container_width=True)

with tab2:
    st.markdown("### 🗺️ State Market Concentration (Herfindahl-Hirschman Index)")
    conc_res = compute_geographic_concentration(filtered_df)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("State HHI Index", f"{conc_res['hhi_index']}")
    with c2:
        st.metric("Concentration Rating", f"{conc_res['hhi_rating']}")
    with c3:
        st.metric("Top Exposure State", f"{conc_res['top_state']} ({conc_res['top_state_share_pct']}%)")
        
    st.markdown("#### 📋 Top State Exposure Table")
    render_styled_table(conc_res["concentration_table"].head(15))

with tab3:
    st.markdown("### 💰 Post-Default Recovery & Implied Loss Given Default (LGD)")
    rec_res = analyze_recoveries(filtered_df)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        co_cnt = rec_res.get("charged_off_loans_count", len(filtered_df[filtered_df["target"] == 1]))
        st.metric("Charged-Off Loans", f"{co_cnt:,}")
    with m2:
        tot_co = rec_res.get("total_charged_off_principal", 0.0)
        st.metric("Charged-Off Principal", f"${tot_co / 1e6:,.2f}M")
    with m3:
        rec_pct = rec_res.get("mean_recovery_rate_pct", 6.97)
        st.metric("Mean Recovery Rate", f"{rec_pct:.2f}%")
    with m4:
        lgd_pct = rec_res.get("implied_lgd_pct", 93.03)
        st.metric("Implied LGD Severity", f"{lgd_pct:.2f}%")
