import dash_bootstrap_components as dbc

from dash import dcc, html, State, Input, Output, dash_table,callback
import dash_daq as daq
from dash.dependencies import Input, Output, ClientsideFunction
import dash
import plotly.express as px
from io import StringIO
from base64 import b64encode
import pandas as pd
import logging
from aPhyloGeo import aPhyloGeo
from Bio import Phylo
import dash_cytoscape as cyto
import math


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
figures =[]

def create_table(file):
    df = pd.DataFrame(file['df'])
    #global dff 
    #dff = df
    file_name = file['file_name']
    global data_climatic 
    # data_climatic = pd.read_csv(file_name)
    data_climatic = df
    param_selection = html.Div([
        html.Div([
            html.Div([
                html.H2('Create Phylogeography Trees', className="title"),  # title
                dbc.Row([
                    dbc.Col([
                        dash_table.DataTable(
                            id='datatable-interactivity',
                            data=df.to_dict('records'),
                            columns=[{'name': i, 'id': i} for i in df.columns],
                            filter_action="native",     # allow filtering of data by user ('native') or not ('none')
                            sort_action="native",       # enables data to be sorted per-column by user or not ('none')
                            sort_mode="single",         # sort across 'multi' or 'single' columns
                            page_current=0,             # page number that user is on
                            page_size=15,               # number of rows visible per page
                            filter_query='',            # query that determines which rows to keep in table
                            #page_action="native",       # all data is passed to the table up-front or not ('none')
                            #sort_by=[],                 # list of columns that user sorts table by
                            style_header={
                                'backgroundColor': '#f5f4f6',
                            },
                        ),
                        dcc.Store(id='stored-data', data=df.to_dict('records')),
                        # html.Hr(),  # horizontal line
                    ], ),

                ], className="paramsMeteoTable", justify='around'),
                html.Div(id='filter-container'),
                html.Div([
                    # html.H5(file_name),
                    # html.H6(datetime.datetime.fromtimestamp(date)),
                    html.Div([
                        html.Div([
                            html.P("Insert X axis data"),
                            dcc.Dropdown(id='xaxis-data',
                                         options=[{'label': x, 'value': x} for x in df.columns]),
                        ], className=""),
                        html.Div([
                            html.P("Insert Y axis data"),
                            dcc.Dropdown(id='yaxis-data',
                                         options=[{'label': x, 'value': x} for x in df.columns]),
                        ], className=""),
                        html.Div([
                        html.P("Select data for choropleth map"),
                        dcc.Dropdown(id='map-data',
                                     options=[{'label': x, 'value': x} for x in df.columns]),
                        ], className=""),
                    ], className="axis"),
                    dcc.RadioItems(id='choose-graph-type',
                                   options=[
                                       {'label': 'Bar Graph', 'value': 'Bar'},
                                       {'label': 'Scatter Plot', 'value': 'Scatter'},
                                       {'label': 'Line Plot', 'value': 'Line'},
                                       {'label': 'Pie Plot', 'value': 'Pie'}
                                   ],
                                   value='Bar'
                                   ),
                    html.Br(),
                    html.Button(id="submit-button", className='button', children="Create Graph"),
                ], className="paramsMeteoParameters"),
                dbc.Row([ # for Bar Graph, Scatter Plot,Line Plot and Pie Plot
                    dbc.Col([
                        html.Div(id='output-div'),
                            ],# width={'size':3, 'offset':1, 'order':1},
                            xs=12, sm=12, md=12, lg=10, xl=10
                            ),
                        ], justify='around'),
                dbc.Row([ # Choropleth Map
                    dbc.Col([
                        html.Div(id='output-map'),
                        html.Hr()
                    ],xs=12, sm=12, md=12, lg=10, xl=10),
                ],justify='around'),                             
                html.Div([
                    html.Div([
                        # parameters for creating phylogeography trees
                        html.H4("select the name of the column to analyze"),
                        html.P('The values of the column must be numeric for the program to work properly.'),
                        dcc.Checklist(id='col-analyze',
                                      options=[{'label': x, 'value': x} for x in df._get_numeric_data().columns],
                                      labelStyle={'display': 'inline-block', 'marginRight': '20px'}
                                      ),
                        html.Br(),
                        html.Button(id="submit-forTree", className='button primary', children="Submit"),
                        html.Hr(),
                    ], className="axis")
                ], className="paramsMeteoParameters"),
                dbc.Row([ # Climatic tree
                    dbc.Col([
                        html.Div(id='climatic-tree'),
                    ],xs=12, sm=12, md=12, lg=10, xl=10),
                ],justify='around'),      
            ], className="params_meteo"),
        ], className="ParametersSectionInside"),
    ], className="ParametersSection")

    return param_selection
