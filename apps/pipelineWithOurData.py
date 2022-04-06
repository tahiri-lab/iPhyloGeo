import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Row import Row
#from dash import dcc
#from dash import html
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State

import plotly.express as px
import pandas as pd
import pathlib
from app import app
import os
import base64
import datetime
import io
import pipeline

# get relative data folder
#PATH = pathlib.Path(__file__).parent
#data_path = PATH.joinpath("../user/example/output/").resolve()

# get all the newick files produced 
os.chdir('user/example/output/')
tree_path = os.listdir()
tree_files = []
for item in tree_path:
    if item.endswith("_newick"):
        tree_files.append(item)
os.chdir('../../..')

#reference gene max length, for the validation of 'sliding window size' and 'step size'
ref_genes_len = 658

layout = dbc.Container([
    html.H1('Phylogenetic Tree', style={"textAlign": "center"}),  #title
    
    # the first row
    
     dbc.Row([

        dbc.Col([
            html.Div([
                html.H3("Bootstrap value threshold"),
                dcc.Slider(id='BootstrapThreshold-slider1',
                            min=0,  
                            max=100,
                            step=0.1,
                            marks={
                                0: {'label':'0.0%','style': {'color': '#77b0b1'}},
                                25: {'label':'25.0%','style': {'color': '#77b0b1'}},
                                50: {'label':'50.0%','style': {'color': '#77b0b1'}},
                                75: {'label':'75.0%','style': {'color': '#77b0b1'}},
                                100: {'label':'100.0%','style': {'color': '#77b0b1'}}},
                            value=10),
                html.Div(id='BootstrapThreshold-slider-output-container1')        
            ]),
        ], #width={'size':5, 'offset':0, 'order':2},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.Div([
                html.H3("Robinson and Foulds distance threshold"),
                dcc.Slider(id='RF-distanceThreshold-slider1',
                            min=0,
                            max=100,
                            step=0.1,
                            marks={
                                0: {'label':'0.0%', 'style': {'color': '#77b0b1'}},
                                25: {'label':'25.0%', 'style': {'color': '#77b0b1'}},
                                50: {'label':'50.0%', 'style': {'color': '#77b0b1'}},
                                75: {'label':'75.0%', 'style': {'color': '#77b0b1'}},
                                100: {'label':'100.0%','style': {'color': '#77b0b1'}}},
                            value=10),
                html.Div(id='RFThreshold-slider-output-container1'),       
            ]),
            ], #width={'size':5, 'offset':0, 'order':2},
            xs=12, sm=12, md=12, lg=5, xl=5
            ),
    ],justify='around'),  # Horizontal:start,center,end,between,around
    
    
    # for sliding window siza & step size 
    dbc.Row([

        dbc.Col([
            html.Div([
                html.H3("Sliding Window Size"),
                dcc.Input(id = "input_windowSize", type = "number", min = 0, max = ref_genes_len-1,
                    placeholder = "Enter Sliding Window Size", value = 0,
                    style= {'width': '65%','marginRight':'20px'}),
                html.Div(id='input_windowSize-container1'),      
                    ]),

        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.Div([
                html.H3("Step Size"),
                dcc.Input(id = "input_stepSize", type = "number", min = 0, max = ref_genes_len-1, 
                    placeholder = "Enter Step Size", value = 0,
                    style= {'width': '65%','marginRight':'20px'}),
                html.Div(id='input_stepSize-container1'), 
                    ]),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),
    ], justify='around'),  # Horizontal:start,center,end,between,around

# select the files of reference tree
    dbc.Row([
            dbc.Col([
                html.Br(),
                html.Hr(),
                html.H3("Select the file(s) of reference trees"),
                dcc.Checklist(id = 'reference_trees',
                            options =[{'label': x, 'value': x} for x in tree_files],
                            labelStyle={'display': 'inline-block','marginRight':'20px'}),
            ],# width={'size':3, 'offset':1, 'order':1},
            xs=12, sm=12, md=12, lg=10, xl=10
            ),
        ], justify='around'),

    #submit button
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Button(id="submit-button", children="Submit"),
            html.Br(),
            html.Hr(),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=10, xl=10
        ),
    ], justify='around'),

    # for output of pipeline
    dbc.Row([
            dbc.Col([
                dcc.Interval(id='interval1', interval=1 * 1000, n_intervals=0,max_intervals=30*60*1000),
                html.Div(id='interval_container1'),
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],justify='around'),
  
    dbc.Row([
            dbc.Col([
                html.Div(id='output-container1'),
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],justify='around'),
       


], fluid=True)



#-------------------------------------------------
# view the value chosen
@app.callback(
    dash.dependencies.Output('BootstrapThreshold-slider-output-container1', 'children'),
    [dash.dependencies.Input('BootstrapThreshold-slider1', 'value')])
def update_output(value):
    return 'You have selected {:0.1f}%'.format(value)

@app.callback(
    dash.dependencies.Output('RFThreshold-slider-output-container1', 'children'),
    [dash.dependencies.Input('RF-distanceThreshold-slider1', 'value')])
def update_output(value):
    return 'You have selected {:0.1f}%'.format(value)

@app.callback(
    dash.dependencies.Output('input_windowSize-container1', 'children'),
    [dash.dependencies.Input('input_stepSize', 'value')])
def update_output(value):
    if value == None:
        value_max = ref_genes_len - 1
    else:
        value_max = ref_genes_len - 1 - value
    return 'The input value must an integer from 0 to {}'.format(value_max)

@app.callback(
    dash.dependencies.Output('input_stepSize-container1', 'children'),
    [dash.dependencies.Input('input_windowSize', 'value')])
def update_output(value):
    if value == None:
        value_max = ref_genes_len - 1
    else:
        value_max = ref_genes_len - 1 - value
    return 'The input value must be an integer from 0 to {}'.format(value_max)

#-------------------------------------------------
# run pipeline

@app.callback(
    Output('output-container1', 'children'),
    Input("submit-button", "n_clicks"),
    State('BootstrapThreshold-slider1','value'),
    State('RF-distanceThreshold-slider1','value'),
    State('input_windowSize','value'),
    State('input_stepSize','value'),
    State('reference_trees','value'),
    )

def update_output(n_clicks, bootstrap_threshold, rf_threshold, window_size, step_size, data_names):
    if n_clicks is None:
        return dash.no_update
    else:
        reference_gene_file = '../input/reference_gene.fasta'
        pipeline.createPhylogeneticTree(reference_gene_file, window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
        output_container = dbc.Card([
            dbc.CardImg(src="/assets/trees-img.jpg", top=True),
            dbc.CardBody([
                html.H4("Done", className="card-title"),
                dcc.Markdown('bootstrap_thrshold :  **{}**'.format(bootstrap_threshold),className="card-text"),
                dcc.Markdown('rf_threshold :  **{}**'.format(rf_threshold),className="card-text"),
                dcc.Markdown('window_size :  **{}**'.format(window_size),className="card-text"),
                dcc.Markdown('step_size :  {}'.format(step_size),className="card-text"),
                dcc.Markdown('data_names :  {}'.format(data_names),className="card-text"),
                
                dbc.CardLink("Check Results", href="checkResults"),
                #dbc.Button("Go somewhere", color="primary"),
            ]
        ),
    ],
    style={"width": "60%"},       #50rem
),

        return output_container
# add a timer
@app.callback(
    Output('interval_container1', 'children'),
    Input("submit-button", "n_clicks"),
    Input('interval1', 'n_intervals'),
    State('output-container1', 'children')
    )
def update_interval(n_clicks, n_intervals,output):
    if n_clicks is None:
        return dash.no_update
    else:
        if output == None:
            interval_container = html.Div([
                dcc.Markdown('Program is running **{}** s'.format(n_intervals))
            ])

            return interval_container
        else:
            return dash.no_update



