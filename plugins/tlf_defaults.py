"""
TLF Summary plugin for TUFLOW Dash Dashboard
-------------------------------------------
Summarises TUFLOW *.tsf files (Classic & HPC)
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import io
import pandas as pd
import re

from core.plugin_base import TuflowPlugin
from core.layout import finalise_dashboard


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

