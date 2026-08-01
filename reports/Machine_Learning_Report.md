# Enterprise Machine Learning Models Technical Report

**Document Control & Model Risk Governance**
- **Model Scope**: Machine Learning Credit Risk Classifiers & Benchmark Suite
- **Development Sample**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Regulatory Framework**: SR 11-7 / OCC 2011-12, Basel III EBA Guidelines, IFRS 9 ECL
- **Author**: Quantitative Risk Analytics & Independent Model Validation Team

---

## 1. Executive Summary

This report presents the technical development, validation, calibration, robustness testing, and business governance evaluation for **Phase 9: Enterprise Machine Learning Models**.

Six Machine Learning architectures were built using the Phase 7 Machine Learning Dataset (29 continuous, categorical, and interaction risk drivers) and benchmarked against the Phase 8 Champion Logistic Scorecard:
1. **Pruned Decision Tree** (Baseline Non-Linear Model)
2. **Random Forest** (Bagged Ensemble Model)
3. **Extra Trees** (Extremely Randomized Trees Ensemble)
4. **XGBoost** (Extreme Gradient Boosting Model)
5. **LightGBM** (Light Gradient Boosting Machine Model)
6. **CatBoost** (Categorical Gradient Boosting Model)

---

## 2. Comprehensive Model Evaluation & Diagnostic Matrix

Below is the master diagnostic matrix evaluated on the independent **Out-Of-Time (OOT) Test Dataset (2018 Originations)**:

| Model Architecture | OOT ROC-AUC | Gini ($2\text{AUC}-1$) | KS Stat (%) | Brier Score | MCC | Balanced Accuracy | Sensitivity | Specificity | F1-Score | Inference Latency (ms / 1k) | Seed Stability (Std AUC) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Logistic Scorecard (Statistical Champion)** | 0.7245 | 0.4490 | 34.82% | 0.14120 | 0.3125 | 0.6726 | 0.6840 | 0.6612 | 0.4735 | **0.8 ms** | **0.00000** |
| **Decision Tree (Pruned)** | 0.6985 | 0.3970 | 30.12% | 0.14850 | 0.2740 | 0.6420 | 0.6280 | 0.6560 | 0.4320 | **1.2 ms** | 0.00012 |
| **Random Forest** | 0.7385 | 0.4770 | 36.85% | 0.13840 | 0.3340 | 0.6880 | 0.6980 | 0.6780 | 0.4910 | 18.5 ms | 0.00045 |
| **Extra Trees** | 0.7352 | 0.4704 | 36.20% | 0.13910 | 0.3280 | 0.6840 | 0.6920 | 0.6760 | 0.4850 | 14.2 ms | 0.00052 |
| **XGBoost** | 0.7476 | 0.4952 | 38.15% | 0.13520 | 0.3510 | 0.7010 | 0.7120 | 0.6900 | 0.5120 | 8.4 ms | 0.00038 |
| **LightGBM (ML Champion)** | **0.7482** | **0.4964** | **38.42%** | **0.13480** | **0.3540** | **0.7025** | **0.7140** | **0.6910** | **0.5145** | **4.1 ms** | **0.00028** |
| **CatBoost** | 0.7468 | 0.4936 | 38.05% | 0.13550 | 0.3490 | 0.7000 | 0.7100 | 0.6900 | 0.5100 | 12.8 ms | 0.00031 |

---

## 3. Individual Model Analyses & Governance Summaries

### 3.1 Baseline Decision Tree
- **Depth & Pruning**: Pruned at `max_depth = 6` with `min_samples_leaf = 50`.
- **Top Risk Drivers**: `sub_grade`, `int_rate`, `fe_fico_midpoint`.
- **Finding**: Underperforms Logistic Regression ($\text{AUC} = 0.6985$ vs $0.7245$) due to step-wise step-function approximation of continuous risk curves.

### 3.2 Random Forest & Extra Trees
- **OOB Score**: Random Forest achieved an Out-of-Bag (OOB) accuracy of **78.85%**.
- **Performance**: Provides +1.40% ROC-AUC lift over Logistic Regression ($\text{AUC} = 0.7385$ vs $0.7245$).
- **Inference Speed**: Higher latency (18.5 ms per 1k) due to evaluating 150 deep decision trees.

### 3.3 Gradient Boosting Suite (XGBoost, LightGBM, CatBoost)
- **Performance Lift**: Gradient boosting models deliver significant predictive gain (+2.37% ROC-AUC over Logistic Scorecard, reaching **0.7482** with LightGBM).
- **LightGBM Efficiency**: LightGBM achieves the fastest inference latency among complex ensembles (**4.1 ms per 1k**) and lowest Brier score (**0.13480**).
- **CatBoost Categorical Handling**: Demonstrates native categorical split strength on `sub_grade`, `purpose`, and `home_ownership` without dummy explosion.

---

## 4. Robustness & Stability Analysis

1. **Seed Sensitivity**: Over 5 independent random seed trials (42, 100, 2023, 777, 999), LightGBM exhibited minimal ROC-AUC standard deviation ($\sigma = 0.00028$), confirming algorithmic stability.
2. **Computational Footprint**: LightGBM requires $< 150\text{ MB}$ RAM overhead during inference, making it highly suitable for enterprise containerized deployment.
