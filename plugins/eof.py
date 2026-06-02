import io
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.parsing import parse_csv
from core.plugin_base import TuflowPlugin
from core.styles import COLOURS


class EOFPlugin(TuflowPlugin):

    @property
    def name(self):
        return "EOF Storage Layer"

    @property
    def match_patterns(self):
        return [
            re.compile(r"\.eof$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, contents: bytes) -> pd.DataFrame:

        text = contents.decode("utf-8", errors="ignore")

        node_blocks = re.split(r'\bNode\s+', text)[1:]

        data = []

        for block in node_blocks:
            lines = block.strip().splitlines()
            node_name = lines[0].strip()

            elev = []
            area = []

            for i, line in enumerate(lines):

                # Capture elevation values and surface area values

                if line.strip().startswith("Elevation"):
                    line_data = line.split(")", 1)[-1]
                    elev = [float(v) for v in re.findall(r"[-+]?\d*\.\d+|\d+", line_data)]

                if line.strip().startswith("Surface Area"):
                    line_data = line.split(")", 1)[-1]
                    area = [float(v) for v in re.findall(r"[-+]?\d*\.\d+|\d+", line_data)]

            if elev and area:
                if len(elev) != len(area):
                    print(f"WARNING: mismatch in {node_name}: {len(elev)} vs {len(area)}")

                n = min(len(elev), len(area))

                for i in range(n):
                    data.append({
                        "Node": node_name,
                        "Elevation (m)": elev[i],
                        "Surface Area (m2)": area[i]
                    })

        df = pd.DataFrame(data)
        #print(df) #For troubleshooting
        return df

    # ------------------------------------------------------------
    # PLOT
    # ------------------------------------------------------------
    import plotly.graph_objs as go
    import pandas as pd

    def make_figure(self, df: pd.DataFrame, filename: str):

        runname = filename.replace(".eof", "")

        # --- Basic validation (same pattern as yours) ---
        if df.empty or df.shape[0] < 3:
            fig = go.Figure()

            fig.add_annotation(
                text="<b>No NODE DATA found</b><br>"
                     "Elevation / Surface Area structure not recognised",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14),
                align="center"
            )

            fig.update_layout(
                title=f"<b>TUFLOW Storage Curves – {runname}</b>",
                height=300,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                margin=dict(l=20, r=20, t=60, b=20)
            )

            return fig

        # --- Expecting columns exactly like your parser output ---
        required_cols = ["Node", "Elevation (m)", "Surface Area (m2)"]
        if not all(c in df.columns for c in required_cols):
            raise ValueError("Expected columns: Node, Elevation (m), Surface Area (m2)")

        # --- Sort per node (important for clean curves) ---
        df = df.sort_values(["Node", "Elevation (m)"])

        nodes = df["Node"].unique()

        if len(nodes) == 0:
            raise ValueError("No nodes found in EOF data")

        # --- Helper (keeps your style) ---
        def yaxis_title_for_node():
            return "Elevation (m)"

        def xaxis_title_for_node():
            return "Surface Area (m²)"

        # --- First node (initial trace) ---
        first_node = nodes[0]
        first_df = df[df["Node"] == first_node]

        fig = go.Figure(
            go.Scatter(
                x=first_df["Surface Area (m2)"],
                y=first_df["Elevation (m)"],
                mode="lines",
                fill="tozerox",  # fill to x = 0
                fillcolor="rgba(31, 119, 180, 0.2)",  # light version of your line colour
                showlegend=False,
                name=first_node,
                marker_color=COLOURS["blue_main"],
                hovertemplate=(
                    "Area: %{x:.2f} m²<br>"
                    "Elevation: %{y:.3f} m<br>"
                )
            )
        )
        fig.update_xaxes(rangemode="tozero")# Include zero
        fig.update_yaxes(title_text=f"<b>{yaxis_title_for_node()}</b>")

        # --- Dropdown (same pattern as your PO code) ---
        buttons = []

        for node in nodes:
            node_df = df[df["Node"] == node]

            buttons.append(
                dict(
                    method="update",
                    label=node,

                    args=[
                        {
                            "x": [node_df["Surface Area (m2)"]],
                            "y": [node_df["Elevation (m)"]],
                            "name": node,
                            "hovertemplate": [
                                "Area: %{x:.2f} m²<br>"
                                "Elevation: %{y:.3f} m<br>"
                            ],
                        },
                        {
                            "title": f"<b>TUFLOW Storage Curve – {runname} – {node}</b>"
                        }
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
        xaxis_title=f"<b>{xaxis_title_for_node()}</b>",
        showlegend=True,
        height=650
    )

        return finalise_dashboard(
        fig,
        title=f"<b>TUFLOW Storage Curves – {runname}</b>",
    )




