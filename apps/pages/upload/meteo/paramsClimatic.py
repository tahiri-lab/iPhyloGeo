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

def create_table(df):
    param_selection = html.Div([
        html.Div([
            html.Div([
                html.Div([
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
                            style_data={
                                'color': 'var(--reverse-black-white-color)',
                                'backgroundColor': 'var(--table-bg-color'
                            },
                        ),
                        dcc.Store(id='stored-data', data=df.to_dict('records')),
                        # html.Hr(),  # horizontal line
                    ], className=""),

                ], className="paramsClimaticTable"),
                html.Div(id='filter-container'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div('Generate your graph', className="title"),
                            html.Div([
                                html.P("Insert X axis data"),
                                dcc.Dropdown(id='xaxis-data',
                                             options=[{'label': x, 'value': x} for x in df.columns]),
                            ], className="field"),
                            html.Div([
                                html.P("Insert Y axis data"),
                                dcc.Dropdown(id='yaxis-data',
                                             options=[{'label': x, 'value': x} for x in df.columns]),
                            ], className="field"),
                            dcc.RadioItems(id='choose-graph-type',
                                           options=[
                                               {'label': 'Bar Graph', 'value': 'Bar'},
                                               {'label': 'Scatter Plot', 'value': 'Scatter'},
                                               {'label': 'Line Plot', 'value': 'Line'},
                                               {'label': 'Pie Plot', 'value': 'Pie'}
                                           ], value='Bar', className="field graphType"),
                            html.Div([
                                html.P("Select data for choropleth map"),
                                dcc.Dropdown(id='map-data',
                                             options=[{'label': x, 'value': x} for x in df.columns]),
                            ], className="field"),
                            html.Button(id="submit-button", className='button', children="Create Graph"),
                        ], className="axisField"),
                        html.Div([
                            html.Div(id='output-map', className="choroplethMap"),
                        ], className="choroplethMapContainer"),
                    ], className="axis"),
                ], className="paramsClimaticParameters"),
                html.Div([
                    html.Div(id='output-graph', className="generatedGraph"),
                ], className="graphGeneratorContainer"),
                html.Div([
                    html.Div([
                        html.Div("Select the name of the column to analyze"),
                        dcc.Checklist(id='col-analyze',
                                      options=[{'label': x, 'value': x} for x in df._get_numeric_data().columns],
                                      labelStyle={'display': 'inline-block', 'marginRight': '20px'}
                                      ),
                    ], className="axis")
                ], className="colToAnalyseContainer")
            ], className="params_climatic"),
        ], className="ParametersSectionInside"),
    ], className="ParametersSection", id="meteo_params_section")

    return param_selection

@callback(Output('output-graph', 'children'),
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
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='var(--reverse-black-white-color)')),
        fig.update_annotations(font_color='white'),

    return figures

# Choropleth Map
@callback(
    Output('output-map','children'),
    Input('upload-data','contents'),
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

            fig.update_geos(
                showocean=True, oceancolor="LightBlue",
                showlakes=True, lakecolor="Blue",
                showrivers=True, rivercolor="Blue"
            )

            fig.update_layout(title=dict(font=dict(size=28),x=0.5,xanchor='center'),
                            margin=dict(l=60, r=60, t=50, b=50), paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)'),

            fig.update_annotations(text="No matching data found")

            return dcc.Graph(figure=fig)
        else:
            map_fig = html.Div([
                html.Div("No map to display.")
            ], className="noMapAvailable")
            return map_fig


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