# Optuna Hyperparameter Optimization Audit Report

**Document Control & Model Risk Governance**
- **Model Scope**: Hyperparameter Tuning & Search Space Documentation for ML Risk Models
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary development records)
- **Framework**: Optuna TPE (Tree-structured Parzen Estimator) Bayesian Optimization
- **Author**: Quantitative Risk Analytics & Independent Model Validation Team

---

## 1. Executive Summary & Optimization Framework

Hyperparameter optimization for enterprise credit risk models requires a systematic, reproducible search mechanism that prevents overfitting to training data while maximizing Out-Of-Time validation ROC-AUC. 

**Optuna** was selected as the primary optimization framework due to its efficient Tree-structured Parzen Estimator (TPE) algorithm, automated trial logging, and search space sampling capabilities across gradient boosting and ensemble tree architectures.

---

## 2. Search Space Specifications & Best Parameters

| Model Architecture | Hyperparameter Name | Search Space Range | Sampling Type | Optimal Value Selected | Business Rationale & Effect |
| --- | --- | --- | --- | --- | --- |
| **XGBoost** | `learning_rate` | [0.01, 0.15] | Log Uniform | `0.042` | Low rate prevents gradient overshoot. |
| | `max_depth` | [3, 8] | Discrete Int | `5` | Controls tree depth to avoid high variance. |
| | `n_estimators` | [100, 300] | Discrete Int | `220` | Early stopping triggered around 185 trees. |
| | `subsample` | [0.6, 1.0] | Uniform | `0.80` | Row subsampling adds stochastic regularization. |
| | `colsample_bytree` | [0.6, 1.0] | Uniform | `0.75` | Feature subsampling reduces tree correlation. |
| | `gamma` | [0.0, 1.0] | Uniform | `0.15` | Minimum loss reduction for split. |
| | `reg_alpha` ($L_1$) | [1e-3, 10.0] | Log Uniform | `0.52` | $L_1$ regularization enforces feature sparsity. |
| | `reg_lambda` ($L_2$) | [1e-3, 10.0] | Log Uniform | `2.10` | $L_2$ regularization smooths leaf weights. |
| **LightGBM** | `learning_rate` | [0.01, 0.15] | Log Uniform | `0.038` | Enables fine-grained gradient updates. |
| | `num_leaves` | [15, 63] | Discrete Int | `31` | Controls leaf capacity for non-linearities. |
| | `min_child_samples` | [20, 100] | Discrete Int | `50` | Prevents isolated noisy leaf creation ($>50$). |
| | `subsample` | [0.6, 1.0] | Uniform | `0.85` | Row sampling parameter. |
| | `colsample_bytree` | [0.6, 1.0] | Uniform | `0.80` | Feature sampling parameter. |
| **CatBoost** | `iterations` | [100, 300] | Discrete Int | `250` | Number of boosting iterations. |
| | `learning_rate` | [0.01, 0.15] | Log Uniform | `0.045` | Step size shrinking. |
| | `depth` | [4, 8] | Discrete Int | `6` | Symmetric tree depth. |
| | `l2_leaf_reg` | [1.0, 10.0] | Uniform | `4.5` | $L_2$ regularization coefficient. |
| **Random Forest** | `n_estimators` | [100, 300] | Discrete Int | `150` | Ensemble forest size. |
| | `max_depth` | [6, 16] | Discrete Int | `12` | Tree depth restriction. |
| | `min_samples_leaf` | [10, 50] | Discrete Int | `30` | Minimum leaf node size ($>30$). |

---

## 3. Optuna Trial Performance & Execution Time Comparison

| Model Architecture | Total Trials Evaluated | Best Validation ROC-AUC | Best Trial Number | Average Trial Duration (s) | Total Tuning Time (min) |
| --- | --- | --- | --- | --- | --- |
| **LightGBM** | 15 | **0.7482** | Trial 11 | 4.2 s | 1.1 min |
| **XGBoost** | 15 | **0.7476** | Trial 9 | 12.5 s | 3.1 min |
| **CatBoost** | 15 | **0.7468** | Trial 14 | 18.2 s | 4.5 min |
| **Random Forest** | 15 | **0.7385** | Trial 8 | 15.1 s | 3.8 min |
| **Extra Trees** | 15 | **0.7352** | Trial 6 | 11.4 s | 2.8 min |

---

## 4. Hyperparameter Audit & Stability Conclusion

1. **LightGBM Speed & Performance Lead**: LightGBM completed 15 Optuna trials in just 1.1 minutes while achieving the highest validation ROC-AUC (0.7482), demonstrating exceptional computational efficiency.
2. **Convergence Verification**: All gradient boosting algorithms converged smoothly within 10–15 trials, displaying stable parameter boundaries without extreme hyperparameter values.
