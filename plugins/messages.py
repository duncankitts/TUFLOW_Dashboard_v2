"""
Messages plugin for TUFLOW Dash Dashboard
--------------------------------------
Messages.csv summary table
"""

import re

import plotly.graph_objects as go
from dash import dash_table, html
from core.layout import finalise_dashboard
from core.parsing import parse_csv
from core.plugin_base import TuflowPlugin


class Messages(TuflowPlugin):
    """
    Handles TUFLOW *Message.csv files
    """
    SEVERITY_COLOURS = {
        "ERROR": "rgb(226,001,119)",
        "WARNING": "rgb(126,209,225)",
        "CHECK": "rgb(185,224,247)",
    }
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
    # Clean Data and Get Summary Functions
    # ------------------------------------------------------------------
    def _clean_data(self, df):
        """Clean and normalize dataframe"""
        df = df.copy()
        df["Message_Text"] = df["Message_Text"].str.strip()
        df["Wiki_URL"] = df["Wiki_URL"].astype(str).str.strip()
        df["Severity"] = (
            df["Message_Text"]
            .str.upper()
            .str.extract(r"(WARNING|ERROR|CHECK)", expand=False)
        )
        df["Message_ID"] = df["Message_ID"].astype(str).str.zfill(4)
        return df

    def _get_summary(self, df):
        """Group messages by ID, Severity, Text and URL"""
        return (
            df.groupby(
                ["Message_ID", "Severity", "Message_Text", "Wiki_URL"],
                dropna=False
            )
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )

    def _get_severity_colours(self, severity_list):
        """Map severity values to colours"""
        return [
            self.SEVERITY_COLOURS.get(sev, "#325A7E")
            for sev in severity_list
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
        # Clean and normalize
        df = self._clean_data(df)

        # Group unique messages
        summary = self._get_summary(df)
        severity_colours = self._get_severity_colours(summary["Severity"])

        # Exit if messages file is empty or invalid
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

        # Create clickable wiki links for error messages
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

        return fig
    def make_output(self, df, filename: str):
        df = self._clean_data(df)
        summary = self._get_summary(df)

        if df.empty or df["Message_Text"].dropna().empty:
            return html.Div(
                [
                    html.H4("No messages found"),
                    html.P(
                        "The messages file is empty or contains no valid entries."
                    ),
                ],
                style={"padding": "20px"}
            )

        def make_wiki_markdown(url):
            if isinstance(url, str) and url.strip():
                label = url.rstrip("/").split("/")[-1]
                return f"[{label}]({url})"
            return ""

        summary["Wiki_Link"] = summary["Wiki_URL"].apply(make_wiki_markdown)

        # Build conditional styling for severity-based row colouring
        style_data_conditional = [
            {
                "if": {"column_id": "Count"},
                "textAlign": "right",
            },
        ]

        # Add severity-based background colours to all cells in the row
        for severity, colour in self.SEVERITY_COLOURS.items():
            style_data_conditional.append({
                "if": {"filter_query": f'{{Severity}} = "{severity}"'},
                "backgroundColor": colour,
            })

        table = dash_table.DataTable(
            columns=[
                {"name": "Severity", "id": "Severity"},
                {"name": "ID", "id": "Message_ID"},
                {"name": "Message", "id": "Message_Text"},
                {"name": "Wiki URL", "id": "Wiki_Link", "presentation": "markdown"},
                {"name": "Count", "id": "Count"},
            ],
            data=summary.to_dict("records"),
            page_size=20,
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "whiteSpace": "normal",
                "height": "auto",
                "padding": "8px",
                "fontFamily": '"Open Sans", verdana, arial, sans-serif',
                "fontSize": "12px",
            },

            style_header={
                "backgroundColor": "#325A7E",
                "color": "white",
                "fontWeight": "bold",
            },
            style_data_conditional=style_data_conditional,
        )

        runname = filename.replace("_messages.csv", "")

        return html.Div(
            [
                html.H3(f"TUFLOW Messages Summary – {runname}"),
                table,
            ],
            style={"padding": "20px"}
        )
