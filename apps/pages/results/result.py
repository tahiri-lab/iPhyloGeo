from dash import html, dash_table,callback, Output, Input,State
import dash
import dash_bootstrap_components as dbc
from pprint import pprint
from utils import utils
from db.controllers.files import str_csv_to_df
import dash_cytoscape as cyto
import math

dash.register_page(__name__, path_template='/result/<result_id>')

layout = html.Div([
    html.Div([
        html.Div([
            html.H2('Results table', className="title"),  # title
            html.Div(id='output_results'),
            html.Div(id='climatic-tree'),
        ], className="center"),
    ], className="ParametersSectionInside"),
], className="ParametersSection")

@callback(
    Output('output_results', 'children'),
    Input('result_id', "data"),
)
def show_result(result_id):
    result = utils.get_result(result_id)
    data = {}
    # TODO - a delete plus tard
    column_header = ["Gene","Phylogeographic tree","Name of species","Position in ASM","Bootstrap mean","Least-Square distance"]
    for header in column_header:
        data[header] = [header]
    for row in result['output']:
        for i in range(len(row)):
            data[column_header[i]].append(row[i])
    data = str_csv_to_df(data)
    return dbc.Col([
        dash_table.DataTable(
            id='datatable-interactivity',                                
            data=data.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in data.columns],
            filter_action="native",     # allow filtering of data by user ('native') or not ('none')
            sort_action="native",       # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",         # sort across 'multi' or 'single' columns
            page_current=0,             # page number that user is on
            page_size=15,               # number of rows visible per page
            filter_query='',            # query that determines which rows to keep in table
            #page_action="native",       # all data is passed to the table up-front or not ('none')
            #sort_by=[],                 # list of columns that user sorts table by
            style_data={
                'color': 'var(--reverse-black-white-color)',
                'backgroundColor': 'var(--table-bg-color'
            },
        ),
        # html.Hr(),  # horizontal line
    ], className="center")

"""

@callback(
    Output('climatic-tree','children'),
    Input('result_id', 'data')
)
def update_output(result_id):

    climatic_trees = utils.get_result(result_id)['climatic_trees']
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


def generate_elements(tree, xlen=30, ylen=30, grabbable=False):
    def get_col_positions(tree, column_width=80):
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

"""