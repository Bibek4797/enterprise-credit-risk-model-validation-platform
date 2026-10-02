"""Premium Metric Cards and Status Banner Components."""

from __future__ import annotations
import streamlit as st


def render_kpi_card(
    title: str,
    value: str,
    delta: str | None = None,
    is_positive_good: bool = True,
    icon: str = "",
) -> None:
    """Render a glassmorphism KPI metric card with unclipped titles."""
    st.markdown(
        """
        <style>
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricLabel"] > div,
        div[data-testid="stMetricLabel"] p {
            white-space: normal !important;
            text-overflow: unset !important;
            overflow: visible !important;
            word-break: normal !important;
            line-height: 1.35 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    delta_color = "normal" if is_positive_good else "inverse"
    label = f"{icon} {title}".strip() if icon else title
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def render_traffic_light_header(
    status: str = "GREEN",
    message: str = "Model Risk Compliance Satisfied",
) -> None:
    """Render a premium glassmorphism traffic-light status banner."""
    config = {
        "GREEN": {
            "bg": "linear-gradient(135deg, rgba(6,95,70,0.45) 0%, rgba(5,150,105,0.3) 100%)",
            "border": "rgba(52, 211, 153, 0.35)",
            "dot": "#34d399",
            "label": "PASS · STABLE",
            "glow": "rgba(52,211,153,0.15)",
        },
        "YELLOW": {
            "bg": "linear-gradient(135deg, rgba(120,80,0,0.45) 0%, rgba(180,120,0,0.3) 100%)",
            "border": "rgba(251,191,36,0.35)",
            "dot": "#fbbf24",
            "label": "WARNING · MONITOR",
            "glow": "rgba(251,191,36,0.12)",
        },
        "RED": {
            "bg": "linear-gradient(135deg, rgba(120,20,20,0.5) 0%, rgba(185,28,28,0.35) 100%)",
            "border": "rgba(248,113,113,0.35)",
            "dot": "#f87171",
            "label": "CRITICAL · RETRAIN REQUIRED",
            "glow": "rgba(248,113,113,0.15)",
        },
    }
    c = config.get(status.upper(), config["GREEN"])
    st.markdown(
        f"""
        <div style="
            background: {c['bg']};
            border: 1px solid {c['border']};
            border-radius: 14px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 0 24px {c['glow']};
        ">
            <div style="
                width: 10px; height: 10px;
                border-radius: 50%;
                background: {c['dot']};
                box-shadow: 0 0 8px {c['dot']};
                flex-shrink: 0;
                animation: pulse 2s infinite;
            "></div>
            <div>
                <span style="
                    font-size: 0.7rem;
                    font-weight: 700;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                    color: {c['dot']};
                    display: block;
                    margin-bottom: 2px;
                ">{c['label']}</span>
                <span style="
                    font-size: 0.9rem;
                    font-weight: 500;
                    color: #e2e8f0;
                ">{message}</span>
            </div>
        </div>
        <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; box-shadow: 0 0 8px {c['dot']}; }}
            50% {{ opacity: 0.6; box-shadow: 0 0 16px {c['dot']}; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = "") -> None:
    """Render a styled section header with optional subtitle."""
    sub_html = f'<p style="margin:0;font-size:0.8rem;color:#64748b;font-weight:500;letter-spacing:0.04em;">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div style="margin-bottom: 1rem;">
            <h3 style="
                margin: 0 0 2px 0;
                font-size: 1rem;
                font-weight: 700;
                color: #cbd5e1;
                letter-spacing: -0.01em;
            ">{title}</h3>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
