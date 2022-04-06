from typing import Container
import dash
from dash import Dash, html, dcc
#from dash import dcc
#from dash import html
from dash.dependencies import Output, Input, State
import plotly.express as px
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import pathlib

# get relative data folder
#PATH = pathlib.Path(__file__).parent
#IMG_PATH = PATH.joinpath("../assets").resolve()

#dfg = pd.read_csv(DATA_PATH.joinpath("theData_IfWeHave.csv"))

card1 = dbc.Card(
    [
        dbc.CardImg(src="/assets/UdeS1.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("Welcome to the Tahiri Lab", className="card-title"),
                html.P(
                    "We are a dynamic research group at the Sherbrooke University, Department of Computer Science. ",
                    className="card-text",
                ),
                html.P(
                    "Through engaged scholarship, our laboratory develops transdisciplinary research projects to analyze the" 
                    "evolution of species and assess the impacts on health by combining, among other things, information"
                     "from the genetics of species and climatic parameters.",
                    className="card-text",
                ),
                dbc.CardLink("Tahiri Lab", href="https://tahirinadia.github.io/"),
            ]
        ),
    ],
    #style={"width": "45%"},
),

card2 = dbc.Card(
    [
        dbc.CardImg(src="/assets/pipeline.png", top=True),
        dbc.CardBody(
            [
                html.H4("Phylotree", className="card-title"),
                html.P(
                    """This platform can be used to obtain trees from environment data (reference data) of the regions where the samples have been collected. 
                    Those reference trees are then used for topological comparison against phylogenetic trees 
                    from multiple sequence alignments (MSAs) using the Robinson-Foulds (RF) metric. 
                    MSAs that yield trees with a significant RF value are then saved in folders with their respective tree. 
                    The output.csv file contains the informations of all the significant MSAs informations.""",
                    className="card-text",
                ),
                dbc.CardLink("Github", href="https://github.com/tahiri-lab/phylogeography-viz/tree/main/Python"),
            ]
        ),
    ],
    #style={"width": "45%"},
),

#-----------------------------------------
layout = html.Div([
    html.Div(html.H2("Phylogeography"), style={"text-align":"center"}),
    html.Hr(),
    #----------
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div(card1),
            ],xs=12, sm=12, md=12, lg=4, xl=4),
            dbc.Col([
                html.Div(card2),
            ],xs=12, sm=12, md=12, lg=7, xl=7),

         ],justify='around'),
         
         ],fluid=True),
    
    #-------
    dbc.CardHeader(
            dbc.Button(
                "MUSCLE: Multiple sequence alignment",
                color="link",
                id="button-MUCLE",
            )
        ),
    dbc.Collapse(
            dcc.RadioItems(id='param-MUCLE',
                            options=[{'label': 'Default Parameters', 'value': 'Default'},
                                    {'label': 'Custom Parameters', 'value': 'Custom'}],
                            value='Default'), 
                            
                            id = 'forMUCLE', is_open=False,   # the Id of Collapse
                    ),
    #---------
    dbc.CardHeader(
            dbc.Button(
                "Seqboot: From PHYLIP (A free package of programs for inferring phylogenies)",
                color="link",
                id="button-Seqboot",
            )
        ),
    dbc.Collapse(
            dcc.RadioItems(id='param-Seqboot',
                            options=[{'label': 'Default Parameters', 'value': 'Default'},
                                    {'label': 'Custom Parameters', 'value': 'Custom'}],
                            value='Default'), 
                            
                            id = 'forSeqboot', is_open=False,   # the Id of Collapse
                            ),

    #---------
    dbc.CardHeader(
            dbc.Button(
                "DNADist: From PHYLIP (A free package of programs for inferring phylogenies)",
                color="link",
                id="button-DNADist",
            )
        ),
    dbc.Collapse(
            dcc.RadioItems(id='param-DNADist',
                            options=[{'label': 'Default Parameters', 'value': 'Default'},
                                    {'label': 'Custom Parameters', 'value': 'Custom'}],
                            value='Default'), 
                            
                            id = 'forDNADist', is_open=False,   # the Id of Collapse
                            ),
    #---------
    dbc.CardHeader(
            dbc.Button(
                "Neighbor: From PHYLIP (A free package of programs for inferring phylogenies)",
                color="link",
                id="button-Neighbor",
            )
        ),
    dbc.Collapse(
            dcc.RadioItems(id='param-Neighbor',
                            options=[{'label': 'Default Parameters', 'value': 'Default'},
                                    {'label': 'Custom Parameters', 'value': 'Custom'}],
                            value='Default'), 
                            
                            id = 'forNeighbor', is_open=False,   # the Id of Collapse
                            ),

    #---------
    dbc.CardHeader(
            dbc.Button(
                "Consense: From PHYLIP (A free package of programs for inferring phylogenies)",
                color="link",
                id="button-Consense",
            )
        ),
    dbc.Collapse(
            dcc.RadioItems(id='param-Consense',
                            options=[{'label': 'Default Parameters', 'value': 'Default'},
                                    {'label': 'Custom Parameters', 'value': 'Custom'}],
                            value='Default'), 
                            
                            id = 'forConsense', is_open=False,   # the Id of Collapse
                            ),
    #---------
    dbc.CardHeader(
            dbc.Button(
                "rf: Comparison of phylogenetic trees",
                color="link",
                id="button-rf",
            )
        ),
    dbc.Collapse(
            dcc.RadioItems(id='param-rf',
                            options=[{'label': 'Default Parameters', 'value': 'Default'},
                                    {'label': 'Custom Parameters', 'value': 'Custom'}],
                            value='Default'), 
                            
                            id = 'forrf', is_open=False,   # the Id of Collapse
                            ),
    #---------
    dbc.CardHeader(
            dbc.Button(
                "RAxML: A tool for phylogenetic analysis and post-analysis of large phylogenies",
                color="link",
                id="button-RAxML",
            )
        ),
    dbc.Collapse(
            dcc.RadioItems(id='param-RAxML',
                            options=[{'label': 'Default Parameters', 'value': 'Default'},
                                    {'label': 'Custom Parameters', 'value': 'Custom'}],
                            value='Default'), 
                            
                            id = 'forRAxML', is_open=False,   # the Id of Collapse
                            ),


]),




@app.callback(
    Output("forMUCLE", "is_open"),
    [Input("button-MUCLE", "n_clicks")],
    [State("forMUCLE", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("forSeqboot", "is_open"),
    [Input("button-Seqboot", "n_clicks")],
    [State("forSeqboot", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("forDNADist", "is_open"),
    [Input("button-DNADist", "n_clicks")],
    [State("forDNADist", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("forNeighbor", "is_open"),
    [Input("button-Neighbor", "n_clicks")],
    [State("forNeighbor", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("forConsense", "is_open"),
    [Input("button-Consense", "n_clicks")],
    [State("forConsense", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("forrf", "is_open"),
    [Input("button-rf", "n_clicks")],
    [State("forrf", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("forRAxML", "is_open"),
    [Input("button-RAxML", "n_clicks")],
    [State("forRAxML", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open