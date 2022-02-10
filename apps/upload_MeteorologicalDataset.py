import dash
import dash_core_components as dcc
from dash_core_components.Graph import Graph
import dash_html_components as html
from dash.dependencies import Input, Output,State
import dash_bootstrap_components as dbc
from dash_html_components import H4
from dash_html_components.Br import Br
from dash_html_components.Hr import Hr
import plotly.express as px
import pandas as pd
import pathlib
from app import app
import dash_table
from dash.exceptions import PreventUpdate

import base64
import datetime
import io
import os 
import subprocess

import importlib
import tree


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
    ], no_gutters=True, justify='around'),  # Horizontal:start,center,end,between,around 


    dbc.Row([
        dbc.Col([
            html.Div(id='output-datatable'),
                ],# width={'size':10, 'offset':1, 'order':1},
                xs=12, sm=12, md=12, lg=10, xl=10
                ),
                ], no_gutters=True, justify='around'),  # Horizontal:start,center,end,between,around 
    # for Bar Graph or Scatter Plot
    dbc.Row([
        dbc.Col([
             html.Div(id='output-div'),
                ],# width={'size':3, 'offset':1, 'order':1},
                xs=12, sm=12, md=12, lg=10, xl=10
                ),
            ], no_gutters=True, justify='around'),  # Horizontal:start,center,end,between,around 
        
    # another row for Choropleth Map
    dbc.Row([
            dbc.Col([
                html.Div(id='output-map'),
                html.Hr()
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],no_gutters=True, justify='around'),    

    # running tree.py and get newick files
    dbc.Row([
            dbc.Col([
                html.Div(id='newick-files-container1'),
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],no_gutters=True, justify='around'),

    dbc.Row([
            dbc.Col([
                html.Div(id='newick-files-container2'),
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],no_gutters=True, justify='around'),

    dbc.Row([
            dbc.Col([
                html.Div(id='newick-files-container3'),
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],no_gutters=True, justify='around'),

    dbc.Row([
            dbc.Col([
                html.Div(id='newick-files-container4'),
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],no_gutters=True, justify='around'),

         ], fluid=True)


        
    

#---------------------------------------------------------

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
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
                                html.H5(filename),
                                #html.H6(datetime.datetime.fromtimestamp(date)),
                                html.P("Inset X axis data"),
                                dcc.Dropdown(id='xaxis-data',
                                            options=[{'label':x, 'value':x} for x in df.columns]),
                                html.P("Inset Y axis data"),
                                dcc.Dropdown(id='yaxis-data',
                                            options=[{'label':x, 'value':x} for x in df.columns]),
                                html.P("Select data for choropleth map"),
                                dcc.Dropdown(id='map-data',
                                            options=[{'label':x, 'value':x} for x in df.columns]),
                                html.Br(),
                                dcc.RadioItems(id='choose-graph-type',
                                                options=[
                                                    {'label': 'Bar Graph', 'value': 'Bar'},
                                                    {'label': 'Scatter Plot', 'value': 'Scatter'}
                                                ],
                                                value='Bar'
                                            ),  
                                html.Br(),
                                html.Button(id="submit-button", children="Create Graph"),
                                html.Hr(),
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
                                html.Button(id="submit-forTree", children="Create Newick files"),  
                                html.Hr(),

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

@app.callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              State('choose-graph-type','value'),
              State('stored-data','data'),
              State('xaxis-data','value'),
              State('yaxis-data', 'value')
              )
def make_graphs(n, graph_type, data, x_data, y_data):
    if n is None:
        return dash.no_update
    else:
        if graph_type == 'Bar':
            bar_fig = px.bar(data, x=x_data, y=y_data)
        if graph_type =='Scatter':
            bar_fig = px.scatter(data, x=x_data, y=y_data)
        # print(data)
        return dcc.Graph(figure=bar_fig)

# Choropleth Map
@app.callback(
    Output('output-map','children'),
    Input('submit-button','n_clicks'),
    State('stored-data','data'),
    State('map-data', 'value')
)

def update_output(num_clicks, data, val_selected):
    #print(data[0].keys())
    if num_clicks is None:
        return dash.no_update
    else:
        if "iso_alpha" in data[0].keys():

            fig = px.choropleth(data, locations="iso_alpha",
                                color=val_selected,
                                projection='natural earth',
                                color_continuous_scale=px.colors.sequential.Turbo)

            fig.update_layout(title=dict(font=dict(size=28),x=0.5,xanchor='center'),
                            margin=dict(l=60, r=60, t=50, b=50))

            return dcc.Graph(figure=fig)

# phylogeography trees : parameters
@app.callback(
    Output('newick-files-container1','children'),
    Input('submit-forTree','n_clicks'),
    State('upload-data', 'filename')
)
def update_output(n,file_name):
    if n is None:
        return dash.no_update
    else:
        return dcc.Markdown('You have selected file:  **{}**'.format("; ".join(file_name)))

@app.callback(
    Output('newick-files-container2','children'),
    Input('submit-forTree','n_clicks'),
    State('col-specimens','value')
)
def update_output(n,specimen):
    if n is None:
        return dash.no_update
    else:
        return dcc.Markdown('In this file, the name of column containing the sequence Id is :  **{}**'.format(specimen))

@app.callback(
    Output('newick-files-container3','children'),
    Input('submit-forTree','n_clicks'),
    State('col-analyze', 'value')
)
def update_output(n,names):
    if n is None:
        return dash.no_update
    else:
        return dcc.Markdown('In order to create reference trees, the columns selected are:  **{}**'.format("; ".join(names)))
    
# phylogeography trees : newick files
@app.callback(
    Output('newick-files-container4','children'),
    Input('submit-forTree','n_clicks'),
    State('upload-data', 'filename'),
    State('col-specimens','value'),
    State('col-analyze', 'value')
)
def update_output(n,file_name,specimen,names):
    if n is None:
        return dash.no_update
    else:
        col_names = [specimen] + list(names)
        tree.create_tree(file_name[0], list(col_names)) # run tree.py
        
        tree_path = os.listdir()
        tree_files = []
        for item in tree_path:
            if item.endswith("_newick"):
                tree_files.append(item)
                #print(item)
        #print(tree_files)

        outputs_container = html.Div([
            html.Hr(),
            html.H6('output files:'),
            html.H5("; ".join(tree_files)),
            dcc.Input(id = "input_fileName", type = "text", 
                    placeholder = "Enter the name of the file to be downloaded", 
                    style= {'width': '68%','marginRight':'20px'}),
            dbc.Button(id='btn-newick',
                            children=[html.I(className="fa fa-download mr-1"), "Download newick files"],
                            color="info",
                            className="mt-1"
                                    ),
            dcc.Download(id="download-newick"),

        ])

        return outputs_container

# for download button
@app.callback(
    Output("download-newick", "data"),
    Input("btn-newick", "n_clicks"),
    State('input_fileName','value'), 
    prevent_initial_call=True,
)
def func(n_clicks, fileName):
    if n_clicks is None:
        return dash.no_update
    else:
        return dcc.send_file(fileName)