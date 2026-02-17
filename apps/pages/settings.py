import json

import dash
import dash_bootstrap_components as dbc
from aphylogeo.params import Params
from dash import Input, Output, State, callback, ctx, dcc, html
from dash.exceptions import PreventUpdate
from enums import (AlignmentMethod, DistanceMethod, FitMethod,
                   MantelTestMethod, PreprocessingToggle, SimilarityMethod,
                   StatisticalTest, TreeType)

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

PREPROCESSING_THRESHOLD_GENETIC_MIN = 0
PREPROCESSING_THRESHOLD_GENETIC_MAX = 1
PREPROCESSING_THRESHOLD_CLIMATIC_MIN = 0
PREPROCESSING_THRESHOLD_CLIMATIC_MAX = 1
CORRELATION_THRESHOLD_CLIMATIC_MIN = 0
CORRELATION_THRESHOLD_CLIMATIC_MAX = 1
PERMUTATIONS_MIN = 1
PERMUTATIONS_MAX = 99999

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
PREPROCESSING_GENETIC_DEFAULT = PreprocessingToggle.DISABLED.value
PREPROCESSING_CLIMATIC_DEFAULT = PreprocessingToggle.DISABLED.value
PREPROCESSING_THRESHOLD_GENETIC_DEFAULT = 0
PREPROCESSING_THRESHOLD_CLIMATIC_DEFAULT = 0
CORRELATION_CLIMATIC_ENABLED_DEFAULT = PreprocessingToggle.DISABLED.value
CORRELATION_THRESHOLD_CLIMATIC_DEFAULT = 0.9
PERMUTATIONS_MANTEL_TEST_DEFAULT = 999
PERMUTATIONS_PROTEST_DEFAULT = 999
MANTEL_TEST_METHOD_DEFAULT = MantelTestMethod.PEARSON.value
STATISTICAL_TEST_DEFAULT = StatisticalTest.BOTH.value

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
                "max-width": "800px",
                "margin-left": "auto",
                "margin-right": "auto",
                "background-color": "#1A1C1E",  # Set background to black
                "color": "white",  # Set text color to white
            },
            children=[
                dbc.CardHeader(
                    "GENETIC PARAMETERS",
                    style={"font-size": "1.25rem", "text-align": "center"},
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
                                                style={"text-align": "center"},
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
                            style={"margin-top": "20px"},
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
                            style={"margin-top": "20px"},
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
                        html.Br(),
                        # --- Preprocessing Section ---
                        html.H5(
                            "Preprocessing",
                            className="card-title",
                            style={"margin-top": "20px"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Genetic preprocessing"),
                                            dcc.Dropdown(
                                                id="preprocessing-genetic",
                                                options=PreprocessingToggle.choices(),
                                                value=genetic_settings_file.get(
                                                    "preprocessing_genetic",
                                                    PREPROCESSING_GENETIC_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Genetic preprocessing threshold"),
                                            dcc.Input(
                                                id="preprocessing-threshold-genetic",
                                                type="number",
                                                min=PREPROCESSING_THRESHOLD_GENETIC_MIN,
                                                max=PREPROCESSING_THRESHOLD_GENETIC_MAX,
                                                step=0.01,
                                                value=genetic_settings_file.get(
                                                    "preprocessing_threshold_genetic",
                                                    PREPROCESSING_THRESHOLD_GENETIC_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Climatic preprocessing"),
                                            dcc.Dropdown(
                                                id="preprocessing-climatic",
                                                options=PreprocessingToggle.choices(),
                                                value=genetic_settings_file.get(
                                                    "preprocessing_climatic",
                                                    PREPROCESSING_CLIMATIC_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Climatic preprocessing threshold"),
                                            dcc.Input(
                                                id="preprocessing-threshold-climatic",
                                                type="number",
                                                min=PREPROCESSING_THRESHOLD_CLIMATIC_MIN,
                                                max=PREPROCESSING_THRESHOLD_CLIMATIC_MAX,
                                                step=0.01,
                                                value=genetic_settings_file.get(
                                                    "preprocessing_threshold_climatic",
                                                    PREPROCESSING_THRESHOLD_CLIMATIC_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Correlation filtering (climatic)"),
                                            dcc.Dropdown(
                                                id="correlation-climatic-enabled",
                                                options=PreprocessingToggle.choices(),
                                                value=genetic_settings_file.get(
                                                    "correlation_climatic_enabled",
                                                    CORRELATION_CLIMATIC_ENABLED_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Max correlation (climatic)"),
                                            dcc.Input(
                                                id="max-correlation-climatic",
                                                type="number",
                                                min=CORRELATION_THRESHOLD_CLIMATIC_MIN,
                                                max=CORRELATION_THRESHOLD_CLIMATIC_MAX,
                                                step=0.01,
                                                value=genetic_settings_file.get(
                                                    "correlation_threshold_climatic",
                                                    CORRELATION_THRESHOLD_CLIMATIC_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                            ]
                        ),
                        html.Br(),
                        # --- Statistical Tests Section ---
                        html.H5(
                            "Statistical Tests",
                            className="card-title",
                            style={"margin-top": "20px"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Statistical test"),
                                            dcc.Dropdown(
                                                id="statistical-test",
                                                options=StatisticalTest.choices(),
                                                value=genetic_settings_file.get(
                                                    "statistical_test",
                                                    STATISTICAL_TEST_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Mantel test method"),
                                            dcc.Dropdown(
                                                id="mantel-test-method",
                                                options=MantelTestMethod.choices(),
                                                value=genetic_settings_file.get(
                                                    "mantel_test_method",
                                                    MANTEL_TEST_METHOD_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("Mantel test permutations"),
                                            dcc.Input(
                                                id="permutations-mantel-test",
                                                type="number",
                                                min=PERMUTATIONS_MIN,
                                                max=PERMUTATIONS_MAX,
                                                value=genetic_settings_file.get(
                                                    "permutations_mantel_test",
                                                    PERMUTATIONS_MANTEL_TEST_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dbc.Form(
                                        [
                                            dbc.Label("PROTEST permutations"),
                                            dcc.Input(
                                                id="permutations-protest",
                                                type="number",
                                                min=PERMUTATIONS_MIN,
                                                max=PERMUTATIONS_MAX,
                                                value=genetic_settings_file.get(
                                                    "permutations_protest",
                                                    PERMUTATIONS_PROTEST_DEFAULT,
                                                ),
                                                className="form-control",
                                            ),
                                        ]
                                    ),
                                    width=6,
                                ),
                            ]
                        ),
                        html.Div(
                            id="setting-buttons",
                            style={"margin-top": "30px"},
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
        "preprocessing_genetic": PREPROCESSING_GENETIC_DEFAULT,
        "preprocessing_climatic": PREPROCESSING_CLIMATIC_DEFAULT,
        "preprocessing_threshold_genetic": PREPROCESSING_THRESHOLD_GENETIC_DEFAULT,
        "preprocessing_threshold_climatic": PREPROCESSING_THRESHOLD_CLIMATIC_DEFAULT,
        "correlation_climatic_enabled": CORRELATION_CLIMATIC_ENABLED_DEFAULT,
        "correlation_threshold_climatic": CORRELATION_THRESHOLD_CLIMATIC_DEFAULT,
        "permutations_mantel_test": PERMUTATIONS_MANTEL_TEST_DEFAULT,
        "permutations_protest": PERMUTATIONS_PROTEST_DEFAULT,
        "mantel_test_method": MANTEL_TEST_METHOD_DEFAULT,
        "statistical_test": STATISTICAL_TEST_DEFAULT,
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
    Output("preprocessing-genetic", "value"),
    Output("preprocessing-climatic", "value"),
    Output("preprocessing-threshold-genetic", "value"),
    Output("preprocessing-threshold-climatic", "value"),
    Output("correlation-climatic-enabled", "value"),
    Output("max-correlation-climatic", "value"),
    Output("permutations-mantel-test", "value"),
    Output("permutations-protest", "value"),
    Output("mantel-test-method", "value"),
    Output("statistical-test", "value"),
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
        settings.get("preprocessing_genetic", PREPROCESSING_GENETIC_DEFAULT),
        settings.get("preprocessing_climatic", PREPROCESSING_CLIMATIC_DEFAULT),
        settings.get("preprocessing_threshold_genetic", PREPROCESSING_THRESHOLD_GENETIC_DEFAULT),
        settings.get("preprocessing_threshold_climatic", PREPROCESSING_THRESHOLD_CLIMATIC_DEFAULT),
        settings.get("correlation_climatic_enabled", CORRELATION_CLIMATIC_ENABLED_DEFAULT),
        settings.get("correlation_threshold_climatic", CORRELATION_THRESHOLD_CLIMATIC_DEFAULT),
        settings.get("permutations_mantel_test", PERMUTATIONS_MANTEL_TEST_DEFAULT),
        settings.get("permutations_protest", PERMUTATIONS_PROTEST_DEFAULT),
        settings.get("mantel_test_method", MANTEL_TEST_METHOD_DEFAULT),
        settings.get("statistical_test", STATISTICAL_TEST_DEFAULT),
    )


# To reset or save the settings in the JSON file
@callback(
    Output("genetic-settings", "data"),
    Output("toast-store", "data", allow_duplicate=True),
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
    State("preprocessing-genetic", "value"),
    State("preprocessing-climatic", "value"),
    State("preprocessing-threshold-genetic", "value"),
    State("preprocessing-threshold-climatic", "value"),
    State("correlation-climatic-enabled", "value"),
    State("max-correlation-climatic", "value"),
    State("permutations-mantel-test", "value"),
    State("permutations-protest", "value"),
    State("mantel-test-method", "value"),
    State("statistical-test", "value"),
    prevent_initial_call=True,
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
    preprocessing_genetic,
    preprocessing_climatic,
    preprocessing_threshold_genetic,
    preprocessing_threshold_climatic,
    correlation_climatic_enabled,
    correlation_threshold_climatic,
    permutations_mantel_test,
    permutations_protest,
    mantel_test_method,
    statistical_test,
):
    # Prevent callback from running if no button was actually clicked
    if not n_clicks_reset and not n_clicks_save:
        raise PreventUpdate

    # Load default parameters if reset button is clicked
    if ctx.triggered_id == "reset-button":
        default_params = Params()
        # Assuming Params class has a method called `to_dict` or similar to get default settings
        if hasattr(default_params, "to_dict"):
            return default_params.to_dict(), {"message": "Settings reset to default", "type": "success"}
        else:
            return get_default_settings(), {"message": "Settings reset to default", "type": "success"}

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
            "preprocessing_genetic": preprocessing_genetic,
            "preprocessing_climatic": preprocessing_climatic,
            "preprocessing_threshold_genetic": preprocessing_threshold_genetic,
            "preprocessing_threshold_climatic": preprocessing_threshold_climatic,
            "correlation_climatic_enabled": correlation_climatic_enabled,
            "correlation_threshold_climatic": correlation_threshold_climatic,
            "permutations_mantel_test": permutations_mantel_test,
            "permutations_protest": permutations_protest,
            "mantel_test_method": mantel_test_method,
            "statistical_test": statistical_test,
        }
        with open("genetic_settings_file.json", "w") as file:
            json.dump(updated_settings, file, indent=4)

        # Update the settings store
        return updated_settings, {"message": "Settings saved successfully", "type": "success"}

    else:
        raise PreventUpdate
