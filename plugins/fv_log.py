import re
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.layout import finalise_dashboard
from core.plugin_base import TuflowPlugin


class FVlog_Plugin(TuflowPlugin):

    @property
    def name(self):
        return "FV Log"

    @property
    def match_patterns(self):
        return [
            re.compile(r"(?<!simulations)\.log$", re.IGNORECASE)
        ]

    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"

    pattern = re.compile(
        rf"^\s*t\s*=\s*"
        rf"(\d{{2}}/\d{{2}}/\d{{4}}\s+\d{{2}}:\d{{2}}:\d{{2}})"
        rf"\.?\s+"
        rf"dt\s*=\s*({number})\s*/\s*({number})\s*s\.?\s+"
        rf"elapsed\s+time\s*=\s*({number})\s*s\.?",
        re.IGNORECASE,
    )

    start_marker = "Entering timestep loop"
    end_marker = "Exiting timestep loop"

    def parse(self, contents: bytes) -> pd.DataFrame:
        text = contents.decode("utf-8", errors="ignore")
        lines = text.splitlines()

        records = []
        inside_timestep_loop = False
        total_lines = 0
        lines_inside_loop = 0
        lines_starting_t = 0
        regex_matches = 0

        for raw_line in lines:
            total_lines += 1
            line = raw_line.rstrip("\n")

            if self.start_marker.lower() in line.lower():
                inside_timestep_loop = True
                continue

            if self.end_marker.lower() in line.lower():
                break

            if not inside_timestep_loop:
                continue

            lines_inside_loop += 1
            stripped_line = line.strip()

            if not stripped_line.lower().startswith("t"):
                continue

            if not re.match(r"^t\s*=", stripped_line, re.IGNORECASE):
                continue

            lines_starting_t += 1
            match = self.pattern.search(stripped_line)

            if not match:
                continue

            regex_matches += 1
            records.append(
                {
                    "t": datetime.strptime(match.group(1), "%d/%m/%Y %H:%M:%S"),
                    "internal dt": float(match.group(2)),
                    "external dt": float(match.group(3)),
                    "elapsed_time": float(match.group(4)),
                }
            )

        df = pd.DataFrame(records)

        if df.empty:
            raise ValueError(
                "No timestep records found.\n"
                f"Total lines read: {total_lines}\n"
                f"Lines inside loop: {lines_inside_loop}\n"
                f"Lines beginning with 't': {lines_starting_t}\n"
                f"Regex matches: {regex_matches}"
            )

        return df

    def make_figure(self, df: pd.DataFrame, filename: str):
        runname = re.sub(r"\.log$", "", filename, flags=re.IGNORECASE)

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.2,
            specs=[
                [{"secondary_y": True}],
                [{}]
            ]
        )

        fig.add_trace(
            go.Scatter(
                x=df["t"],
                y=df["internal dt"],
                mode="lines",
                name="Internal Timestep",
                line=dict(color="#003A70", width=2),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Internal dt: %{y:.3f} s"
                    "<extra></extra>"
                )
            ),
            row=1,
            col=1,
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=df["t"],
                y=df["external dt"],
                mode="lines",
                name="External Timestep",
                line=dict(color="#FC1CBF", width=2),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "External dt: %{y:.3f} s"
                    "<extra></extra>"
                )
            ),
            row=1,
            col=1,
            secondary_y=True
        )

        fig.add_trace(
            go.Scatter(
                x=df["t"],
                y=df["elapsed_time"],
                mode="lines",
                name="Elapsed Time",
                line=dict(color="#003A70", width=2),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Elapsed Time: %{y:.1f} s"
                    "<extra></extra>"
                )
            ),
            row=2,
            col=1
        )

        fig.update_yaxes(
            title_text="<b>Internal Timestep (s)</b>",
            row=1,
            col=1,
        )

        fig.update_yaxes(
            title_text="<b>External Timestep (s)</b>",
            row=1,
            col=1,
            secondary_y=True
        )

        fig.update_yaxes(
            title_text="<b>Elapsed Time (s)</b>",
            row=2,
            col=1
        )

        fig.update_xaxes(
            title_text="<b>Simulation Time</b>",
            row=2,
            col=1
        )

        fig.update_layout(
            title=dict(
                text=f"<b>TUFLOW FV Timestep Diagnostics — {runname}</b>",
                x=0.5,
                xanchor="center"
            ),
            template="plotly_white",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.12,
                yanchor="top"
            ),
            margin=dict(l=80, r=80, t=90, b=100)
        )

        return finalise_dashboard(fig, title=f"<b>TUFLOW FV Timesteps – {runname}</b>")