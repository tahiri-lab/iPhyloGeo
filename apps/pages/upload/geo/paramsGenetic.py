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
                            dcc.Slider(id='bootstrap_threshold', className="slider",
                                       min=0, max=100, step=0.1,
                                       marks={
                                           0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                                           25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                                           50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                                           75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                                           100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}},
                                       value=10),
                            html.Div(id='bootstrap_threshold_output_container')
                        ], className="ParameterContainerInside"),
                        html.Div([
                            html.Div('Ls Threshold', className="paramTitle"),
                            dcc.Slider(id='ls_threshold_slider', className="slider",
                                       min=0, max=100, step=0.1,
                                       marks={
                                           0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                                           25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                                           50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                                           75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                                           100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}},
                                       value=10),
                            html.Div(id='ls_threshold_slider_output_container'),
                        ], className="ParameterContainerInside"),
                        html.Div([
                                html.Div("Sliding Window Size"),
                                dcc.Input(id="input_windowSize", type="number", min=0, max=10,
                                          placeholder="Enter Sliding Window Size", value=0,
                                          style={'width': '65%', 'marginRight': '20px'}),
                                html.Div(id='input_windowSize_container'),
                        ], className="ParameterContainerInside"),
                        html.Div([
                            html.Div("Step Size"),
                            dcc.Input(id="input_stepSize", type="number", min=0, max=10,
                                      placeholder="Enter Step Size", value=0,
                                      style={'width': '65%', 'marginRight': '20px'}),
                            html.Div(id='input_stepSize_container'),
                        ], className="ParameterContainerInside"),
                        html.Div([
                            html.Div("Bootstrap amount"),
                            dcc.Input(id="bootstrap_amount", type="number", min=0, max=500,
                                      placeholder="Enter Step Size", value=0,
                                      style={'width': '65%', 'marginRight': '20px'}),
                            html.Div(id='bootstrap_amount_container'),
                        ], className="ParameterContainerInside"),
                    ], className="ParameterContainer", id="geo_params_section",),
                ], className="ParametersSectionInside"),
            ], className="ParametersSection", id="ParametersSection"
        ),
    ],),
],)