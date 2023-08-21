from dash import dcc, html, Output, Input, callback  # , State
import dash


dash.register_page(__name__, path='/settings')

layout = html.Div([
    html.Div(style={'margin': '0 300px'}, children=[
        # Header
        html.Div([
            html.H1("Settings", className="text-center", style={'color': 'white', 'font-weight': 'bold'})  # Title centered
        ], className="header"),

        # Input parameters
        html.Div([
            html.Div([
                html.Label("Bootstrap value threshold"),
                dcc.Input(id='bootstrap-value-threshold', type='number', value=10, className="custom-input"),
            ], className="input-wrapper"),

            html.Div([
                html.Label("Sliding Window Size:"),
                dcc.Input(id='window-size', type='number', value=200, className="custom-input"),
            ], className="input-wrapper"),

            html.Div([
                html.Label("Step Size:"),
                dcc.Input(id='step-size', type='number', value=100, className="custom-input"),
            ], className="input-wrapper"),

            html.Div([
                html.Label("Bootstrap amount :"),
                dcc.Input(id='bootstrap-amount', type='number', value=100, className="custom-input"),
            ], className="input-wrapper"),

            html.Div([
                html.Label("LS Threshold:"),
                dcc.Input(id='ls-threshold', type='number', value=50, className="custom-input"),
            ], className="input-wrapper"),

            html.Div([
                html.Label("Starting Position:"),
                dcc.Input(id='starting-position', type='number', value=0, className="custom-input"),
            ], className="input-wrapper"),

            html.Div([
                html.Label("Sliding Window (0-1500):"),
                dcc.Input(id='sliding-window', type='number', value=750, min=0, max=1500, className="custom-input"),
            ], className="input-wrapper"),

            # Repeat the above pattern for the other input parameters
        ], className="settings"),

        # Button to reset parameters
        html.Button("Reset to Defaults", id="reset-button", n_clicks=0, className="custom-button"),

        # Store to save values
        dcc.Store(id="parameter-store", storage_type="local")
    ])
])


# Callback to update the stored parameters
@callback(
    Output("bootstrap-value-threshold", "value"),
    Output("window-size", "value"),
    Output("step-size", "value"),
    Output("bootstrap-amount", "value"),
    Output("ls-threshold", "value"),
    Output("starting-position", "value"),
    Output("sliding-window", "value"),
    Input("reset-button", "n_clicks"),
    prevent_initial_call=True
)
def update_parameters(reset_button_clicks):
    if reset_button_clicks > 0:
        default_values = {
            "bootstrap_value_threshold": 10,
            "window_size": 200,
            "step_size": 100,
            "bootstrap_amount": 100,
            "ls_threshold": 50,
            "starting_position": 0,
            "sliding_window": 750
        }
        return (
            default_values["bootstrap_value_threshold"],
            default_values["window_size"],
            default_values["step_size"],
            default_values["bootstrap_amount"],
            default_values["ls_threshold"],
            default_values["starting_position"],
            default_values["sliding_window"]
        )

    raise dash.exceptions.PreventUpdate
