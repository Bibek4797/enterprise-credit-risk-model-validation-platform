# Quantitative & Risk Analyst Resume Packaging Guide

**Document Control & Career Acceleration**
- **Target Roles**: Quantitative Risk Analyst, Model Validation Manager, Credit Risk Modeler, Risk Data Scientist
- **Domain Focus**: Consumer Credit Risk, Basel III, SR 11-7, Machine Learning & Explainable AI
- **Author**: Lead Quantitative Risk Architect

---

## 1. One-Line Resume Descriptions

- **Option A (Quantitative/Model Risk)**: Developed and validated an SR 11-7 compliant Credit Risk PD platform on 1.37M LendingClub records, deploying a Logistic Scorecard ($\text{AUC} = 0.7245$, $\text{KS} = 34.82\%$) for FCRA origination and a LightGBM engine ($\text{AUC} = 0.7482$) for risk pricing, achieving $\$24.2\text{M}$ in annual net charge-off savings.
- **Option B (Data Science/ML)**: Built a production credit analytics platform featuring dual Scorecard/LightGBM models, 1,000 bootstrap validation trials, SHAP explainability, macro stress testing, and real-time PSI/CSI drift monitoring in a multi-page Streamlit application.

---

## 2. ATS-Friendly Project Summary Bullets

- Built an enterprise Credit Risk Probability of Default ($\text{PD}$) platform on $1.37\text{M}$ mature LendingClub consumer loan records (2007–2018).
- Implemented a dual-model framework: an **Unpenalized Logistic Scorecard** (`PD-SCORECARD-2026-V1`, OOT AUC $0.7245$, KS $34.82\%$) for FCRA-compliant automated underwriting and a **LightGBM Classifier** (`PD-LIGHTGBM-2026-CHALLENGER`, OOT AUC $0.7482$, KS $38.42\%$) for risk-based pricing.
- Conducted 9-stage feature selection (WoE/IV, Ward correlation clustering $\rho < 0.70$, VIF $\le 5.0$, LASSO, RFECV), screening 100+ raw variables into 10 monotonic WoE risk drivers.
- Executed Independent Model Validation (SR 11-7) including 1,000 bootstrap 95% confidence intervals, ECOA fair lending audit ($\text{DIR} \ge 0.85$), and Hosmer-Lemeshow calibration tests ($p = 0.142$).
- Implemented global/local Explainable AI (TreeSHAP attributions, PDP, ICE, counterfactuals) with automated FCRA Adverse Action reason code generation.
- Formulated enterprise portfolio analytics (vintage default seasoning curves, 4x4 roll rate matrices, HHI index $= 584.2$) and macro stress testing engines ($\Delta \text{EL}$ expansion under adverse scenarios).
- Built automated drift monitoring tracking Population Stability Index ($\text{PSI}$), Characteristic Stability Index ($\text{CSI}$), and KS 2-sample tests with automated retraining triggers.
- Benchmarked PyTorch Deep Learning MLPs ($\text{AUC} = 0.7312$), establishing a formal governance decision to reject neural networks for origination due to opacity and sub-optimal discrimination.
- Containerized full solution using Docker / Docker Compose and deployed an 8-page Streamlit analytics dashboard backed by a 12-test pytest suite (100% pass rate).

---

## 3. Technology Stack & Business Impact Summaries

### Technical Stack Summary
`Python 3.11`, `Streamlit`, `LightGBM`, `PyTorch`, `Scikit-Learn`, `Statsmodels`, `SHAP`, `Plotly`, `Pytest`, `Docker`, `Docker Compose`, `Git`, `GitHub Actions CI/CD`.

### Financial & Business Impact
- **Annual Credit Loss Savings**: $\$24.2\text{ Million}$ saved annually on a $\$1.0\text{ Billion}$ origination portfolio.
- **Default Rate Reduction**: Reduced approved applicant default rate from $17.11\%$ to $13.45\%$ at an optimal $0.20$ score cutoff.
- **Approval Yield**: Maintained a high $78.4\%$ application approval rate while pruning high-risk tail borrowers.
