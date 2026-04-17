import re

import plotly.graph_objects as go
from core.layout import finalise_dashboard
from core.parsing import parse_csv
from core.plugin_base import TuflowPlugin
from plotly.subplots import make_subplots


class HPCDTPlugin(TuflowPlugin):
    @property
    def match_patterns(self):
        return [
            re.compile(r"hpc\.dt\.csv$", re.IGNORECASE),
        ]

    name = "HPC DT Summary"

    def parse(self, contents):
        return parse_csv(contents)

    def make_figure(self, df, filename):
        runname = filename[:-11]

        if 'Eff' in df.columns:
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    "<b>Target Timestep</b>", "<b>Timestep</b>", "<b>Courant Number (Nu)</b>", "<b>Celerity Number (Nc)</b>",
                    "<b>Diffusion Number (Nd)</b>",
                    "<b>Efficiency</b>"), shared_xaxes='all', x_title='<b>Hours of Simulation</b>')
        else:
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    "<b>Target Timestep</b>", "<b>Timestep</b>", "<b>Courant Number (Nu)</b>",
                    "<b>Celerity Number(Nc)</b>", "<b>Diffusion Number(Nd)</b>"),
                shared_xaxes='all', x_title='<b>Hours of Simulation</b>')

        # Adds traces
        # plot one
        fig.add_trace(
            go.Scattergl(x=df['tEnd'] / 3600, y=df['dtStar'],
                         name='Target Timestep', marker_color='#D5E9EB', hovertemplate=(
                             "Time: %{x}<br>"
                             "Value: %{y}<br>"
                             "Desired timestep from the 2D component of the model.")),
            row=1, col=1)
        # plot two
        fig.add_trace(go.Scattergl(x=df['tEnd'] / 3600, y=df['dt'],
                                   name='Timestep', marker_color='#D5E9EB', hovertemplate=(
                             "Time: %{x}<br>"
                             "Value: %{y}<br>"
                             "Actual timestep, can be affected by the 1D timestep and output frequency.")),
                      row=1, col=2)
        # plot three
        fig.add_trace(
            go.Scattergl(x=df['tEnd'] / 3600, y=df['Nu'],
                         name='Courant Number (Nu)', marker_color='#36B2BE', hovertemplate=(
                             "Time: %{x}<br>"
                             "Value: %{y}<br>"
                             "The Courant number relates to velocity relative to the cell size. Higher velocities will trigger this as the timestep control.")),
            row=2, col=1)

        fig.add_hrect(
            y0=0,
            y1=1,
            fillcolor="green",
            opacity=0.1,
            line_width=1, row=2, col=1
        )

        fig.add_hrect(
            y0=1,
            y1=1.2,
            yref='paper',
            fillcolor="red",
            opacity=0.1,
            line_width=1, row=2, col=1)
        # plot four
        fig.add_trace(
            go.Scattergl(x=df['tEnd'] / 3600, y=df['Nc'],
                         name='Celerity Number (Nc)', marker_color='#36B2BE',hovertemplate=(
                             "Time: %{x}<br>"
                             "Value: %{y}<br>"
                             "The Celerity Control number relates to water depth relative to cell size. Energy can pass through deeper water faster than shallow water, as such deep water will trigger this control.")),
            row=2, col=2)

        fig.add_hrect(
            y0=0,
            y1=1,
            fillcolor="green",
            opacity=0.1,
            line_width=1, row=2, col=2
        )

        fig.add_hrect(
            y0=1,
            y1=1.2,
            yref='paper',
            fillcolor="red",
            opacity=0.1,
            line_width=1, row=2, col=2)

        # plot five
        fig.add_trace(
            go.Scattergl(x=df['tEnd'] / 3600, y=df['Nd'],
                         name='Diffusion Number (Nd)', marker_color='#325A7E',hovertemplate=(
                             "Time: %{x}<br>"
                             "Value: %{y}<br>"
                             "The diffusion control relates diffusion of momentum relating to the sub grid viscosity. Small cells subject to deep water will trigger this control.")),
            row=3, col=1)
        fig.add_hrect(
            y0=0,
            y1=0.3,
            fillcolor="green",
            opacity=0.1,
            line_width=1, row=3, col=1
        )

        fig.add_hrect(
            y0=0.3,
            y1=1.0,
            yref='paper',
            fillcolor="red",
            opacity=0.1,
            line_width=1, row=3, col=1)

        # plot six
        if 'Eff' in df.columns:
            fig.add_trace(
                go.Scattergl(x=df['tEnd'] / 3600, y=df['Eff'],
                             name='Timestep Efficiency', marker_color='#325A7E', hovertemplate=(
                             "Time: %{x}<br>"
                             "Value: %{y}<br>"
                             "Efficiency value that represents the ratio of actual 2D timestep (dt) to possible 2D timestep (dtStar).")),
                row=3, col=2)

        # Update yaxis properties
        fig.update_yaxes(row=1, col=1, title_text="<b>Target Timestep (s)</b>")
        fig.update_yaxes(row=1, col=2, title_text="<b>Timestep (s)</b>")
        fig.update_yaxes(range=[0, 1.2], row=2, col=1, title_text="<b>Nu</b>")
        fig.update_yaxes(range=[0, 1.2], row=2, col=2, title_text="<b>Nc</b>")
        fig.update_yaxes(range=[0, 0.5], row=3, col=1, title_text="<b>Nd</b>")
        fig.update_yaxes(row=3, col=2, title_text="<b>Timestep Efficiency</b>")

        runname = filename[:-11]
        fig.update_layout(template="plotly_white", title_text="<b>TUFLOW HPC Summary Graphs for <b>" + runname,
                    showlegend=False, title_font_size=24, height = 650)
                    
        # ------------------------------------------------------------------
        # Final formatting
        # ------------------------------------------------------------------
        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW MB Summary – {runname}</b>",
        )

        return fig