"""Model Risk Governance & SR 11-7 Documentation Engine.

Generates Model Inventory catalogs, Assumption Registers, Model Risk Ratings,
and standardized SR 11-7 Model Cards per institutional banking standards.
"""

from __future__ import annotations

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def generate_assumption_register() -> pd.DataFrame:
    """Return formal Assumption Register and Model Limitations catalog."""
    records = [
        {
            "assumption_id": "ASM-001",
            "category": "Data & Target Definition",
            "description": "Mature binary definition (excluding active Current loans) eliminates right-censoring bias.",
            "validation_status": "VERIFIED",
            "impact_level": "HIGH",
            "mitigation_control": "Out-of-time (OOT) validation on 2018 vintage confirms stability.",
        },
        {
            "assumption_id": "ASM-002",
            "category": "Linear Log-Odds",
            "description": "Logistic Scorecard assumes linear relationship between Weight of Evidence (WoE) bins and log-odds.",
            "validation_status": "VERIFIED",
            "impact_level": "HIGH",
            "mitigation_control": "Monotonicity verification across all 10 binned risk drivers.",
        },
        {
            "assumption_id": "ASM-003",
            "category": "Stationarity & Economic Cycle",
            "description": "Historical default relationships (2007–2016) remain valid under normal economic conditions.",
            "validation_status": "VERIFIED WITH MONITORING",
            "impact_level": "MEDIUM",
            "mitigation_control": "Monthly PSI tracking with trigger at PSI >= 0.10.",
        },
        {
            "assumption_id": "ASM-004",
            "category": "No Multicollinearity",
            "description": "Selected features exhibit low Variance Inflation Factor (VIF < 3.0).",
            "validation_status": "VERIFIED",
            "impact_level": "MEDIUM",
            "mitigation_control": "Pairwise correlation and VIF matrix audit.",
        },
        {
            "assumption_id": "ASM-005",
            "category": "Independence of Errors",
            "description": "Loan default events are conditionally independent given risk drivers.",
            "validation_status": "VERIFIED",
            "impact_level": "LOW",
            "mitigation_control": "Standard errors robust to macroeconomic clustering.",
        },
    ]
    return pd.DataFrame(records)


def calculate_model_risk_rating(
    model_complexity: str = "Medium",
    financial_materiality: str = "High",
    operational_risk: str = "Low",
) -> dict[str, str]:
    """Compute overall SR 11-7 Model Risk Rating (High, Medium, Low Tier)."""
    rating_matrix = {
        ("High", "High"): "TIER 1 (HIGH MODEL RISK)",
        ("Medium", "High"): "TIER 1 (HIGH MODEL RISK)",
        ("Low", "High"): "TIER 2 (MEDIUM MODEL RISK)",
        ("Medium", "Medium"): "TIER 2 (MEDIUM MODEL RISK)",
        ("Low", "Low"): "TIER 3 (LOW MODEL RISK)",
    }
    key = (model_complexity, financial_materiality)
    tier = rating_matrix.get(key, "TIER 2 (MEDIUM MODEL RISK)")

    return {
        "model_complexity": model_complexity,
        "financial_materiality": financial_materiality,
        "operational_risk": operational_risk,
        "overall_model_risk_rating": tier,
        "validation_frequency": "Annual Re-validation" if "TIER 1" in tier else "Biennial Re-validation",
    }


def generate_model_card(
    model_name: str,
    model_type: str,
    model_owner: str,
    target_variable: str,
    key_inputs: list[str],
    performance_summary: dict[str, float],
    approval_status: str,
) -> str:
    """Generate markdown-formatted SR 11-7 Model Card document."""
    inputs_str = ", ".join([f"`{col}`" for col in key_inputs])
    perf_str = "\n".join([f"- **{k}**: {v}" for k, v in performance_summary.items()])

    card_md = f"""# SR 11-7 Model Governance Card: {model_name}

**Model Metadata**
- **Model Name**: {model_name}
- **Model Type / Architecture**: {model_type}
- **Model Owner**: {model_owner}
- **Governance Status**: **{approval_status}**
- **Target Variable**: `{target_variable}`

---

## 1. Model Purpose & Scope
This model estimates individual borrower 12-month Probability of Default (PD) for retail consumer credit underwriting, risk-based pricing, and portfolio capital management under Basel III and IFRS 9 ECL standards.

---

## 2. Key Input Variables
{inputs_str}

---

## 3. Out-Of-Time (OOT) Performance Validation Summary
{perf_str}

---

## 4. Governance Controls & Re-validation Schedule
- **Annual Independent Re-validation**: Mandated under SR 11-7 Tier 1 guidelines.
- **Monthly Monitoring**: PSI, CSI, and default rate drift monitoring.
"""
    return card_md
