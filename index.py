# from importlib.abc import Traversable
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import Input, Output
#from dash import dash_bootstrap_components as dbc
import tree
import pipeline

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import *
from apps import homePage
# from apps import pipelineWithOurData
from apps import pipelineWithUploadedData
from apps import upload_MeteorologicalDataset
from apps import checkResults
from apps import usingOurMeteorologicalDataset
# pipelineWithOurData, pipelineWithUploadedData, upload_MeteorologicalDataset, homePage, checkResults, usingOurMeteorologicalDataset



# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "26rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "25rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Tahiri Lab", className="display-4"),
        html.Hr(),
        html.H3(
            "Phylogeography", className='text-center text-primary mb-3'
        ),
        dbc.Nav(
            [dbc.NavLink("Home", href='/apps/homePage', active="exact"),
            dbc.NavLink("Climatic Dataset", href='/apps/upload_MeteorologicalDataset', active="exact"),
            dbc.NavLink("Genetic Dataset", href='/apps/pipelineWithUploadedData', active="exact"),
            dbc.NavLink("Sample Climatic Dataset (yellow-legged hornet)", href='/apps/usingOurMeteorologicalDataset', active="exact"),
            # dbc.NavLink("Phylogeography Analysis With Sample Genetic Dataset (yellow-legged hornet)", href='/apps/pipelineWithOurData', active="exact"),
            dbc.NavLink("Results", href='/apps/checkResults', active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])



@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/homePage': 
        return homePage.layout
    if pathname == '/apps/upload_MeteorologicalDataset': 
        return upload_MeteorologicalDataset.layout
    if pathname == '/apps/pipelineWithUploadedData':
        return pipelineWithUploadedData.layout
    if pathname == '/apps/usingOurMeteorologicalDataset': 
        return usingOurMeteorologicalDataset.layout
    if pathname == '/apps/pipelineWithOurData':
        return pipelineWithOurData.layout
    if pathname == '/apps/checkResults':
        return checkResults.layout
    else:
        return homePage.layout 


if __name__ == '__main__':
    app.run_server(debug=True)