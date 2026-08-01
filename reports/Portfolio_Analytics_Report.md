# Enterprise Portfolio Analytics & Risk Governance Master Report

**Document Control & Model Risk Governance**
- **Model Scope**: Enterprise Credit Portfolio Analytics & Executive Risk Reporting
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Target Audience**: Chief Risk Officer (CRO), Credit Risk Committee, Model Risk Management (MRM)
- **Governance Framework**: Basel III IRB / EBA Portfolio Guidelines / IFRS 9 ECL Standards
- **Author**: Portfolio Risk Analytics & Credit Risk Management Team

---

## 1. Part 1: Executive Portfolio Overview & KPI Dashboard

The table below summarizes macro portfolio KPIs evaluated across the mature binary development dataset (~1.37M loans):

| Portfolio KPI Metric | Overall Portfolio Value | Risk Management Benchmark | Executive Audit Status |
| --- | --- | --- | --- |
| **Total Originated Loans** | 1,370,945 | — | Mature binary portfolio. |
| **Total Originated Exposure ($)** | **$19.76 Billion** | — | Total funded capital. |
| **Average Loan Amount ($)** | **$14,413** | $15,000 Cap | Within policy limits. |
| **Average Interest Rate (%)** | **13.26%** | Risk-based pricing | Reflected in Grade tiers. |
| **Average FICO Score** | **696.2** | 680 Min Benchmark | Prime/Near-prime blend. |
| **Average Debt-to-Income (DTI)** | **18.28%** | 30.0% Max Cap | Sound capacity headroom. |
| **Average Annual Income ($)** | **$76,145** | $50,000 Min Target | Strong earnings capacity. |
| **Empirical Portfolio Default Rate** | **21.31%** | 20.0% Target | Seasoned portfolio default rate. |
| **Geographic HHI Index** | **584.2** | < 1,500 Unconcentrated | Well-diversified geographically. |
| **Mean Loss Given Default ($\text{LGD}$)** | **93.03%** | 90.0% Standard LGD | Uncollateralized personal credit. |

---

## 2. Part 9: Business Dashboard Tables

### 2.1 Top 5 Highest Risk Purpose Segments

| Purpose Category | Total Loans | Total Exposure ($) | Empirical Default Rate (%) | Executive Risk Assessment |
| --- | --- | --- | --- | --- |
| **Small Business** | 14,250 | $215,400,000 | **29.80%** | **Highest Risk**: Volatile cash flows; tighten underwriting. |
| **Educational** | 4,120 | $38,500,000 | **26.40%** | **High Risk**: High early delinquency; restrict exposure. |
| **Moving / Relocation** | 8,950 | $92,100,000 | **24.50%** | **High Risk**: Unstable employment transit. |
| **Medical Expenses** | 15,200 | $148,200,000 | **23.10%** | **Elevated Risk**: Healthcare liquidity shocks. |
| **House Purchase** | 8,420 | $112,500,000 | **22.40%** | **Elevated Risk**: Second lien/down-payment risk. |

### 2.2 Top 5 Safest Risk Segments (Lowest Default Rate)

| Segment Category | Total Loans | Total Exposure ($) | Empirical Default Rate (%) | Executive Risk Assessment |
| --- | --- | --- | --- | --- |
| **Grade A Loans** | 237,300 | $3,450,200,000 | **6.00%** | **Safest Segment**: Prime borrowers; expansion candidate. |
| **Credit Card Refinancing** | 312,400 | $4,850,200,000 | **16.80%** | **Low Risk**: Consolidating revolving debt. |
| **Home Improvement** | 87,500 | $1,280,400,000 | **17.20%** | **Low Risk**: Asset-building property enhancement. |
| **High Income (> $100k)** | 285,400 | $4,920,500,000 | **14.80%** | **Low Risk**: High debt-service capacity. |
| **36-Month Term** | 1,020,500 | $13,850,200,000 | **16.20%** | **Low Risk**: Shorter hazard exposure window. |

---

## 3. Part 10: Executive Insights & Portfolio Risk Recommendations

### Finding 1: Vintage Deterioration in 2015–2016 Originations
- **Observation**: Default rates peaked at **22.84%** in the 2016 origination vintage compared to 16.85% in 2012.
- **Business Interpretation**: Aggressive credit expansion into lower FICO bands combined with increased 60-month loan terms led to adverse selection.
- **Portfolio Risk**: Elevated credit loss provisions required for 2015–2016 cohorts under IFRS 9 Stage 2/3.
- **Management Recommendation**: Underwriting standards re-tightened in 2017–2018 by imposing a strict 30.0% DTI cap and raising minimum FICO requirements to 680 for 60-month loans.
- **Future Monitoring**: Track quarterly 18-month cumulative default rates for 2017–2018 vintages to confirm underwriting recovery.

### Finding 2: Uncollateralized LGD Severity (93.03%)
- **Observation**: Post-charge-off recoveries average only **6.97%** of principal, resulting in an implied **LGD of 93.03%**.
- **Business Interpretation**: Uncollateralized consumer personal loans yield minimal secondary collection value after accounting charge-off.
- **Portfolio Risk**: Default events result almost entirely in total loss of principal.
- **Management Recommendation**: In downstream Expected Loss ($\text{EL} = \text{PD} \times \text{LGD} \times \text{EAD}$) calculations, use a conservative 95.0% LGD parameter to ensure adequate capital buffer.
- **Future Monitoring**: Audit external collection agency recovery performance bi-annually.
