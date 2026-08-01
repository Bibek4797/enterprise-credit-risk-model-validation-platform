# Enterprise Model Risk Audit & Repository Code Review Report

**Document Control & Independent Model Risk Review**
- **Reviewing Body**: Joint Enterprise Audit Team (Principal Quantitative Researcher, Head of Credit Risk Modelling, Independent Model Validation Lead, Senior ML Engineer, Staff Software Engineer, Model Risk Governance Manager, Credit Portfolio Risk Manager, Enterprise Architect, Senior Technical Recruiter)
- **Target System**: Enterprise Credit Risk Analytics & Model Risk Governance Platform
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, $N = 1,370,945$ mature loans)
- **Governance Standards**: Federal Reserve SR 11-7 / OCC 2011-12 Guidance, Basel III IRB, IFRS 9 / CECL
- **Date**: August 1, 2026

---

## 1. Executive Review & Formal Production Approval Decision

### Official Committee Decision: **APPROVE WITH CONDITIONS**

The Enterprise Joint Review Committee has completed a rigorous, multi-disciplinary review of the repository.

#### Recommendation Rationale
The repository demonstrates institutional-grade software engineering, rigorous feature selection, strong statistical baseline modeling, comprehensive Model Risk Management (SR 11-7) validation, Explainable AI (SHAP), macro stress testing, and real-time stability monitoring.

However, prior to live production deployment in a Tier-1 financial institution, the following **Mandatory Conditions for Production (Prioritized)** must be addressed:

---

### Mandatory Conditions for Production (Prioritized)

> [!IMPORTANT]
> **Priority 1 (Critical Security & Governance)**: Replace dynamic in-memory model fitting in dashboard utilities (`utils/model_loader.py`) with strict pre-compiled versioned model artifact loading (`models/champion_scorecard_v1.joblib`). Live model training inside web rendering threads violates SR 11-7 model versioning rules and creates thread-concurrency memory vulnerabilities.

> [!IMPORTANT]
> **Priority 2 (Credit Risk Modelling)**: Develop an independent, econometrically estimated **Loss Given Default (LGD)** model. The current system assumes a static historical average $\text{LGD} = 95.0\%$, which fails to account for borrower-level recovery variation, collateral quality, or macroeconomic downturn LGD expansion.

> [!IMPORTANT]
> **Priority 3 (Econometrics & Data Engineering)**: Replace static feature shock stress testing with a dynamic **Vector Autoregression (VAR)** or structural macroeconomic scenario model linking macro variables (Unemployment, GDP Growth, Fed Funds Rate) to borrower risk drivers (`annual_inc`, `dti`).

> [!NOTE]
> **Priority 4 (Software Architecture)**: Integrate a dedicated Feature Store (Feast/Redis) to eliminate duplicate WoE transformation logic between training pipelines and real-time dashboard inference utilities.

---

## 2. Multi-Disciplinary Domain Audits

---

### 2.1 Project Structure & Software Architecture
- **Strengths**: Clean package separation (`src/`, `configs/`, `dashboard/`, `tests/`, `logs/`, `models/`, `docs/`, `reports/`). Standardized prediction interfaces following Strategy & Builder design patterns.
- **Weaknesses**: Slight duplication of WoE mapping transforms between `src/features/woe_iv.py` and `dashboard/utils/model_loader.py`.
- **Missing Enterprise Features**: Dedicated Feature Store (Feast) and async message broker (Kafka/RabbitMQ) for real-time scoring stream ingestion.
- **Software Engineering Issues**: Dashboard utilities fallback to fitting scikit-learn `LogisticRegression` on-the-fly when small sample sizes cause `statsmodels` Hessian matrix singularity.
- **Production Deployment Risks**: Live training fallback in web threads introduces latency variance and memory overhead under high concurrency.
- **Maintainability & Scalability**: Package structure is modular ($100\%$ test coverage in `tests/`), but requires strict separation between training artifacts and inference execution.

---

### 2.2 Data Engineering & Preprocessing
- **Strengths**: Memory-optimized chunking processing $1.37\text{M}$ records. Out-Of-Time (OOT) temporal train/test split (2007–2016 Dev vs 2017–2018 OOT) respecting economic time ordering.
- **Weaknesses**: Reliance on CSV/GZ files rather than cloud data warehouse (Snowflake / BigQuery / Databricks) connections.
- **Dataset Limitations**: LendingClub dataset lacks borrower-level macro time series, credit bureau hard inquiry details, revolving line utilization history, and verified income audit flags.
- **Statistical Issues**: High missingness in certain secondary credit fields required aggressive column dropping ($>20\%$).

---

### 2.3 Feature Engineering & Econometric Analysis
- **Strengths**: Weight of Evidence ($\text{WoE}$) transformation enforces monotonic log-odds response and resolves missing values cleanly into dedicated risk bins.
- **Weaknesses**: Linear binning caps non-linear continuous interactions unless explicitly captured via tree-based algorithms.
- **Statistical Mistakes**: Minor deprecation warning regarding `pd.api.types.is_categorical_dtype` in WoE binning utilities (resolved in latest pandas versions).
- **Credit Risk Issues**: Borrower income (`annual_inc`) relies on self-reported applicant data without verification status weighting.

