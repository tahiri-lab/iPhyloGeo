import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
# Connect to main app.py file
from app import app
# Connect to your app pages
from apps import addMeteo, mainPage, homePage, checkResults, addGene, logPage, run


#------------------------------------

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
            dbc.NavLink("Upload Datasets", href='/apps/mainPage', active="exact"),
            dbc.NavLink("Add Meteorological Data", href='/apps/addMeteo', active="exact"),
            dbc.NavLink("Add genetic data", href='/apps/addGene', active="exact"),
            dbc.NavLink("Log Page", href='/apps/logPage', active="exact"),
            dbc.NavLink("Run iPhyloGeo", href='/apps/run', active="exact"),
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
    if pathname == '/apps/addMeteo': 
        return addMeteo.layout
    if pathname == '/apps/mainPage':
        return mainPage.layout
    if pathname == '/apps/checkResults':
        return checkResults.layout
    if pathname == '/apps/addGene':
        return addGene.layout
    if pathname == '/apps/logPage':
        return logPage.layout
    if pathname == '/apps/run':
        return run.layout
    else:
        return homePage.layout 


if __name__ == '__main__':
    app.run_server(debug=True)