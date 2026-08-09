"""Page 06: Independent Model Validation & Benchmark Triangulation."""

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
    from utils.ui_helpers import page_header, section_divider, label
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.tables import render_styled_table

from deep_learning.evaluation import build_triangulation_benchmark_table

st.set_page_config(page_title="Model Validation | Credit Risk Platform", page_icon="🤖", layout="wide")

page_header(
    "🤖  Independent Model Validation & Benchmark Triangulation",
    "SR 11-7 · Basel III IRB — Statistical vs ML vs Deep Learning",
)

# ── Executive Decision Banner ─────────────────────────────────
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, rgba(120,20,20,0.35) 0%, rgba(185,28,28,0.2) 100%);
        border: 1px solid rgba(248,113,113,0.3);
        border-radius: 14px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    ">
        <span style="font-size:1.4rem;">⛔</span>
        <div>
            <span style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                color:#f87171;display:block;margin-bottom:2px;">Executive Decision</span>
            <span style="font-size:0.9rem;font-weight:600;color:#fca5a5;">
                REJECT Deep Learning for Production Credit Origination
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='color:#94a3b8;font-size:0.9rem;line-height:1.7;'>"
    "This phase evaluates whether PyTorch Neural Networks (MLP / TabNet) provide meaningful improvements "
    "over traditional ML models (LightGBM) and Baseline Statistical Models (Logistic Scorecard)."
    "</p>",
    unsafe_allow_html=True,
)

# ── Benchmark Table ───────────────────────────────────────────
stat_m = {"roc_auc": 0.7245, "gini_index": 0.4490, "ks_statistic_pct": 34.82, "brier_score": 0.14120, "training_time": 1.2,  "latency_ms": 0.5}
ml_m   = {"roc_auc": 0.7482, "gini_index": 0.4964, "ks_statistic_pct": 38.42, "brier_score": 0.13480, "training_time": 18.4, "latency_ms": 4.1}
dl_m   = {"roc_auc": 0.7312, "gini_index": 0.4624, "ks_statistic_pct": 35.80, "brier_score": 0.13950, "training_time": 45.2, "latency_ms": 12.8}

bench_df = build_triangulation_benchmark_table(stat_m, ml_m, dl_m)
for col in bench_df.columns:
    bench_df[col] = bench_df[col].astype(str)

label("Three-Way Model Benchmark Triangulation")
render_styled_table(bench_df)

section_divider()

# ── Rationale ─────────────────────────────────────────────────
label("Executive Business & Regulatory Rationale")
st.markdown(
    """
    <div style="
        background: rgba(15,30,60,0.6);
        border: 1px solid rgba(96,165,250,0.12);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        backdrop-filter: blur(8px);
    ">
        <ol style="color:#94a3b8;font-size:0.88rem;line-height:1.9;margin:0;padding-left:1.2rem;">
            <li><strong style="color:#e2e8f0;">Sub-optimal Discrimination:</strong>
                PyTorch MLP (AUC = 0.7312) fails to surpass LightGBM (AUC = 0.7482),
                sacrificing 1.70% of ROC-AUC power.</li>
            <li><strong style="color:#e2e8f0;">Regulatory Black-Box Opacity:</strong>
                MLPs create dense multi-layer interactions violating FCRA Adverse Action
                reason-code generation guidelines.</li>
            <li><strong style="color:#e2e8f0;">Operational Complexity:</strong>
                PyTorch introduces heavy C++ runtime dependencies and ONNX serialization
                overhead vs. native tree-based or scorecard implementations.</li>
            <li><strong style="color:#e2e8f0;">Final Governance Selection:</strong>
                <ul style="margin-top:0.4rem;">
                    <li><code style="color:#60a5fa;background:rgba(59,130,246,0.1);
                        padding:1px 6px;border-radius:4px;">PD-SCORECARD-2026-V1</code>
                        → Operational Underwriting Champion</li>
                    <li><code style="color:#a78bfa;background:rgba(139,92,246,0.1);
                        padding:1px 6px;border-radius:4px;">PD-LIGHTGBM-2026-CHALLENGER</code>
                        → Portfolio Challenger & Pricing Engine</li>
                    <li><code style="color:#64748b;background:rgba(100,116,139,0.1);
                        padding:1px 6px;border-radius:4px;">PD-MLP-2026-BENCHMARK</code>
                        → Archived Independent Benchmark</li>
                </ul>
            </li>
        </ol>
    </div>
    """,
    unsafe_allow_html=True,
)
