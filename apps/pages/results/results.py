import dash_bootstrap_components as dbc
from dash import html, callback, dcc
import dash
from flask import request
from dash.dependencies import Input, Output
import utils.utils as utils

dash.register_page(__name__, path_template='/results')

NO_RESULTS_HTML = html.Div([
                    html.Div([
                        html.Div('You have no results yet. You can start a new job by going to the "Upload data" page',
                                 className="text"),
                        html.Div(className="img bg1"),
                    ], className="notification"),
                ], className="emptyResults"),



def get_layout():
    dcc.Location(id="url")
    return html.Div([
    html.Div([
        html.Div(children=[
            dash.dcc.Location(id='url'),
            html.Div(id='cookie_output', className="hidden"),  # needed for the callback to trigger
            html.Div([
                html.Div('Results', className="title"),
                html.Div(id='results_list', className="resultsRow"),
            ], className="resultsContainer"),
        ], className="results"),
    ])
])

@callback(
    Output('results_list', 'children'),
    Input('url', 'pathname'),
)
def generate_result_list(path):
   
    cookie = request.cookies.get("AUTH")
    if not cookie:
        return NO_RESULTS_HTML
    
    cookies = cookie.split('.')
    results = utils.get_results(cookies)
    
    if not results:
        return NO_RESULTS_HTML
        
    layout = []
    for result in results:
        progress_value = 100 if result['status'] == 'complete' else 50
        layout.append(
            html.Div([
                html.Div([
                    html.Div('Name', className="label"),
                    html.Div(result['name'], className="data"),
                ], className="nameContainer"),
                html.Div([
                    html.Div('Creation date', className="label"),
                    html.Div(result['created_at'].strftime("%Y/%m/%d"), className="data"),
                ], className="creationDateContainer"),
                html.Div([
                    html.Div('Expiration date',className="label"),
                    html.Div(result['expired_at'].strftime("%Y/%m/%d"), className="data"),
                ], className="expirationDateContainer"),
                html.Div([
                    html.Div('Progress',className="label"),
                    html.Div([
                        dbc.Progress(value=progress_value),
                    ], className='progressBar'),
                ], className="progressContainer"),
                html.Div([
                    # html.Div('Expiration date', className="label"),
                    html.A(
                        html.Img(src='/assets/icons/arrow-circle-right.svg', className="icon"),
                        href=f'/result/{result["_id"]}',
                    ),
                ], className="arrowContainer"),
            ], className="row")
        )

    return layout

layout = get_layout()