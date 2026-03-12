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
from db.controllers.files import str_csv_to_df
from flask import request
from plotly.subplots import make_subplots

dash.register_page(__name__, path_template="/result/<result_id>")


def create_email_section():
    """
    Creates the email share section content (header + input).
    """
    return [
        html.Div(
            [
                html.Div("Share result", className="result-section-title"),
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
                    "if you would like to receive the url of these data by email, you can enter your address mail below.",
                    className="email-description",
                ),
                create_email_input(
                    input_id="user-input",
                    placeholder="Enter your address mail here",
                ),
            ],
            id="email-section-container",
        ),
    ]


layout = html.Div(
    [
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
        html.Div(id="dummy-share-result-output", style={"display": "none"}),
        html.Div(id="dummy-table-collapse", style={"display": "none"}),
        html.Div(id="dummy-climatic-collapse", style={"display": "none"}),
        html.Div(id="dummy-genetic-collapse", style={"display": "none"}),
        html.Div(id="dummy-email-collapse", style={"display": "none"}),
        html.Div(
            [
                html.H1(id="results-name", className="title"),
                # Processing status with spinner (shown when not complete)
                html.Div(
                    id="processing-status-container",
                    className="processing-status-container",
                    style={"display": "none"},
                ),
                # Top action buttons row
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("share", className="text"),
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
                                html.Span("download output.csv", className="text"),
                                html.Img(
                                    src="../../assets/icons/download.svg",
                                    className="icon",
                                ),
                            ],
                            className="button download",
                            id="download-button-complete",
                        ),
                        html.Div(
                            [
                                html.Span("download genetic sequences", className="text"),
                                html.Img(
                                    src="../../assets/icons/download.svg",
                                    className="icon",
                                ),
                            ],
                            className="button download",
                            id="download-button-aligned",
                        ),
                    ],
                    className="result-actions",
                ),
                # Results section card
                html.Div(
                    [
                        html.Div(id="results-table-title"),
                        html.Div(
                            [
                                html.Div(id="output-results"),
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
                ),
                # Email section card
                html.Div(
                    create_email_section(),
                    className="page-card result-section-card-bottom",
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
    Input("result-status-interval", "n_intervals"),
    State("url", "pathname"),
    State("result-processing-status", "data"),
    State("refresh-trigger", "data"),
    prevent_initial_call=True,
)
def check_result_status(n_intervals, path, prev_status, current_refresh):
    """
    Check if a processing result has completed and refresh the page.
    """
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate

    result = utils.get_result(result_id)
    status = result.get("status", "pending")
    title = result["name"]

    # Status labels mapping
    status_labels = {
        "pending": "Queued",
        "queued": "Queued",
        "running": "Processing",
        "climatic_trees": "Building climatic trees",
        "alignment": "Aligning sequences",
        "genetic_trees": "Building genetic trees",
        "output": "Generating output",
        # Uppercase variants
        "PENDING": "Queued",
        "QUEUED": "Queued",
        "RUNNING": "Processing",
        "CLIMATIC_TREES": "Building climatic trees",
        "ALIGNMENT": "Aligning sequences",
        "GENETIC_TREES": "Building genetic trees",
        "OUTPUT": "Generating output",
    }

    # If already complete or error, disable the interval and hide spinner
    if status.lower() == "complete":
        if prev_status and prev_status.lower() != "complete":
            # Just became complete - show toast and trigger refresh
            new_refresh = (current_refresh or 0) + 1
            return status, True, f"Result of {title}", [], {"display": "none"}, {"message": "Results are ready!", "type": "success"}, new_refresh
        return status, True, f"Result of {title}", [], {"display": "none"}, dash.no_update, dash.no_update
    elif status.lower() == "error":
        return status, True, f"Result of {title} (Error)", [], {"display": "none"}, dash.no_update, dash.no_update
    else:
        # Still processing - show spinner with status
        status_label = status_labels.get(status, status.replace("_", " ").title())
        spinner_content = [
            html.Div(className="loading-spinner"),
            html.Span(f"In progress – {status_label}...", className="processing-text"),
        ]
        return status, False, f"Result of {title}", spinner_content, {"display": "flex"}, dash.no_update, dash.no_update


@callback(
    Output("toast-store", "data", allow_duplicate=True),
    Input("share-result-btn", "n_clicks"),
    State("url", "href"),
    prevent_initial_call=True,
)
def share_result_link(n_clicks, href):
    """
    Copy the result link to clipboard and show a toast notification.
    """
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    return {"message": "Link copied to your clipboard!", "type": "success", "clipboard": href}


@callback(
    Output("toast-store", "data", allow_duplicate=True),
    State("url", "pathname"),
    Input(get_button_id("user-input"), "n_clicks"),
    State("user-input", "value"),
    prevent_initial_call=True,
)
def handle_submit_click(pathname, n_clicks, user_email):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    if not validate_email(user_email):
        return {"message": "Invalid email address", "type": "error"}
    success = mail.send_results_ready_email(user_email, pathname)
    msg = "Email sent successfully!" if success else "Error sending email"
    return {"message": msg, "type": "success" if success else "error"}


@callback(
    Output("results-name", "children"),
    Output("processing-status-container", "children"),
    Output("processing-status-container", "style"),
    Input("url", "pathname"),
)
def show_result_name(path):
    """
    args:
        path (str): the path of the page
    returns:
        tuple: the title, spinner content, and spinner style
    """
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    result = utils.get_result(result_id)
    title = result["name"]
    status = result.get("status", "pending")

    # Status labels mapping
    status_labels = {
        "pending": "Queued",
        "queued": "Queued",
        "running": "Processing",
        "climatic_trees": "Building climatic trees",
        "alignment": "Aligning sequences",
        "genetic_trees": "Building genetic trees",
        "output": "Generating output",
        # Uppercase variants
        "PENDING": "Queued",
        "QUEUED": "Queued",
        "RUNNING": "Processing",
        "CLIMATIC_TREES": "Building climatic trees",
        "ALIGNMENT": "Aligning sequences",
        "GENETIC_TREES": "Building genetic trees",
        "OUTPUT": "Generating output",
    }

    # Show processing status if not complete
    if status.lower() == "complete":
        return f"Result of {title}", [], {"display": "none"}
    elif status.lower() == "error":
        return f"Result of {title} (Error)", [], {"display": "none"}
    else:
        # Show spinner with status
        status_label = status_labels.get(status, status.replace("_", " ").title())
        spinner_content = [
            html.Div(className="loading-spinner"),
            html.Span(f"In progress – {status_label}...", className="processing-text"),
        ]
        return f"Result of {title}", spinner_content, {"display": "flex"}


@callback(
    Output("results-table-title", "children"),
    Output("output-results", "children"),
    Output("output-results-graph", "children"),
    State("url", "pathname"),
    Input("all-results", "children"),
    Input("refresh-trigger", "data"),
)
def show_complete_results(path, generated_page, refresh_trigger):
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
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    result = utils.get_result(result_id)

    if "genetic" not in result["result_type"] or "output" not in result:
        return "", "", ""

    results_data = str_csv_to_df(result["output"])

    # Check if results_data is a valid DataFrame and has required columns
    if not isinstance(results_data, pd.DataFrame) or not all(
        col in results_data.columns for col in ["Position in ASM", "Bootstrap mean"]
    ):
        return (
            create_result_table_header(),  # Still return the header
            create_result_table(results_data),  # Display the table (might be empty)
            "",  # No graph to display
        )

    # Filter out statistical test summary rows (NaN in core columns) for the graphic
    core_cols = ["Position in ASM", "Bootstrap mean"]
    results_data[core_cols] = results_data[core_cols].replace(r'^\s*$', np.nan, regex=True)
    graphic_data = results_data.dropna(subset=core_cols)

    # Now it's safe to call create_result_graphic
    graph_output = create_result_graphic(graphic_data) if len(graphic_data) > 0 else None

    return (
        create_result_table_header(),
        create_result_table(results_data),
        graph_output,
    )


@callback(
    Output("climatic-tree-title", "children"),
    Output("climatic-tree", "children"),
    State("url", "pathname"),
    Input("output-results-graph", "children"),
    Input("theme-store", "data"),
    Input("refresh-trigger", "data"),
)
def create_climatic_trees(path, generated_results_header, is_dark_theme, refresh_trigger):
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
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    add_to_cookie(result_id)

    result = utils.get_result(result_id)
    if "climatic" not in result["result_type"] or "climatic_trees" not in result:
        return "", ""

    climatic_trees = result["climatic_trees"]
    tree_names = list(climatic_trees.keys())
    climatic_elements = []
    for tree in climatic_trees.values():
        tree = Phylo.read(StringIO(tree), "newick")
        nodes, edges = generate_elements(tree)
        climatic_elements.append(nodes + edges)

    return create_climatic_trees_header(), html.Div(
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
    Input("download-button-complete", "n_clicks"),
    Input("download-btn-genetic", "n_clicks"),
    Input("download-btn-climatic", "n_clicks"),
    prevent_initial_call=True,
)
def download_results(
    path,
    btn_aligned,
    btn_complete,
    btn_genetic,
    btn_climatic,
):
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

    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    result = utils.get_result(result_id)

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "download-btn-genetic" and btn_genetic:
        if "genetic_trees" not in result:
            raise dash.exceptions.PreventUpdate
        result_genetic_trees = result["genetic_trees"]
        data_genetic = "".join(list(result_genetic_trees.values()))
        return dict(
            content=data_genetic, filename=result["name"] + "_genetic_trees.newick"
        ), {"message": "Genetic trees downloaded!", "type": "success"}
    if trigger_id == "download-btn-climatic" and btn_climatic:
        if "climatic_trees" not in result:
            raise dash.exceptions.PreventUpdate
        result_climatic_trees = result["climatic_trees"]
        data_climatic = "".join(list(result_climatic_trees.values()))
        return dict(
            content=data_climatic, filename=result["name"] + "_climatic_trees.newick"
        ), {"message": "Climatic trees downloaded!", "type": "success"}
    if trigger_id == "download-button-aligned" and btn_aligned:
        if "msaSet" not in result:
            raise dash.exceptions.PreventUpdate
        result_msa = result["msaSet"]
        data_msa = json.dumps(result_msa)
        return dict(
            content=data_msa, filename=result["name"] + "_msa.json"
        ), {"message": "Genetic sequences downloaded!", "type": "success"}
    if trigger_id == "download-button-complete" and btn_complete:
        if "output" not in result:
            raise dash.exceptions.PreventUpdate
        data_results = str_csv_to_df(result["output"])
        return dict(
            content=data_results.to_csv(header=True, index=False),
            filename=result["name"] + "_results.csv",
        ), {"message": "Output downloaded!", "type": "success"}

    raise dash.exceptions.PreventUpdate


@callback(
    Output("genetic-tree-title", "children"),
    Output("genetic-tree", "children"),
    State("url", "pathname"),
    Input("output-results-graph", "children"),
    Input("theme-store", "data"),
    Input("refresh-trigger", "data"),
)
def create_genetic_trees(path, generated_results_header, is_dark_theme, refresh_trigger):
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
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    result = utils.get_result(result_id)
    if "genetic" not in result["result_type"] or "genetic_trees" not in result:
        return "", ""

    genetic_trees = result["genetic_trees"]
    tree_names = list(genetic_trees.keys())

    genetic_elements = []
    for tree in genetic_trees.values():
        tree = Phylo.read(StringIO(tree), "newick")
        nodes, edges = generate_elements(tree)
        genetic_elements.append(nodes + edges)

    return create_genetic_trees_header(), html.Div(
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


def create_result_table_header():
    """
    Creates the collapsible section header for the results table.
    """
    return html.Div(
        [
            html.Div("Results", className="result-section-title"),
            html.Img(
                src="../../assets/icons/angle-down.svg",
                id="results-table-collapse-button",
                className="icon collapse-icon",
            ),
        ],
        className="result-section-header",
    )


def create_result_table(data):
    """
    This function creates the results table
    args:
        data (pandas.DataFrame): the data to display in the table
    returns:
        dash_table.DataTable: the table containing the results
    """

    return html.Div(
        [
            dash_table.DataTable(
                id="datatable-interactivity",
                data=data.to_dict("records"),
                columns=[{"name": i, "id": i} for i in data.columns],
                filter_action="native",
                sort_action="native",
                sort_mode="single",
                page_current=0,
                page_size=15,
                filter_query="",
                row_selectable="multi",
                **utils.get_table_styles(),
            )
        ],
        className="result-table",
    )


def create_result_graphic(results_data):
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
                name="bootstrap mean",
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
            title_text=str("Bootstrap mean and " + distance_method),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
        )
        fig.update_xaxes(
            title_text="Position in ASM", gridcolor="rgba(255,255,255,0.2)"
        )
        fig.update_yaxes(
            title_text="<b>Bootstrap mean</b>",
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


def create_climatic_trees_header():
    """
    Creates the collapsible section header for the climatic trees.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div("Climatic Trees", className="result-section-title"),
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
                    html.Span("download climatic trees", className="text"),
                    html.Img(
                        src="../../assets/icons/download.svg", className="icon"
                    ),
                ],
                className="button download download-climatic-trigger",
            ),
        ],
        className="result-section-header result-section-header--with-action",
    )


def create_genetic_trees_header():
    """
    Creates the collapsible section header for the genetic trees.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div("Genetic Trees", className="result-section-title"),
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
                    html.Span("download genetic trees", className="text"),
                    html.Img(
                        src="../../assets/icons/download.svg", className="icon"
                    ),
                ],
                className="button download download-genetic-trigger",
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
