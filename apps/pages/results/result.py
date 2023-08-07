from dotenv import dotenv_values
from dash import html, dash_table, callback, Output, Input, State, dcc, clientside_callback, ClientsideFunction
import dash
import json
import dash_cytoscape as cyto
import math
import numpy as np
from Bio import Phylo
from io import StringIO
from flask import request
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.utils as utils
from db.controllers.files import str_csv_to_df
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

with open(os.getcwd() + "\\apps\\pages\\results\\password.env") as f:
    password = f.read().split('=')[1]

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
                    html.Div([
                        html.Img(src='../../assets/icons/share.svg', id="share_result", className="options-icons"),
                    ], className="header-options"),
                    html.Div('Link copied to your clipboard', id="share_tooltip", className="tooltips"),
                ]),
            ], className="header"),

            html.Div([
                html.H2("If you would like to receive the URL by email, you can enter your address below.",
                        style={'text-align': 'center', 'color': '#AD00FA', 'font-size': '14px'}),
                html.Div([
                    dcc.Input(id='user-input', type='email', placeholder='Write your mail here...'),  # Barre de saisie
                    html.Button([html.Span('Submit', style={'font-size': '18px'})], id='submit-button',
                                n_clicks=0,
                                style={'font-family': 'Calibri', 'color': 'white',
                                       'background-color': '#AD00FA',
                                       'border-radius': '10px'}),  # Bouton "Submit"
                ], className='input-container', style={'display': 'flex', 'justify-content': 'center'}),
            ], className='center-container', style={'text-align': 'center'}),

            html.H2(id='results-table-title', className="title"),
            html.Div([
                html.Div(id='output-results'),
                html.Div(id='output-results-graph', className="graph"),
            ], id='results-row', className="results-row"),
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
    Input('submit-button', 'n_clicks'),
    State('user-input', 'value')
)
def handle_submit_click(pathname, n_clicks, user_email):
    if n_clicks and n_clicks > 0 and user_email:
        # Collect URL
        url = dash.callback_context.inputs['url.pathname']
        # Send URL in email message
        subject = 'Process finished'
        content = f"Votre processus Aphylogeo situé à l'URL suivante : http://localhost:8050{url}"
        # Call send_alarm_email function with URL
        send_alarm_email(subject, content, user_email)
    return None


def send_alarm_email(subject, content, user_email):
    try:
        message = MIMEMultipart()
        message["From"] = user_email
        message['To'] = user_email
        message['Subject'] = subject
        # body

        plain_text = MIMEText(content, _subtype='plain', _charset='UTF-8')
        message.attach(plain_text)

        my_message = message.as_string()
        email_session = smtplib.SMTP('smtp.gmail.com', 587)
        email_session.starttls()
        email_session.login('aphylogeotest@gmail.com', password)
        email_session.sendmail('aphylogeotest@gmail.com', user_email, my_message)
        email_session.quit()
    except Exception as e:
        print(e)
        print("Unable to send email")


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
    Output('output-results-graph', 'children'),
    Input('url', 'pathname'),
)
def show_complete_results(path):
    """
    args:
        path (str): the path of the page
    returns:
        html.Div: the div containing the header (title & download button) of the results
        html.Div: the div containing the results tabke
        html.Div: the div containing the results graph
    """
    result_id = path.split('/')[-1]
    result = utils.get_result(result_id)

    if 'genetic' not in result['result_type'] or 'output' not in result:
        return None, None, None
    results_data = str_csv_to_df(result['output'])

    return create_result_table_header(), create_result_table(results_data), create_result_graphic(results_data)


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
        htmml.Div: the div containing the header (title & download button) of the climatic trees
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

    return create_climatic_trees_header(), html.Div(children=[generate_tree(elem, name) for elem, name in zip(climatic_elements, tree_names)], className="tree-sub-container")


@callback(
    Output("download-link-results", "data"),
    Input('url', 'pathname'),
    Input("download-button-genetic", "n_clicks"),
    Input("download-button-climatic", "n_clicks"),
    Input("download-button-aligned", "n_clicks"),
    Input("download-button-complete", "n_clicks"),
    prevent_initial_call=True,
)
def download_results(path, btn_genetic, btn_climatic, btn_aligned, btn_complete):
    """
    This function creates the list of divs containing the genetic trees
    Because the buttons are not created in the initial layout, we need to use the suppress_callback_exceptions

    args:
        path (str): the path of the page
        btn_genetic : dummy inpput needed to trigger the callback
        btn_climatic : dummy inpput needed to trigger the callback
        btn_msa : dummy inpput needed to trigger the callback
        btn_data : dummy inpput needed to trigger the callback
    """

    result_id = path.split('/')[-1]
    result = utils.get_result(result_id)

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "download-button-genetic" and btn_genetic:
        result_genetic_trees = result['genetic_trees']
        data_genetic = "".join(list(result_genetic_trees.values()))
        return dict(content=data_genetic, filename=result["name"] + "_genetic_trees.newick")
    if trigger_id == "download-button-climatic" and btn_climatic:
        result_climatic_trees = result['climatic_trees']
        data_climatic = "".join(list(result_climatic_trees.values()))
        return dict(content=data_climatic, filename=result["name"] + "_climatic_trees.newick")
    if trigger_id == "download-button-aligned" and btn_aligned:
        result_msa = result['msaSet']
        data_msa = json.dumps(result_msa)
        return dict(content=data_msa, filename=result["name"] + "_msa.json")
    if trigger_id == "download-button-complete" and btn_complete:
        data_results = str_csv_to_df(result['output'])
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
        htmml.Div: the div containing the header (title & download button) of the genetic trees
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

    return create_genetic_trees_header(), html.Div(children=[generate_tree(elem, name) for elem, name in zip(genetic_elements, tree_names)], className="tree-sub-container")


