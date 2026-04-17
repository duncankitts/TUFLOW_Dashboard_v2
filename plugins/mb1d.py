"""
MB1D.csv plugin for TUFLOW Dash Dashboard
----------------------------------------
1D Mass Balance summary plots
"""

import re

import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.parsing import parse_csv
from core.plugin_base import TuflowPlugin
from plotly.subplots import make_subplots


class MB1DPlugin(TuflowPlugin):
    """
    Handles TUFLOW *MB1D.csv files
    """

    @property
    def name(self) -> str:
        return "1D Mass Balance Summary"

    @property
    def match_patterns(self):
        return [
            # Match *_mb.csv but NOT *_1d_mb.csv
            re.compile(r"(?<!_1d)_mb1D\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, contents: bytes):
        df = parse_csv(contents)

        if df.empty:
            raise ValueError("MB1D.csv file is empty")

        return df

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def make_figure(self, df, filename: str):
        fig = make_subplots(
                rows=2, cols=4,
                subplot_titles=(
                    "<b>H Volume</b>", "<b>S Volume</b>", "<b>Estry Volume</b>", "<b>X1D Volume</b>",
                    "<b>Total Volume</b>", "<b>Q ME(%)</b>", "<b>Cum Volumes</b>"),
                specs=[[{}, {}, {}, {}],
                       [{'secondary_y': True}, {}, {'secondary_y': True}, {}]],
                shared_xaxes='all', x_title='<b>Hours of Simulation</b>')
        # plot one: H Volume
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['H V In      '],
                         name='Volume in H Boundaries', marker_color='rgb(000,085,129)',hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing into all 1D domains at 1D water level (HQ, HS, HT) boundaries since the previous time.")),
            row=1, col=1)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['H V Out     '],
                         name='Volume Out H Boundaries', marker_color='rgb(026,189,201)',hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing out of all 1D domains at 1D water level (HQ, HS, HT) boundaries since the previous time.")),
            row=1, col=1)
        # plot one: Q Volumes
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Q V In      '],
                         name='Volume in Q Boundaries', marker_color='rgb(000,085,129)',line=dict(dash='dash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing into all 1D domains from 1D flow (QH, QS, QT) boundaries, except for 1D QT Regions, since the previous time.")),
            row=1, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Q V Out     '],
                         name='Volume Out Q Boundaries', marker_color='rgb(026,189,201)',line=dict(dash='dash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing out of all 1D domains from 1D flow (QH, QS, QT) boundaries, except for 1D QT Regions since the previous time.")),
            row=1, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['QR V In     '],
                         name='Volume in S/RF Boundaries', marker_color='rgb(226,001,119)',line=dict(dash='dash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing into all 1D domains from 1D QT Region flow boundaries, since the previous time.")),
            row=1, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['QR V Out    '],
                         name='Volume Out S/RF Boundaries', marker_color='rgb(212,208,015)',line=dict(dash='dash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing out of all 1D domains from 1D QT Region flow boundaries, since the previous time.")),
            row=1, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Q2D V In    '],
                         name='2D Volume In', marker_color='rgb(000,182,221)',line=dict(dash='dash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing into hidden 1D nodes from 2D QT flow boundaries, since the previous time.")),
            row=1, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Q2D V Out   '],
                         name='2D Volume Out', marker_color='rgb(126,209,225)',line=dict(dash='dash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing out of hidden 1D nodes from 2D QT flow boundaries, since the previous time.")),
            row=1, col=2)
        # plot three: Estry Boundary Volumes
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['HX2D V In   '],
                         name='HX In', marker_color='rgb(000,085,129)',line=dict(dash='dot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing into all 1D domains across 2D HX links since the previous time.")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['HX2D V Out  '],
                         name='HX Out', marker_color='rgb(026,189,201)',line=dict(dash='dot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing out of all 1D domains across 2D HX links since the previous time.")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['SX2D V In   '],
                         name='SX In', marker_color='rgb(226,001,119)',line=dict(dash='dot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing into all 1D domains from 2D SX links since the previous time.")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['SX2D V Out  '],
                         name='SX Out', marker_color='rgb(212,208,015)',line=dict(dash='dot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing out of all 1D domains from 2D SX links since the previous time.")),
            row=1, col=3)

        # plot four: X1D Boundary Volumes
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['X1DH V In   '],
                         name='X1DH In', marker_color='rgb(000,085,129)',line=dict(dash='dashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume in, in m<sup>3</sup>, since the previous time via External X1DH boundaries.")),
            row=1, col=4)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['X1DH V Out  '],
                         name='X1DH Out', marker_color='rgb(026,189,201)',line=dict(dash='dashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume Out, in m<sup>3</sup>, since the previous time via External X1DH boundaries.")),
            row=1, col=4)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['X1DQ V In   '],
                         name='X1DQ In', marker_color='rgb(226,001,119)',line=dict(dash='dashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume In, in m <sup>3</sup>, since the previous time via External X1DQ boundaries.")),
            row=1, col=4)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['X1DQ V Out  '],
                         name='X1DQ Out', marker_color='rgb(212,208,015)',line=dict(dash='dashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Volume Out, in m <sup>3</sup>, since the previous time via External X1DQ boundaries.")),
            row=1, col=4)
        # plot five: Volume Error
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Vol In-Out  '],
                         name='Volume in - Volume Out', marker_color='rgb(000,085,129)',line=dict(dash='longdash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "Sum of all the volumes in less the sum of all the volumes out (i.e. the net volume of water in m<sup>3</sup> entering all the 1D domains since the previous time).")),
            row=2, col=1)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['dVol        '],
                         name='Change in Volume', marker_color='rgb(026,189,201)',line=dict(dash='longdash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The change in the 1D domains’ volume in m<sup>3</sup> since the previous time.")),
            row=2, col=1)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Vol Err     '],
                         name='Volume Error (Secondary Axis)', marker_color='#FC1CBF',line=dict(dash='longdash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "'dVol' minus “Vol In-Out” (i.e. the volume error or amount of water in m<sup>3</sup> unaccounted for since the previous time). A positive value indicates the 1D domains may have gained mass, while a negative value indicates a possible mass loss.")), secondary_y=True,
            row=2, col=1)
        # plot Six: Q ME(%)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Q ME (%)    '],
                         name='Q Mass Error(%)    ', marker_color='rgb(000,085,129)',line=dict(dash='longdashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "('Vol Err'/(ΣV In + ΣV Out))*100 (i.e. the percentage mass error based on the volume of water flowing through the 1D domains since the previous time).")),
            row=2, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Cum ME (%)  '],
                         name='Cumulative Mass Error(%)    ', marker_color='rgb(026,189,201)',line=dict(dash='longdashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "('Cum Vol Error'/max('Cum Vol In+Out' and 'Total Vol'))*100 (i.e. the percentage mass error based on the maximum of the volume of water that has flowed through the 1D domains and the total volume of water in the 1D domains). ")),
            row=2, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Cum Q ME (%)'],
                         name='Cumulative Q Mass Error(%)    ', marker_color='rgb(226,001,119)',line=dict(dash='longdashdot'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "'Cum Vol Error'/'“Cum Vol In+Out')*100 (i.e. the percentage mass error based on the volume of water that has flowed through the 1D domains).")),
            row=2, col=2)
        # plot seven: Cum Vol I+O
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Total Vol   '],
                         name='Total Volume', marker_color='rgb(000,085,129)',line=dict(dash='longdash'),hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The total volume of water in m<sup>3</sup> in the 1D domains.")),
            row=2, col=1)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Cum Vol I+O '],
                         name='Cumulative Volume In + Out', marker_color='rgb(212,208,015)',hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The cumulative volume of water in m<sup>3</sup> entering and leaving the 1D domains (i.e. the cumulative total of (ΣV In + ΣV Out)).")),
            row=2, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h) '], y=df['Cum Vol Err '],
                         name='Cumulative Volume Error (Secondary Axis)', marker_color='#FC1CBF',hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The cumulative volume error in m<sup>3</sup> (i.e. the cumulative total of “Vol Err”).")),
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

        runname = filename[:-9]
        fig.update_layout(template="plotly_white", title_text="<b>TUFLOW MB 1D Summary Graphs for <b>" + runname,
                          height = 650, title_font_size=24)
       

        # --------------------------------------------------------------
        # Final formatting
        # --------------------------------------------------------------
        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW MB1D Summary – {runname}</b>",
        )

        return fig