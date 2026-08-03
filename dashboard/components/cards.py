"""Metric Cards and Header Banners Component Module."""

from __future__ import annotations

import streamlit as st


def render_kpi_card(title: str, value: str, delta: str | None = None, is_positive_good: bool = True) -> None:
    """Render styled KPI Metric card block."""
    delta_color = "normal" if is_positive_good else "inverse"
    st.metric(label=title, value=value, delta=delta, delta_color=delta_color)


def render_traffic_light_header(status: str = "GREEN", message: str = "Model Risk Compliance Satisfied") -> None:
    """Render institutional traffic light status banner."""
    color_map = {
        "GREEN": ("#059669", "🟢 PASS / STABLE"),
        "YELLOW": ("#D97706", "🟡 WARNING / MONITOR"),
        "RED": ("#DC2626", "🔴 CRITICAL DRIFT / RETRAIN REQUIRED"),
    }
    bg_color, label = color_map.get(status.upper(), ("#059669", "🟢 PASS"))

    st.markdown(
        f"""
        <div style="background-color: {bg_color}; padding: 14px 20px; border-radius: 8px; margin-bottom: 20px; color: white;">
            <h4 style="margin: 0; font-size: 16px; font-weight: 700;">{label} — {message}</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )
