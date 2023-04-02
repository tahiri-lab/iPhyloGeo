from typing import Container

from Bio import SeqIO
from dash import dcc, html, State, Input, Output, clientside_callback,callback
from dash.dependencies import Output, Input, ClientsideFunction
import dash_bootstrap_components as dbc
import dash
from utils import utils
from pages.upload import dataTypeSection, dropFileSection
from pages.upload.meteo import paramsMeteo
from pages.upload.geo import params
from pages.upload import submitButton
import json

dash.register_page(__name__, path='/getStarted')

# climatic = html.Div(id="climatic-section", children=[])
# genetic = html.Div(id="genetic-section", children=[])
all_section = []

layout = html.Div([
    dcc.Store(data='test', id='memory'),
    dcc.Store(id='memory-output'),
    html.Div(id='action'),
    html.Div(
        className="getStarted",
        children=[
            # Upload type section
            # html.Div(children=[dataTypeSection.layout]),
            # Drop file section
            html.Div(children=[dropFileSection.layout]),
            # params (determine with the choose_option function in dataTypeSection)
            html.Div(id="climatic-section", children=[]),
        ]
    ),
])

@callback(
    # Output('upload-data-output', 'children'),
    Output('climatic-section', 'children'),
    Output('memory', 'data'),
    # Output('genetic-section', 'children'),
    # Output('all-section', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    prevent_initial_call=True,log = True
)
def upload_file(list_of_contents, list_of_names, last_modifieds):
    result = {}

    files = utils.get_files_from_base64(list_of_contents, list_of_names, last_modifieds)
    for file in files:
        if file['type'] == 'climatic':
            result['climatic'] = file['df'].to_json()
            all_section.append(paramsMeteo.create_table(file))
        if file['type'] == 'genetic':
            result['genetic'] = file['file']
            all_section.append(params.layout)

    all_section.append(submitButton.layout)

    #
    # print(type(files[0]))
    return all_section, result

@callback(
    Output('memory-output', 'children'),
    Input('memory', 'data'),
    Input('submit_dataSet', 'n_clicks'),
    # Input('memory', 'value'),
    prevent_initial_call=True,log = True
)
def test2(data, click):
    # TODO : enregistrer les données dans la base de données
    if click is not None:
        if data['climatic'] is not None and data['genetic'] is not None:
            utils.run_complete_pipeline(data['climatic'], data['genetic'], {}, {})
        elif data['climatic'] is not None:
            utils.run_climatic_pipeline(data['climatic'], {})

    return ''

