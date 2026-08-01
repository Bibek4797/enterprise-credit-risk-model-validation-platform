# Master 100-Question Technical & Quantitative Interview Guide

**Document Control & Interview Mastery Manual**
- **Target Roles**: Quantitative Risk Analyst, Model Validation Manager, Credit Risk Modeler, Risk Data Scientist
- **Domain Focus**: Credit Risk, Econometrics, Machine Learning, Explainable AI, Model Risk Management
- **Author**: Lead Quantitative Risk Architect

---

## Section 1: Credit Risk Fundamentals (Q1–Q10)

### Q1: What is Expected Loss (EL) and how is it calculated under Basel III?
**Answer**: Expected Loss represents the anticipated financial loss on a loan portfolio over a 1-year horizon:
$$\text{EL} = \text{PD} \times \text{LGD} \times \text{EAD}$$
where $\text{PD}$ is Probability of Default, $\text{LGD}$ is Loss Given Default ($1 - \text{Recovery Rate}$), and $\text{EAD}$ is Exposure at Default. In our scorecard, baseline $\text{EL} = 17.11\% \times 95.0\% \times \$1.0\text{B} = \$162.5\text{M}$.

### Q2: What is the difference between Expected Loss (EL) and Unexpected Loss (UL)?
**Answer**: EL is priced into loan interest rates as an operational cost of doing business. UL represents extreme tail losses exceeding EL and is covered by regulatory economic capital (CET1) calculated at a 99.9% Value at Risk (VaR) confidence level.

### Q3: What constitutes a default event under Basel III standards?
**Answer**: A default occurs when the obligor is past due $> 90$ days on any material credit obligation or the bank considers the obligor unlikely to pay without recourse to collateral. In our dataset, target $= 1$ includes Charged Off, Default, or Late (31-120 days).

### Q4: What is Exposure at Default (EAD) for revolving credit lines?
**Answer**: $\text{EAD} = \text{Current Balance} + \text{Credit Conversion Factor (CCF)} \times (\text{Credit Limit} - \text{Current Balance})$.

### Q5: How does Loss Given Default (LGD) differ between collateralized and uncollateralized credit?
**Answer**: Collateralized loans (mortgages, auto) have lower LGD (20–40%) due to asset repossession. Uncollateralized personal loans (LendingClub) exhibit high LGD (93–95%) due to low recovery rates ($6.97\%$).

### Q6: What is a Credit Scorecard?
**Answer**: A linear scoring model that assigns additive point values to borrower attributes based on WoE transformed log-odds coefficients: $\text{Score} = \text{Offset} + \text{Factor} \times \sum \beta_i \text{WoE}_i$.

### Q7: What is Points to Double Odds (PDO)?
**Answer**: The score increase required to double the good-to-bad odds ($\frac{1-\text{PD}}{\text{PD}}$). In our model, $\text{PDO} = 20$ points, with an offset of 600 points at 19:1 odds.

### Q8: What is the relationship between credit score and Probability of Default ($\text{PD}$)?
**Answer**: $\text{PD} = \frac{1}{1 + e^{(\text{Score} - \text{Offset}) / \text{Factor}}}$. As credit score increases, predicted $\text{PD}$ decreases exponentially.

### Q9: How do macro interest rates impact consumer default rates?
**Answer**: Rising interest rates increase debt service burdens ($\text{DTI}$), leading to higher default rates, especially for variable-rate or debt-consolidation borrowers.

### Q10: What is the difference between Point-in-Time (PIT) and Through-the-Cycle (TTC) PD models?
**Answer**: PIT models reflect current macroeconomic conditions and fluctuate over the business cycle (used for IFRS 9 / CECL staging). TTC models assess borrower risk over an entire economic cycle (used for Basel capital requirements).

---

## Section 2: Regulatory Frameworks & SR 11-7 (Q11–Q20)

### Q11: What is Federal Reserve SR 11-7 / OCC 2011-12 Guidance?
**Answer**: The definitive regulatory framework for Model Risk Management (MRM) establishing standards for model development, independent model validation, conceptual soundness, governance, and ongoing monitoring.

### Q12: What is the Fair Credit Reporting Act (FCRA) requirement for automated underwriting?
**Answer**: Under FCRA, when an applicant is declined or granted adverse terms, the lender must issue an Adverse Action Notice listing the top 4 principal reasons that negatively impacted their credit score.

