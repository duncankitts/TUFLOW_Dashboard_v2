"""
MB2D.csv plugin for TUFLOW Dash Dashboard
----------------------------------------
2D Mass Balance summary plots with original
TUFLOW colours and line styles preserved.
"""

import re

import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.parsing import parse_csv
from core.plugin_base import TuflowPlugin
from core.styles import COLOURS, LINE_STYLES
from plotly.subplots import make_subplots


class MB2DPlugin(TuflowPlugin):

    @property
    def name(self) -> str:
        return "2D Mass Balance Summary"

    @property
    def match_patterns(self):
        return [
            # Match *_mb.csv but NOT *_1d_mb.csv
            re.compile(r"(?<!_1d)_mb2D\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, contents: bytes):
        df = parse_csv(contents)

        if df.empty:
            raise ValueError("MB2D.csv file is empty")

        return df

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def make_figure(self, df, filename: str):
        runname = filename[:-9]        
        t = df["Time (h) "]
        
        
        fig = make_subplots(
                rows=2, cols=4,
                subplot_titles=(
                    "<b>H Volume</b>", "<b>S Volume</b>", "<b>Estry Volume</b>", "<b>X1D Volume</b>",
                    "<b>Total Volume</b>", "<b>Q ME(%)</b>", "<b>Cum Volumes</b>"),
                specs=[[{}, {}, {}, {}],
                       [{'secondary_y': True}, {}, {'secondary_y': True}, {}]],
                shared_xaxes='all', x_title='<b>Hours of Simulation</b>')
        # plot one: H Volumes
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['H V In      '],
                             name='Volume in H Boundaries', marker_color='rgb(000,085,129)', hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing into the model across water level (HQ, HS, HT) boundaries since the previous time.")),
                row=1, col=1)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['H V Out     '],
                             name='Volume Out H Boundaries', marker_color='rgb(026,189,201)', hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing out of the model across water level (HQ, HS, HT) boundaries since the previous time.")),
                row=1, col=1)
        # plot one: Q Volumes
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['SS V In     '],
                             name='Volume in S Boundaries', marker_color='rgb(000,085,129)',line=dict(dash="dash"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing into the 2D domain/s from 2D flow sources (RF, SA, SH, ST) boundaries since the previous time.")),
                row=1, col=2)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['SS V Out    '],
                             name='Volume Out S Boundaries', marker_color='rgb(026,189,201)',line=dict(dash="dash"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing out of the 2D domain/s from 2D flow sources (RF, SA, SH, ST) boundaries since the previous time.")),
                row=1, col=2)
        # plot three: Estry Boundary Volumes
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Es HX V In  '],
                             name='Estry HX In', marker_color='rgb(000,085,129)',line=dict(dash="dot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing into the 2D domain/s across HX links to TUFLOW 1D (ESTRY) domains since the previous time. Note, this figure includes any 2D QT boundaries and 2D links as these become HX links connected to hidden 1D nodes.")),
                row=1, col=3)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Es HX V Out '],
                             name='Estry HX Out', marker_color='rgb(026,189,201)',line=dict(dash="dot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing out of the 2D domain/s across HX links to TUFLOW 1D (ESTRY) domains since the previous time. Note, this figure includes any 2D QT boundaries and 2D links as these become HX links connected to hidden 1D nodes.")),
                row=1, col=3)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Es SX V In  '],
                             name='Estry SX In', marker_color='rgb(226,001,119)',line=dict(dash="dot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing into the 2D domain/s through SX links to TUFLOW 1D (ESTRY) domains since the previous time.")),
                row=1, col=3)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Es SX V Out '],
                             name='Estry SX Out', marker_color='rgb(212,208,015)',line=dict(dash="dot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing out of the 2D domain/s through SX links to TUFLOW 1D (ESTRY) domains since the previous time.")),
                row=1, col=3)

        # plot four: X1D Boundary Volumes
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['x1D HX V In '],
                             name='X1D HX In', marker_color='rgb(000,085,129)',line=dict(dash="dashdot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing into the 2D domain/s across HX links to an external 1D scheme since the previous time.")),
                row=1, col=4)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['x1D HX V Out'],
                             name='X1D HX Out', marker_color='rgb(026,189,201)',line=dict(dash="dashdot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing out of the 2D domain/s across HX links to an external 1D scheme since the previous time.")),
                row=1, col=4)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['x1D SX V In '],
                             name='X1D SX In', marker_color='rgb(226,001,119)',line=dict(dash="dashdot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing into the 2D domain/s through SX links to an external 1D scheme since the previous time.")),
                row=1, col=4)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['x1D SX V Out'],
                             name='X1D SX Out', marker_color='rgb(212,208,015)',line=dict(dash="dashdot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The volume of water in m<sup>3</sup> flowing out of the 2D domain/s through SX links to an external 1D scheme since the previous time.")),
                row=1, col=4)
        # plot five: Volume Error
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['V In-Out    '],
                             name='Volume in - Volume Out', marker_color='rgb(000,085,129)',line=dict(dash="longdash"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "Sum of all the volumes in less the sum of all the volumes out (i.e. the net volume of water in m3 entering the 2D domain/s since the previous time).")),
                row=2, col=1)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['dVol        '],
                             name='Change in Volume', marker_color='rgb(026,189,201)',line=dict(dash="longdash"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The change in the 2D domain/s’ volume in m3 since the previous time.")),
                row=2, col=1)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['V Err       '],
                             name='Volume Error (Secondary Axis)', marker_color='#FC1CBF',line=dict(dash="longdash"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "'dVol' minus 'V In-Out' (i.e. the volume error or amount of water in m<sup>3</sup> unaccounted for since the previous time). A positive value indicates the 2D domain/s may have gained mass, while a negative value indicates a possible mass loss.")), secondary_y=True,
                row=2, col=1)
        # plot Six: Q ME(%)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Q ME (%)    '],
                             name='Q Mass Error(%)    ', marker_color='rgb(000,085,129)',line=dict(dash="longdashdot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "('V Err'/(ΣV In + ΣV Out))*100 (i.e. the percentage mass error based on the volume of water flowing through the 2D domain/s since the previous time).")),
                row=2, col=2)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Cum ME (%)  '],
                             name='Cumulative Mass Error(%)  ', marker_color='rgb(026,189,201)',line=dict(dash="longdashdot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "('Cum V Error'/max('Cum V In+Out' and 'Total V'))*100 (i.e. the percentage mass error based on the maximum of the volume of water that has flowed through the 2D domain/s and the total volume of water in the 2D domain/s).")),
                row=2, col=2)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Cum Q ME (%)'],
                             name='Cumulative Q Mass Error(%)', marker_color='rgb(226,001,119)',line=dict(dash="longdashdot"), hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "('Cum V Error'/max('Cum V In+Out' and 'Total V'))*100 (i.e. the percentage mass error based on the maximum of the volume of water that has flowed through the 2D domain/s and the total volume of water in the 2D domain/s). ")),
                row=2, col=2)
        # plot seven: Cum Vol I+O
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Total V     '],
                             name='Total Volume', marker_color='rgb(000,085,129)', hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The total volume of water in m<sup>3</sup> in the 2D domain/s.")),
                row=2, col=3)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Cum V In+Out'],
                             name='Cumulative Volume In + Out', marker_color='rgb(212,208,015)', hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The cumulative volume of water in m<sup>3</sup> entering and leaving the 2D domain/s (i.e. the cumulative total of (ΣV In + ΣV Out)).")),
                row=2, col=3)
        fig.add_trace(
                go.Scattergl(x=df['Time (h) '], y=df['Cum V Error '],
                             name='Cumulative Volume Error (Secondary Axis)', marker_color='#FC1CBF', hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Time: %{x}<br>"
                        "Value: %{y}<br>"
                        "The cumulative volume error in m<sup>3</sup> (i.e. the cumulative total of “V Err”).")),
                secondary_y=True,
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
        fig.update_yaxes(row=2, col=3, title_text="<b>Volume Error(m<sup>3</sup>)</b>", secondary_y=True)

        fig.update_layout(template="plotly_white", title_text="<b>TUFLOW MB2D Summary Graphs for <b>" + runname,
                          height = 650, title_font_size=24)


        # --------------------------------------------------------------
        # Final formatting
        # --------------------------------------------------------------
        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW MB2D Summary – {runname}</b>",
        )

        return fig