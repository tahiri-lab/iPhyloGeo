import dash
import dash_bootstrap_components as dbc
from flask import Flask
import os
import dash_daq as daq
from dash.dependencies import Input, Output, ClientsideFunction
from dash import dcc,html


path_params = {
    'Results': {'img': '/assets/icons/folder-upload.svg', 'name': 'Check results'},
    'Homepage': {'img': '/assets/icons/house-solid.svg', 'name': 'Home'},
    'Getstarted': {'img': '/assets/icons/dashboard.svg', 'name': 'Upload data'}
}

server = Flask(__name__)

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], #https://bootswatch.com/default/
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                server=server,use_pages=True)

ENV_CONFIG = {
     'APP_ENV': os.environ.get('APP_ENV', 'local'),
}


app.layout = html.Div([
    html.Div('Your window is to small to show the content of this page.', className="smallWindow"),
    html.Div([
        dash.page_container,
        html.Div([
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
                    html.Div(
                        [
                            dcc.Link([
                                html.Img(src=path_params[page['name']]['img'], className="icon"),
                                html.A(f"{path_params[page['name']]['name']}", href=page["relative_path"], className="text")
                            ], href=page["relative_path"], className="nav-link")
                        for page in dash.page_registry.values()
                        ]
                    ),
                    #Legacy
                    # html.Div("Legacy"),
                    # dbc.NavLink("Upload Meteorological Data", href='/apps/upload_MeteorologicalDataset', active="exact"),
                    # dbc.NavLink("Uploaded Genetic Data", href='/apps/pipelineWithUploadedData', active="exact"),
                    # dbc.NavLink("Using Our Meteorological Data (yellow-legged hornet)", href='/apps/usingOurMeteorologicalDataset', active="exact"),
                    # dbc.NavLink("Phylogeography Analysis With Our Data (yellow-legged hornet)", href='/apps/pipelineWithOurData', active="exact"),
                    # dbc.NavLink("See my Results", href='/apps/checkResults', active="exact"),
                ],id="nav-link", className="nav-link-container"),
                html.Div([
                    html.A([
                        html.Img(src='/assets/icons/github.svg', className="icon"),
                        html.Div("Visit our GitHub", className="text"),
                    ], target='_blank', href="https://github.com/tahiri-lab", className="gitHub"),
                ], id="gitHub-container", className="gitHub-container"),
            ]),
            html.Div(className="footer"),
        ]),
    ], id='themer'),
])

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='navbar_function'
    ),
    Output("dummy-output", "children"), # needed for the callback to trigger
    Input("labLogo", "n_clicks"),
    prevent_initial_call=True,
)

@app.callback(
          Output('theme-switch-output', 'children'), # hidden div to trigger callback
          Input('theme-switch', 'on'),  # button to trigger callback (need at least one parameter, but we dont use n_clicks)
          #prevent_initial_call=True,
)
def change_theme(on):
    #app.logger.info('change_theme'),
    return on

@app.callback(
    Output("themer", "style"),
    [Input("theme-switch-output", "children")]
)
def update_color(children):
    #app.logger.info(children),
    # CSS for light theme
    if not children:
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
            "--black-and-white": "white",
            "--table-bg-color": "white"
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
            "--black-and-white": "#111111",
            "--table-bg-color": "#282b32"
        }


if __name__ == '__main__':
    app.run_server(debug=True)