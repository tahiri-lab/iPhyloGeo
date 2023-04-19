from dotenv import load_dotenv, dotenv_values
import dash_bootstrap_components as dbc
from dash import html, callback, dcc
import dash
from flask import request
from dash.dependencies import Input, Output
import utils.utils as utils
load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value


dash.register_page(__name__, path_template='/results')

NO_RESULTS_HTML = html.Div([
    html.Div([
        html.Div('You have no results yet. You can start a new job by going to the "Upload data" page', className="text"),
        html.Div(className="img bg1"),
    ], className="notification"),
], className="empty-results"),

PROGRESS = {'pending': 0, 'climatic_trees': 10, 'alignement': 66, 'genetic_trees': 90, 'complete': 100, 'error': 100}


def get_layout():
    dcc.Location(id="url")
    return html.Div([
        html.Div([
            html.Div(children=[
                dash.dcc.Location(id='url'),  # invisible component needed for the callback
                html.Div([
                    html.Div('Results', className="title"),
                    html.Div(id='results-list', className="results-row"),
                ], className="results-container"),
            ], className="results"),
        ])
    ])


@callback(
    Output('results-list', 'children'),
    Input('url', 'pathname'),
)
def generate_result_list(path):
    """
    This function generates the list of layout of the results in the cookies.
    args :
        path : unused
    returns :
        layout : layout containing NO_RESULTS_HTML if no results are found, or a list of the results layout otherwise
    """

    try:
        cookie = request.cookies.get("AUTH")
    except Exception as e:
        print(e)
        return NO_RESULTS_HTML

    if not cookie:
        return NO_RESULTS_HTML

    results_ids = cookie.split('.')
    results = utils.get_results(results_ids)

    new_cookie_ids = [str(result['_id']) for result in results]
    response = dash.callback_context.response
    response.set_cookie(utils.COOKIE_NAME, '.'.join(new_cookie_ids), max_age=utils.COOKIE_MAX_AGE)

    if not results:
        return NO_RESULTS_HTML

    return [create_layout(result) for result in results]


def create_layout(result):
    """
    This function creates the layout for a result.
    args :
        result (dict) : result object
    returns :
        layout : layout containing the result
    """
    return html.Div([
        html.Div([
            html.Div('Name', className="label"),
            html.Div(result['name'], className="data"),
        ], className="nameContainer"),
        html.Div([
            html.Div('Creation date', className="label"),
            html.Div(result['created_at'].strftime("%Y/%m/%d"), className="data"),
        ], className="creationDateContainer"),
        html.Div([
            html.Div('Expiration date', className="label"),
            html.Div(result['expired_at'].strftime("%Y/%m/%d"), className="data"),
        ], className="expirationDateContainer"),
        html.Div([
            html.Div('Progress', className="label"),
            html.Div([
                dbc.Progress(value=PROGRESS[result['status']], label='Error' if result['status'] == 'error' else None, color="danger" if result['status'] == 'error' else ""),
            ], className='progressBar'),
        ], className="progressContainer"),
        html.Div([
            html.A(
                html.Img(src='/assets/icons/arrow-circle-right.svg', className="icon"),
                href=f'/result/{result["_id"]}',
            ),
        ], className="arrowContainer"),
    ], className="row")


layout = get_layout()
