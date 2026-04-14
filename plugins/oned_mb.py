import io
import pandas as pd
import plotly.graph_objects as go
import re
from core.plugin_base import TuflowPlugin
from core.parsing import parse_csv
from core.layout import finalise_dashboard
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
        # Rename first remaining column to Time
        df = df.rename(columns={df.columns[0]: "Time"})

        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)

        print(df.head())

        return df

    # ------------------------------------------------------------
    # PLOT
    # ------------------------------------------------------------
    def make_figure(self, df: pd.DataFrame, filename: str):
        runname = filename[:-10]


        fig = go.Figure(
            data=go.Scatter(x=df['Time'], y=df[df.columns[1]], mode='lines', marker_color='rgb(000,085,129)'))

        time_col = "Time"

        buttons = []

        for idx, col in enumerate(df.columns):
            if col == time_col:
                continue

            buttons.append(
                dict(
                    method="restyle",
                    label=col,
                    args=[{"y": [df.iloc[:, idx]]}],
                )
            )

        fig.update_layout(
            title={
                'text': '1D Mass Balance ' + runname,
                'y': 0.95,
                'x': 0.5
            }, updatemenus=[dict(
                buttons=buttons,
                name='Node',
                direction='down',
            )],
            template="plotly_white")
        fig.update_yaxes(title_text="Volume (m<sup>3</sup>)")
        fig.update_xaxes(title_text="Simulation Time (Hrs)")

        return finalise_dashboard(
            fig,
            title=f"<b>1D Mass Balance – {runname}</b>",
        )
