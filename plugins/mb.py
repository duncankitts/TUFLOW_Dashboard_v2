"""
MB.csv plugin for TUFLOW Dash Dashboard
--------------------------------------
Mass Balance summary plots
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from core.plugin_base import TuflowPlugin
from core.parsing import parse_csv
from core.layout import finalise_dashboard


class MBPlugin(TuflowPlugin):
    """
    Handles TUFLOW *MB.csv files
    """

    @property
    def name(self) -> str:
        return "Mass Balance Summary"

    @property
    def match_patterns(self):
        return [
            # Match *_mb.csv but NOT *_1d_mb.csv
            re.compile(r"(?<!_1d)_mb\.csv$", re.IGNORECASE),
        ]

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, contents: bytes):
        df = parse_csv(contents)

        if df.empty:
            raise ValueError("MB.csv file is empty")

        return df

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def make_figure(self, df, filename: str):

        fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=(
                    "<b>H Volume</b>", "<b>Q Volume</b>", "<b>Total Volume</b>",
                    "<b>Volume Err</b>", "<b>Q ME(%)</b>", "<b>Cum Volumes</b>"),
                specs=[[{}, {}, {'secondary_y': True}],
                       [{'secondary_y': True}, {}, {'secondary_y': True}]],
                shared_xaxes='all', x_title='<b>Hours of Simulation</b>')
        # plot one: H Volumes
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['H Vol In    '],
                         name='H Vol In', marker_color='rgb(000,085,129)', hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing into the model across water level (HQ, HS, HT) boundaries since the previous time.")),
            row=1, col=1)

        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['H Vol Out   '],
                         name='H Vol Out', marker_color='rgb(026,189,201)', hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing out of the model across water level (HQ, HS, HT) boundaries since the previous time.")),
            row=1, col=1)
        # plot two: Q Volumes
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Q Vol In    '],
                         name='Q Vol In', marker_color='rgb(000,085,129)',line=dict(dash="dash"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing into the model from flow (QH, QS, QT, RF, SA, ST) boundaries since the previous time.")),
            row=1, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Q Vol Out   '],
                         name='Q Vol Out', marker_color='rgb(026,189,201)',line=dict(dash="dash"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The volume of water in m<sup>3</sup> flowing out of the model across flow (QH, QS, QT, RF, SA, ST) boundaries since the previous time.")),
            row=1, col=2)
        # plot three: Total Volumes
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Tot Vol In  '],
                         name='Total Vol In', marker_color='rgb(226,001,119)',line=dict(dash="dot"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The total volume of water entering the model since the previous time in m<sup>3</sup>.")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Tot Vol Out '],
                         name='Total Vol Out', marker_color='rgb(026,189,201)',line=dict(dash="dot"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The total volume of water leaving the model since the previous time in m<sup>3</sup>.")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Vol I-O     '],
                         name='Total Vol In-Out', marker_color='rgb(000,085,129)',line=dict(dash="dot"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "'Tot Vol In' minus 'Tot Vol Out' (i.e. the net volume of water in m<sup>3</sup> entering the model since the previous time).")),
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Vol I+O     '],
                         name='Vol In + Out', marker_color='rgb(000,085,129)',line=dict(dash="dashdot"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "'Tot Vol In' + 'Tot Vol Out' (i.e. the volume of water in m<sup>3</sup> entering and leaving the model since the previous time).")),
            row=1, col=3)
        # plot four: Volume Error
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['dVol        '],
                         name=''
                              'Change in Volume (Secondary Axis)', marker_color='rgb(212,208,015)',line=dict(dash="dot"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The change in the model’s volume since the previous time in m<sup>3</sup>.")),secondary_y=True,
            row=1, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Vol Err     '],
                         name='Volume Error (Secondary Axis)', marker_color='#FC1CBF', line=dict(dash='dash'), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "'dVol' minus 'Vol I-O' (i.e. the volume error or amount of water in m<sup>3</sup> unaccounted for since the previous time). A positive value indicates the solution may have gained mass, while a negative value indicates a possible mass loss.")),
            secondary_y=True, row=2, col=1)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Tot Vol     '],
                         name='Total Volume', marker_color='rgb(000,085,129)',line=dict(dash="dashdot"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The total volume of water in the model in m<sup>3</sup>.")),
            row=2, col=1)
        # plot five: Q ME(%)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Q ME (%)    '],
                         name='Q Mass Error (%)', marker_color='rgb(000,085,129)',line=dict(dash="longdash"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "('Vol Err'/'Vol I+O')*100 (i.e. the percentage mass error based on the volume of water flowing through the model since the previous time).")),
            row=2, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Cum ME (%)  '],
                         name='Cumulative Mass Error(%)', marker_color='rgb(026,189,201)',line=dict(dash="longdash"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "('Cum Vol Err'/max('Tot Vol' and 'Cum Vol I+O'))*100 (i.e. the percentage mass error based on the maximum of the volume of water that has flowed through the model and total volume of water in the model).")),
            row=2, col=2)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Cum Q ME (%)'],
                         name='Cumulative Q Mass Error (%)', marker_color='rgb(226,001,119)',line=dict(dash="longdash"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "('Cum Vol Err'/'Cum Vol I+O')*100 (i.e. the percentage mass error based on the cumulative volume of water that has flowed through the model).")),
            row=2, col=2)
        # plot six: Cum Vol I+O
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Cum Vol I+O '],
                         name='Cumulative Vol In + Out ', marker_color='rgb(000,085,129)',line=dict(dash="longdashdot"), hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x}<br>"
                    "Value: %{y}<br>"
                    "The cumulative volume of water entering and leaving the model in m<sup>3</sup> (i.e. the cumulative total of 'Vol I+O').")),
            row=2, col=3)
        fig.add_trace(
            go.Scattergl(x=df['Time (h)    '], y=df['Cum Vol Err '],
                         name='Cumulative Volume Error (Secondary Axis)', marker_color='#FC1CBF', line=dict(dash="longdashdot"),
                         hovertemplate=(
                             "<b>%{fullData.name}</b><br>"
                             "Time: %{x}<br>"
                             "Value: %{y}<br>"
                             "The cumulative volume error in m<sup>3</sup> (i.e. the cumulative total of 'Vol Err').")),
            secondary_y=True,
            row=2, col=3)

        # Update yaxis properties
        fig.update_yaxes(row=1, col=1, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=1, col=2, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=1, col=3, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=2, col=1, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=2, col=1, title_text="<b>Volume Error(m<sup>3</sup>)</b>", secondary_y=True)
        fig.update_yaxes(row=2, col=2, title_text="<b>Error %</b>")
        fig.update_yaxes(row=2, col=3, title_text="<b>Volume (m<sup>3</sup>)</b>")
        fig.update_yaxes(row=2, col=3, title_text="<b>Volume Error(m<sup>3</sup>)</b>", secondary_y=True)

        runname = filename[:-7]
        fig.update_layout(template="plotly_white", title_text="<b>TUFLOW MB Summary Graphs for <b>" + runname,
                          height = 650, title_font_size=24)

        # ------------------------------------------------------------------
        # Final formatting
        # ------------------------------------------------------------------
        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW MB Summary – {runname}</b>",
        )

        return fig

