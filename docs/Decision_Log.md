# Master Enterprise Decision Log

**Document Control & Architecture Governance**
- **System Scope**: Master Repository Decision Log for Credit Risk Analytics Platform
- **Target Audience**: Model Risk Committee (MRC), Independent Model Validators, Enterprise Architects
- **Author**: Quantitative Risk Analytics & Model Governance Team

---

## 1. Executive Overview

This document records the master **Enterprise Decision Log**, capturing the mathematical, statistical, business, and regulatory rationale behind every major architectural and modeling decision executed across the 19 phases of development.

Adhering to **Federal Reserve SR 11-7** guidelines, each decision includes a clear statement of the choice made, alternatives considered, technical reasoning, statistical justification, business impact, and regulatory compliance implication.

---

## 2. Master Decision Register

### DEC-01: Dual-Model Production Architecture
- **Decision**: Deploy an Unpenalized Logistic Scorecard (`PD-SCORECARD-2026-V1`) for primary credit origination underwriting and a LightGBM Classifier (`PD-LIGHTGBM-2026-CHALLENGER`) for risk-based pricing optimization.
- **Alternatives Considered**: 
  1. Monolithic XGBoost model for all underwriting and pricing.
  2. Single Logistic Scorecard for both underwriting and pricing.
- **Statistical Justification**: LightGBM achieves an Out-of-Time ROC-AUC of $0.7482$ (+2.37% lift over Scorecard $0.7245$) and a KS statistic of $38.42\%$ (vs $34.82\%$).
- **Business Justification**: Maximizes risk-adjusted net interest margin by pricing high-exposure applicants accurately while maintaining high approval yield ($78.4\%$).
- **Regulatory Implication**: FCRA mandates closed-form score point additivity for decline reason codes. The scorecard guarantees 100% compliance for origination, while LightGBM runs internally for pricing.
- **Final Choice**: **APPROVED (Dual-Model Architecture)**.

---

### DEC-02: Weight of Evidence (WoE) Feature Binning
- **Decision**: Transform continuous numerical risk drivers into Weight of Evidence ($\text{WoE}$) binned categories.
- **Alternatives Considered**: 
  1. Standard Min-Max / Z-score normalization.
  2. One-hot encoding of raw quantiles.
- **Statistical Justification**: WoE maps non-linear feature relationships into continuous linear log-odds space ($\ln(\text{Good}/\text{Bad})$), ensuring monotonic log-odds response and eliminating outlier leverage.
- **Business Justification**: Guarantees business logic compliance (higher FICO score must always yield higher score points and lower predicted $\text{PD}$).
- **Regulatory Implication**: WoE coefficients map directly into closed-form score points ($\text{Score} = \text{Offset} + \text{Factor} \times \text{WoE}$), enabling transparent score card points tables.
- **Final Choice**: **APPROVED (WoE Binning)**.

---

### DEC-03: Rejection of PyTorch Deep Learning MLP for Origination
- **Decision**: Formally reject PyTorch Multilayer Perceptrons (`PD-MLP-2026-BENCHMARK`) for production credit origination.
- **Alternatives Considered**: 
  1. Replacing Logistic Scorecard with PyTorch MLP.
  2. Deploying TabNet / FT-Transformer for origination.
- **Statistical Justification**: PyTorch MLP achieved an OOT ROC-AUC of $0.7312$—failing to surpass LightGBM ($0.7482$) while requiring 3.1x higher inference latency ($12.8\text{ ms}$ vs $4.1\text{ ms}$).
- **Business Justification**: Increases operational computational costs without improving credit loss reduction.
- **Regulatory Implication**: Dense multi-layer neural network weight matrices violate FCRA adverse action notice guidelines.
- **Final Choice**: **REJECTED (Archived as Independent Benchmark)**.

---

### DEC-04: Multicollinearity Screening Threshold ($\text{VIF} \le 5.0$)
- **Decision**: Enforce a strict Variance Inflation Factor limit of $\text{VIF} \le 5.0$ and Spearman correlation limit of $\rho < 0.70$ during feature selection.
- **Alternatives Considered**: 
  1. Allowing correlated features and using Ridge ($L_2$) penalty.
  2. Relaxing VIF threshold to $10.0$.
- **Statistical Justification**: Prevents covariance matrix ill-conditioning and Hessian matrix singularity in maximum likelihood estimation.
- **Business Justification**: Ensures un-correlated, stable score point contributions across individual risk drivers.
- **Regulatory Implication**: Prevents sign inversions (e.g., negative coefficient on FICO score) that would undermine model credibility during audit.
- **Final Choice**: **APPROVED ($\text{VIF} \le 5.0$)**.

---

### DEC-05: Monthly PSI Monitoring & Retraining Triggers
- **Decision**: Implement monthly Population Stability Index ($\text{PSI}$) tracking with a mandatory retraining trigger at $\text{PSI} \ge 0.25$.
- **Alternatives Considered**: 
  1. Fixed calendar-based semi-annual retraining.
  2. Ad-hoc retraining upon business request.
- **Statistical Justification**: $\text{PSI} \ge 0.25$ indicates significant population distribution drift ($p < 0.01$) relative to baseline development data.
- **Business Justification**: Prevents silent underwriting model decay during macroeconomic regime shifts.
- **Regulatory Implication**: Direct compliance with SR 11-7 ongoing monitoring directives.
- **Final Choice**: **APPROVED ($\text{PSI} \ge 0.25$ Trigger)**.
