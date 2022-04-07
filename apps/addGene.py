import dash
from dash import Dash, html, dcc
#from dash import dcc
#from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from app import app
import os
import base64
from Bio import SeqIO
from requests import get
from apps import geneParam, mainPage

#----------------------------------------
def getIpAdress():
    ip = get("https://api.ipify.org").text
    return ip
theIp = getIpAdress()
    
 #create user's file
user_input = 'user/'  + theIp +'/input' 
user_output = 'user/'  + theIp +'/output' 
if not os.path.exists(user_input):
    os.makedirs(user_input)
if not os.path.exists(user_output):
    os.makedirs(user_output)

#-------------------------------------------
# create a csv table for gene parameters
genes_csv = 'user/' + theIp + '/input/parameters.csv'
if not os.path.exists(genes_csv):
    with open(genes_csv, 'w') as f:
        f.write("Gene,Bootstrap value threshold,Robinson and Foulds distance threshold,Sliding Window Size,Step Size\n")


#-------------------------------------------
layout = dbc.Container([
    html.H1('Add Genetic Data', style={"textAlign": "center"}),  #title
    
    #add gene button
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Button(id="add-button", children="Add Gene"),
            html.Br(),
            html.Hr(),
        ], #width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=10, xl=10
        ),
    ], justify='around'),

    # add more genes
    dbc.Row([
            dbc.Col([
                html.Div(id='addGene-container'),
                #html.Hr(),
                ],xs=12, sm=12, md=12, lg=10, xl=10),

            ], justify='around'),
    #add gene button
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Button(id="addMore-button", children="Add Another Gene"),
            html.Br(),
            html.Hr(),
        ], #width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),
        dbc.Col([
            html.Br(),
            dcc.Link(html.Button("Finished"), href="/apps/logPage", refresh=True),
            html.Br(),
            html.Hr(),
        ], #width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),
    ], justify='around'),
    dbc.Row([
            dbc.Col([
                html.Hr(),
                html.Div(mainPage.layout),
                #html.Hr(),
                ],xs=12, sm=12, md=12, lg=10, xl=10),

            ], justify='around'),
    
], fluid=True)

#-----------------------------------
@app.callback(
    Output('addGene-container', 'children'),
    Input("add-button", "n_clicks"),
    Input("addMore-button", "n_clicks"),
    )

def update_output(add, add_more):
    gene_param = dbc.Container([
                html.Div(geneParam.layout),    
                        ], fluid=True)

    if add and add_more is None:
        return dash.no_update
    else:
        return gene_param
        
            

#-------------------------------------------
