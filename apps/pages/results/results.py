import dash_bootstrap_components as dbc
from dash import html, callback, dcc
import dash
from flask import request
from dash.dependencies import Input, Output
import utils.utils as utils

dash.register_page(__name__, path_template='/results')

NO_RESULTS_HTML = html.Div([
    html.Div([
        html.Div('You have no results yet. You can start a new job by going to the "Upload data" page', className="text"),
        html.Div(className="img bg1"),
    ], className="notification"),
], className="empty-results"),


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

    cookie = request.cookies.get("AUTH")
    if not cookie:
        return NO_RESULTS_HTML

    cookies = cookie.split('.')
    results = utils.get_results(cookies)

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
    progress_value = 100 if result['status'] == 'complete' else 50
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
                        dbc.Progress(value=progress_value),
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
