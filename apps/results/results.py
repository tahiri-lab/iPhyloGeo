import dash_bootstrap_components as dbc

from dash import dcc, html, State, Input, Output
import dash_daq as daq
from dash.dependencies import Input, Output, ClientsideFunction
import pandas as pd
from app import app

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


