import json
import math
import re
from io import StringIO

import dash
from bson import ObjectId
import dash_cytoscape as cyto
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import utils.mail as mail
import utils.utils as utils
from utils.i18n import LANGUAGE_LIST, t
from Bio import Phylo
from components.email_input import (
    create_email_input,
    get_button_id,
    validate_email,
)
from dash import (
    ClientsideFunction,
    callback,
    clientside_callback,
    dash_table,
    dcc,
    html,
)
from dash.dependencies import Input, Output, State
from db.controllers import temp_results
from db.controllers.files import str_csv_to_df
from flask import request
from plotly.subplots import make_subplots

dash.register_page(__name__, path_template="/result/<result_id>")


def _get_result_id_from_path(path):
    if not path:
        return None
    return path.split("/")[-1]


def _is_valid_result_id(result_id):
    if not result_id:
        return False
    return ObjectId.is_valid(result_id) or temp_results.is_temp_result_id(result_id)


def _load_result_from_path(path):
    result_id = _get_result_id_from_path(path)
    if not _is_valid_result_id(result_id):
        return None, None

    result = utils.get_result(result_id)
    if not result:
        return result_id, None

    return result_id, result


def _missing_result_toast(lang):
    return {"message": t("result.errors.not-found-message", lang), "type": "error"}


def create_email_section(lang="en"):
    """
    Creates the email share section content (header + input).
    """
    return [
        html.Div(
            [
                html.Div(t("result.sections.share-result", lang), className="result-section-title"),
                html.Img(
                    src="../../assets/icons/angle-down.svg",
                    id="results-email-collapse-button",
                    className="icon collapse-icon",
                ),
            ],
            className="result-section-header",
        ),
        html.Div(
            [
                html.P(
                    t("result.sections.email-description", lang),
                    className="email-description",
                ),
                create_email_input(
                    input_id="user-input",
                    placeholder=t("result.email.placeholder", lang),
                    button_text=t("result.email.send", lang),
                ),
            ],
            id="email-section-container",
        ),
    ]


layout = html.Div(
    [
        dcc.Interval(id="result-alive-check", interval=30000, n_intervals=0),
        # Interval for auto-refreshing while result is processing
        dcc.Interval(
            id="result-status-interval",
            interval=3000,  # Poll every 3 seconds
            n_intervals=0,
        ),
        dcc.Store(id="result-processing-status", data=None),
        dcc.Store(id="refresh-trigger", data=0),  # Trigger to force component refresh
        # Hidden placeholder buttons for dynamic download buttons (suppress callback exceptions)
        html.Button(id="download-btn-genetic", style={"display": "none"}),
        html.Button(id="download-btn-climatic", style={"display": "none"}),
        html.Button(id="download-btn-genetic-json", style={"display": "none"}),
        html.Button(id="download-btn-complete", style={"display": "none"}),
        html.Div(id="dummy-share-result-output", className="hidden"),
        html.Div(id="dummy-table-collapse", className="hidden"),
        html.Div(id="dummy-climatic-collapse", className="hidden"),
        html.Div(id="dummy-genetic-collapse", className="hidden"),
        html.Div(id="dummy-email-collapse", className="hidden"),
        html.Div(
            [
                html.H1(id="results-name", className="title"),
                html.Div(id="unavailable-result-message", className="hidden"),
                # Processing status with spinner (shown when not complete)
                html.Div(
                    id="processing-status-container",
                    className="processing-status-container",
                    style={"display": "none"},
                ),
                # Error banner (shown when result has errored)
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(t("result.error.title", "en"), className="error-banner__title", id="error-banner-title"),
                                html.Div(t("result.error.description", "en"), className="error-banner__description", id="error-banner-description"),
                            ],
                            className="error-banner__body",
                        ),
                        html.A(
                            t("result.error.back", "en"),
                            href="/results",
                            className="button error",
                            id="error-banner-back",
                        ),
                    ],
                    id="error-banner",
                    className="error-banner hidden",
                ),
                # Top action buttons row
                html.Div(
                    [
                        # Top action buttons row
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(t("result.actions.share", "en"), className="text", id="share-action-text"),
                                        html.Img(
                                            src="../../assets/icons/share.svg",
                                            id="share_result",
                                            className="icon",
                                        ),
                                    ],
                                    className="button download",
                                    id="share-result-btn",
                                ),
                                html.Div(
                                    [
                                        html.Span(t("result.actions.download-sequences", "en"), className="text", id="download-sequences-text"),
                                        html.Img(
                                            src="../../assets/icons/download.svg",
                                            className="icon",
                                        ),
                                    ],
                                    className="button download",
                                    id="download-button-aligned",
                                ),
                                html.Div(
                                    [
                                        html.Span(t("result.actions.download-alignment-json", "en"), className="text", id="download-alignment-json-text"),
                                        html.Img(
                                            src="../../assets/icons/download.svg",
                                            className="icon",
                                        ),
                                    ],
                                    className="button download",
                                    id="download-button-alignment-json",
                                ),
                            ],
                            className="result-actions",
                            id="result-actions-row",
                        ),
                    ],
                    id="result-actions",
                ),
                # All result content — hidden on error
                html.Div(
                    [
                        # Results section card
                        html.Div(
                            [
                                html.Div(id="results-table-title"),
                                html.Div(
                                    [
                                        html.Div(id="main-results-table-container"),
                                        html.Div(id="statistical-results-table-container"),
                                        html.Div(id="output-results-graph", className="graph"),
                                    ],
                                    id="results-row",
                                    className="results-row",
                                ),
                            ],
                            className="page-card result-section-card",
                        ),
                        dcc.Download(id="download-link-results"),
                        # Climatic trees section card
                        html.Div(
                            [
                                html.Div(id="climatic-tree-title"),
                                html.Div(
                                    [html.Div(id="climatic-tree")],
                                    className="tree",
                                    id="climatic-tree-container",
                                ),
                            ],
                            className="page-card result-section-card",
                        ),
                        # Genetic trees section card
                        html.Div(
                            [
                                html.Div(id="genetic-tree-title"),
                                html.Div(
                                    [html.Div(id="genetic-tree")],
                                    className="tree",
                                    id="genetic-tree-container",
                                ),
                            ],
                            className="page-card result-section-card",
                            id="genetic-section-card",
                        ),
                        # Email section card
                        html.Div(
                            create_email_section(),
                            id="email-section-card-content",
                            className="page-card result-section-card-bottom",
                        ),
                    ],
                    id="result-content-sections",
                ),
            ],
            className="page-container result-page",
        ),
        html.Div(
            id="email-status-message",
            style={"textAlign": "center", "marginTop": "20px"},
        ),
    ],
    className="resultContainer",
    id="all-results",
)


