import os

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, Patch, State, clientside_callback, html
from dash.exceptions import PreventUpdate
from scripts.layout import layout
from scripts.parser import ProjParser, VaspParser, WannParser
from scripts.plot import make_symm_lines, plain_bandplot, proj_bandplot
from scripts.utils import check_yrange_input, find_indices, generate_path_completions

HOME_DIR = "/data"
VASP_COLOR = px.colors.qualitative.Plotly[0]
WANN_COLOR = px.colors.qualitative.Plotly[1]
PROJ_COLOR = "Agsunset"
DIS_WIN_COLOR = px.colors.qualitative.Pastel[1]
FROZ_WIN_COLOR = px.colors.qualitative.Pastel[0]
SYMMLINE_COLOR = px.colors.qualitative.Prism[10]


app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.title = "Wannier Dash"
app.layout = layout


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
@app.callback(
    Output("kpoints-input-dropdown", "data"), [Input("kpoints-input", "value")]
)
def update_kpoints_dropdown_options(input_value):
    if input_value:
        completions = generate_path_completions(input_value)
        if completions:
            return completions
        else:
            raise PreventUpdate
    else:
        return []


@app.callback(
    Output("kpoints-input", "value"), [Input("kpoints-input-dropdown", "value")]
)
def update_kpoints_input_value(dropdown_value):
    if dropdown_value:
        return dropdown_value
    else:
        raise PreventUpdate


@app.callback(
    [
        Output("vasp-input", "required"),
        Output("kpoints-input", "required"),
        Output("proj-input", "required"),
        Output("wann-input", "required"),
        Output("atom-select", "required"),
        Output("orbital-select", "required"),
    ],
    Input("checklist", "value"),
)
def update_is_file_required(checklist_values):
    required = [False] * 6
    if "vasp" in checklist_values:
        required[0] = True
        required[1] = True
    if "proj" in checklist_values:
        required[0] = True
        required[1] = True
        required[2] = True
        required[4] = True
        required[5] = True
    if "wann" in checklist_values:
        required[0] = True
        required[3] = True
    return required


clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    Output("load-data", "loading", allow_duplicate=True),
    Input("load-data", "n_clicks"),
    prevent_initial_call=True,
)


@app.callback(
    [
        Output("atom-select", "data"),
        Output("orbital-select", "data"),
        Output("load-data", "loading"),
        Output("loaded-data", "data"),
    ],
    [
        Input("load-data", "n_clicks"),
        State("vasp-input", "value"),
        State("kpoints-input", "value"),
        State("proj-input", "value"),
        State("wann-input", "value"),
    ],
)
def update_path_and_options(n_clicks, vasp_data, kpoints_data, proj_data, wann_data):
    atom_list = []
    orbital_list = []
    loaded_data = {}
    if n_clicks > 0:
        if vasp_data:
            vasp_data = os.path.join(HOME_DIR, vasp_data)
            vasp = VaspParser(vasp_data)
            atom_list = list(set(vasp.atom_list))
            loaded_data["vasp"] = vasp_data
        if proj_data and vasp_data:
            proj_data = os.path.join(HOME_DIR, proj_data)
            proj = ProjParser(proj_data, vasp_xml=vasp_data)
            orbital_list = proj.orbitals
            loaded_data["proj"] = proj_data
        if kpoints_data:
            kpoints_data = os.path.join(HOME_DIR, kpoints_data)
            loaded_data["kpoints"] = kpoints_data
        if wann_data:
            wann_data = os.path.join(HOME_DIR, wann_data)
            loaded_data["wann"] = wann_data

    return atom_list, orbital_list, False, loaded_data


@app.callback(Output("yrange", "error"), Input("yrange", "value"))
def update_yrange_error_info(value):
    return check_yrange_input(value)


@app.callback(
    Output("graph", "figure", allow_duplicate=True),
    [Input("update-yrange", "n_clicks"), State("yrange", "value")],
    prevent_initial_call=True,
)
def update_yrange(n_clicks, y_range):
    if n_clicks > 0:
        y_min = float(y_range.replace(" ", "").split(",")[0])
        y_max = float(y_range.replace(" ", "").split(",")[1])
        y_range = (y_min, y_max)
        patched_figure = Patch()
        patched_figure["layout"]["yaxis"]["range"] = y_range
        return patched_figure


