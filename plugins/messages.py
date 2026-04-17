"""
Messages plugin for TUFLOW Dash Dashboard
--------------------------------------
Messages.csv summary table
"""

import re

import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.parsing import parse_csv
from core.plugin_base import TuflowPlugin


class Messages(TuflowPlugin):
    """
    Handles TUFLOW *MB.csv files
    """

    @property
    def name(self) -> str:
        return "Run Messages Summary"

    @property
    def match_patterns(self):
        return [
            # Match *_mb.csv but NOT *_1d_mb.csv
            re.compile(r"(?<!_1d)_messages\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, contents: bytes):
        df = parse_csv(contents)

        # Assign expected column names (based on file structure)
        df.columns = [
            "Message_ID",
            "Severity_Code",
            "X",
            "Y",
            "Message_Text",
            "Extra_1",
            "Extra_2",
            "Extra_3",
            "Wiki_URL"
        ]

        return df

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def make_figure(self, df, filename: str):
        # ------------------------------------------------------------
        # 2. CLEAN AND NORMALISE
        # ------------------------------------------------------------
        # Strip whitespace
        df["Message_Text"] = df["Message_Text"].str.strip()
        df["Wiki_URL"] = df["Wiki_URL"].astype(str).str.strip()

        # Infer severity from text (robust)
        df["Severity"] = df["Message_Text"].str.extract(
            r"^(WARNING|ERROR|CHECK)",
            expand=False
        )

        # Ensure Message_ID is string-safe
        df["Message_ID"] = df["Message_ID"].astype(str).str.zfill(4)

        # ------------------------------------------------------------
        # 3. GROUP UNIQUE MESSAGES
        # ------------------------------------------------------------
        summary = (
            df.groupby(
                ["Message_ID", "Severity", "Message_Text", "Wiki_URL"],
                dropna=False
            )
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )

        SEVERITY_COLOURS = {
            "ERROR": "rgb(226,001,119)",
            "WARNING": "rgb(126,209,225)",
            "CHECK": "rgb(185,224,247)",
        }

        severity_colours = [
            SEVERITY_COLOURS.get(sev, '#325A7E')
            for sev in summary["Severity"]
        ]

        # ------------------------------------------------------------
        # Early exit if messages file is empty or invalid
        # ------------------------------------------------------------
        if df.empty or df["Message_Text"].dropna().empty:
            fig = go.Figure()

            fig.add_annotation(
                text="<b>No messages found</b><br>"
                     "The messages file is empty or contains no valid entries.",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14),
                align="center"
            )

            fig.update_layout(
                title=f"<b>TUFLOW Messages Summary – {filename.replace('_messages.csv', '')}</b>",
                height=300,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                margin=dict(l=20, r=20, t=60, b=20)
            )

            return fig

        # Create clickable wiki links with same visible text

        def make_wiki_link(url):
            if isinstance(url, str) and url.strip():
                label = url.rstrip("/").split("/")[-1]
                return f'{url}'
            return ""

        summary["Wiki_Link"] = summary["Wiki_URL"].apply(make_wiki_link)

        fig = go.Figure(
            data=[
                go.Table(
                    columnwidth=[1, 1, 5, 2, 1],
                    header=dict(
                        values=[
                            "<b>Severity</b>",
                            "<b>ID</b>",
                            "<b>Message</b>",
                            "<b>Wiki URL</b>",
                            "<b>Count</b>",
                        ],
                        fill_color='#325A7E',
                        line_color='#325A7E',
                        align="left",
                        font=dict(size=12, color='White')
                    ),
                    cells=dict(
                        values=[
                            summary["Severity"].astype(str).tolist(),
                            summary["Message_ID"].astype(str).tolist(),
                            summary["Message_Text"].astype(str).tolist(),
                            summary["Wiki_Link"].astype(str).tolist(),
                            summary["Count"].astype(str).tolist(),
                        ],

                        fill_color=[
                            severity_colours,
                            severity_colours,
                            severity_colours,
                            severity_colours,
                            severity_colours,
                        ],
                        align="left",
                        height=24
                    )
                )
            ]
        )

        runname = filename.replace("_messages.csv", "")

        fig.update_layout(
            title=f"<b>TUFLOW Messages Summary – {runname}</b>",
            height=1000,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        # ------------------------------------------------------------------
        # Final formatting
        # ------------------------------------------------------------------
        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW Messages Summary – {runname}</b>",
        )

        return fig

