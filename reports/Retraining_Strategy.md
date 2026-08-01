# Production Model Retraining Strategy & Replacement Governance

**Document Control & Model Risk Governance**
- **Model Scope**: Production Retraining Governance & Replacement Protocols for Champion Credit Model
- **Dataset Version**: LendingClub Accepted Originations (2007–2018 Q4, ~1.37M mature binary records)
- **Governance Framework**: Federal Reserve SR 11-7 Model Change Management / OCC 2011-12
- **Author**: Model Risk Governance & Quantitative Risk Analytics Team

---

## 1. Executive Summary & Retraining Philosophy

Credit risk models degrade over time due to macroeconomic cycles, shifts in underwriting policy, credit bureau score recalculations, and borrower demographic changes.

This report establishes the formal **Retraining Strategy & Champion/Challenger Replacement Protocol** for the Champion Credit Risk Model.

---

## 2. Retraining Cadence & Multi-Criterion Trigger Matrix

Retraining occurs under two distinct operational mechanisms:
1. **Scheduled Retraining**: Annual mandatory recalibration using the most recent 24–36 months of mature origination data.
2. **Trigger-Based Retraining**: Off-cycle emergency retraining executed whenever monitoring alert thresholds are breached.

| Retraining Trigger Condition | Metric Evaluated | Warning Threshold (Yellow) | Critical Trigger Threshold (Red) | Automated System Action Required |
| --- | --- | --- | --- | --- |
| **Population Drift** | Overall Portfolio $\text{PSI}$ | $0.10 \le \text{PSI} < 0.25$ | **$\text{PSI} \ge 0.25$** | Trigger off-cycle Model Retraining & MCR submission. |
| **Feature Drift** | Max Feature $\text{CSI}$ | $0.10 \le \text{CSI} < 0.25$ | **$\text{CSI} \ge 0.25$** | Recalibrate feature WoE bins and re-estimate parameters. |
| **Discrimination Loss** | OOT ROC-AUC Drop | $\Delta \text{AUC} \le -0.0300$ | **$\Delta \text{AUC} \le -0.0500$** | Mandatory model retraining and Challenger benchmarking. |
| **Risk Separation Drop** | KS Statistic ($\text{KS} \%$) | $30.0\% \le \text{KS} < 34.0\%$ | **$\text{KS} < 30.0\%$** | Mandatory model retraining and feature set re-selection. |
| **Calibration Misalignment** | Obs vs Pred PD Error | $2.0\% < E_{\text{cal}} \le 5.0\%$ | **$E_{\text{cal}} > 5.0\%$** | Execute Scorecard Intercept Recalibration. |

---

## 3. Governance Approval Workflow & Champion Cutover Protocol

```
[Monitoring Alert / Scheduled Review]
                  │
                  ▼
[1. Trigger Fired (RED Status)]
                  │
                  ▼
[2. Model Developer Re-fits Candidate Challenger]
                  │
                  ▼
[3. Benchmarking on 6-Month OOT Validation Sample]
                  │
                  ▼
[4. Independent Model Validation (IMV) Audit & Sign-off]
                  │
                  ▼
[5. Model Risk Committee (MRC) Approval Gate]
                  │
                  ▼
[6. Production API Cutover & Legacy Archive]
```

### Protocol Execution Mandate
- **Challenger Superiority Rule**: A Candidate Challenger model replaces the Operational Champion only if it achieves a statistically significant performance gain ($\Delta \text{AUC} \ge +0.0150$, $p < 0.05$) without violating FCRA adverse action notice compliance or ECOA fair lending guidelines ($\text{DIR} \ge 0.80$).
