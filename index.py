from importlib.abc import Traversable
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import tree
import pipeline

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import pipelineWithOurData, pipelineWithUploadedData, upload_MeteorologicalDataset, homePage, checkResults, usingOurMeteorologicalDataset



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
            dbc.NavLink("Upload Meteorological Data", href='/apps/upload_MeteorologicalDataset', active="exact"), 
            dbc.NavLink("Uploaded Genetic Data", href='/apps/pipelineWithUploadedData', active="exact"),
            dbc.NavLink("Using Our Meteorological Data (yellow-legged hornet)", href='/apps/usingOurMeteorologicalDataset', active="exact"),
            dbc.NavLink("Phylogeography Analysis With Our Data (yellow-legged hornet)", href='/apps/pipelineWithOurData', active="exact"),
            dbc.NavLink("Check Results", href='/apps/checkResults', active="exact"),
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