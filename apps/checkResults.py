import sys
import math
import dash_cytoscape
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
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
def getOutputCSV(fileName = "output.csv"):
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
                html.Div(output_table(output_df),id = "output-csv"),
                
            ],xs=12, sm=12, md=12, lg=10, xl=10),

         ],className="g-0", justify='around'),

    dbc.Row([
            dbc.Col(
                html.Div([
                    html.Br(),
                    dbc.Button(id="submit-button-filter1", children="Create Graph"),
                ]),
            width = {"size":1}
            ),
            dbc.Col(
                html.Div([
                    html.Br(),
                    dbc.Button(id="trees-button1", children="Create tree"),
                ]),
            width = {"size":1}
            ),
            dbc.Col(
                html.Div([
                    html.Br(),
                    dbc.Button(id="alignChart-button1", children="Create Alignment Chart"),
                ]),
            width = {"size":1}
            ),

            dbc.Col(
                html.Div([
                    html.Br(),
                    dbc.Button(id='btn-csv1',
                            children=[html.I(className="fa fa-download mr-1"), "Download to CSV"],
                            color="info",
                            className="mt-1"),
                ]),
            width = {"size":1}
            ),

                dcc.Download(id="download-component-csv1"),

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
            interval=60000, # in milliseconds
            n_intervals=0,
            max_intervals=10000000
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
    Input("trees-button1", "n_clicks"),
    State('datatable-interactivity1', "derived_virtual_data"),
    State('datatable-interactivity1', 'derived_virtual_selected_rows'),
    prevent_initial_call=True,
)
def func(n_clicks, select_rows, n_intervals):
    if n_clicks is None:
        return dash.no_update
    else:
        data = pd.DataFrame(select_rows)
        stylesheet = [
            {
                'selector': '.nonterminal',
                'style': {
                    'label': 'data(confidence)',
                    'background-opacity': 0,
                    "text-halign": "left",
                    "text-valign": "top",
                }
            },
            {
                'selector': '.support',
                'style': {'background-opacity': 0}
            },
            {
                'selector': 'edge',
                'style': {
                    "source-endpoint": "inside-to-node",
                    "target-endpoint": "inside-to-node",
                }
            },
            {
                'selector': '.terminal',
                'style': {
                    'label': 'data(name)',
                    'width': 10,
                    'height': 10,
                    "text-valign": "center",
                    "text-halign": "right",
                    'background-color': '#222222'
                }
            }
        ]
        layout = {'name': 'preset'}
        elementsReturn = []
        for trees_name in data['Arbre phylogeographique'][n_intervals]:
            tree = Phylo.read(trees_name, 'newick')
            nodes, edges = generate_elements(tree)
            elements = nodes + edges
            elementsReturn.append(dash_cytoscape.Cytoscape(
                    id='cytoscape-usage-phylogeny',
                    elements=elements,
                    stylesheet=stylesheet,
                    layout=layout,
                    style={
                        'height': '95vh',
                        '       width': '100%'
                    }
            ))
    return html.Div(elementsReturn)


def generate_elements(tree, xlen=30, ylen=30, grabbable=False):
    def get_col_positions(tree, column_width=80):
        taxa = tree.get_terminals()

        # Some constants for the drawing calculations
        max_label_width = max(len(str(taxon)) for taxon in taxa)
        drawing_width = column_width - max_label_width - 1

        """Create a mapping of each clade to its column position."""
        depths = tree.depths()
        # If there are no branch lengths, assume unit branch lengths
        if not max(depths.values()):
            depths = tree.depths(unit_branch_lengths=True)
            # Potential drawing overflow due to rounding -- 1 char per tree layer
        fudge_margin = int(math.ceil(math.log(len(taxa), 2)))
        cols_per_branch_unit = ((drawing_width - fudge_margin) /
                                float(max(depths.values())))
        return dict((clade, int(blen * cols_per_branch_unit + 1.0))
                    for clade, blen in depths.items())

    def get_row_positions(tree):
        taxa = tree.get_terminals()
        positions = dict((taxon, 2 * idx) for idx, taxon in enumerate(taxa))

        def calc_row(clade):
            for subclade in clade:
                if subclade not in positions:
                    calc_row(subclade)
            positions[clade] = ((positions[clade.clades[0]] +
                                 positions[clade.clades[-1]]) // 2)

        calc_row(tree.root)
        return positions

    def add_to_elements(clade, clade_id):
        children = clade.clades

        pos_x = col_positions[clade] * xlen
        pos_y = row_positions[clade] * ylen

        cy_source = {
            "data": {"id": clade_id},
            'position': {'x': pos_x, 'y': pos_y},
            'classes': 'nonterminal',
            'grabbable': grabbable
        }
        nodes.append(cy_source)

        if clade.is_terminal():
            cy_source['data']['name'] = clade.name
            cy_source['classes'] = 'terminal'

        for n, child in enumerate(children):
            # The "support" node is on the same column as the parent clade,
            # and on the same row as the child clade. It is used to create the
            # 90 degree angle between the parent and the children.
            # Edge config: parent -> support -> child

            support_id = clade_id + 's' + str(n)
            child_id = clade_id + 'c' + str(n)
            pos_y_child = row_positions[child] * ylen

            cy_support_node = {
                'data': {'id': support_id},
                'position': {'x': pos_x, 'y': pos_y_child},
                'grabbable': grabbable,
                'classes': 'support'
            }

            cy_support_edge = {
                'data': {
                    'source': clade_id,
                    'target': support_id,
                    'sourceCladeId': clade_id
                },
            }

            cy_edge = {
                'data': {
                    'source': support_id,
                    'target': child_id,
                    'length': clade.branch_length,
                    'sourceCladeId': clade_id
                },
            }

            if clade.confidence and clade.confidence.value:
                cy_source['data']['confidence'] = clade.confidence.value

            nodes.append(cy_support_node)
            edges.extend([cy_support_edge, cy_edge])

            add_to_elements(child, child_id)

    col_positions = get_col_positions(tree)
    row_positions = get_row_positions(tree)

    nodes = []
    edges = []

    add_to_elements(tree.clade, 'r')

    return nodes, edges

# -----------------------------------
# select gene
@app.callback(
    Output("alignment-select1", "children"),
    Input("alignChart-button1", "n_clicks"),
    State('datatable-interactivity1', "derived_virtual_data"),
    State('datatable-interactivity1', 'derived_virtual_selected_rows'),
    prevent_initial_call=True,
)
def func(n_clicks,all_rows_data,select_rows):
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
@app.callback(
    Output('output-csv', 'children'),
    Input("interval-component", "n_intervals")
)
def update_output(n_intervals):
    global lastmt
    global output_df

    if os.stat(path).st_mtime > lastmt:
        output_df = pd.read_csv(path)
        print("File modified")
        lastmt = os.stat(path).st_mtime
    return output_table(output_df)



            

            
        











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