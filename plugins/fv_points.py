import io
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.layout import finalise_dashboard
from core.parsing import parse_time_column
from core.plugin_base import TuflowPlugin
from core.styles import COLOURS



class FVPoints_Plugin(TuflowPlugin):

    @property
    def name(self):
        return "Points"

    @property
    def match_patterns(self):
        return [
            re.compile(r"_points\.csv$", re.IGNORECASE)
        ]

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------

    def parse(self, contents: bytes) -> pd.DataFrame:

        df = pd.read_csv(
            io.StringIO(contents.decode("utf-8")),
            engine="python"
        )

        first_col = df.columns[0]

        df.rename(
            columns={first_col: "Time"},
            inplace=True
        )

        df["Time"] = parse_time_column(df["Time"])

        for col in df.columns:
            if col != "Time":
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

        df.replace(-99999, np.nan, inplace=True)

        return df

    # ------------------------------------------------------------
    # UNIT FORMATTER
    # ------------------------------------------------------------

    @staticmethod
    def format_units(units):
        units = units.replace("degrees celsius", "°C")
        units = units.replace("^3", "³")
        units = units.replace("^2", "²")
        units = units.replace("^-1", "⁻¹")
        units = units.replace("^-2", "⁻²")
        units = units.replace("^-3", "⁻³")

        return units

    # ------------------------------------------------------------
    # COLUMN PARSER
    # ------------------------------------------------------------

    @staticmethod
    def get_variable_info(col):

        unit_match = re.search(
            r"\[(.*?)\]",
            col
        )

        units = ""
        if unit_match:
            units = unit_match.group(1)

        clean = re.sub(
            r"\s*\[.*?\]",
            "",
            col
        ).strip()

        if clean.startswith("NS"):
            clean = clean[2:]

        site = ""
        variable = clean

        if "_" in clean:
            parts = clean.rsplit("_", 1)
            if len(parts) == 2 and parts[0] and parts[1]:
                site = parts[0].replace("_", " ").strip()
                variable = parts[1]

        variable_display = variable.replace("_", " ").title()

        return {
            "site": site,
            "variable": variable,
            "variable_display": variable_display,
            "units": units,
        }

    # ------------------------------------------------------------
    # FIGURE
    # ------------------------------------------------------------

    def make_figure(
        self,
        df: pd.DataFrame,
        filename: str
    ):

        runname = re.sub(
            r"_points\.csv$",
            "",
            filename,
            flags=re.IGNORECASE
        )

        column_info = []

        for col in df.columns:
            if col == "Time":
                continue
            info = self.get_variable_info(col)
            label = (
                f"{info['site']} | "
                f"{info['variable_display']}"
            )
            axis_title = info["variable_display"]
            if info["units"]:
                axis_title += (
                    f" ({self.format_units(info['units'])})"
                )
            column_info.append(
                {
                    "column": col,
                    "label": label,
                    "axis_title": axis_title,
                }
            )

        if not column_info:
            raise ValueError(
                "No Points output columns found"
            )

        first = column_info[0]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["Time"],
                y=df[first["column"]],
                mode="lines",
                name=first["label"],
                line=dict(
                    color=COLOURS.get(
                        "blue_main",
                        "#1f77b4"
                    )
                ),
                hovertemplate=
                "Time: %{x}<br>"
                "Value: %{y}<extra></extra>"
            )
        )
        fig.update_yaxes(
            title_text=f"<b>{first['axis_title']}</b>"
        )

        buttons = []

        for info in column_info:
            buttons.append(
                dict(
                    method="update",
                    label=info["label"],
                    args=[
                        {
                            "y": [
                                df[info["column"]]
                            ],
                            "name": info["label"]
                        },
                        {
                            "yaxis.title.text":
                                f"<b>{info['axis_title']}</b>"
                        }
                    ]
                )
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=1.02,
                    y=1,
                    yanchor="top"
                )
            ],
            title=(
                f"<b>TUFLOW FV Points Outputs - "
                f"{runname}</b>"
            ),
            xaxis_title="<b>Time</b>",
            height=650,
            showlegend=True
        )

        return finalise_dashboard(
            fig,
            title=(
                f"<b>TUFLOW FV Points Outputs - "
                f"{runname}</b>"
            )
        )