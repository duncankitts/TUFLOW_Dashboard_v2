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

from core.plugin_base import TuflowPlugin
from core.layout import finalise_dashboard
from core.styles import COLOURS


class POPlugin(TuflowPlugin):

    @property
    def name(self):
        return "Plot Output (PO)"

    @property
    def match_patterns(self):
        return [
            re.compile(r"_po\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, contents: bytes) -> pd.DataFrame:

        # Read in CSV
        df = pd.read_csv(
            io.StringIO(contents.decode("utf-8")),
            header=None,
            index_col=False,
            engine="python"
        )

        # ---------- basic validation ----------
        if df.shape[0] < 4 or df.shape[1] < 3:
            raise ValueError("PO.csv header structure not recognised")

        # Line 1: descriptive headers
        hdr_desc = df.iloc[0].astype(str).str.strip()

        # Line 2: names
        hdr_name = df.iloc[1].astype(str).str.strip()

        # ---------- build column names ----------
        cols = []
        for desc, name in zip(hdr_desc, hdr_name):
            if name.lower() == "time":
                cols.append("Time")
            else:
                cols.append(f"{name} {desc}".strip())

        df.columns = cols

        # Drop header + junk rows
        df = df.iloc[3:].reset_index(drop=True)

        # Drop first (path) column
        df = df.iloc[:, 1:].reset_index(drop=True)

        # Treat -99999 as no-data
        df = df.astype(float, errors="ignore")
        df.replace(-99999, np.nan, inplace=True)

        # Force numerics
        for c in df.columns:
            if c != "Time":
                df[c] = pd.to_numeric(df[c], errors="coerce")

        return df

    # ------------------------------------------------------------
    # PLOT
    # ------------------------------------------------------------
    def make_figure(self, df: pd.DataFrame, filename: str):

        time_col = "Time"
        runname = filename.replace("_PO.csv", "")

        # Attempt to dynamically set Y axis title based on PO header information for each trace.  Need to work on regions and GW outputs (are there others?).
        def yaxis_title_for_column(col: str) -> str:
            c = col.lower()
            if "level" in c:
                return "Water Level (m)"
            if "flow" in c:
                return "Flow (m³/s)"
            if "volume" in c:
                return "Volume (m³)"
            if "velocity" in c:
                return "Velocity (m/s)"
            return "Value"

        data_cols = [
            (i, c) for i, c in enumerate(df.columns)
            if c != time_col
        ]

        if not data_cols:
            raise ValueError("PO.csv contains no output columns")

        first_idx, first_col = data_cols[0]

        fig = go.Figure(
            go.Scatter(
                x=df[time_col],
                y=df.iloc[:, first_idx],
                mode="lines",
                name=first_col,
                marker_color=COLOURS["blue_main"],
                hovertemplate=(
                    "Time: %{x}<br>"
                    "Value: %{y}<br>")
            )
        )

        fig.update_yaxes(title_text=f"<b>{yaxis_title_for_column(first_col)}</b>")

        buttons = []
        for col_idx, col_name in data_cols:
            buttons.append(
                dict(
                    method="update",
                    label=col_name,

                    args=[
                        # Update the trace data
                        {"y": [df.iloc[:, col_idx]]},

                        # Y-axis title update
                        {"yaxis.title.text": f"<b>{yaxis_title_for_column(col_name)}</b>"},
                    ],

                )
            )

        fig.update_layout(
            updatemenus=[dict(
                buttons=buttons,
                direction="down",
                showactive=True,
                x=1.02,
                y=1,
                yanchor="top",
            )],
            xaxis_title="<b>Simulation Time</b>",
            showlegend=True, height=650
        )

        return finalise_dashboard(
            fig,
            title=f"<b>TUFLOW PO Outputs – {runname}</b>",
        )
