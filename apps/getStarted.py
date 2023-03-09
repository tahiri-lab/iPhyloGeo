from typing import Container
from dash import Dash, html, dcc, ctx
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from app import app
# import pandas as pd
# import pathlib


layout = html.Div([
    html.Div(id='action'),
    html.Div(
        className="getStarted",
        children=[
            html.Div(
            className="ChoiceSection",
            children=[
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
                dbc.NavLink("Next", href='/apps/getStarted', id='themes', className="button actions", active="exact"),
            ],),
            # Drop file section
            html.Div(
                className="DropFileSection",
                children=[
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
                                ], className="dropContainer"),
                                # Allow multiple files to be uploaded
                                multiple=True
                            ),
                            html.Div('Insert my data manually', className="ManualInsertText")
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
                ], ),
        ]
    ),
])

@app.callback(
        Output('meteo', 'className'),
        Output('genetic', 'className'),
        Output('meteoGene', 'className'),
          [Input('meteo', 'n_clicks'),
            Input('genetic', 'n_clicks'),
            Input('meteoGene', 'n_clicks')],
          prevent_initial_call=True,
)

def choose_option(meteo, genetic, meteoGene):
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return ('option selected' if button_id == 'meteo' else 'option',
            'option selected' if button_id == 'genetic' else 'option',
            'option selected' if button_id == 'meteoGene' else 'option')