# Callback to check result status and refresh when complete
@callback(
    Output("result-processing-status", "data"),
    Output("result-status-interval", "disabled"),
    Output("results-name", "children", allow_duplicate=True),
    Output("processing-status-container", "children", allow_duplicate=True),
    Output("processing-status-container", "style", allow_duplicate=True),
    Output("toast-store", "data", allow_duplicate=True),
    Output("refresh-trigger", "data"),
    Output("error-banner", "className", allow_duplicate=True),
    Output("result-content-sections", "style", allow_duplicate=True),
    Output("result-actions", "style", allow_duplicate=True),
    Input("result-status-interval", "n_intervals"),
    State("url", "pathname"),
    State("result-processing-status", "data"),
    State("refresh-trigger", "data"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def check_result_status(n_intervals, path, prev_status, current_refresh, language):
    """
    Check if a processing result has completed and refresh the page.
    """
    lang = language if language in LANGUAGE_LIST else "en"
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate

    result = utils.get_result(result_id)
    status = result.get("status", "pending")
    title = result["name"]

    status_key_map = {
        "pending": "results.card.status.in-progress",
        "queued": "results.card.status.in-progress",
        "running": "results.card.status.in-progress",
        "climatic_trees": "results.card.status.climatic-trees",
        "alignment": "results.card.status.alignment",
        "genetic_trees": "results.card.status.genetic-trees",
        "output": "results.card.status.output",
    }

    if status.lower() == "complete":
        title_str = t("result.title-of", lang).replace("{name}", title)
        if prev_status and prev_status.lower() != "complete":
            new_refresh = (current_refresh or 0) + 1
            return status, True, title_str, [], {"display": "none"}, {"message": t("result.results-ready", lang), "type": "success"}, new_refresh, "error-banner hidden", {}, {}
        return status, True, title_str, [], {"display": "none"}, dash.no_update, dash.no_update, "error-banner hidden", {}, {}
    elif status.lower() == "error":
        title_str = t("result.title-of-error", lang).replace("{name}", title)
        return status, True, title_str, [], {"display": "none"}, dash.no_update, dash.no_update, "error-banner", {"display": "none"}, {"display": "none"}
    else:
        status_key = status_key_map.get(status.lower(), "results.card.status.in-progress")
        status_label = t(status_key, lang)
        spinner_content = [
            html.Div(className="loading-spinner"),
            html.Span(t("result.in-progress", lang).replace("{status}", status_label), className="processing-text"),
        ]
        title_str = t("result.title-of", lang).replace("{name}", title)
        return status, False, title_str, spinner_content, {"display": "flex"}, dash.no_update, dash.no_update, "error-banner hidden", {}, {}


@callback(
    Output("toast-store", "data", allow_duplicate=True),
    Input("share-result-btn", "n_clicks"),
    State("url", "pathname"),
    State("url", "href"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def share_result_link(n_clicks, pathname, href, language):
    """
    Copy the result link to clipboard and show a toast notification.
    """
    lang = language if language in LANGUAGE_LIST else "en"
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    _, result = _load_result_from_path(pathname)
    if result is None:
        return _missing_result_toast(lang)
    return {"message": t("result.toast.link-copied", lang), "type": "success", "clipboard": href}


@callback(
    Output("toast-store", "data", allow_duplicate=True),
    State("url", "pathname"),
    Input(get_button_id("user-input"), "n_clicks"),
    State("user-input", "value"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def handle_submit_click(pathname, n_clicks, user_email, language):
    lang = language if language in LANGUAGE_LIST else "en"
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    _, result = _load_result_from_path(pathname)
    if result is None:
        return _missing_result_toast(lang)
    if not validate_email(user_email):
        return {"message": t("result.email.invalid", lang), "type": "error"}
    success = mail.send_results_ready_email(user_email, pathname, lang)
    msg = t("result.email.sent", lang) if success else t("result.email.error", lang)
    return {"message": msg, "type": "success" if success else "error"}


@callback(
    Output("results-name", "children"),
    Output("processing-status-container", "children"),
    Output("processing-status-container", "style"),
    Output("error-banner", "className"),
    Output("result-content-sections", "style"),
    Output("result-actions", "style"),
    Input("url", "pathname"),
    Input("result-alive-check", "n_intervals"),
    Input("language-store", "data"),
)
def show_result_name(path, _alive_tick, language):
    lang = language if language in LANGUAGE_LIST else "en"
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    result = utils.get_result(result_id)
    if result is None:
        return t("result.errors.not-found-title", lang), [], {"display": "none"}, "error-banner hidden", {}, {}
    title = result["name"]
    status = result.get("status", "pending")

    status_key_map = {
        "pending": "results.card.status.in-progress",
        "queued": "results.card.status.in-progress",
        "running": "results.card.status.in-progress",
        "climatic_trees": "results.card.status.climatic-trees",
        "alignment": "results.card.status.alignment",
        "genetic_trees": "results.card.status.genetic-trees",
        "output": "results.card.status.output",
    }

    if status.lower() == "complete":
        return t("result.title-of", lang).replace("{name}", title), [], {"display": "none"}, "error-banner hidden", {}, {}
    elif status.lower() == "error":
        return t("result.title-of-error", lang).replace("{name}", title), [], {"display": "none"}, "error-banner", {"display": "none"}, {"display": "none"}
    else:
        status_key = status_key_map.get(status.lower(), "results.card.status.in-progress")
        status_label = t(status_key, lang)
        spinner_content = [
            html.Div(className="loading-spinner"),
            html.Span(t("result.in-progress", lang).replace("{status}", status_label), className="processing-text"),
        ]
        return t("result.title-of", lang).replace("{name}", title), spinner_content, {"display": "flex"}, "error-banner hidden", {}, {}


@callback(
    Output("unavailable-result-message", "children"),
    Output("unavailable-result-message", "className"),
    Output("result-content-sections", "style", allow_duplicate=True),
    Input("url", "pathname"),
    Input("result-alive-check", "n_intervals"),
    Input("language-store", "data"),
    prevent_initial_call=True,
)
def toggle_unavailable_result_view(path, _alive_tick, language):
    lang = language if language in LANGUAGE_LIST else "en"
    _, result = _load_result_from_path(path)

    if result is None:
        message = html.Div(
            [
                html.P(
                    t("result.errors.not-found-message", lang),
                    className="email-description unavailable-result-description",
                ),
                dcc.Link(
                    t("result.errors.back-to-results", lang),
                    href="/results",
                    className="button download unavailable-result-link",
                ),
            ],
            className="page-card result-section-card unavailable-result-card",
        )
        hidden = {"display": "none"}
        return message, "", hidden

    shown = {}
    return "", "hidden", shown


@callback(
    Output("share-action-text", "children"),
    Output("download-sequences-text", "children"),
    Output("download-alignment-json-text", "children"),
    Output("email-section-card-content", "children"),
    Output("error-banner-title", "children"),
    Output("error-banner-description", "children"),
    Output("error-banner-back", "children"),
    Input("language-store", "data"),
)
def update_result_static_text(language):
    lang = language if language in LANGUAGE_LIST else "en"
    return (
        t("result.actions.share", lang),
        t("result.actions.download-sequences", lang),
        t("result.actions.download-alignment-json", lang),
        create_email_section(lang),
        t("result.error.title", lang),
        t("result.error.description", lang),
        t("result.error.back", lang),
    )


@callback(
    Output("results-table-title", "children"),
    Output("main-results-table-container", "children"),
    Output("statistical-results-table-container", "children"),
    Output("output-results-graph", "children"),
    State("url", "pathname"),
    Input("all-results", "children"),
    Input("refresh-trigger", "data"),
    Input("language-store", "data"),
)
def show_complete_results(path, generated_page, refresh_trigger, language):
    """

      This function creates the header (title & download button) of the results,
    the results table, and the results graph.

    Args:
        path (str): The path of the page.
        generated_page: (Not used in this function, but required for the callback trigger)
        refresh_trigger: Trigger to force refresh when processing completes

    Returns:
        html.Div: The div containing the header of the results table.
        html.Div: The div containing the results table.
        Union[dcc.Graph, None]: The results graph if data is available and valid, else None.
    """
    lang = language if language in LANGUAGE_LIST else "en"
    _, result = _load_result_from_path(path)
    if result is None:
        return "", "", "", ""

    if "genetic" not in result["result_type"] or "output" not in result:
        return "", "", "", ""

    results_data = str_csv_to_df(result["output"])

    # Check if results_data is a valid DataFrame and has required columns
    if not isinstance(results_data, pd.DataFrame) or not all(
        col in results_data.columns for col in ["Position in ASM", "Bootstrap mean"]
    ):
        return (
            create_result_table_header(lang),  # Still return the header
            create_titled_result_table(
                results_data,
                "",
                "datatable-main-results",
                lang,
            ),
            "",  # No statistical table to display
            "",  # No graph to display
        )

    # Split exported output into main results and optional statistical test block
    core_cols = ["Position in ASM", "Bootstrap mean"]
    results_data[core_cols] = results_data[core_cols].replace(r'^\s*$', np.nan, regex=True)
    normal_results_data, statistical_results_data = split_output_tables(results_data)
    graphic_data = normal_results_data.dropna(subset=core_cols)

    # Now it's safe to call create_result_graphic
    graph_output = create_result_graphic(graphic_data, lang) if len(graphic_data) > 0 else None

    main_results_table = create_titled_result_table(
        normal_results_data,
        "",
        "datatable-main-results",
        lang,
    )

    statistical_results_table = ""
    if isinstance(statistical_results_data, pd.DataFrame) and not statistical_results_data.empty:
        statistical_results_table = create_titled_result_table(
            statistical_results_data,
            t("result.table.statistical-tests-title", lang),
            "datatable-statistical-tests",
            lang,
        )

    return (
        create_result_table_header(lang),
        main_results_table,
        statistical_results_table,
        graph_output,
    )


@callback(
    Output("climatic-tree-title", "children"),
    Output("climatic-tree", "children"),
    State("url", "pathname"),
    Input("output-results-graph", "children"),
    Input("theme-store", "data"),
    Input("refresh-trigger", "data"),
    Input("language-store", "data"),
)
def create_climatic_trees(path, generated_results_header, is_dark_theme, refresh_trigger, language):
    lang = language if language in LANGUAGE_LIST else "en"
    """
    This function creates the list of divs containing the climatic trees


    args:
        path (str): the path of the page
        generated_results_header: used to wait for the results header to be created before showing climatic trees
        is_dark_theme: True if dark theme, False if light theme
    returns:
        htmml.Div: the div containing the header (title & download button) of the climatic trees
        html.Div: the div containing the climatic trees
    """
    result_id, result = _load_result_from_path(path)
    if result is None:
        return "", ""
    add_to_cookie(result_id)
    if "climatic" not in result["result_type"]:
        return "", ""

    climatic_trees = result["climatic_trees"]
    tree_names = list(climatic_trees.keys())
    climatic_elements = []
    for tree in climatic_trees.values():
        tree = Phylo.read(StringIO(tree), "newick")
        nodes, edges = generate_elements(tree)
        climatic_elements.append(nodes + edges)

    return create_climatic_trees_header(lang), html.Div(
        children=[
            generate_tree(elem, name, is_dark_theme)
            for elem, name in zip(climatic_elements, tree_names)
        ],
        className="tree-sub-container",
    )


# Callback for static download buttons (aligned and complete) - these always exist in layout
@callback(
    Output("download-link-results", "data"),
    Output("toast-store", "data", allow_duplicate=True),
    State("url", "pathname"),
    Input("download-button-aligned", "n_clicks"),
    Input("download-btn-complete", "n_clicks"),
    Input("download-btn-genetic", "n_clicks"),
    Input("download-btn-climatic", "n_clicks"),
    Input("download-button-alignment-json", "n_clicks"),
    Input("download-btn-genetic-json", "n_clicks"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def download_results(
    path,
    btn_aligned,
    btn_complete,
    btn_genetic,
    btn_climatic,
    btn_alignment_json,
    btn_genetic_trees_json,
    language,
):
    lang = language if language in LANGUAGE_LIST else "en"
    """
    This function handles all download buttons.
    The genetic and climatic buttons are hidden placeholders that get clicked via JS.

    args:
        path (str): the path of the page
        btn_aligned : aligned sequences download button
        btn_complete : complete results download button
        btn_genetic : genetic trees download button (hidden placeholder)
        btn_climatic : climatic trees download button (hidden placeholder)
    """

    _, result = _load_result_from_path(path)
    if result is None:
        return dash.no_update, _missing_result_toast(lang)

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "download-btn-genetic" and btn_genetic:
        if "genetic_trees" not in result:
            raise dash.exceptions.PreventUpdate
        result_genetic_trees = result["genetic_trees"]
        data_genetic = "".join(list(result_genetic_trees.values()))
        return dict(
            content=data_genetic, filename=result["name"] + "_genetic_trees.newick"
        ), {"message": t("result.toast.genetic-downloaded", lang), "type": "success"}
    if trigger_id == "download-btn-climatic" and btn_climatic:
        if "climatic_trees" not in result:
            raise dash.exceptions.PreventUpdate
        result_climatic_trees = result["climatic_trees"]
        data_climatic = "".join(list(result_climatic_trees.values()))
        return dict(
            content=data_climatic, filename=result["name"] + "_climatic_trees.newick"
        ), {"message": t("result.toast.climatic-downloaded", lang), "type": "success"}
    if trigger_id == "download-button-aligned" and btn_aligned:
        if "msaSet" not in result:
            raise dash.exceptions.PreventUpdate
        result_msa = result["msaSet"]
        data_msa = json.dumps(result_msa)
        return dict(
            content=data_msa, filename=result["name"] + "_msa.json"
        ), {"message": t("result.toast.sequences-downloaded", lang), "type": "success"}
    if trigger_id == "download-button-alignment-json" and btn_alignment_json:
        if "msaSet" not in result:
            raise dash.exceptions.PreventUpdate
        # Convert stored [{fasta_per_seq}] format back to Alignment JSON so the
        # file can be re-uploaded as pre-aligned data.
        msa_windows = {}
        for window, seqs in result["msaSet"].items():
            if isinstance(seqs, list):
                msa_windows[window] = "".join(seqs)
            else:
                msa_windows[window] = str(seqs)
        alignment_json = json.dumps({
            "type": "Alignment",
            "alignment_method": "0",
            "msa": msa_windows,
        })
        return dict(
            content=alignment_json,
            filename=result["name"] + "_alignment.json",
        ), {"message": t("result.toast.alignment-json-downloaded", lang), "type": "success"}
    if trigger_id == "download-btn-genetic-json" and btn_genetic_trees_json:
        if "genetic_trees" not in result:
            raise dash.exceptions.PreventUpdate
        data_trees = json.dumps(result["genetic_trees"])
        return dict(
            content=data_trees,
            filename=result["name"] + "_genetic_trees.json",
        ), {"message": t("result.toast.genetic-trees-json-downloaded", lang), "type": "success"}
    if trigger_id == "download-btn-complete" and btn_complete:
        if "output" not in result:
            raise dash.exceptions.PreventUpdate
        data_results = str_csv_to_df(result["output"])
        return dict(
            content=data_results.to_csv(header=True, index=False),
            filename=result["name"] + "_results.csv",
        ), {"message": t("result.toast.output-downloaded", lang), "type": "success"}

    raise dash.exceptions.PreventUpdate


@callback(
    Output("genetic-tree-title", "children"),
    Output("genetic-tree", "children"),
    State("url", "pathname"),
    Input("output-results-graph", "children"),
    Input("theme-store", "data"),
    Input("refresh-trigger", "data"),
    Input("language-store", "data"),
)
def create_genetic_trees(path, generated_results_header, is_dark_theme, refresh_trigger, language):
    lang = language if language in LANGUAGE_LIST else "en"
    """
    This function creates the list of divs containing the genetic trees
    args:
        path (str): the path of the page
        generated_results_header: used to wait for the results header to be created before showing genetic trees
        is_dark_theme: True if dark theme, False if light theme
    returns:
        htmml.Div: the div containing the header (title & download button) of the genetic trees
        html.Div: the div containing the genetic trees
    """
    _, result = _load_result_from_path(path)
    if result is None:
        return "", ""
    if "genetic" not in result["result_type"] or "genetic_trees" not in result:
        return "", ""

    genetic_trees = result["genetic_trees"]
    tree_names = list(genetic_trees.keys())

    genetic_elements = []
    for tree in genetic_trees.values():
        tree = Phylo.read(StringIO(tree), "newick")
        nodes, edges = generate_elements(tree)
        genetic_elements.append(nodes + edges)

    return create_genetic_trees_header(lang), html.Div(
        children=[
            generate_tree(elem, name, is_dark_theme)
            for elem, name in zip(genetic_elements, tree_names)
        ],
        className="tree-sub-container",
    )


def add_to_cookie(result_id):
    """
    This function takes the result id and adds it to the cookie
    args:
        result_id (str): the id of the result to add to the cookie
    """

    auth_cookie = request.cookies.get("AUTH")
    response = dash.callback_context.response
    utils.make_cookie(result_id, auth_cookie, response)


def create_result_table_header(lang="en"):
    """
    Creates the collapsible section header for the results table.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div(t("result.sections.results", lang), className="result-section-title"),
                    html.Img(
                        src="../../assets/icons/angle-down.svg",
                        id="results-table-collapse-button",
                        className="icon collapse-icon",
                    ),
                ],
                className="result-section-header",
            ),
            html.Div(
                [
                    html.Span(t("result.actions.download-output", lang), className="text"),
                    html.Img(src="../../assets/icons/download.svg", className="icon"),
                ],
                className="button download download-complete-trigger",
            ),
        ],
        className="result-section-header result-section-header--with-action",
    )


def create_titled_result_table(data, title, table_id, lang="en"):
    return html.Div(
        [
            *([] if not title else [html.Div(title, className="results-table-title")]),
            html.Div(
                [
                    dash_table.DataTable(
                        id=table_id,
                        data=data.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in data.columns],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        page_current=0,
                        page_size=15,
                        filter_query="",
                        filter_options={"placeholder_text": t("result.table.filter-placeholder", lang)},
                        row_selectable="multi",
                        **utils.get_table_styles(),
                    ),
                ],
                className="shared-table",
            ),
        ]
    )


def split_output_tables(results_data):
    expected_order = ["Mantel_r", "Mantel_p", "Procrustes_M2", "PROTEST_p"]

    if not isinstance(results_data, pd.DataFrame):
        return pd.DataFrame(), pd.DataFrame(columns=expected_order)

    if results_data.empty:
        return results_data, pd.DataFrame(columns=expected_order)

    df = results_data.reset_index(drop=True).copy()

    def normalize_token(token):
        return re.sub(r"[^a-z0-9]", "", str(token).lower())

    normalized_expected = {normalize_token(col): col for col in expected_order}

    def build_stats_df_from_rows(header_row, value_row):
        stats_record = {}
        for index, header in enumerate(header_row.tolist()):
            header_text = str(header).strip()
            if not header_text:
                continue
            normalized_header = normalize_token(header_text)
            if normalized_header not in normalized_expected:
                continue
            canonical_name = normalized_expected[normalized_header]
            value = value_row.iloc[index] if index < len(value_row) else ""
            stats_record[canonical_name] = value

        if not stats_record:
            return pd.DataFrame(columns=expected_order)

        ordered_record = {
            col: stats_record[col] for col in expected_order if col in stats_record
        }
        return pd.DataFrame([ordered_record])

    clean_df = df.fillna("").astype(str).apply(lambda col: col.str.strip())
    normalized_df = clean_df.apply(
        lambda col: col.str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    )

    empty_row_mask = clean_df.eq("").all(axis=1)
    header_row_mask = normalized_df.isin(set(normalized_expected.keys())).any(axis=1)

    separator_candidate_mask = empty_row_mask & header_row_mask.shift(-1, fill_value=False)
    candidate_indices = np.flatnonzero(separator_candidate_mask.to_numpy())
    valid_candidate_indices = candidate_indices[candidate_indices + 2 < len(df)]

    if len(valid_candidate_indices) > 0:
        separator_idx = int(valid_candidate_indices[0])
        header_row = df.iloc[separator_idx + 1]
        value_row = df.iloc[separator_idx + 2]
        main_results_data = df.iloc[:separator_idx].copy()
        statistical_results_data = build_stats_df_from_rows(header_row, value_row)
        return main_results_data, statistical_results_data

    return df, pd.DataFrame(columns=expected_order)


def create_result_graphic(results_data, lang="en"):
    """
    This function creates the results graphic
    args:
        data (pandas.DataFrame): the data to display in the table
    returns:
        dash_table.DataTable: the table containing the results
    """
    # regex pattern to find the distance method column
    pattern = re.compile(r".*[dD]istance")
    results_data["starting_position"] = [
        int(x.split("_")[0]) for x in results_data["Position in ASM"]
    ]

    # Get the name of the columns that containts Distance method information
    results_column_headers = list(results_data.columns.values)
    distance_method = list(filter(lambda x: pattern.match(x), results_column_headers))[
        0
    ]

    results_data = results_data[
        ["starting_position", "Bootstrap mean", distance_method]
    ]
    results_data = results_data.groupby("starting_position").mean().reset_index()

    if len(results_data) > 0:  # Verify that the data exists
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=results_data["starting_position"],
                y=results_data["Bootstrap mean"],
                name=t("result.graph.bootstrap-mean", lang),
                line=dict(color="#AD00FA"),
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=results_data["starting_position"],
                y=results_data[distance_method],
                name=distance_method,
                line=dict(color="#00faad"),
            ),
            secondary_y=True,
        )
        fig.update_layout(
            title_text=t("result.graph.title-bootstrap-distance", lang).replace("{distance_method}", distance_method),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
        )
        fig.update_xaxes(
            title_text=t("result.graph.x-axis-position", lang), gridcolor="rgba(255,255,255,0.2)"
        )
        fig.update_yaxes(
            title_text=t("result.graph.y-axis-bootstrap", lang),
            secondary_y=False,
            gridcolor="rgba(255,255,255,0.2)",
        )
        fig.update_yaxes(
            title_text=str("<b>" + distance_method + "</b>"),
            secondary_y=True,
            gridcolor="rgba(255,255,255,0.2)",
        )

        min_bootstrap = results_data["Bootstrap mean"].min()
        max_bootstrap = results_data["Bootstrap mean"].max()
        bootstrap_ticks = np.linspace(min_bootstrap, max_bootstrap, 6)

        min_ls = results_data[distance_method].min()
        max_ls = results_data[distance_method].max()
        ls_ticks = np.linspace(min_ls, max_ls, 6)

        fig.update_layout(yaxis1_tickvals=bootstrap_ticks, yaxis2_tickvals=ls_ticks)


def create_climatic_trees_header(lang="en"):
    """
    Creates the collapsible section header for the climatic trees.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div(t("result.sections.climatic-trees", lang), className="result-section-title"),
                    html.Img(
                        src="../../assets/icons/angle-down.svg",
                        id="results-climatic-collapse-button",
                        className="icon collapse-icon",
                    ),
                ],
                className="result-section-header",
            ),
            html.Div(
                [
                    html.Span(t("result.actions.download-climatic-trees", lang), className="text"),
                    html.Img(
                        src="../../assets/icons/download.svg", className="icon"
                    ),
                ],
                className="button download download-climatic-trigger",
            ),
        ],
        className="result-section-header result-section-header--with-action",
    )


def create_genetic_trees_header(lang="en"):
    """
    Creates the collapsible section header for the genetic trees.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div(t("result.sections.genetic-trees", lang), className="result-section-title"),
                    html.Img(
                        src="../../assets/icons/angle-down.svg",
                        id="results-genetic-collapse-button",
                        className="icon collapse-icon",
                    ),
                ],
                className="result-section-header",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(t("result.actions.download-genetic-trees", lang), className="text"),
                            html.Img(src="../../assets/icons/download.svg", className="icon"),
                        ],
                        className="button download download-genetic-trigger",
                    ),
                    html.Div(
                        [
                            html.Span(t("result.actions.download-genetic-trees-json", lang), className="text"),
                            html.Img(src="../../assets/icons/download.svg", className="icon"),
                        ],
                        className="button download download-genetic-json-trigger",
                    ),
                ],
                className="genetic-header-actions",
            ),
        ],
        className="result-section-header result-section-header--with-action",
    )


# the following code is taken from https://dash.plotly.com/cytoscape/biopython
def generate_tree(elem, name, is_dark_theme=True):
    # Create a unique ID for the cytoscape element
    cyto_id = f"cyto-{name.replace(' ', '-').replace('_', '-')}"
    return html.Div(
        [
            html.H3(name, className="treeTitle"),
            html.Div(
                [
                    cyto.Cytoscape(
                        id=cyto_id,
                        elements=elem,
                        stylesheet=get_cytoscape_stylesheet(is_dark_theme),
                        layout={"name": "preset", "fit": True, "padding": 20},
                        style={"height": "400px", "width": "100%", "cursor": "grab"},
                        userZoomingEnabled=False,
                        userPanningEnabled=True,
                        minZoom=0.2,
                        maxZoom=3,
                    ),
                    html.Div(
                        [
                            html.Button(
                                "+",
                                className="tree-zoom-btn tree-zoom-in",
                                **{"data-cyto-id": cyto_id},
                            ),
                            html.Button(
                                "−",
                                className="tree-zoom-btn tree-zoom-out",
                                **{"data-cyto-id": cyto_id},
                            ),
                            html.Button(
                                "⟲",
                                className="tree-zoom-btn tree-zoom-reset",
                                **{"data-cyto-id": cyto_id},
                            ),
                        ],
                        className="tree-zoom-controls",
                    ),
                ],
                className="tree-cytoscape-wrapper",
            ),
        ],
        id=name,
        className="tree-container",
    )


def generate_elements(tree, xlen=30, ylen=30, grabbable=False):
    def get_col_positions(tree, column_width=25):
        taxa = tree.get_terminals()

        # Some constants for the drawing calculations
        max_label_width = max(len(str(taxon)) for taxon in taxa)
        drawing_width = column_width - max_label_width - 1

        depths = tree.depths()
        # If there are no branch lengths, assume unit branch lengths
        if not max(depths.values()):
            depths = tree.depths(unit_branch_lengths=True)
            # Potential drawing overflow due to rounding, 1 char per tree layer
        fudge_margin = int(math.ceil(math.log(len(taxa), 2)))
        cols_per_branch_unit = (drawing_width - fudge_margin) / float(
            max(depths.values())
        )
        return dict(
            (clade, int(blen * cols_per_branch_unit + 1.0))
            for clade, blen in depths.items()
        )

    def get_row_positions(tree):
        taxa = tree.get_terminals()
        positions = dict((taxon, 2 * idx) for idx, taxon in enumerate(taxa))

        def calc_row(clade):
            for subclade in clade:
                if subclade not in positions:
                    calc_row(subclade)
            positions[clade] = (
                positions[clade.clades[0]] + positions[clade.clades[-1]]
            ) // 2

        calc_row(tree.root)
        return positions

    def add_to_elements(clade, clade_id):
        children = clade.clades

        pos_x = col_positions[clade] * xlen
        pos_y = row_positions[clade] * ylen

        cy_source = {
            "data": {"id": clade_id},
            "position": {"x": pos_x, "y": pos_y},
            "classes": "nonterminal",
        }
        nodes.append(cy_source)

        if clade.is_terminal():
            cy_source["data"]["name"] = clade.name
            cy_source["classes"] = "terminal"

        for n, child in enumerate(children):
            # The "support" node is on the same column as the parent clade,
            # and on the same row as the child clade. It is used to create the
            # 90 degree angle between the parent and the children.
            # Edge config: parent -> support -> child

            support_id = clade_id + "s" + str(n)
            child_id = clade_id + "c" + str(n)
            pos_y_child = row_positions[child] * ylen

            cy_support_node = {
                "data": {"id": support_id},
                "position": {"x": pos_x, "y": pos_y_child},
                "classes": "support",
            }

            cy_support_edge = {
                "data": {
                    "source": clade_id,
                    "target": support_id,
                    "sourceCladeId": clade_id,
                },
            }

            cy_edge = {
                "data": {
                    "source": support_id,
                    "target": child_id,
                    "length": clade.branch_length,
                    "sourceCladeId": clade_id,
                },
            }

            if clade.confidence:
                cy_source["data"]["confidence"] = clade.confidence

            nodes.append(cy_support_node)
            edges.extend([cy_support_edge, cy_edge])

            add_to_elements(child, child_id)

    col_positions = get_col_positions(tree)
    row_positions = get_row_positions(tree)

    nodes = []
    edges = []

    add_to_elements(tree.clade, "r")

    return nodes, edges


clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="collapse_result_section_function"
    ),
    Output("dummy-climatic-collapse", "children"),  # needed for the callback to trigger
    [
        Input("results-climatic-collapse-button", "n_clicks"),
        Input("climatic-tree-container", "id"),
        Input("results-climatic-collapse-button", "id"),
    ],
    prevent_initial_call=True,
)


clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="collapse_result_section_function"
    ),
    Output("dummy-table-collapse", "children"),  # needed for the callback to trigger
    [
        Input("results-table-collapse-button", "n_clicks"),
        Input("results-row", "id"),
        Input("results-table-collapse-button", "id"),
    ],
    prevent_initial_call=True,
)


clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="collapse_result_section_function"
    ),
    Output("dummy-genetic-collapse", "children"),  # needed for the callback to trigger
    [
        Input("results-genetic-collapse-button", "n_clicks"),
        Input("genetic-tree-container", "id"),
        Input("results-genetic-collapse-button", "id"),
    ],
    prevent_initial_call=True,
)


clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="collapse_result_section_function"
    ),
    Output("dummy-email-collapse", "children"),  # needed for the callback to trigger
    [
        Input("results-email-collapse-button", "n_clicks"),
        Input("email-section-container", "id"),
        Input("results-email-collapse-button", "id"),
    ],
    prevent_initial_call=True,
)


def get_cytoscape_stylesheet(is_dark_theme=True):
    """
    Returns the Cytoscape stylesheet with the appropriate text color based on theme.
    Args:
        is_dark_theme: True for dark theme (white text), False for light theme (dark text)
    """
    text_color = "#FFFFFF" if is_dark_theme else "#1A1C1E"
    line_color = "#9F74D0" if is_dark_theme else "#B593DD"
    node_color = "#1FA391" if is_dark_theme else "#2DD4BF"
    return [
        {
            "selector": ".nonterminal",
            "style": {
                "label": "",
                "background-opacity": 0,
                "text-opacity": 0,
            },
        },
        {"selector": ".support", "style": {"background-opacity": 0, "text-opacity": 0}},
        {
            "selector": "edge",
            "style": {
                "line-color": line_color,
                "source-endpoint": "inside-to-node",
                "target-endpoint": "inside-to-node",
            },
        },
        {
            "selector": ".terminal",
            "style": {
                "label": "data(name)",
                "font-weight": "bold",
                "color": text_color,
                "width": 10,
                "height": 10,
                "text-valign": "center",
                "text-halign": "right",
                "background-color": node_color,
            },
        },
    ]


# Default stylesheet (dark theme)
stylesheet = get_cytoscape_stylesheet(True)
