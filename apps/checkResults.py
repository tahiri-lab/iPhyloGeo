import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
#from dash_core_components.Graph import Graph
from dash.dependencies import Input, Output,State
import dash_bio as dashbio
from more_itertools import last
#from dash_html_components.Br import Br
#from dash_html_components.Div import Div
#from dash_html_components.Hr import Hr
import plotly.express as px
import pandas as pd
import pathlib
from dash import dash_table
from dash.exceptions import PreventUpdate
import os
from Bio import AlignIO, SeqIO, Phylo
import re
import numpy as np

from app import app

# get relative data folder
'''
def getOutputCSV(fileName = path):
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("../").resolve()
    if os.path.exists(DATA_PATH.joinpath(fileName)):
        dfg = pd.read_csv(DATA_PATH.joinpath(fileName))
    return dfg

output_df = getOutputCSV()
'''

path = "output.csv"
lastmt = os.stat(path).st_mtime
#print(lastmt)
output_df = pd.read_csv(path)

def output_table(data):
    table_interact = dash_table.DataTable(
                            id='datatable-interactivity1',
                            columns=[
                                {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": False}
                                for i in output_df.columns
                            ],
                            data=data.to_dict('records'),  # the contents of the table
                            editable=False,              # allow editing of data inside all cells
                            filter_action="native",     # allow filtering of data by user ('native') or not ('none')
                            sort_action="native",       # enables data to be sorted per-column by user or not ('none')
                            sort_mode="single",         # sort across 'multi' or 'single' columns
                            column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                            row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                            row_deletable=False,         # choose if user can delete a row (True) or not (False)
                            selected_columns=[],        # ids of columns that user selects
                            selected_rows=[],           # indices of rows that user selects
                            page_action="native",       # all data is passed to the table up-front or not ('none')
                            page_current=0,             # page number that user is on
                            page_size=12,                # number of rows visible per page
                            style_cell={                # ensure adequate header width when text is shorter than cell's text
                                'minWidth': 95, 'maxWidth': 95, 'width': 95
                            },
                            style_data={'color': 'black',
                                'backgroundColor': 'white'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(220, 220, 220)',
                                }
                            ],
                            style_header={
                                'backgroundColor': 'rgb(210, 210, 210)',
                                'color': 'black',
                                'fontWeight': 'bold'
                            }
                        )
    return table_interact


