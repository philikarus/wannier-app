import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify


def make_input_file_tooltips(input_file):
    return dbc.Tooltip(
        "input ./ to select under home directory",
        id=f"{input_file}-input-tooltip",
        target=f"{input_file}-input",
        placement="right-end",
    )


header = dbc.Navbar(
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
        class_name="g-0",
    ),
    # style={"textDecoration": "none"},
    color="primary",
    dark=True,
    # sticky="top",
)

file_input_tooltips = [
    make_input_file_tooltips(_) for _ in ["wann", "vasp", "proj", "outcar"]
]

file_input_panel = [
    html.Div(file_input_tooltips),
    dbc.Col(
        dmc.TextInput(
            id="vasp-input",
            type="text",
            placeholder="Enter a path...",
            label="VASPRUN XML Path",
            debounce=True,
        ),
        md=12,
        # className="my-2",
    ),
    dbc.Col(
        dmc.Select(
            id="vasp-input-dropdown",
            data=[],
            searchable=True,
            placeholder="Select under path",
            value=None,
        ),
        className="my-1",
        md=12,
    ),
    dbc.Col(
        dmc.TextInput(
            id="proj-input",
            type="text",
            placeholder="Enter a path...",
            label="PROCAR Path",
            debounce=True,
        ),
        # className="my-2",
        md=12,
    ),
    dbc.Col(
        dmc.Select(
            id="proj-input-dropdown",
            data=[],
            searchable=True,
            placeholder="Select under path",
            value=None,
        ),
        className="my-1",
        md=12,
    ),
    dbc.Col(
        dmc.TextInput(
            id="wann-input",
            type="text",
            placeholder="Enter a path...",
            label="Wanneier Band Data Path",
            debounce=True,
        ),
        md=12,
    ),
    dbc.Col(
        dmc.Select(
            id="wann-input-dropdown",
            data=[],
            searchable=True,
            placeholder="Select under path",
            value=None,
            allowDeselect=True,
        ),
        className="my-1",
        md=12,
    ),
    dbc.Col(
        dmc.TextInput(
            id="kpoints-input",
            type="text",
            placeholder="Enter a path...",
            label="KPOINTS Path",
            debounce=True,
        ),
        # className="my-2",
        md=12,
    ),
    dbc.Col(
        dmc.Select(
            id="kpoints-input-dropdown",
            data=[],
            searchable=True,
            placeholder="Select under path",
            value=None,
        ),
        className="my-1",
        md=12,
    ),
]

yrange_tooltips = dbc.Tooltip(
    "format: y_min, y_max",
    id="yrange-tooltip",
    target="yrange",
    placement="right-end",
)

control_panel = [
    html.Div(yrange_tooltips),
    html.B(dbc.Label("Pick Data to Plot")),
    dbc.Col(
        dbc.Checklist(
            id="checklist",
            options=[
                {"label": "vasp", "value": "vasp"},
                {
                    "label": "vasp projection",
                    "value": "proj",
                },
                {
                    "label": "wannier",
                    "value": "wann",
                },
            ],
            value=["proj"],
            inline=True,
        ),
        # width={"size": 4, "offset": 1},
    ),
    dbc.Col(
        dmc.TextInput(
            id="yrange",
            label="Y-axis Limit",
            placeholder="-4, 4",
            value="-4, 4",
            size="xs",
            error=False,
            style={"width": 100},
        ),
        md=4,
    ),
]

graph_panel = [
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
        # required to render latex
        mathjax=True,
    ),
    dbc.Row(
        [
            dbc.Col(
                dmc.Button(
                    "Plot",
                    id="generate-button",
                    n_clicks=0,
                    variant="gradient",
                    leftIcon=DashIconify(icon="mdi:graph-line", height=20),
                ),
                width={"size": 3, "offset": 4},
            ),
        ],
        align="center",
    ),
]