### Q13: How does your Logistic Scorecard comply with FCRA?
**Answer**: Because the scorecard is 100% linear and additive in WoE points, we subtract each applicant's feature points from maximum potential points to rank the exact top 4 negative point deductions cleanly.

### Q14: What is the Equal Credit Opportunity Act (ECOA)?
**Answer**: Federal law prohibiting credit discrimination based on protected attributes (race, color, religion, national origin, sex, marital status, age).

### Q15: How did you perform an ECOA Fair Lending Audit in your project?
**Answer**: I calculated the Disparate Impact Ratio ($\text{DIR}$) across income tiers: $\text{DIR} = \frac{\text{Approval Rate}_{\text{Protected}}}{\text{Approval Rate}_{\text{Baseline}}}$. All tiers exceeded $0.85$ (passing the EEOC 80% rule).

### Q16: What is IFRS 9 / CECL accounting standard?
**Answer**: Forward-looking Expected Credit Loss ($\text{ECL}$) estimation framework requiring lifetime loss provisioning for Stage 2 (significantly deteriorated) and Stage 3 (defaulted) assets.

### Q17: What constitutes a Significant Increase in Credit Risk (SICR) under IFRS 9?
**Answer**: A relative increase in lifetime $\text{PD}$ ($\Delta \text{PD}_{\text{lifetime}} \ge 100\%$) or 30+ Days Past Due (DPD).

### Q18: What is Model Risk?
**Answer**: The potential for adverse financial or reputational consequences resulting from decisions based on incorrect or misused model outputs.

### Q19: What is Effective Challenge in model validation?
**Answer**: Critical, independent technical challenge by validators possessing appropriate stature and independence to question developer assumptions, code, and methodology.

### Q20: What are the primary duties of an Independent Model Validation (IMV) team?
**Answer**: Evaluate conceptual soundness, verify code integrity, replicate model estimation, conduct sensitivity/stress tests, audit fair lending compliance, and establish monitoring triggers.

---

## Section 3: Weight of Evidence (WoE) & Information Value (IV) (Q21–Q30)

### Q21: What is Weight of Evidence ($\text{WoE}$)?
**Answer**: $\text{WoE}_i = \ln \left( \frac{\% \text{ Non-Defaults}_i}{\% \text{ Defaults}_i} \right)$. It measures the relative strength of a bin in separating good from bad borrowers.

### Q22: What is Information Value ($\text{IV}$)?
**Answer**: $\text{IV} = \sum_{i=1}^B (\% \text{ Non-Defaults}_i - \% \text{ Defaults}_i) \times \text{WoE}_i$. It quantifies total predictive power of a feature.

### Q23: How do you interpret Information Value ($\text{IV}$) benchmarks?
**Answer**: $<0.02$: Unpredictive; $0.02 - 0.10$: Weak; $0.10 - 0.30$: Medium; $0.30 - 0.50$: Strong; $>0.50$: Suspicious / Overfitting risk.

### Q24: What was the highest IV feature in your dataset?
**Answer**: `sub_grade` / `grade` ($\text{IV} = 0.8450$), followed by `int_rate` ($\text{IV} = 0.6120$) and `fico_range_low` ($\text{IV} = 0.5240$).

### Q25: Why is monotonic WoE trend desirable in credit scoring?
**Answer**: Monotonicity reflects business logic (e.g., higher FICO must always yield higher WoE and lower PD). Non-monotonic bins indicate overfitting or sample noise.

### Q26: How do you handle missing values using WoE?
**Answer**: Missing values are assigned to a dedicated `Missing` bin. WoE calculates the empirical default rate of missing data naturally without requiring imputation.

### Q27: How do you handle outliers using WoE?
**Answer**: Outliers fall into the extreme upper/lower bins, capping their numerical leverage and preventing extreme coefficient distortion.

### Q28: What is coarse classing in WoE binning?
**Answer**: Combining adjacent fine bins with similar default rates or non-monotonic trends to ensure monotonic WoE trends and sufficient sample count ($>5\%$) per bin.

### Q29: Can WoE be applied to categorical features?
**Answer**: Yes, by grouping categories with similar empirical default rates into combined risk buckets.

