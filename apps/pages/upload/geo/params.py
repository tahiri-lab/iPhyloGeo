import dash_bootstrap_components as dbc

from dash import dcc, html, State, Input, Output
import dash_daq as daq
from dash.dependencies import Input, Output, ClientsideFunction


layout = html.Div([
    html.Div(children=[
        html.Div(
            children=[
                html.Div([
                    html.Div('Parameters', className="title"),
                    html.Div([
                        html.Div([
                            html.Div("Bootstrap value threshold", className="paramTitle"),
                            dcc.Slider(id='BootstrapThreshold-slider1', className="slider",
                                       min=0, max=100, step=0.1,
                                       marks={
                                           0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                                           25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                                           50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                                           75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                                           100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}},
                                       value=10),
                            html.Div(id='BootstrapThreshold-slider-output-container1')
                        ], className="ParameterContainerInside"),
                        html.Div([
                            html.Div('Robinson and Foulds distance threshold', className="paramTitle"),
                            dcc.Slider(id='RF-distanceThreshold-slider', className="slider",
                                       min=0, max=100, step=0.1,
                                       marks={
                                           0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                                           25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                                           50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                                           75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                                           100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}},
                                       value=10),
                            html.Div(id='RFThreshold-slider-output-container'),
                        ], className="ParameterContainerInside"),
                        html.Div([
                                html.Div("Sliding Window Size"),
                                dcc.Input(id="input_windowSize", type="number", min=0, max=10,
                                          placeholder="Enter Sliding Window Size", value=0,
                                          style={'width': '65%', 'marginRight': '20px'}),
                                html.Div(id='input_windowSize-container1'),
                        ], className="ParameterContainerInside"),
                        html.Div([
                            html.Div("Step Size"),
                            dcc.Input(id="input_stepSize", type="number", min=0, max=10,
                                      placeholder="Enter Step Size", value=0,
                                      style={'width': '65%', 'marginRight': '20px'}),
                            html.Div(id='input_stepSize-container1'),
                        ], className="ParameterContainerInside"),
                    ], className="ParameterContainer", id="geo_params_section",),
                ], className="ParametersSectionInside"),
            ], className="ParametersSection", id="ParametersSection"
        ),
    ],),
],)