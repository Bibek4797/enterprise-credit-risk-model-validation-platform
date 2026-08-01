# Regularized Logistic Models Report (LASSO, Ridge & Elastic Net)

**Document Control & Model Risk Governance**
- **Model Scope**: Penalized Logistic Regression & Regularization Benchmarking
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary development records)
- **Regulatory Framework**: SR 11-7 Model Risk Guidance / Overfitting Diagnostics
- **Author**: Quantitative Risk & Independent Model Validation Team

---

## 1. Executive Summary & Regularization Objectives

Regularized logistic regression models introduce penalty terms to the log-likelihood objective function to prevent overfitting, mitigate multicollinearity, and perform feature selection:

$$\min_{\beta} \left[ -\sum_{i=1}^N y_i \ln(p_i) + (1-y_i) \ln(1-p_i) + \lambda P(\beta) \right]$$

- **Ridge (L2 Penalty)**: $P(\beta) = \frac{1}{2} \sum \beta_j^2$. Shrinks coefficients toward zero, handling multicollinearity without zeroing features.
- **LASSO (L1 Penalty)**: $P(\beta) = \sum |\beta_j|$. Enforces sparsity by setting non-informative feature coefficients strictly to zero.
- **Elastic Net (L1 + L2 Penalty)**: $P(\beta) = \alpha \sum |\beta_j| + \frac{1-\alpha}{2} \sum \beta_j^2$. Combines L1 feature selection with L2 grouping of correlated risk drivers.

---

## 2. Hyperparameter Tuning & Cross-Validation Results

Using 5-fold Cross-Validation on standardized continuous & binned candidate features, optimal inverse regularization strengths ($C = 1/\lambda$) were identified:

| Model Architecture | Penalty Type | Optimal $C^*$ ($\lambda^* = 1/C^*$) | Active Features Retained | Train ROC-AUC | Val ROC-AUC | Brier Score | Hyperparameter Search Range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Unpenalized Logistic** | None | $\infty$ ($C = \infty$) | 10 / 10 | 0.7248 | 0.7245 | 0.14120 | Baseline unconstrained MLE |
| **Ridge Logistic (L2)** | $L_2$ | $1.00$ ($\lambda = 1.0$) | 10 / 10 | 0.7247 | 0.7245 | 0.14122 | $C \in [10^{-3}, 10^2]$ |
| **LASSO Logistic (L1)** | $L_1$ | $0.215$ ($\lambda = 4.65$) | 8 / 10 | 0.7245 | 0.7244 | 0.14125 | $C \in [10^{-3}, 10^2]$ |
| **Elastic Net** | $L_1 + L_2$ | $0.464$ ($\alpha = 0.5$) | 9 / 10 | 0.7246 | 0.7245 | 0.14123 | $C \in [10^{-3}, 10^2], \alpha = 0.5$ |

---

## 3. Coefficient Shrinkage Path Analysis

The table below details standardized coefficient estimates across unpenalized MLE, Ridge, LASSO, and Elastic Net models:

| Feature Name | Unpenalized MLE Coef | Ridge ($L_2$) Coef | LASSO ($L_1$) Coef | Elastic Net Coef | LASSO Selection Status | Shrinkage Effect |
| --- | --- | --- | --- | --- | --- | --- |
| `grade_woe` | +1.1240 | +1.1180 | +1.1050 | +1.1120 | **RETAINED** | Slight shrinkage (-1.7%) |
| `fe_fico_midpoint_woe` | +0.9420 | +0.9380 | +0.9260 | +0.9310 | **RETAINED** | Slight shrinkage (-1.7%) |
| `int_rate_woe` | +0.8150 | +0.8100 | +0.7980 | +0.8040 | **RETAINED** | Slight shrinkage (-2.1%) |
| `dti_woe` | +0.5840 | +0.5800 | +0.5650 | +0.5720 | **RETAINED** | Moderate shrinkage (-3.3%) |
| `annual_inc_woe` | +0.4920 | +0.4880 | +0.4720 | +0.4800 | **RETAINED** | Moderate shrinkage (-4.1%) |
| `revol_util_woe` | +0.4210 | +0.4160 | +0.3980 | +0.4080 | **RETAINED** | Moderate shrinkage (-5.5%) |
| `inq_last_6mths_woe` | +0.3840 | +0.3780 | +0.3550 | +0.3660 | **RETAINED** | Moderate shrinkage (-7.6%) |
| `acc_open_past_24mths_woe` | +0.3120 | +0.3060 | +0.2820 | +0.2940 | **RETAINED** | Moderate shrinkage (-9.6%) |
| `term_woe` | +0.2850 | +0.2780 | 0.0000 | +0.1250 | **SHRUNK TO 0** | Total shrinkage (Captured by Grade/Rate) |
| `home_ownership_woe` | +0.1820 | +0.1750 | 0.0000 | +0.0820 | **SHRUNK TO 0** | Total shrinkage (Captured by Income/DTI) |

---

## 4. Model Governance & Selection Rationale

1. **Overfitting Assessment**: The negligible gap between Train ROC-AUC (0.7248) and Validation ROC-AUC (0.7245) confirms that the 1.37M mature loan sample is sufficiently large that unpenalized MLE does not suffer from variance or overfitting.
2. **Parsimony vs Accuracy**: LASSO successfully eliminates 2 weak features (`term_woe`, `home_ownership_woe`) while retaining 99.9% of the validation AUC (0.7244 vs 0.7245), providing a parsimonious 8-variable scorecard option.
3. **Recommendation**: Retain Unpenalized Logistic Regression as the primary Champion model for full scorecard point allocation, and store LASSO as an audit-approved Sparse Benchmark model.
