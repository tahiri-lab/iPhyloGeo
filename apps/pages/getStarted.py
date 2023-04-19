from dash import dcc, html, State, Input, Output, callback
import dash
from dash.exceptions import PreventUpdate
from dotenv import dotenv_values
from flask import request
import multiprocessing
import dash_bootstrap_components as dbc
import pages.upload.dropFileSection as dropFileSection
import utils.utils as utils
import pages.upload.climatic.paramsClimatic as paramsClimatic
import pages.upload.genetic.paramsGenetic as paramsGenetic
import pages.upload.submitButton as submitButton
import pages.utils.popup as popup

dash.register_page(__name__, path='/getStarted')

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

NUMBER_OF_COLUMNS_ERROR_MESSAGE = "You need to select at least two columns"
NAME_ERROR_MESSAGE = "You need to give a name to your dataset"

layout = html.Div([
    dcc.Store(id='input-data', data={'genetic': {'file': None, 'layout': None, 'name': None}, 'climatic': {'file': None, 'layout': None}, 'submit button': False}),
    dcc.Store(id='params-climatic', data={'names': None}),
    dcc.Store(id='params-genetic', data={'window_size': None, 'step_size': None, 'bootstrap_amount': None, 'bootstrap_threshold': None, 'ls_threshold': None}),
    html.Div(id='action'),
    html.Div(
        className="get-started",
        children=[
            html.Div(children=[popup.layout]),
            html.Div(children=[dropFileSection.layout]),
            html.Div([
                html.Div(id="climatic-params-layout"),
                html.Div(id="genetic-params-layout"),
                html.Div(id="submit-button"),
            ], id="params-sections")
        ]
    ),
])


