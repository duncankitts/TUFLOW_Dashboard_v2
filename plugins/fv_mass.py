import io
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.layout import finalise_dashboard
from core.parsing import parse_time_column
from core.plugin_base import TuflowPlugin
from core.styles import COLOURS


VARIABLE_NAMES = { # There's more to be added here, particularly for organic water quality variables, but this is a start.
    "VOLUME": "Volume",
    "WATER_MASS": "Water Mass",
    "POTENTIAL_ENERGY": "Potential Energy",
    "SALT_MASS": "Salt Mass",
    "HEAT_CONTENT": "Heat Content",
    "SED_1_MASS": "Sediment Mass",
    "SED_1_BED_MASS": "Bed Mass",
    "WQ_DISS_OXYGEN_MG_L_MASS": "Dissolved Oxygen",
    "WQ_SILICATE_MG_L_MASS": "Silicate",
    "WQ_AMMONIUM_MG_L_MASS": "Ammonium",
    "WQ_NITRATE_MG_L_MASS": "Nitrate",
    "WQ_FRP_MG_L_MASS": "FRP",
    "WQ_PHYTO_DUMMY_CONC_MICG_L_MASS": "Phytoplankton",
    "WQ_PATH_ECOLI_ALIVE_CFU_100mL_MASS": "E.coli Alive",
    "WQ_PATH_ECOLI_DEAD_CFU_100mL_MASS": "E.coli Dead",
}


class FVMassPlugin(TuflowPlugin):

    @property
    def name(self):
        return "FV Mass"

    @property
    def match_patterns(self):
        return [
            re.compile(r"_mass\.csv$", re.IGNORECASE)
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

            if col == "Time":
                continue

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
    # COLUMN INFO
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
        )

        clean = clean.strip()

        variable_display = VARIABLE_NAMES.get(
            clean,
            clean.replace("_", " ").title()
        )

        return {
            "variable": clean,
            "display": variable_display,
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
            r"_mass\.csv$",
            "",
            filename,
            flags=re.IGNORECASE
        )

        volume_col = None
        water_mass_col = None

        dropdown_columns = []

        for col in df.columns:

            if col == "Time":
                continue

            info = self.get_variable_info(col)

            if info["variable"] == "VOLUME":
                volume_col = col
                continue

            if info["variable"] == "WATER_MASS":
                water_mass_col = col
                continue

            axis_title = info["display"]

            if info["units"]:
                axis_title += (
                    f" ({self.format_units(info['units'])})"
                )

            dropdown_columns.append(
                {
                    "column": col,
                    "label": info["display"],
                    "axis_title": axis_title,
                }
            )

        if volume_col is None:
            raise ValueError(
                "VOLUME column not found"
            )

        if water_mass_col is None:
            raise ValueError(
                "WATER_MASS column not found"
            )

        if not dropdown_columns:
            raise ValueError(
                "No MASS output variables found"
            )

        first = dropdown_columns[0]

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=(
                "Volume and Water Mass",
                first["label"]
            )
        )

        # ------------------------------------------------
        # Row 1
        # ------------------------------------------------

        fig.add_trace(
            go.Scatter(
                x=df["Time"],
                y=df[volume_col],
                mode="lines",
                name="Volume",
                line=dict(color="#1f77b4"),
                showlegend=True
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df["Time"],
                y=df[water_mass_col],
                mode="lines",
                name="Water Mass",
                line=dict(color="rgb(226,001,119)"),
                showlegend=True
            ),
            row=1,
            col=1
        )

        # ------------------------------------------------
        # Row 2
        # ------------------------------------------------

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
                showlegend=False
            ),
            row=2,
            col=1
        )

        fig.update_yaxes(
            title_text="<b>Volume / Water Mass</b>",
            row=1,
            col=1
        )

        fig.update_yaxes(
            title_text=f"<b>{first['axis_title']}</b>",
            row=2,
            col=1
        )

        buttons = []

        for info in dropdown_columns:
            buttons.append(
                dict(
                    method="update",
                    label=info["label"],
                    args=[
                        {
                            "y": [
                                df[volume_col],
                                df[water_mass_col],
                                df[info["column"]]
                            ]
                        },
                        {
                            "yaxis2.title.text":
                                f"<b>{info['axis_title']}</b>",

                            "annotations[1].text":
                                info["label"]
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
                    xanchor="left",
                    y=0.5,
                    yanchor="middle"
                )
            ],
            title=(
                f"<b>TUFLOW FV Mass Outputs - "
                f"{runname}</b>"
            ),
            height=850,
            showlegend=True
        )

        fig.update_xaxes(
            title_text="<b>Time</b>",
            row=2,
            col=1
        )

        fig = finalise_dashboard(
            fig,
            title=(
                f"<b>TUFLOW FV Mass Outputs - "
                f"{runname}</b>"
            )
        )

        fig.update_layout(
            margin=dict(l=40, r=220, t=80, b=80),
            legend=dict(
                orientation="v",
                x=1.02,
                y=0.98,
                xanchor="left",
                yanchor="top"
            )
        )

        return fig