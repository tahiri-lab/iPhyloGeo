from unittest import result
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from app import app
from requests import get
import os 
import time
import dash_extensions as de

#----------------------------------------
def getIpAdress():
    ip = get("https://api.ipify.org").text
    return ip
theIp = getIpAdress()  
#-----------------------------------------
 #create user's file
user_input = 'user/'  + theIp +'/input' 
user_output = 'user/'  + theIp +'/output' 
if not os.path.exists(user_input):
    os.makedirs(user_input)
if not os.path.exists(user_output):
    os.makedirs(user_output)

# create a csv table for gene parameters
genes_csv = 'user/' + theIp + '/input/parameters.csv'
if not os.path.exists(genes_csv):
    with open(genes_csv, 'w') as f:
        f.write("Gene,Bootstrap value threshold,Robinson and Foulds distance threshold,Sliding Window Size,Step Size\n")
# create a csv table for meteo parameters
meteo_csv = 'user/' + theIp + '/input/meteo.csv'
if not os.path.exists(meteo_csv):
    pd.DataFrame(list()).to_csv(meteo_csv)
#-------------------------------------------
# get all the newick files produced 
os.chdir('user/' + theIp + '/output/')
tree_path = os.listdir()
tree_files = []
for item in tree_path:
    if item.endswith("_newick"):
        tree_files.append(item)
os.chdir('../../..')
#-------------------------------------
layout = dbc.Container([
    html.H1('Phylogenetic Tree', style={"textAlign": "center"}),  #title

    dbc.Row([
            dbc.Col([
                html.Br(),
                dbc.Button(id = "run-button",
                        children=[html.I(className="fa fa-cog mr-1"),'Please click here'],
                        color='info',className='d-grid gap-2 col-12 mx-auto',size="lg")
            ],xs=12, sm=12, md=12, lg=10, xl=10),
            
            ],justify='around'),

    dbc.Row([
            dbc.Col([
                html.Div(id="waiting-container"),
            ],xs=12, sm=12, md=12, lg=10, xl=10),
            
            ],justify='around'),

    dbc.Row([
            dbc.Col([
                html.Br(),
                html.Div(id="result-container"),
            ],xs=12, sm=12, md=12, lg=10, xl=10),
            
            ],justify='around'),
            

    
   
   
    
], fluid=True)

#---------------------------------------------
@app.callback(Output('waiting-container', 'children'),
              Input('run-button','n_clicks'),
              )
def run_pipeline(n):
    if n is None:
        return dash.no_update
    else:
        # Setup options.
        url = "https://assets9.lottiefiles.com/packages/lf20_YXD37q.json"
        options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))
        waiting = de.Lottie(options=options, width="25%", height="25%", url=url)
        return waiting

@app.callback(Output('result-container', 'children'),
              Input('run-button','n_clicks'),
              )
def run_pipeline(n):
    if n is None:
        return dash.no_update
    else:
        time.sleep(5)
        result = dcc.Link(dbc.Button(children=[html.I(className="fa fa-th-list mr-1"),'CheckResults'],
                        color='success',className='d-grid gap-2 col-12 mx-auto',size="lg"), href='/apps/checkResults',refresh=False)  
        return result