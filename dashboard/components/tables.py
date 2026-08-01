"""Styled DataFrames and CSV Download Button Components."""

import pandas as pd
import streamlit as st


def render_styled_table(df: pd.DataFrame, title: str = "") -> None:
    """Render a styled DataFrame block with title."""
    if title:
        st.markdown(f"#### {title}")
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_download_button(df: pd.DataFrame, filename: str, label: str = "📥 Download CSV") -> None:
    """Render a CSV download button for reports and datasets."""
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
    )
