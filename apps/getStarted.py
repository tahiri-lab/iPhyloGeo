from typing import Container
from dash import Dash, html, dcc, ctx
from dash.dependencies import Output, Input, ClientsideFunction
import dash_bootstrap_components as dbc
from app import app
# import pandas as pd
# import pathlib


layout = html.Div([
    html.Div(id='action'),
    html.Div(id='option_position'),
    html.Div(
        className="getStarted",
        children=[
            html.Div(
                children=[
                    html.Div([
                        html.Div('How are you going to change the world today ?', className="title"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Img(src='../assets/icons/meteorological.svg', className="img"),
                                ], className="optionImage"),
                                    html.Div('Upload Meteorological data', className="title"),
                                    html.Div('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.', className="description"),
                                ], id='meteo', className="option"),
                            html.Div([
                                html.Div([
                                    html.Img(src='../assets/icons/genetic.svg', className="img"),
                                ], className="optionImage"),
                                html.Div('Upload Genetic data', className="title"),
                                html.Div('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.', className="description"),
                            ], id='genetic', className="option"),
                           html.Div([
                                html.Div([
                                    html.Img(src='../assets/icons/meteo-genetic.svg', className="img"),
                                ], className="optionImage"),
                                html.Div('Upload Meteorological and Genetic data', className="title"),
                                html.Div('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.', className="description"),
                            ], id='meteoGene', className="option"),
                        ], id='options', className="container"),
                        html.Div("Next", id='option_choice', className="button actions"),
                    ], className="choiceSectionInside"),
                ],
            className="ChoiceSection"),
            # Drop file section
            html.Div(
                children=[
                    html.Div([
                        html.Div('Please drop your file right here', className="title"),
                        html.Div([
                            html.Div([
                                dcc.Upload(
                                    id='upload-data',
                                    children=html.Div([
                                        html.A([
                                            html.Img(src='../assets/icons/folder-drop.svg', className="icon"),
                                            html.Div('Drag and Drop or Select Files', className="text"),
                                        ], className="dropContent"),
                                    ], className="dropContainer", id="dropContainer"),
                                    # Allow multiple files to be uploaded
                                    multiple=True
                                ),
                                html.Div([
                                    dcc.Textarea(
                                        cols='60', rows='8',
                                        value='Textarea content initialized\nwith multiple lines of text',
                                        className="textArea hidden", id='manualField'
                                    ),
                                ],),
                                html.Div('Insert my data manually', id="manualInsert", className="ManualInsertText")
                            ], className="dropZone"),
                        ], id='options', className="container"),
                        dbc.NavLink([
                            html.Div([
                                html.Div('Don’t know where to start ?', className="title"),
                                html.Div('No worries, let’s try with some of our already made example.',
                                         className="description"),
                            ], className="content"),
                            html.Img(src='../assets/icons/arrow-circle-right.svg', className="icon"),
                            ], href='/apps/getStarted', id='themes', className="helper primary", active="exact"),
                        html.Div([
                            html.Div("Previous", id='drop_prev', className="button actions"),
                            html.Div("Next", id='option_choice', className="button actions"),
                        ], className="buttonPack"),

                    ], className="DropFileSectionInside"),
                ],
            className="DropFileSection", id="DropFileSection"),
            # Params
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
                                html.Div([
                                    html.Div("Sliding Window Size"),
                                    dcc.Input(id="input_windowSize", type="number", min=0, max= 10,
                                              placeholder="Enter Sliding Window Size", value=0,
                                              style={'width': '65%', 'marginRight': '20px'}),
                                    html.Div(id='input_windowSize-container1'),
                                ]),
                            ], className="ParameterContainerInside"),
                            html.Div([
                                html.Div("Step Size"),
                                dcc.Input(id="input_stepSize", type="number", min=0, max= 10,
                                          placeholder="Enter Step Size", value=0,
                                          style={'width': '65%', 'marginRight': '20px'}),
                                html.Div(id='input_stepSize-container1'),
                            ], className="ParameterContainerInside"),
                        ], className="ParameterContainer"),
                        html.Div("Submit", className="button actions"),
                    ], className="ParametersSectionInside"),
                ],className="ParametersSection", id="ParametersSection"
            ),
        ]
    ),
])

@app.callback(
        Output('meteo', 'className'),
        Output('genetic', 'className'),
        Output('meteoGene', 'className'),
        Output('ParametersSection', 'className'), # showing or not the params section
          [Input('meteo', 'n_clicks'),
            Input('genetic', 'n_clicks'),
            Input('meteoGene', 'n_clicks')],
          prevent_initial_call=True,
)

def choose_option(meteo, genetic, meteoGene):
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return ('option selected' if button_id == 'meteo' else 'option',
            'option selected' if button_id == 'genetic' else 'option',
            'option selected' if button_id == 'meteoGene' else 'option',
            'ParametersSection hidden' if button_id == 'meteo' else 'ParametersSection')

# @app.callback(
#     Output('BootstrapThreshold-slider-output-container1', 'children'),
#     [Input('BootstrapThreshold-slider1', 'value')])
# def update_output(value):
#     return '{:0.1f}%'.format(value)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='show_text_field'
    ),
    Output("manualField", "children"), # needed for the callback to trigger
    Input("manualInsert", "n_clicks"),
    prevent_initial_call=True,
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='next_option_function'
    ),
    Output("option_position", "children"), # needed for the callback to trigger
    [Input("option_choice", "n_clicks"),
     Input("drop_prev", "n_clicks"),],
    prevent_initial_call=True,
)