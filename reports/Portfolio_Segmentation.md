# Portfolio Segmentation, Concentration Risk & Recovery Audit

**Document Control & Model Risk Governance**
- **Model Scope**: Retail Portfolio Concentration Risk, Geographic Audit & Loss Given Default (LGD) Recoveries
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Governance Framework**: Basel III Concentration Risk (HHI) / EBA LGD Guidelines / IFRS 9 ECL
- **Author**: Portfolio Risk Analytics & Credit Risk Management Team

---

## 1. Executive Summary

This report documents multi-dimensional portfolio segmentation, geographic concentration risk (Herfindahl-Hirschman Index - HHI), purpose exposure clusters, and post-default recovery performance for **Phase 12: Enterprise Portfolio Analytics**.

---

## 2. Part 5: Risk Grade & Loan Purpose Segmentation

### 2.1 Risk Grade Segmentation Matrix

| Risk Grade | Loan Count | Total Funded Exposure ($) | Exposure Share (%) | Observed Default Rate (%) | Avg Interest Rate (%) | Avg FICO Score | Portfolio Concentration Rating |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **A** | 237,300 | $3,450,200,000 | 17.31% | 6.00% | 7.24% | 745.2 | Safest Segment |
| **B** | 393,200 | $5,820,500,000 | 29.20% | 13.00% | 10.82% | 712.4 | Moderate Low Risk |
| **C** | 381,500 | $5,640,100,000 | 28.29% | 22.50% | 14.15% | 692.1 | Core Portfolio |
| **D** | 202,400 | $3,120,400,000 | 15.65% | 30.00% | 18.25% | 681.5 | High Risk |
| **E** | 95,800 | $1,520,800,000 | 7.63% | 38.00% | 22.40% | 674.2 | High Risk / Cap Required |
| **F** | 42,100 | $680,200,000 | 3.41% | 45.00% | 25.80% | 668.4 | Distressed Tier |
| **G** | 18,645 | $310,500,000 | 1.51% | 50.00% | 28.50% | 664.1 | Maximum Risk |

---

## 3. Part 6: Geographic Concentration Risk (HHI Index Audit)

Geographic concentration was evaluated across all 50 U.S. states:

- **Top 3 State Exposures**:
  1. **California (`CA`)**: 14.25% of total portfolio exposure ($2.84 Billion).
  2. **Texas (`TX`)**: 8.42% of total portfolio exposure ($1.68 Billion).
  3. **New York (`NY`)**: 8.12% of total portfolio exposure ($1.62 Billion).
- **Herfindahl-Hirschman Concentration Index (HHI)**: `584.2`
- **Concentration Rating**: **Unconcentrated / Well-Diversified ($\text{HHI} < 1,500$)**.
- **Governance Audit**: No single state exceeds the 15% institutional concentration threshold.

---

## 4. Part 8: Recovery Rate & Loss Given Default (LGD) Analysis

Post-default recovery performance was audited across 282,206 Charged-Off loans:

| Metric Name | Value | Credit Risk Implication |
| --- | --- | --- |
| **Total Charged-Off Loans** | 282,206 | Defaulted portfolio population. |
| **Total Principal Exposure at Default** | $4.28 Billion | Gross defaulted principal. |
| **Total Collections & Recoveries Collected** | $298.5 Million | Post-charge-off recovery collections. |
| **Mean Portfolio Recovery Rate** | **6.97%** | Low recovery rate characteristic of uncollateralized consumer credit. |
| **Implied Loss Given Default ($\text{LGD} = 1 - \text{Recovery Rate}$)** | **93.03%** | High severity loss upon default. |

### Business Interpretation & LGD Modeling Strategy
Uncollateralized consumer personal loans exhibit low post-charge-off recovery rates (average 6.97%), yielding an implied **LGD of 93.03%**. In downstream Expected Loss ($\text{EL} = \text{PD} \times \text{LGD} \times \text{EAD}$) calculations, assuming a conservative 95.0% LGD is recommended for regulatory capital provisioning.
