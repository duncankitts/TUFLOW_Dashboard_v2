"""
2D / X1D check file plugin for TUFLOW Dash Dashboard
---------------------------------------------------
Handles:
- 2D_Q_from_x1D.csv
- 2D_Q_to_x1D.csv
- x1D_H_to_2D.csv
- x1D_H_from_2D.csv
"""

import plotly.graph_objects as go
import re
from core.plugin_base import TuflowPlugin
from core.parsing import parse_csv
from core.layout import finalise_dashboard


class Checks2DX1DPlugin(TuflowPlugin):
    """
    Handles TUFLOW 2D / 1D interface check CSV files
    """

    @property
    def name(self) -> str:
        return "2D / X1D Check Files"

    @property
    def match_patterns(self):
        return [
            re.compile(r"2d_q_(to|from)_x1d\.csv$", re.IGNORECASE),
            re.compile(r"x1d_h_(to|from)_2d\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, contents: bytes):
        df = parse_csv(contents)

        if df.empty:
            raise ValueError("Check file is empty")

        if "Time" not in df.columns:
            raise ValueError("Check file missing 'Time' column")

        if len(df.columns) < 2:
            raise ValueError("Check file has no data columns")

        return df

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def make_figure(self, df, filename: str):

        runname = filename.rsplit(".", 1)[0]

        time_col = "Time"
        data_cols = [c for c in df.columns if c != time_col]

        # Initial trace: first data column
        fig = go.Figure(
            go.Scatter(
                x=df[time_col],
                y=df[data_cols[0]],
                mode="lines",
                name=data_cols[0],
                marker_color="rgb(0,85,129)",
            )
        )

        # Build dropdown buttons (exclude Time)
        buttons = [
            dict(
                method="restyle",
                label=col,
                args=[{"y": [df[col]]}],
            )
            for col in data_cols
        ]

        # Axis titles depend on file type
        if "Q_" in filename:
            y_title = "Flow (m³/s)"
        else:
            y_title = "Water Level (m)"

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=1.02,
                    y=1,
                )
            ],
            xaxis_title="Simulation Time",
            yaxis_title=y_title,
        )

        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW Check File – {runname}</b>",
        )

        return fig