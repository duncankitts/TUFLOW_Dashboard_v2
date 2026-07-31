import io
import os
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.layout import finalise_dashboard
from core.plugin_base import TuflowPlugin
from core.styles import COLOURS


class FV_wq_mb_Plugin(TuflowPlugin):

    @property
    def name(self):
        return "TUFLOW FV MASS Balance Output"

    @property
    def match_patterns(self):
        return [
            re.compile(r"massbalance(?:_[^/\\]+)?\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, contents: bytes) -> pd.DataFrame:

        raw = pd.read_csv(
            io.StringIO(contents.decode("utf-8")),
            header=None,
            index_col=False,
            engine="python",
            skip_blank_lines=True
        )

        if raw.empty:
            return pd.DataFrame(columns=["Time"])

        header_idx = None
        for idx in range(min(len(raw), 3)):
            row = raw.iloc[idx].astype(str).str.strip()
            if row.isna().all() or (row == "").all():
                continue
            values = [str(v).strip() for v in row.tolist() if str(v).strip()]
            if not values:
                continue
            if values[0].lower() in {"time", "datetime", "date"}:
                header_idx = idx
                break

        if header_idx is None:
            header_idx = 0

        headers = raw.iloc[header_idx].astype(str).str.strip().tolist()
        headers = [h if h else f"Column {i + 1}" for i, h in enumerate(headers)]

        df = raw.iloc[header_idx + 1:].reset_index(drop=True).copy()
        if df.empty:
            return pd.DataFrame(columns=["Time"])

        df.columns = headers

        # Drop a leading path/file-like column if present.
        if df.shape[1] > 1:
            first_col_name = str(df.columns[0]).strip().lower()
            if "path" in first_col_name or "file" in first_col_name:
                df = df.iloc[:, 1:].reset_index(drop=True)
                df.columns = headers[1:]

        cleaned_headers = []
        for col in df.columns:
            name = str(col).strip()
            if not name:
                name = "Column"
            if name.lower() == "time":
                name = "Time"
            cleaned_headers.append(name)
        df.columns = cleaned_headers

        df.replace(-99999, np.nan, inplace=True)

        if "Time" not in df.columns:
            time_col = None
            for col in df.columns:
                if re.search(r"time", str(col).lower()):
                    time_col = col
                    break
            if time_col is not None:
                df = df.rename(columns={time_col: "Time"})

        for col in df.columns:
            if col == "Time":
                try:
                    df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                except Exception:
                    pass
            else:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(" ", "", regex=False),
                    errors="coerce"
                )

        return df

    # ------------------------------------------------------------
    # PLOT
    # ------------------------------------------------------------
    def make_figure(self, df: pd.DataFrame, filename: str):

        base = os.path.splitext(filename)[0]
        determinant_match = re.search(r"massbalance_([^/\\]+)$", base, re.IGNORECASE)
        determinant = determinant_match.group(1) if determinant_match else "mass balance"
        runname = re.sub(r"(?:^|_)(massbalance(?:_[^/\\]+)?)$", "", base, flags=re.IGNORECASE)
        runname = runname.strip("_") or "TUFLOW FV"

        if df.empty or df.shape[1] < 2:
            fig = go.Figure()
            fig.add_annotation(
                text="<b>No FV mass balance data found</b><br>"
                     "The file could not be parsed into time-series columns.",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14),
                align="center"
            )
            fig.update_layout(
                title=dict(text=f"<b>TUFLOW FV {determinant.title()} Mass Balance</b>", x=0.5),
                height=300,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                margin=dict(l=20, r=20, t=60, b=20)
            )
            return fig

        time_col = None
        for col in df.columns:
            if re.search(r"time", str(col).lower()):
                time_col = col
                break

        if time_col is None:
            time_col = df.columns[0]

        data_cols = [col for col in df.columns if col != time_col]
        if not data_cols:
            raise ValueError("MASSBALANCE.csv contains no output columns")

        mass_column = next((col for col in data_cols if re.search(r"(vol|mass)", str(col).lower()) and "flux" not in str(col).lower()), data_cols[0])
        mass_flux_columns = [
            col for col in data_cols
            if col != mass_column and "flux" in str(col).lower()
        ]
        other_columns = [
            col for col in data_cols
            if col not in {mass_column, "MF_PCT_ERROR", "MF_TURNOVERS"} and col not in mass_flux_columns
        ]

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            subplot_titles=("<b>Mass Balance</b>", "<b>Fluxes</b>"),
            specs=[[{"type": "xy", "secondary_y": True}], [{"type": "xy", "secondary_y": True}]]
        )

        fig.add_trace(
            go.Scatter(
                x=df[time_col],
                y=df[mass_column],
                mode="lines",
                line=dict(color=COLOURS.get("blue_main", "#005581")),
                name="Mass / Volume",
                legendgroup="Mass Output"
            ),
            row=1,
            col=1
        )

        for idx, col in enumerate(mass_flux_columns):
            fig.add_trace(
                go.Scatter(
                    x=df[time_col],
                    y=df[col],
                    mode="lines",
                    name=col,
                    legendgroup="Mass Output",
                    line=dict(color=COLOURS.get("cyan_main", "#1ABDC9"))
                ),
                row=1,
                col=1
            )

        if "MF_PCT_ERROR" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df[time_col],
                    y=df["MF_PCT_ERROR"],
                    mode="lines",
                    name="Percentage Error",
                    legendgroup="Mass Output",
                    line=dict(dash="dash", color="Red")
                ),
                row=1,
                col=1,
                secondary_y=True
            )

        for idx, col in enumerate(other_columns):
            fig.add_trace(
                go.Scatter(
                    x=df[time_col],
                    y=df[col],
                    mode="lines",
                    name=col,
                    legendgroup="Mass Flux",
                    line=dict(color=[COLOURS.get("blue_main", "#1f77b4"), COLOURS.get("orange_main", "#ff7f0e"), COLOURS.get("green_main", "#2ca02c")][idx % 3])
                ),
                row=2,
                col=1
            )

        if "MF_TURNOVERS" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df[time_col],
                    y=df["MF_TURNOVERS"],
                    mode="lines",
                    name="Turnovers",
                    legendgroup="Mass Flux",
                    line=dict(dash="dash", color="Blue")
                ),
                row=2,
                col=1,
                secondary_y=True
            )

        if determinant.lower() == "volume":
            fig.update_yaxes(title_text="<b>Pollutant Volume</b>", row=1, col=1)
            fig.update_yaxes(title_text="<b>Pollutant Volume Flux</b>", row=2, col=1)
        else:
            fig.update_yaxes(title_text="<b>Pollutant Mass</b>", row=1, col=1)
            fig.update_yaxes(title_text="<b>Pollutant Mass Flux</b>", row=2, col=1)

        fig.update_yaxes(title_text="<b>Percentage error (%)</b>", row=1, col=1, secondary_y=True)
        fig.update_yaxes(title_text="<b>Turnover (-)</b>", row=2, col=1, secondary_y=True)

        fig.update_layout(
            height=800,
            title_text=f"<b>TUFLOW FV Mass Balance Analysis for {determinant} for {runname}</b>",
            title_x=0.4,
            showlegend=True,
            margin=dict(l=50, r=260, t=80, b=50)
        )

        fig = finalise_dashboard(
            fig,
            title=(
                f"<b>TUFLOW FV {determinant.title()} Mass Balance Outputs - {runname}</b>"
            )
        )

        fig.update_layout(
            legend=dict(
                orientation="v",
                x=1.02,
                y=0.98,
                xanchor="left",
                yanchor="top"
            )
        )

        return fig