from dash import html, dash_table, callback, Output, State, Input, dcc, clientside_callback, ClientsideFunction
import dash
import json
import dash_cytoscape as cyto
import math
from Bio import Phylo
from io import StringIO
from flask import request
import utils.utils as utils
from db.controllers.files import str_csv_to_df
from Bio import AlignIO, SeqIO
import dash_bio as dashbio
import pandas as pd
from pprint import pprint


dash.register_page(__name__, path_template='/result/<result_id>')

layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="dummy-share-result-output", style={"display": "none"}),
    html.Div(id="dummy-table-collapse", style={"display": "none"}),
    html.Div(id="dummy-climatic-collapse", style={"display": "none"}),
    html.Div(id="dummy-genetic-collapse", style={"display": "none"}),
    html.Div([
        html.Div([
            html.Div([
                html.H1(id='results-name', className="title"),
                html.Div([
                    html.Img(src='../../assets/icons/share.svg', id="share_result", className="share_icon"),
                    html.Div('Link copied to your clipboard', id="share_tooltip", className="tooltips"),
                ]),
            ], className="header"),
            html.H2(id='results-table-title', className="title"),
            html.Div(id='output-results', className="results-row"),
            html.Button('Download Genetic Tree', id='download-button-genetic', className="download-button"),
            html.Button('Download Climatic Tree', id='download-button-climatic', className="download-button"),
            html.Button('Download MSA alignment', id='download-button-msa', className="download-button"),
            html.Button('Download data', id='download-button-data', className="download-button"),
            html.Button('Alignment Chart', id='download-alignment', className="download-button"),
             html.Div([
                html.Div(id='select-alignment-position'),
                html.Div(id='alignment-chart'),
            ]),
            dcc.Download(id='download-link-results'),
            html.H2(id="climatic-tree-title", className="title"),
            html.Div([
                html.Div(id='climatic-tree'),
            ], className="tree", id="climatic-tree-container"),
            html.H2(id="genetic-tree-title", className="title"),
            html.Div([
                html.Div(id='genetic-tree'),
            ], className="tree", id="genetic-tree-container"),
        ], className='treeContainer'),
    ], className="result")
], className="resultContainer")


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='share_result_function'
    ),
    Output("dummy-share-result-output", "children"),  # needed for the callback to trigger
    Input("share_result", "n_clicks"),
    prevent_initial_call=True,
)


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
    Output('results-table-title', 'children'),
    Output('output-results', 'children'),
    Input('url', 'pathname'),
)
def show_genetic_table(path):
    result_id = path.split('/')[-1]
    result = utils.get_result(result_id)

    if 'genetic' not in result['result_type'] or 'output' not in result:
        return None, None

    data = str_csv_to_df(result['output'])
    return (
        html.Div([
            html.Div('Results table', className="title"),
            html.Img(src='../../assets/icons/angle-down.svg', id="results-table-collapse-button", className="icon collapse-icon")
        ], className="section"),
        html.Div([
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
                row_selectable="multi",     # allow user to select 'multi' or 'single' rows
                style_data={
                    'color': 'var(--reverse-black-white-color)',
                    'backgroundColor': 'var(--table-bg-color'
                },
            )
        ])
    )


@callback(
    Output('climatic-tree-title', 'children'),
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

    result = utils.get_result(result_id)
    if 'climatic' not in result['result_type']:
        return None, None

    climatic_trees = result['climatic_trees']
    tree_names = list(climatic_trees.keys())
    climatic_elements = []
    for tree in climatic_trees.values():
        tree = Phylo.read(StringIO(tree), "newick")
        nodes, edges = generate_elements(tree)
        climatic_elements.append(nodes + edges)

    return (
        html.Div([
            html.Div('Climate Trees', className="title"),
            html.Img(src='../../assets/icons/angle-down.svg', id="results-climatic-collapse-button", className="icon collapse-icon")
        ], className="section"),
        html.Div(children=[generate_tree(elem, name) for elem, name in zip(climatic_elements, tree_names)], className="tree-sub-container")
    )


@callback(
    Output("download-link-results", "data"),
    [Input("download-button-genetic", "n_clicks"),
     Input("download-button-climatic", "n_clicks"),
     Input("download-button-msa", "n_clicks"),
     Input("download-button-data", "n_clicks"),
     Input('url', 'pathname')],
    prevent_initial_call=True
)
def download_results(btn_genetic, btn_climatic, btn_msa, btn_data, path):

    result_id = path.split('/')[-1]
    result = utils.get_result(result_id)
    result_genetic_trees = result['genetic_trees']
    result_climatic_trees = result['climatic_trees']
    result_msa = result['msaSet']

    data_results = str_csv_to_df(result['output'])

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "download-button-genetic":
        data_genetic = "".join(list(result_genetic_trees.values()))
        return dict(content=data_genetic, filename=result["name"] + "_genetic_trees.newick")
    if trigger_id == "download-button-climatic":
        data_climatic = "".join(list(result_climatic_trees.values()))
        return dict(content=data_climatic, filename=result["name"] + "_climatic_trees.newick")
    if trigger_id == "download-button-msa":
        data_msa = json.dumps(result_msa)
        return dict(content=data_msa, filename=result["name"] + "_msa.json")
    if trigger_id == "download-button-data":
        return dict(content=data_results.to_csv(header=True, index=False), filename=result["name"] + "_results.csv")


@callback(
    Output('genetic-tree-title', 'children'),
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
    result = utils.get_result(result_id)
    if 'genetic' not in result['result_type'] or 'genetic_trees' not in result:
        return None, None

    genetic_trees = result['genetic_trees']
    tree_names = list(genetic_trees.keys())

    genetic_elements = []
    for tree in genetic_trees.values():
        tree = Phylo.read(StringIO(tree), "newick")
        nodes, edges = generate_elements(tree)
        genetic_elements.append(nodes + edges)

    return (
        html.Div([
            html.Div('Genetic Trees', className="title"),
            html.Img(src='../../assets/icons/angle-down.svg', id="results-genetic-collapse-button", className="icon collapse-icon")
        ], className="section"),
        html.Div(children=[generate_tree(elem, name) for elem, name in zip(genetic_elements, tree_names)], className="tree-sub-container")
    )


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
    ], id=name, className="tree-container")


