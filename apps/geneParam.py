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
from csv import writer
from Bio import SeqIO
from requests import get

#----------------------------------------
def getIpAdress():
    ip = get("https://api.ipify.org").text
    return ip
theIp = getIpAdress()
# create a csv table for gene parameters
genes_csv = 'user/' + theIp + '/input/parameters.csv'
if not os.path.exists(genes_csv):
    with open(genes_csv, 'w') as f:
        f.write("Gene,Bootstrap value threshold,Robinson and Foulds distance threshold,Sliding Window Size,Step Size\n")
#---------------------------------------------
# Ids
input_geneName = "input_geneName"
upload_data = "upload_data"
Bootstrap_slider = "Bootstrap_slider"
Bootstrap_container = "Bootstrap_container"
RF_slider = "RF_slider"
RF_container ="RF_container"
input_windowSize = "input_windowSize"
WindowSize_container = "WindowSize_container"
input_stepSize = "input_stepSize"
StepSize_container = "StepSize_container)"
submit_button = "submit_button"
summary_container = "summary_container"
#------------------------------
layout = dbc.Container([
    html.Br(),
    dbc.Row([
        html.Br(),
        dbc.Col([
            html.H5("Please enter the name of gene to be analyzed"),
            html.Br()   
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=8, sm=8, md=8, lg=7, xl=7
        ),
        dbc.Col([
            dcc.Input(id=input_geneName, type="text", placeholder="name of gene",debounce=False,value=""),
            html.Br()
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=4, sm=4, md=4, lg=5, xl=5
        ),
    ], justify='around'),  # Horizontal:start,center,end,between,around
    
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id= upload_data,
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select .fasta Files')
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

    # The second row
     dbc.Row([

        dbc.Col([
            html.Div([
                html.H3("Bootstrap value threshold"),
                dcc.Slider(id= Bootstrap_slider,
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
                html.Div(id= Bootstrap_container)        
            ]),
        ], #width={'size':5, 'offset':0, 'order':2},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.Div([
                html.H3("Robinson and Foulds distance threshold"),
                dcc.Slider(id= RF_slider,
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
                html.Div(id= RF_container),       
            ]),
            ], #width={'size':5, 'offset':0, 'order':2},
            xs=12, sm=12, md=12, lg=5, xl=5
            ),
    ], justify='around'),  # Horizontal:start,center,end,between,around
    
    # for sliding window size & step size 
    dbc.Row([

        dbc.Col([
            html.Div([
                html.H3("Sliding Window Size"),
                dcc.Input(id = input_windowSize, type = "number", min = 0, max = 50000,
                    placeholder = "Enter Sliding Window Size", 
                    style= {'width': '65%','marginRight':'20px'}), 
                html.Div(id= WindowSize_container)        
                    ]),

        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.Div([
                html.H3("Step Size"),
                dcc.Input(id = input_stepSize, type = "number", min = 0, max = 50000, 
                    placeholder = "Enter Step Size", 
                    style= {'width': '65%','marginRight':'20px'}),
                html.Div(id=StepSize_container)        
                    ]),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),
    ], justify='around'),  # Horizontal:start,center,end,between,around

     #submit button and more genes button
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Button(id= submit_button, children="Submit"),
            html.Br(),
            #html.Hr(),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=10, xl=10),
        
    ], justify='around'),
  # summary
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Div(id= summary_container),
            html.Br(),
            #html.Hr(),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=10, xl=10),
        
    ], justify='around'),
    # output fasta
    dbc.Row([
        dbc.Col([
            #html.Hr(),
            #html.Br(),
            html.Div(id='output-fasta'),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=10, xl=10
        ),
    ],justify='around'),  # Horizontal:start,center,end,between,around
    
    ], fluid=True),

#------------------------------------

@app.callback(
    Output(summary_container, 'children'),
    Input(submit_button, "n_clicks"),
    State(input_geneName,'value'),
    State(Bootstrap_slider,'value'),
    State(RF_slider,'value'),
    State(input_windowSize,'value'),
    State(input_stepSize,'value'),
    State(upload_data, 'filename'),
    )

def update_output(n_clicks, gene_name, bootstrap_threshold, rf_threshold, window_size, step_size,filename):
    if n_clicks is None:
        return dash.no_update
    else:
        #add parameters into csv file
        list = [gene_name, bootstrap_threshold, rf_threshold, window_size, step_size]
        with open('user/' + theIp + '/input/parameters.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(list)
            f_object.close()
        #print(filename[0])
        old_name = 'user/' + theIp + '/input/' + filename[0]
        new_name = 'user/' + theIp + '/input/' + gene_name +'.fasta'
        if gene_name != '':
            os.rename(old_name,new_name)
        # display    
        output_container = dbc.Card([
            #dbc.CardImg(src="/assets/trees-img.jpg", top=True),
            dbc.CardBody([
                html.H4("Done", className="card-title"),
                dcc.Markdown('Gene name :  **{}**'.format(gene_name),className="card-text"),
                dcc.Markdown('bootstrap_thrshold :  **{}**'.format(bootstrap_threshold),className="card-text"),
                dcc.Markdown('rf_threshold :  **{}**'.format(rf_threshold),className="card-text"),
                dcc.Markdown('window_size :  **{}**'.format(window_size),className="card-text"),
                dcc.Markdown('step_size :  {}'.format(step_size),className="card-text"),
                
                #dbc.CardLink("Check Results", href="checkResults"),
                #dbc.Button("Go somewhere", color="primary"),
            ]
        ),
    ],
    style={"width": "60%"},       #50rem
),

        return output_container

#-------------------------------------------------
# view the value chosen
@app.callback(
    dash.dependencies.Output(Bootstrap_container, 'children'),
    [dash.dependencies.Input(Bootstrap_slider, 'value')])
def update_output(value):
    return 'You have selected {:0.1f}%'.format(value)

@app.callback(
    dash.dependencies.Output(RF_container, 'children'),
    [dash.dependencies.Input(RF_slider, 'value')])
def update_output(value):
    return 'You have selected {:0.1f}%'.format(value)

# callback for sliding window siza & step size; view the value chosen
def getSeqLengthMax(fileName = "user/" + theIp + "/input/upload_gene.fasta"):
    len_seq_max = 0
    for seq_record in SeqIO.parse(fileName, "fasta"):
        if len(seq_record) > len_seq_max:
            len_seq_max = len(seq_record)
    return len_seq_max

@app.callback(
    dash.dependencies.Output(WindowSize_container, 'children'),
    [dash.dependencies.Input(input_stepSize, 'value')])
def update_output(value):
    if os.path.exists("user/" + theIp + "/input/upload_gene.fasta"):
        ref_genes_len = getSeqLengthMax("user/" + theIp +"/input/upload_gene.fasta")
        if value == None:
            value_max = ref_genes_len - 1
        else:
            value_max = ref_genes_len - 1 - value
        return 'The input value must an integer from 0 to {}'.format(value_max)

@app.callback(
    dash.dependencies.Output(StepSize_container, 'children'),
    [dash.dependencies.Input(input_windowSize, 'value')])
def update_output(value):
    if os.path.exists("user/" + theIp + "/input/upload_gene.fasta"):
        ref_genes_len = getSeqLengthMax("user/" + theIp + "/input/upload_gene.fasta")
        if value == None:
            value_max = ref_genes_len - 1
        else:
            value_max = ref_genes_len - 1 - value
        return 'The input value must be an integer from 0 to {}'.format(value_max)

#------------------------------------
# get the contens of uploaded files    

def parse_fasta_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'fasta' in filename:
            # Assume that the user uploaded a fasta file
            seq_upload = decoded.decode('utf-8')
            with open("user/" + theIp + "/input/"+ filename, "w") as f:
                f.write(seq_upload)

            return html.Div([
                        dcc.Markdown('You have uploades file(s):  **{}**'.format(filename)),
                        #html.H6(datetime.datetime.fromtimestamp(date)),
                        #html.Small(seq_upload),

                        # For debugging, display the raw contents provided by the web browser
                        #html.Div('Raw Content'),
                        #html.Pre(contents[0:200] + '...', style={
                         #   'whiteSpace': 'pre-wrap',
                         #   'wordBreak': 'break-all'
                        #})
                    ])
        else:
            # Assume that the user uploaded other files
            return html.Div([
                dcc.Markdown('Please upload a **fasta file**.'),   
        ])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.' 
        ])
    
#callback for uploaded data

@app.callback(Output('output-fasta', 'children'),
              Input(upload_data, 'contents'),
              State(upload_data, 'filename'),
              State(upload_data, 'last_modified'),
              )
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_fasta_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
