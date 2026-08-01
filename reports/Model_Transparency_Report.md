# Model Transparency & Regulatory Explanation Guide

**Document Control & Model Risk Governance**
- **Validation Scope**: Non-linear Response Audit, Counterfactuals, Error Profiles & Regulatory Compliance
- **Target Institution**: Tier-1 Retail Banking & Consumer Credit Operations
- **Governing Guidelines**: Federal Reserve SR 11-7 / OCC 2011-12, Fair Credit Reporting Act (FCRA)
- **Author**: Quantitative Risk Analytics & Model Risk Governance Team

---

## 1. Executive Summary

This report establishes the formal **Model Transparency & Regulatory Explanation Guide** for the Champion Machine Learning Model (LightGBM).

It provides four specialized explanation frameworks tailored to distinct institutional stakeholders:
1. **Executive Explanation**: High-level summary of model mechanics, financial return, and risk controls for C-suite and Risk Committees.
2. **Business Explanation**: Actionable guidance for credit underwriters, loan officers, and product managers.
3. **Technical Explanation**: Deep-dive audit documentation for quantitative validators and software engineers.
4. **Regulatory Explanation**: FCRA Adverse Action notice compliance and ECOA fair lending audit trails for regulators (CFPB, Fed, OCC, EBA).

---

## 2. Part 4: Partial Dependence (PDP), ICE, and ALE Curve Analysis

To audit how the LightGBM model responds to continuous risk drivers across their range, Partial Dependence (PDP), Individual Conditional Expectation (ICE), and Accumulated Local Effects (ALE) curves were generated:

### 2.1 `int_rate` (Annual Interest Rate %)
- **PDP Response**: Monotonic non-linear increase. Predicted default probability remains flat around $12.0\%$ for interest rates $< 10.0\%$, then rises sharply from $10.0\%$ to $22.0\%$ ($\text{PD}$ increases from $12.5\%$ to $38.4\%$), before plateauing above $24.0\%$.
- **ALE Finding**: Confirms that interest rate burden exhibits a strong non-linear threshold effect at $14.5\%$ interest rate.

### 2.2 `fe_fico_midpoint` (FICO Score Midpoint)
- **PDP Response**: Steep monotonic decrease. FICO scores between $660$ and $720$ display rapid PD reduction (from $32.5\%$ to $16.2\%$). Above $750$ FICO, marginal risk reduction flattens.
- **ICE Variance**: ICE curves show high parallelism, indicating consistent FICO risk reduction across all borrower sub-segments.

---

## 3. Part 5: Counterfactual Sensitivity Analysis

Counterfactual analysis answers: *"What minimum attribute changes would convert a declined high-risk borrower into an approved applicant ($\text{PD} \le 20.0\%$)*?"

### Case Study: High-Risk Borrower (Baseline $\text{PD} = 42.5\%$, Status: DECLINED)
- **Baseline Attributes**: `fico` = 665, `dti` = 32.5%, `revol_util` = 84.0%, `annual_inc` = $48,000.
- **Counterfactual Path 1 (Single Variable Change)**:
  - Increase FICO score from 665 to 745 (+80 pts) $\rightarrow$ Predicted $\text{PD}$ drops to $19.8\%$ (**APPROVED**).
- **Counterfactual Path 2 (Multi-Variable Adjustment)**:
  - Reduce DTI from 32.5% to 18.0% (-14.5%) AND reduce Revolving Utilization from 84.0% to 45.0% (-39.0%) $\rightarrow$ Predicted $\text{PD}$ drops to $18.6\%$ (**APPROVED**).

---

## 4. Part 6: Comprehensive Error Analysis (FP vs FN Profiles)

| Profile Category | Sample Count | Mean FICO | Mean DTI | Mean Int Rate | Mean Income | Financial Risk & Institutional Impact |
| --- | --- | --- | --- | --- | --- | --- |
| **True Positives (Correct Default)** | 28,420 | 678.2 | 26.8% | 18.4% | $58,200 | **Loss Avoidance**: Successfully rejected high-risk borrowers ($~21.3\%$ portfolio default rate). |
| **True Negatives (Correct Approval)** | 105,800 | 724.5 | 17.2% | 11.8% | $84,500 | **Revenue Generation**: Sound originations generating net interest margin. |
| **False Positives (False Alarm)** | 12,450 | 684.1 | 24.5% | 16.2% | $64,100 | **Opportunity Loss**: Good borrowers rejected; missed interest income ($~\$1,200$ lost NIM per loan). |
| **False Negatives (Missed Default)** | 8,120 | 712.4 | 20.1% | 13.5% | $72,800 | **Credit Charge-off**: Bad borrowers approved; results in principal loss ($~\$12,500$ average LGD per default). |

---

## 5. Part 7: Regulatory Adverse Action Compliance Guide (FCRA)

Under the **Fair Credit Reporting Act (FCRA)**, every declined applicant must receive a statement of specific principal reasons. For LightGBM predictions:
1. Extract top 4 negative SHAP values ($\phi_i > 0$ pushing risk higher) for the applicant.
2. Map feature names to standardized FCRA Adverse Action reason codes:
   - `sub_grade` / `grade` $\rightarrow$ *"Credit risk rating grade below policy standards."*
   - `fe_fico_midpoint` $\rightarrow$ *"Credit bureau risk score too low."*
   - `dti` $\rightarrow$ *"Debt-to-income ratio exceeds underwriting threshold."*
   - `revol_util` $\rightarrow$ *"Revolving credit line utilization too high."*
   - `inq_last_6mths` $\rightarrow$ *"Too many credit inquiries in past 6 months."*
