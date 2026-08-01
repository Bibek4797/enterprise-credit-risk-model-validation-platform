# 15-Slide Executive Pitch Deck Guide & Speaker Notes

**Document Control & C-Suite Presentation Deck**
- **System Scope**: Executive Presentation Deck, Speaker Notes & Visual Layout
- **Target Audience**: Model Risk Committee (MRC), Chief Risk Officer (CRO), Technical Evaluators
- **Author**: Lead Quantitative Risk Architect

---

## 1. 15-Slide Pitch Deck Structure & Speaker Notes

### Slide 1: Title Slide
- **Visual**: Institutional dark blue layout, project title, author, date.
- **Content**: *Enterprise Credit Risk Modelling, Independent Model Validation & XAI Platform*.
- **Speaker Note**: "Welcome. Today I present our enterprise credit risk platform engineered on 1.37 million LendingClub origination records."

### Slide 2: Executive Summary & Financial ROI
- **Visual**: KPI cards showing $\$24.2\text{M}$ savings, $13.45\%$ default rate, $78.4\%$ approval rate.
- **Speaker Note**: "Our dual-model system saves \$24.2M annually in avoided net charge-offs on a \$1B portfolio."

### Slide 3: The Retail Banking Compliance Challenge
- **Visual**: Balance scale graphic (Regulatory Compliance vs Predictive Accuracy).
- **Speaker Note**: "Banks face a core trade-off: FCRA adverse action rules mandate linear interpretability, while ML maximizes pricing precision."

### Slide 4: Dual-Model Solution Architecture
- **Visual**: Architecture flowchart (Underwriting Champion Scorecard vs Pricing Challenger LightGBM).
- **Speaker Note**: "We solve this with a dual-model framework: Scorecard for automated origination, LightGBM for risk-based pricing."

### Slide 5: Dataset & Out-Of-Time (OOT) Split
- **Visual**: Data timeline graphic (2007–2016 Dev vs 2017–2018 OOT Test).
- **Speaker Note**: "We trained on 875k records and validated out-of-time on 495k mature 2017–2018 loans."

### Slide 6: Multi-Stage Feature Selection Framework
- **Visual**: Funnel diagram (100+ variables $\to$ WoE/IV $\to$ Clustering $\to$ VIF $\to$ 10 Scorecard features).
- **Speaker Note**: "Our 9-stage screening eliminated collinearity ($\text{VIF} \le 5.0$), ensuring stable WoE parameters."

### Slide 7: Champion Scorecard Performance & Scaling
- **Visual**: ROC curve ($\text{AUC} = 0.7245$) and score distribution histogram ($\text{KS} = 34.82\%$).
- **Speaker Note**: "Our Unpenalized Scorecard delivers strong separation and scales to 600 points at 19:1 odds."

### Slide 8: Challenger LightGBM & Machine Learning Benchmarks
- **Visual**: Model comparison bar chart (Scorecard vs LightGBM vs XGBoost vs CatBoost).
- **Speaker Note**: "LightGBM achieved an OOT ROC-AUC of 0.7482—a +2.37% lift over the scorecard."

### Slide 9: Rejection of PyTorch Deep Learning
- **Visual**: Triangulation matrix highlighting Deep Learning sub-optimality ($\text{AUC} = 0.7312$, 12.8 ms latency).
- **Speaker Note**: "We formally rejected Deep Learning: it failed to beat LightGBM and introduces black-box opacity."

### Slide 10: Independent Model Validation (SR 11-7) & ECOA
- **Visual**: 1,000 Bootstrap distribution curve & ECOA Fair Lending bar chart ($\text{DIR} \ge 0.85$).
- **Speaker Note**: "1,000 bootstrap trials confirmed 95% CI stability, and ECOA tests cleared fair lending."

### Slide 11: Explainable AI & FCRA Adverse Action Generation
- **Visual**: SHAP summary plot & local borrower waterfall attribution card.
- **Speaker Note**: "Our SHAP engine extracts top 4 adverse action reason codes for instant FCRA compliance."

### Slide 12: Portfolio Analytics & Vintage Seasoning
- **Visual**: Vintage default seasoning curves & 4x4 roll rate transition matrix.
- **Speaker Note**: "Vintage seasoning curves confirm default stabilization; HHI index ($584.2$) shows low state concentration."

### Slide 13: Enterprise Macro Stress Testing
- **Visual**: Severe Adverse scenario bar chart ($\Delta \text{EL}$ expansion $+\$88.7\text{M}$).
- **Speaker Note**: "Under a severe macro shock, our portfolio stress engine predicts Expected Loss expansion to guide capital buffers."

### Slide 14: Automated Model Monitoring & Drift Triggers
- **Visual**: Monthly $\text{PSI}$ traffic light gauge ($\text{PSI} = 0.0412$, GREEN).
- **Speaker Note**: "Our monitoring pipeline tracks PSI and CSI monthly, triggering automated retraining if $\text{PSI} \ge 0.25$."

### Slide 15: Conclusion & Production Sign-off
- **Visual**: Official SR 11-7 Conditional Approval Stamp & Streamlit App Screenshot.
- **Speaker Note**: "The platform is fully containerized with Docker, covered by 12 pytest tests, and approved for production."
