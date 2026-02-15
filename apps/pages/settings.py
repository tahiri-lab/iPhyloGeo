import json

import dash
import dash_bootstrap_components as dbc
from aphylogeo.params import Params
from dash import Input, Output, State, callback, ctx, dcc, html
from dash.exceptions import PreventUpdate
from enums import AlignmentMethod, DistanceMethod, FitMethod, SimilarityMethod, TreeType

dash.register_page(__name__, path="/settings")

# Minimum and maximum values for settings
BOOTSTRAP_THRESHOLD_MIN = 0
BOOTSTRAP_THRESHOLD_MAX = 100
DISTANCE_THRESHOLD_MIN = 0
DISTANCE_THRESHOLD_MAX = 100

WINDOW_SIZE_MIN = 1
WINDOW_SIZE_MAX = 1000
STEP_SIZE_MIN = 1
STEP_SIZE_MAX = 500
RATE_SIMILARITY_MIN = 0
RATE_SIMILARITY_MAX = 100

# Default values for settings
BOOTSTRAP_THRESHOLD_DEFAULT = 10
DISTANCE_THRESHOLD_DEFAULT = 50

WINDOW_SIZE_DEFAULT = 200
STEP_SIZE_DEFAULT = 100
ALIGNMENT_METHOD_DEFAULT = AlignmentMethod.PAIRWISE_ALIGN.value
DISTANCE_METHOD_DEFAULT = DistanceMethod.LEAST_SQUARE.value
FIT_METHOD_DEFAULT = FitMethod.WIDER_FIT.value
TREE_TYPE_DEFAULT = TreeType.BIOPYTHON.value
RATE_SIMILARITY_DEFAULT = 90
METHOD_SIMILARITY_DEFAULT = SimilarityMethod.HAMMING.value

# Load the genetic settings file
with open("genetic_settings_file.json", "r") as file:
    genetic_settings_file = json.load(file)

layout = html.Div(
    [
        dcc.Store(
            id="genetic-settings", storage_type="session", data=genetic_settings_file
        ),
        dbc.Card(
            id="main-container",
            style={
                "margin": "20px",
                "width": "80%",
                "maxWidth": "800px",
                "marginLeft": "auto",
                "marginRight": "auto",
                "backgroundColor": "#1A1C1E",  # Set background to black
                "color": "white",  # Set text color to white
            },
            children=[
                dbc.CardHeader(
                    "GENETIC PARAMETERS",
                    style={"fontSize": "1.25rem", "textAlign": "center"},
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label(
                                                "Bootstrap threshold",
                                                style={"textAlign": "center"},
                                            ),
                                            dcc.Input(
                                                id="bootstrap-threshold",
                                                type="number",
                                                min=BOOTSTRAP_THRESHOLD_MIN,
                                                max=BOOTSTRAP_THRESHOLD_MAX,
                                                value=genetic_settings_file[
                                                    "bootstrap_threshold"
                                                ],
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    className="form-group",
                                    width=4,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Distance threshold"),
                                            dcc.Input(
                                                id="distance-threshold",
                                                type="number",
                                                min=DISTANCE_THRESHOLD_MIN,
                                                max=DISTANCE_THRESHOLD_MAX,
                                                value=genetic_settings_file[
                                                    "dist_threshold"
                                                ],
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=4,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Window size"),
                                            dcc.Input(
                                                id="input-window-size",
                                                type="number",
                                                min=WINDOW_SIZE_MIN,
                                                max=WINDOW_SIZE_MAX,
                                                value=genetic_settings_file[
                                                    "window_size"
                                                ],
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=4,
                                ),
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Step size"),
                                            dcc.Input(
                                                id="input-step-size",
                                                type="number",
                                                min=STEP_SIZE_MIN,
                                                max=STEP_SIZE_MAX,
                                                value=genetic_settings_file[
                                                    "step_size"
                                                ],
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=4,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Similarity rate"),
                                            dcc.Input(
                                                id="rate-similarity",
                                                type="number",
                                                min=RATE_SIMILARITY_MIN,
                                                max=RATE_SIMILARITY_MAX,
                                                value=genetic_settings_file[
                                                    "rate_similarity"
                                                ],
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=4,
                                ),
                            ]
                        ),
                        html.Br(),
                        # --- Alignment Method Section ---
                        html.H5(
                            "Alignment Method",
                            className="card-title",
                            style={"marginTop": "20px"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Alignment method"),
                                            dcc.Dropdown(
                                                id="alignment-method",
                                                options=AlignmentMethod.choices(),
                                                value=ALIGNMENT_METHOD_DEFAULT,
                                                className="form-control",
                                                clearable=False,
                                            ),
                                        ]
                                    ),
                                    width=4,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Distance method"),
                                            dcc.Dropdown(
                                                id="distance-method",
                                                options=DistanceMethod.choices(),
                                                value=DISTANCE_METHOD_DEFAULT,
                                                className="form-control",
                                                clearable=False,
                                            ),
                                        ]
                                    ),
                                    width=4,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Fit method"),
                                            dcc.Dropdown(
                                                id="fit-method",
                                                options=FitMethod.choices(),
                                                value=FIT_METHOD_DEFAULT,
                                                className="form-control",
                                                optionHeight=50,
                                                clearable=False,
                                            ),
                                        ]
                                    ),
                                    width=4,
                                ),
                            ]
                        ),
                        html.Br(),
                        # --- Tree Type Section ---
                        html.H5(
                            "Tree Type",
                            className="card-title",
                            style={"marginTop": "20px"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Tree type"),
                                            dcc.Dropdown(
                                                id="tree-type",
                                                options=TreeType.choices(),
                                                value=TREE_TYPE_DEFAULT,
                                                className="form-control",
                                                clearable=False,
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Similarity method"),
                                            dcc.Dropdown(
                                                id="method-similarity",
                                                options=SimilarityMethod.choices(),
                                                value=METHOD_SIMILARITY_DEFAULT,
                                                className="form-control",
                                                clearable=False,
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                            ]
                        ),
                        html.Div(
                            id="setting-buttons",
                            style={"marginTop": "30px"},
                            children=[
                                dbc.Button(
                                    "Reset to default",
                                    id="reset-button",
                                    n_clicks=0,
                                    color="secondary",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Save settings",
                                    id="save-settings-button",
                                    n_clicks=0,
                                    color="primary",
                                ),
                            ],
                        ),
                    ]
                ),
            ],
        ),
    ]
)


