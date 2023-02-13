from typing import Container
from dash import Dash, html, dcc
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import pathlib

# Font Awesome
import plotly.express as px
import plotly.graph_objs as go

# app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v6.1.1/css/all.css'])

external_stylesheets = [
{
    'href': 'https://use.fontawesome.com/releases/v6.1.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}
]

# get relative data folder
#PATH = pathlib.Path(__file__).parent
#IMG_PATH = PATH.joinpath("../assets").resolve()

#dfg = pd.read_csv(DATA_PATH.joinpath("theData_IfWeHave.csv"))

app = Dash(__name__)

layout = html.Div([
    html.Div(
        className="home-page",
        children=[
            html.Video(src='../assets/indexPhylogeo.mp4', autoPlay=True, loop=True, muted=True, controls=False, className="home-page__video"),
            html.Div(
            className="main-text",
            children=[
                html.Div('Welcome to the Tahiri Lab', className="title"),
                html.Div(['We are a dynamic research group at the Sherbrooke University, Department of Computer Science. ',
                html.A(['Learn more',
                    html.ObjectEl(id='icon', data='../assets/icons/up-right-from-square-solid.svg', type="image/svg+xml", className='icon')
                    ], target='_blank', href='https://tahirinadia.github.io/', className="url"),
                ], className="sub-title"),
                html.Div('Get Started', className="button primary"),
                ]
            ),
        ]
    ),
    html.Div(
        children=html.Div([
            html.H5('Overview'),
            html.Div('''
                Testing
            ''')
        ])
    )
])
