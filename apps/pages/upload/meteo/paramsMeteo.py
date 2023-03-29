import dash_bootstrap_components as dbc

from dash import dcc, html, State, Input, Output, dash_table
import dash_daq as daq
from dash.dependencies import Input, Output, ClientsideFunction


def create_tables(file):
    df = file['df']
    file_name = file['file_name']

    param_selection = html.Div([
        html.Div([
            html.Div([
                html.H2('Create Phylogeography Trees', className="title"),  # title
                dbc.Row([
                    dbc.Col([
                        dash_table.DataTable(
                            data=df.to_dict('records'),
                            columns=[{'name': i, 'id': i} for i in df.columns],
                            page_size=15,
                            style_header={
                                'backgroundColor': '#f5f4f6',
                            },
                        ),
                        dcc.Store(id='stored-data', data=df.to_dict('records')),
                        # html.Hr(),  # horizontal line
                    ], ),

                ], className="paramsMeteoTable", justify='around'),

                html.Div([
                    # html.H5(file_name),
                    # html.H6(datetime.datetime.fromtimestamp(date)),
                    html.Div([
                        html.Div([
                            html.P("Inset X axis data"),
                            dcc.Dropdown(id='xaxis-data',
                                         options=[{'label': x, 'value': x} for x in df.columns]),
                        ], className=""),
                        html.Div([
                            html.P("Inset Y axis data"),
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
                                       {'label': 'Scatter Plot', 'value': 'Scatter'}
                                   ],
                                   value='Bar'
                                   ),
                    html.Br(),
                    html.Button(id="submit-button", className='button', children="Create Graph"),
                ], className="paramsMeteoParameters"),

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