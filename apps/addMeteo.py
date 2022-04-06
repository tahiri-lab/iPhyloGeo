import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output,State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import pathlib
from app import app
from dash import dash_table
from dash.exceptions import PreventUpdate
import base64
import datetime
import io
import os 
import subprocess
import importlib
import tree_user
from requests import get
from apps import mainPage
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
#-------------------------------------------
# create a csv table for meteo parameters
meteo_csv = 'user/' + theIp + '/input/meteo.csv'
if not os.path.exists(meteo_csv):
    pd.DataFrame(list()).to_csv(meteo_csv)

#---------------------------
# For uploaded dataset

layout = dbc.Container([
    html.H1('Phylogeography', style={"textAlign": "center"}),  #title
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '99%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=10, xl=10
        ),
    ], justify='around'),  # Horizontal:start,center,end,between,around


    dbc.Row([
        dbc.Col([
            html.Div(id='output-datatable'),
                ],# width={'size':10, 'offset':1, 'order':1},
                xs=12, sm=12, md=12, lg=10, xl=10
                ),
                ], justify='around'),  # Horizontal:start,center,end,between,around
    
    dbc.Row([
            dbc.Col([
                html.Div(id='summary-container1'),
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],justify='around'),

    # log
    dbc.Row([
            dbc.Col([
                html.Hr(),
                dcc.Link(html.Button("Finished"), href="/apps/logPage", refresh=True),
                #html.Hr(),
                ],xs=12, sm=12, md=12, lg=10, xl=10),

            ], justify='around'),
    dbc.Row([
            dbc.Col([
                html.Hr(),
                html.Div(mainPage.layout),
                #html.Hr(),
                ],xs=12, sm=12, md=12, lg=10, xl=10),

            ], justify='around'),

         ], fluid=True)


#---------------------------------------------------------

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    seq_upload = decoded.decode('utf-8')
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(seq_upload))
            df.to_csv("user/" + theIp + "/input/donnees.csv")
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            df.to_csv("user/" + theIp + "/input/donnees.csv")
        else:
            # Assume that the user uploaded other files
            return html.Div([
                'Please upload a CSV file or an excel file.'
        ])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    #print(content_string)
    param_selection = dbc.Container([ 
                dbc.Row([
                        dbc.Col([
                            dash_table.DataTable(
                                    data= df.to_dict('records'),
                                    columns=[{'name': i, 'id': i} for i in df.columns],
                                    page_size=15
                                ),
                                dcc.Store(id='stored-data', data=df.to_dict('records')),

                                html.Hr(),  # horizontal line

                                # For debugging, display the raw contents provided by the web browser
                                #html.Div('Raw Content'),
                                #html.Pre(contents[0:200] + '...', style={
                                #    'whiteSpace': 'pre-wrap',
                                #    'wordBreak': 'break-all'
                                #}),
                        ],xs=12, sm=12, md=12, lg=10, xl=10),

                    ],no_gutters=True, justify='around'), 

                dbc.Row([
                        dbc.Col([
                            html.Div([
                                #html.H5(filename),
                                #html.H6(datetime.datetime.fromtimestamp(date)),
                            # parameters for creating phylogeography trees
                                html.H2('Create Phylogeography Trees', style={"textAlign": "center"}),  #title
                                html.H4("Inset the name of the column containing the sequence Id"),
                                dcc.Dropdown(id='col-specimens',
                                            options=[{'label':x, 'value':x} for x in df.columns]),
                                html.H4("select the name of the column to analyze"),
                                html.P('The values of the column must be numeric for the program to work properly.'),
                                dcc.Checklist(id = 'col-analyze',
                                            options =[{'label': x, 'value': x} for x in df._get_numeric_data().columns],
                                            labelStyle={'display': 'inline-block','marginRight':'20px'}
                                        ),
                                html.Br(),
                                html.Button(id="submit-forTree", children="Submit"),  
                                ])
                        ],xs=12, sm=12, md=12, lg=10, xl=10),
                    ],no_gutters=True, justify='around'), 

                   
         ], fluid=True)

    return param_selection
        

#--------------------------------------------------------------------------------
@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

# phylogeography trees : parameters
@app.callback(
    Output('summary-container1','children'),
    Input('submit-forTree','n_clicks'),
    State('upload-data', 'filename'),
    State('col-specimens','value'),
    State('col-analyze', 'value')
)
def update_output(n,file_name,specimen, col_names):
    if n is None:
        return dash.no_update
    else:
        summary_container = dbc.Card([
            dbc.CardBody([
                html.H4("Done", className="card-title"),
                dcc.Markdown('You have selected file:  **{}**'.format("; ".join(file_name))),
                dcc.Markdown('In this file, the name of column containing the sequence Id is :  **{}**'.format(specimen)),
                dcc.Markdown('In order to create reference trees, the columns selected are:  **{}**'.format("; ".join(col_names)))
            ]),
    ],
    style={"width": "60%"},       #50rem
),
        return summary_container