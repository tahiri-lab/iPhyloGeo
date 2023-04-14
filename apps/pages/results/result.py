from dash import html, dash_table, callback, Output, Input, dcc
import dash
import dash_cytoscape as cyto
import math
from Bio import Phylo
from io import StringIO
from flask import request
import utils.utils as utils
from db.controllers.files import str_csv_to_df

dash.register_page(__name__, path_template='/result/<result_id>')

layout = html.Div([
    dcc.Location(id="url"),
    html.Div([
        html.Div([
            html.H1(id='results-name', className="title"),
            html.H2('Results table', className="title"),
            html.Div(id='output-results', className="results-row"),
            html.H2('Climatic Trees', className="title"),
            html.Div([
                html.Div(id='climatic-tree'),
            ], className="tree"),
            html.H2('Genetic Trees', className="title"),
            html.Div([
                html.Div(id='genetic-tree'),
            ], className="tree"),
        ], className='treeContainer'),
    ], className="result")
], className="resultContainer")


@callback(
    Output('results-name', 'children'),
    Input('url', 'pathname'),
)
def show_result_name(path):
    """
    args:
        path (str): the path of the page
    returns:
        html.Div: the div containing the name of the result
    """
    result_id = path.split('/')[-1]
    title = utils.get_result(result_id)['name']
    return html.Div(title, className="title")


@callback(
    Output('output-results', 'children'),
    Input('url', 'pathname'),
)
def show_result(path):
    result_id = path.split('/')[-1]

    result = utils.get_result(result_id)
    data = {}
    # TODO - a delete plus tard
    column_header = ["Gene", "Phylogeographic tree", "Name of species", "Position in ASM", "Bootstrap mean", "Least-Square distance"]
    for header in column_header:
        data[header] = [header]
    for row in result['output']:
        for i in range(len(row)):
            data[column_header[i]].append(row[i])
    data = str_csv_to_df(data)
    return html.Div([
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
            style_data={
                'color': 'var(--reverse-black-white-color)',
                'backgroundColor': 'var(--table-bg-color'
            },
        ),
    ])


@callback(
    Output('climatic-tree', 'children'),
    Input('url', 'pathname'),
)
def create_climatic_trees(path):
    """
    This function creates the list of divs containing the climatic trees

    args:
        path (str): the path of the page
    returns:
        html.Div: the div containing the climatic trees
    """
    result_id = path.split('/')[-1]
    add_to_cookie(result_id)

    climatic_trees = utils.get_result(result_id)['climatic_trees']
    tree_names = list(climatic_trees.keys())
    climatic_elements = []
    for tree in climatic_trees.values():
        tree = Phylo.read(StringIO(tree), "newick")
        nodes, edges = generate_elements(tree)
        climatic_elements.append(nodes + edges)

    return html.Div(
        children=[generate_tree(elem, name) for elem, name in zip(climatic_elements, tree_names)],
        className="tree-sub-container"
    )


@callback(
    Output('genetic-tree', 'children'),
    Input('url', 'pathname'),
)
def create_genetic_trees(path):
    """
    This function creates the list of divs containing the genetic trees
    args:
        path (str): the path of the page
    returns:
        html.Div: the div containing the genetic trees
    """
    result_id = path.split('/')[-1]

    genetic_trees = utils.get_result(result_id)['genetic_trees']
    tree_names = list(genetic_trees.keys())

    genetic_elements = []
    for tree in genetic_trees.values():
        tree = Phylo.read(StringIO(tree), "newick")
        nodes, edges = generate_elements(tree)
        genetic_elements.append(nodes + edges)

    return html.Div(children=[generate_tree(elem, name) for elem, name in zip(genetic_elements, tree_names)], className="tree-sub-container")

def add_to_cookie(result_id):
    """
    This function takes the result id and adds it to the cookie
    args:
        result_id (str): the id of the result to add to the cookie
    """

    auth_cookie = request.cookies.get("AUTH")
    auth_cookie_value = utils.make_cookie(result_id, auth_cookie)

    response = dash.callback_context.response
    response.set_cookie("AUTH", auth_cookie_value)


# the following code is taken from https://dash.plotly.com/cytoscape/biopython
def generate_tree(elem, name):
    return html.Div([
        html.H3(name, className="treeTitle"),  # title
        cyto.Cytoscape(
            id='cytoscape',
            elements=elem,
            stylesheet=stylesheet,
            layout={'name': 'preset'},
            style={
                'height': '350px',
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

            if clade.confidence:
                cy_source['data']['confidence'] = clade.confidence

            nodes.append(cy_support_node)
            edges.extend([cy_support_edge, cy_edge])

            add_to_elements(child, child_id)

    col_positions = get_col_positions(tree)
    row_positions = get_row_positions(tree)

    nodes = []
    edges = []

    add_to_elements(tree.clade, 'r')

    return nodes, edges


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
                  'background-color': "pink"}
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
