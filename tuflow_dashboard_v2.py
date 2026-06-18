import plotly.graph_objects as go
from core.parsing import decode_upload
from core.plugin_registry import find_plugin
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "TUFLOW Dashboard"

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

app.layout = html.Div([
    html.Img(src=app.get_asset_url("Logo.jpg"),
             style={"height": "80px", "marginBottom": "30px"}),

    dcc.Upload(
        id="upload",
        children=html.Div(
            ['Drag and Drop *.TSF, *.TLF, *MB.csv, *PO.csv, *.hpc.dt.csv, .eof, run_stats.txt, start_stats.txt, messages.csv, _ TUFLOW Simulations.log or external X1D Check files to here or ',
             html.A('Select File')]),
        multiple=True,
        style={
            "width": "100%",
            "height": "50px",
            "lineHeight": "50px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
        },
    ),

    html.Div(id="result"),
    html.Div(id="error", style={"color": "red", "marginTop": "10px"})
])


@app.callback(
    Output("result", "children"),
    Output("error", "children"),
    Input("upload", "contents"),
    Input("upload", "filename"),
)
def update(contents, filename):
    if contents is None or filename is None:
        raise PreventUpdate

    if isinstance(contents, list):
        contents = contents[0]
    if isinstance(filename, list):
        filename = filename[0]

    plugin = find_plugin(filename)
    if not plugin:
        return None, f"Unsupported file type: {filename}"

    try:
        raw = decode_upload(contents)
        data = plugin.parse(raw)

        if hasattr(plugin, "make_output"):
            return plugin.make_output(data, filename), ""

        return dcc.Graph(
            figure=plugin.make_figure(data, filename),
            config={
                'scrollZoom': True,
                "displaylogo": False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'TUFLOW Dashboard Output',
                },
            }
        ), ""

    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    app.run(debug=True)

    # TODO Tidy up code.
    # Improve error messaging like messages plugin
    # Support POMM files? HPC.TLF? Grids or Result Files (should be technically possible with PyTUFLOW)
