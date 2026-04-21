import json

import dash
from aphylogeo.params import Params
from dash import Input, Output, State, callback, ctx, dcc, html
from dash.exceptions import PreventUpdate
from components.page_section import create_field, create_page_section
from utils.i18n import LANGUAGE_LIST, t
from enums import (AlignmentMethod, DistanceMethod, FitMethod,
                   MantelTestMethod, PreprocessingToggle, SimilarityMethod,
                   StatisticalTest, TreeType)

dash.register_page(__name__, path="/settings")

# Minimum and maximum values for settings
BOOTSTRAP_THRESHOLD_MIN = 0
BOOTSTRAP_THRESHOLD_MAX = 100
DISTANCE_THRESHOLD_MIN = 0
DISTANCE_THRESHOLD_MAX = 100000

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
DISTANCE_THRESHOLD_DEFAULT = 10000

WINDOW_SIZE_DEFAULT = 200
STEP_SIZE_DEFAULT = 100
ALIGNMENT_METHOD_DEFAULT = AlignmentMethod.PAIRWISE_ALIGN.value
DISTANCE_METHOD_DEFAULT = DistanceMethod.LEAST_SQUARE.value
FIT_METHOD_DEFAULT = FitMethod.WIDER_FIT.value
TREE_TYPE_DEFAULT = TreeType.BIOPYTHON.value
RATE_SIMILARITY_DEFAULT = 50
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

SETTINGS_FILE_PATH = "genetic_settings_file.json"


