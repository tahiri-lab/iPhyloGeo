import dash
from datetime import datetime, timezone
import utils.utils as utils
from components.result_card import create_result_card
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dotenv import dotenv_values, load_dotenv
from flask import request
from utils.i18n import LANGUAGE_LIST, t

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

dash.register_page(__name__, path_template="/results")


def _temporary_remaining_label(result, lang="en"):
    if not result.get("is_temporary"):
        return None

    expires_at = utils.to_datetime_utc(result.get("expired_at"))
    if expires_at == datetime.min.replace(tzinfo=timezone.utc):
        return t("results.card.temporary", lang)

    now = datetime.now(timezone.utc)

    delta_seconds = int((expires_at - now).total_seconds())
    if delta_seconds <= 0:
        return t("results.card.expired-now", lang)

    total_minutes = max(1, delta_seconds // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0:
        return (
            t("results.card.expire-in-hours-minutes", lang)
            .replace("{hours}", str(hours))
            .replace("{minutes}", str(minutes))
        )

    return t("results.card.expire-in-minutes", lang).replace(
        "{count}", str(total_minutes)
    )


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


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def get_layout(lang="en"):
    return html.Div(
        [
            # Poll every 3 s to refresh in-progress cards
            dcc.Interval(id="results-poll", interval=3000, n_intervals=0),
            html.Div(
                [
                    html.Div(
                        children=[
                            html.Div(
                                [
                                    html.Div(t("results.title", lang), className="title", id="results-title"),
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


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@callback(
    Output("results-list", "children"),
    Input("url", "pathname"),
    Input("results-poll", "n_intervals"),
    Input("language-store", "data"),
)
def generate_result_list(path, _n, language):
    """
    Generates the list of result cards.
    Triggered on page load (url change) and every 3 s (Interval).
    """
    lang = language if language in LANGUAGE_LIST else "en"

    if ENV_CONFIG["HOST"] == "local":
        local_results = utils.get_all_results() or []

        temp_results = []
        try:
            cookie = request.cookies.get("AUTH")
            if cookie:
                temp_ids = [result_id for result_id in cookie.split(".") if result_id.startswith("tmp_")]
                if temp_ids:
                    temp_results = utils.get_results(temp_ids)
        except Exception as e:
            print(e)

        combined = {str(result["_id"]): result for result in local_results}
        for result in temp_results:
            combined[str(result["_id"])] = result

        results = sorted(
            combined.values(),
            key=lambda result: utils.to_datetime_utc(result.get("created_at")),
        )

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
    results = sorted(results, key=lambda result: utils.to_datetime_utc(result.get("created_at")))

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
    """Creates the card layout for a single result."""
    # Determine dates based on environment
    created_at = None
    expired_at = None

    if ENV_CONFIG["HOST"] != "local":
        created_at = utils.format_card_date(result.get("created_at"))
        expired_at = utils.format_card_date(result.get("expired_at"))

    remaining_time = _temporary_remaining_label(result, lang)

    status = result.get("status", "pending")

    return create_result_card(
        name=result["name"],
        status=status,
        created_at=created_at,
        expired_at=expired_at,
        remaining_time=remaining_time,
        result_id=str(result["_id"]),
        lang=lang,
    )


layout = html.Div(id="results-page-content", children=get_layout())


@callback(
    Output("results-title", "children"),
    Input("language-store", "data"),
)
def update_results_language(language):
    lang = language if language in LANGUAGE_LIST else "en"
    return t("results.title", lang)
