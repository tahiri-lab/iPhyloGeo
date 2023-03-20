from typing import Container
from dash import Dash, html, dcc, ctx
from dash.dependencies import Output, Input, ClientsideFunction
import dash_bootstrap_components as dbc
from app import app
# import pandas as pd
# import pathlib

from apps import upload_MeteorologicalDataset
from apps.upload.geo import params
from apps.upload import dataTypeSection, dropFileSection

content = html.Div(id="third-section", children=[params.layout])

layout = html.Div([
    html.Div(id='action'),
    html.Div(
        className="getStarted",
        children=[
            # Upload type section
            html.Div(children=[dataTypeSection.layout]),
            # Drop file section
            html.Div(children=[dropFileSection.layout]),
            # params (determine with the choose_option function in dataTypeSection)
            content,
        ]
    ),
])
