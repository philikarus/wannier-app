import os

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html

from scripts.app_utils import generate_path_completions
from scripts.parser import ProParser, SimpleParser

HOME_DIR = os.path.expanduser("~")

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

app.layout = dbc.Container(
    [
        dbc.Navbar(
            # Use row and col to control vertical alignment of logo / brand
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="https://images.plot.ly/logo/new-branding/plotly-logomark.png",
                                height="30px",
                                style={"margin-left": "5px"},
                            )
                        ),
                        dbc.Col(dbc.NavbarBrand("Wannier App", className="ms-2")),
                    ],
                    align="center",
                ),
                style={"textDecoration": "none"},
            ),
            color="dark",
            dark=True,
            # sticky="top",
        ),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    # dcc.Input(
                                    #    id="wann-input",
                                    #    type="text",
                                    #    value=("/public/home/" + os.getlogin()),
                                    #    # placeholder="Enter wannier data path...",
                                    #    debounce=True,
                                    # ),
                                    # className="my-2",
                                    dmc.TextInput(
                                        id="wann-input",
                                        type="text",
                                        # value=("/public/home/" + os.getlogin()),
                                        label="Wanneier band data path",
                                        debounce=True,
                                    )
                                ),
                                dbc.Row(
                                    dcc.Dropdown(
                                        id="wann-input-dropdown", options=[], value=None
                                    ),
                                    className="my-1",
                                ),
                                dbc.Row(
                                    dmc.TextInput(
                                        id="vasp-input",
                                        type="text",
                                        # value=("/public/home/" + os.getlogin()),
                                        label="Vasp band data path",
                                        # placeholder="Enter vasp data path...",
                                        debounce=True,
                                    ),
                                    # className="my-2",
                                ),
                                dbc.Row(
                                    dcc.Dropdown(
                                        id="vasp-input-dropdown", options=[], value=None
                                    ),
                                    className="my-1",
                                ),
                                dbc.Row(
                                    dmc.TextInput(
                                        id="proj-input",
                                        type="text",
                                        # value=("/public/home/" + os.getlogin()),
                                        label="PROCAR path",
                                        debounce=True,
                                    ),
                                    # className="my-2",
                                ),
                                dbc.Row(
                                    dcc.Dropdown(
                                        id="proj-input-dropdown", options=[], value=None
                                    ),
                                    className="my-1",
                                ),
                                dbc.Row(
                                    dmc.TextInput(
                                        id="outcar-input",
                                        type="text",
                                        # value=("/public/home/" + os.getlogin()),
                                        label="OUTCAR path",
                                        debounce=True,
                                    ),
                                    # className="my-2",
                                ),
                                dbc.Row(
                                    dcc.Dropdown(
                                        id="outcar-input-dropdown",
                                        options=[],
                                        value=None,
                                    ),
                                    className="my-1",
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="graph",
                                    config={
                                        "toImageButtonOptions": {
                                            "format": "png",
                                            "filename": "wann-app",
                                            "height": 800,
                                            "width": 800,
                                            "scale": 3,
                                        }
                                    },
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Checklist(
                                                id="checklist",
                                                options=[
                                                    "vasp",
                                                    "vasp projection",
                                                    "wannier",
                                                ],
                                                value=["vasp projection"],
                                                inline=True,
                                            ),
                                            width={"size": 4},
                                        ),
                                        dbc.Col(
                                            html.Button(
                                                "Plot", id="generate-button", n_clicks=0
                                            ),
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    # align="center",
                )
            ]
        ),
    ]
)

yrange = [-4, 4]


@app.callback(Output("wann-input-dropdown", "options"), [Input("wann-input", "value")])
def update_wann_dropdown_options(input_value):
    if input_value:
        return generate_path_completions(input_value)
    else:
        return []


@app.callback(Output("wann-input", "value"), [Input("wann-input-dropdown", "value")])
def update_wann_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise dash.exceptions.PreventUpdate


# ------------------------------------
@app.callback(Output("vasp-input-dropdown", "options"), [Input("vasp-input", "value")])
def update_vasp_dropdown_options(input_value):
    if input_value:
        return generate_path_completions(input_value)
    else:
        return []


@app.callback(Output("vasp-input", "value"), [Input("vasp-input-dropdown", "value")])
def update_vasp_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise dash.exceptions.PreventUpdate


# -----------------------------------------
@app.callback(Output("proj-input-dropdown", "options"), [Input("proj-input", "value")])
def update_proj_dropdown_options(input_value):
    if input_value:
        return generate_path_completions(input_value)
    else:
        return []


