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

    if isinstance(contents, list) and isinstance(filename, list):
        if len(contents) != len(filename):
            return None, "Upload error: file content and filename count do not match. Please try again."
        if len(contents) != 1:
            return None, "Please upload one file at a time. Multiple file upload is not supported yet."
        contents = contents[0]
        filename = filename[0]
    elif isinstance(contents, list) or isinstance(filename, list):
        return None, "Upload error: inconsistent upload payload. Please select a single file."

    if not isinstance(filename, str) or not filename.strip():
        return None, "Upload error: filename is missing or invalid. Please try again."
    if not isinstance(contents, str) or not contents.strip():
        return None, "Upload error: file contents are invalid or empty. Please try again."

    plugin = find_plugin(filename)
    if not plugin:
        return None, f"Unsupported file type: {filename}. Please upload one of the supported TUFLOW files."

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

    except ValueError as e:
        return None, f"Upload failed: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error processing {filename}: {e.__class__.__name__}. Please check the file and try again."


if __name__ == "__main__":
    app.run(debug=True)

    # TODO Tidy up code.
    # Improve error messaging like messages plugin
    # Support POMM files? HPC.TLF? Grids or Result Files (should be technically possible with PyTUFLOW)
    # FV Mass (test), FLUX (Test), Points (Test), Structflux (Test), Mass Balance (Test)
