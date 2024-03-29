import os

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from scripts.app_utils import check_yrange_input, generate_path_completions
from scripts.layout import control_panel, file_input_panel, graph_panel, header
from scripts.parser import ProParser, SimpleParser
from scripts.plot import plain_bandplot, proj_bandplot

HOME_DIR = os.path.expanduser("~")
VASP_COLOR = px.colors.qualitative.Plotly[0]
WANN_COLOR = px.colors.qualitative.Plotly[1]
PROJ_COLOR = "Agsunset"

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = dbc.Container(
    [
        header,
        html.Br(),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col((file_input_panel + control_panel), md=3),
                        dbc.Col(graph_panel),
                    ],
                    # align="center",
                    # justify="between",
                )
            ]
        ),
    ],
    fluid=True,
)

# yrange = [-4, 4]


@app.callback(Output("wann-input-dropdown", "data"), [Input("wann-input", "value")])
def update_wann_dropdown_options(input_value):
    if input_value:
        completions = generate_path_completions(input_value)
        if completions:
            return completions
        else:
            raise PreventUpdate
    else:
        return []


@app.callback(Output("wann-input", "value"), [Input("wann-input-dropdown", "value")])
def update_wann_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise PreventUpdate


# ------------------------------------
@app.callback(Output("vasp-input-dropdown", "data"), [Input("vasp-input", "value")])
def update_vasp_dropdown_options(input_value):
    if input_value:
        completions = generate_path_completions(input_value)
        if completions:
            return completions
        else:
            raise PreventUpdate
    else:
        return []


@app.callback(Output("vasp-input", "value"), [Input("vasp-input-dropdown", "value")])
def update_vasp_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise PreventUpdate


# -----------------------------------------
@app.callback(Output("proj-input-dropdown", "data"), [Input("proj-input", "value")])
def update_proj_dropdown_options(input_value):
    if input_value:
        completions = generate_path_completions(input_value)
        if completions:
            return completions
        else:
            raise PreventUpdate
    else:
        return []


@app.callback(Output("proj-input", "value"), [Input("proj-input-dropdown", "value")])
def update_proj_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise PreventUpdate


# -----------------------------------------
@app.callback(Output("outcar-input-dropdown", "data"), [Input("outcar-input", "value")])
def update_outcar_dropdown_options(input_value):
    if input_value:
        completions = generate_path_completions(input_value)
        if completions:
            return completions
        else:
            raise PreventUpdate
    else:
        return []


@app.callback(
    Output("outcar-input", "value"), [Input("outcar-input-dropdown", "value")]
)
def update_outcar_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise PreventUpdate


@app.callback(Output("yrange", "error"), Input("yrange", "value"))
def update_yrange_error_info(value):
    return check_yrange_input(value)


@app.callback(
    Output("graph", "figure"),
    [
        Input("checklist", "value"),
        Input("generate-button", "n_clicks"),
        State("wann-input", "value"),
        State("vasp-input", "value"),
        State("outcar-input", "value"),
        State("proj-input", "value"),
        State("yrange", "value"),
    ],
)
def update_figure(
    checklist_values, n_clicks, wann_data, vasp_data, outcar_data, proj_data, y_range
):
    fig = go.Figure()
    y_min = float(y_range.replace(" ", "").split(",")[0])
    y_max = float(y_range.replace(" ", "").split(",")[1])
    y_range = (y_min, y_max)

    layout = dict(
        yaxis=dict(range=y_range, title="Energy (eV)", showgrid=False),
        xaxis=dict(showgrid=False),
        width=800,
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="left",
            x=0.01,
            font=dict(size=12),
        ),
    )

    if n_clicks > 0:
        if "vasp" in checklist_values and vasp_data:
            vasp_data = os.path.join(HOME_DIR, vasp_data)
            vasp = SimpleParser(vasp_data)
            vasp.read_file()
            plain_bandplot(
                fig,
                vasp.kpath,
                vasp.bands,
                # yrange=y_range,
                color=VASP_COLOR,
                name="vasp band",
            )
        if "wann" in checklist_values and wann_data:
            wann_data = os.path.join(HOME_DIR, wann_data)
            outcar_data = os.path.join(HOME_DIR, outcar_data)
            wann = SimpleParser(wann_data, outcar=outcar_data)
            wann.read_file()
            plain_bandplot(
                fig,
                wann.kpath,
                wann.bands,
                color=WANN_COLOR,
                # yrange=y_range,
                name="wannier band",
            )

        if "proj" in checklist_values and proj_data:
            proj_data = os.path.join(HOME_DIR, proj_data)
            if outcar_data:
                outcar_data = os.path.join(HOME_DIR, outcar_data)
            vasp_proj = ProParser(proj_data, outcar=outcar_data)
            vasp_proj.select_orb([0], [0, 1], [5, 7])

            proj_bandplot(
                fig,
                vasp_proj.kpath,
                vasp_proj.bands,
                vasp_proj.weights,
                cmap=PROJ_COLOR,
                # yrange=y_range,
                name="projected band",
            )

        fig.update_layout(layout)

        return fig
    else:
        return go.Figure(layout=layout)


app.run_server(debug=True)
