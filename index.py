from pydoc import classname
import dash_bootstrap_components as dbc

from dash import dcc, html, State, Input, Output
from dash.dependencies import Input, Output


# Connect to main app.py file
from app import app
# Connect to your app pages
from apps import pipelineWithOurData, pipelineWithUploadedData, upload_MeteorologicalDataset, homePage, checkResults, usingOurMeteorologicalDataset

sidebar = html.Div(
    [
        html.Div(
            className="nav-bar-container",
            children=[
                html.Div([
                    #html.Div(id='hidden-div', style={'display': 'none'}), # hidden div to trigger callback (necessary to store data in local storage)
                    html.Div([
                        html.Img(src='../assets/logo/LabLogo.png', className="logo"),
                        html.Div('Tahiri Lab', className="lab-name"),
                        dcc.Input(id="input1", type="text", placeholder="ici", style={'marginRight':'10px'}),
                        html.Img(src='../assets/icons/theme.svg', id='submit-val', className="icon"),
                    ], className="lab-container"),
                    ], className="nav-bar"),
                html.Div([
                    dbc.NavLink([
                        html.Img(src='../assets/icons/house-solid.svg', className="icon"),
                        html.Div("Home", className="text"),
                    ], href='/apps/homePage', active="exact", className="nav-link"),
                    dbc.NavLink([
                        html.Img(src='../assets/icons/folder-upload.svg', className="icon"),
                        html.Div("Upload Data", className="text"),
                    ], href='/apps/homePage', active="exact", className="nav-link"),
                    dbc.NavLink([
                        html.Img(src='../assets/icons/dashboard.svg', className="icon"),
                        html.Div("Check Results", className="text"),
                    ], href='/apps/checkResults', active="exact", className="nav-link"),
                    # Legacy
                    # html.Div("Legacy"),
                    # dbc.NavLink("Upload Meteorological Data", href='/apps/upload_MeteorologicalDataset', active="exact"),
                    # dbc.NavLink("Uploaded Genetic Data", href='/apps/pipelineWithUploadedData', active="exact"),
                    # dbc.NavLink("Using Our Meteorological Data (yellow-legged hornet)", href='/apps/usingOurMeteorologicalDataset', active="exact"),
                    # dbc.NavLink("Phylogeography Analysis With Our Data (yellow-legged hornet)", href='/apps/pipelineWithOurData', active="exact"),
                    # dbc.NavLink("See my Results", href='/apps/checkResults', active="exact"),
                ], className="nav-link-container"),
                html.Div([
                    html.A([
                        html.Img(src='../assets/icons/github.svg', className="icon"),
                        html.Div("Visit our GitHub", className="text"),
                    ], target='_blank', href="https://github.com/tahiri-lab", className="gitHub"),
                ], className="gitHub-container"),
            ],
        ),
    ],
)

content = html.Div(id="page-content", children=[])

app.layout = html.Div([
    dcc.Store(id='theme', data='light', storage_type='local'), # store to store theme data
    dcc.Location(id="url"),
    html.Div(children=[
    sidebar,
    content
    ], id='themer', style={'display': 'flex'})
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

@app.callback(Output('theme', 'data'), # hidden div to trigger callback (necessary to store data in local storage)
              Input('input1', 'value'))  # button to trigger callback (need at least one parameter, but we dont use n_clicks)
            #   State('theme', 'data'))           # store to get current theme

def change_theme(data):
    app.logger.info('change_theme'),
    app.logger.info(data),
    # print(dcc.Store(id='theme', data='light', storage_type='local'))
    #data = 'lol'
    # if data == None:
    #     data = 'dark'
    # elif data == 'dark':
    #    data = 'light'
    # else:
    #     data = 'dark'
    return data

@app.callback(
    Output("themer", "style"),
    [Input("theme", "data")]
)
def update_color(data):
    # CSS for light theme
#     app.logger.info('style'),
#     app.logger.info(data)
    if data == 'light':
        return {
            "--text-color": "#f5f5f5",
            "--reverse-black-white-color": "black",
            "--reverse-white-black-color": "white",
            "--icon-filter": "invert(0%) sepia(82%) saturate(7500%) hue-rotate(33deg) brightness(84%) contrast(115%)",
            "--reverse-icon-filter": "invert(100%) sepia(0%) saturate(0%) hue-rotate(109deg) brightness(106%) contrast(101%)",
            "--glass-style": "rgba(255, 255, 255, 0.5)",
            "--glass-overlay-style": "rgba(28, 28, 32, 0.5)"
        }
    # CSS for dark theme
    else:
        return {
            "--text-color": "#E0E0E0",
            "--reverse-black-white-color": "white",
            "--reverse-white-black-color": "black",
            "--icon-filter": "invert(100%) sepia(0%) saturate(0%) hue-rotate(109deg) brightness(106%) contrast(101%)",
            "--reverse-icon-filter": "invert(0%) sepia(82%) saturate(7500%) hue-rotate(33deg) brightness(84%) contrast(115%)",
            "--glass-style": "rgba(41, 40, 50, 0.5)",
            "--glass-overlay-style": "rgba(59, 58, 67, 0.5)"
        }

if __name__ == '__main__':
    app.run_server(debug=True)
