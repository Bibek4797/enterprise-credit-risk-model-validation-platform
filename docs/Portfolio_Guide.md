# Portfolio Storytelling & Walkthrough Guide

**Document Control & Technical Communication**
- **System Scope**: Storytelling Scripts, Walkthrough Guides & Executive Briefings
- **Target Audience**: Technical Recruiters, Hiring Managers, Senior Quants, Model Validation Managers
- **Author**: Lead Quantitative Risk Architect

---

## 1. Project Story Scripts

### 1.1 30-Second Elevator Pitch
> "I built an enterprise credit risk modeling and validation platform on 1.37 million LendingClub records. To balance regulatory compliance under Federal Reserve SR 11-7 with predictive power, I engineered a dual-model framework: a Logistic Scorecard for FCRA-compliant automated underwriting and a LightGBM engine for risk-based pricing. I executed 1,000 bootstrap validation trials, SHAP explainability, macro stress testing, and real-time PSI drift monitoring, saving \$24.2M annually on a \$1B portfolio."

### 1.2 1-Minute Elevator Pitch
> "In consumer credit underwriting, banks must comply with FCRA adverse action rules while maximizing portfolio profitability. I built an end-to-end credit risk modeling platform trained on 1.37 million LendingClub loans. My champion Logistic Scorecard achieves a 0.7245 OOT ROC-AUC and 34.82% KS statistic, converting into closed-form score points for instant decline reason code generation. My challenger LightGBM model delivers a 0.7482 ROC-AUC—a 2.37% lift for risk pricing. I independently validated the models using 1,000 bootstrap trials, ECOA fair lending audits ($\text{DIR} \ge 0.85$), and benchmarked a PyTorch Deep Learning MLP, formally documenting why neural networks were rejected for origination. I containerized the system with Docker, wrote a 12-test pytest suite, and built an 8-page Streamlit analytics dashboard."

---

## 2. Technical, Business, and Executive Walkthroughs

### 2.1 Technical Walkthrough (Software & Quant Engineers)
- **Data Engineering**: Processed 1.37M binary records using memory-optimized chunking. Engineered WoE/IV coarse classing across 10 risk drivers.
- **Feature Selection**: Executed 9-stage screening (missingness $<20\%$, $\text{IV} \ge 0.02$, Ward clustering $\rho < 0.70$, $\text{VIF} \le 5.0$, LASSO, RFECV).
- **Model Estimation**: Fitted Logistic Regression, Probit, LASSO/Ridge, Random Forest, XGBoost, LightGBM, CatBoost, and PyTorch MLP.
- **Validation & XAI**: Calculated 1,000 bootstrap 95% CIs, Hosmer-Lemeshow calibration ($p = 0.142$), TreeSHAP attributions, PDP, ICE, and ALE curves.
- **Monitoring & CI/CD**: Built monthly $\text{PSI}$ / $\text{CSI}$ tracking with automated retraining triggers ($\text{PSI} \ge 0.25$), containerized with Docker, and automated CI testing via GitHub Actions.

### 2.2 Business & Executive Walkthrough (Risk Committee & C-Suite)
- **Problem**: Balancing underwriting regulatory compliance with credit loss minimization.
- **Solution**: Dual-model architecture separating origination decisioning from risk-based pricing.
- **Financial Return**: On a \$1B portfolio, reduces default rates from $17.11\%$ to $13.45\%$ while preserving a $78.4\%$ approval yield, generating **\$24.2M in annual net charge-off savings**.
