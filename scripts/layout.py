import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify


def make_dmc_tooltips(child, label, **kwargs):
    return dmc.Tooltip(
        label=label, children=[child], position="right", transition="pop", **kwargs
    )


def make_dmc_fileinput_tooltips(child):
    file_input_tooltip_label = html.P(
        [
            "Input ./ to select under home directory. Fields with ",
            html.Span("*", style={"color": "red"}),
            " are required.",
        ]
    )

    return dmc.Tooltip(
        label=file_input_tooltip_label,
        children=[child],
        multiline=True,
        position="right",
        withArrow=True,
        transition="pop",
        width=300,
        color="gray",
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


file_input_panel = [
    # html.Div(file_input_tooltips),
    dbc.Col(
        make_dmc_fileinput_tooltips(
            dmc.TextInput(
                id="vasp-input",
                type="text",
                placeholder="Enter a path...",
                label="VASPRUN XML Path",
                required=False,
                debounce=True,
                style={"width": 300},
            )
        ),
        md=12,
        # className="my-2",
    ),
    dbc.Col(
        dmc.Select(
            id="vasp-input-dropdown",
            data=[],
            searchable=True,
            clearable=True,
            placeholder="Select under path",
            value=None,
            style={"width": 300},
            mb=5,
        ),
        className="my-1",
        md=12,
    ),
    dbc.Col(
        make_dmc_fileinput_tooltips(
            dmc.TextInput(
                id="kpoints-input",
                type="text",
                placeholder="Enter a path...",
                label="KPOINTS Path",
                required=False,
                debounce=True,
                style={"width": 300},
            )
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
            style={"width": 300},
            mb=5,
        ),
        className="my-1",
        md=12,
    ),
    dbc.Col(
        make_dmc_fileinput_tooltips(
            dmc.TextInput(
                id="proj-input",
                type="text",
                placeholder="Enter a path...",
                label="PROCAR Path",
                required=False,
                debounce=True,
                style={"width": 300},
            )
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
            style={"width": 300},
            mb=5,
        ),
        className="my-1",
        md=12,
    ),
    dbc.Col(
        make_dmc_fileinput_tooltips(
            dmc.TextInput(
                id="wann-input",
                type="text",
                placeholder="Enter a path...",
                label="Wanneier Band Data Path",
                required=False,
                debounce=True,
                style={"width": 300},
            )
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
            style={"width": 300},
            mb=5,
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
    dbc.Col(
        make_dmc_tooltips(
            dmc.Button(
                "Load Data",
                leftIcon=DashIconify(
                    icon="fluent:database-plug-connected-20-filled", width=20
                ),
                id="load-data",
                size="sm",
                mt=5,
                mb=5,
                variant="outline",
                color="blue",
                n_clicks=0,
            ),
            label="Click to load data so that it can be plotted",
            color="gray",
        ),
        md=3,
    ),
    dbc.Col(
        dmc.CheckboxGroup(
            id="checklist",
            label="Pick Data to Plot",
            orientation="horizontal",
            offset="xs",
            mb=5,
            children=[
                dmc.Checkbox(label="Vasp", value="vasp"),
                dmc.Checkbox(label="Projection", value="proj"),
                dmc.Checkbox(label="Wannier", value="wann"),
            ],
            value=["proj"],
        ),
        md=12,
    ),
    dbc.Col(
        dmc.MultiSelect(
            id="atom-select",
            label="Select Atoms",
            data=[],
            mb=5,
            # style={"width": 200},
        ),
        md=8,
    ),
    dbc.Col(
        dmc.MultiSelect(
            id="orbital-select",
            label="Select Orbitals",
            data=[],
        ),
        md=8,
    ),
    dmc.TextInput(
        id="yrange",
        label="Y-axis Limit",
        placeholder="-4, 4",
        value="-4, 4",
        size="sm",
        error=False,
        style={"width": 100},
        rightSection=dmc.ActionIcon(
            DashIconify(icon="material-symbols:sync", width=20),
            id="update-yrange",
            # size="lg",
            color="blue",
            variant="subtle",
        ),
    ),
]

graph_panel = [
    dcc.Store(id="loaded-data"),
    dmc.LoadingOverlay(
        html.Div(
            children=[
                dcc.Graph(
                    id="graph",
                    config={
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": "wann-app",
                            "height": 600,
                            "width": 800,
                            "scale": 4,
                        }
                    },
                    # required to render latex
                    mathjax=True,
                )
            ],
            id="graph-overlay",
        ),
        loaderProps={"variant": "dots", "color": "blue", "size": "xl"},
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
        align="end",
        justify="between",
    ),
]

layout = dbc.Container(
    [
        header,
        html.Br(),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            (file_input_panel + control_panel),
                            # md=3,
                            style={"overflowY": "scroll", "height": "600px"},
                            width={"size": 3, "offset": 0},
                            # class_name="bg-light",
                        ),
                        dbc.Col(graph_panel, width={"size": 8}),
                    ],
                    # align="center",
                    justify="around",
                )
            ]
        ),
    ],
    fluid=True,
)