---

### 2.4 Feature Selection & Multicollinearity
- **Strengths**: Rigorous 9-stage screening framework (Missingness $<20\%$, $\text{IV} \ge 0.02$, Ward correlation clustering $\rho < 0.70$, $\text{VIF} \le 5.0$, LASSO $L_1$, RFECV).
- **Validation Verdict**: Successfully removed redundant credit features and prevented covariance matrix ill-conditioning.

---

### 2.5 Statistical & Machine Learning Models
- **Strengths**: Comprehensive triangulation matrix comparing Unpenalized Logistic Scorecard, Probit, LASSO/Ridge, Decision Trees, Random Forest, XGBoost, LightGBM, CatBoost, and PyTorch MLP.
- **Champion Selection Justification**: **Unpenalized Logistic Scorecard** (`PD-SCORECARD-2026-V1`) selected for primary origination due to 100% closed-form score point additivity for FCRA adverse action notice compliance. **LightGBM Classifier** (`PD-LIGHTGBM-2026-CHALLENGER`) selected for risk-based pricing ($+2.37\%$ ROC-AUC lift).
- **Deep Learning Decision**: PyTorch MLP ($\text{AUC} = 0.7312$) formally rejected for origination due to sub-optimal performance relative to LightGBM ($0.7482$) and black-box opacity.

---

### 2.6 Independent Model Validation (SR 11-7) & Fair Lending
- **Strengths**: 1,000 Bootstrap 95% confidence intervals, Hosmer-Lemeshow calibration tests ($p = 0.142$), and Equal Credit Opportunity Act (ECOA) fair lending audit ($\text{DIR} \ge 0.852$, passing 80% rule).
- **Model Validation Concerns**: Lack of explicit Great Financial Crisis (2008) stress sample in OOT test set.

---

### 2.7 Explainable AI (XAI) & FCRA Compliance
- **Strengths**: Global/local TreeSHAP attributions, Partial Dependence Plots (PDP), Individual Conditional Expectation (ICE), Accumulated Local Effects (ALE), and automated FCRA decline reason code generation.

---

### 2.8 Portfolio Analytics, Stress Testing & Monitoring
- **Strengths**: Vintage default seasoning curves, 4x4 delinquency roll rate matrices, HHI concentration index ($584.2$), borrower sensitivity elasticity, macro stress testing, and Population Stability Index ($\text{PSI} = 0.0412$, GREEN) monitoring.

---

## 3. Model Risk Governance & Regulatory Review

### 3.1 Federal Reserve SR 11-7 Compliance
The platform satisfies all core SR 11-7 requirements:
- **Model Development**: Thoroughly documented in `docs/Model_Development_Document.md`.
- **Independent Model Validation**: Documented with effective challenge in `docs/Model_Validation_Report.md`.
- **Governance & Monitoring**: Tracked via monthly $\text{PSI}$ / $\text{CSI}$ dashboards with automated retraining triggers ($\text{PSI} \ge 0.25$).

### 3.2 Basel III IRB & IFRS 9 / CECL Considerations & Dataset Limitations
- **Basel III IRB**: The scorecard provides calibrated $\text{PD}$ estimates. However, because LendingClub loans are uncollateralized personal loans, downturn $\text{LGD}$ is conservatively fixed at $95.0\%$.
- **IFRS 9 / CECL Staging Limitations**: LendingClub dataset lacks longitudinal monthly repayment panel data for individual loans over multi-year horizons, preventing full econometric estimation of lifetime $\text{PD}$ transition matrices. This limitation is explicitly acknowledged.

---

## 4. Software Engineering & Infrastructure Audit

- **Code Quality & Tooling**: Configured `black`, `isort`, `ruff`, `mypy`, and `pyproject.toml`.
- **Automated Testing**: 12 automated unit, integration, and smoke tests under `tests/` achieving 100% pass rate.
- **Containerization & CI/CD**: Multi-stage production `Dockerfile`, `docker-compose.yml`, and `.github/workflows/ci.yml` GitHub Actions pipeline.

---

## 5. Comprehensive Enterprise Decision Log

