from dash import dcc, html, Output, Input, callback  # , State
import dash_bio as dashbio
import dash


def get_layout(file):
    max_sequence_length = get_max_sequence_length(file)
    first_quartile = int(0.25 * max_sequence_length)
    second_quartile = int(0.5 * max_sequence_length)
    third_quartile = int(0.75 * max_sequence_length)
    print(max_sequence_length)
    return html.Div(
        children=[
            html.Div([
                dcc.Store(id="sync", data={"starting_position": 0, "window_size": 200}),
                html.Div([
                    dcc.Store(id='stored-genetic-data', data=file),
                    html.Div('Genetic parameters', className="title"),
                    html.Div([
                        html.Div("Bootstrap value threshold", className="param-title"),
                        dcc.Slider(id='bootstrap-threshold', className="slider", min=0, max=100, step=0.1,
                                   marks={
                                      0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                                      25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                                      50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                                      75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                                      100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}}, value=10),
                        html.Div(id='bootstrap-threshold-output-container')
                    ], className="parameter-container-inside"),
                    html.Div([
                        html.Div('LS Threshold', className="param-title"),
                        dcc.Slider(id='ls-threshold-slider', className="slider", min=0, max=100, step=0.1,
                                   marks={
                                      0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                                      25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                                      50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                                      75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                                      100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}}, value=60),
                        html.Div(id='ls-threshold-slider-output-container'),
                    ], className="parameter-container-inside"),
                    html.Div([
                        html.Div([
                            html.Div("Sliding Window Size"),
                            dcc.Input(id="input-window-size", type="number", min=0, max=max_sequence_length,
                                      placeholder="Enter Sliding Window Size", value=200, className="input-field"),
                            html.Div(id='input-window-size-container'),
                        ], className="manual-input"),
                        html.Div([
                            html.Div("Step Size"),
                            dcc.Input(id="input-step-size", type="number", min=0, max=max_sequence_length,
                                      placeholder="Enter Step Size", value=100, className="input-field"),
                            html.Div(id='input-step-size-container'),
                        ], className="manual-input"),
                        html.Div([
                            html.Div("Bootstrap amount"),
                            dcc.Input(id="bootstrap-amount", type="number", min=1, max=500,
                                      placeholder="Enter Step Size", value=100, className="input-field"),
                            html.Div(id='bootstrap-amount-container'),
                        ], className="manual-input"),
                        html.Div([
                            html.Div("Starting position"),
                            dcc.Input(id="input-starting-position", type="number", min=0, max=max_sequence_length,
                                      placeholder="Enter the starting position", value=0, className="input-field"),
                            html.Div(id='bootstrap-amount-container'),
                        ], className="manual-input"),
                    ], className="manual-input-container"),
                    html.Div([
                        html.Div("Sliding Window", className='sub-title'),
                        dcc.RangeSlider(id='sliding-window-slider', className="slider", min=0, max=max_sequence_length, step=1,
                                        marks={
                                            0: {'label': '0', 'style': {'color': '#77b0b1'}},
                                            first_quartile: {'label': str(first_quartile), 'style': {'color': '#77b0b1'}},
                                            second_quartile: {'label': str(second_quartile), 'style': {'color': '#77b0b1'}},
                                            third_quartile: {'label': str(third_quartile), 'style': {'color': '#77b0b1'}},
                                            max_sequence_length: {'label': str(max_sequence_length), 'style': {'color': '#77b0b1'}}},
                                        ),
                        html.Div(id='sliding-window-slider-output-container')
                    ]),
                    html.Div([
                        html.Div([
                            html.Div("Alignement chart", className='sub-title'),
                            html.Div(id='alignment-chart'),
                        ]),
                    ]),
                ], className="parameter-container", id="genetic-params-section",),
            ], className="params-genetic"),
        ], className="parameters-section", id="parameters-section"
    )


