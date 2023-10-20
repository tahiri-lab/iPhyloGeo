
import json

from dash import dcc, html, Output, Input, callback, State, ctx
import dash
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path='/settings')

BOOTSTRAP_THRESHOLD_MIN = 0
BOOTSTRAP_THRESHOLD_MAX = 100
DISTANCE_THRESHOLD_MIN = 0
DISTANCE_THRESHOLD_MAX = 100
BOOTSTRAP_AMOUNT_MIN = 0
BOOTSTRAP_AMOUNT_MAX = 100
WINDOW_SIZE_MIN = 1
WINDOW_SIZE_MAX = 1500
STEP_SIZE_MIN = 1
STEP_SIZE_MAX = 1500
STARTING_POSITION_MIN = 1
STARTING_POSITION_MAX = 1500

genetic_settings_file = json.load(open('genetic_settings_file.yaml', 'r'))

layout = html.Div([
    dcc.Store(id='genetic-settings', storage_type='session',
              data=genetic_settings_file),
    html.Div(id='main-container', style={'margin': '0 150px'}, children=[
        html.Div([
            html.Div('Genetic parameters', className="title"),
            html.Div([
                html.Div([
                    # ----- Bootstrap value threshold -----
                    html.Div("Bootstrap threshold"),
                    dcc.Input(id="bootstrap-threshold", type="number",
                              min=BOOTSTRAP_THRESHOLD_MIN, max=BOOTSTRAP_THRESHOLD_MAX,
                              value=genetic_settings_file['bootstrap-threshold'], className="input-field"),
                    html.Div(id='bootstrap-value-threshold-container'),
                ], className="manual-input"),
                html.Div([
                    # ----- Distance threshold -----
                    html.Div("Distance threshold"),
                    dcc.Input(id="distance-threshold", type="number",
                              min=DISTANCE_THRESHOLD_MIN, max=DISTANCE_THRESHOLD_MAX,
                              value=genetic_settings_file['distance-threshold'], className="input-field"),
                ], className="manual-input"),
                html.Div([
                    # ----- Sliding window size -----
                    html.Div("Sliding Window Size"),
                    dcc.Input(id="input-window-size", type="number",
                              min=WINDOW_SIZE_MIN, max=WINDOW_SIZE_MAX,
                              value=genetic_settings_file['window-size'], className="input-field"),
                    html.Div(id='input-window-size-container'),
                ], className="manual-input"),
                html.Div([
                    # ----- Step size -----
                    html.Div("Step Size"),
                    dcc.Input(id="input-step-size", type="number",
                              min=STEP_SIZE_MIN, max=STEP_SIZE_MAX,
                              value=genetic_settings_file['step-size'], className="input-field"),
                    html.Div(id='input-step-size-container'),
                ], className="manual-input"),
                html.Div([
                    # ----- Bootstrap amount -----
                    html.Div("Bootstrap amount"),
                    dcc.Input(id="bootstrap-amount", type="number",
                              min=BOOTSTRAP_AMOUNT_MIN, max=BOOTSTRAP_AMOUNT_MAX,
                              value=genetic_settings_file['bootstrap-amount'], className="input-field"),
                    html.Div(id='bootstrap-amount-container'),
                ], className="manual-input"),
                html.Div([
                    # ----- Starting position -----
                    html.Div("Starting position"),
                    dcc.Input(id="input-starting-position", type="number",
                              min=STARTING_POSITION_MIN, max=STARTING_POSITION_MAX,
                              value=genetic_settings_file['starting-position'], className="input-field"),
                    html.Div(id='starting-position-container'),
                ], className="manual-input"),
            ], className="manual-input-container"),
                html.Div(id='setting-buttons', children=[
                    # Button to reset settings to default
                    html.Button("Reset to default", id="reset-button", n_clicks=0),

                    # Button to save settings
                    html.Button("Save settings", id="save-settings-button", n_clicks=0)
                ])
        ], className="parameter-container"),
    ], className="params-genetic")
])


# Update settings on the form
@callback(
    Output('bootstrap-threshold', 'value'),
    Output('distance-threshold', 'value'),
    Output('input-window-size', 'value'),
    Output('input-step-size', 'value'),
    Output('bootstrap-amount', 'value'),
    Output('input-starting-position', 'value'),
    Input('genetic-settings', 'data')
)
def update_settings(settings):
    return (settings['bootstrap-threshold'],
            settings['distance-threshold'],
            settings['window-size'],
            settings['step-size'],
            settings['bootstrap-amount'],
            settings['starting-position'])


# To reset or save the settings in the YAML file
@callback(
    Output('genetic-settings', 'data'),
    Input("reset-button", "n_clicks"),
    Input('save-settings-button', 'n_clicks'),
    State('bootstrap-threshold', 'value'),
    State('distance-threshold', 'value'),
    State('input-window-size', 'value'),
    State('input-step-size', 'value'),
    State('bootstrap-amount', 'value'),
    State('input-starting-position', 'value'),
    prevent_initial_call=True
)
def update_parameters(reset_button_clicks, save_settings_button_clicks, bootstrap_threshold, distance_threshold, window_size, step_size, bootstrap_amount, starting_position):

    settings_out_of_bound = (bootstrap_threshold is None or distance_threshold is None or window_size is None or step_size is None or bootstrap_amount is None or starting_position is None)

    button_clicked = ctx.triggered_id

    if button_clicked == 'reset-button':
        default_values = {
            "bootstrap-threshold": 10,
            "distance-threshold": 50,
            "window-size": 200,
            "step-size": 100,
            "bootstrap-amount": 100,
            "starting-position": 1
        }

        with open('genetic_settings_file.yaml', 'w') as f:
            json.dump(default_values, f)

        return default_values

    elif button_clicked == 'save-settings-button' and not settings_out_of_bound:
        genetic_settings_yaml = {
            'bootstrap-threshold': bootstrap_threshold,
            'distance-threshold': distance_threshold,
            'window-size': window_size,
            'step-size': step_size,
            'bootstrap-amount': bootstrap_amount,
            'starting-position': starting_position
        }

        with open('genetic_settings_file.yaml', 'w') as f:
            json.dump(genetic_settings_yaml, f)

        return genetic_settings_yaml

    raise PreventUpdate
