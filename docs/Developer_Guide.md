# Developer Engineering & Architecture Guide

**Document Control & Software Engineering Manual**
- **System Scope**: Developer Architecture, Codebase Design & Testing Framework
- **Target Audience**: Quantitative Software Engineers, Data Engineers, Maintainers
- **Author**: Lead Software Architect

---

## 1. Codebase Architecture & Key Modules

```
c:\Users\BIBEK\OneDrive\Desktop\Credit-Risk-Modelling\
├── src/                          # Core Domain Logic
│   ├── features/                 # WoE/IV, Correlation, RFECV & Stability
│   ├── models/                   # Scorecard, Probit, LightGBM, PyTorch & Packaging
│   ├── validation/               # Model Metrics, Bootstrap CIs, Fair Lending ECOA
│   ├── explainability/           # SHAP, PDP, ICE, ALE & Counterfactuals
│   ├── portfolio/                # Vintage Curves, Cohorts, Roll Rates & HHI
│   ├── stress_testing/           # Scenario Generator, Elasticity & Stress Engine
│   ├── monitoring/               # PSI, CSI, Data Drift & Retraining Triggers
│   ├── deep_learning/            # PyTorch MLP Architecture & Benchmark
│   └── utils/                    # Enterprise Logger & Seed Control
├── configs/                      # Centralized YAML Configurations
├── dashboard/                    # Streamlit Multi-Page Application
└── tests/                        # Pytest Automated Test Suite
```

---

## 2. Development & Testing Workflow

### 2.1 Setting Up Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2.2 Running Automated Test Suite
```bash
python -m pytest tests/
```

### 2.3 Code Formatting & Quality Tools
```bash
ruff check src/ dashboard/
black src/ dashboard/
```
