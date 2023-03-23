import os
from pydoc import classname
import dash_bootstrap_components as dbc

from dash import dcc, html, State, Input, Output
import dash_daq as daq
from dash.dependencies import Input, Output, ClientsideFunction


# Connect to main app.py file
from app import app
# Connect to your app pages
from apps import pipelineWithOurData, pipelineWithUploadedData, upload_MeteorologicalDataset, homePage, checkResults, usingOurMeteorologicalDataset
from apps.upload import getStarted
from apps.results import results



sidebar = html.Div(
    [
        html.Div(
            className="nav-bar-container",
            id="navBar",
            children=[
                html.Div([
                    html.Div([
                        html.Div(id='dummy-output'),
                        html.Img(src='/assets/logo/LabLogo.png', id="labLogo", className="logo"),
                        html.Div('Tahiri Lab', id="lab-name", className="lab-name"),
                        daq.BooleanSwitch(id='theme-switch', className="themeSwitcher", on=True),
                        html.Div(id='theme-switch-output')
                    ], id="lab-container", className="lab-container"),
                    ], className="nav-bar"),
                html.Div([
                    dbc.NavLink([
                        html.Img(src='/assets/icons/house-solid.svg', className="icon"),
                        html.Div("Home", className="text"),
                    ], href='/apps/homePage', active="exact", className="nav-link"),
                    dbc.NavLink([
                        html.Img(src='/assets/icons/folder-upload.svg', className="icon"),
                        html.Div("Upload Data", className="text"),
                    ], href='/apps/getStarted', active="exact", className="nav-link"),
                    dbc.NavLink([
                        html.Img(src='/assets/icons/dashboard.svg', className="icon"),
                        html.Div("Check Results", className="text"),
                    ], href='/apps/results/results', active="exact", className="nav-link"),
                    #Legacy
                    # html.Div("Legacy"),
                    # dbc.NavLink("Upload Meteorological Data", href='/apps/upload_MeteorologicalDataset', active="exact"),
                    # dbc.NavLink("Uploaded Genetic Data", href='/apps/pipelineWithUploadedData', active="exact"),
                    # dbc.NavLink("Using Our Meteorological Data (yellow-legged hornet)", href='/apps/usingOurMeteorologicalDataset', active="exact"),
                    # dbc.NavLink("Phylogeography Analysis With Our Data (yellow-legged hornet)", href='/apps/pipelineWithOurData', active="exact"),
                    # dbc.NavLink("See my Results", href='/apps/checkResults', active="exact"),
                ], id="nav-link", className="nav-link-container"),
                html.Div([
                    html.A([
                        html.Img(src='/assets/icons/github.svg', className="icon"),
                        html.Div("Visit our GitHub", className="text"),
                    ], target='_blank', href="https://github.com/tahiri-lab", className="gitHub"),
                ], id="gitHub-container", className="gitHub-container"),
            ],
        ),
    ],
)

content = html.Div(id="page-content", children=[])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='theme', data='light', storage_type='local'), # store to store theme data
    html.Div(children=[
        sidebar,
        content
    ], id='themer', style={'display': 'flex'}),
],)


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='navbar_function'
    ),
    Output("dummy-output", "children"), # needed for the callback to trigger
    Input("labLogo", "n_clicks"),
)


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
)
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
    if pathname == '/apps/results/results':
        return results.layout
    if pathname == '/apps/getStarted':
        return getStarted.layout
    else:
        return homePage.layout

@app.callback(
          Output('theme-switch-output', 'children'), # hidden div to trigger callback
          Input('theme-switch', 'on'),  # button to trigger callback (need at least one parameter, but we dont use n_clicks)
          prevent_initial_call=True,
)
def change_theme(on):
    #app.logger.info('change_theme'),
    return on

@app.callback(
    Output("themer", "style"),
    [Input("theme-switch-output", "children")]
)
def update_color(children):
    app.logger.info(children),
    # CSS for light theme
    if children == False:
        return {
            "--theme-icon": "url(../assets/icons/theme-light.svg)",
            "--switch-toggle-background": "rgb(230, 230, 230)",
            "--switch-toggle-border": "white 1px solid",
            "--text-color": "#f5f5f5",
            "--reverse-black-white-color": "#1A1C1E",
            "--reverse-white-black-color": "white",
            "--background-color": "#EBECF0",
            "--reverse-background-color": "#1A1C1E",
            "--icon-filter": "invert(0%) sepia(82%) saturate(7500%) hue-rotate(33deg) brightness(84%) contrast(115%)",
            "--reverse-icon-filter": "invert(100%) sepia(0%) saturate(0%) hue-rotate(109deg) brightness(106%) contrast(101%)",
            "--glass-style": "rgba(173, 173, 173, 0.5)",
            "--glass-overlay-style": "rgba(28, 28, 32, 0.5)",
            "--result-row-color": "#E7E7E7",
        }
    # CSS for dark theme
    else:
        return {
            "--theme-icon": "url(../assets/icons/theme-dark.svg)",
            "--switch-toggle-background": "black",
            "--switch-toggle-border": "white 1px solid",
            "--text-color": "#E0E0E0",
            "--reverse-black-white-color": "white",
            "--reverse-white-black-color": "#1A1C1E",
            "--background-color": "#1A1C1E",
            "--reverse-background-color": "#EBECF0",
            "--icon-filter": "invert(100%) sepia(0%) saturate(0%) hue-rotate(109deg) brightness(106%) contrast(101%)",
            "--reverse-icon-filter": "invert(0%) sepia(82%) saturate(7500%) hue-rotate(33deg) brightness(84%) contrast(115%)",
            "--glass-style": "rgba(41, 40, 50, 0.5)",
            "--glass-overlay-style": "rgba(59, 58, 67, 0.5)",
            "--result-row-color": "#444444",
        }


if __name__ == '__main__':
    app.run_server(debug=True)
