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
    # TODO: Change this to get id from the cookie
    results = utils.get_all_results()
    layout = []
    if not results:
        return html.Div([
                    html.Div([
                        html.Div('You have no results yet. You can start a new job by going to the "Upload data" page',
                                 className="text"),
                        html.Div(className="img bg1"),
                    ], className="notification"),
                ], className="emptyResults"),
    for result in results:
        layout.append(create_result_html(result))

    return layout


@callback(
        Output('cookie_output', 'children'),
        [Input('url', 'pathname')],
)

def make_cookie(result_id=None):
    """Create a cookie with the result id

    Args:
        result_id (str): The id of the result to add to the cookie

    """
    auth_cookie= request.cookies.get("AUTH")
    if auth_cookie:
        # If the "Auth" cookie exists, split the value into a list of IDs
        auth_ids = auth_cookie.split('.')
    else:
        # If the "Auth" cookie does not exist, set the value to an empty list
        auth_ids = []

    auth_ids.append(str(result_id))

    #Check if the id exists in the mongo db and remove it if it doesn't
    auth_ids = check_id_exist(auth_ids)

    #Create the string format for the cookie
    auth_cookie_value = '.'.join(auth_ids)

    response = dash.callback_context.response
    response.set_cookie("AUTH", auth_cookie_value)

    return result_id

def check_id_exist(auth_ids):
    """Check if the id exists in the mongo db and remove it if it doesn't

    Args:
        auth_ids (list): The list of ids to check

    Returns:
        list: The list of ids that exist in the mongo db

    """
    tmp_auth_ids = auth_ids

    for index in auth_ids:
        #if files_ctrl.get_file_by_id(index) == []: # de ce que j'ai compis du get_files_by_id, il renvoie un tableau vide si l'id n'existe pas
        #    tmp_auth_ids.remove(index)
        pass

    return tmp_auth_ids


def create_result_html(result):
    """
    Args:
        result (dict): The result to display
    Returns:
        html.Div: The html div containing the result
    """
    progress_value = 100 if result['status'] == 'complete' else 50

    html_list = []
    html_list.append( html.Div([
                        html.Div('Name', className="label"),
                        html.Div(result['name'], className="data"),
                    ], className="nameContainer"))
    if ENV_CONFIG['APP_MODE'] != 'local':
        html_list.append( html.Div([
                        html.Div('Creation date', className="label"),
                        html.Div(result['created_at'].strftime("%Y/%m/%d"), className="data"),
                    ], className="creationDateContainer"))
        html_list.append(
                    html.Div([
                        html.Div('Expiration date',className="label"),
                        html.Div(result['expired_at'].strftime("%Y/%m/%d"), className="data"),
                    ], className="expirationDateContainer"))
        
    html_list.append( html.Div([
                        html.Div('Progress',className="label"),
                        html.Div([
                            dbc.Progress(value=progress_value),
                        ], className='progressBar'),
                    ], className="progressContainer"))
    html_list.append(
                    html.Div([
                        # html.Div('Expiration date', className="label"),
                        html.A(
                            html.Img(src='/assets/icons/arrow-circle-right.svg', className="icon"),
                            href=f'/result/{result["_id"]}',
                        ),
                    ], className="arrowContainer"))
    
    return html.Div(html_list, className="row")

layout = get_layout()