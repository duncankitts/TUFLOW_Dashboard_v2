from core.parsing import decode_upload
from core.plugin_registry import find_plugin
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate

EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
UPLOAD_HELP_TEXT = (
    "Drag and drop a supported TUFLOW file here, or "
    "select one from your device."
)

app = Dash(__name__, external_stylesheets=EXTERNAL_STYLESHEETS)
app.title = "TUFLOW Dashboard"
server = app.server

app.layout = html.Div(
    [
        html.Img(
            src=app.get_asset_url("Logo.jpg"),
            style={"height": "80px", "marginBottom": "30px"},
        ),
        dcc.Upload(
            id="upload",
            children=html.Div([UPLOAD_HELP_TEXT, html.A(" Select File")]),
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
        html.Div(id="error", style={"color": "red", "marginTop": "10px"}),
    ],
    style={"padding": "20px"},
)


def _normalise_upload_payload(contents, filename):
    if contents is None or filename is None:
        raise PreventUpdate

    if isinstance(contents, list) and isinstance(filename, list):
        if len(contents) != len(filename):
            raise ValueError("File content and filename count do not match.")
        if len(contents) != 1:
            raise ValueError("Please upload one file at a time.")
        return contents[0], filename[0]

    if isinstance(contents, list) or isinstance(filename, list):
        raise ValueError("Please select a single file.")

    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("Filename is missing or invalid.")
    if not isinstance(contents, str) or not contents.strip():
        raise ValueError("File contents are invalid or empty.")

    return contents, filename


@app.callback(
    Output("result", "children"),
    Output("error", "children"),
    Input("upload", "contents"),
    Input("upload", "filename"),
)
def update(contents, filename):
    try:
        contents, filename = _normalise_upload_payload(contents, filename)
    except PreventUpdate:
        raise
    except ValueError as exc:
        return None, f"Upload error: {exc}"

    plugin = find_plugin(filename)
    if not plugin:
        return None, f"Unsupported file type: {filename}."

    try:
        raw = decode_upload(contents)
        data = plugin.parse(raw)

        if hasattr(plugin, "make_output"):
            return plugin.make_output(data, filename), ""

        return dcc.Graph(
            figure=plugin.make_figure(data, filename),
            config={
                "scrollZoom": True,
                "displaylogo": False,
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": "TUFLOW Dashboard Output",
                },
            },
        ), ""
    except ValueError as exc:
        return None, f"Upload failed: {exc}"
    except Exception as exc:
        return None, (
            f"Unexpected error processing {filename}: "
            f"{exc.__class__.__name__}."
        )


if __name__ == "__main__":
    app.run(debug=True)

#TODO: Support for POMM files?
#TODO: What about other result files?
#TODO: Tidy up error messaging
#TODO: Tidy up some of the displays.  Particularly the mass balance outputs.
#TODO: Check colour scheme throughout.