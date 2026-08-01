# Enterprise Scenario Analysis & Stress Test Specifications

**Document Control & Model Risk Governance**
- **Model Scope**: Stress Testing & Scenario Analysis Specifications for Retail Credit Portfolio
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Regulatory Framework**: Federal Reserve CCAR / DFAST, CECL, IFRS 9 Stress Testing Standards
- **Author**: Enterprise Risk Management & Credit Risk Analytics Team

---

## 1. Executive Summary & Stress Testing Framework

Under **Federal Reserve CCAR/DFAST** and **IFRS 9 Expected Credit Loss** standards, banking institutions must evaluate portfolio loss resilience under adverse economic conditions.

This report documents the specifications and technical assumptions for 8 Borrower-Level Stress Scenarios and 3 Multi-Factor Portfolio Macro Scenarios applied to the Champion Credit Risk Model.

---

## 2. Part 2: Borrower-Level Stress Scenario Specifications

| Scenario ID | Scenario Name | Shock Specification & Parameter Change | Economic Justification & Borrower Context |
| --- | --- | --- | --- |
| **Scenario 1** | Income Shock (-10%) | `annual_inc` $\times 0.90$ | Moderate wage stagnation / reduction in overtime hours. |
| **Scenario 2** | Severe Income Shock (-20%) | `annual_inc` $\times 0.80$ | Macroeconomic recession / partial unemployment / furloughs. |
| **Scenario 3** | Debt-to-Income Surge (+15%) | `dti` $\times 1.15$ | Increased non-housing debt obligations / inflation pressure. |
| **Scenario 4** | Interest Rate Spike (+200 bps) | `int_rate` $+ 2.0\%$ | Central bank monetary policy tightening / rate hike cycle. |
| **Scenario 5** | Revolving Utilization Spike (+20%) | `revol_util` $\times 1.20$ | Household liquidity exhaustion / credit card dependence. |
| **Scenario 6** | Credit Score Downgrade (-30 pts) | `fico_range_low` $- 30$ pts | Credit bureau delinquency history / missed payments. |
| **Scenario 7** | Principal Exposure Surge (+15%) | `loan_amnt` $\times 1.15$ | Increased borrowing requests under inflationary pressure. |
| **Scenario 8** | Employment Tenure Shock | `emp_length` reduction | Job insecurity / employment tenure disruption. |

---

## 3. Part 3: Portfolio Multi-Factor Macroeconomic Scenarios

Rather than inventing unobserved macroeconomic time series, portfolio-level stress scenarios are constructed by applying combined multi-factor feature shocks to the development dataset:

### 3.1 Scenario Baseline: Current Portfolio State
- **Shock Specification**: $0\%$ parameter modification.
- **Economic Context**: Current benign economic conditions (Base Expected Loss).

### 3.2 Scenario Adverse: Moderate Economic Slowdown
- **Shock Specification**: Income $-10\%$, DTI $+10\%$, FICO $-15$ pts, Revolving Utilization $+10\%$.
- **Economic Context**: Mild recession with unemployment rising to $6.5\%$, modest wage cuts, and increased consumer leverage.

### 3.3 Scenario Severe Adverse: Severe Recession & Debt Crisis
- **Shock Specification**: Income $-20\%$, DTI $+20\%$, Interest Rate $+3.0\%$, FICO $-35$ pts, Revolving Utilization $+25\%$.
- **Economic Context**: Severe macroeconomic crisis with unemployment peaking at $9.5\%$, interest rate spikes, sharp real wage contraction, and widespread credit bureau downgrades.
