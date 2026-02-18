import dash
import dash_bootstrap_components as dbc
import utils.utils as utils
from components.result_card import create_result_card
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dotenv import dotenv_values, load_dotenv
from flask import request

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

dash.register_page(__name__, path_template="/results")

NO_RESULTS_HTML = html.Div(
    [
        html.Div(
            [
                html.Div(
                    'You have no results yet. You can start a new job by going to the "Upload data" page',
                    className="text",
                ),
                html.Div(className="img bg1"),
            ],
            className="notification",
        ),
    ],
    className="empty-results",
)

PROGRESS = {
    "pending": 0,
    "climatic_trees": 10,
    "alignement": 66,
    "genetic_trees": 90,
    "complete": 100,
    "error": 100,
}


def get_layout():
    return html.Div(
        [
            dcc.Location(id="url"),  # This component is needed for URL change detection
            html.Div(
                [
                    html.Div(
                        children=[
                            html.Div(
                                [
                                    html.Div("Results", className="title"),
                                    html.Div(
                                        id="results-list", className="results-row"
                                    ),
                                ],
                                className="results-container",
                            ),
                        ],
                        className="results",
                    ),
                ]
            ),
        ]
    )


@callback(
    Output("results-list", "children"),
    Input("url", "pathname"),
)
def generate_result_list(path):
    """
    This function generates the list of layout of the results.
    args :
        path : unused
    returns :
        layout : layout containing NO_RESULTS_HTML if no results are found, or a list of the results layout otherwise
    """
    if ENV_CONFIG["HOST"] == "local":
        results = utils.get_all_results()
        if not results:
            return NO_RESULTS_HTML
        return [create_layout(result) for result in results]

    try:
        cookie = request.cookies.get("AUTH")
    except Exception as e:
        print(e)
        return NO_RESULTS_HTML

    if not cookie:
        return NO_RESULTS_HTML

    results_ids = cookie.split(".")
    results = utils.get_results(results_ids)

    if not results:
        return NO_RESULTS_HTML

    # Update the cookie with the new list of result IDs, if needed
    new_cookie_ids = [str(result["_id"]) for result in results]
    response = dash.callback_context.response
    if response:
        response.set_cookie(
            utils.COOKIE_NAME, ".".join(new_cookie_ids), max_age=utils.COOKIE_MAX_AGE
        )

    return [create_layout(result) for result in results]


def create_layout(result):
    """
    This function creates the layout for a result.
    args :
        result (dict) : result object
    returns :
        layout : layout containing the result
    """
    # Determine dates based on environment
    created_at = None
    expired_at = None

    if ENV_CONFIG["HOST"] != "local":
        created_at = result["created_at"].strftime("%d/%m/%Y")
        expired_at = result["expired_at"].strftime("%d/%m/%Y")

    return create_result_card(
        name=result["name"],
        status=result["status"],
        created_at=created_at,
        expired_at=expired_at,
        result_id=str(result["_id"]),
    )


layout = get_layout()
