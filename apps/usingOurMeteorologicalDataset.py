import dash
#from dash import dcc
from dash import Dash, html, dcc
#from dash import html
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
import tree
import os

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../user/example/input/").resolve()

dfg = pd.read_csv(DATA_PATH.joinpath("donnees.csv"))

# Creating an ID column name gives us more interactive capabilities
#dfg['id'] = dfg['iso_alpha']
#dfg.set_index('id', inplace=True, drop=False)

#-------------------------------------------------------------
    # Using Data Table from our database
    # Sorting operators (https://dash.plotly.com/datatable/filtering)
layout = dbc.Container([
    html.H1('Phylogeography', style={"textAlign": "center"}),  #title
    dbc.Row([
            dbc.Col([
                html.Div([
                        dash_table.DataTable(
                            id='datatable-interactivity',
                            columns=[
                                {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
                                for i in dfg.columns
                            ],
                            data=dfg.to_dict('records'),  # the contents of the table
                            editable=True,              # allow editing of data inside all cells
                            filter_action="native",     # allow filtering of data by user ('native') or not ('none')
                            sort_action="native",       # enables data to be sorted per-column by user or not ('none')
                            sort_mode="single",         # sort across 'multi' or 'single' columns
                            column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                            #row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                            row_deletable=False,         # choose if user can delete a row (True) or not (False)
                            selected_columns=[],        # ids of columns that user selects
                            #selected_rows=[],           # indices of rows that user selects
                            page_action="native",       # all data is passed to the table up-front or not ('none')
                            page_current=0,             # page number that user is on
                            page_size=6,                # number of rows visible per page
                            style_cell={                # ensure adequate header width when text is shorter than cell's text
                                'minWidth': 95, 'maxWidth': 95, 'width': 95
                            },
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

        dbc.Row([
             dbc.Col([
                dbc.Button(id='btn-csv',
                            children=[html.I(className="fa fa-download mr-1"), "Download to CSV"],
                            color="info",
                            className="mt-1"
                                    ),
                dcc.Download(id="download-component-csv"),

             ],xs=12, sm=12, md=12, lg=10, xl=10),

         ], justify='around'),

         

        dbc.Row([
             dbc.Col([
                html.Br(),
                #html.Br(),
                html.Div(id='filter-container'),
                html.Div(id='graph-container'),
                html.Div(id='choromap-container')

             ],xs=12, sm=12, md=12, lg=10, xl=10),

         ], justify='around'),

        # running tree.py and get newick files
        html.Hr(),
        dbc.Row([
                dbc.Col([
                    html.Div(id='newick-files-container2_1'),
                ],xs=12, sm=12, md=12, lg=10, xl=10),

            ], justify='around'),

        dbc.Row([
                dbc.Col([
                    html.Div(id='newick-files-container3_1'),
                ],xs=12, sm=12, md=12, lg=10, xl=10),

            ],justify='around'),

        dbc.Row([
                dbc.Col([
                    html.Div(id='newick-files-container4_1'),
                ],xs=12, sm=12, md=12, lg=10, xl=10),

            ], justify='around'),

        
    
         ], fluid=True)

#------------------------------------------------
 
# learn code from https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/DataTable/datatable_intro_and_sort.py
@app.callback(
    Output(component_id='filter-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     #Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
     #Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
     #Input(component_id='datatable-interactivity', component_property='selected_rows'),
     #Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
     #Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
     #Input(component_id='datatable-interactivity', component_property='active_cell'),
     #Input(component_id='datatable-interactivity', component_property='selected_cells')
     ]
)

def parse_contents_fromInteractiveDT(all_rows_data):
    # Creating a new data frame based on the rows that I have left after I filter

    dff = pd.DataFrame(all_rows_data)

    #print("shape",dff.shape)

    return html.Div([
        html.P("Select X axis data"),
        dcc.Dropdown(id='xaxis-data-filtered',
                     options=[{'label':x, 'value':x} for x in dff.columns]),
        html.P("Select Y axis data"),
        dcc.Dropdown(id='yaxis-data-filtered',
                     options=[{'label':x, 'value':x} for x in dff.columns]),
        html.P("Select data for choropleth map"),
        dcc.Dropdown(id='map-data-filtered',
                     options=[{'label':x, 'value':x} for x in dff.columns]),
        html.Br(),
        dcc.RadioItems(id='choose-graph-type-filtered',
                        options=[
                            {'label': 'Bar Graph', 'value': 'Bar'},
                            {'label': 'Scatter Plot', 'value': 'Scatter'}
                        ],
                        value='Bar'
                    ),  
        html.Br(),
        html.Button(id="submit-button-filter", children="Create Graph"),
        html.Hr(),
        html.Br(),
        # parameters for creating phylogeography trees
        html.H2('Create Phylogeography Trees', style={"textAlign": "center"}),  #title
        html.H4("Inset the name of the column containing the sequence ID"),
        dcc.Dropdown(id='col-specimens', options=[{'label':x, 'value':x} for x in dff.columns]),
        html.H4("select the name of the column to analyze"),
        dcc.Markdown('The values of the column **must be numeric** for the program to work properly.'),
        dcc.Checklist(id = 'col-analyze', options =[{'label': x, 'value': x} for x in dff._get_numeric_data().columns],
                        labelStyle={'display': 'inline-block', 'marginRight':'20px'}),
        html.Br(),
        html.Button(id="submit-forTree", children="Create Newick files"),  
        html.Hr(),
    ])

@app.callback(Output('graph-container', 'children'),
              Input('submit-button-filter','n_clicks'),
              State('choose-graph-type-filtered','value'),
              State('datatable-interactivity', "derived_virtual_data"),
              State('xaxis-data-filtered','value'),
              State('yaxis-data-filtered', 'value'))

def make_graphs(n, graph_type, all_rows_data, x_data, y_data):
    dff = pd.DataFrame(all_rows_data)
    if n is None:
        return dash.no_update
    else:
        if graph_type == 'Bar':
            bar_fig = px.bar(dff, x=x_data, y=y_data)
        if graph_type =='Scatter':
            bar_fig = px.scatter(dff, x=x_data, y=y_data)
        # print(data)
        return dcc.Graph(figure=bar_fig)

# -------------------------------------------------------------------------------------
# Highlight selected column
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]

#--------------------------------------------------------------------------------------
# Choropleth Map
@app.callback(
    Output('choromap-container','children'),
    Input('submit-button-filter', 'n_clicks'),
    State('datatable-interactivity', "derived_virtual_data"),
    State('map-data-filtered', 'value')
)

def update_output(num_clicks,all_rows_data,val_selected):
    dff = pd.DataFrame(all_rows_data)
    if val_selected is None:
        raise PreventUpdate
    if num_clicks is None:
        return dash.no_update
    else:
        if "iso_alpha" in dff and val_selected in dff:

            fig = px.choropleth(dff, locations="iso_alpha",
                                color=val_selected,
                                hover_name="Region",
                                projection='natural earth',
                                color_continuous_scale=px.colors.sequential.Turbo)

            fig.update_layout(title=dict(font=dict(size=28),x=0.5,xanchor='center'),
                            margin=dict(l=60, r=60, t=50, b=50))

        return dcc.Graph(figure=fig)
#-----------------------------------------------------------------------
# for download button
@app.callback(
    Output("download-component-csv", "data"),
    Input("btn-csv", "n_clicks"),
    State('datatable-interactivity', "derived_virtual_data"),
    prevent_initial_call=True,
)
def func(n_clicks,all_rows_data):
    dff = pd.DataFrame(all_rows_data)

    return dcc.send_data_frame(dff.to_csv, "mydf_csv.csv")
    
#----------------------------------------------------------------------
# phylogeography trees : parameters

@app.callback(
    Output('newick-files-container2_1','children'),
    Input('submit-forTree','n_clicks'),
    State('col-specimens','value')
)
def update_output(n,specimen):
    if n is None:
        return dash.no_update
    else:
        return dcc.Markdown('In this file, the name of column containing the sequence ID is :  **{}**'.format(specimen))

@app.callback(
    Output('newick-files-container3_1','children'),
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
    Output('newick-files-container4_1','children'),
    Input('submit-forTree','n_clicks'),
    State('col-specimens','value'),
    State('col-analyze', 'value')
)

def update_output(n,specimen,names):
    file_name = "donnees.csv"
    if n is None:
        return dash.no_update
    else:
        col_names = [specimen] + list(names)
        tree.create_tree(file_name, list(col_names)) # run tree.py
        
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
            dcc.Download(id="download-newick-1"),

        ])

        return outputs_container

# for download button
@app.callback(
    Output("download-newick-1", "data"),
    Input("btn-newick", "n_clicks"),
    State('input_fileName','value'), 
    prevent_initial_call=True,
)
def func(n_clicks, fileName):
    if n_clicks is None:
        return dash.no_update
    else:
        return dcc.send_file(fileName)