#-----------------------------------
# select gene
@callback(
    Output("select-alignment-position", "children"),
    Input("download-alignment", "n_clicks"),
    State('datatable-interactivity', "derived_virtual_data"),
    State('datatable-interactivity', 'derived_virtual_selected_rows'),
    prevent_initial_call=True,
)
def select_position_asm(n_clicks,all_rows_data,select_rows):
    if n_clicks is None:
        return dash.no_update
    else:
        #if row['Gene'] != 'output/reference_gene.fasta':
        dff = pd.DataFrame(all_rows_data)
        df_select = dff[dff.index.isin(select_rows)]

        genes_selected = df_select['Gene'].unique()
        #print(genes_selected)
        
        positions_selected = df_select['Position in ASM'].unique()
        return html.Div([
            html.H4("Select position ASM for alignment visualisation"),
            dcc.RadioItems(id='choose-align-gene',
                        options=[{'label':x, 'value':x} for x in positions_selected],),  
                        ])



@callback(
    Output("alignment-chart", "children"),
    Input('url', 'pathname'),
    Input('choose-align-gene','value'),
    prevent_initial_call=True
)
def make_alignment_chart(path,sliding_window_value):

    result_id = path.split('/')[-1]
    result = utils.get_result(result_id)
    if sliding_window_value != None:        
        val_split = sliding_window_value.split('_')
        first_value = val_split[0]
        second_value = val_split[1]
        
        file_gene_id = result['genetic_files_id']
        print(file_gene_id)
        file_gene = utils.get_file_from_db(file_gene_id)
        print(file_gene)
        data_gene = file_gene['file']
        data = {}
        pprint(data_gene)
        """
        for key in data_gene.keys():
            data +='>'+ key + '\n'
            #app.logger.info(record.seq[0:250])
            #app.logger.info("Je suis le record" +record.seq[first_value:second_value])
            data +=str(data_gene[key][int(first_value):int(second_value)])+'\n'
        """
        
        result = SeqIO.to_dict(data_gene)
        for key in result:
            result[key] = str(result[key].seq)
        #pprint(result)
        for key in result.keys():
            data[key] = result[key][int(first_value):int(second_value)]
        pprint(data)
        test = ""
        for key in data.keys():
            test +='>'+ key + '\n'
            test +=str(data[key])+'\n'
        
        #for record in SeqIO.parse(StringIO(data_gene), "fasta"):
        #    data[record.id] = str(record.seq[int(first_value):int(second_value)])
        #pprint(data)
        #make_alignement_chart(align_chart_path)
        pprint(test)
        layout = alignment_chart(test)
        return layout


def alignment_chart(data):
    return html.Div([
                    dashbio.AlignmentChart(
                        id='my-alignment-viewer',
                        data=data,
                        tilewidth=30,
                        height=900,
                    ),
                    html.Br(),
                    html.Br(),
                    html.Div(id='alignment-viewer-output'),
                ])

def generate_elements(tree, xlen=30, ylen=30, grabbable=False):
    def get_col_positions(tree, column_width=25):
        taxa = tree.get_terminals()

        # Some constants for the drawing calculations
        max_label_width = max(len(str(taxon)) for taxon in taxa)
        drawing_width = column_width - max_label_width - 1

        depths = tree.depths()
        # If there are no branch lengths, assume unit branch lengths
        if not max(depths.values()):
            depths = tree.depths(unit_branch_lengths=True)
            # Potential drawing overflow due to rounding, 1 char per tree layer
        fudge_margin = int(math.ceil(math.log(len(taxa), 2)))
        cols_per_branch_unit = ((drawing_width - fudge_margin) / float(max(depths.values())))
        return dict((clade, int(blen * cols_per_branch_unit + 1.0))
                    for clade, blen in depths.items())

    def get_row_positions(tree):
        taxa = tree.get_terminals()
        positions = dict((taxon, 2 * idx) for idx, taxon in enumerate(taxa))

        def calc_row(clade):
            for subclade in clade:
                if subclade not in positions:
                    calc_row(subclade)
            positions[clade] = ((positions[clade.clades[0]] + positions[clade.clades[-1]]) // 2)

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


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='collapse_result_section_function'
    ),
    Output("dummy-climatic-collapse", "children"),  # needed for the callback to trigger
    [Input("results-climatic-collapse-button", "n_clicks"),
     Input("climatic-tree-container", "id"),
     Input("results-climatic-collapse-button", "id")],
    prevent_initial_call=True,
)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='collapse_result_section_function'
    ),
    Output("dummy-table-collapse", "children"),  # needed for the callback to trigger
    [Input("results-table-collapse-button", "n_clicks"),
     Input("output-results", "id"),
     Input("results-table-collapse-button", "id")],
    prevent_initial_call=True,
)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='collapse_result_section_function'
    ),
    Output("dummy-genetic-collapse", "children"),  # needed for the callback to trigger
    [Input("results-genetic-collapse-button", "n_clicks"),
     Input("genetic-tree-container", "id"),
     Input("results-genetic-collapse-button", "id")],
    prevent_initial_call=True,
)


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
            'background-color': "pink",
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
