import dash
import utils.utils as utils
from components.result_card import create_result_card
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dotenv import dotenv_values, load_dotenv
from flask import request
from utils.background_tasks import get_task_status
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


# ---------------------------------------------------------------------------
# Per-mode step bases (% when a step *starts*)
# ---------------------------------------------------------------------------
STEP_BASES = {
    "genetic": {
        "pending": 0, "queued": 0, "running": 0,
        "climatic_trees": 5,
        "alignment": 15,
        "genetic_trees": 50,
        "output": 88,
        "complete": 100, "error": 100,
    },
    "aligned": {
        "pending": 0, "queued": 0, "running": 0,
        "climatic_trees": 5,
        "genetic_trees": 20,
        "output": 88,
        "complete": 100, "error": 100,
    },
    "tree": {
        "pending": 0, "queued": 0, "running": 0,
        "climatic_trees": 10,
        "output": 88,
        "complete": 100, "error": 100,
    },
}

STEP_ORDER = {
    "genetic": ["pending", "climatic_trees", "alignment", "genetic_trees", "output", "complete"],
    "aligned": ["pending", "climatic_trees", "genetic_trees", "output", "complete"],
    "tree":    ["pending", "climatic_trees", "output", "complete"],
}


def _get_mode(result):
    result_type = result.get("result_type", [])
    if "tree" in result_type:
        return "tree"
    if "aligned" in result_type:
        return "aligned"
    return "genetic"


def compute_progress(result) -> int:
    """
    Return a 0-100 progress integer for a result dict.

    Combines:
      - Step base %  from STEP_BASES (mode-aware)
      - Sub-step %   from background_tasks._task_store["sub_progress"]
        (the 'Started: X / Y' lines captured from aphylogeo's multiProcessor)
    """
    status = result.get("status", "pending")

    # Terminal states need no computation
    if status in ("complete", "error"):
        return 100

    mode = _get_mode(result)
    table = STEP_BASES[mode]
    base = table.get(status, 0)

    # Try to blend in within-step sub-progress
    task_status = get_task_status(str(result.get("_id", "")))
    sub = task_status.get("sub_progress") if task_status else None

    if sub is not None:
        order = STEP_ORDER[mode]
        try:
            idx = order.index(status)
            next_status = order[idx + 1] if idx + 1 < len(order) else status
            next_base = table.get(next_status, base)
            step_range = next_base - base
            base += round((sub / 100) * step_range)
        except ValueError:
            pass

    return max(0, min(99, base))   # cap at 99 until truly complete


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
    """Creates the card layout for a single result."""
    # Determine dates based on environment
    created_at = None
    expired_at = None

    if ENV_CONFIG["HOST"] != "local":
        created_at = result["created_at"].strftime("%d/%m/%Y")
        expired_at = result["expired_at"].strftime("%d/%m/%Y")

    status = result.get("status", "pending")
    progress = compute_progress(result) if status not in ("complete", "error") else None

    return create_result_card(
        name=result["name"],
        status=status,
        created_at=created_at,
        expired_at=expired_at,
        result_id=str(result["_id"]),
        progress=progress,
        lang=lang,
    )


layout = html.Div(id="results-page-content", children=get_layout())


@callback(Output("results-page-content", "children"), Input("language-store", "data"))
def update_results_language(language):
    lang = language if language in LANGUAGE_LIST else "en"
    return get_layout(lang)
