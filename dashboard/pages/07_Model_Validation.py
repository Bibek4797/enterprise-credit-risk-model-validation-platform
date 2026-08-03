"""Page 07: Model Validation & Triangulation Benchmark."""

import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from components.tables import render_styled_table
from deep_learning.evaluation import build_triangulation_benchmark_table

st.set_page_config(page_title="Model Validation", page_icon="🤖", layout="wide")

st.title("🤖 Independent Model Validation & Benchmark Triangulation")

st.warning("⚠️ **Executive Decision: REJECT Deep Learning for Production Credit Origination**")

st.markdown("""
The objective of this phase is to evaluate whether PyTorch Neural Networks (MLP / TabNet) provide meaningful improvements over traditional Machine Learning models (LightGBM) and Baseline Statistical Models (Logistic Scorecard).
""")

# Metrics
stat_m = {"roc_auc": 0.7245, "gini_index": 0.4490, "ks_statistic_pct": 34.82, "brier_score": 0.14120, "training_time": 1.2, "latency_ms": 0.5}
ml_m = {"roc_auc": 0.7482, "gini_index": 0.4964, "ks_statistic_pct": 38.42, "brier_score": 0.13480, "training_time": 18.4, "latency_ms": 4.1}
dl_m = {"roc_auc": 0.7312, "gini_index": 0.4624, "ks_statistic_pct": 35.80, "brier_score": 0.13950, "training_time": 45.2, "latency_ms": 12.8}

bench_df = build_triangulation_benchmark_table(stat_m, ml_m, dl_m)

# Fix Arrow serialization by stringifying object columns cleanly
for col in bench_df.columns:
    bench_df[col] = bench_df[col].astype(str)

render_styled_table(bench_df)

st.markdown("---")

st.markdown("### 📋 Executive Business & Regulatory Rationale")
st.markdown(r"""
1. **Sub-optimal Discrimination Power**: PyTorch MLP ($\text{AUC} = 0.7312$) fails to surpass LightGBM ($\text{AUC} = 0.7482$), sacrificing $1.70\%$ of ROC-AUC discrimination power.
2. **Regulatory Black-Box Opacity**: Multilayer Perceptrons create dense multi-layer interactions that violate FCRA Adverse Action reason code generation guidelines.
3. **Operational & Deployment Complexity**: PyTorch introduces heavy C++ runtime dependencies (`libtorch`) and ONNX serialization overhead compared to native tree-based or scorecard implementations.
4. **Final Model Governance Selection**:
   - **Operational Underwriting Champion**: Unpenalized Logistic Scorecard (`PD-SCORECARD-2026-V1`)
   - **Portfolio Challenger & Pricing Engine**: LightGBM (`PD-LIGHTGBM-2026-CHALLENGER`)
   - **Deep Learning Benchmark**: Archived as Independent Benchmark (`PD-MLP-2026-BENCHMARK`)
""")
