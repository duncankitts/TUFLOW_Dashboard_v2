import io
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.layout import finalise_dashboard
from core.plugin_base import TuflowPlugin
from core.styles import COLOURS


COORDINATE_COLUMNS = ("ctrd_x", "ctrd_y")
DATA_COLUMNS = ("cfl_dt_min", "cfl_dt_mean")
SENTINEL_VALUES = (-99999, 4999.5)
DEFAULT_Z_COLUMN = "cfl_dt_min"


class CFLDTPlugin(TuflowPlugin):

    @property
    def name(self):
        return "CFL DT"

    @property
    def match_patterns(self):
        return [
            re.compile(r"_ext_cfl_dt\.csv$|_int_cfl_dt\.csv$", re.IGNORECASE)
        ]

    def parse(self, contents: bytes) -> pd.DataFrame:
        df = pd.read_csv(
            io.StringIO(contents.decode("utf-8")),
            engine="python"
        )

        for col in COORDINATE_COLUMNS + DATA_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df.replace(SENTINEL_VALUES, np.nan, inplace=True)

        return df

    @staticmethod
    def _percentile_levels(step: int = 5):
        return np.arange(0, 101, step)

    @staticmethod
    def _percentile_color_values(values: np.ndarray, reference_values: np.ndarray):
        values = np.asarray(values, dtype=float)
        reference_values = np.asarray(reference_values, dtype=float)

        reference_values = reference_values[np.isfinite(reference_values)]
        if reference_values.size == 0:
            return np.full(values.shape, np.nan, dtype=float)

        reference_percentiles = np.percentile(
            reference_values,
            np.linspace(0, 100, 101)
        )
        reference_scale = np.linspace(0, 100, len(reference_percentiles))

        return np.interp(values, reference_percentiles, reference_scale)

    @staticmethod
    def _build_filtered_data(df: pd.DataFrame, z_column: str, percentile: float):
        x = df["ctrd_x"].to_numpy(dtype=float)
        y = df["ctrd_y"].to_numpy(dtype=float)
        z = df[z_column].to_numpy(dtype=float)

        if z.size == 0:
            return x, y, z

        finite = np.isfinite(z)
        z_finite = z[finite]
        if z_finite.size == 0:
            return np.array([]), np.array([]), np.array([])

        cutoff = np.percentile(z_finite, percentile)
        mask = (
            np.isfinite(x)
            & np.isfinite(y)
            & np.isfinite(z)
            & (z <= cutoff)
        )

        return x[mask], y[mask], z[mask]

    @staticmethod
    def _build_histogram_arrays(values: np.ndarray, reference_values: np.ndarray):
        values = np.asarray(values, dtype=float)
        reference_values = np.asarray(reference_values, dtype=float)

        finite_values = values[np.isfinite(values)]
        if finite_values.size == 0:
            return np.array([]), np.array([], dtype=float), np.array([])

        counts, bin_edges = np.histogram(finite_values, bins="auto")
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        bin_colors = CFLDTPlugin._percentile_color_values(bin_centers, reference_values)
        return bin_centers, counts.astype(float), bin_colors

    def _build_scatter_trace(self, x, y, z, reference_values, z_column: str):
        z_percentile_values = self._percentile_color_values(z, reference_values)
        colorbar_title = "CFL Minimum Timestep"
        if z_column == "cfl_dt_mean":
            colorbar_title = "CFL Mean Timestep"

        return go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(
                size=8,
                color=z_percentile_values,
                colorscale=[[0.0, "rgb(226,001,119)"], [0.5, "#FFFFFF"], [1.0, "#005581"]],
                cmin=0.0,
                cmax=100.0,
                showscale=True,
                colorbar=dict(title=f"{colorbar_title} (percentile)")
            ),
            customdata=z,
            hovertemplate=(
                "ctrd_x: %{x}<br>"
                "ctrd_y: %{y}<br>"
                f"{z_column}: %{{customdata}}<extra></extra>"
            ),
            name=z_column,
            showlegend=False
        )

    def _build_histogram_trace(self, values, reference_values, z_column: str):
        bin_centers, counts, bin_colors = self._build_histogram_arrays(values, reference_values)

        return go.Bar(
            x=bin_centers,
            y=counts,
            marker=dict(
                color=bin_colors,
                colorscale=[[0.0, "rgb(226,001,119)"], [0.5, "#FFFFFF"], [1.0, "#005581"]],
                cmin=0.0,
                cmax=100.0,
                line=dict(color="rgba(0, 0, 0, 0.2)", width=1)
            ),
            hovertemplate=(
                "Timestep bin: %{x}<br>"
                "Count: %{y}<extra></extra>"
            ),
            name=f"{z_column} histogram",
            showlegend=False
        )

    def _build_slider_layout(self, df: pd.DataFrame, z_column: str, reference_values=None):
        z_values = df[z_column].to_numpy(dtype=float)
        thresholds = CFLDTPlugin._percentile_levels()

        if reference_values is None:
            reference_values = z_values

        if thresholds.size == 0:
            return {"steps": []}

        steps = []
        for threshold in thresholds:
            x, y, z = CFLDTPlugin._build_filtered_data(df, z_column, float(threshold))
            z_percentile_values = self._percentile_color_values(z, reference_values)
            steps.append(
                dict(
                    method="update",
                    args=[
                        {
                            "x": [x],
                            "y": [y],
                            "marker.color": [z_percentile_values],
                            "customdata": [z],
                            "hovertemplate": [
                                (
                                    "ctrd_x: %{x}<br>"
                                    "ctrd_y: %{y}<br>"
                                    f"{z_column}: %{{customdata}}<extra></extra>"
                                )
                            ],
                            "name": [z_column],
                        },
                        {},
                        [0],
                    ],
                    label=f"< {int(round(float(threshold)))}%"
                )
            )

        return dict(
            active=len(steps) - 1,
            currentvalue={"prefix": "<b>Show points with timestep in bottom </b>"},
            steps=steps,
            pad={"t": 40},
            x=0.0,
            y=-0.15,
            lenmode="fraction",
            len=1.0,
        )

    def make_figure(self, df: pd.DataFrame, filename: str):
        runname = re.sub(
            r"(_ext|_int)_cfl_dt\.csv$",
            "",
            filename,
            flags=re.IGNORECASE
        )

        z_column = DEFAULT_Z_COLUMN
        z_values = df[z_column].to_numpy(dtype=float)
        z_values = z_values[np.isfinite(z_values)]

        if z_values.size == 0:
            raise ValueError("No CFL-DT values found")

        default_threshold = 100.0
        x, y, z = self._build_filtered_data(df, z_column, default_threshold)

        colorbar_title = "CFL Minimum Timestep"
        if z_column == "cfl_dt_mean":
            colorbar_title = "CFL Mean Timestep"

        scatter_trace = self._build_scatter_trace(x, y, z, z_values, z_column)
        histogram_trace = self._build_histogram_trace(z_values, z_values, z_column)

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=False,
            vertical_spacing=0.22,
            row_heights=[0.72, 0.28],
        )
        fig.add_trace(scatter_trace, row=1, col=1)
        fig.add_trace(histogram_trace, row=2, col=1)

        base_x = df["ctrd_x"].to_numpy(dtype=float)
        base_y = df["ctrd_y"].to_numpy(dtype=float)
        base_z = df[z_column].to_numpy(dtype=float)
        valid = np.isfinite(base_x) & np.isfinite(base_y) & np.isfinite(base_z)
        base_x = base_x[valid]
        base_y = base_y[valid]
        base_z = base_z[valid]

        dropdown_buttons = []
        for option in ["cfl_dt_min", "cfl_dt_mean"]:
            option_values = df[option].to_numpy(dtype=float)
            option_values = option_values[np.isfinite(option_values)]
            if option_values.size == 0:
                continue

            default_threshold = 100.0
            x_opt, y_opt, z_opt = self._build_filtered_data(df, option, default_threshold)
            option_values = df[option].to_numpy(dtype=float)
            option_values = option_values[np.isfinite(option_values)]
            hist_x_opt, hist_y_opt, hist_colors_opt = self._build_histogram_arrays(option_values, option_values)
            z_opt_percentiles = self._percentile_color_values(z_opt, option_values)
            slider_layout = self._build_slider_layout(df, option, reference_values=option_values)
            dropdown_buttons.append(
                dict(
                    method="update",
                    label=option,
                    args=[
                        {
                            "x": [x_opt, hist_x_opt],
                            "y": [y_opt, hist_y_opt],
                            "marker.color": [z_opt_percentiles, hist_colors_opt],
                            "customdata": [z_opt, None],
                            "hovertemplate": [
                                (
                                    "ctrd_x: %{x}<br>"
                                    "ctrd_y: %{y}<br>"
                                    f"{option}: %{{customdata}}<extra></extra>"
                                ),
                                "Timestep bin: %{x}<br>Count: %{y}<extra></extra>"
                            ],
                            "name": [option, f"{option} histogram"],
                        }
                    ]
                )
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    type="dropdown",
                    buttons=dropdown_buttons,
                    direction="down",
                    showactive=True,
                    x=1.02,
                    y=1.0,
                    yanchor="top",
                    bgcolor="white",
                    bordercolor=COLOURS.get("blue_main", "#1f77b4")
                )
            ],
            sliders=[self._build_slider_layout(df, z_column)],
            title=dict(text=f"<b>TUFLOW FV CFL Timestep - {runname}</b>", x=0.5),
            xaxis_title="<b>ctrd_x</b>",
            yaxis_title="<b>ctrd_y</b>",
            xaxis2_title="<b>Timestep value (s)</b>",
            yaxis2_title="<b>Count</b>",
            xaxis_range=[np.nanmin(base_x), np.nanmax(base_x)],
            yaxis_range=[np.nanmin(base_y), np.nanmax(base_y)],
            height=700,
            showlegend=False,
            margin=dict(l=40, r=140, t=80, b=80),
            legend=dict(yanchor="top", y=1.0, xanchor="left", x=1.02),
        )

        fig.update_traces(
            selector=dict(type="scatter"),
            marker=dict(colorbar=dict(
                x=1.02,
                y=0.7,
                len=0.55,
                yanchor="middle",
                xanchor="left",
                thickness=20,
                outlinewidth=0,
                title=dict(text="Percentile")
            ))
        )

        fig.update_yaxes(row=2, col=1, domain=[0.0, 0.22])
        fig.update_layout(
            shapes=[
                dict(
                    type="rect",
                    xref="paper",
                    yref="paper",
                    x0=0.96,
                    x1=1.0,
                    y0=0.05,
                    y1=0.68,
                    fillcolor="rgba(255,255,255,0.0)",
                    line=dict(width=0),
                )
            ]
        )

        return finalise_dashboard(
            fig,
            title=(f"<b>TUFLOW FV CFL Timestep - {runname}</b>")
        )