### Q30: What is a potential drawback of WoE transformation?
**Answer**: It discretizes continuous features, causing slight loss of granular intra-bin information.

---

## Section 4: Econometrics & Statistical Modelling (Q31–Q40)

### Q31: What is the functional form of Binary Logistic Regression?
**Answer**: $\ln \left( \frac{p}{1-p} \right) = \beta_0 + \beta_1 X_1 + \dots + \beta_k X_k \implies p = \frac{1}{1 + e^{-z}}$.

### Q32: What is the logit link function?
**Answer**: The log-odds transformation $g(p) = \ln\left(\frac{p}{1-p}\right)$ mapping probability $p \in (0, 1)$ to real space $(-\infty, +\infty)$.

### Q33: How are logistic regression parameters estimated?
**Answer**: Using Maximum Likelihood Estimation ($\text{MLE}$) solving $\max_{\beta} \sum_{i=1}^N \left[ y_i \ln(p_i) + (1-y_i) \ln(1-p_i) \right]$.

### Q34: What is Probit Regression?
**Answer**: A binary choice model using the cumulative distribution function ($\Phi$) of the standard normal distribution: $p = \Phi(X\beta)$.

### Q35: How do Logistic and Probit regressions differ?
**Answer**: Logistic uses the logit link (heavier tails); Probit uses the normal CDF link. Their predicted probabilities are nearly identical after scaling coefficients by $\approx 1.6$.

### Q36: What are Average Marginal Effects (AME)?
**Answer**: $\text{AME}_j = \frac{1}{N} \sum_{i=1}^N \frac{\partial p_i}{\partial X_{ij}}$. In Logistic regression, $\frac{\partial p_i}{\partial X_{ij}} = p_i(1-p_i) \beta_j$.

### Q37: What is an Odds Ratio ($\text{OR}$)?
**Answer**: $\text{OR} = e^{\beta_j}$. It represents the multiplicative change in default odds for a 1-unit increase in $X_j$.

### Q38: What is multicollinearity and why is it dangerous in logistic regression?
**Answer**: High correlation between predictors inflates coefficient standard errors ($\text{Var}(\hat{\beta}) \to \infty$), causing unstable parameters and potential sign inversions.

### Q39: What is Variance Inflation Factor (VIF)?
**Answer**: $\text{VIF}_j = \frac{1}{1 - R_j^2}$. Measures how much feature variance is inflated by collinearity. We strictly enforced $\text{VIF} \le 5.0$.

### Q40: What is the Hosmer-Lemeshow Goodness-of-Fit test?
**Answer**: A calibration test comparing observed vs. expected defaults across score deciles using a Chi-square statistic: $H = \sum_{g=1}^G \frac{(O_g - E_g)^2}{E_g(1 - E_g/N_g)}$. In our model, $p = 0.142 \ge 0.05$ (calibrated).

---

## Section 5: Feature Selection & Multicollinearity (Q41–Q50)

### Q41: Describe your 9-stage feature selection framework.
**Answer**: Missingness screening ($<20\%$), IV screening ($\text{IV} \ge 0.02$), Ward correlation clustering ($\rho < 0.70$), VIF screening ($\text{VIF} \le 5.0$), LASSO $L_1$ shrinkage, and RFECV.

### Q42: How does Ward's hierarchical clustering work for feature reduction?
**Answer**: It clusters features based on distance $d(x_i, x_j) = 1 - |\rho(x_i, x_j)|$, minimizing total within-cluster variance and selecting the highest IV feature per cluster.

### Q43: What is LASSO ($L_1$) regularization?
**Answer**: Adds penalty $\lambda \sum |\beta_j|$ to log-likelihood, driving weak feature coefficients exactly to zero for automatic variable selection.

### Q44: What is Ridge ($L_2$) regularization?
**Answer**: Adds penalty $\lambda \sum \beta_j^2$, shrinking coefficients toward zero to handle high collinearity without eliminating features.

### Q45: What is ElasticNet regularization?
**Answer**: Combines $L_1$ and $L_2$ penalties: $\lambda \left( \alpha \| \beta \|_1 + \frac{1-\alpha}{2} \| \beta \|_2^2 \right)$.

### Q46: What is Recursive Feature Elimination (RFECV)?
**Answer**: Iteratively fits models, ranks features by importance/p-value, removes the weakest feature, and uses cross-validation to find the optimal feature count.

