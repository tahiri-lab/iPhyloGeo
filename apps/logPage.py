import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from app import app
from requests import get
import os 
from dash import dash_table

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

# create csv files for gene and meteo parameters
genes_csv = 'user/' + theIp + '/input/parameters.csv'
if not os.path.exists(genes_csv):
    with open(genes_csv, 'w') as f:
        f.write("Gene,Bootstrap value threshold,Robinson and Foulds distance threshold,Sliding Window Size,Step Size\n")
meteo_csv = 'user/' + theIp + '/input/meteo.csv'
if not os.path.exists(meteo_csv):
    pd.DataFrame(list()).to_csv(meteo_csv)

#-------------------------------------------
# update csv
#os.chdir('user/' + theIp + '/input/')
#tree_path = os.listdir()
#for item in tree_path:
#    if item.endswith("csv"):
#        df_gene = pd.read_csv('parameters.csv')
#        df_meteo = pd.read_csv('meteo.csv')
#os.chdir('../../..')
#-------------------------------------
#df_gene = pd.read_csv('user/' + theIp + '/input/parameters.csv')
#df_meteo = pd.read_csv('user/' + theIp + '/input/meteo.csv')

#---------------------------
geneTable = dbc.Container([
     # table of parameters
    dbc.Row([
            dbc.Col([
                html.Br(),
                #html.Hr(),
                html.Div([
                        dash_table.DataTable(
                            id='gene-table',
                            columns=[
                                {"name": i, "id": i, "deletable": False, "selectable": False, "hideable": False}
                                for i in pd.read_csv('user/' + theIp + '/input/parameters.csv').columns ],
                            data= pd.read_csv('user/' + theIp + '/input/parameters.csv').to_dict('records'),  # the contents of the table
                            editable=False,              # allow editing of data inside all cells
                            filter_action="none",     # allow filtering of data by user ('native') or not ('none')
                            sort_action="none",       # enables data to be sorted per-column by user or not ('none')
                            #sort_mode="single",         # sort across 'multi' or 'single' columns
                            #column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                            #row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                            row_deletable=True,         # choose if user can delete a row (True) or not (False)
                            selected_columns=[],        # ids of columns that user selects
                            selected_rows=[],           # indices of rows that user selects
                            page_action="native",       # all data is passed to the table up-front or not ('none')
                            page_current=0,             # page number that user is on
                            page_size=10,                # number of rows visible per page
                            style_cell={                # ensure adequate header width when text is shorter than cell's text
                                'minWidth': 95, 'maxWidth': 95, 'width': 95
                            },
                            style_cell_conditional = [ #align text column to left
                                {
                                    'if':{'column_id': c},
                                    'textAlign': 'left'
                                } for c in ['Gene']
                            ],
                            style_data={                # overflow cells' content into multiple lines
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            style_header={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            }
                        ),

                        #html.Br(),
                    ]),

            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],justify='around'),

], fluid=True)

meteoTable = dbc.Container([
     # table of parameters
    dbc.Row([
            dbc.Col([
                html.Br(),
                #html.Hr(),
                html.Div([
                        dash_table.DataTable(
                            id='meteo-table',
                            columns=[
                                {"name": i, "id": i, "deletable": False, "selectable": False, "hideable": False}
                                for i in pd.read_csv('user/' + theIp + '/input/meteo.csv').columns ],
                            data= pd.read_csv('user/' + theIp + '/input/meteo.csv').to_dict('records'),  # the contents of the table
                            editable=False,              # allow editing of data inside all cells
                            filter_action="none",     # allow filtering of data by user ('native') or not ('none')
                            sort_action="none",       # enables data to be sorted per-column by user or not ('none')
                            #sort_mode="single",         # sort across 'multi' or 'single' columns
                            #column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                            #row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                            row_deletable=True,         # choose if user can delete a row (True) or not (False)
                            selected_columns=[],        # ids of columns that user selects
                            selected_rows=[],           # indices of rows that user selects
                            page_action="native",       # all data is passed to the table up-front or not ('none')
                            page_current=0,             # page number that user is on
                            page_size=10,                # number of rows visible per page
                            style_cell={                # ensure adequate header width when text is shorter than cell's text
                                'minWidth': 95, 'maxWidth': 95, 'width': 95
                            },
                            style_cell_conditional = [ #align text column to left
                                {
                                    'if':{'column_id': c},
                                    'textAlign': 'left'
                                } for c in ['Gene']
                            ],
                            style_data={                # overflow cells' content into multiple lines
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            style_header={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            }
                        ),

                        #html.Br(),
                    ]),

            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],justify='around'),

], fluid=True)
#-----------------------------------------
card1 = dbc.Card(
    [
        dbc.CardImg(src="/assets/climate.jpg", top=True),
        dbc.CardBody(
            [
            html.H4("Add meteorological data", className="card-title"),
            dbc.CardLink("Add dataset", href="addMeteo"),
            ]
        ),
    ],
    #style={"width": "45%"},
),

card2 = dbc.Card(
    [
        dbc.CardImg(src="/assets/dna.jpg", top=True),
        dbc.CardBody(
            [
            html.H4("Add genetic data", className="card-title"),
               
            dbc.CardLink("Add dataset", href="addGene"),
            ]
        ),
    ],
    #style={"width": "45%"},
),

card3 = dbc.Card(
    [
        dbc.CardImg(src="/assets/trees-img.jpg", top=True),
        dbc.CardBody(
            [
            dcc.ConfirmDialog(
                id='confirm-run',
                message='Note: Please make sure that all parameters have been set and confirmed',
                    ),
            html.H4("Submit & Run iPhyloGeo", className="card-title"),
            html.Button(id= "run_button", children="Submit"),
            html.Br(),
            html.Br(),
            html.Div(id="change_page"),
            ]
        ),
    ],
    #style={"width": "45%"},
),
#--------------------------------------------------------
layout = dbc.Container([
    # For Genes parameters
    html.Br(),
    #html.Br(),
    dbc.CardHeader(
            dbc.Button(
                "Genes and parameters to be analyzed",
                color="link",
                id="button-geneTable",
            )
        ),
    dbc.Collapse(
            html.Div(geneTable),
                            
            id = 'forGeneTable', is_open=False,   # the Id of Collapse
                            ),
    #comfirm button ----- gene
    dbc.Row([
        dbc.Col([
            html.Br(),
            dbc.Button(id= "confirm_button", children="Confirm genetic parameters",
                        color="success", className="me-1"),
            html.Br(),
            html.Br(),
            dcc.Link(dbc.Button(children=[html.I(className="fa fa-arrow-circle-o-up mr-1"),'Add more genetic datasets'],
                        color="info", className="me-1"), href='/apps/addGene',refresh=False),
            html.Br(),
            #html.Hr(),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=4, xl=4),
        dbc.Col([
            html.Br(),
            html.Div(id="confirmed"),
            html.Br(),
            #html.Hr(),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5),
    ], justify='around'),

     # For Meteo parameters
     html.Br(),
     #html.Br(),
    dbc.CardHeader(
            dbc.Button(
                children = "Meteorological dataset and parameters to be analyzed",
                color="link",
                id="button-meteoTable",
            )
        ),
    dbc.Collapse(
            html.Div(meteoTable),
                            
            id = 'forMeteoTable', is_open=False,   # the Id of Collapse
                            ),
    #comfirm button ----- meteo
    dbc.Row([
        dbc.Col([
            html.Br(),
            dbc.Button(id= "confirm_meteo_button", children= "Confirm meteorological parameters",
                        color="success", className="me-1"),
            html.Br(),
            html.Br(),
            dcc.Link(dbc.Button(children=[html.I(className="fa fa-arrow-circle-o-up mr-1"),'Re-Upload meteorological dataset'],
                        color="info", className="me-1"), href='/apps/addMeteo',refresh=False), 
            html.Br(),
            #html.Hr(),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=4, xl=4),
        dbc.Col([
            html.Br(),
            html.Div(id="confirmed_meteo"),
            html.Br(),
            #html.Hr(),
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5),
        
    ], justify='around'),

    # For send email
     html.Br(),
     #html.Br(),
    dbc.CardHeader(
            dbc.Button(
                [html.I(className="fa fa-envelope-o mr-1"),"Receive analysis results by email"],
                color="link",
                id="button-email",
            )
        ),
    dbc.Collapse(
        dbc.Row([
        html.Br(),
        dbc.Col([
            html.H5("Please enter the email address used to receive the analysis results"),
            html.Br()   
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=8, sm=8, md=8, lg=7, xl=7
        ),
       
        dbc.Col([
            html.Br(),
            #html.Br(),
            dcc.Input(id="input_email", type="text", placeholder="Email addeess",debounce=True,),
            html.Br()
        ],# width={'size':3, 'offset':1, 'order':1},
           xs=4, sm=4, md=4, lg=5, xl=5
        ),
    ], justify='around'),  # Horizontal:start,center,end,between,around
                            
            id = 'forEmail', is_open=False,   # the Id of Collapse
                            ),
     
    html.Br(),
    html.Br(),
    dbc.Row([
            dbc.Col([
                html.Div(card1),
            ],xs=12, sm=12, md=12, lg=4, xl=4),
            dbc.Col([
                html.Div(card2),
            ],xs=12, sm=12, md=12, lg=4, xl=4),
            dbc.Col([
                html.Div(card3),
            ],xs=12, sm=12, md=12, lg=4, xl=4),
            
         ],justify='around'),
], fluid=True)

    

#----------------------------------------
@app.callback(Output('confirmed', 'children'),
              Input('confirm_button','n_clicks'),
              Input('gene-table', "derived_virtual_data"),
          )

def save_genesTable(n, all_rows_data):
    print('***************************************************************************')
    print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    print('*****************------------------------********************************')
    dff = pd.DataFrame(all_rows_data)
    if n is None:
        return dash.no_update
    else:
        dff.to_csv('user/' + theIp + '/input/parameters.csv',index=False)
        #print(dff)
        return dcc.Markdown('The genetic parameters have been confirmed',className="card-text"),

@app.callback(Output('confirmed_meteo', 'children'),
              Input('confirm_meteo_button','n_clicks'),
              Input('meteo-table', "derived_virtual_data"),)

def save_meteoTable(n, all_rows_data):
    dff = pd.DataFrame(all_rows_data)
    if n is None:
        return dash.no_update
    else:
        dff.to_csv('user/' + theIp + '/input/meteo.csv',index=False)
        print(dff)
        return dcc.Markdown('The meteorological parameters have been confirmed',className="card-text"),
#-------------------------------------
@app.callback(
    Output("forGeneTable", "is_open"),
    [Input("button-geneTable", "n_clicks")],
    [State("forGeneTable", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("forMeteoTable", "is_open"),
    [Input("button-meteoTable", "n_clicks")],
    [State("forMeteoTable", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("forEmail", "is_open"),
    [Input("button-email", "n_clicks")],
    [State("forEmail", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
#confirm dialoge
@app.callback(Output('confirm-run', 'displayed'),
              Input('run_button','n_clicks'),)
              
def confirmSend(n):
    if n is None:
        return False
    else:
        return True
#change run page
@app.callback(Output('change_page', 'children'),
              Input('confirm-run','submit_n_clicks'),)
              
def confirmSend(n):
    if n:
        return dcc.Link(dbc.Button(children=[html.I(className="fa fa-play-circle-o mr-1"),'Run iPhyloGeo'],
                        color='info',className='mt-1',size="lg"), href='/apps/run',refresh=False)       