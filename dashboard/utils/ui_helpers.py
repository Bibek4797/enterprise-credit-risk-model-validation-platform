"""Shared CSS injection utility — call inject_css() at top of every page."""
from __future__ import annotations
from pathlib import Path
import streamlit as st


def inject_css() -> None:
    """Load and inject the shared premium stylesheet into the Streamlit page."""
    # Walk up from this file to find dashboard/assets/styles.css
    this = Path(__file__).resolve()
    # utils/ -> dashboard/ -> assets/styles.css
    css_path = this.parent.parent / "assets" / "styles.css"
    if css_path.is_file():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def page_header(title: str, caption: str = "") -> None:
    """Render a consistent premium page header with optional regulatory caption."""
    inject_css()
    cap_html = ""
    if caption:
        cap_html = (
            f"<p style='margin:0.3rem 0 0 0;font-size:0.72rem;color:#64748b;"
            f"letter-spacing:0.1em;text-transform:uppercase;font-weight:600;'>{caption}</p>"
        )
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(15,30,70,0.85) 0%, rgba(25,10,55,0.8) 100%);
            border: 1px solid rgba(96,165,250,0.18);
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(12px);
        ">
            <h1 style="
                margin:0;
                font-size:1.5rem;
                font-weight:800;
                background: linear-gradient(135deg,#60a5fa 0%,#a78bfa 60%,#38bdf8 100%);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
                background-clip:text;
                letter-spacing:-0.02em;
            ">{title}</h1>
            {cap_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_divider() -> None:
    """Render a subtle section divider line."""
    st.markdown(
        "<div style='margin:1.4rem 0;border-top:1px solid rgba(96,165,250,0.1);'></div>",
        unsafe_allow_html=True,
    )


def label(text: str) -> None:
    """Render a small uppercase section label."""
    st.markdown(
        f"<p style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;"
        f"text-transform:uppercase;color:#64748b;margin:0 0 0.6rem 0;'>{text}</p>",
        unsafe_allow_html=True,
    )
