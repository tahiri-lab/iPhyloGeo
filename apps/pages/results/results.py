import dash_bootstrap_components as dbc
from dash import html, callback, dcc
import dash
from flask import request
from dash.dependencies import Input, Output
import utils.utils as utils

dash.register_page(__name__, path_template='/results')

def get_layout():
    return html.Div([
    html.Div(children=[
        dash.dcc.Location(id='url', refresh=False),
        html.Div(id='cookie_output', className="hidden"), # needed for the callback to trigger
        html.Div([
            html.Div('Results', className="title"),
            html.Div([
                html.Div([
                    html.Div('3', className="count"),
                    html.Div(className="img bg1"),
                    html.Div('Jobs in progress', className="notificationFooter")
                ], className="notification"),
                html.Div([
                    html.Div('12', className="count"),
                    html.Div(className="img bg2"),
                    html.Div('days before your files expire', className="notificationFooter")
                ], className="notification"),
            ], className="notificationStack"),
            html.Div(children=generate_result_list(), className="resultsRow"),
        ], className="resultsContainer"),
    ], className="results"),
])

def generate_result_list():
    # TODO: Change this to get id from the cookie
    results = utils.get_all_results()
    layout = []
    for result in results:
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
                        dbc.Progress(value=50),
                    ], className='progressBar'),
                ], className="progressContainer"),
                html.Div([
                    # html.Div('Expiration date', className="label"),
                    html.A(
                        html.Img(src='/assets/icons/arrow-circle-right.svg', className="icon"),
                        href=f'/result/{result["_id"]}',
                    ),
                    dcc.Store(id='result_res', data=str(result["_id"])),
                ], className="arrowContainer"),
            ], className="row")
        )

    return layout


@callback(
    Output('result_id', 'data'),
    Input('result_res', 'data'),
)
def update_result(result_id):
    return result_id

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

layout = get_layout()