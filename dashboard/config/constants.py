"""Constants, KPI benchmarks, and configuration parameters for Enterprise Credit Risk Dashboard."""

APP_TITLE = "Enterprise Credit Risk Analytics & Model Risk Platform"
APP_SUBTITLE = "Independent Model Governance, Portfolio Risk Monitoring & XAI Decision Platform"

PORTFOLIO_KPI_BENCHMARKS = {
    "target_default_rate_pct": 20.0,
    "max_dti_cap_pct": 30.0,
    "min_fico_benchmark": 680,
    "max_hhi_unconcentrated": 1500,
    "psi_green_threshold": 0.10,
    "psi_yellow_threshold": 0.25,
    "min_auc_benchmark": 0.7200,
    "min_ks_benchmark_pct": 34.0,
}

NAV_PAGES = [
    "1_Executive_Dashboard",
    "2_Portfolio_Analytics",
    "3_Model_Performance",
    "4_Explainable_AI",
    "5_Stress_Testing",
    "6_Model_Monitoring",
    "7_Deep_Learning_Benchmark",
    "8_Reports",
]