# Function to return default settings if `Params` class does not provide one
def get_default_settings():
    return {
        "bootstrap_threshold": BOOTSTRAP_THRESHOLD_DEFAULT,
        "dist_threshold": DISTANCE_THRESHOLD_DEFAULT,
        "window_size": WINDOW_SIZE_DEFAULT,
        "step_size": STEP_SIZE_DEFAULT,
        "alignment_method": ALIGNMENT_METHOD_DEFAULT,
        "distance_method": DISTANCE_METHOD_DEFAULT,
        "fit_method": FIT_METHOD_DEFAULT,
        "tree_type": TREE_TYPE_DEFAULT,
        "rate_similarity": RATE_SIMILARITY_DEFAULT,
        "method_similarity": METHOD_SIMILARITY_DEFAULT,
    }


# Update settings on the form
@callback(
    Output("bootstrap-threshold", "value"),
    Output("distance-threshold", "value"),
    Output("input-window-size", "value"),
    Output("input-step-size", "value"),
    Output("alignment-method", "value"),
    Output("distance-method", "value"),
    Output("fit-method", "value"),
    Output("tree-type", "value"),
    Output("rate-similarity", "value"),
    Output("method-similarity", "value"),
    Input("genetic-settings", "data"),
)
def update_settings(settings):
    return (
        settings["bootstrap_threshold"],
        settings["dist_threshold"],
        settings["window_size"],
        settings["step_size"],
        settings["alignment_method"],
        settings["distance_method"],
        settings["fit_method"],
        settings["tree_type"],
        settings["rate_similarity"],
        settings["method_similarity"],
    )


# To reset or save the settings in the JSON file
@callback(
    Output("genetic-settings", "data"),
    Input("reset-button", "n_clicks"),
    Input("save-settings-button", "n_clicks"),
    State("bootstrap-threshold", "value"),
    State("distance-threshold", "value"),
    State("input-window-size", "value"),
    State("input-step-size", "value"),
    State("alignment-method", "value"),
    State("distance-method", "value"),
    State("fit-method", "value"),
    State("tree-type", "value"),
    State("rate-similarity", "value"),
    State("method-similarity", "value"),
)
def update_parameters(
    n_clicks_reset,
    n_clicks_save,
    bootstrap_threshold,
    dist_threshold,
    window_size,
    step_size,
    alignment_method,
    distance_method,
    fit_method,
    tree_type,
    rate_similarity,
    method_similarity,
):
    # Load default parameters if reset button is clicked
    if ctx.triggered_id == "reset-button":
        default_params = Params()
        # Assuming Params class has a method called `to_dict` or similar to get default settings
        if hasattr(default_params, "to_dict"):
            return default_params.to_dict()
        else:
            return get_default_settings()

    # Save the settings to the JSON file if save button is clicked
    elif ctx.triggered_id == "save-settings-button":
        updated_settings = {
            "bootstrap_threshold": bootstrap_threshold,
            "dist_threshold": dist_threshold,
            "window_size": window_size,
            "step_size": step_size,
            "alignment_method": alignment_method,
            "distance_method": distance_method,
            "fit_method": fit_method,
            "tree_type": tree_type,
            "rate_similarity": rate_similarity,
            "method_similarity": method_similarity,
        }
        with open("genetic_settings_file.json", "w") as file:
            json.dump(updated_settings, file, indent=4)

        # Update the settings store
        return updated_settings

    else:
        raise PreventUpdate
