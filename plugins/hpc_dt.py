import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.plugin_base import TuflowPlugin
from core.parsing import parse_csv
from core.layout import finalise_dashboard
import re


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
                    "Target Timestep", "Timestep", "Courant Number (Nu)", "Celerity Number (Nc)",
                    "Diffusion Number (Nd)",
                    "Efficiency"), shared_xaxes='all', x_title='Hours of Simulation')
        else:
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    "Target Timestep", "Timestep", "Courant Number (Nu)",
                    "Celerity Number(Nc)", "Diffusion Number(Nd)"),
                shared_xaxes='all', x_title='Hours of Simulation')

        # Adds traces
        # plot one
        fig.add_trace(
            go.Scattergl(x=df['tEnd'] / 3600, y=df['dtStar'],
                         name='Target Timestep', marker_color='#D5E9EB'),
            row=1, col=1)
        # plot two
        fig.add_trace(go.Scattergl(x=df['tEnd'] / 3600, y=df['dt'],
                                   name='Timestep', marker_color='#D5E9EB'),
                      row=1, col=2)
        # plot three
        fig.add_trace(
            go.Scattergl(x=df['tEnd'] / 3600, y=df['Nu'],
                         name='Courant Number (Nu)', marker_color='#36B2BE'),
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
                         name='Celerity Number (Nc)', marker_color='#36B2BE'),
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
                         name='Diffusion Number (Nd)', marker_color='#325A7E'),
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
                             name='Timestep Efficiency', marker_color='#325A7E'),
                row=3, col=2)

        # Update yaxis properties
        fig.update_yaxes(row=1, col=1, title_text="Target Timestep (s)")
        fig.update_yaxes(row=1, col=2, title_text="Timestep (s)")
        fig.update_yaxes(range=[0, 1.2], row=2, col=1, title_text="Nu")
        fig.update_yaxes(range=[0, 1.2], row=2, col=2, title_text="Nc")
        fig.update_yaxes(range=[0, 0.5], row=3, col=1, title_text="Nd")
        fig.update_yaxes(row=3, col=2, title_text="Timestep Efficiency")

        runname = filename[:-11]
        fig.update_layout(template="plotly_white", title_text="<b>TUFLOW HPC Summary Graphs for <b>" + runname,
                    showlegend=False, title_font_size=24)
                    
        # ------------------------------------------------------------------
        # Final formatting
        # ------------------------------------------------------------------
        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW MB Summary – {runname}</b>",
        )

        return fig