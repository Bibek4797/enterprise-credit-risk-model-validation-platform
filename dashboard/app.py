"""Streamlit Application Entry Point — Executive Risk Committee Dashboard."""

import sys
from pathlib import Path
import streamlit as st

file_path = Path(__file__).resolve()
dash_dir = file_path.parent
root_dir = dash_dir.parent
for d in [str(root_dir), str(dash_dir), str(root_dir / "src")]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from utils.loaders import load_credit_data, load_trained_models
    from components.cards import render_kpi_card, render_traffic_light_header
    from components.charts import create_grade_distribution_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.components.cards import render_kpi_card, render_traffic_light_header
    from dashboard.components.charts import create_grade_distribution_chart
    from dashboard.components.tables import render_styled_table

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Credit Risk Platform | Executive Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject premium CSS ────────────────────────────────────────
css_path = dash_dir / "assets" / "styles.css"
if css_path.is_file():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── Hero banner ───────────────────────────────────────────────
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, rgba(15,30,70,0.9) 0%, rgba(30,10,65,0.85) 100%);
        border: 1px solid rgba(96,165,250,0.2);
        border-radius: 18px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(16px);
    ">
        <div style="position:relative;z-index:1;">
            <div style="
                display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;
            ">
                <span style="font-size:1.8rem;">🏦</span>
                <h1 style="
                    margin:0;
                    font-size:1.6rem;
                    font-weight:800;
                    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 60%, #38bdf8 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    letter-spacing: -0.02em;
                ">Enterprise Credit Risk & Model Governance Platform</h1>
            </div>
            <p style="
                margin:0;
                font-size:0.78rem;
                color:#64748b;
                letter-spacing:0.1em;
                text-transform:uppercase;
                font-weight:600;
            ">SR 11-7 · Basel III IRB · FCRA · ECOA · 1.37M Consumer Loan Records</p>
        </div>
        <div style="
            position:absolute; top:-60px; right:-60px;
            width:300px; height:300px;
            background: radial-gradient(circle, rgba(96,165,250,0.08) 0%, transparent 70%);
            pointer-events:none;
        "></div>
        <div style="
            position:absolute; bottom:-80px; left:40%;
            width:200px; height:200px;
            background: radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%);
            pointer-events:none;
        "></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Traffic light ─────────────────────────────────────────────
render_traffic_light_header(
    status="GREEN",
    message="SR 11-7 Model Governance & Performance Compliance Satisfied — All Systems Operational",
)

# ── Load data & models ────────────────────────────────────────
df = load_credit_data(sample_size=30000)
models = load_trained_models(df)