@callback(
    Output('genetic-params-layout', 'children'),
    Output('climatic-params-layout', 'children'),
    Output('submit-button', 'children'),
    Output('input-data', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    State('input-data', 'data'),
    prevent_initial_call=True,
    log=True
)
def upload_file(list_of_contents, list_of_names, last_modifieds, current_data):
    """
    This function is called when the user uploads one or two files. It stores the data from the files in a json object,
    it creates the layout for the genetic and climatic parameters as needed and it creates the submit button.

    args:
        list_of_contents : list of the contents of the files
        list_of_names : list of the names of the files
        last_modifieds : list of the last modified dates of the files
        current_data : json file containing the current uploaded files. Should be empty at the beginning

    returns:
        paramsGenetic.layout : layout for the genetic parameters
        paramsClimatic.layout : layout for the climatic parameters
        submitButton.layout : layout for the submit button
        current_data : json file containing the current uploaded files

    """
    files = utils.get_files_from_base64(list_of_contents, list_of_names, last_modifieds)

    # if submit button is already here, we don't want to recreate the layout
    submit_button = None
    if not current_data['submit button']:
        current_data['submit button'] = True
        submit_button = submitButton.layout

    for file, name in zip(files, list_of_names):
        if file['type'] == 'genetic':
            current_data['genetic']['file'] = file
            current_data['genetic']['layout'] = paramsGenetic.get_layout(file['file'])
            current_data['genetic']['name'] = name
        elif file['type'] == 'climatic':
            current_data['climatic']['layout'] = paramsClimatic.create_table(file['df'])
            current_data['climatic']['file'] = file
            current_data['climatic']['file']['df'] = file['df'].to_json()

    return current_data['genetic']['layout'], current_data['climatic']['layout'], submit_button, current_data


@callback(
    Output('params-genetic', 'data'),
    Input('input-window-size', 'value'),
    Input('bootstrap-threshold', 'value'),
    Input('ls-threshold-slider', 'value'),
    Input('input-step-size', 'value'),
    Input('bootstrap-amount', 'value'),
    State('params-genetic', 'data'),
    prevent_initial_call=True
)
def params_genetic(window_size, bootstrap_threshold, ls_threshold, step_size, bootstrap_amount, current_data):
    """
    This function fills the params_genetic json object
    args:
        window_size : size of the window for the genetic data
        bootstrap_threshold : threshold for the bootstrap
        ls_threshold : threshold for the least square distance
        step_size : step size for the genetic data
        bootstrap_amount : amount of bootstrap
        current_data : json file containing the current parameters for the genetic data. Should be empty at the beginning

    returns:
        current_data : json file containing the current parameters for the genetic data
    """
    current_data['window_size'] = window_size
    current_data['step_size'] = step_size
    current_data['input_step_size_container'] = step_size
    current_data['bootstrap_threshold'] = bootstrap_threshold
    current_data['ls_threshold'] = ls_threshold
    current_data['bootstrap_amount'] = bootstrap_amount
    return current_data


@callback(
    Output('params-climatic', 'data'),
    Input('col-analyze', 'value'),
    State('params-climatic', 'data'),
    prevent_initial_call=True
)
def params_climatic(column_names, current_data):
    """
    This function fills the params_climatic json object
    args:
        names : names of the columns to use
        current_data : json file containing the current parameters for the climatic data. Should be empty at the beginning

    returns:
        current_data : json file containing the current parameters for the climatic data
    """
    current_data['names'] = column_names
    return current_data


@callback(
    Output('popup', 'className'),
    Output('column-error-message', 'children'),
    Output('name-error-message', 'children'),
    [Input('submit-dataset', 'n_clicks'),
        Input("close_popup", "n_clicks"),
        Input('input-dataset', 'value')],
    State('input-data', 'data'),
    State('params-climatic', 'data'),
    State('params-genetic', 'data'),
    prevent_initial_call=True
)
def submit_button(open, close, result_name, input_data, params_climatic, params_genetic):
    """
    When the submit button is clicked, the data is passed to the aPhyloGeo pipeline. The results are stored in the database or
    the file system depending on the configuration. If the inputs are not valid, an error message is displayed. If the inputs
    are valid, a popup appears to notice the user to not close his window.
    Because the pipeline is a long process, it is executed in a separate process (multiprocessing).

    args:
        open : counter of the submit button
        close : counter of the close button - not used but necessary
        result_name : name of the results that will be generated
        input_data : json file containing the data from the uploaded files
        params_climatic : parameters for the climatic data
        params_genetic : parameters for the genetic data

    returns:
        className : class of the popup if the inputs are valid
        column-error-message : NUMBER_OF_COLUMNS_ERROR_MESSAGE if the number of columns is not valid
        name_error_message : NAME_ERROR_MESSAGE if the name of the results is not valid
    """
    files_are_present = input_data['genetic']['file'] is not None or input_data['climatic']['file'] is not None

    if open is None or open < 1 or not files_are_present:
        raise PreventUpdate

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "close_popup":
        return 'popup hidden', '', ''

    result_name_is_valid = result_name is not None or result_name
    params_climatic_is_complete = params_climatic['names'] is not None and len(params_climatic['names']) >= 2

    if not params_climatic_is_complete and result_name_is_valid:
        return 'popup hidden', dbc.Alert(NUMBER_OF_COLUMNS_ERROR_MESSAGE, color="danger"), ''
    if params_climatic_is_complete and not result_name_is_valid:
        return 'popup hidden', '', dbc.Alert(NAME_ERROR_MESSAGE, color="danger")
    if not params_climatic_is_complete and not result_name_is_valid:
        return 'popup hidden', dbc.Alert(NUMBER_OF_COLUMNS_ERROR_MESSAGE, color="danger"), dbc.Alert(NAME_ERROR_MESSAGE, color="danger")

    if trigger_id != "submit-dataset":
        return '', '', ''

    climatic_file = input_data['climatic']['file']
    genetic_file = input_data['genetic']['file']

    result_type = []
    files_ids = {}
    if climatic_file is not None:
        result_type.append('climatic')
        climatic_file_id = utils.save_files(climatic_file)
        files_ids['climatic_files_id'] = climatic_file_id

    if genetic_file is not None:
        result_type.append('genetic')
        genetic_file_id = utils.save_files(genetic_file)
        files_ids['genetic_files_id'] = genetic_file_id

    try:
        # create a new result in the database
        result_id = utils.create_result(files_ids, result_type, params_climatic, params_genetic, result_name)
        if ENV_CONFIG['HOST'] != 'local':
            add_result_to_cookie(result_id)

        climatic_status = 'climatic_trees' if 'genetic' in result_type else 'complete'

        # add climatic
        climatic_trees = utils.create_climatic_trees(result_id, climatic_file['df'], params_climatic, climatic_status)

        if 'genetic' not in result_type:
            return 'popup', '', ''

        genetic_filename = input_data['genetic']['name']

        process = multiprocessing.Process(target=utils.run_genetic_pipeline,
                                          args=(result_id, climatic_file['df'], genetic_file['file'],
                                                params_genetic, genetic_filename, climatic_trees))
        process.start()
        return 'popup', '', ''
    except Exception as e:
        # TODO: print error message popup
        print('[Error]:', e)
        return 'popup', '', ''


def add_result_to_cookie(result_id):
    """
    Creates a cookie (AUTH) that contains the id of the result.

    args:
        result_id : id of the result

    """
    auth_cookie = request.cookies.get("AUTH")
    response = dash.callback_context.response
    utils.make_cookie(result_id, auth_cookie, response)
