"""Plotly Styling & Layout Utility Module."""

from __future__ import annotations

import plotly.graph_objects as go


def apply_enterprise_theme(fig: go.Figure, title: str = "", height: int = 450) -> go.Figure:
    """Apply consistent institutional dark theme layout to Plotly figures."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "y": 0.95,
            "x": 0.05,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 16, "color": "#F8FAFC"},
        },
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font={"family": "Inter, Roboto, sans-serif", "color": "#94A3B8"},
        margin={"l": 40, "r": 40, "t": 60, "b": 40},
        height=height,
        hoverlabel={"bgcolor": "#1E293B", "font_size": 13, "font_family": "Inter"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig
