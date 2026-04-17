import io
import re

import pandas as pd
import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.layout import finalise_dashboard
from core.parsing import parse_csv
from core.plugin_base import TuflowPlugin
from core.plugin_base import TuflowPlugin
from core.styles import COLOURS


class RunStats(TuflowPlugin):

    @property
    def name(self):
        return "Run Stats"

    @property
    def match_patterns(self):
        return [
            re.compile(r"_run_Stats\.txt$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, contents: bytes) -> pd.DataFrame:
        # Read the text file
        df = pd.read_csv(
            io.StringIO(contents.decode("utf-8")),
            sep=",",
            skipinitialspace=True
        )
        return df

    # ------------------------------------------------------------
    # PLOT
    # ------------------------------------------------------------
    def make_figure(self, df: pd.DataFrame, filename: str):

        time_col = "Time"
        runname = filename.replace("_run_stats.txt", "")

        fig= go.Figure()

        fig.add_trace(go.Scatter(
            x=df["Simulation Time"],
            y=df["Other (%)"],
            name="Other",
            mode="lines",
            showlegend=True,
            stackgroup="one",
            line = dict(color="rgb(000,085,129)"),
            fillcolor = "rgba(000,085,129)",
            hovertemplate=(
                "Other: %{y:.1f}%<extra></extra>"
            )
        )
            )

        fig.add_trace(
        go.Scatter(
            x=df["Simulation Time"],
            y=df["2D (%)"],
            name="2D",
            mode="lines",
            showlegend=True,
            stackgroup="one",
            line=dict(color="rgb(126,209,225)"),
            fillcolor="rgba(126,209,225)",
            hovertemplate = (
            "2D: %{y:.1f}%<extra></extra>"
        )
        )
        )


        fig.add_trace(
        go.Scatter(
            x=df["Simulation Time"],
            y=df["1D (%)"],
            name="1D",
            mode="lines",
            showlegend=True,
            stackgroup="one",
            line=dict(color="rgb(185,224,247)"),
            fillcolor="rgba(185,224,247)",hovertemplate=(
                "1D: %{y:.1f}%<extra></extra>"
            ))
        )

        # Layout
        fig.update_layout(
        title = "<b>Simulation Time Breakdown</b>",
        xaxis_title = "<b>Simulation Time</b>",
        yaxis_title = "<b>Percentage (%) of Time</b>",
        yaxis = dict(range=[0, 100]),
        hovermode = "x unified",
        xaxis_unifiedhovertitle=dict(text="Time: %{x}<br>"),
        height=650
        )


        fig=finalise_dashboard(
            fig,
            title=f"<b>TUFLOW Run Stats Summary – {runname}</b>",
        )

        return fig

