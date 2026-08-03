"""Report Exporter & CSV Download Utilities."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_csv_download_button(df: pd.DataFrame, filename: str = "export.csv", label: str = "📥 Download CSV") -> None:
    """Render styled CSV download button."""
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )
