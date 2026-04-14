"""
/***************************************************************************
Generate a Local TUFLOW Dashboard using Dash
                             -------------------
        begin                : 2021-04-13
        copyright            : (C) 2021 by Duncan Kitts
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import base64
import io
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'TUFLOW Summary'
server = app.server

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

app.layout = html.Div([
    html.Img(src=app.get_asset_url('Logo.jpg'), height=100),  # reads in TUFLOW logo
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop *.TSF, *MB.csv or *.hpc.dt.csv files to here or ',
            html.A('Select File')
        ]),
        style={
            'width': '100%',
            'height': '50px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True #False #True
    ),
    dcc.Graph(id='Mygraph', config=dict({
        'scrollZoom': True,
        'displaylogo': False,
        'toImageButtonOptions': {
            'format': 'png',  # one of png, svg, jpeg, webp
            'filename': 'TUFLOW Summary',
            'height': None,
            'width': None,
            'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
        }
    })),
    html.Div(id='output-data-upload')  # This doesn't work.  Need to find out why.
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'tsf' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = io.StringIO(decoded.decode('utf-8')).readlines()
        elif 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df


@app.callback(Output('Mygraph', 'figure'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')
               ]
              )
def update_graph(contents, filename):
    fig = {
        'layout': go.Layout(
            height=800,
            plot_bgcolor=colors["graphBackground"],
            paper_bgcolor=colors["graphBackground"])
    }
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_contents(contents, filename)

        if filename.endswith('hpc.dt.csv'):  # Checks to see if file is hpc.dt.csv file.

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
                y1=1.0,
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
                y1=1.0,
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

            fig.add_layout_image(
                dict(
                    source=app.get_asset_url('Logo.jpg'),
                    xref="paper", yref="paper",
                    x=1, y=1.0,
                    sizex=0.2, sizey=0.2,
                    xanchor="right", yanchor="bottom"
                )
            )
        elif filename.endswith('MB.csv'):
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=(
                    "H Volume", "Q Volume", "Total Volume",
                    "Volume Err", "Q ME(%)", "Cum Volumes"),
                specs=[[{}, {}, {'secondary_y': True}],
                       [{'secondary_y': True}, {}, {'secondary_y': True}]],
                shared_xaxes='all', x_title='Hours of Simulation')
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
            fig.update_yaxes(row=1, col=1, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=2, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=3, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=1, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=1, title_text="Volume Error(m<sup>3</sup>)", secondary_y=True)
            fig.update_yaxes(row=2, col=2, title_text="Error %")
            fig.update_yaxes(row=2, col=3, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=3, title_text="Volume Error(m<sup>3</sup>)", secondary_y=True)

            runname = filename[:-7]
            fig.update_layout(template="plotly_white", title_text="<b>TUFLOW MB Summary Graphs for <b>" + runname,
                              title_font_size=24)
            fig.add_layout_image(
                dict(
                    source=app.get_asset_url('Logo.jpg'),
                    xref="paper", yref="paper",
                    x=1, y=1.0,
                    sizex=0.2, sizey=0.2,
                    xanchor="right", yanchor="bottom"
                )
            )
        elif filename.endswith('MB2D.csv'):
            fig = make_subplots(
                rows=2, cols=4,
                subplot_titles=(
                    "H Volume", "S Volume", "Estry Volume", "X1D Volume",
                    "Total Volume", "Q ME(%)", "Cum Volumes"),
                specs=[[{}, {}, {}, {}],
                       [{'secondary_y': True}, {}, {'secondary_y': True}, {}]],
                shared_xaxes='all', x_title='Hours of Simulation')
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
            fig.update_yaxes(row=1, col=1, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=2, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=3, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=4, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=1, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=1, title_text="Volume Error(m<sup>3</sup>)", secondary_y=True)
            fig.update_yaxes(row=2, col=2, title_text="Error %")
            fig.update_yaxes(row=2, col=3, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=3, title_text="Volume Error(m<sup>3</sup>)", secondary_y=True)

            runname = filename[:-9]
            fig.update_layout(template="plotly_white", title_text="<b>TUFLOW MB2D Summary Graphs for <b>" + runname,
                              title_font_size=24)
            fig.add_layout_image(
                dict(
                    source=app.get_asset_url('Logo.jpg'),
                    xref="paper", yref="paper",
                    x=1, y=1.0,
                    sizex=0.2, sizey=0.2,
                    xanchor="right", yanchor="bottom"
                )
            )
        elif filename.endswith('MB_HPC.csv'):
            fig = make_subplots(
                rows=2, cols=4,
                subplot_titles=(
                    "H Volume", "S Volume", "Estry Volume", "X1D Volume",
                    "Total Volume", "Q ME(%)", "Cumulative Volumes"),
                specs=[[{}, {}, {}, {}],
                       [{'secondary_y': True}, {}, {}, {}]],
                shared_xaxes='all', x_title='Hours of Simulation')
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
            fig.update_yaxes(row=1, col=1, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=2, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=3, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=4, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=1, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=1, title_text="Volume Error(m<sup>3</sup>)", secondary_y=True)
            fig.update_yaxes(row=2, col=2, title_text="Error %")
            fig.update_yaxes(row=2, col=3, title_text="Volume (m<sup>3</sup>)")

            runname = filename[:-11]
            fig.update_layout(template="plotly_white", title_text="<b>TUFLOW HPC_MB Summary Graphs for <b>" + runname,
                              title_font_size=24)
            fig.add_layout_image(
                dict(
                    source=app.get_asset_url('Logo.jpg'),
                    xref="paper", yref="paper",
                    x=1, y=1.0,
                    sizex=0.2, sizey=0.2,
                    xanchor="right", yanchor="bottom"
                )
            )
        elif filename.endswith('MB1D.csv'):
            fig = make_subplots(
                rows=2, cols=4,
                subplot_titles=(
                    "H Volume", "S Volume", "Estry Volume", "X1D Volume",
                    "Total Volume", "Q ME(%)", "Cum Volumes"),
                specs=[[{}, {}, {}, {}],
                       [{'secondary_y': True}, {}, {'secondary_y': True}, {}]],
                shared_xaxes='all', x_title='Hours of Simulation')
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
            fig.update_yaxes(row=1, col=1, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=2, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=3, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=1, col=4, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=1, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=1, title_text="Volume Error(m<sup>3</sup>)", secondary_y=True)
            fig.update_yaxes(row=2, col=2, title_text="Error %")
            fig.update_yaxes(row=2, col=3, title_text="Volume (m<sup>3</sup>)")
            fig.update_yaxes(row=2, col=3, title_text="Volume Error(m<sup>3</sup>)", secondary_y=True)

            runname = filename[:-9]
            fig.update_layout(template="plotly_white", title_text="<b>TUFLOW MB 1D Summary Graphs for <b>" + runname,
                              title_font_size=24)
            fig.add_layout_image(
                dict(
                    source=app.get_asset_url('Logo.jpg'),
                    xref="paper", yref="paper",
                    x=1, y=1.0,
                    sizex=0.2, sizey=0.2,
                    xanchor="right", yanchor="bottom"
                )
            )
        elif filename.endswith(
                '.tsf'):
            # if file is TUFLOW Summary then present TUFLOW summary dashboard.
            # Need to check whether Classic or HPC and also if running.
            runname = filename[:-4]
            # Search through tlf and populate parameters.
            for line in df:
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
            fig.add_layout_image(
                dict(
                    source=app.get_asset_url('Logo.jpg'),
                    xref="paper", yref="paper",
                    x=1, y=1.0,
                    sizex=0.2, sizey=0.2,
                    xanchor="right", yanchor="bottom"
                )
            )
            fig.update_layout(autotypenumbers='convert types')
        elif filename.endswith('2D_Q_from_x1D.csv'):
            # Set up figure
            runname = filename[:-18]
            fig = go.Figure(
                data=go.Scatter(x=df['Time'], y=df[df.columns[1]], mode='lines', marker_color='rgb(000,085,129)'))

            buttons = []

            for col in df.columns:
                if col == 'Time':
                    continue  # Ignore Time Column
                buttons.append(dict(method='restyle', label=col, visible=True,
                                    args=[{'y': [df[col]]}]))

            fig.update_layout(
                title={
                    'text': '2D Q From X1D Check File for ' + runname,
                    'y': 0.95,
                    'x': 0.5
                }, updatemenus=[dict(
                    buttons=buttons,
                    name='Node',
                    direction='down',
                )],
                template="plotly_white",yaxis_title="Volume (m<sup>3</sup>)",xaxis_title="Simulation Time")
        elif filename.endswith('2D_Q_to_x1D.csv'):
            # Set up figure
            runname = filename[:-16]
            fig = go.Figure(
                data=go.Scatter(x=df['Time'], y=df[df.columns[1]], mode='lines', marker_color='rgb(000,085,129)'))

            buttons = []

            for col in df.columns:
                if col == 'Time':
                    continue  # Ignore Time Column
                buttons.append(dict(method='restyle', label=col, visible=True,
                                    args=[{'y': [df[col]]}]))

            fig.update_layout(
                title={
                    'text': '2D Q to X1D Check File for ' + runname,
                    'y': 0.95,
                    'x': 0.5
                }, updatemenus=[dict(
                    buttons=buttons,
                    name='Node',
                    direction='down',
                )],
                template="plotly_white",
                yaxis_title="Volume (m<sup>3</sup>)",
                xaxis_title="Simulation Time")
        elif filename.endswith('x1D_H_to_2D.csv'):
            # Set up figure
            runname = filename[:-16]
            fig = go.Figure(
                data=go.Scatter(x=df['Time'], y=df[df.columns[1]], mode='lines', marker_color='rgb(000,085,129)'))

            buttons = []

            for col in df.columns:
                if col == 'Time':
                    continue  # Ignore Time Column
                buttons.append(dict(method='restyle', label=col, visible=True,
                                    args=[{'y': [df[col]]}]))

            fig.update_layout(
                title={
                    'text': 'X1D H to 2D Check File for ' + runname,
                    'y': 0.95,
                    'x': 0.5
                }, updatemenus=[dict(
                    buttons=buttons,
                    name='Node',
                    direction='down',
                )],
                template="plotly_white",yaxis_title="Water Level (m AD)",xaxis_title="Simulation Time")
        elif filename.endswith('x1D_H_from_2D.csv'):
            # Set up figure
            runname = filename[:-18]
            fig = go.Figure(
                data=go.Scatter(x=df['Time'], y=df[df.columns[1]], mode='lines', marker_color='rgb(000,085,129)'))

            buttons = []

            for col in df.columns:
                if col == 'Time':
                    continue  # Ignore Time Column
                buttons.append(dict(method='restyle', label=col, visible=True,
                                    args=[{'y': [df[col]]}]))

            fig.update_layout(
                title={
                    'text': 'X1D H to 2D Check File for ' + runname,
                    'y': 0.95,
                    'x': 0.5
                }, updatemenus=[dict(
                    buttons=buttons,
                    name='Node',
                    direction='down',
                )],
                template="plotly_white", yaxis_title="Water Level (m AD)", xaxis_title="Simulation Time")
        elif filename.endswith('PO.csv'):
        # Set up figure
            runname = filename[:-7]

            # Remove first row (metadata / units row)
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
            df = df.iloc[:, 1:].reset_index(drop=True)

            y_cols = df.columns  # Ignore first column in dropdow

            fig = go.Figure(
                data=go.Scatter(x=df['Time'], y=df[df.columns[1]], mode='lines', marker_color='rgb(000,085,129)'))

            buttons = []

            for col in df.columns:
                if col == 'Time':
                    continue  # Ignore Time Column
                buttons.append(dict(method='restyle', label=col, visible=True,
                                    args=[{'y': [df[col]]}]))

            fig.update_layout(
                title={
                    'text': 'PO Outputs ' + runname,
                    'y': 0.95,
                    'x': 0.5
                }, updatemenus=[dict(
                    buttons=buttons,
                    name='Node',
                    direction='down',
                )],
                template="plotly_white", yaxis_title="Output", xaxis_title="Simulation Time")

    return fig

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(
    #     debug=False,
    #     use_reloader=False,
    #     host="127.0.0.1",
    #     port=8060
    # )