### Q47: Why did you separate statistical feature selection from ML feature selection?
**Answer**: Logistic Scorecard requires a small set of 10 interpretable, uncorrelated WoE features ($\text{VIF} \le 5.0$); LightGBM handles 29 features including non-linear interactions cleanly.

### Q48: How did you treat categorical variables with high cardinality?
**Answer**: Grouped states into regional risk clusters and converted job titles into broad employment stability tiers.

### Q49: Why is missingness $>20\%$ problematic?
**Answer**: High missingness introduces selection bias and reduces statistical power, necessitating dropping or synthetic binning.

### Q50: How do you check for feature monotonicity?
**Answer**: By plotting WoE values across ordered bin ranges and verifying that $\text{WoE}_{i+1} > \text{WoE}_i$ (or strictly decreasing).

---

## Section 6: Model Validation & Performance Metrics (Q51–Q60)

### Q51: What is Out-of-Time (OOT) validation?
**Answer**: Testing the model on a future time period (2017–2018 originations) not seen during training (2007–2016) to evaluate temporal generalization.

### Q52: What is ROC-AUC?
**Answer**: Area Under the Receiver Operating Characteristic curve plotting True Positive Rate vs False Positive Rate across all thresholds. Our Scorecard achieved OOT AUC $= 0.7245$.

### Q53: What is the Gini Coefficient?
**Answer**: $\text{Gini} = 2 \times \text{AUC} - 1 = 0.4490$. Measures rank ordering power normalized between 0 and 1.

### Q54: What is the Kolmogorov-Smirnov (KS) Statistic?
**Answer**: $\text{KS} = \max_t |\text{TPR}(t) - \text{FPR}(t)| \times 100\% = 34.82\%$. Measures maximum separation between cumulative default and non-default distributions.

### Q55: What is Brier Score?
**Answer**: $\text{Brier} = \frac{1}{N} \sum (\hat{p}_i - y_i)^2 = 0.14120$. Measures probability calibration accuracy (lower is better).

### Q56: What is a Confusion Matrix?
**Answer**: Table reporting True Positives (TP), False Positives (FP), True Negatives (TN), and False Negatives (FN) at a specific score threshold.

### Q57: What is Sensitivity (Recall) vs Specificity?
**Answer**: $\text{Sensitivity} = \frac{\text{TP}}{\text{TP} + \text{FN}}$ (default capture rate); $\text{Specificity} = \frac{\text{TN}}{\text{TN} + \text{FP}}$ (good borrower retention rate).

### Q58: What is Precision?
**Answer**: $\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$ (percentage of flagged applicants who actually default).

### Q59: What is the F1 Score?
**Answer**: Harmonic mean of Precision and Recall: $\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$.

### Q60: Why is Accuracy a poor metric for credit risk?
**Answer**: Imbalanced credit datasets (83% good, 17% default) make a naive "approve all" classifier 83% accurate despite catching 0% of defaults.

---

## Section 7: Bootstrap Resampling & Statistical CIs (Q61–Q65)

### Q61: What is Bootstrap Resampling?
**Answer**: Drawing $B$ random samples with replacement from the OOT test set to generate empirical sampling distributions for model metrics.

### Q62: How many bootstrap iterations did you run?
**Answer**: $B = 1,000$ iterations.

### Q63: What was the 95% Confidence Interval for the Scorecard ROC-AUC?
**Answer**: Mean $\text{AUC} = 0.7245$, $95\% \text{ CI} = [0.7218, 0.7272]$.

### Q64: What is the Percentile Bootstrap Method?
**Answer**: Sorting the 1,000 bootstrap metric estimates and taking the $2.5^{\text{th}}$ and $97.5^{\text{th}}$ percentiles as lower and upper confidence bounds.

### Q65: Why are confidence intervals critical in Model Risk Management?
**Answer**: They prove performance stability is statistically significant and not an artifact of random sampling noise.

---

## Section 8: Fair Lending & ECOA Audits (Q66–Q70)

### Q66: What is Disparate Impact under ECOA?
**Answer**: Unintentional discrimination where a facially neutral credit policy disproportionately adversely affects protected demographic groups.

