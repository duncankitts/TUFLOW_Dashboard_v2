"""
Simulations Log Summary plugin for TUFLOW Dash Dashboard
-------------------------------------------------------
Summarises _ TUFLOW Simulations.log files
"""

import io
import re
from collections import defaultdict
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.plugin_base import TuflowPlugin


class SimulationsLog(TuflowPlugin):
    """
    Handles _ TUFLOW Simulations.log summary files
    """

    @property
    def name(self) -> str:
        return "Simulations Log Summary"

    @property
    def match_patterns(self):
        return [
            re.compile(r"_ TUFLOW Simulations\.log$", re.IGNORECASE)
        ]

    # ------------------------------------------------------------
    # Parse log file
    # ------------------------------------------------------------
    def parse(self, contents: bytes) -> pd.DataFrame:

        text = io.StringIO(contents.decode("utf-8", errors="ignore"))

        # ---------- Regex patterns ----------
        START_RE = re.compile(
            r"""
            (?P<dt>\d{4}-[A-Za-z]{3}-\d{2}\s+\d{2}:\d{2})\s+
            Don:\s+(?P<don>\S+)\s+
            \S+\s+
            (?P<computer>\S+)\s+
            Build:\s+(?P<build>\S+).*?
            Started:\s+(?P<run>[^\s"\\]+)
            """,
            re.VERBOSE,
        )

        FINISHED_RE = re.compile(
            r"""
            (?P<dt>\d{4}-[A-Za-z]{3}-\d{2}\s+\d{2}:\d{2}).*?
            Finished:\s+(?P<run>[^\s"\\]+)
            """,
            re.VERBOSE,
        )

        UNSTABLE_RE = re.compile(r"\bUNSTABLE\b", re.IGNORECASE)
        INTERRUPTED_RE = re.compile(r"\bINTERRUPTED\b", re.IGNORECASE)

        # ---------- Event storage ----------
        events_by_run = defaultdict(list)

        # ---------- Helper for optional fields ----------
        def _get(pattern: str, line: str) -> str:
            m = re.search(pattern, line)
            return m.group(1) if m else "--"

        # ---------- Pass 1: collect events ----------
        for line in text:

            s = START_RE.search(line)
            if s:
                events_by_run[s["run"]].append({
                    "time": datetime.strptime(s["dt"], "%Y-%b-%d %H:%M"),
                    "type": "start",
                    "don": s["don"],
                    "computer": s["computer"],
                    "build": s["build"],
                })
                continue

            f = FINISHED_RE.search(line)
            if f:
                events_by_run[f["run"]].append({
                    "time": datetime.strptime(f["dt"], "%Y-%b-%d %H:%M"),
                    "type": "finished",
                    "ini": _get(r"Ini:\s+(\d+:\d+:\d+)", line),
                    "ct": _get(r"\bCT\s+(\d+:\d+:\d+)", line),
                    "tot": _get(r"Tot:\s+(\d+:\d+:\d+)", line),
                    "hardware": _get(r"\b(GPUx\d+|CPUx\d+)\b", line),
                })
                continue

            if UNSTABLE_RE.search(line):
                m = re.search(r"(Started|Finished):\s+([^\s\"\\]+)", line)
                if m:
                    events_by_run[m.group(2)].append({
                        "type": "unstable"
                    })

            if INTERRUPTED_RE.search(line):
                m = re.search(r"(Started|Finished):\s+([^\s\"\\]+)", line)
                if m:
                    events_by_run[m.group(2)].append({
                        "type": "interrupted"
                    })

        # ---------- Resolve starts ----------
        rows = []

        for run, events in events_by_run.items():
            events.sort(key=lambda e: e.get("time", datetime.max))

            for i, evt in enumerate(events):
                if evt["type"] != "start":
                    continue

                status = "Unknown"
                ini = ct = tot = "--"
                pt = "--"
                hw = ""

                # Look forward in time
                for next_evt in events[i + 1:]:

                    if next_evt["type"] == "start":
                        # overridden → Unknown
                        break

                    if next_evt["type"] == "finished":
                        status = "Finished"
                        ini = next_evt["ini"]
                        ct = next_evt["ct"]
                        tot = next_evt["tot"]
                        hw = next_evt["hardware"]
                        break

                    if next_evt["type"] == "unstable":
                        status = "UNSTABLE"
                        break

                    if next_evt["type"] == "interrupted":
                        status = "Interrupted"
                        break

                rows.append({
                    "Start DateTime": evt["time"],
                    "Don": evt["don"],
                    "Computer": evt["computer"],
                    "Build": evt["build"],
                    "Initialisation Time": ini,
                    "Compute Time": ct,
                    "Total Time": tot,
                    "Hardware": hw,
                    "Run Name": run,
                    "Run Status": status,
                })

        df = pd.DataFrame(rows)
        df.sort_values("Start DateTime", inplace=True)

        return df

    # ------------------------------------------------------------
    # Build Plotly table
    # ------------------------------------------------------------
    def make_figure(self, df: pd.DataFrame, filename: str):

        # Row colouring based on Run Status
        row_colours = []
        for status in df["Run Status"]:
            if status == "Finished":
                row_colours.append("rgb(000,182,221)")
            elif status == "Interrupted":
                row_colours.append("rgb(226,001,119)")
            elif status == "UNSTABLE":
                row_colours.append("rgb(226,001,119)")  # red
            else:
                row_colours.append("rgb(216,208,199)")  # grey (Unknown)

        cell_colours = [row_colours for _ in df.columns]

        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(df.columns),
                        fill_color="#003f5c",
                        font=dict(color="white", size=12),
                        align="left",
                    ),
                    cells=dict(
                        values=[df[col] for col in df.columns],
                        fill_color=cell_colours,
                        align="left",
                        height=24,
                    ),
                )
            ]
        )

        fig.update_layout(height=1000)

        return finalise_dashboard(
            fig,
            title=(
                "<b>TUFLOW Simulations Summary</b><br>"
                f"Total Simulations: {len(df)}"
            ),
        )