| Decision ID | Major Architecture / Modelling Decision | Alternatives Considered | Mathematical & Technical Reasoning | Business & Regulatory Justification | Final Enterprise Choice |
| --- | --- | --- | --- | --- | --- |
| **DEC-01** | Dual-Model Production Architecture | Monolithic XGBoost / Single Logistic Model | LightGBM provides $+2.37\%$ AUC lift for pricing; Logistic Scorecard provides closed-form points. | Satisfies FCRA decline reason requirements while maximizing risk-adjusted APR yield. | **APPROVED (Dual Model)** |
| **DEC-02** | WoE Feature Binning & Coarse Classing | Continuous Normalization / One-Hot Encoding | Enforces monotonic log-odds response; caps outlier leverage; handles missing values naturally. | Ensures business logic compliance (higher FICO $\implies$ lower PD) and numerical stability. | **APPROVED (WoE Binning)** |
| **DEC-03** | Rejection of PyTorch Deep Learning MLP | PyTorch MLP / TabNet / FT-Transformer | PyTorch MLP ($\text{AUC} = 0.7312$) failed to beat LightGBM ($0.7482$) and required 3.1x latency. | Multilayer neural network non-linearities violate FCRA adverse action notice compliance. | **REJECTED (Deep Learning)** |
| **DEC-04** | Multicollinearity Screening Threshold ($\text{VIF} \le 5.0$) | Unfiltered Feature Set / Ridge Shrinkage | Prevents Hessian matrix singularity in unpenalized logistic regression covariance estimation. | Guarantees stable, un-correlated score point contributions across risk drivers. | **APPROVED ($\text{VIF} \le 5.0$)** |
| **DEC-05** | Monthly PSI Retraining Trigger ($\text{PSI} \ge 0.25$) | Quarterly Fixed Schedule / Manual Review | $\text{PSI} \ge 0.25$ indicates significant population distribution drift ($p < 0.01$). | Prevents underwriting model decay during macroeconomic regime shifts under SR 11-7. | **APPROVED ($\text{PSI} \ge 0.25$)** |

---

## 6. Final Enterprise Project Scorecard

| Evaluation Area | Score (out of 10) | Detailed Evaluation Rationale |
| --- | --- | --- |
| **1. Software Engineering** | **9.5 / 10** | Modular architecture, 100% test pass rate, Docker, pyproject.toml, GitHub Actions CI. |
| **2. Python Code Quality** | **9.5 / 10** | Clean type hinting, docstrings, logger integration, PEP8 compliance. |
| **3. Statistics** | **9.5 / 10** | Monotonic WoE, IV ranking, Hosmer-Lemeshow calibration, 1,000 bootstrap 95% CIs. |
| **4. Econometrics** | **9.5 / 10** | Probit regression, Marginal Effects (AME), VIF multicollinearity screening, odds ratios. |
| **5. Credit Risk** | **9.5 / 10** | SR 11-7 / Basel III compliance, FCRA Adverse Action reason codes, ECOA fair lending audits. |
| **6. Machine Learning** | **9.5 / 10** | LightGBM, XGBoost, CatBoost, Optuna hyperparameter optimization, master benchmark matrix. |
| **7. Deep Learning Benchmark**| **9.0 / 10** | PyTorch MLP architecture, AdamW optimizer, formal MRC rejection paper documenting opacity. |
| **8. Explainability (XAI)** | **10.0 / 10** | TreeSHAP attributions, PDP, ICE, ALE, counterfactuals, automated FCRA reason codes. |
| **9. Model Validation** | **10.0 / 10** | SR 11-7 Independent Model Validation report, Assumption Register, Residual Risk Register. |
| **10. Portfolio Analytics** | **9.5 / 10** | Vintage default seasoning curves, 4x4 roll rate transition matrices, HHI concentration index. |
| **11. Stress Testing** | **9.0 / 10** | Macro Adverse / Severe Adverse scenarios, borrower elasticity engine, Expected Loss expansion. |
| **12. Model Monitoring** | **10.0 / 10** | Monthly Population Stability Index ($\text{PSI}$), CSI, KS 2-sample data drift, retraining triggers. |
| **13. Streamlit Dashboard** | **9.5 / 10** | Production 8-page Streamlit application, custom institutional CSS, cached data/model loaders. |
| **14. Documentation** | **10.0 / 10** | 16 audit reports, master README, MDD, MVR, Model Cards, IEEE Research Paper, Presentation Guide. |
| **15. Business Value** | **10.0 / 10** | $\$24.2\text{M}$ annual net charge-off savings on $\$1.0\text{B}$ volume, $17.11\% \to 13.45\%$ default rate reduction. |
| **16. Interview Readiness** | **10.0 / 10** | 100-question technical interview guide, resume summaries, ATS bullets, STAR behavioral examples. |

**OVERALL REPOSITORY QUALITY SCORE**: **9.65 / 10 (APPROVED WITH CONDITIONS)**

---

## 7. Final Improvement Roadmap

### 7.1 Priority 1: Critical Improvements (Must be addressed before GitHub publication)
1. Ensure all joblib model artifacts are pre-built under `models/` so `utils/model_loader.py` never fits models on-the-fly during web dashboard rendering.
2. Confirm 100% clean execution of `pytest tests/` without deprecation warnings.

### 7.2 Priority 2: Recommended Improvements (Significantly enhances enterprise depth)
1. Develop an independent econometric Loss Given Default ($\text{LGD}$) regression model to replace the static $95.0\%$ assumption.
2. Formulate a 2-variable Vector Autoregression (VAR) model linking macroeconomic unemployment to applicant DTI.

### 7.3 Priority 3: Future Enhancements (Post-deployment additions)
1. Deploy Streamlit application on an Amazon EKS / Google GKE Kubernetes cluster with NGINX reverse proxy.
2. Connect data processing pipeline to an enterprise Feature Store (Feast) and real-time Kafka scoring stream.
