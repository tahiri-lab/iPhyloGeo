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
from db.controllers.files import str_csv_to_df
from flask import request
from plotly.subplots import make_subplots

dash.register_page(__name__, path_template="/result/<result_id>")


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
        html.Div(id="dummy-share-result-output", style={"display": "none"}),
        html.Div(id="dummy-table-collapse", style={"display": "none"}),
        html.Div(id="dummy-climatic-collapse", style={"display": "none"}),
        html.Div(id="dummy-genetic-collapse", style={"display": "none"}),
        html.Div(id="dummy-email-collapse", style={"display": "none"}),
        html.Div(
            [
                html.H1(id="results-name", className="title"),
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
                                html.Span(t("result.actions.download-output", "en"), className="text", id="download-output-text"),
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
                                html.Span(t("result.actions.download-sequences", "en"), className="text", id="download-sequences-text"),
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
                ),
                # Email section card
                html.Div(
                    create_email_section(),
                    id="email-section-card-content",
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


@callback(
    Output("toast-store", "data", allow_duplicate=True),
    Input("share-result-btn", "n_clicks"),
    State("url", "href"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def share_result_link(n_clicks, href, language):
    """
    Copy the result link to clipboard and show a toast notification.
    """
    lang = language if language in LANGUAGE_LIST else "en"
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
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
    if not validate_email(user_email):
        return {"message": t("result.email.invalid", lang), "type": "error"}
    success = mail.send_results_ready_email(user_email, pathname, lang)
    msg = t("result.email.sent", lang) if success else t("result.email.error", lang)
    return {"message": msg, "type": "success" if success else "error"}


@callback(
    Output("results-name", "children"),
    Input("url", "pathname"),
    Input("language-store", "data"),
)
def show_result_name(path, language):
    """
    args:
        path (str): the path of the page
    returns:
        html.Div: the div containing the name of the result
    """
    lang = language if language in LANGUAGE_LIST else "en"
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    title = utils.get_result(result_id)["name"]
    return t("result.title-of", lang).replace("{name}", title)


@callback(
    Output("share-action-text", "children"),
    Output("download-output-text", "children"),
    Output("download-sequences-text", "children"),
    Output("email-section-card-content", "children"),
    Input("language-store", "data"),
)
def update_result_static_text(language):
    lang = language if language in LANGUAGE_LIST else "en"
    return (
        t("result.actions.share", lang),
        t("result.actions.download-output", lang),
        t("result.actions.download-sequences", lang),
        create_email_section(lang),
    )


@callback(
    Output("results-table-title", "children"),
    Output("main-results-table-container", "children"),
    Output("statistical-results-table-container", "children"),
    Output("output-results-graph", "children"),
    State("url", "pathname"),
    Input("all-results", "children"),
    Input("language-store", "data"),
)
def show_complete_results(path, generated_page, language):
    """

      This function creates the header (title & download button) of the results,
    the results table, and the results graph.

    Args:
        path (str): The path of the page.
        generated_page: (Not used in this function, but required for the callback trigger)

    Returns:
        html.Div: The div containing the header of the results table.
        html.Div: The div containing the results table.
        Union[dcc.Graph, None]: The results graph if data is available and valid, else None.
    """
    lang = language if language in LANGUAGE_LIST else "en"
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    result = utils.get_result(result_id)

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
                t("result.table.main-results-title", lang),
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
        t("result.table.main-results-title", lang),
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
    Input("language-store", "data"),
)
def create_climatic_trees(path, generated_results_header, is_dark_theme, language):
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
    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    add_to_cookie(result_id)

    result = utils.get_result(result_id)
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


@callback(
    Output("download-link-results", "data"),
    Output("toast-store", "data", allow_duplicate=True),
    State("url", "pathname"),
    Input("climatic-tree", "children"),
    Input("genetic-tree", "children"),
    Input("download-button-genetic", "n_clicks"),
    Input("download-button-climatic", "n_clicks"),
    Input("download-button-aligned", "n_clicks"),
    Input("download-button-complete", "n_clicks"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def download_results(
    path,
    climatic_tree,
    genetic_tree,
    btn_genetic,
    btn_climatic,
    btn_aligned,
    btn_complete,
    language,
):
    lang = language if language in LANGUAGE_LIST else "en"
    """
    This function creates the list of divs containing the genetic trees
    Because the buttons are not created in the initial layout, we need to use the suppress_callback_exceptions

    args:
        path (str): the path of the page
        climatic_tree: Climatic section previously generated, have to be generated for this callback to fire
        genetic_tree: Genetic section previously generated, have to be generated for this callback to fire
        btn_genetic : dummy inpput needed to trigger the callback
        btn_climatic : dummy inpput needed to trigger the callback
        btn_msa : dummy inpput needed to trigger the callback
        btn_data : dummy inpput needed to trigger the callback
    """

    result_id = path.split("/")[-1]
    if not result_id or not ObjectId.is_valid(result_id):
        raise dash.exceptions.PreventUpdate
    result = utils.get_result(result_id)

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "download-button-genetic" and btn_genetic:
        result_genetic_trees = result["genetic_trees"]
        data_genetic = "".join(list(result_genetic_trees.values()))
        return dict(
            content=data_genetic, filename=result["name"] + "_genetic_trees.newick"
        ), {"message": t("result.toast.genetic-downloaded", lang), "type": "success"}
    if trigger_id == "download-button-climatic" and btn_climatic:
        result_climatic_trees = result["climatic_trees"]
        data_climatic = "".join(list(result_climatic_trees.values()))
        return dict(
            content=data_climatic, filename=result["name"] + "_climatic_trees.newick"
        ), {"message": t("result.toast.climatic-downloaded", lang), "type": "success"}
    if trigger_id == "download-button-aligned" and btn_aligned:
        result_msa = result["msaSet"]
        data_msa = json.dumps(result_msa)
        return dict(
            content=data_msa, filename=result["name"] + "_msa.json"
        ), {"message": t("result.toast.sequences-downloaded", lang), "type": "success"}
    if trigger_id == "download-button-complete" and btn_complete:
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
    Input("language-store", "data"),
)
def create_genetic_trees(path, generated_results_header, is_dark_theme, language):
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
            html.Div(t("result.sections.results", lang), className="result-section-title"),
            html.Img(
                src="../../assets/icons/angle-down.svg",
                id="results-table-collapse-button",
                className="icon collapse-icon",
            ),
        ],
        className="result-section-header",
    )


def create_titled_result_table(data, title, table_id, lang="en"):
    return html.Div(
        [
            html.Div(title, className="results-table-title"),
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
                className="button download",
                id="download-button-climatic",
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
                    html.Span(t("result.actions.download-genetic-trees", lang), className="text"),
                    html.Img(
                        src="../../assets/icons/download.svg", className="icon"
                    ),
                ],
                className="button download",
                id="download-button-genetic",
            ),
        ],
        className="result-section-header result-section-header--with-action",
    )


# the following code is taken from https://dash.plotly.com/cytoscape/biopython
def generate_tree(elem, name, is_dark_theme=True):
    return html.Div(
        [
            html.H3(name, className="treeTitle"),
            cyto.Cytoscape(
                elements=elem,
                stylesheet=get_cytoscape_stylesheet(is_dark_theme),
                layout={"name": "preset", "fit": True, "padding": 20},
                style={"height": "400px", "width": "100%", "cursor": "pointer"},
                userZoomingEnabled=False,
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
