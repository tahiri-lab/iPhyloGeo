import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import os
import dash_extensions as de

#-----------------------------------------
card1 = dbc.Card(
    [
        #dbc.CardImg(src="/assets/climate.jpg", top=True),
        de.Lottie(options=dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice')), 
                    width="50%", height="25%", 
                    url="https://assets5.lottiefiles.com/packages/lf20_dcoytsm3.json"),
        dbc.CardBody(
            [
                html.H4("Add meteorological data", className="card-title"),
                dbc.CardLink("Add dataset", href="addMeteo"),
            ]
        ),
    ],
    #style={"width": "45%"},
),

card2 = dbc.Card(
    [
        #dbc.CardImg(src="/assets/dna.jpg", top=True),
        de.Lottie(options=dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice')), 
                    width="50%", height="30%", 
                    url="https://assets5.lottiefiles.com/packages/lf20_cftvyhwc.json"),
        dbc.CardBody(
            [
                html.H4("Add genetic data", className="card-title"),
               
                dbc.CardLink("Add dataset", href="addGene"),
            ]
        ),
    ],
    #style={"width": "45%"},
),
#-------------------------------------------
layout = dbc.Container([
    #html.H1('Phylogenetic Tree', style={"textAlign": "center"}),  #title
    dbc.Row([
            dbc.Col([
                html.Div(card1),
            ],xs=12, sm=12, md=12, lg=6, xl=6),
            dbc.Col([
                html.Div(card2),
            ],xs=12, sm=12, md=12, lg=6, xl=6),

         ],justify='around'),
    
], fluid=True)

