from dotenv import load_dotenv, dotenv_values
import dash
import dash_bootstrap_components as dbc
from flask import Flask
import dash_daq as daq
from dash.dependencies import Input, Output, ClientsideFunction
from dash import dcc, html

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

LIGHT_THEME = {
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

DARK_THEME = {
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

path_params = {
    'Results': {'img': ' /assets/icons/dashboard.svg', 'name': 'Check results'},
    'Homepage': {'img': '/assets/icons/house-solid.svg', 'name': 'Home'},
    'Getstarted': {'img': '/assets/icons/folder-upload.svg', 'name': 'Upload data'},
    'Settings': {'img': '/assets/icons/gear.svg', 'name': 'Settings'},
    'Help': {'img': '/assets/icons/question-circle.svg', 'name': 'Help'},
}

server = Flask(__name__)

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB],  # https://bootswatch.com/default/
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                server=server, use_pages=True)


app.layout = html.Div([
    html.Div([
        dash.page_container,
        html.Div([
            html.Div(
                className="nav-bar-container",
                id="nav-bar",
                children=[
                    html.Div([
                        html.Div([
                            html.Div(id='dummy-output'),
                            html.Img(src='/assets/logo/LabLogo.png', id="lab-logo", className="logo"),
                            html.Div('Tahiri Lab', id="lab-name", className="lab-name"),
                            daq.BooleanSwitch(id='theme-switch', className="theme-switcher", persistence=True, on=True),
                            html.Div(id='theme-switch-output')
                        ], id="lab-container", className="lab-container"),
                    ], className="nav-bar"),
                    html.Div([
                        html.Div([
                            dcc.Link([
                                html.Img(src=path_params[page['name']]['img'], className="icon"),
                                html.A(f"{path_params[page['name']]['name']}", href=page["relative_path"], className="text")
                            ], href=page["relative_path"], className="nav-link")
                            for page in [page for page in dash.page_registry.values() if page['name'] != "Result"]
                        ])
                    ], id="nav-link", className="nav-link-container"),
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
    Output("dummy-output", "children"),  # needed for the callback to trigger
    Input("lab-logo", "n_clicks"),
    prevent_initial_call=True,
)


@app.callback(
    Output('theme-switch-output', 'children'),
    Input('theme-switch', 'on'),
)
def change_theme(on):
    """

    args:
        on: boolean, True if dark theme is selected, False if light theme is selected.
            Button to trigger callback (need at least one parameter, but we dont use n_clicks)
    returns:
        theme-switch-output: value of the buttone on (true or false). Hidden div to trigger callback
    """
    return on


@app.callback(
    Output("themer", "style"),
    Input("theme-switch-output", "children")
)
def update_color(children):
    """
    args:
        children: boolean, True if dark theme is selected, False if light theme is selected.
            Button to trigger callback (need at least one parameter, but we dont use n_clicks)
    returns:
        themer: dict, css style for the theme
    """
    return LIGHT_THEME if not children else DARK_THEME


if __name__ == '__main__':
    host = ENV_CONFIG['URL']
    port = ENV_CONFIG['PORT']
    if 'http://' in host:
        host = host.replace('http://', '')

    print('Starting server... on ', host + ':' + port)

    app_dev = ENV_CONFIG['APP_ENV']

    app.run_server(
        debug=False if app_dev == 'prod' else True,
        port=port,
        host=host,
    )
