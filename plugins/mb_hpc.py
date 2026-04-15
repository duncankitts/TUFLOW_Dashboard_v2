"""
MB_HPC.csv plugin for TUFLOW Dash Dashboard
------------------------------------------
HPC Mass Balance summary plots
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from core.plugin_base import TuflowPlugin
from core.parsing import parse_csv
from core.layout import finalise_dashboard


class MBHPCPlugin(TuflowPlugin):
    """
    Handles TUFLOW *MB_HPC.csv files
    """

    @property
    def name(self) -> str:
        return "HPC Mass Balance Summary"

    @property
    def match_patterns(self):
        return [
            # Match *_mb.csv but NOT *_1d_mb.csv
            re.compile(r"(?<!_1d)_mb_hpc\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, contents: bytes):
        df = parse_csv(contents)

        if df.empty:
            raise ValueError("MB_HPC.csv file is empty")

        return df

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def make_figure(self, df, filename: str):
        fig = make_subplots(
                rows=2, cols=4,
                subplot_titles=(
                    "<b>H Volume</b>", "<b>S Volume</b>", "<b>Estry Volume</b>", "<b>X1D Volume</b>",
                    "<b>Total Volume</b>", "<b>Q ME(%)</b>", "<b>Cumulative Volumes</b>"),
                specs=[[{}, {}, {}, {}],
                       [{'secondary_y': True}, {}, {}, {}]],
                shared_xaxes='all', x_title='<b>Hours of Simulation</b>')
        # plot one: H Volumes
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['H V In      '],
                         name='Volume in H Boundaries', marker_color='rgb(000,085,129)', hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume in since the previous time via 2D H boundaries (HQ, HT).")),
            row=1, col=1)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['H V Out     '],
                         name='Volume Out H Boundaries', marker_color='rgb(026,189,201)', hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume out since the previous time via 2D H boundaries (HQ, HT).")),
            row=1, col=1)
        # plot one: Q Volumes
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['S/RF Vol In '],
                         name='Volume in S/RF Boundaries', marker_color='rgb(000,085,129)',line=dict(dash='dash'), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume in since the previous time from 2D source boundaries (RF, SA, ST, subsurface water return, infiltration).")),
            row=1, col=2)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['S/RF Vol Out'],
                         name='Volume Out S/RF Boundaries', marker_color='rgb(026,189,201)',line=dict(dash='dash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume out since the previous time from 2D source boundaries (RF, SA, ST, infiltration).")),
            row=1, col=2)
        # plot three: Estry Boundary Volumes
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['Es HX V In  '],
                         name='Estry HX In', marker_color='rgb(000,085,129)',line=dict(dash='dot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume in since the previous time via 2D HX boundaries.")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['Es HX V Out '],
                         name='Estry HX Out', marker_color='rgb(026,189,201)',line=dict(dash='dot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume out since the previous time via 2D HX boundaries.")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['Es SX V In  '],
                         name='Estry SX In', marker_color='rgb(226,001,119)',line=dict(dash='dot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume in since the previous time via 2D SX boundaries.")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['Es SX V Out '],
                         name='Estry SX Out', marker_color='rgb(212,208,015)',line=dict(dash='dot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume out since the previous time via 2D SX boundaries.")),
            row=1, col=3)

        # plot four: X1D Boundary Volumes
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['x1D HX V In '],
                         name='X1D HX In', marker_color='rgb(000,085,129)',line=dict(dash='dashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume in since the previous time via External 1D HX boundaries")),
            row=1, col=4)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['x1D HX V Out'],
                         name='X1D HX Out', marker_color='rgb(026,189,201)',line=dict(dash='dashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume out since the previous time via External 1D HX boundaries")),
            row=1, col=4)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['x1D SX V In '],
                         name='X1D SX In', marker_color='rgb(226,001,119)',line=dict(dash='dashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume in since the previous time via External 1D SX boundaries")),
            row=1, col=4)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['x1D SX V Out'],
                         name='X1D SX Out', marker_color='rgb(212,208,015)',line=dict(dash='dashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume out since the previous time via External 1D SX boundaries")),
            row=1, col=4)
        # plot five: Volume Error
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['V In-Out    '],
                         name='Volume in - Volume Out', marker_color='rgb(000,085,129)',line=dict(dash='longdash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume In less Volume Out of 2D domain.")),
            row=2, col=1)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['dVol        '],
                         name='Change in Volume', marker_color='rgb(026,189,201)',line=dict(dash='longdash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Change in total volume of water within 2D domain.")),
            row=2, col=1)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['V Err       '],
                         name='Volume Error (Secondary Axis)', marker_color='#FC1CBF', line=dict(dash='longdash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "'dVol' less 'V In-Out'.")), secondary_y=True,
            row=2, col=1)
        # plot Six: Q ME(%)
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['Q ME (%)'],
                         name='Q Mass Error(%)    ', marker_color='rgb(000,085,129)',line=dict(dash='longdashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume in since the previous time via 2D H boundaries (HQ, HT)..")),
            row=2, col=2)
        # plot seven: Cum Vol I+O
        fig.add_trace(
            go.Scattergl(x=df['   Time (h) '], y=df['Total V     '],
                         name='Total Volume', marker_color='#FC1CBF',hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Mass error expressed as a percentage of 'V Err'/(Vin + Vout).")),
            row=2, col=3)

        # Update yaxis properties
        fig.update_yaxes(row=1, col=1, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=1, col=2, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=1, col=3, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=1, col=4, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=2, col=1, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=2, col=1, title_text="<b>Volume Error(m<sup>3</sup>)</b>", secondary_y=True)
        fig.update_yaxes(row=2, col=2, title_text="<b>Error %</b>")
        fig.update_yaxes(row=2, col=3, title_text="<b>Volume (m<sup>3</sup>)</b>")

        runname = filename[:-11]
        fig.update_layout(template="plotly_white", title_text="<b>TUFLOW HPC_MB Summary Graphs for <b>" + runname,
                          title_font_size=24)


        # --------------------------------------------------------------
        # Final formatting
        # --------------------------------------------------------------
        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW MB_HPC Summary – {runname}</b>",
        )

        return fig