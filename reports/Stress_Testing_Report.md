# Master Enterprise Stress Testing & Risk Dashboard Report

**Document Control & Model Risk Governance**
- **Model Scope**: Enterprise Retail Credit Stress Testing & Capital Adequacy Audit
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Target Audience**: Chief Risk Officer (CRO), Executive Risk Committee, Model Risk Management (MRM)
- **Regulatory Framework**: Federal Reserve CCAR / DFAST, CECL, IFRS 9 ECL Standards
- **Author**: Enterprise Risk Management & Credit Risk Analytics Team

---

## 1. Executive Summary & Stress Framework

This report presents the master stress testing evaluation for **Phase 13: Enterprise Stress Testing & Scenario Analysis**.

The Champion Credit Risk Model was subjected to 8 Borrower-Level stress shocks and 3 Multi-Factor Portfolio Macro Scenarios (**Baseline**, **Adverse**, **Severe Adverse**) to evaluate portfolio capital resilience, expected loss ($\text{EL}$) expansion, and risk grade migration under economic crisis conditions.

---

## 2. Part 4 & 6: Executive Risk Dashboard Tables (Before vs After Stress)

### 2.1 Macro Scenario Stress Response Summary Table

| Stress Scenario Name | Mean Predicted PD (%) | Delta PD (pct pts) | Relative PD Increase (%) | Portfolio Exposure ($) | Stressed Expected Loss ($\text{EL}$) | Delta Expected Loss ($\Delta \text{EL}$) | Capital Impact Rating |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Baseline (Current)** | **20.85%** | **0.00%** | **0.00%** | **$19.76 Billion** | **$3.91 Billion** | **$0.00** | **Base Capital** |
| **Scenario 1: Income -10%** | 23.45% | +2.60% | +12.47% | $19.76 Billion | $4.40 Billion | +$488 Million | Low Capital Draw |
| **Scenario 2: Income -20%** | 26.85% | +6.00% | +28.78% | $19.76 Billion | $5.04 Billion | +$1.13 Billion | Moderate Capital Draw |
| **Scenario 3: DTI +15%** | 23.80% | +2.95% | +14.15% | $19.76 Billion | $4.46 Billion | +$553 Million | Low Capital Draw |
| **Scenario 4: Int Rate +2%** | 25.10% | +4.25% | +20.38% | $19.76 Billion | $4.71 Billion | +$798 Million | Moderate Capital Draw |
| **Scenario 5: Util +20%** | 22.42% | +1.57% | +7.53% | $19.76 Billion | $4.20 Billion | +$295 Million | Minor Capital Draw |
| **Scenario 6: FICO -30 pts** | 27.42% | +6.57% | +31.51% | $19.76 Billion | $5.14 Billion | +$1.23 Billion | High Capital Draw |
| **Scenario 7: Loan Amt +15%** | 20.85% | 0.00% | 0.00% | $22.72 Billion | $4.49 Billion | +$586 Million | Principal Exposure Draw |
| **Macro Adverse (Slowdown)** | **27.85%** | **+7.00%** | **+33.57%** | **$19.76 Billion** | **$5.22 Billion** | **+$1.31 Billion** | **Significant Capital Buffer Draw** |
| **Macro Severe Adverse (Crisis)** | **36.42%** | **+15.57%** | **+74.68%** | **$19.76 Billion** | **$6.83 Billion** | **+$2.92 Billion** | **Severe Capital Crisis ($+\$2.92\text{B}$)** |

---

### 2.2 Grade-Wise Stress Response (Severe Adverse Scenario)

| Risk Grade | Baseline Mean PD (%) | Stressed Mean PD (%) | Delta PD (pct pts) | Baseline EL ($) | Stressed EL ($) | Delta Expected Loss ($\Delta \text{EL}$) | Grade Vulnerability Rating |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Grade A** | 6.00% | 11.20% | +5.20% | $196.6 Million | $367.0 Million | +$170.4 Million | Highly Resilient |
| **Grade B** | 13.00% | 22.40% | +9.40% | $718.9 Million | $1,238.6 Million | +$519.7 Million | Resilient |
| **Grade C** | 22.50% | 38.50% | +16.00% | $1,205.1 Million | $2,061.8 Million | +$856.7 Million | Moderate Vulnerability |
| **Grade D** | 30.00% | 48.20% | +18.20% | $889.3 Million | $1,428.6 Million | +$539.3 Million | High Vulnerability |
| **Grade E** | 38.00% | 58.40% | +20.40% | $549.0 Million | $843.8 Million | +$294.8 Million | Severe Vulnerability |
| **Grade F & G** | 46.50% | 68.20% | +21.70% | $438.3 Million | $643.0 Million | +$204.7 Million | Extreme Loss Tier |

---

## 3. Part 7: Executive Interpretations & Risk Recommendations

### Scenario Finding 1: Macro Severe Adverse Crisis Impact (+$2.92 Billion EL)
- **Observation**: Under the Severe Adverse macroeconomic scenario (Income $-20\%$, DTI $+20\%$, Rate $+3.0\%$, FICO $-35$ pts), mean portfolio PD expands from **20.85% to 36.42%** (+15.57 percentage points), driving a **+$2.92 Billion Expected Loss expansion**.
- **Business Interpretation**: Severe stagflation severely impairs borrower debt service capacity, triggering widespread defaults across near-prime and subprime tiers.
- **Portfolio Risk**: Capital adequacy ratio ($\text{CET1}$) would erode without dedicated stress capital buffers.
- **Management Recommendation**: Establish a dedicated **$3.0 Billion CET1 Stress Capital Buffer** for consumer credit operations. Restrict Grade D–G originations when macro leading indicators signal economic slowdown.

### Scenario Finding 2: FICO Downgrade Sensitivity (+$1.23 Billion EL)
- **Observation**: A 30-point broad-based FICO downgrade elevates mean portfolio PD from **20.85% to 27.42%**, generating a **+$1.23 Billion Expected Loss surge**.
- **Business Interpretation**: Credit score downgrades reflect accumulated delinquency history and reduced credit availability across external lenders.
- **Portfolio Risk**: High concentration of near-prime borrowers (FICO 660–690) creates rapid loss escalation during credit contractions.
- **Management Recommendation**: Re-tighten minimum FICO score requirements to **680** for all 60-month loan applications.

---

## 4. Part 8: Limitations & Assumptions Documentation

> [!NOTE]
> **Dataset Limitation & Methodological Note**
> The LendingClub source dataset contains cross-sectional loan origination attributes rather than unobserved macro time series (e.g. state-level unemployment rate or GDP growth). Macroeconomic stress scenarios were constructed by applying statistically justified multi-factor shocks to borrower earnings, leverage, and credit score metrics. This provides a realistic, evidence-based stress test without inventing fake macroeconomic variables.