#---------------------------------------------
layout = dbc.Container([
    html.H1('Output', style={"textAlign": "center"}),  #title

    dbc.Row([
            dbc.Col([
                #html.Button(id="view-button1", children="Update results"),
                #html.Br(),
                #html.Br(),
                html.Div(output_table(output_df),id= "output-csv"),
                
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],className="g-0", justify='around'),

    dbc.Row([
             dbc.Col([
                html.Br(),
                html.Button(id="submit-button-filter1", children="Create Graph"),
             ],xs=3, sm=3, md=3, lg=3, xl=3),

             dbc.Col([
                html.Br(),
                dbc.Button(id="trees-button1", children="Create tree"),
             ],xs=3, sm=3, md=3, lg=3, xl=3),

             dbc.Col([
                html.Br(),
                dbc.Button(id="alignChart-button1", children="Create AlignmentChart"),
             ],xs=3, sm=3, md=3, lg=3, xl=3),

             dbc.Col([
                html.Br(),
                dbc.Button(id='btn-csv1',
                            children=[html.I(className="fa fa-download mr-1"), "Download to CSV"],
                            color="info",
                            className="mt-1"
                                    ),
                dcc.Download(id="download-component-csv1"),

             ],xs=3, sm=3, md=3, lg=3, xl=3),


         ],className="g-0", justify='around'),

    # For Graph
    dbc.Row([
             dbc.Col([
                html.Br(),
                html.Div(id='graph-container1'),
             ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],className="g-0", justify='around'),

    # For tree
    dbc.Row([
             dbc.Col([
                html.Hr(),
                html.Br(),
                html.Div(id='trees-container1'),
             ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],className="g-0", justify='around'),

    # For alignment chart
    dbc.Row([
             dbc.Col([
                html.Hr(),
                html.Br(),
                html.Div(id='alignment-select1'),
             ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],className="g-0", justify='around'),

    dbc.Row([
             dbc.Col([
                html.Br(),
                html.Div(id='alignment-container1'),

             ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],className="g-0", justify='around'),
    
    #For live updates
    dcc.Interval(
            id='interval-component',
            interval=500, # in milliseconds
            n_intervals=0,
            max_intervals=100000
        )



    ], fluid=True)


#-----------------------------------------------------------------------
# for download button
@app.callback(
    Output("download-component-csv1", "data"),
    Input("btn-csv1", "n_clicks"),
    State('datatable-interactivity1', "derived_virtual_data"),
    prevent_initial_call=True,
)
def func(n_clicks,all_rows_data):
    dff = pd.DataFrame(all_rows_data)

    return dcc.send_data_frame(dff.to_csv, path)

#-----------------------------------
@app.callback(
    Output("graph-container1", "children"),
    Input("submit-button-filter1", "n_clicks"),
    State('datatable-interactivity1', "derived_virtual_data"),
    prevent_initial_call=True,
)

def func(n_clicks,all_rows_data):
    if n_clicks is None:
        return dash.no_update
    else:
        dff = pd.DataFrame(all_rows_data)
        dff['100-RF normalise'] = 100 - dff['RF normalise']
        #print(dff['Gene'].unique())

        graphs = []

        for gene in dff['Gene'].unique():
            dfg = dff[dff['Gene'] == gene]

            scatter_output = px.scatter(
                data_frame=dfg,
                x="Position ASM",
                y="Bootstrap moyen",
                size = "100-RF normalise",
                size_max=10,
                color = "Arbre phylogeographique",
                opacity = 0.5,
                hover_data=['Gene'],
                facet_col="Arbre phylogeographique",
                facet_col_wrap=1,
                title="phylogeographic analysis of {}".format(gene),
                
                #symbol = "Arbre phylogeographique",
                )
            graphs.append(dcc.Graph(figure=scatter_output))

        return graphs
#------------------------------------
# For trees
@app.callback(
    Output("trees-container1", "children"),
    Input("trees-button1", "n_clicks"), Input("interval-component", "n_intervals"),
    State('datatable-interactivity1', "derived_virtual_data"),
    State('datatable-interactivity1', 'derived_virtual_selected_rows'),
    prevent_initial_call=True,
)

def func(n_clicks,all_rows_data,select_rows,n_intervals):
    if n_clicks is None:
        return dash.no_update
    else:
        dff = pd.DataFrame(all_rows_data)
        df_select = dff[dff.index.isin(select_rows)]
        #print(df_select)
        trees_display = []
        for index, row in df_select.iterrows():
            #if row['Gene'] != 'output/reference_gene.fasta':
            gene = row['Gene']
            position_ASM = row['Position ASM']
            tree_phylogeo = row['Arbre phylogeographique']

            directory_name = gene + '_gene'
            #align_file_name = position_ASM
            theGene_fileFasta = directory_name + '.fasta'
            tree_output_file = position_ASM + '_' + tree_phylogeo + '_tree'

            tree_path = os.path.join('./output',directory_name,tree_output_file)
            tree = Phylo.read(tree_path, "newick")
            tree_txt_path = './output/phylo_tree.txt' + str(index)
            with open(tree_txt_path, 'w') as fh:
                Phylo.draw_ascii(tree, file = fh)
            with open (tree_txt_path, "r") as f:
                tree_txt = f.read()

            tree_card = dbc.Card([
            dbc.CardBody([
                    html.H4("Row index :" + str(index), className="card-title"),
                    html.Div(tree_txt, style={'whiteSpace': 'pre-line'}),
                ]),
                    ],style={"width": "95%"},)
            
            trees_display.append(tree_card)
 
        
    return trees_display

#-----------------------------------
# select gene
@app.callback(
    Output("alignment-select1", "children"),
    Input("alignChart-button1", "n_clicks"), Input("interval-component", "n_intervals"),
    State('datatable-interactivity1', "derived_virtual_data"),
    State('datatable-interactivity1', 'derived_virtual_selected_rows'),
    prevent_initial_call=True,
)

def func(n_clicks,all_rows_data,select_rows,n_intervals):
    if n_clicks is None:
        return dash.no_update
    else:
        #if row['Gene'] != 'output/reference_gene.fasta':
        dff = pd.DataFrame(all_rows_data)
        df_select = dff[dff.index.isin(select_rows)]

        genes_selected = df_select['Gene'].unique()
        #print(genes_selected)
        if genes_selected[0] != 'output/reference_gene.fasta':
            
            return html.Div([
                html.H4("Select gene for alignment visualisation"),
                dcc.RadioItems(id='choose-align-gene',
                            options=[{'label':x, 'value':x} for x in genes_selected],),  
                            ])
        else:
            positions_selected = df_select['Position ASM'].unique()
            return html.Div([
                html.H4("Select position ASM for alignment visualisation"),
                dcc.RadioItems(id='choose-align-gene',
                            options=[{'label':x, 'value':x} for x in positions_selected],),  
                            ])


#prepare dataset
@app.callback(
    Output("alignment-container1", "children"),
    Input('choose-align-gene','value')
    )

def func(val):
    if val != None:
        
        if not bool(re.search(r'\d', val[0])):
            directory_name = val + '_gene'
            theGene_fileFasta = directory_name + '.fasta'
            align_chart_path = os.path.join('./output',directory_name,theGene_fileFasta)
        else:
            phylip_path = os.path.join('./output/windows',val)
            records = SeqIO.parse(phylip_path, "phylip")
            #align_chart_path = phylip_path +'.clustal'
            align_chart_path = phylip_path +'.fasta'
            SeqIO.write(records, align_chart_path, "fasta")


        with open(align_chart_path, encoding='utf-8') as data_file:
            data = data_file.read()

        return html.Div([
                    dashbio.AlignmentChart(
                        id='my-alignment-viewer',
                        data=data
                    ),
                    html.Div(id='alignment-viewer-output')
                ])
#create alignment chart
# @app.callback(
#     Output('alignment-viewer-output', 'children'),
#     Input('my-alignment-viewer', 'eventDatum'), Input("interval-component", "n_intervals"),
# )


# def update_output(value,n_intervals):
#     # if value is None:'datatable-interactivity1'
#     #     return 'No data.'
#     # return str(value)
#     if os.stat(path).st_mtime > lastmt:
#         print("modified")
#         lastmt = os.stat(path).st_mtime
#         return pd.read_csv(path).to_dict('records')
#     return dash.no_update


@app.callback(
    Output('output-csv', 'children'),
    Input("interval-component", "n_intervals")
)
def update_output(n_intervals):
    global lastmt
    global output_df
    #output_df = pd.read_csv(path)
    #print(output_df)
    #print("modified")
    if os.stat(path).st_mtime > lastmt:
        output_df = pd.read_csv(path)
        print("File modified")
        lastmt = os.stat(path).st_mtime
    return output_table(output_df)
    # if value is None:'datatable-interactivity1'
    #     return 'No data.'
    # return str(value)
    # if os.stat(path).st_mtime > lastmt:
    #     print("modified")
    #     lastmt = os.stat(path).st_mtime
    #     #output_df = pd.read_csv(path).to_dict('records')
    #     return pd.read_csv(path).to_dict('records')
    # return dash.no_update


            

            
        











#------------------------------------------------
'''
@app.callback(
    Output("output-csv","children"),
    Input("view-button1", "n_clicks"))

def update_data(n_clicks):
    if n_clicks is None:
        return dash.no_update
    else:
        return table_interact



        
'''