"""
operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

@callback(
    Output('datatable-interactivity', "data"),
    Input('datatable-interactivity', "page_current"),
    Input('datatable-interactivity', "page_size"),
    Input('datatable-interactivity', "sort_by"),
    Input('datatable-interactivity', "filter_query"))
def update_table(page_current, page_size, sort_by, filter):
    print("allo c'est karl")
    filtering_expressions = filter.split(' && ')
    tmp_dff = dff
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            tmp_dff = tmp_dff.loc[getattr(tmp_dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            tmp_dff = tmp_dff.loc[tmp_dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            tmp_dff = tmp_dff.loc[tmp_dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        tmp_dff = tmp_dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )
    logger.info(tmp_dff)
    return tmp_dff.iloc[
        page_current*page_size: (page_current + 1)*page_size
    ].to_dict('records')
"""
@callback(Output('output-div', 'children'),
              [Input('submit-button','n_clicks')],
              State('choose-graph-type','value'),
              State('stored-data','data'),
              State('xaxis-data','value'),
              State('yaxis-data', 'value')
              )
def make_graphs(n, graph_type, filter_query, x_data, y_data):
    #edge case if only choro map is selected
    if n is None:
        return dash.no_update
    else:
        if graph_type == 'Bar':
            fig = px.bar(filter_query, x=x_data, y=y_data)
        if graph_type =='Scatter':
            fig = px.scatter(filter_query, x=x_data, y=y_data)
        if graph_type == 'Line':
            fig = px.line(filter_query, x=x_data, y=y_data)
        if graph_type == 'Pie':
            fig = px.pie(filter_query, values=y_data, names=x_data, labels=x_data)
        figures.append(dcc.Graph(figure=fig))
    return figures

# Choropleth Map
@callback(
    Output('output-map','children'),
    Input('submit-button','n_clicks'),
    State('datatable-interactivity','data'),
    State('map-data', 'value')
)

def update_output(num_clicks, data, val_selected):
    if num_clicks is None:
        return dash.no_update
    else:
        if "iso_alpha" in data[0].keys():
            fig = px.choropleth(data, locations="iso_alpha",scope="world",
                                color=val_selected,
                                projection='natural earth',
                                color_continuous_scale=px.colors.sequential.Turbo)

            fig.update_layout(title=dict(font=dict(size=28),x=0.5,xanchor='center'),
                            margin=dict(l=60, r=60, t=50, b=50))

            return dcc.Graph(figure=fig)



#Après integration aphylo dans le code, on pourra work sur le code ci-dessous pour créer le newick file

# phylogeography trees : newick files
@callback(
    Output('climatic-tree','children'),
    Input('submit-forTree','n_clicks'),
    State('col-analyze', 'value')
)
def update_output(n, names):
    if n is None:
        return dash.no_update
    else:
        col_names = ['id'] + names
        climatic_trees = aPhyloGeo.climaticPipeline(data_climatic, col_names)
        elements = []
        for tree in climatic_trees.values():
            nodes, edges = generate_elements(tree)
            elements.append(nodes + edges)
        return html.Div(children=[generate_tree(elem) for elem in elements])
        
def generate_tree(elem):
     return html.Div([
            cyto.Cytoscape(
                id='cytoscape',
                elements=elem,
                stylesheet=stylesheet,
                layout=layout,
                style={
                    'height': '95vh',
                    'width': '100%'
                }
            )
        ])
# for download buttonv
#     Input("btn-newick", "n_clicks"),
#     State('input_fileName','value'),
#     prevent_initial_call=True,

# def func(n_clicks, fileName):
#     if n_clicks is None:
#         return dash.no_update
#     else:
#         return dcc.send_file(fileName)



#Button to extract all graphs to a pdf using js https://community.plotly.com/t/exporting-multi-page-dash-app-to-pdf-with-entire-layout/37953/3 ++


def generate_elements(tree, xlen=30, ylen=30, grabbable=False):
    def get_col_positions(tree, column_width=80):
        """Create a mapping of each clade to its column position."""
        taxa = tree.get_terminals()

        # Some constants for the drawing calculations
        max_label_width = max(len(str(taxon)) for taxon in taxa)
        drawing_width = column_width - max_label_width - 1

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
            'classes': 'nonterminal'
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


layout = {'name': 'preset'}

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
        'style': {'background-opacity': 0,
                  'background-color':"pink"}
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
            'background-color': "pink"
        }
    }
]


@callback(Output('cytoscape', 'stylesheet'),
              [Input('cytoscape', 'mouseoverEdgeData')])
def color_children(edgeData):
    if edgeData is None:
        return stylesheet

    if 's' in edgeData['source']:
        val = edgeData['source'].split('s')[0]
    else:
        val = edgeData['source']

    children_style = [{
        'selector': f'edge[source *= "{val}"]',
        'style': {
            'line-color': 'white'
        }
    }]

    return stylesheet + children_style

