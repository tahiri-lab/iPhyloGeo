import pandas as pd
import base64
import io
import os

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

from app import app

FILES_PATH = 'files/'
# TODO add this to the .env file
APP_ENV = 'local' # os.environ.get('APP_ENV', 'local')

def get_file(id, options={}):
    """
        Get the file with the given id.
        If the app is running in local mode, the file is read from the local file system.
        Otherwise, the file is read from database.
    """

    if APP_ENV == 'local':
        return read_local_file(FILES_PATH + id, options)
    else:
        return get_file_from_db(id)

def read_local_file(path, options={}):
    """ Read the file from the local file system.

    Args:
        path (string): The path of the file.
    """
    # check if the file exists
    if not os.path.isfile(path):
        return None
    # read the file
    if 'pd' in options:
        return pd.read_csv(path)

def get_file_from_db(id):
    """ Get the file from the database.

    Args:
        id (string): The id of the file.
    """
    # TODO: implement this function
    pass

def get_files_from_base64(list_of_contents, list_of_names, list_of_dates):
    app.logger.info('get_files')

    app.logger.info("list_of_contents: {}".format(list_of_contents))
    app.logger.info("list_of_names: {}".format(list_of_names))
    app.logger.info("list_of_dates: {}".format(list_of_dates))

    results = []
    for content, file_name, date in zip(list_of_contents, list_of_names, list_of_dates):
        results.append(parse_contents(content, file_name, date))
    return results

def parse_contents(content, file_name, date):
    res = {
        'file_name': file_name,
        'date': date,
    }

    try:
        content_type, content_string = content.split(',')
        decoded_content = base64.b64decode(content_string)

        if content_type == 'data:text/csv;base64':
            # Assume that the user uploaded a CSV file
            res['df'] = pd.read_csv(io.StringIO(decoded_content.decode('utf-8')))
        elif 'xls' in file_name:
            # Assume that the user uploaded an excel file
            res['df'] = pd.read_excel(io.BytesIO(decoded_content))
        elif 'fasta' in file_name:
            res['file'] = decoded_content.decode('utf-8')
        else:
            app.logger.info('Unknown file type', content_type)
            res['error'] = True

        return res
    except Exception as e:
        app.logger.info('parse_contents2 error: {}'.format(e))

def create_table(file):
    df = file['df']
    file_name = file['file_name']

    param_selection = dbc.Container([
                dbc.Row([
                        dbc.Col([
                            dash_table.DataTable(
                                    data= df.to_dict('records'),
                                    columns=[{'name': i, 'id': i} for i in df.columns],
                                    page_size=15
                                ),
                                dcc.Store(id='stored-data', data=df.to_dict('records')),

                                html.Hr(),  # horizontal line

                                # For debugging, display the raw contents provided by the web browser
                                #html.Div('Raw Content'),
                                #html.Pre(contents[0:200] + '...', style={
                                #    'whiteSpace': 'pre-wrap',
                                #    'wordBreak': 'break-all'
                                #}),
                        ],xs=12, sm=12, md=12, lg=10, xl=10),

                    ],className="g-0", justify='around'),

                dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5(file_name),
                                #html.H6(datetime.datetime.fromtimestamp(date)),
                                html.P("Inset X axis data"),
                                dcc.Dropdown(id='xaxis-data',
                                            options=[{'label':x, 'value':x} for x in df.columns]),
                                html.P("Inset Y axis data"),
                                dcc.Dropdown(id='yaxis-data',
                                            options=[{'label':x, 'value':x} for x in df.columns]),
                                html.P("Select data for choropleth map"),
                                dcc.Dropdown(id='map-data',
                                            options=[{'label':x, 'value':x} for x in df.columns]),
                                html.Br(),
                                dcc.RadioItems(id='choose-graph-type',
                                                options=[
                                                    {'label': 'Bar Graph', 'value': 'Bar'},
                                                    {'label': 'Scatter Plot', 'value': 'Scatter'}
                                                ],
                                                value='Bar'
                                            ),
                                html.Br(),
                                html.Button(id="submit-button", children="Create Graph"),
                                html.Hr(),
                            # parameters for creating phylogeography trees
                                html.H2('Create Phylogeography Trees', style={"textAlign": "center"}),  #title
                                html.H4("Inset the name of the column containing the sequence Id"),
                                dcc.Dropdown(id='col-specimens',
                                            options=[{'label':x, 'value':x} for x in df.columns]),
                                html.H4("select the name of the column to analyze"),
                                html.P('The values of the column must be numeric for the program to work properly.'),
                                dcc.Checklist(id = 'col-analyze',
                                            options =[{'label': x, 'value': x} for x in df._get_numeric_data().columns],
                                            labelStyle={'display': 'inline-block','marginRight':'20px'}
                                        ),
                                html.Br(),
                                html.Button(id="submit-forTree", children="Create Newick files"),
                                html.Hr(),

                                ])
                        ],xs=12, sm=12, md=12, lg=10, xl=10),
                ],className="g-0", justify='around'),


         ], fluid=True)

    return param_selection


def create_seq_html(file):
    file_name = file['file_name']

    if 'error' in file and file['error']:
        return html.Div([
                dcc.Markdown('Please upload a **fasta file**.'),
        ])

    return html.Div([
        dcc.Markdown('You have uploades file(s):  **{}**'.format(file_name)),
        #html.H6(datetime.datetime.fromtimestamp(date)),
        #html.Small(seq_upload),

        # For debugging, display the raw contents provided by the web browser
        #html.Div('Raw Content'),
        #html.Pre(contents[0:200] + '...', style={
            #   'whiteSpace': 'pre-wrap',
            #   'wordBreak': 'break-all'
        #})
    ])