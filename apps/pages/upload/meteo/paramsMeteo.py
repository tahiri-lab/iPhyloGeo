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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
figures =[]

def create_table(file):
    df = pd.DataFrame(file['df'])
    #global dff 
    #dff = df
    file_name = file['file_name']

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
                        html.H4("Inset the name of the column containing the sequence Id"),
                        dcc.Dropdown(id='col-specimens',
                                     options=[{'label': x, 'value': x} for x in df.columns]),
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
                ], className="paramsMeteoParameters")
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
"""
# phylogeography trees : newick files
@callback(
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

# for download buttonv
    Input("btn-newick", "n_clicks"),
    State('input_fileName','value'),
    prevent_initial_call=True,

def func(n_clicks, fileName):
    if n_clicks is None:
        return dash.no_update
    else:
        return dcc.send_file(fileName)
"""


#Button to extract all graphs to a pdf using js https://community.plotly.com/t/exporting-multi-page-dash-app-to-pdf-with-entire-layout/37953/3 ++