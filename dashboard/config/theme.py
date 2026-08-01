"""Professional institutional color palettes and Plotly theme definitions."""

# Institutional Color Palette
PRIMARY_BLUE = "#0A2540"
SECONDARY_NAVY = "#1A365D"
ACCENT_BLUE = "#0066CC"
SUCCESS_GREEN = "#107C41"
WARNING_YELLOW = "#D97706"
DANGER_RED = "#C53030"
NEUTRAL_DARK = "#2D3748"
NEUTRAL_LIGHT = "#F7FAFC"

GRADE_COLORS = {
    "A": "#107C41",
    "B": "#2B6CB0",
    "C": "#D97706",
    "D": "#DD6B20",
    "E": "#C53030",
    "F": "#9B2C2C",
    "G": "#742A2A",
}

PLOTLY_THEME = {
    "layout": {
        "font": {"family": "Inter, Arial, sans-serif", "color": NEUTRAL_DARK},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "margin": {"l": 40, "r": 40, "t": 40, "b": 40},
    }
}
