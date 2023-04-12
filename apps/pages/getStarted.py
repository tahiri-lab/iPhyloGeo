from dash import dcc, html, State, Input, Output, callback
from dash.dependencies import Output, Input
import dash
from dash.exceptions import PreventUpdate
import multiprocessing

import dash_bootstrap_components as dbc
import pages.upload.dropFileSection as dropFileSection
import utils.utils as utils
import pages.upload.climatic.paramsClimatic as paramsClimatic
import pages.upload.genetic.paramsGenetic as paramsGenetic
import pages.upload.submitButton as submitButton
import pages.utils.popup as popup


dash.register_page(__name__, path='/getStarted')

layout = html.Div([
    dcc.Store(id='params', data={'genetic': {'file': None, 'layout': None, 'name': None}, 'climatic': {'file': None, 'layout': None}}),
    dcc.Store(id='params_climatic', data={'names': None}),
    dcc.Store(id='params_genetic', data={'window_size': None, 'step_size': None, 'bootstrap_amount': None, 'bootstrap_threshold': None, 'ls_threshold': None}),
    html.Div(id='action'),
    html.Div(
        className="getStarted",
        children=[
            html.Div(children=[popup.layout]),
            html.Div(children=[dropFileSection.layout]),
            html.Div([
                html.Div(id="climatic_params_layout"),
                html.Div(id="genetic_params_layout"),
                html.Div(id="submit_button"),
            ], id="params_sections")
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

    for file, name in zip(files, list_of_names):
        if file['type'] == 'genetic':
            current_data['genetic']['file'] = file
            current_data['genetic']['layout'] = paramsGenetic.layout
            current_data['genetic']['name'] = name
        elif file['type'] == 'climatic':
            current_data['climatic']['layout'] = paramsClimatic.create_table(file['df'])
            current_data['climatic']['file'] = file
            current_data['climatic']['file']['df'] = file['df'].to_json()

    return current_data['genetic']['layout'], current_data['climatic']['layout'], submitButton.layout, current_data


@callback(
    Output('params_genetic', 'data'),
    Input('input_windowSize', 'value'),
    Input('bootstrap_threshold', 'value'),
    Input('ls_threshold_slider', 'value'),
    Input('input_stepSize', 'value'),
    Input('bootstrap_amount', 'value'),
    State('params_genetic', 'data'),
    prevent_initial_call=True
)
def params_climatic(window_size, bootstrap_threshold, ls_distance, step_size, bootstrap_amount, current_data):
    current_data['window_size'] = window_size
    current_data['step_size'] = step_size
    current_data['input_stepSize_container'] = step_size
    current_data['bootstrap_threshold'] = bootstrap_threshold
    current_data['ls_threshold'] = ls_distance
    current_data['bootstrap_amount'] = bootstrap_amount
    return current_data

@callback(
    Output('params_climatic', 'data'),
    Input('col-analyze', 'value'),
    State('params_climatic', 'data'),
    prevent_initial_call=True
)
def params_climatic(col_analyze, current_data):
    current_data['names'] = col_analyze
    return current_data

@callback(
    Output('popup', 'className'),
    Output('column_error_message', 'children'),
    Output('name_error_message', 'children'),
    [Input('submit_dataSet', 'n_clicks'),
        Input("close_popup", "n_clicks"),
        Input('input_dataSet', 'value')],
    State('params', 'data'),
    State('params_climatic', 'data'),
    State('params_genetic', 'data'),
    prevent_initial_call=True
)

def submit_button(open, close, input_dataSet, params, params_climatic, params_genetic):
    if open is None or open < 1 or (params['genetic']['file'] is None and params['climatic']['file'] is None):
        raise PreventUpdate

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if (params_climatic['names'] is None or len(params_climatic['names']) < 2) or (input_dataSet is None or not input_dataSet):
        if (params_climatic['names'] is None or len(params_climatic['names']) < 2) and (input_dataSet is not None or input_dataSet):
            return 'popup hidden', dbc.Alert("You need to select at least two columns", color="danger"), ''
        if (params_climatic['names'] is not None and len(params_climatic['names']) >= 2) and (input_dataSet is None or not input_dataSet):
            return 'popup hidden', '', dbc.Alert("You need to give a name to your DataSet", color="danger")
        return 'popup hidden', dbc.Alert("You need to select at least two column", color="danger"), dbc.Alert("You need to give a name to your DataSet", color="danger")

    if trigger_id == "close_popup":
        return 'popup hidden', '', ''

    if trigger_id == "submit_dataSet":
        if params['genetic']['file'] is not None and params['climatic']['file'] is not None:
            files_ids = utils.save_files([params['climatic']['file'], params['genetic']['file']])
            process = multiprocessing.Process(target=utils.run_complete_pipeline, args=(params['climatic']['file']['df'], params['genetic']['file']['file'], params_climatic, params_genetic, input_dataSet, files_ids[0], files_ids[1]))
            process.start()
            return 'popup', '', ''

        elif params['climatic']['file'] is not None:
            files_id = utils.save_files(params['climatic']['file'])
            process = multiprocessing.Process(target=utils.run_climatic_pipeline, args=(params['climatic']['file']['df'], params_climatic, files_id))
            process.start()
            return 'popup', '', ''
    return '', '', ''
