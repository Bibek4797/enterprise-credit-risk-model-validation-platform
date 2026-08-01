# Production Model Cards — Credit Risk PD Models

**Document Control & Model Governance**
- **Champion Model ID**: `PD-SCORECARD-2026-V1` (Logistic Scorecard)
- **Challenger Model ID**: `PD-LIGHTGBM-2026-CHALLENGER` (LightGBM Classifier)
- **Model Type**: Probability of Default ($\text{PD}$) Binary Classifiers
- **Governing Guidelines**: Federal Reserve SR 11-7 / OCC 2011-12, FCRA, ECOA
- **Status**: CONDITIONALLY APPROVED FOR PRODUCTION DEPLOYMENT

---

## 1. Model Card: Champion Logistic Scorecard (`PD-SCORECARD-2026-V1`)

### 1.1 Purpose & Intended Use
- **Primary Use**: Automated credit origination underwriting for consumer personal loan applications.
- **Secondary Use**: Generating closed-form point additivity for Fair Credit Reporting Act (FCRA) Adverse Action notice decline reason codes.
- **Out of Scope**: Commercial corporate lending, real estate mortgages, or auto loans.

### 1.2 Model Inputs & Preprocessing
- **Inputs (10 WoE Risk Drivers)**: `sub_grade`, `int_rate`, `fico_range_low`, `dti`, `annual_inc`, `revol_util`, `inq_last_6mths`, `acc_open_past_24mths`, `tot_cur_bal`, `mort_acc`.
- **Preprocessing**: Coarse classing, Weight of Evidence ($\text{WoE}$) transformation ensuring monotonic log-odds response.

### 1.3 Model Output & Score Conversion
- **Raw Output**: Predicted Probability of Default $P(y=1|x) \in [0, 1]$.
- **Scaled Credit Score**:
  $$\text{Score} = \text{Offset} + \text{Factor} \times \ln \left( \frac{1 - \text{PD}}{\text{PD}} \right)$$
  (Targeting $600$ points at $19:1$ odds with $\text{PDO} = 20$ points).

### 1.4 Performance & Metrics Summary
- **Out-of-Time ROC-AUC**: `0.7245` (95% CI: `[0.7218, 0.7272]`)
- **Gini Index**: `0.4490`
- **KS Statistic**: `34.82%`
- **Brier Score**: `0.14120` (Hosmer-Lemeshow test $p = 0.142$, naturally calibrated).
- **Inference Latency**: `0.5 Milliseconds` per 1,000 requests.

### 1.5 Ethical Considerations & Fair Lending Audit
- **ECOA Compliance**: Protected demographic attributes (race, gender, age, marital status) strictly excluded.
- **Disparate Impact Ratio**: All income tier groups exceed the 80% rule ($\text{DIR} \ge 0.852$).

---

## 2. Model Card: Challenger LightGBM (`PD-LIGHTGBM-2026-CHALLENGER`)

### 2.1 Purpose & Intended Use
- **Primary Use**: Risk-based interest rate pricing optimization, high-exposure portfolio segmentation, and early warning monitoring.
- **Performance**: OOT ROC-AUC = `0.7482` (+2.37% lift over Scorecard), KS = `38.42%`, Inference Latency = `4.1 Milliseconds`.
- **Monitoring Strategy**: Monthly $\text{PSI} < 0.10$ tracking, quarterly ROC-AUC audit ($\Delta \text{AUC} \le -0.0300$), semi-annual isotonic recalibration.