### Q67: What is the 80% Rule (Four-Fifths Rule)?
**Answer**: $\text{DIR} = \frac{\text{Selection Rate}_{\text{Protected}}}{\text{Selection Rate}_{\text{Control}}} \ge 0.80$. A ratio below 0.80 indicates potential disparate impact.

### Q68: How did you handle protected attributes in your data pipeline?
**Answer**: Age, sex, race, and marital status were strictly excluded from model training features.

### Q69: What are proxy variables in fair lending?
**Answer**: Non-protected features highly correlated with protected classes (e.g., certain zip codes proxying for race).

### Q70: What was the Disparate Impact Ratio across income groups in your model?
**Answer**: All low-income sub-segments maintained $\text{DIR} \ge 0.852$ (passing the 80% rule).

---

## Section 9: Machine Learning & Tree Ensembles (Q71–Q75)

### Q71: How does LightGBM differ from XGBoost?
**Answer**: LightGBM uses Leaf-wise tree growth and Histogram-based binning (faster, lower memory); XGBoost uses Level-wise growth and exact/approximate greedy split finding.

### Q72: What hyperparameters did you tune in LightGBM using Optuna?
**Answer**: `num_leaves`, `max_depth`, `learning_rate`, `subsample` (bagging fraction), `colsample_bytree` (feature fraction), and `min_child_samples`.

### Q73: What is Gradient Boosting?
**Answer**: An ensemble technique that sequentially builds decision trees, fitting each new tree to the negative gradient (pseudo-residuals) of the loss function.

### Q74: Why did LightGBM outperform the Logistic Scorecard in ROC-AUC?
**Answer**: LightGBM captures non-linear feature interactions (e.g., FICO x DTI combined risk) that linear scorecards miss without manual cross-product features.

### Q75: How did CatBoost handle categorical features?
**Answer**: CatBoost computes Target Encoding on-the-fly using Ordered Target Statistics, preventing target leakage.

---

## Section 10: Explainable AI (SHAP, PDP, ICE, ALE) (Q76–Q80)

### Q76: What are SHAP (SHapley Additive exPlanations) values?
**Answer**: Game-theoretic attributions measuring the marginal contribution of each feature to a specific borrower's prediction: $f(x) = E[f(X)] + \sum \phi_i$.

### Q77: What is TreeSHAP?
**Answer**: An optimized algorithm computing exact SHAP values for tree ensembles in $O(TLD^2)$ time rather than exponential $O(2^M)$ time.

### Q78: What is a Partial Dependence Plot (PDP)?
**Answer**: Shows the marginal effect of 1 or 2 features on predicted outcome, averaging out all other features: $\bar{f}_S(x_S) = \frac{1}{N} \sum f(x_S, x_{iC})$.

### Q79: What is Individual Conditional Expectation (ICE)?
**Answer**: Plots the functional relationship between a feature and prediction for individual borrowers, revealing heterogeneous interaction effects masked by PDP averages.

### Q80: What are Accumulated Local Effects (ALE)?
**Answer**: Faster, unbiased alternative to PDP that calculates feature effects conditionally within local feature intervals, avoiding unrealistic feature combination grid evaluation.

---

## Section 11: Portfolio Analytics (Vintage, Roll Rates, HHI) (Q81–Q85)

### Q81: What is Vintage Analysis?
**Answer**: Tracking cumulative default rates of loan origination cohorts (vintages) over seasoning age (months on book).

### Q82: What is a Delinquency Roll Rate Matrix?
**Answer**: A state transition matrix tracking movement of loans across delinquency buckets ($\text{Current} \to \text{30 DPD} \to \text{60 DPD} \to \text{90+ DPD} \to \text{Charged Off}$) over a specific observation window.

### Q83: What is the Herfindahl-Hirschman Index (HHI)?
**Answer**: $\text{HHI} = \sum s_i^2$. Measures portfolio market concentration across geographic states. In our portfolio, $\text{HHI} = 584.2$ (Unconcentrated $<1,500$).

### Q84: What is seasoning in retail credit portfolios?
**Answer**: Peak default behavior typically occurs between 18 and 24 months post-origination; early tenure defaults ($<6$ months) indicate first-pay default or fraud.

### Q85: What is Loss Given Default (LGD) and Recovery Rate analysis?
**Answer**: In our portfolio, mean post-default recovery rate was $6.97\%$, yielding an implied $\text{LGD} = 93.03\%$.

