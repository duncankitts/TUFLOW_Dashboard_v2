import plotly.graph_objects as go
from core.plugin_base import TuflowPlugin
from core.parsing import parse_csv
from core.layout import finalise_dashboard
import pandas as pd
import re
import numpy as np

import io
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.plugin_base import TuflowPlugin
from core.layout import finalise_dashboard
from core.styles import COLOURS


class StartStats(TuflowPlugin):

    @property
    def name(self):
        return "Start Stats"

    @property
    def match_patterns(self):
        return [
            re.compile(r"_Start_Stats\.txt$", re.IGNORECASE),
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

        # Standardise column names
        df.columns = [c.strip() for c in df.columns]

        # Convert to numeric
        df["Total (s)"] = pd.to_numeric(df["Total (s)"], errors="coerce")
        df["Elapsed (s)"] = pd.to_numeric(df["Elapsed (s)"], errors="coerce")

        # Drop zero or near-zero elapsed times (optional but recommended)
        df = df[df["Elapsed (s)"] > 0.0]

        # Preserve original file order explicitly
        df["File Order"] = df.index

        return df

    # ------------------------------------------------------------
    # PLOT
    # ------------------------------------------------------------
    def make_figure(self, df: pd.DataFrame, filename: str):
        small_stage_threshold: float = 0.05
        runname = filename.replace("_start_stats.txt", "")

        # --------------------------------------------------
        # Group small stages into "Other"
        # --------------------------------------------------
        small = df["Elapsed (s)"] < small_stage_threshold
        other_elapsed = df.loc[small, "Elapsed (s)"].sum()

        bars_df = df.loc[~small, ["Stage", "Elapsed (s)"]].copy()

        if other_elapsed > 0:
            bars_df = pd.concat([
                bars_df,
                pd.DataFrame([{
                    "Stage": f"Other (< {small_stage_threshold:.2f} s)",
                    "Elapsed (s)": other_elapsed,
                }])
            ])

        # Sort for bar chart (largest elapsed at top)
        bars_df = bars_df.sort_values("Elapsed (s)", ascending=True)

        fig= go.Figure()

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=False,
            vertical_spacing=0.25,
            subplot_titles=(
                "<b>Startup Bottlenecks (Elapsed Time per Stage)</b>",
                "<b>Cumulative Startup Timeline</b>"
            )
        )

        # --------------------------------------------------
        # Top plot: Horizontal bar chart
        # --------------------------------------------------
        fig.add_trace(
            go.Bar(
                x=bars_df["Elapsed (s)"],
                y=bars_df["Stage"],
                orientation="h",
                marker=dict(
                    color='rgb(000,085,129)'
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Elapsed: %{x:.2f} s<br>"
                    "<extra></extra>"
                ),
                showlegend=False
            ),
            row=1,
            col=1
        )

        fig.update_xaxes(title_text="<b>Time (seconds)</b>", row=1, col=1)
        fig.update_yaxes(title_text="<b>Startup Stage</b>", row=1, col=1)


        # --------------------------------------------------
        # Bottom plot: Cumulative timeline
        # --------------------------------------------------
        fig.add_trace(
            go.Scatter(
                x=df["File Order"],
                y=df["Total (s)"],
                mode="lines+markers",
                line=dict(color="rgb(000,085,129)"),
                marker=dict(size=5),
                hovertemplate=(
                    "<b>%{customdata}</b><br>"
                    "Total time: %{y:.2f} s"
                    "<extra></extra>"
                ),
                customdata=df["Stage"],
                showlegend=False
            ),
            row=2,
            col=1
        )

        # --------------------------------------------------
        # Layout
        # --------------------------------------------------
        fig.update_layout(
            title=f"<b>TUFLOW Startup Timing Breakdown – {runname}</b>",
            margin=dict(l=260, r=40, t=80, b=40),
            height=650
        )

        fig.update_xaxes(title_text="<b>Startup Stage</b>", row=2, col=1)
        fig.update_yaxes(title_text="<b>Total Cumulative Time (seconds)</b>", row=2, col=1)


        fig=finalise_dashboard(
            fig,
            title=f"<b>TUFLOW Start Stats Summary – {runname}</b>",
        )

        return fig