@app.callback(Output("proj-input", "value"), [Input("proj-input-dropdown", "value")])
def update_proj_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise dash.exceptions.PreventUpdate


# -----------------------------------------
@app.callback(
    Output("outcar-input-dropdown", "options"), [Input("outcar-input", "value")]
)
def update_outcar_dropdown_options(input_value):
    if input_value:
        return generate_path_completions(input_value)
    else:
        return []


@app.callback(
    Output("outcar-input", "value"), [Input("outcar-input-dropdown", "value")]
)
def update_outcar_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise dash.exceptions.PreventUpdate


def plain_bandplot(fig: go.Figure, kpath, bands, **kwargs):
    num_bands = bands.shape[1]
    yrange = kwargs.get("yrange", [-4, 4])
    color = kwargs.get("color", "blue")
    lineplot_layout = dict(
        yaxis=dict(range=yrange, showgrid=False),
        xaxis=dict(showgrid=False),
        width=800,
        height=800,
    )

    for idx in range(1, num_bands + 1):
        fig.add_trace(
            go.Scatter(
                x=kpath,
                y=bands[idx],
                mode="lines",
                # name=f"Trace{idx}",
                customdata=[f"{idx}"] * len(kpath),
                hovertemplate="band-index: %{customdata}<br>energy: %{y:.3f} eV<extra></extra>",
                line=dict(color=color, width=2),
                showlegend=False,
            )
        )
    fig.update_layout(lineplot_layout)
    # fig.update_traces(hovertemplate="band-index: %{customdata}<br> energy: %{y} eV")

    return fig


def proj_bandplot(fig: go.Figure, kpath, bands, weights, **kwargs):
    xrange = (kpath.min(), kpath.max())
    yrange = kwargs.get("yrange", [-4, 4])
    cmap = kwargs.get("cmap", "jet")
    scatter_layout = dict(
        yaxis=dict(range=yrange, showgrid=False),
        xaxis=dict(range=xrange, showgrid=False),
        width=800,
        height=800,
    )

    for idx in range(weights.shape[-1]):
        fig.add_trace(
            go.Scatter(
                x=kpath,
                y=bands[:, idx],
                mode="markers",
                marker=dict(
                    size=5,
                    color=weights[:, idx],
                    colorscale=cmap,
                    colorbar_thickness=25,
                    cmin=weights.min(),
                    cmax=weights.max(),
                ),
                customdata=[f"{idx+1}"] * len(kpath),
                hovertemplate="band-index: %{customdata}<br>energy: %{y:.3f} eV<extra></extra>",
                showlegend=False,
            )
        )
    fig.update_layout(scatter_layout)

    return fig


@app.callback(
    Output("graph", "figure"),
    [
        Input("checklist", "value"),
        Input("generate-button", "n_clicks"),
        State("wann-input", "value"),
        State("vasp-input", "value"),
        State("outcar-input", "value"),
        State("proj-input", "value"),
    ],
)
def update_figure(options, n_clicks, wann_data, vasp_data, outcar_data, proj_data):
    fig = go.Figure()
    layout = dict(
        yaxis=dict(range=yrange, showgrid=False),
        xaxis=dict(showgrid=False),
        width=800,
        height=800,
    )
    fig.update_layout(layout)

    if n_clicks > 0:
        if "vasp" in options and vasp_data:
            vasp_data = os.path.join(HOME_DIR, vasp_data)
            vasp = SimpleParser(vasp_data)
            vasp.read_file()
            plain_bandplot(
                fig,
                vasp.kpath,
                vasp.bands,
                yrange=yrange,
                color=px.colors.sequential.ice[5],
            )
        if "wannier" in options and wann_data:
            wann_data = os.path.join(HOME_DIR, wann_data)
            outcar_data = os.path.join(HOME_DIR, outcar_data)
            wann = SimpleParser(wann_data, outcar=outcar_data)
            wann.read_file()
            plain_bandplot(
                fig,
                wann.kpath,
                wann.bands,
                color=px.colors.sequential.Mint[3],
                yrange=yrange,
            )

        if "vasp projection" in options and proj_data:
            proj_data = os.path.join(HOME_DIR, proj_data)
            outcar_data = os.path.join(HOME_DIR, outcar_data)
            vasp_proj = ProParser(proj_data, outcar=outcar_data)
            vasp_proj.select_orb([0], [0, 1], [5, 7])

            proj_bandplot(
                fig,
                vasp_proj.kpath,
                vasp_proj.bands,
                vasp_proj.weights,
                cmap="plasma",
                yrange=yrange,
            )

        return fig
    else:
        return dash.no_update


app.run_server(debug=True)
