"""Reusable KPI Metric Cards and Traffic Light Status Badges."""

import streamlit as st


def render_kpi_card(title: str, value: str, subtext: str = "", badge_type: str | None = None) -> None:
    """Render a styled KPI Card block."""
    badge_html = ""
    if badge_type == "green":
        badge_html = '<span class="badge-green">GREEN (PASS)</span>'
    elif badge_type == "yellow":
        badge_html = '<span class="badge-yellow">YELLOW (WARN)</span>'
    elif badge_type == "red":
        badge_html = '<span class="badge-red">RED (ALERT)</span>'

    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title} {badge_html}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_traffic_light_header(status: str = "GREEN (PASS)", message: str = "Model operating within normal risk bounds.") -> None:
    """Render an executive Traffic Light Banner at top of page."""
    badge_class = "badge-green" if "GREEN" in status else ("badge-yellow" if "YELLOW" in status else "badge-red")
    banner_html = f"""
    <div style="background-color: #F8FAFC; border-left: 5px solid #0066CC; padding: 1rem 1.5rem; border-radius: 4px; margin-bottom: 1.5rem;">
        <span class="{badge_class}" style="font-size: 1rem; margin-right: 0.75rem;">{status}</span>
        <span style="font-size: 0.95rem; font-weight: 600; color: #2D3748;">{message}</span>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)
