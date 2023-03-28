import dash_bootstrap_components as dbc
from dash import html, callback
import dash_daq as daq
import pandas as pd
import dash
from flask import request
from dash.dependencies import Input, Output, ClientsideFunction
#import db.controllers.files as files_ctrl



dash.register_page(__name__, path_template='/results/<result_id>')


data = {'results': [
    [{'name': 'result1'}, {'creationDate': '2023/01/02'}, {'expirationDate': '2023/01/22'}, {'progress': 10}],
    [{'name': 'result2'}, {'creationDate': '2023/01/03'}, {'expirationDate': '2023/01/23'}, {'progress': 50}],
    [{'name': 'result3'}, {'creationDate': '2023/01/04'}, {'expirationDate': '2023/01/24'}, {'progress': 100}],
    [{'name': 'result4'}, {'creationDate': '2023/01/05'}, {'expirationDate': '2023/01/25'}, {'progress': 85}],
]}
df_results = pd.DataFrame(data)


def generate_result_list(result_data):
    return html.Div([
        html.Div([
            html.Div('Name', className="label"),
            html.Div(result_data[0]['name'], className="data"),
        ], className="nameContainer"),
        html.Div([
            html.Div('Creation date', className="label"),
            html.Div(result_data[1]['creationDate'], className="data"),
        ], className="creationDateContainer"),
        html.Div([
            html.Div('Expiration date', className="label"),
            html.Div(result_data[2]['expirationDate'], className="data"),
        ], className="expirationDateContainer"),
        html.Div([
            html.Div('Progress', className="label"),
            html.Div([
                dbc.Progress(value=result_data[3]['progress']),
            ], className='progressBar'),
        ], className="progressContainer"),
        html.Div([
            # html.Div('Expiration date', className="label"),
            html.Img(src='/assets/icons/arrow-circle-right.svg', className="icon"),
        ], className="arrowContainer"),
    ], className="row")

layout = html.Div([
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
            html.Div(children=[generate_result_list(i) for i in df_results['results']], className="resultsRow"),
        ], className="resultsContainer"),
    ], className="results"),
])



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

    print(result_id)
    print (auth_ids)
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
        print(index)
        #if files_ctrl.get_file_by_id(index) == []: # de ce que j'ai compis du get_files_by_id, il renvoie un tableau vide si l'id n'existe pas
        #    tmp_auth_ids.remove(index)

    
    return tmp_auth_ids