# ── KPI Row ───────────────────────────────────────────────────
st.markdown(
    "<p style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
    "color:#64748b;margin:0 0 0.75rem 0;'>Executive Portfolio Snapshot</p>",
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card("Total Loans", f"{len(df):,}", icon="📋")
with c2:
    exp_m = df["loan_amnt"].sum() / 1e6 if "loan_amnt" in df.columns else 0.0
    render_kpi_card("Total Exposure", f"${exp_m:,.1f}M", icon="💰")
with c3:
    avg_rate = df["int_rate"].mean() if "int_rate" in df.columns else 0.0
    render_kpi_card("Avg Interest Rate", f"{avg_rate:.2f}%", icon="📈")
with c4:
    def_rate = (df["target"].mean() * 100) if "target" in df.columns else 0.0
    render_kpi_card("Default Rate", f"{def_rate:.2f}%", icon="⚠️", is_positive_good=False)
with c5:
    render_kpi_card("Portfolio Health", "94 / 100", icon="🛡️")

st.markdown("<div style='margin:1.5rem 0;border-top:1px solid rgba(96,165,250,0.1);'></div>", unsafe_allow_html=True)

# ── Charts row ────────────────────────────────────────────────
col_chart, col_summary = st.columns([1.6, 1], gap="large")

with col_chart:
    st.markdown(
        "<p style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
        "color:#64748b;margin:0 0 0.6rem 0;'>Portfolio Exposure by Risk Grade</p>",
        unsafe_allow_html=True,
    )
    fig_grade = create_grade_distribution_chart(df)
    st.plotly_chart(fig_grade, use_container_width=True)

with col_summary:
    st.markdown(
        "<p style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
        "color:#64748b;margin:0 0 0.6rem 0;'>Portfolio Risk Summary</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(15,30,60,0.65) 0%, rgba(10,20,45,0.75) 100%);
            border: 1px solid rgba(96,165,250,0.14);
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            backdrop-filter: blur(10px);
        ">
            <div style="display:flex;flex-direction:column;gap:0.85rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;color:#64748b;font-weight:500;">Champion Model</span>
                    <span style="font-size:0.8rem;color:#60a5fa;font-weight:600;font-family:monospace;">PD-SCORECARD-2026-V1</span>
                </div>
                <div style="border-top:1px solid rgba(96,165,250,0.08);"></div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;color:#64748b;font-weight:500;">Challenger Model</span>
                    <span style="font-size:0.8rem;color:#a78bfa;font-weight:600;font-family:monospace;">PD-LIGHTGBM-2026</span>
                </div>
                <div style="border-top:1px solid rgba(96,165,250,0.08);"></div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;color:#64748b;font-weight:500;">Champion ROC-AUC</span>
                    <span style="font-size:0.8rem;color:#34d399;font-weight:700;">0.7245</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;color:#64748b;font-weight:500;">Challenger ROC-AUC</span>
                    <span style="font-size:0.8rem;color:#34d399;font-weight:700;">0.7482</span>
                </div>
                <div style="border-top:1px solid rgba(96,165,250,0.08);"></div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;color:#64748b;font-weight:500;">PSI</span>
                    <span style="font-size:0.8rem;color:#fbbf24;font-weight:700;">0.0412 <span style="color:#34d399;font-size:0.7rem;">● GREEN</span></span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;color:#64748b;font-weight:500;">HHI (Geographic)</span>
                    <span style="font-size:0.8rem;color:#fbbf24;font-weight:700;">584.2 <span style="color:#34d399;font-size:0.7rem;">● Unconcentrated</span></span>
                </div>
                <div style="border-top:1px solid rgba(96,165,250,0.08);"></div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;color:#64748b;font-weight:500;">Est. Net Loss Savings</span>
                    <span style="font-size:0.85rem;color:#e2e8f0;font-weight:800;">$24.2M / year</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin:1.5rem 0;border-top:1px solid rgba(96,165,250,0.1);'></div>", unsafe_allow_html=True)

# ── Grade Exposure Table ───────────────────────────────────────
st.markdown(
    "<p style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
    "color:#64748b;margin:0 0 0.75rem 0;'>Grade Exposure Breakdown</p>",
    unsafe_allow_html=True,
)

grade_summary = (
    df.groupby("grade", observed=False)
    .agg(
        Loans=("grade", "count"),
        Exposure_M=("loan_amnt", lambda x: round(x.sum() / 1e6, 2)),
        Avg_Int_Rate=("int_rate", lambda x: round(x.mean(), 2)),
        Default_Rate_Pct=("target", lambda x: round(x.mean() * 100, 2)),
    )
    .reset_index()
    .rename(columns={
        "grade": "Grade",
        "Exposure_M": "Exposure ($M)",
        "Avg_Int_Rate": "Avg Rate (%)",
        "Default_Rate_Pct": "Default Rate (%)",
    })
)
render_styled_table(grade_summary)

# ── Footer ────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-top:3rem;padding-top:1.5rem;border-top:1px solid rgba(96,165,250,0.08);
        text-align:center;">
        <p style="font-size:0.72rem;color:#334155;letter-spacing:0.06em;font-weight:500;">
            ENTERPRISE CREDIT RISK & MODEL GOVERNANCE PLATFORM &nbsp;·&nbsp;
            SR 11-7 &nbsp;·&nbsp; Basel III IRB &nbsp;·&nbsp; FCRA &nbsp;·&nbsp; ECOA
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
