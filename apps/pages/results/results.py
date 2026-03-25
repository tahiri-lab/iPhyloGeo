import dash
import utils.utils as utils
from components.result_card import create_result_card
from dash import callback, html
from dash.dependencies import Input, Output
from dotenv import dotenv_values, load_dotenv
from flask import request
from utils.i18n import LANGUAGE_LIST, t

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

dash.register_page(__name__, path_template="/results")


def get_no_results_html(lang="en"):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        t("results.empty", lang),
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


def get_layout(lang="en"):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        children=[
                            html.Div(
                                [
                                    html.Div(t("results.title", lang), className="title"),
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
    Input("language-store", "data"),
)
def generate_result_list(path, language):
    """
    This function generates the list of layout of the results.
    args :
        path : unused
    returns :
        layout : layout containing NO_RESULTS_HTML if no results are found, or a list of the results layout otherwise
    """
    lang = language if language in LANGUAGE_LIST else "en"

    if ENV_CONFIG["HOST"] == "local":
        results = utils.get_all_results()
        if not results:
            return get_no_results_html(lang)
        return [create_layout(result, lang) for result in results]

    try:
        cookie = request.cookies.get("AUTH")
    except Exception as e:
        print(e)
        return get_no_results_html(lang)

    if not cookie:
        return get_no_results_html(lang)

    results_ids = cookie.split(".")
    results = utils.get_results(results_ids)

    if not results:
        return get_no_results_html(lang)

    # Update the cookie with the new list of result IDs, if needed
    new_cookie_ids = [str(result["_id"]) for result in results]
    response = dash.callback_context.response
    if response:
        response.set_cookie(
            utils.COOKIE_NAME, ".".join(new_cookie_ids), max_age=utils.COOKIE_MAX_AGE
        )

    return [create_layout(result, lang) for result in results]


def create_layout(result, lang="en"):
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
        lang=lang,
    )


layout = html.Div(id="results-page-content", children=get_layout())


@callback(Output("results-page-content", "children"), Input("language-store", "data"))
def update_results_language(language):
    lang = language if language in LANGUAGE_LIST else "en"
    return get_layout(lang)
