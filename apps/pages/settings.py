from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from dash import callback
import dash
from dash import dcc, html
from flask import Flask
import dash_daq as daq

dash.register_page(__name__, path='/settings')

layout = html.Div([
    # Header
    html.Div([
        html.H1("Settings", className="text-center")  # Title centered
    ], className="header"),

    # Settings Form
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Changer l'échelle (0-100%)"),
                dcc.Slider(
                    id="scale-slider",
                    min=0,
                    max=100,
                    step=1,
                    value=50,
                    marks={i: str(i) for i in range(0, 101, 20)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], md=6),  # Half-width column on medium-sized screens
            dbc.Col([
                html.Label("Changer les unités"),
                dcc.Dropdown(
                    id="unit-dropdown",
                    options=[
                        {"label": "Centimètres", "value": "cm"},
                        {"label": "Pouces", "value": "in"},
                        {"label": "Mètres", "value": "m"},
                        {"label": "Pieds", "value": "ft"},
                    ],
                    value="cm",
                    style={"background-color": "#AD00FA", "color": "white"}  # Custom style for the dropdown
                ),
            ], md=6),  # Half-width column on medium-sized screens
        ]),
        dbc.Row([
            dbc.Col([
                # Add any additional settings elements here
            ], md=12),  # Full-width column on medium-sized screens
        ]),
        dbc.Row([
            dbc.Col([
                html.Button("Enregistrer", id="save-button", n_clicks=0, className="btn btn-primary"),
            ], md=6, className="text-center mt-3")  # Half-width column on medium-sized screens, centered
        ])
    ], className="settings-form"),

], className="page-container")