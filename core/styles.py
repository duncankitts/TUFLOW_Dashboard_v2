"""
Shared colour and line-style definitions for TUFLOW dashboards
"""

COLOURS = {
    "blue_main": "rgb(000,085,129)",
    "blue_light": "rgb(026,189,201)",
    "blue_dark": "#325A7E",
    "cyan": "#36B2BE",
    "pink": "#FC1CBF",
    "magenta": "rgb(226,001,119)",
    "yellow": "rgb(212,208,015)",
    "teal": "#D5E9EB",
}

LINE_STYLES = {
    "solid": None,
    "dash": "dash",
    "dot": "dot",
    "dashdot": "dashdot",
    "longdash": "longdash",
    "longdashdot": "longdashdot",
}

def styled_scatter(
    *,
    x,
    y,
    name,
    color,
    dash=None,
    mode="lines"
):
    return dict(
        x=x,
        y=y,
        name=name,
        mode=mode,
        marker_color=color,
        line=dict(dash=dash) if dash else None,
    )