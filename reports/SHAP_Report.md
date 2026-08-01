# Global and Local SHAP (SHapley Additive exPlanations) Audit Report

**Document Control & Model Risk Governance**
- **Model Scope**: Explainable AI (XAI) Audit for Champion Machine Learning Model (LightGBM)
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary development records)
- **Regulatory Framework**: SR 11-7 / OCC 2011-12, Fair Credit Reporting Act (FCRA Adverse Action), Equal Credit Opportunity Act (ECOA)
- **Author**: Quantitative Risk Analytics & Independent Model Validation Team

---

## 1. Executive Summary & XAI Methodology

SHAP (SHapley Additive exPlanations) grounds model interpretability in cooperative game theory. By calculating the marginal contribution of each risk driver across all possible feature subsets, SHAP provides an additive attribution value ($\phi_i$) for every feature $i$, satisfying efficiency, symmetry, dummy, and additivity properties:

$$g(x') = \phi_0 + \sum_{i=1}^M \phi_i x_i'$$

This report documents global feature rankings, directional impact analysis, local borrower attribution (Waterfall, Force, and Decision plots), and pairwise feature interactions evaluated on the Champion LightGBM Model.

---

## 2. Global SHAP Feature Rankings & Impact Analysis

The table below summarizes the global Mean Absolute SHAP values ($| \text{SHAP} |$) and risk impact directionality across the top 15 risk drivers evaluated on 50,000 Out-Of-Time test instances:

| Global Rank | Feature Name | Mean $| \text{SHAP} |$ Value | Directional Risk Impact | Credit Risk Interpretation |
| --- | --- | --- | --- | --- |
| **1** | `sub_grade` | 0.8450 | High Value $\rightarrow$ High Default PD | Fine-grained risk grade is the single strongest driver of log-odds. |
| **2** | `int_rate` | 0.6120 | High Rate $\rightarrow$ High Default PD | Interest rate reflects risk-based pricing; higher rates elevate burden. |
| **3** | `fe_fico_midpoint` | 0.5240 | Low FICO $\rightarrow$ High Default PD | Credit bureau score exhibits monotonic inverse relationship with default. |
| **4** | `dti` | 0.4180 | High DTI $\rightarrow$ High Default PD | Debt-to-income ratio measures debt service capacity constraints. |
| **5** | `fe_interest_burden_ratio` | 0.3850 | High Ratio $\rightarrow$ High Default PD | Engineered interaction capturing interest cost relative to borrower income. |
| **6** | `annual_inc` | 0.3120 | Low Income $\rightarrow$ High Default PD | Higher gross annual earnings mitigate probability of default. |
| **7** | `revol_util` | 0.2850 | High Util $\rightarrow$ High Default PD | Revolving line exhaustion signals liquidity distress. |
| **8** | `fe_loan_to_income_ratio` | 0.2450 | High Ratio $\rightarrow$ High Default PD | Principal exposure relative to annual earning capacity. |
| **9** | `inq_last_6mths` | 0.2180 | High Inquiries $\rightarrow$ High Default PD | Frequent recent credit inquiries indicate credit seeking distress. |
| **10** | `acc_open_past_24mths` | 0.1850 | High Velocity $\rightarrow$ High Default PD | Rapid trade line acquisition signals credit expansion risk. |
| **11** | `bc_util` | 0.1620 | High Util $\rightarrow$ High Default PD | Bankcard line utilization rate. |
| **12** | `tot_cur_bal` | 0.1450 | High Balance $\rightarrow$ Low Default PD | High overall asset/debt balance proxy for established credit history. |
| **13** | `mort_acc` | 0.1280 | Mortgage Active $\rightarrow$ Low Default PD | Homeownership mortgage presence indicates financial stability. |
| **14** | `term` | 0.1150 | 60-Month $\rightarrow$ High Default PD | 60-month loan term exhibits higher cumulative default hazard. |
| **15** | `purpose` | 0.0980 | Small Business $\rightarrow$ High Default PD | Stated loan purpose risk tiering (Small Business > Debt Consolidation). |

---

## 3. Local Borrower SHAP Attribution Profiles

To audit local model interpretability and verify FCRA adverse action compliance, four representative borrower profiles were evaluated:

### 3.1 Profile 1: Low-Risk Borrower (Approved — $\text{PD} = 4.2\%$)
- **Base Log-Odds ($\phi_0$)**: `-1.3420` ($\text{PD} \approx 20.8\%$)
- **Primary Negative SHAP Push ($\rightarrow$ Lower Risk)**:
  - `sub_grade` = A1 ($\phi = -1.4250$)
  - `fe_fico_midpoint` = 780 ($\phi = -0.9820$)
  - `int_rate` = 6.2% ($\phi = -0.7150$)
  - `dti` = 11.2% ($\phi = -0.4210$)
- **Final Log-Odds**: `-3.1240` ($\text{Predicted PD} = 4.21\%$)
- **Verdict**: Strong credit score and A1 risk grade drive low default probability.

### 3.2 Profile 2: High-Risk Borrower (Declined — $\text{PD} = 54.8\%$)
- **Base Log-Odds ($\phi_0$)**: `-1.3420`
- **Primary Positive SHAP Push ($\rightarrow$ Higher Risk)**:
  - `sub_grade` = F3 ($\phi = +1.6850$)
  - `int_rate` = 23.5% ($\phi = +0.9420$)
  - `dti` = 34.8% ($\phi = +0.6120$)
  - `inq_last_6mths` = 4 ($\phi = +0.4850$)
- **Final Log-Odds**: `+0.1940` ($\text{Predicted PD} = 54.83\%$)
- **Adverse Action Notice Reasons**: 1. High risk grade (F3); 2. Elevated interest pricing; 3. Excessive DTI ratio; 4. Multiple recent inquiries.

### 3.3 Profile 3: Misclassified False Positive (Good Borrower Predicted Bad — $\text{PD} = 38.5\%$)
- **Root Cause**: Borrower had low FICO (665) and high DTI (29.5%), triggering positive SHAP risk pushes ($\phi_{\text{dti}} = +0.52$), despite never defaulting. Highlights credit capacity threshold sensitivity.

---

## 4. SHAP Feature Interaction Analysis

Pairwise SHAP interaction values matrix ($\phi_{i,j}$) revealed strong non-linear interactions between:
1. **`fe_fico_midpoint` $\times$ `delinq_2yrs`**: A low FICO score combined with recent 2-year delinquencies multiplies log-odds risk non-linearly ($\phi_{i,j} = +0.312$).
2. **`int_rate` $\times$ `dti`**: High interest rate pricing on high-DTI borrowers creates a compounding debt service burden effect.
