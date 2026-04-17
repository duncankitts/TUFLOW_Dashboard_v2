import io
import re

import pandas as pd
import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.parsing import parse_csv
from core.plugin_base import TuflowPlugin
from core.styles import COLOURS


class OnedMBPlugin(TuflowPlugin):

    @property
    def name(self):
        return "Mass Balance 1D"
    """
    Handles TUFLOW *_1D_MB.csv files
    """

    @property
    def match_patterns(self):
        return [
            re.compile(r"_1d_mb\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, contents: bytes) -> pd.DataFrame:

        df = pd.read_csv(
            io.StringIO(contents.decode("utf-8")),
            header=None,
            index_col=False,
            engine="python"
        )

        # Drop first 3 rows (headers/junk)
        df = df.iloc[4:].reset_index(drop=True)
        # Drop first column (paths)
        df = df.iloc[:, 1:].reset_index(drop=True)
        # Rename first remaining column to Time.  Probably not really needed
        df = df.rename(columns={df.columns[0]: "Time"})

        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)

        return df

    # ------------------------------------------------------------
    # PLOT
    # ------------------------------------------------------------
    def make_figure(self, df: pd.DataFrame, filename: str):
        runname = filename[:-10]


        fig = go.Figure(
            data=go.Scatter(x=df['Time'], y=df[df.columns[1]], mode='lines',name=df.columns[1], marker_color='rgb(000,085,129)', hovertemplate=(
                    "Time: %{x}<br>"
                    "Value: %{y}<br>")))

        time_col = "Time"

        buttons = []

        for idx, col in enumerate(df.columns):
            if col == time_col:
                continue

            buttons.append(
                dict(
                    method="restyle",
                    label=col,
                    args=[{"y": [df.iloc[:, idx]],
                           "name": col}],
                    )
            )

        fig.update_layout(
            title={
                'text': "f</b>1D Mass Balance ' + {runname}</b>",
                'y': 0.95,
                'x': 0.5
            }, updatemenus=[dict(
                buttons=buttons,
                name='Node',
                x=1.02,
                y=1,
                direction='down',
                xanchor="right",
                yanchor="top",
            )],height = 650,
            template="plotly_white")
        fig.update_yaxes(title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_xaxes(title_text="<b>Simulation Time (Hrs)</b>")

        return finalise_dashboard(
            fig,
            title=f"<b>1D Mass Balance – {runname}</b>",
        )