def _read_settings() -> dict:
    try:
        with open(SETTINGS_FILE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return get_default_settings()


def get_alignment_method_options(lang="en"):
    return [
        {"label": t("setting.options.alignment.no-alignment", lang), "value": AlignmentMethod.NO_ALIGNMENT.value},
        {"label": t("setting.options.alignment.pairwise-align", lang), "value": AlignmentMethod.PAIRWISE_ALIGN.value},
        {"label": t("setting.options.alignment.muscle", lang), "value": AlignmentMethod.MUSCLE.value},
        {"label": t("setting.options.alignment.clustalw", lang), "value": AlignmentMethod.CLUSTALW.value},
        {"label": t("setting.options.alignment.mafft", lang), "value": AlignmentMethod.MAFFT.value},
    ]


def get_distance_method_options(lang="en"):
    return [
        {"label": t("setting.options.distance.all", lang), "value": DistanceMethod.ALL.value},
        {"label": t("setting.options.distance.least-square", lang), "value": DistanceMethod.LEAST_SQUARE.value},
        {"label": t("setting.options.distance.robinson-foulds", lang), "value": DistanceMethod.ROBINSON_FOULDS.value},
        {"label": t("setting.options.distance.bipartition", lang), "value": DistanceMethod.BIPARTITION.value},
    ]


def get_fit_method_options(lang="en"):
    return [
        {"label": t("setting.options.fit.wider-fit", lang), "value": FitMethod.WIDER_FIT.value},
        {"label": t("setting.options.fit.narrow-fit", lang), "value": FitMethod.NARROW_FIT.value},
    ]


def get_tree_type_options(lang="en"):
    return [
        {"label": t("setting.options.tree.biopython", lang), "value": TreeType.BIOPYTHON.value},
        {"label": t("setting.options.tree.fast-tree", lang), "value": TreeType.FASTTREE.value},
    ]


def get_similarity_method_options(lang="en"):
    return [
        {"label": t("setting.options.similarity.hamming", lang), "value": SimilarityMethod.HAMMING.value},
        {"label": t("setting.options.similarity.levenshtein", lang), "value": SimilarityMethod.LEVENSHTEIN.value},
        {"label": t("setting.options.similarity.damerau-levenshtein", lang), "value": SimilarityMethod.DAMERAU_LEVENSHTEIN.value},
        {"label": t("setting.options.similarity.jaro", lang), "value": SimilarityMethod.JARO.value},
        {"label": t("setting.options.similarity.jaro-winkler", lang), "value": SimilarityMethod.JARO_WINKLER.value},
        {"label": t("setting.options.similarity.smith-waterman", lang), "value": SimilarityMethod.SMITH_WATERMAN.value},
        {"label": t("setting.options.similarity.jaccard", lang), "value": SimilarityMethod.JACCARD.value},
        {"label": t("setting.options.similarity.sorensen-dice", lang), "value": SimilarityMethod.SORENSEN_DICE.value},
    ]


def get_preprocessing_toggle_options(lang="en"):
    return [
        {"label": t("setting.options.preprocessing.disabled", lang), "value": PreprocessingToggle.DISABLED.value},
        {"label": t("setting.options.preprocessing.enabled", lang), "value": PreprocessingToggle.ENABLED.value},
    ]


def get_statistical_test_options(lang="en"):
    return [
        {"label": t("setting.options.statistical.both", lang), "value": StatisticalTest.BOTH.value},
        {"label": t("setting.options.statistical.mantel", lang), "value": StatisticalTest.MANTEL_TEST.value},
        {"label": t("setting.options.statistical.procrustes", lang), "value": StatisticalTest.PROCRUSTES.value},
        {"label": t("setting.options.statistical.none", lang), "value": StatisticalTest.NONE.value},
    ]


def get_mantel_method_options(lang="en"):
    return [
        {"label": t("setting.options.mantel.pearson", lang), "value": MantelTestMethod.PEARSON.value},
        {"label": t("setting.options.mantel.spearman", lang), "value": MantelTestMethod.SPEARMAN.value},
        {"label": t("setting.options.mantel.kendall-tau", lang), "value": MantelTestMethod.KENDALL_TAU.value},
    ]


def get_layout(lang="en"):
    settings = _read_settings()
    return html.Div(
        className="page-container",
        children=[
            dcc.Store(
                id="genetic-settings", storage_type="session", data=settings
            ),
            html.Div(t("setting.title", lang), className="title"),
            html.Div(
                className="page-card",
                children=[
                    # --- Genetic Parameters ---
                    create_page_section(
                        t("setting.sections.genetic-parameters", lang),
                        icon_src="/assets/icons/dna.svg",
                        children=[
                            create_field(
                                t("setting.fields.bootstrap-threshold", lang),
                                dcc.Input(
                                    id="bootstrap-threshold",
                                    type="number",
                                    value=settings["bootstrap_threshold"],
                                ),
                            ),
                            create_field(
                                t("setting.fields.distance-threshold", lang),
                                dcc.Input(
                                    id="distance-threshold",
                                    type="number",
                                    value=settings["dist_threshold"],
                                ),
                            ),
                            create_field(
                                t("setting.fields.window-size", lang),
                                dcc.Input(
                                    id="input-window-size",
                                    type="number",
                                    value=settings["window_size"],
                                ),
                            ),
                            create_field(
                                t("setting.fields.step-size", lang),
                                dcc.Input(
                                    id="input-step-size",
                                    type="number",
                                    value=settings["step_size"],
                                ),
                            ),
                            create_field(
                                t("setting.fields.similarity-rate", lang),
                                dcc.Input(
                                    id="rate-similarity",
                                    type="number",
                                    value=settings["rate_similarity"],
                                ),
                            ),
                        ],
                    ),

                    # --- Alignment Method ---
                    create_page_section(
                        t("setting.sections.alignment-method", lang),
                        icon_src="/assets/icons/grip-lines.svg",
                        children=[
                            create_field(
                                t("setting.fields.alignment-method", lang),
                                dcc.Dropdown(
                                    id="alignment-method",
                                    options=get_alignment_method_options(lang),
                                    value=settings.get("alignment_method", ALIGNMENT_METHOD_DEFAULT),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                            create_field(
                                t("setting.fields.distance-method", lang),
                                dcc.Dropdown(
                                    id="distance-method",
                                    options=get_distance_method_options(lang),
                                    value=settings.get("distance_method", DISTANCE_METHOD_DEFAULT),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                            create_field(
                                t("setting.fields.fit-method", lang),
                                dcc.Dropdown(
                                    id="fit-method",
                                    options=get_fit_method_options(lang),
                                    value=settings.get("fit_method", FIT_METHOD_DEFAULT),
                                    optionHeight=50,
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                        ],
                    ),

                    # --- Tree Type ---
                    create_page_section(
                        t("setting.sections.tree-type", lang),
                        icon_src="/assets/icons/chart-diagram.svg",
                        children=[
                            create_field(
                                t("setting.fields.tree-type", lang),
                                dcc.Dropdown(
                                    id="tree-type",
                                    options=get_tree_type_options(lang),
                                    value=settings.get("tree_type", TREE_TYPE_DEFAULT),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                            create_field(
                                t("setting.fields.similarity-method", lang),
                                dcc.Dropdown(
                                    id="method-similarity",
                                    options=get_similarity_method_options(lang),
                                    value=settings.get("method_similarity", METHOD_SIMILARITY_DEFAULT),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                        ],
                    ),

                    # --- Preprocessing ---
                    create_page_section(
                        t("setting.sections.preprocessing", lang),
                        icon_src="/assets/icons/gears.svg",
                        children=[
                            create_field(
                                t("setting.fields.genetic-preprocessing", lang),
                                dcc.Dropdown(
                                    id="preprocessing-genetic",
                                    options=get_preprocessing_toggle_options(lang),
                                    value=settings.get(
                                        "preprocessing_genetic",
                                        PREPROCESSING_GENETIC_DEFAULT,
                                    ),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                            create_field(
                                t("setting.fields.genetic-threshold", lang),
                                dcc.Input(
                                    id="preprocessing-threshold-genetic",
                                    type="number",
                                    step=0.01,
                                    value=settings.get(
                                        "preprocessing_threshold_genetic",
                                        PREPROCESSING_THRESHOLD_GENETIC_DEFAULT,
                                    ),
                                ),
                            ),
                            create_field(
                                t("setting.fields.climatic-preprocessing", lang),
                                dcc.Dropdown(
                                    id="preprocessing-climatic",
                                    options=get_preprocessing_toggle_options(lang),
                                    value=settings.get(
                                        "preprocessing_climatic",
                                        PREPROCESSING_CLIMATIC_DEFAULT,
                                    ),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                            create_field(
                                t("setting.fields.climatic-threshold", lang),
                                dcc.Input(
                                    id="preprocessing-threshold-climatic",
                                    type="number",
                                    step=0.01,
                                    value=settings.get(
                                        "preprocessing_threshold_climatic",
                                        PREPROCESSING_THRESHOLD_CLIMATIC_DEFAULT,
                                    ),
                                ),
                            ),
                            create_field(
                                t("setting.fields.correlation-filtering-climatic", lang),
                                dcc.Dropdown(
                                    id="correlation-climatic-enabled",
                                    options=get_preprocessing_toggle_options(lang),
                                    value=settings.get(
                                        "correlation_climatic_enabled",
                                        CORRELATION_CLIMATIC_ENABLED_DEFAULT,
                                    ),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                            create_field(
                                t("setting.fields.max-correlation-climatic", lang),
                                dcc.Input(
                                    id="max-correlation-climatic",
                                    type="number",
                                    step=0.01,
                                    value=settings.get(
                                        "correlation_threshold_climatic",
                                        CORRELATION_THRESHOLD_CLIMATIC_DEFAULT,
                                    ),
                                ),
                            ),
                        ],
                    ),

                    # --- Statistical Tests ---
                    create_page_section(
                        t("setting.sections.statistical-tests", lang),
                        icon_src="/assets/icons/flask.svg",
                        children=[
                            create_field(
                                t("setting.fields.statistical-test", lang),
                                dcc.Dropdown(
                                    id="statistical-test",
                                    options=get_statistical_test_options(lang),
                                    value=settings.get(
                                        "statistical_test",
                                        STATISTICAL_TEST_DEFAULT,
                                    ),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                            create_field(
                                t("setting.fields.mantel-test-method", lang),
                                dcc.Dropdown(
                                    id="mantel-test-method",
                                    options=get_mantel_method_options(lang),
                                    value=settings.get(
                                        "mantel_test_method",
                                        MANTEL_TEST_METHOD_DEFAULT,
                                    ),
                                    clearable=False,
                                    className="pointer-dropdown",
                                ),
                            ),
                            create_field(
                                t("setting.fields.mantel-test-permutations", lang),
                                dcc.Input(
                                    id="permutations-mantel-test",
                                    type="number",
                                    value=settings.get(
                                        "permutations_mantel_test",
                                        PERMUTATIONS_MANTEL_TEST_DEFAULT,
                                    ),
                                ),
                            ),
                            create_field(
                                t("setting.fields.protest-permutations", lang),
                                dcc.Input(
                                    id="permutations-protest",
                                    type="number",
                                    value=settings.get(
                                        "permutations_protest",
                                        PERMUTATIONS_PROTEST_DEFAULT,
                                    ),
                                ),
                            ),
                        ],
                    ),

                    # --- Action Buttons ---
                    html.Div(
                        className="page-actions",
                        children=[
                            html.Button(
                                t("setting.actions.save", lang),
                                id="save-settings-button",
                                n_clicks=0,
                                className="button theme-action",
                            ),
                            html.Button(
                                t("setting.actions.reset", lang),
                                id="reset-button",
                                n_clicks=0,
                                className="button primary border",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def layout():
    from flask import request
    lang = request.cookies.get("lang", "en")
    return html.Div(id="settings-page-content", children=get_layout(lang))


@callback(Output("settings-page-content", "children"), Input("language-store", "data"))
def update_settings_language(language):
    lang = language if language in LANGUAGE_LIST else "en"
    return get_layout(lang)


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


def validate_updated_settings(settings, lang="en"):
    """
    Validate that all numeric settings are within their allowed bounds.

    Args:
        settings: dict of setting key -> value

    Returns:
        str | None: A human-readable error message if any value is invalid,
                    or None if all values are valid.
    """
    numeric_bounds = [
        (
            "bootstrap_threshold",
            "setting.fields.bootstrap-threshold",
            BOOTSTRAP_THRESHOLD_MIN,
            BOOTSTRAP_THRESHOLD_MAX,
        ),
        (
            "dist_threshold",
            "setting.fields.distance-threshold",
            DISTANCE_THRESHOLD_MIN,
            DISTANCE_THRESHOLD_MAX,
        ),
        ("window_size", "setting.fields.window-size", WINDOW_SIZE_MIN, WINDOW_SIZE_MAX),
        ("step_size", "setting.fields.step-size", STEP_SIZE_MIN, STEP_SIZE_MAX),
        (
            "rate_similarity",
            "setting.fields.similarity-rate",
            RATE_SIMILARITY_MIN,
            RATE_SIMILARITY_MAX,
        ),
        (
            "preprocessing_threshold_genetic",
            "setting.fields.genetic-threshold",
            PREPROCESSING_THRESHOLD_GENETIC_MIN,
            PREPROCESSING_THRESHOLD_GENETIC_MAX,
        ),
        (
            "preprocessing_threshold_climatic",
            "setting.fields.climatic-threshold",
            PREPROCESSING_THRESHOLD_CLIMATIC_MIN,
            PREPROCESSING_THRESHOLD_CLIMATIC_MAX,
        ),
        (
            "correlation_threshold_climatic",
            "setting.fields.max-correlation-climatic",
            CORRELATION_THRESHOLD_CLIMATIC_MIN,
            CORRELATION_THRESHOLD_CLIMATIC_MAX,
        ),
        (
            "permutations_mantel_test",
            "setting.fields.mantel-test-permutations",
            PERMUTATIONS_MIN,
            PERMUTATIONS_MAX,
        ),
        (
            "permutations_protest",
            "setting.fields.protest-permutations",
            PERMUTATIONS_MIN,
            PERMUTATIONS_MAX,
        ),
    ]
    for key, label_key, min_val, max_val in numeric_bounds:
        value = settings.get(key)
        label = t(label_key, lang)
        if value is None:
            return t("setting.validation.required", lang).replace("{field}", label)
        if not (min_val <= value <= max_val):
            return (
                t("setting.validation.range", lang)
                .replace("{field}", label)
                .replace("{min}", str(min_val))
                .replace("{max}", str(max_val))
                .replace("{value}", str(value))
            )
    return None


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
    State("language-store", "data"),
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
    language,
):
    lang = language if language in LANGUAGE_LIST else "en"
    # Prevent callback from running if no button was actually clicked
    if not n_clicks_reset and not n_clicks_save:
        raise PreventUpdate

    # Load default parameters if reset button is clicked
    if ctx.triggered_id == "reset-button":
        default_params = Params()
        # Assuming Params class has a method called `to_dict` or similar to get default settings
        if hasattr(default_params, "to_dict"):
            return default_params.to_dict(), {
                "message": t("setting.toast.reset-default", lang),
                "type": "success",
            }
        else:
            return get_default_settings(), {
                "message": t("setting.toast.reset-default", lang),
                "type": "success",
            }

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
        error = validate_updated_settings(updated_settings, lang)
        if error:
            return dash.no_update, {"message": error, "type": "error"}

        with open("genetic_settings_file.json", "w") as file:
            json.dump(updated_settings, file, indent=4)

        # Update the settings store
        return updated_settings, {
            "message": t("setting.toast.saved-success", lang),
            "type": "success",
        }

    else:
        raise PreventUpdate