@app.callback(
    Output("band-minmax", "children"),
    [
        Input("calc-band-minmax", "n_clicks"),
        Input("band-idx", "value"),
        State("loaded-data", "data"),
        State("atom-select", "value"),
        State("orbital-select", "value"),
    ],
)
def get_band_min_max(n_clicks, band_idx, loaded_data, atoms, orbitals):
    if n_clicks > 0:
        proj_data = loaded_data.get("proj", None)
        vasp_data = loaded_data.get("vasp", None)
        kpoints_data = loaded_data.get("kpoints", None)

        if proj_data and vasp_data and kpoints_data:
            vasp = VaspParser(vasp_data, kpoints_data)
            vasp_proj = ProjParser(proj_data, vasp_xml=vasp_data)
            efermi = vasp_proj.efermi
            atom_list = vasp.atom_list
            atoms = list(find_indices(atom_list, atoms))
            orbital_list = vasp_proj.orbitals
            orbitals = list(find_indices(orbital_list, orbitals))
            vasp_proj.select_atom_and_orb([0], atoms, orbitals)
            if band_idx:
                band_idx = int(band_idx)
            band = vasp_proj.bands[:, band_idx - 1]
            band_min = band.min()
            band_min_nofermi = band_min - efermi
            band_max = band.max()
            band_max_nofermi = band_max - efermi

            data = {
                "Emin": band_min,
                "Emin+Ef": band_min_nofermi,
                "Emax": band_max,
                "Emax+Ef": band_max_nofermi,
            }

            return [
                html.Div(
                    [
                        html.Span(
                            key + " : ",
                            style={
                                "display": "inline-block",
                                "width": "100px",
                                "text-align": "left",
                            },
                        ),
                        html.Span(
                            "{:.3f} eV".format(value),
                            style={
                                "display": "inline-block",
                                "width": "100px",
                                "text-align": "right",
                            },
                        ),
                    ],
                    style={"margin-bottom": "5px"},
                )
                for key, value in data.items()
            ]


@app.callback(
    Output("graph", "figure"),
    [
        State("checklist", "value"),
        Input("generate-button", "n_clicks"),
        State("loaded-data", "data"),
        State("atom-select", "value"),
        State("orbital-select", "value"),
        State("yrange", "value"),
        # TODO: Symplify logic
        State("dis-win", "value"),
        Input("switch-dis-win", "checked"),
        State("froz-win", "value"),
        Input("switch-froz-win", "checked"),
    ],
)
def update_figure(
    checklist_values,
    n_clicks,
    # wann_data,
    # vasp_data,
    # kpoints_data,
    # proj_data,
    loaded_data,
    atoms,
    orbitals,
    y_range,
    dis_win,
    switch_dis_win_checked,
    froz_win,
    switch_froz_win_checked,
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
        vasp_data = loaded_data.get("vasp", None)
        kpoints_data = loaded_data.get("kpoints", None)
        wann_data = loaded_data.get("wann", None)
        proj_data = loaded_data.get("proj", None)

        if vasp_data and kpoints_data:
            # vasp_data = os.path.join(HOME_DIR, vasp_data)
            # kpoints_data = os.path.join(HOME_DIR, kpoints_data)
            vasp = VaspParser(vasp_data, kpoints_data)
            x_range = [vasp.kpath[0], vasp.kpath[-1]]
            layout["xaxis"]["range"] = x_range

        if "vasp" in checklist_values:
            plain_bandplot(
                fig,
                vasp.kpath,
                vasp.bands,
                # yrange=y_range,
                color=VASP_COLOR,
                label="vasp band",
            )
            # make_symm_lines(fig, vasp.ticks, color="black")

        if "wann" in checklist_values and wann_data:
            # wann_data = os.path.join(HOME_DIR, wann_data)
            # vasp_data = os.path.join(HOME_DIR, vasp_data)
            wann = WannParser(wann_data, vasp_xml=vasp_data)
            wann.read_file()
            plain_bandplot(
                fig,
                wann.kpath,
                wann.bands,
                color=WANN_COLOR,
                # yrange=y_range,
                label="wannier band",
            )

        if "proj" in checklist_values and proj_data:
            # proj_data = os.path.join(HOME_DIR, proj_data)
            vasp_proj = ProjParser(proj_data, vasp_xml=vasp_data)
            atom_list = vasp.atom_list
            atoms = list(find_indices(atom_list, atoms))
            orbital_list = vasp_proj.orbitals
            orbitals = list(find_indices(orbital_list, orbitals))
            vasp_proj.select_atom_and_orb([0], atoms, orbitals)

            proj_bandplot(
                fig,
                vasp.kpath,
                vasp_proj.bands,
                vasp_proj.weights,
                normalize=False,
                cmap=PROJ_COLOR,
                # yrange=y_range,
                label="projected band",
            )

        if switch_dis_win_checked > 0:
            if dis_win:
                dis_win_min = float(dis_win.replace(" ", "").split(",")[0])
                dis_win_max = float(dis_win.replace(" ", "").split(",")[1])
                fig.add_hrect(
                    y0=dis_win_min,
                    y1=dis_win_max,
                    line_width=0,
                    fillcolor=DIS_WIN_COLOR,
                    opacity=0.2,
                )

        if switch_froz_win_checked > 0:
            if froz_win:
                froz_win_min = float(froz_win.replace(" ", "").split(",")[0])
                froz_win_max = float(froz_win.replace(" ", "").split(",")[1])
                fig.add_hrect(
                    y0=froz_win_min,
                    y1=froz_win_max,
                    line_width=0,
                    fillcolor=FROZ_WIN_COLOR,
                    opacity=0.2,
                )

        fig.update_layout(layout)
        make_symm_lines(fig, vasp.ticks, color=SYMMLINE_COLOR, use_dash=False)
        return fig
    else:
        return go.Figure(layout=layout)


app.run_server(host="0.0.0.0", debug=True)