@callback(
    Output('alignment-chart', 'children'),
    Input('input-starting-position', 'value'),
    Input('input-window-size', 'value'),
    Input('stored-genetic-data', 'data'),
)
def make_alignment_chart(starting_position, window_size, file):
    """
    This function creates the alignment chart
    args:
        starting_position (int): starting position of the alignment chart
        window_size (int): size of the window
        file (dict): dictionary containing the sequences
    """
    if starting_position is None:
        return dash.no_update
    end_window = starting_position + window_size
    genetic_values = ""
    for key, value in file.items():
        genetic_values += '>' + key + '\n'
        genetic_values += str(value[int(starting_position):int(end_window)]) + '\n'
    return html.Div([
        dashbio.AlignmentChart(
            id='my-alignment-viewer',
            data=genetic_values,
            tilewidth=20,
            height=600,
        ),
        html.Div(id='alignment-viewer-output', className='alignment-chart'),
    ])

# TODO: fix the bug with dash 2.9 and multiprocessing
# the following callbacks are using allow_duplicate=True, which is a new feature in dash 2.9.0
# When running the code with dash 2.9.0, the pipeline can't run in a windows environment (because multiprocessing is not supported)
# We chose to comment the code for now, to make sure the code can run on windows, but it can be uncommented when running on linux (just make sure to install dash 2.9.0 or higher)

# @callback(
#     Output("sync", "data", allow_duplicate=True),
#     Input("input-starting-position", "value"),
#     State("sync", "data"),
#     prevent_initial_call=True
# )
# def sync_starting_position_value(value, current_data):
#     """
#     Function to sync the starting position value with it's associated slider (sliding-window-slider)
#     args:
#         value: the new value of the starting position
#         current_data (dict) : the current data
#     returns:
#         current_data (dict) : the updated data
#     """
#     current_data["starting_position"] = value
#     return current_data


# @callback(
#     Output("sync", "data", allow_duplicate=True),
#     Input("input-window-size", "value"),
#     State("sync", "data"),
#     prevent_initial_call=True
# )
# def sync_window_size_value(value, current_data):
#     """
#     Function to sync the window size value with it's associated slider (sliding-window-slider)
#     args:
#         value: the new value of the window size
#         current_data (dict) : the current data
#     returns:
#         current_data (dict) : the updated data
#     """
#     current_data["window_size"] = value
#     return current_data


# @callback(
#     Output("sync", "data", allow_duplicate=True),
#     Input("sliding-window-slider", "value"),
#     State("sync", "data"),
#     prevent_initial_call=True
# )
# def sync_slider_value(value, current_data):
#     """
#     function to sync the slider value with it's associated inputs (input-window-size and input-starting-position)
#     args:
#         value: the new value of the slider
#         current_data (dict) : the current data
#     returns:
#         current_data (dict) : the updated data
#     """
#     current_data["starting_position"] = value[0]
#     current_data["window_size"] = value[1] - value[0]
#     return current_data


# @callback(
#     Output("input-window-size", "value"),
#     Output("input-starting-position", "value"),
#     Output("sliding-window-slider", "value"),
#     Input("sync", "data"),
#     State("input-window-size", "value"),
#     State("input-starting-position", "value"),
#     State("sliding-window-slider", "value")
# )
# def update_components(current_value, window_size_prev, starting_position_prev, slider_prev):
#     """
#     This function updates the components (input-window-size, input-starting-position and sliding-window-slider) only if needed. The function is
#     complex because it has a bidirectional synchronization between the components. The soltion is based on the following reference:
#     https://community.plotly.com/t/synchronize-components-bidirectionally/14158/10
#     args:
#         current_value: dictionary with the current values
#         window_size_prev: previous value of the window size
#         starting_position_prev: previous value of the starting position
#         slider_prev: previous value of the slider
#     returns:
#         window_size: the new value of the window size
#     """
#     window_size = current_value["window_size"] if current_value["window_size"] != window_size_prev else dash.no_update
#     starting_position = current_value["starting_position"] if current_value["starting_position"] != starting_position_prev else dash.no_update
#     current_slider = [current_value["starting_position"], current_value["starting_position"] + current_value["window_size"]]
#     slider = current_slider if current_slider != slider_prev else dash.no_update
#     return window_size, starting_position, slider


def get_max_sequence_length(file):
    """
    This function returns the maximum length of the sequences
    args:
        file: dictionary with the sequences
    returns:
        max_sequence_length: the maximum length of the sequences
    """
    max_sequence_length = 0
    for value in file.values():
        if len(value) > max_sequence_length:
            max_sequence_length = len(value)
    return max_sequence_length
