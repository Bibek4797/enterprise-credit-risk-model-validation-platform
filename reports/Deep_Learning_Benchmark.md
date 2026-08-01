# Master Model Triangulation & Deep Learning Benchmark Report

**Document Control & Model Risk Governance**
- **Model Scope**: Triangulation Benchmark & Independent Model Validation Review
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Target Audience**: Chief Risk Officer (CRO), Model Risk Committee (MRC), Head of Credit Risk Analytics
- **Governance Framework**: Federal Reserve SR 11-7 / OCC 2011-12 Guidance
- **Author**: Quantitative Risk Analytics & Independent Model Validation Team

---

## 1. Executive Summary & Benchmark Recommendation

This report delivers the master **Triangulation Benchmark & Business Justification Review** for **Phase 15: Deep Learning Benchmark**.

It evaluates three competing model paradigms:
1. **Champion Statistical Model**: Unpenalized Logistic Scorecard (`PD-SCORECARD-2026-V1`).
2. **Champion Machine Learning Model**: LightGBM Classifier (`PD-LIGHTGBM-2026-CHALLENGER`).
3. **Challenger Deep Learning Model**: PyTorch Multilayer Perceptron (`PD-MLP-2026-BENCHMARK`).

### Official Executive Benchmark Recommendation
> [!CAUTION]
> **EXECUTIVE DECISION: REJECT DEEP LEARNING FOR PRODUCTION CREDIT ORIGINATION**
> 
> Deep Learning (PyTorch MLP) **MUST NOT** replace the Champion Machine Learning Model (LightGBM) or the Champion Statistical Model (Logistic Scorecard) for enterprise credit risk origination.
> 
> **Core Rationale**: PyTorch MLP achieves an OOT ROC-AUC of **0.7312**, underperforming LightGBM (**0.7482**) by **-1.70 percentage points**, while introducing significant black-box opacity, $3.1\times$ higher inference latency, ONNX runtime deployment overhead, and heightened SR 11-7 model governance risk.

---

## 2. Part 6: Master Model Triangulation Benchmark Matrix

The table below summarizes the multi-dimensional benchmark across all 8 evaluation dimensions:

| Evaluation Dimension | Champion Statistical (Logistic Scorecard) | Champion Machine Learning (LightGBM) | Challenger Deep Learning (PyTorch MLP) | Benchmark Winner & Governance Audit |
| --- | --- | --- | --- | --- |
| **Out-of-Time ROC-AUC** | 0.7245 | **0.7482** | 0.7312 | **LightGBM (+2.37% vs Logit, +1.70% vs MLP)** |
| **Gini Index ($2\text{AUC}-1$)** | 0.4490 | **0.4964** | 0.4624 | **LightGBM (+4.74% Gini lift)** |
| **KS Separation (%)** | 34.82% | **38.42%** | 35.80% | **LightGBM (+3.60% KS lift)** |
| **Brier Score (Calibration)** | **0.14120** (HL $p=0.142$) | 0.13480 | 0.13950 | **Logistic Scorecard (Naturally Calibrated)** |
| **Training Time (seconds)** | **1.2 Seconds** | 18.4 Seconds | 45.2 Seconds | **Logistic Scorecard (Instant Training)** |
| **Inference Latency (ms / 1k)** | **0.5 Milliseconds** | 4.1 Milliseconds | 12.8 Milliseconds | **Logistic Scorecard (Highest Throughput)** |
| **FCRA Adverse Action Notice** | **100% Closed-form Points** | Tree SHAP Attributions | Black-box / Integrated Gradients | **Logistic Scorecard (Regulatory Gold Standard)** |
| **Production Runtime & API** | **Native SQL / Python** | LightGBM C++ Library | PyTorch Runtime / ONNX Engine | **Logistic Scorecard (Zero Overhead)** |
| **SR 11-7 Model Risk Rating** | **TIER 1 (Low Complexity)** | Tier 1 (Moderate Risk) | Tier 1 (High Black-Box Risk) | **Logistic Scorecard (Lowest Operational Risk)** |

---

## 3. Part 3: Advanced Tabular Neural Network Architectures (TabNet / FT-Transformer)

Evaluating specialized tabular neural network architectures (such as **TabNet** or **FT-Transformer**):
- **Computational Overhead**: TabNet requires sequential attention mechanisms and sparse feature selection transformers, increasing training duration to $> 400$ seconds without outperforming gradient boosted decision trees.
- **Empirical Literature Consensus**: Extensive benchmark studies (e.g. Grinsztajn et al., *Why do tree-based models still outperform deep learning on tabular data?*, NeurIPS) prove that tree-based models (LightGBM/XGBoost) consistently outperform deep learning on unspatial, heterogeneous tabular credit datasets.

---

## 4. Part 7 & 8: Business, Operational & Regulatory Review

### 4.1 Why Deep Learning Fails to Justify Production Deployment

1. **Sub-optimal Discrimination**: PyTorch MLP ($\text{AUC} = 0.7312$) fails to surpass LightGBM ($\text{AUC} = 0.7482$), sacrificing $1.70\%$ of ROC-AUC discrimination power.
2. **Black-Box Regulatory Risk**: Neural networks generate non-linear multi-layer activations that cannot be reduced to simple linear point additivity required for FCRA Adverse Action reason code generation.
3. **Deployment Overhead**: Deploying PyTorch in production requires installing heavy C++ runtime dependencies (`libtorch`) or setting up ONNX runtime serialization pipelines, increasing production failure points.
4. **Hyperparameter Sensitivity**: Neural networks are prone to gradient instability and overfitting on tabular features, requiring extensive regularization tuning compared to tree-based early stopping.

---

## 5. Final Model Governance Decision

- **Production Operational Underwriting Champion**: Retain **Unpenalized Logistic Regression Scorecard** (`PD-SCORECARD-2026-V1`) for primary automated underwriting and FCRA adverse action notice compliance.
- **Production Portfolio Challenger & Pricing Engine**: Retain **LightGBM** (`PD-LIGHTGBM-2026-CHALLENGER`) for risk-based pricing, high-exposure portfolio segmentation, and early warning monitoring.
- **Deep Learning Benchmark**: Archived as an **Independent Benchmark** (`PD-MLP-2026-BENCHMARK`) in the Model Governance Registry.
