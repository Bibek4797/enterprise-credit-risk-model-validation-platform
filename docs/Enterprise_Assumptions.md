# Enterprise Modeling & Risk Assumptions Register

**Document Control & Model Risk Governance**
- **System Scope**: Master Governance Register of Modeling, Econometric, and Business Assumptions
- **Target Audience**: Model Risk Management (MRM), Independent Model Validators, Regulators
- **Author**: Quantitative Risk Analytics & Model Risk Governance Team

---

## 1. Executive Summary

Under **Federal Reserve SR 11-7** guidelines, every quantitative model relies on foundational assumptions regarding data, statistical distributions, borrower behavior, and business operations.

This document records the master **Enterprise Assumptions Register** for the Probability of Default ($\text{PD}$) models, detailing each assumption, its technical justification, potential risks if violated, and mandatory monitoring controls.

---

## 2. Master Assumptions Register

| Assumption ID | Category | Assumption Description | Technical & Econometric Justification | Risk if Assumption Fails | Monitoring & Mitigation Control |
| --- | --- | --- | --- | --- | --- |
| **ASM-01** | **Target Definition** | Loans labeled `Charged Off`, `Default`, or `Late (31-120 days)` represent default events ($y=1$); `Fully Paid` loans represent good outcomes ($y=0$). | Standard Basel III IRB definition of obligor default; excludes active current loans without mature credit performance history. | Misclassification of defaulted borrowers as good outcomes, underestimating portfolio $\text{PD}$. | Exclude active non-matured loans; audit target definition against credit bureau charge-off flags. |
| **ASM-02** | **WoE Monotonicity** | Weight of Evidence ($\text{WoE}$) values across ordered feature bins must exhibit monotonic log-odds trends. | Ensures business logic compliance (e.g., higher FICO must always yield higher score points and lower $\text{PD}$). | Non-monotonic bins introduce sample noise, leading to illogical applicant score deductions. | Automated monotonicity check in `src/features/woe_iv.py`; coarse classing of non-monotonic bins. |
| **ASM-03** | **OOT Temporal Stability** | The structural relationship between applicant risk drivers and default risk identified in 2007–2016 development data remains valid for 2017–2018 OOT test data. | Out-of-Time temporal split verifies generalization across mild economic cycle shifts. | Macroeconomic regime shifts (e.g., severe recession) invalidate baseline scorecard weights. | Monthly Population Stability Index ($\text{PSI}$) and Characteristic Stability Index ($\text{CSI}$) tracking. |
| **ASM-04** | **Loss Given Default ($\text{LGD}$)** | Loss Given Default is fixed at a static $\text{LGD} = 95.0\%$ ($\text{Recovery Rate} = 6.97\%$). | Empirical post-default recovery analysis of uncollateralized LendingClub personal loans. | In severe economic downturns, recovery rates may drop further, underestimating Expected Loss ($\text{EL}$). | Maintain conservative $\$3.0\text{B}$ CET1 Stress Capital Buffer; run quarterly macro stress tests. |
| **ASM-05** | **Exposure at Default ($\text{EAD}$)** | Exposure at Default equals the initial funded loan amount ($\text{EAD} = \text{loan\_amnt}$). | Personal installment loans have fixed amortization schedules without revolving draw lines. | Borrower prepayments or early defaults alter outstanding principal balance. | Audit actual principal balances at default against scheduled amortization tables. |
| **ASM-06** | **Multicollinearity Limit** | Features in the unpenalized Logistic Scorecard must satisfy Variance Inflation Factor $\text{VIF} \le 5.0$. | Prevents Hessian matrix singularity and covariance inflation in maximum likelihood estimation. | High collinearity causes unstable, uninterpretable score point contributions across risk drivers. | Spearman correlation Ward-linkage clustering ($\rho < 0.70$) and VIF screening in feature selection. |
| **ASM-07** | **PSI Monitoring Triggers** | Portfolio stability is classified into Traffic Light states ($\text{Green} < 0.10$, $\text{Yellow } 0.10-0.25$, $\text{Red} \ge 0.25$). | Industry standard SR 11-7 monitoring benchmarks. | Unnoticed population drift causes silent deterioration in underwriting discrimination. | Monthly automated PSI audit script (`src/monitoring/psi.py`); mandatory retraining trigger at $\text{PSI} \ge 0.25$. |
| **ASM-08** | **Score Cutoff Threshold** | Optimal score cutoff threshold is fixed at $\text{PD} = 0.20$ ($20.0\%$). | Maximizes Kolmogorov-Smirnov ($\text{KS} = 34.82\%$) bad/good separation while maintaining a high $78.4\%$ approval yield. | Shifting risk appetite requires adjusting approval cutoffs. | Interactive cutoff slider embedded in Streamlit dashboard (`pages/3_Model_Performance.py`). |