def add_to_cookie(result_id):
    """
    This function takes the result id and adds it to the cookie
    args:
        result_id (str): the id of the result to add to the cookie
    """

    auth_cookie = request.cookies.get("AUTH")
    response = dash.callback_context.response
    utils.make_cookie(result_id, auth_cookie, response)


def create_result_table_header():
    """
    This function creates the header of the results table
    returns:
        html.Div: the div containing the header of the results table
    """

    return html.Div([
        html.Div([
            html.Div('Results', className="title"),
            html.Img(src='../../assets/icons/angle-down.svg', id="results-table-collapse-button",
                     className="icon collapse-icon"),
        ], className="sub-section"),
        html.Div([
            html.Div([
                html.Div('Aligned genetic sequences', className="text"),
                html.Img(src='../../assets/icons/download.svg', className="icon"),
            ], className="individual-tree-download-container button download", id='download-button-aligned'),
            html.Div([
                html.Div('output.csv', className="text"),
                html.Img(src='../../assets/icons/download.svg', className="icon"),
            ], className="individual-tree-download-container button download", id='download-button-complete'),
        ], className="download-container")
    ], className="section")


def create_result_table(data):
    """
    This function creates the results table
    args:
        data (pandas.DataFrame): the data to display in the table
    returns:
        dash_table.DataTable: the table containing the results
    """

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
            row_selectable="multi",     # allow user to select 'multi' or 'single' rows
            style_data={
                'color': 'var(--reverse-black-white-color)',
                'backgroundColor': 'var(--table-bg-color'
            },
        )
    ])


def create_result_graphic(results_data):
    """
    This function creates the results graphic
    args:
        data (pandas.DataFrame): the data to display in the table
    returns:
        dash_table.DataTable: the table containing the results
    """
    results_data['starting_position'] = [int(x.split("_")[0]) for x in results_data['Position in ASM']]

    results_data = results_data[['starting_position', 'Bootstrap mean', 'Least-Square distance']]
    results_data = results_data.groupby('starting_position').mean().reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=results_data["starting_position"],
            y=results_data["Bootstrap mean"],
            name="bootstrap mean",
            line=dict(color="#AD00FA")
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=results_data["starting_position"],
            y=results_data["Least-Square distance"],
            name="LS distance",
            line=dict(color="#00faad")
        ),
        secondary_y=True,
    )
    fig.update_layout(title_text="Bootstrap mean and LS distance", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    fig.update_xaxes(
        title_text="Position in ASM",
        gridcolor='rgba(255,255,255,0.2)'
    )
    fig.update_yaxes(
        title_text="<b>Bootstrap mean</b>",
        secondary_y=False,
        gridcolor='rgba(255,255,255,0.2)'
    )
    fig.update_yaxes(
        title_text="<b>LS distance</b>",
        secondary_y=True,
        gridcolor='rgba(255,255,255,0.2)'
    )

    min_bootstrap = results_data['Bootstrap mean'].min()
    max_bootstrap = results_data['Bootstrap mean'].max()
    bootstrap_ticks = np.linspace(min_bootstrap, max_bootstrap, 6)

    min_ls = results_data['Least-Square distance'].min()
    max_ls = results_data['Least-Square distance'].max()
    ls_ticks = np.linspace(min_ls, max_ls, 6)

    fig.update_layout(yaxis1_tickvals=bootstrap_ticks, yaxis2_tickvals=ls_ticks)

    return dcc.Graph(figure=fig)


def create_climatic_trees_header():
    """
    This function creates the header for the climatic trees
    """
    return html.Div([
        html.Div([
            html.Div('Climatic Trees', className="title"),
            html.Img(src='../../assets/icons/angle-down.svg', id="results-climatic-collapse-button", className="icon collapse-icon"),
        ], className="sub-section"),
        html.Div([
            html.Div('Climatic Trees', className="text"),
            html.Img(src='../../assets/icons/download.svg', className="icon"),
        ], className="individual-tree-download-container button download", id='download-button-climatic'),
    ], className="section")


def create_genetic_trees_header():
    """
    This function creates the header for the genetic trees
    """
    return html.Div([
        html.Div([
            html.Div('Genetic Trees', className="title"),
            html.Img(src='../../assets/icons/angle-down.svg', id="results-genetic-collapse-button", className="icon collapse-icon"),
        ], className="sub-section"),
        html.Div([
            html.Div('Genetic Trees', className="text"),
            html.Img(src='../../assets/icons/download.svg', className="icon"),
        ], className="individual-tree-download-container button download", id='download-button-genetic'),
    ], className="section"),


# the following code is taken from https://dash.plotly.com/cytoscape/biopython
def generate_tree(elem, name):
    return html.Div([
        html.H3(name, className="treeTitle"),  # title
        cyto.Cytoscape(
            elements=elem,
            stylesheet=stylesheet,
            layout={'name': 'preset'},
            style={
                'height': '350px',
                'width': '100%'
            },
        )
    ], id=name, className="tree-container")


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
     Input("results-row", "id"),
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
        'style': {'background-opacity': 0}
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': '#AD00FA ',
            "source-endpoint": "inside-to-node",
            "target-endpoint": "inside-to-node",
        }
    },
    {
        'selector': '.terminal',
        'style': {
            'label': 'data(name)',
            'font-weight': 'bold',
            'color': 'white',
            'width': 10,
            'height': 10,
            "text-valign": "center",
            "text-halign": "right",
            'background-color': "#00faad"
        }
    }
]
