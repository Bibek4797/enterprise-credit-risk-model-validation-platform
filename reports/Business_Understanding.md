# Business Understanding: Credit Risk Modelling and Independent Model Validation

## Purpose and Scope

This document establishes the business context for a credit-risk modelling and independent model validation exercise based on LendingClub loan data. It describes the key risk concepts, model-use cases, governance expectations, and the limits of analogy between a marketplace-lending dataset and an institution's regulated credit-risk framework.

## Credit Risk

Credit risk is the risk of financial loss arising when a borrower, counterparty, guarantor, or other obligor fails to meet a contractual obligation. For a lending institution, this includes missed payments, delinquency, default, restructuring, bankruptcy, recovery shortfall, and deterioration in a borrower's creditworthiness. Credit risk is managed across the full customer lifecycle: acquisition, underwriting, pricing, approval, account management, collections, provisioning, capital planning, and portfolio oversight.

Risk is not limited to whether a borrower defaults. It also includes the severity and timing of loss, concentration across sectors or geographies, model uncertainty, operational execution, and the effect of changing economic conditions. A professional risk framework therefore combines sound data, fit-for-purpose models, policy controls, human oversight, independent challenge, and ongoing monitoring.

## Probability of Default (PD)

Probability of Default is the estimated likelihood that an obligor will default over a stated time horizon, commonly 12 months for regulatory and accounting applications. A PD model produces a calibrated risk estimate, not a certainty of default. The definition of default, observation window, portfolio, and point-in-time or through-the-cycle perspective must be explicitly documented because each affects the estimate and its permitted use.

At application, PD can support approval decisions, risk-based pricing, credit limits, and expected-loss estimation. During the customer lifecycle, behavioural PD can support early-warning indicators, collections prioritisation, and account-management actions. Good PD models are assessed for discrimination, calibration, stability, segmentation performance, robustness, interpretability, and operational suitability.

## Loss Given Default (LGD)

Loss Given Default is the proportion of exposure that is not recovered after a default, net of recoveries, collateral proceeds, costs, discounting, and any relevant cure treatment. It is commonly expressed as a percentage between zero and one, although realised measures can occasionally fall outside that range depending on recoveries and costs.

LGD depends on product structure, collateral, seniority, geography, collection strategy, legal process, borrower characteristics, and macroeconomic conditions. Unsecured consumer loans, such as many loans represented in LendingClub data, tend to have limited collateral mitigation; recoveries and collection costs are therefore particularly relevant. LGD must be designed with a clearly defined default event, recovery horizon, discount-rate convention, and treatment of unresolved defaults.

## Exposure at Default (EAD)

Exposure at Default is the expected amount owed when default occurs. For amortising term loans, it reflects outstanding principal plus relevant accrued amounts at the default date. For revolving facilities, EAD additionally considers expected future drawdowns before default, often modelled through a credit conversion factor.

EAD is product-specific. It requires careful alignment to the contractual balance, the definition of default, and the intended calculation basis. It should not be inferred simply from the original loan amount when the account has amortised or when customers can draw further credit.

## Expected Loss (EL)

Expected Loss is the average credit loss anticipated over a defined horizon and is commonly represented as:

```text
Expected Loss = PD × LGD × EAD
```

This relationship is a conceptual foundation rather than a substitute for an institution's approved accounting, regulatory, or economic-capital methodology. The three components must use compatible definitions, horizons, populations, and observation dates. Expected loss supports portfolio planning, pricing, impairment estimation, capital management, and risk appetite monitoring.

## Application Scorecards and Behaviour Scorecards

An application scorecard estimates risk at the point a customer applies for credit. It uses information available before the lending decision, such as verified income, employment, bureau history, existing indebtedness, and application characteristics. Its central control is temporal eligibility: it must exclude any information created after approval, funding, or subsequent repayment performance.

A behaviour scorecard estimates risk for an existing account. It can use account conduct observed after origination, including payment timeliness, delinquency status, balance changes, utilisation, and recent transactions. Behaviour models may be more predictive for account management, but they cannot be used retrospectively as application models because those variables would leak future information.

## Why Banks Build Credit Risk Models

Banks build credit-risk models to make consistent, scalable, evidence-based decisions while preserving policy and expert judgement. Typical uses include:

- underwriting, approval, and credit-limit decisions;
- risk-based pricing and profitability assessment;
- IFRS 9/CECL-style expected-credit-loss estimation where applicable;
- regulatory and economic capital measurement;
- portfolio monitoring, stress testing, and risk appetite;
- collections, remediation, and customer-treatment strategies; and
- management information and governance reporting.

Models do not replace accountability. Their outputs must be used within approved policies, documented limitations, monitoring thresholds, overrides, and escalation procedures.

## Model Validation

Model validation is an independent, evidence-based assessment of whether a model is fit for its intended purpose. It evaluates the conceptual soundness of the methodology, the integrity and appropriateness of data, implementation correctness, performance, limitations, controls, documentation, and ongoing monitoring.

Validation is not merely a re-run of development results. It provides credible challenge to assumptions, alternative approaches, segmentation choices, target definitions, samples, performance claims, and the appropriateness of model use. Validation conclusions should be documented with clear findings, severity ratings, remediation actions, owners, and timelines.

## Model Development and Model Validation

Model development designs, builds, documents, and monitors a model to address a defined business need. Developers select the methodology, establish data lineage, define the target and population, estimate the model, assess performance, and produce implementation specifications.

Model validation is deliberately independent from development. Validators test whether the development choices are justified, reproduce key calculations where appropriate, benchmark or challenge the methodology, assess limitations and controls, and determine whether the model can be approved, approved with conditions, or requires remediation. Independence of reporting, incentives, and decision rights is essential to credible challenge.

## Explainability in Banking

Explainability is important because credit decisions affect customers, financial outcomes, regulatory obligations, and the institution's reputation. Stakeholders must be able to understand the drivers of model outputs, investigate unexpected outcomes, evidence fairness and policy compliance, communicate adverse-action reasons where required, and challenge a model effectively.

An interpretable model is not automatically valid, and a complex model is not automatically inappropriate. The required level of explanation should be proportionate to materiality, use case, customer impact, regulatory context, and operational controls. Any use of explainability techniques must be stable, correctly interpreted, and supported by documentation rather than treated as a substitute for sound modelling.

## Relevance of the LendingClub Project to Banking Practice

LendingClub data provides a useful public setting for demonstrating the disciplined lifecycle of consumer credit modelling: defining an origination population, distinguishing decision-time variables from outcome information, estimating default risk, assessing performance, documenting limitations, and performing independent challenge.

The project is an educational proxy, not a production bank model. A regulated institution would ordinarily require internal data lineage, approved default definitions, bureau and verified-income feeds, policy rules, customer-protection controls, macroeconomic scenarios, model inventory registration, controlled deployment, and formal governance. The project will therefore emphasize methodological discipline and transparent limitations rather than claiming regulatory approval or direct production applicability.

## Governance Principles for This Project

- Preserve raw source data and establish clear data lineage.
- Separate development inputs from post-origination and post-default information.
- Document definitions, assumptions, samples, limitations, and intended uses.
- Maintain reproducible code, configuration, testing, and review evidence.
- Treat model performance as necessary but insufficient; assess conceptual soundness, implementation, fairness considerations, stability, and control effectiveness.
- Present conclusions with appropriate caution and do not overstate results from a public dataset.
