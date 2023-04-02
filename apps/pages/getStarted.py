from typing import Container
from dash import Dash, html, dcc, ctx
from dash.dependencies import Output, Input, ClientsideFunction
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from pages.upload import dataTypeSection, dropFileSection


from dash import dcc, html, State, Input, Output, clientside_callback,callback
from utils import utils
from pages.upload.meteo import paramsMeteo
from pages.upload.geo import params
from pages.upload import submitButton

dash.register_page(__name__, path='/getStarted')

layout = html.Div([
    dcc.Store(id='params', data={'genetic': {'file': None, 'layout': None}, 'climatic': {'file': None, 'layout': None}}),
    html.Div(id='action'),
    html.Div(
        className="getStarted",
        children=[
            # Upload type section
            # html.Div(children=[dataTypeSection.layout]),
            # Drop file section
            html.Div(children=[dropFileSection.layout]),
            # params (determine with the choose_option function in dataTypeSection)
            html.Div(id="climatic_params_layout"),
            html.Div(id="genetic_params_layout"),
            html.Div(id="submit_button"),
            html.Div(id="output_hidden_1", children=[], className="hidden"),
        ]
    ),
])

# Function to upload file and store it in the server
@callback(
    Output('genetic_params_layout', 'children'),
    Output('climatic_params_layout', 'children'),
    Output('submit_button', 'children'),
    Output('params', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    State('params', 'data'),
    prevent_initial_call=True,
    log = True
)
def upload_file(list_of_contents, list_of_names, last_modifieds, current_data):
    files = utils.get_files_from_base64(list_of_contents, list_of_names, last_modifieds)

    for file in files:
        if file['type'] == 'genetic':
            current_data['genetic']['file'] = file
            current_data['genetic']['layout'] = params.layout
        elif file['type'] == 'climatic':
            current_data['climatic']['file'] = file
            current_data['climatic']['layout'] = paramsMeteo.create_table(file)

    return current_data['genetic']['layout'], current_data['climatic']['layout'], submitButton.layout, current_data

@callback(
    Output('sumbit_button', 'children'),
    Input('submit_dataSet', 'n_clicks'),
    State('params', 'data'),
    prevent_initial_call=True
)
def submit_button(n_clicks, params):
    if n_clicks is None or n_clicks < 1 or (params['genetic']['file'] is None and params['climatic']['file'] is None):
        raise PreventUpdate

    if params['genetic']['file'] is not None:
        print('genetic')
        utils.save_files([params['genetic']['file']])
    if params['climatic']['file'] is not None:
        print('climatic')
        utils.save_files([params['climatic']['file']])

    return ''