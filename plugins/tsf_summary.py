"""
TSF Summary plugin for TUFLOW Dash Dashboard
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


class TSFSummaryPlugin(TuflowPlugin):
    """
    Handles TUFLOW *.tsf summary files
    """

    @property
    def name(self) -> str:
        return "TSF Summary"

    @property
    def match_patterns(self):
        return [
            re.compile(r"\.tsf$", re.IGNORECASE)
        ]

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, contents: bytes):

        text = contents.decode("utf-8", errors="ignore")
        lines = text.splitlines()

        if not lines:
            raise ValueError("TSF file is empty")

        return lines

   
    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def make_figure(self, lines, filename: str):

        runname = filename[:-4]
        # Search through tlf and populate parameters.
        for line in lines:
            if "Build:" in line:
                line = line.split(': ')
                build = line[1]
            if "Solution Scheme" in line:
                line = line.split('== ')
                solution_scheme = line[1].rstrip()
            if 'WARNINGs Prior to Simulation' in line:
                line = line.split('== ')
                pre_sim_warnings = line[1]
            if 'WARNINGs During Simulation' in line:
                line = line.split('== ')
                sim_warnings = line[1]
            if 'CHECKs Prior to Simulation' in line:
                line = line.split('== ')
                pre_sim_checks = line[1]
            if 'CHECKs During Simulation' in line:
                line = line.split('== ')
                sim_checks = line[1]
            if "Hardware" in line:
                line = line.split('== ')
                hardware = line[1]
            computer_test = 'False'
            if "Computer Name" in line:  # Not provided in Classic formatted TSF file
                computer_test = 'True'
                line = line.split('== ')
                computer = line[1]
            if "Simulation Status" in line:
                line = line.split('== ')
                sim_stat = line[1].rstrip()
                simulation_status = line[1]
            if "Simulation Start Time" in line:
                line = line.split('== ')
                simulation_start = float(line[1])
            if "Simulation End Time" in line:
                line = line.split('== ')
                simulation_end = float(line[1])

            # if "Simulation Time" in line:
            # Currently using percentage complete to work out how far through a simulation it is.
            #    line = line.split('== ')
            #    simulation_time = float(line[1])

            if "Active 2D Cells" in line:
                line = line.split('== ')
                no2D_cells = line[1]
            if "2D Domain Cell Sizes" in line:
                line = line.split('== ')
                line = line[1].split('.')
                cell_sizes = line[0]
            if "2D Domain Timestep" in line:
                line = line.split('== ')
                timestep = line[1]
                line = timestep.splitlines()
                timestep = line[0]
            if "Number TUFLOW 1D Nodes" in line:
                line = line.split('== ')
                tuflow_1d_nodes = line[1]
            if "Number TUFLOW 1D Channels" in line:
                line = line.split('== ')
                tuflow_1d_channels = line[1]
            if "Percentage Complete" in line:
                line = line.split('== ')
                percent_complete = float(line[1])
            if 'Approximate Clock Time Remaining (h)' in line:
                line = line.split('== ')
                clock_time_remaining = (line[1])
            if "Volume at Start (m3)" in line:
                line = line.split('== ')
                Vol_Start = float(line[1])
            if "Volume at End (m3)" in line:
                line = line.split('== ')
                Vol_End = float(line[1])
            if "Total Volume In (m3)" in line:
                line = line.split('== ')
                Tot_Vol_In = float(line[1])
            if "Total Volume Out (m3)" in line:
                line = line.split('== ')
                Tot_Vol_Out = float(line[1])
            if "Volume Error (m3)" in line:
                line = line.split('== ')
                Vol_Error = float(line[1])
            if "Cumulative Mass Error [ME]" in line:
                line = line.split('== ')
                Cum_ME = float(line[1])
            if "Clock Time" in line:
                line = line.split('== ')
                clock_time = float(line[1])
            if "Volume In Values [Qi]" in line:
                line = line.split('== ')
                data4 = line[1].split(",")
                df4 = pd.DataFrame({'vol_in': data4})
            if "Volume Out Values [Qo]" in line:
                line = line.split('== ')
                data4 = line[1].split(",")
                df4['vol_out'] = data4
            if "Flow In Values [Qi]" in line:
                line = line.split('== ')
                data4 = line[1].split(",")
                df4 = pd.DataFrame({'flow_in': data4})
            if "Flow Out Values [Qo]" in line:
                line = line.split('== ')
                data4 = line[1].split(",")
                df4['flow_out'] = data4
            if "Change in Volume Values [dV]" in line:
                line = line.split('== ')
                data4 = line[1].split(",")
                df4['dvol'] = data4
            if "Mass Error Values [ME]" in line:
                line = line.split('== ')
                data4 = line[1].split(",")
                df4['ME'] = data4
            if "Cumulative Mass Error Values [CME] (%)" in line:
                line = line.split('== ')
                data4 = line[1].split(",")
                df4['CME'] = data4
            if "Summary Output Interval" in line:
                line = line.split('== ')[1]
                interval = int(line.split('.')[0])
            if "Number Summary Values" in line:
                line = line.split('== ')
                sum_values = int(line[1])
            if 'HPC HCN Repeated Timesteps' in line:
                line = line.split('== ')
                line = line[1].split('!')
                hcn_repeat_timesteps = line[0]
            if 'HPC NaN Repeated Timesteps' in line:
                line = line.split('== ')
                line = line[1].split('!')
                nan_repeat_timesteps = line[0]
            if 'HPC NaN WARNING 2550' in line:
                line = line.split('== ')
                nan_warning = line[1]

            # if 'Classic 1D Negative Depths' in line: # Gets 1D Negative Depths.  ignore for time being.
            #  line = line.split('== ')
            # neg_depths_1D = line[1]

            if 'Classic 2D Negative Depths' in line:
                line = line.split('== ')
                neg_depths_2D = line[1]

        # Define Timeseries for plotting Volume In/Out Traces
        timesteps = np.arange(simulation_start, interval * sum_values, interval)
        # print(timesteps)

        # df4=df4.append(pd.DataFrame({'Timesteps': data4})

        # Generate Subplot figure
        if sim_stat == "RUNNING" or sim_stat == "STARTED":
            fig = make_subplots(
                rows=6, cols=2,
                subplot_titles=(
                    "<b>Software Version</b>", "<b>Model Statistics</b>", "<b>Mass Balance Summary</b>", None,
                    "<b>Checks, Warnings and Errors</b>", "<b>Time-Varying Volume Balance</b>"),
                specs=[[{'type': 'table', 'rowspan': 2}, {'type': 'table', 'rowspan': 2}],
                       [None, None],
                       [{'type': 'bar', 'rowspan': 2}, {'type': 'Indicator', 'rowspan': 2}],
                       [None, None],
                       [{'type': 'bar', 'rowspan': 2}, {'type': 'xy', 'rowspan': 2, 'secondary_y': True}],
                       [None, None]]
            )
        else:
            fig = make_subplots(
                rows=6, cols=2,
                subplot_titles=("<b>Software Version</b>", "<b>Model Statistics</b>", "<b>Mass Balance Summary</b>",
                                "<b>Run Statistics</b>", "<b>Checks, Warnings and Errors</b>",
                                "<b>Time-Varying Volume Balance</b>"),
                specs=[[{'type': 'table', 'rowspan': 2}, {'type': 'table', 'rowspan': 2}],
                       [None, None],
                       [{'type': 'bar', 'rowspan': 2}, {'type': 'table', 'rowspan': 2}],
                       [None, None],
                       [{'type': 'bar', 'rowspan': 2}, {'type': 'xy', 'rowspan': 2, 'secondary_y': True}],
                       [None, None]]
            )

        fig.update_layout(template="plotly_white")

        # Define Table Colours
        headerColor = '#325A7E'
        rowEvenColor = '#36B2BE'
        rowOddColor = '#D5E9EB'

        # Define Gauge if simulation is running other wise set up summary table
        if sim_stat == 'RUNNING' or sim_stat == 'STARTED':
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=percent_complete,
                number_suffix='%',
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "#FC1CBF"}},
                title={
                    "text": "<b>Simulation Progress</b><br><span style='font-size:0.6em'>Estimated Remaining Time: " + clock_time_remaining + "hrs</span>"}),
                row=3, col=2)
        else:
            if solution_scheme == 'HPC':
                fig.add_trace(go.Table(header=dict(values=['<b>Parameters</b>', '<b>Values</b>'],
                                                   fill_color=headerColor, font=dict(color='white', size=12)),
                                       cells=dict(values=[
                                           ['Simulation Status', 'Simulation Start Time', 'Simulation End Time',
                                            'Clock Time (hrs)', 'Cumulative Mass Error (%)'],
                                           [simulation_status, simulation_start, simulation_end, clock_time,
                                            Cum_ME]],
                                           fill_color=[
                                               [rowOddColor, rowEvenColor, rowOddColor, rowEvenColor,
                                                rowOddColor] * 5],
                                           align=['left', 'center'],
                                           font=dict(color='darkslategrey', size=11)
                                       ), columnwidth=40), row=3, col=2)
            elif solution_scheme == 'Classic':
                fig.add_trace(go.Table(header=dict(values=['<b>Parameters</b>', '<b>Values</b>'],
                                                   fill_color=headerColor, font=dict(color='white', size=12)),
                                       cells=dict(values=[
                                           ['Simulation Status', 'Simulation Start Time', 'Simulation End Time',
                                            'Clock Time (hrs)', 'Cumulative Mass Error (%)'],
                                           [simulation_status, simulation_start, simulation_end, clock_time,
                                            Cum_ME]],
                                           fill_color=[
                                               [rowOddColor, rowEvenColor, rowOddColor, rowEvenColor,
                                                rowOddColor] * 5],
                                           align=['left', 'center'],
                                           font=dict(color='darkslategrey', size=11)
                                       ), columnwidth=20), row=3, col=2)

        # Define Bar Graph of Mass Balance Values
        fig.add_trace(go.Bar(x=["Vol_Start", "Vol_End", "Tot_Vol_In", "Tot_Vol_Out", "Vol_Error"],
                             y=[Vol_Start, Vol_End, Tot_Vol_In, Tot_Vol_Out, Vol_Error],
                             text=[Vol_Start, Vol_End, Tot_Vol_In, Tot_Vol_Out, Vol_Error], textposition='auto',
                             marker_color='#325A7E', showlegend=False),
                      row=3, col=1),
        fig.update_yaxes(title_text="Volume (m<sup>3</sup>)", row=3, col=1)

        # Define Tables of Software Builds and Solver Types
        if solution_scheme == 'HPC':
            fig.add_trace(go.Table(header=dict(values=['<b>Parameters</b>', '<b>Values</b>'],
                                               fill_color=headerColor, font=dict(color='white', size=12)),
                                   cells=dict(values=[['Build', 'Solution Scheme', 'Hardware', 'Computer'],
                                                      [build, solution_scheme, hardware, computer]],
                                              fill_color=[
                                                  [rowOddColor, rowEvenColor, rowOddColor, rowEvenColor,
                                                   rowOddColor] * 5],
                                              align=['left', 'center'],
                                              font=dict(color='darkslategrey', size=11)
                                              ), columnwidth=20), row=1, col=1)

            fig.add_trace(go.Bar(
                x=['HCN Repeated <br> Timesteps', 'NaN Repeated <br> Timestep', 'NaN Warning <br> 2550',
                   'Warnings Prior <br> to Simulation',
                   'Warnings During <br> Simulation', 'Checks Prior <br> to Simulation',
                   'Checks During <br> Simulation'],
                y=[hcn_repeat_timesteps, nan_repeat_timesteps, nan_warning, pre_sim_warnings, sim_warnings,
                   pre_sim_checks, sim_checks],
                textposition='auto',
                marker_color='#36B2BE', showlegend=False),
                row=5, col=1),
            fig.update_yaxes(title_text="Number of...", row=5, col=1)

        elif solution_scheme == 'Classic':
            if computer_test == 'False':
                fig.add_trace(go.Table(header=dict(values=['<b>Parameter</b>', '<b>Values</b>'],
                                                   fill_color=headerColor, font=dict(color='white', size=12)),
                                       cells=dict(values=[['Build', 'Solution Scheme', 'Hardware'],
                                                          [build, solution_scheme, hardware]],
                                                  fill_color=[
                                                      [rowOddColor, rowEvenColor, rowOddColor, rowEvenColor,
                                                       rowOddColor] * 5],
                                                  align=['left', 'center'],
                                                  font=dict(color='darkslategrey', size=11)
                                                  ), columnwidth=20), row=1, col=1)
            else:
                fig.add_trace(go.Table(header=dict(values=['<b>Parameter</b>', '<b>Values</b>'],
                                                   fill_color=headerColor, font=dict(color='white', size=12)),
                                       cells=dict(values=[['Build', 'Solution Scheme', 'Hardware', 'Computer'],
                                                          [build, solution_scheme, hardware, computer]],
                                                  fill_color=[
                                                      [rowOddColor, rowEvenColor, rowOddColor, rowEvenColor,
                                                       rowOddColor] * 5],
                                                  align=['left', 'center'],
                                                  font=dict(color='darkslategrey', size=11)
                                                  ), columnwidth=20), row=1, col=1)

            fig.add_trace(go.Bar(x=['2D Negative <br> Depths', 'Warnings Prior <br> to Simulation',
                                    'Warnings During <br> Simulation', 'Checks Prior <br> to Simulation',
                                    'Checks During <br> Simulation'],
                                 y=[neg_depths_2D, pre_sim_warnings, sim_warnings, pre_sim_checks, sim_checks],
                                 textposition='auto',
                                 marker_color='#36B2BE', showlegend=False),
                          row=5, col=1),
            fig.update_yaxes(title_text="Number of...", row=5, col=1)

        # Define Table which summarises Model Geometry
        fig.add_trace(go.Table(header=dict(values=['<b>Parameters</b>', '<b>Values</b>'],
                                           fill_color=headerColor, font=dict(color='white', size=12)),
                               cells=dict(values=[['Active 2D Cells', '2D Domain Cell Sizes', '2D Timestep(s)',
                                                   'Number of TUFLOW 1D Nodes', 'Number of TUFLOW 1D Channels'],
                                                  [no2D_cells, cell_sizes, timestep, tuflow_1d_nodes,
                                                   tuflow_1d_channels]],
                                          fill_color=[
                                              [rowOddColor, rowEvenColor, rowOddColor, rowEvenColor,
                                               rowOddColor] * 5],
                                          align=['left', 'center'],
                                          font=dict(color='darkslategrey', size=11)
                                          ), columnwidth=5), row=1, col=2)

        # Set up graph of time-varying volume in/out.  Needs to vary depending on whether HPC or Classic simulation.
        if solution_scheme == 'HPC':
            fig.add_trace(go.Scatter(x=timesteps / 60 / 60,
                                     y=df4['vol_in'], name="Volume In", marker_color='#325A7E'),
                          row=5, col=2)
            fig.add_trace(go.Scatter(x=timesteps / 60 / 60,
                                     y=df4['vol_out'], name="Volume Out", marker_color='#36B2BE'),
                          row=5, col=2)
            fig.add_trace(go.Scatter(x=timesteps / 60 / 60,
                                     y=df4['dvol'], name="Change in Volume", marker_color='#D5E9EB'),
                          row=5, col=2)
            fig.add_trace(go.Scatter(x=timesteps / 60 / 60,
                                     y=df4['ME'], name="Mass Error", marker_color='#FC1CBF',
                                     line=dict(dash='dash')),
                          row=5, col=2, secondary_y=True)
            fig.update_yaxes(title_text="Volume (m<sup>3</sup>)", row=5, col=2)
            fig.update_yaxes(title_text="Mass Error (%)", secondary_y=True, row=5, col=2)
            fig.update_xaxes(title_text="Time (hrs)", row=5, col=2)
        elif solution_scheme == 'Classic':
            fig.add_trace(go.Scatter(x=timesteps / 60 / 60,
                                     y=df4['flow_in'], name="Volume In", marker_color='#325A7E'),
                          row=5, col=2)
            fig.add_trace(go.Scatter(x=timesteps / 60 / 60,
                                     y=df4['flow_out'], name="Volume Out", marker_color='#36B2BE'),
                          row=5, col=2)
            fig.add_trace(go.Scatter(x=timesteps / 60 / 60,
                                     y=df4['dvol'], name="Change in Volume", marker_color='#D5E9EB'),
                          row=5, col=2)
            fig.add_trace(go.Scatter(x=timesteps / 60 / 60,
                                     y=df4['CME'], name="Cumulative Mass Error (%)", marker_color='#FC1CBF',
                                     line=dict(dash='dash')),
                          row=5, col=2, secondary_y=True)
            fig.update_yaxes(title_text="Volume (m<sup>3</sup>)", row=5, col=2)
            fig.update_yaxes(title_text="Mass Error (%)", secondary_y=True, row=5, col=2)
            fig.update_xaxes(title_text="Time (hrs)", row=5, col=2)

        # Add title and position legend.

        fig.update_layout(title={
            'text': '<b>' + runname + '</b>',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            title_font_size=24,
            legend=dict(
                yanchor="top",
                y=0.4,
                xanchor="left",
                x=0.45
            )
        )
        fig.update_layout(autotypenumbers='convert types')

        # -------------------------------
        # Final formatting
        # -------------------------------
        fig = finalise_dashboard(
            fig,
            title=f"<b>TUFLOW TSF Summary – {runname}</b>",
        )

        return fig