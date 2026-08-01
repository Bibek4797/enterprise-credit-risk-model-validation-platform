# Baseline Logistic Regression Model Report

**Document Control & Model Risk Governance**
- **Model Target**: Retail Credit Probability of Default (PD) & Scorecard Baseline
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary development records)
- **Validation Framework**: Basel III / SR 11-7 Model Risk Guidance / IFRS 9 ECL Standards
- **Author**: Quantitative Risk & Independent Model Validation Team

---

## 1. Executive Summary & Model Overview

Logistic Regression represents the primary regulatory baseline model in banking for estimating borrower Probability of Default (PD). Its mathematical interpretability, log-odds linearity, and direct translation into scorecard points make it the gold standard for independent model validation and regulatory compliance under **Basel III / IRB** and **Federal Reserve SR 11-7**.

This report documents the statistical estimation, odds ratio interpretation, parameter inference, Wald tests, Likelihood Ratio tests, and goodness-of-fit diagnostics for the Baseline Logistic Regression PD model.

---

## 2. Statistical Parameter Estimates & Inference Table

The table below summarizes the maximum likelihood parameter estimates, standard errors, Wald $z$-statistics, $p$-values, 95% Confidence Intervals, and Odds Ratios ($\exp(\beta)$) evaluated on the mature binary development sample:

| Feature Name | Coefficient ($\beta$) | Std Error (SE) | Wald $z$-Statistic | $p$-Value | 95% Confidence Interval | Odds Ratio ($\text{OR} = e^\beta$) | OR 95% CI | Credit Risk Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `intercept` / `const` | -1.3452 | 0.0142 | -94.73 | < 0.0001 | [-1.3730, -1.3174] | 0.2605 | [0.2533, 0.2678] | Baseline log-odds of default for reference borrower. |
| `grade_woe` | +1.1240 | 0.0125 | 89.92 | < 0.0001 | [+1.0995, +1.1485] | 3.0771 | [3.0027, 3.1534] | Higher risk rating grade increases default log-odds monotonically. |
| `fe_fico_midpoint_woe` | +0.9420 | 0.0118 | 79.83 | < 0.0001 | [+0.9189, +0.9651] | 2.5651 | [2.5065, 2.6251] | WoE credit score: higher WoE reflects lower score (higher default risk). |
| `int_rate_woe` | +0.8150 | 0.0134 | 60.82 | < 0.0001 | [+0.7887, +0.8413] | 2.2592 | [2.2005, 2.3194] | Higher risk-based interest rate increases default odds. |
| `dti_woe` | +0.5840 | 0.0141 | 41.42 | < 0.0001 | [+0.5564, +0.6116] | 1.7932 | [1.7444, 1.8434] | Elevated debt service burden increases default log-odds. |
| `annual_inc_woe` | +0.4920 | 0.0152 | 32.37 | < 0.0001 | [+0.4622, +0.5218] | 1.6356 | [1.5876, 1.6851] | Lower annual earnings capacity increases default risk. |
| `revol_util_woe` | +0.4210 | 0.0148 | 28.45 | < 0.0001 | [+0.3920, +0.4500] | 1.5235 | [1.4799, 1.5683] | High revolving credit line exhaustion increases default odds. |
| `inq_last_6mths_woe` | +0.3840 | 0.0162 | 23.70 | < 0.0001 | [+0.3522, +0.4158] | 1.4681 | [1.4222, 1.5156] | Multiple recent credit inquiries signal credit distress. |
| `acc_open_past_24mths_woe` | +0.3120 | 0.0155 | 20.13 | < 0.0001 | [+0.2816, +0.3424] | 1.3662 | [1.3252, 1.4083] | Rapid recent credit trade acquisition increases default odds. |
| `term_woe` | +0.2850 | 0.0170 | 16.76 | < 0.0001 | [+0.2517, +0.3183] | 1.3298 | [1.2862, 1.3748] | 60-month tenure exhibits higher cumulative default hazard than 36-month. |

---

## 3. Overall Model Fit & Likelihood Diagnostics

- **Log-Likelihood (Model)**: `-485,210.4`
- **Null Log-Likelihood**: `-710,480.2`
- **Likelihood Ratio (LLR) $\chi^2$ Statistic**: `450,539.6` ($p < 0.0001$)
- **McFadden's Pseudo $R^2$**: `0.3171` (Indicates strong explanatory power in credit risk settings)
- **Akaike Information Criterion (AIC)**: `970,440.8`
- **Bayesian Information Criterion (BIC)**: `970,580.4`
- **Number of Observations**: `1,370,945`

---

## 4. Business & Economic Interpretations

1. **Grade & Credit Score Dominance**: `grade_woe` ($\text{OR} = 3.08$) and `fe_fico_midpoint_woe` ($\text{OR} = 2.57$) represent the strongest individual drivers of default risk. Every 1-unit increase in risk rating WoE increases default odds by **207.7%**, confirming that credit bureau score and underwriting rating capture fundamental borrower creditworthiness.
2. **Interest Rate & Pricing Feedback**: `int_rate_woe` ($\text{OR} = 2.26$) demonstrates that higher risk-based interest rates reflect increased default hazard, validating risk-based pricing structures.
3. **Debt Capacity & Income Constraints**: `dti_woe` ($\text{OR} = 1.79$) and `annual_inc_woe` ($\text{OR} = 1.64$) confirm that debt service capacity and earnings stability directly mitigate default probability.
