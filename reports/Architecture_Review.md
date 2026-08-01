# Enterprise Architecture Review & Design Patterns Report

**Document Control & Software Engineering**
- **System Scope**: Credit Risk Analytics & Independent Model Validation Repository Architecture
- **Version**: 1.0.0 (Production Release)
- **Target Audience**: Lead Software Architects, Model Risk Governance, Senior Engineers
- **Author**: Quantitative Software Engineering & Architecture Team

---

## 1. Executive Summary & Design Principles

This report documents the architectural design principles, modularity improvements, design patterns, and code structure of the **Credit Risk Analytics & Independent Model Validation System**.

The repository has been engineered to transition from research notebooks into an institutional enterprise software platform meeting Tier-1 investment banking standards.

---

## 2. Modular Repository Layout

```
c:\Users\BIBEK\OneDrive\Desktop\Credit-Risk-Modelling\
├── src/                          # Core Domain Logic & Production Modules
│   ├── features/                 # WoE/IV, Correlation, RFECV & Stability
│   ├── models/                   # Scorecard, Probit, LightGBM, PyTorch & Packaging
│   ├── validation/               # Model Metrics, Bootstrap CIs, Fair Lending ECOA
│   ├── explainability/           # TreeExplainer SHAP, PDP, ICE, ALE & Counterfactuals
│   ├── portfolio/                # Vintage Curves, Cohorts, Roll Rates & HHI Concentration
│   ├── stress_testing/           # Scenario Generator, Elasticity & Stress Engine
│   ├── monitoring/               # PSI, CSI, Data Drift & Automated Retraining Triggers
│   ├── deep_learning/            # PyTorch MLP Architecture, Training & Benchmark
│   └── utils/                    # Enterprise Logger & Global Seed Control
├── configs/                      # Centralized YAML Configuration Files
├── dashboard/                    # Multi-Page Streamlit Production Application
├── tests/                        # Pytest Automated Unit & Integration Suite
├── logs/                         # Rotating Application & Model Inference Logs
├── models/                       # Versioned Joblib Model Artifacts & JSON Metadata
├── reports/                      # Banking-Grade Audit Reports & Governance Docs
├── Dockerfile                    # Multi-Stage Production Container Specification
├── docker-compose.yml            # Container Orchestration Specification
├── pyproject.toml                # Package Dependencies & Tooling Configs
└── .github/workflows/ci.yml      # Automated GitHub Actions CI Pipeline
```

---

## 3. Key Design Patterns Implemented

1. **Strategy Pattern (Model Inference Interfaces)**: Standardized prediction wrappers across Logistic Scorecard (`predict_scorecard`), LightGBM (`predict_lgb`), and PyTorch MLP (`predict_mlp`).
2. **Factory & Builder Patterns (Scenario & Pipeline Generators)**: Decoupled scenario creation (`apply_borrower_scenario`, `apply_macro_scenario`) from execution engines.
3. **Singleton Pattern (Logger & Seed Controller)**: Centralized `setup_logger()` and `set_global_seed(42)` guaranteeing uniform logging and deterministic reproducibility across threads.
4. **Metadata Header Pattern (Model Packaging)**: Pairs binary `.joblib` model weights with human-readable `.json` metadata headers (`models/champion_scorecard_v1_metadata.json`).
