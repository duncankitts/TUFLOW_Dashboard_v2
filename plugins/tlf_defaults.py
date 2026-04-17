"""
TLF Summary plugin for TUFLOW Dash Dashboard
-------------------------------------------
Summarises TUFLOW *.tlf files (Classic & HPC)
"""

import re

import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.plugin_base import TuflowPlugin


class TLFSummaryPlugin(TuflowPlugin):
    """
    Handles TUFLOW *.tlf files
    """

    @property
    def name(self) -> str:
        return "TLF Summary"

    @property
    def match_patterns(self):
        return [
            re.compile(r"\.tlf$", re.IGNORECASE)
        ]

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, contents: bytes):

        text = contents.decode("utf-8", errors="ignore")
        lines = text.splitlines()

        if not lines:
            raise ValueError("TLF file is empty")

        return lines

    # ------------------------------------------------------------------
    # Parse TUFLOW Command Lines
    # ------------------------------------------------------------------

    def parse_lines(lines):
        rows = []

        pattern = re.compile(
            r"""
            ^\s*(?P<command>.+?)          # text before ==
            \s*==\s*
            (?P<value>[^!]+?)             # text between == and !
            \s*!.*?
            \{\s*(?P<default>[^}]+)\s*\}  # value inside { }
            """,
            re.VERBOSE
        )

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def make_figure(self, lines, filename: str):
        commands = []
        values = []
        defaults = []
        row_colours = []

        runname = filename[:-4]

        if ".hpc.tlf" in filename:
            fig = go.Figure()

            fig.add_annotation(
                text="<b>Format not support</b><br>"
                     "This is likely to be a *.hpc.tlf.  Please use a *.tlf.",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14),
                align="center"
            )
        else:

            pattern = re.compile(
                r"""
                ^\s*(?P<command>.+?)          # text before ==
                \s*==\s*
                (?P<value>[^!]+?)             # text between == and !
                \s*!.*?
                \{\s*(?P<default>[^}]+)\s*\}  # value inside { }
                """,
                re.VERBOSE
            )

            for line in lines:
                match = pattern.search(line)
                if not match:
                    continue

                command = match.group("command").strip()
                value = match.group("value").strip()
                default = match.group("default").strip()

                commands.append(command)
                values.append(value)
                defaults.append(default)

                # Highlight entire row if value is not default
                if value.strip().casefold() != default.strip().casefold():
                    row_colours.append("rgb(226,001,119)")  # light red
                else:
                    row_colours.append("rgb(185,224,247)")

            fig = go.Figure(
                data=[
                    go.Table(
                        header=dict(
                            values=["Command", "Model Value", "Default"],
                            line_color='#325A7E',
                            fill_color='#325A7E',
                            font_color='white',
                            align="left",
                            font=dict(size=13, color="black")
                        ),
                        cells=dict(
                            values=[commands, values, defaults],
                            fill_color=[
                                row_colours,  # Command column
                                row_colours,  # Value column
                                row_colours  # Default column
                            ],
                            align="left",
                            font=dict(size=12)
                        )
                    )
                ]
            )

            fig.update_layout(
                height=1500,
                margin=dict(l=10, r=10, t=10, b=10)
            )

            # -------------------------------
            # Final formatting
            # -------------------------------
            fig = finalise_dashboard(
                fig,
                title=f"<b>TUFLOW TLF Settings – {runname}</b>"
            )

        return fig

