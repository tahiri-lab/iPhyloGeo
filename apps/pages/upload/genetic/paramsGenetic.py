from dash import dcc, html, no_update, Output, Input, callback
from pprint import pprint
from Bio import SeqIO
import dash_bio as dashbio
import dash

def get_layout(file):
    return html.Div(
        children=[
            html.Div([
                html.Div([
                    dcc.Store(id='stored-data', data=file),
                    html.Div('Genetic parameters', className="title"),
                    html.Div([
                        html.Div("Bootstrap value threshold", className="param-title"),
                        dcc.Slider(id='bootstrap-threshold', className="slider",
                                min=0, max=100, step=0.1,
                                marks={
                                    0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                                    25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                                    50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                                    75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                                    100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}},
                                value=10),
                        html.Div(id='bootstrap-threshold-output-container')
                    ], className="parameter-container-inside"),
                    html.Div([
                        html.Div('Ls Threshold', className="param-title"),
                        dcc.Slider(id='ls-threshold-slider', className="slider",
                                min=0, max=100, step=0.1,
                                marks={
                                    0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                                    25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                                    50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                                    75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                                    100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}},
                                value=60),
                        html.Div(id='ls-threshold-slider-output-container'),
                    ], className="parameter-container-inside"),
                    html.Div([
                        html.Div([
                            html.Div("Sliding Window Size"),
                            dcc.Input(id="input-window-size", type="number", min=0, max=500,
                                    placeholder="Enter Sliding Window Size", value=200, className="input-field"),
                            html.Div(id='input-window-size-container'),
                        ], className="manual-input"),
                        html.Div([
                            html.Div("Step Size"),
                            dcc.Input(id="input-step-size", type="number", min=0, max=500,
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
                            html.Div("Starting Position"),
                            dcc.Input(id="starting-position", type="number", min=0, max=1200,
                                    placeholder="Enter Starting Position", value=100, className="input-field"),
                            html.Div(id='starting-position-container'),
                        ], className="manual-input"),
                        html.Div([
                            html.Div(id='alignment-chart'),
                        ]),
                    ], className="manual-input-container")
                ], className="parameter-container", id="genetic-params-section",),
            ], className="params-genetic"),
        ], className="parameters-section", id="parameters-section"
    )


@callback(
    Output('alignment-chart', 'children'),
    Input('starting-position', 'value'),
    Input('input-window-size', 'value'),
    Input('stored-data', 'data'),
)
def make_alignment_chart(starting_position, window_size, file):
    if starting_position is None:
        return dash.no_update        
    end_window= starting_position + window_size    
    genetic_values = ""
    for key,value in file.items():
        genetic_values +='>'+ key + '\n'
        genetic_values +=str(value[int(starting_position):int(end_window)])+'\n'
    return html.Div([
                dashbio.AlignmentChart(
                    id='my-alignment-viewer',
                    data=genetic_values,
                    tilewidth=30,
                    height=900,
                ),
                html.Br(),
                html.Br(),
                html.Div(id='alignment-viewer-output'),
            ])
    