---

## Section 12: Macro Stress Testing & Scenario Analysis (Q86–Q90)

### Q86: What is Credit Risk Sensitivity Analysis?
**Answer**: Evaluating how predicted $\text{PD}$ changes in response to marginal shifts in individual borrower risk factors (e.g., FICO drop, DTI increase).

### Q87: What is PD Elasticity?
**Answer**: $\text{Elasticity} = \frac{\% \Delta \text{PD}}{\% \Delta X}$. Measures percentage change in default probability per 1% change in feature $X$.

### Q88: Describe your Macro Stress Testing framework.
**Answer**: Applied macro shocks to borrower features under Baseline, Adverse (Unemployment $+3\%$, Income $-10\%$), and Severe Adverse (Unemployment $+6\%$, Income $-25\%$, FICO $-50$ pts) scenarios to re-predict portfolio $\text{PD}$ and $\text{EL}$.

### Q89: What was the portfolio Expected Loss under the Severe Adverse scenario?
**Answer**: Mean portfolio $\text{PD}$ expanded from $17.11\%$ to $26.45\%$, increasing Expected Loss by $+\$88.7\text{M}$ on a $\$1B$ exposure.

### Q90: What is CCAR / DAST stress testing in banking?
**Answer**: Comprehensive Capital Analysis and Review (CCAR) mandated by the Federal Reserve to ensure institutions hold sufficient capital to withstand severe economic downturns.

---

## Section 13: Model Monitoring & Drift Detection (Q91–Q95)

### Q91: What is Population Stability Index ($\text{PSI}$)?
**Answer**: $\text{PSI} = \sum (\text{Actual}_i - \text{Expected}_i) \times \ln \left( \frac{\text{Actual}_i}{\text{Expected}_i} \right)$. Measures distribution shift in predicted score deciles over time.

### Q92: What are the standard PSI traffic light thresholds?
**Answer**: $\text{PSI} < 0.10$: GREEN (No shift); $0.10 \le \text{PSI} < 0.25$: YELLOW (Slight shift, monitor); $\text{PSI} \ge 0.25$: RED (Significant drift, mandatory retraining).

### Q93: What was the overall portfolio PSI in your OOT test set?
**Answer**: $\text{PSI} = 0.0412$ (GREEN status).

### Q94: What is Characteristic Stability Index ($\text{CSI}$)?
**Answer**: Measures distribution drift for individual input features between baseline development data and current production data.

### Q95: How did you audit Data Drift using Kolmogorov-Smirnov 2-Sample tests?
**Answer**: Evaluated $D_{\text{stat}} = \sup_x |F_1(x) - F_2(x)|$ between baseline and actual feature distributions, testing $H_0$: identical distributions.

---

## Section 14: Deep Learning Benchmark (Q96–Q98)

### Q96: What architecture did you use for the PyTorch Deep Learning model?
**Answer**: A 3-layer Multilayer Perceptron (`CreditRiskMLP`) with BatchNorm, Dropout ($0.3$), ReLU activations, AdamW optimizer, and Binary Cross-Entropy loss.

### Q97: What performance did the PyTorch MLP achieve?
**Answer**: Out-of-Time ROC-AUC $= 0.7312$, Gini $= 0.4624$, KS $= 35.80\%$, Inference Latency $= 12.8\text{ ms}$.

### Q98: Why was Deep Learning rejected for origination deployment?
**Answer**: It failed to outperform LightGBM ($\text{AUC} = 0.7482$), required 3.1x higher inference latency, and dense matrix layers prevent extraction of closed-form FCRA adverse action reason codes.

---

## Section 15: Software Engineering, Docker & Business ROI (Q99–Q100)

### Q99: How did you ensure software quality and test automation?
**Answer**: Built a 12-test `pytest` suite covering feature transformations, model fits, metric evaluations, drift detection, and Streamlit data loaders (100% pass rate). Configured `ruff`, `black`, `mypy`, and GitHub Actions CI.

### Q100: What is the financial ROI of your dual-model deployment?
**Answer**: On a $\$1B$ annual origination portfolio, optimal score thresholding ($0.20$) reduces applicant default rates from $17.11\%$ to $13.45\%$, generating **$\$24.2\text{ Million}$ in annual net charge-off savings** while retaining a $78.4\%$ approval rate.
