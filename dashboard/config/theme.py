"""Premium institutional color palette and Plotly dark-mode theme."""

# ── Core Palette ──────────────────────────────────────────────
PRIMARY_BLUE   = "#3b82f6"
ACCENT_BLUE    = "#60a5fa"
ACCENT_PURPLE  = "#8b5cf6"
SUCCESS_GREEN  = "#34d399"
WARNING_YELLOW = "#fbbf24"
DANGER_RED     = "#f87171"
NEUTRAL_DARK   = "#0f1e3c"
NEUTRAL_LIGHT  = "#f1f5f9"

BG_CARD        = "rgba(15, 30, 60, 0.7)"
BG_PLOT        = "rgba(7, 14, 30, 0.0)"
GRID_COLOR     = "rgba(96, 165, 250, 0.08)"
TEXT_MUTED     = "#64748b"
TEXT_MAIN      = "#e2e8f0"

# ── Grade Colours (dark-friendly) ────────────────────────────
GRADE_COLORS = {
    "A": "#34d399",   # emerald
    "B": "#60a5fa",   # blue
    "C": "#fbbf24",   # amber
    "D": "#fb923c",   # orange
    "E": "#f87171",   # red
    "F": "#e879f9",   # fuchsia
    "G": "#c084fc",   # purple
}

# ── Title style (applied separately to avoid kwarg conflict) ──
# Usage: fig.update_layout(title={"text": "My Title", **TITLE_STYLE}, **PLOTLY_THEME["layout"])
TITLE_STYLE = {
    "font": {"color": TEXT_MAIN, "size": 14, "family": "Inter, Arial, sans-serif"},
    "x": 0.02,
    "xanchor": "left",
}

# ── Shared Plotly layout tokens (NO 'title' key here) ─────────
PLOTLY_THEME = {
    "layout": {
        "font": {
            "family": "Inter, Arial, sans-serif",
            "color": TEXT_MAIN,
            "size": 12,
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor":  "rgba(0,0,0,0)",
        "margin": {"l": 48, "r": 24, "t": 44, "b": 36},
        "xaxis": {
            "gridcolor": GRID_COLOR,
            "linecolor": GRID_COLOR,
            "tickcolor": TEXT_MUTED,
            "tickfont": {"color": TEXT_MUTED, "size": 11},
            "title_font": {"color": "#94a3b8", "size": 12},
            "showgrid": True,
            "zeroline": False,
        },
        "yaxis": {
            "gridcolor": GRID_COLOR,
            "linecolor": GRID_COLOR,
            "tickcolor": TEXT_MUTED,
            "tickfont": {"color": TEXT_MUTED, "size": 11},
            "title_font": {"color": "#94a3b8", "size": 12},
            "showgrid": True,
            "zeroline": False,
        },
        "legend": {
            "bgcolor": "rgba(10,20,45,0.7)",
            "bordercolor": GRID_COLOR,
            "borderwidth": 1,
            "font": {"color": "#cbd5e1", "size": 11},
        },
        "hoverlabel": {
            "bgcolor": "rgba(10,20,50,0.95)",
            "bordercolor": "rgba(96,165,250,0.3)",
            "font": {"color": "#f1f5f9", "size": 12, "family": "Inter, Arial, sans-serif"},
        },
    }
}
