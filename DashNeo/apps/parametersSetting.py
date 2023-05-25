from dash import dcc, html, dash_table
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from app import app
import dash
from apps import config_manager
from apps import neoCypher_manager
from apps import geoData_manager
from apps import seqData_manager
import pandas as pd
import yaml
import shutil
# import time
import os


# -----------------------------------------
# prepare the structure of DashTable
envFactor_list = ['precipitation', 'relative_humidity', 'specific_humidity', 'sky_shortwave_irradiance',
                  'wind_speed_10meters_range', 'wind_speed_50meters_range'
                  ]
deletable_columns = [{"name": i, "id": i, "deletable": True,
                      "selectable": False, "hideable": False}
                     for i in envFactor_list]

table_columns = [
    {"name": "id", "id": "id", "deletable": False,
        "selectable": False, "hideable": False},
    {"name": "location", "id": "location", "deletable": False,
        "selectable": False, "hideable": False},
    {"name": "collection_date", "id": "collection_date",
        "deletable": False, "selectable": False, "hideable": False},
]
table_columns.extend(deletable_columns)

data_env = {
    'id': [],
    'location': [],
    'collection_date': [],
    'precipitation': [],
    'relative_humidity': [],
    'specific_humidity': [],
    'sky_shortwave_irradiance': [],
    'wind_speed_10meters_range': [],
    'wind_speed_50meters_range': []
}
df_env = pd.DataFrame(data_env)

# --------------------------------------
layout = html.Div([
    html.Div(html.H2("Parameters Setting"), style={"text-align": "center"}),
    html.Hr(),
    # html.Div(id='page-2-content'),
    # --------------------------------------------------------
    # Get info from page neoExplore
    # html.P(f"Content of dcc.Store: {stored_data}"),
    dbc.Row([
            dbc.Col([
                dbc.Button("Get Input Id",
                           id="get_input_name", outline=True, color="success", className="me-1"),
                html.Br(),
                dcc.Loading(
                    id='loading',
                    type='circle',
                    children=[
                        dcc.Textarea(
                            id="textarea_id",
                            value='',
                            style={"height": 50, 'color': 'blue'},
                            readOnly=True,
                        ),
                        dcc.Clipboard(
                            id="clipboard_id",
                            target_id="textarea_id",
                            title="Copy",
                            style={
                                "display": "inline-block",
                                "fontSize": 20,
                                "verticalAlign": "top",
                                "marginLeft": "10px"
                            },
                        ),
                        dcc.Store(id='seq-length-store',
                                  storage_type='session'),
                    ]),



            ], xs=12, sm=12, md=12, lg=10, xl=10),

            ], justify='around'),

    # --------------
    dbc.Row([

        dbc.Col([
            html.Div([
                html.H3("Bootstrap value threshold"),
                dcc.Slider(id='BootstrapThreshold-slider2',
                           min=0,
                           max=100,
                           step=0.1,
                           marks={
                               0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                               25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                               50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                               75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                               100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}},
                           value=0),
                html.Div(id='BootstrapThreshold-slider-output-container2')
            ]),
        ],  # width={'size':5, 'offset':0, 'order':2},
            xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.Div([
                html.H3("Robinson and Foulds distance threshold"),
                dcc.Slider(id='RF-distanceThreshold-slider2',
                           min=0,
                           max=100,
                           step=0.1,
                           marks={
                               0: {'label': '0.0%', 'style': {'color': '#77b0b1'}},
                               25: {'label': '25.0%', 'style': {'color': '#77b0b1'}},
                               50: {'label': '50.0%', 'style': {'color': '#77b0b1'}},
                               75: {'label': '75.0%', 'style': {'color': '#77b0b1'}},
                               100: {'label': '100.0%', 'style': {'color': '#77b0b1'}}},
                           value=100),
                html.Div(id='RFThreshold-slider-output-container2'),
            ]),
        ],  # width={'size':5, 'offset':0, 'order':2},
            xs=12, sm=12, md=12, lg=5, xl=5
        ),
    ],  justify='around'),  # Horizontal:start,center,end,between,around


    html.Hr(),
    # for sliding window siza & step size
    dbc.Row([

        dbc.Col([
            html.Div([
                html.H3("Sliding window size"),
                dcc.Input(id="input_windowSize2", type="number", min=1,
                          # max=max(ref_genes_len.values())-1,
                          placeholder="Enter Sliding Window Size", value=9,
                          style={'width': '65%', 'marginRight': '20px'}),
                html.Div(id='input_windowSize-container2'),
            ]),

        ],  # width={'size':3, 'offset':1, 'order':1},
            xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.Div([
                html.H3("Step size"),
                dcc.Input(id="input_stepSize2", type="number", min=1,
                          # max=max(ref_genes_len.values())-1,
                          placeholder="Enter Step Size", value=3,
                          style={'width': '65%', 'marginRight': '20px'}),
                html.Div(id='input_stepSize-container2'),
            ]),
        ],  # width={'size':3, 'offset':1, 'order':1},
            xs=12, sm=12, md=12, lg=5, xl=5
        ),
    ],  justify='around'),  # Horizontal:start,center,end,between,around

    html.Hr(),
    # ----------
    dbc.Container([
        dbc.Row([
            dbc.Col([

                html.Div([
                    html.H3("Phylogenetic analysis strategy"),
                    dcc.RadioItems(
                        id='strategy-radio',
                        options=[
                            {'label': 'RAxML-NG', 'value': 'raxml'},
                            {'label': 'FastTree', 'value': 'fasttree'}
                        ],
                        value='fasttree'
                    ),
                    html.Div(id='input-strategy-container'),


                ]),
            ], xs=12, sm=12, md=12, lg=5, xl=5),
            dbc.Col([
                html.Div([html.H3("Average Calculation Interval (day)"),
                         dcc.Input(id="average-interval", type="number", min=3,
                                   # max=max(ref_genes_len.values())-1,
                                   # placeholder="Interval for which the environmental values will be averaged",
                                   value=3,
                                   style={'width': '65%', 'marginRight': '20px'}),
                         html.Div(id='Average-interval-container'),
                          ]),
            ], xs=12, sm=12, md=12, lg=5, xl=5),


        ], justify='around'),

        html.Br(),


        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(
                        html.Div(
                            children=[
                                html.H5(
                                    "Note: Each user's analysis results will be shared for academic purposes!",
                                    style={'color': 'blue',
                                           'font-weight': 'bold'}
                                ),
                                html.H5(
                                    "By clicking the Confirm button, you confirm your consent to share all the results of this analysis.",
                                    style={'color': 'blue',
                                           'font-weight': 'bold'}
                                )
                            ]
                        ),
                    )
                ]),
                html.Br(),

                dbc.Button("Confirm",
                           id="button-confir-param", outline=True, color="success", className="me-1"),
                html.Br(),

                html.Hr(),
                # html.Div([
                #     html.H3(
                #         "Select the environmental factors to be studied:"),
                #     dcc.Checklist(id='choice-envFactor',
                #                   options=[{'label': x, 'value': x}
                #                            for x in envFactor_list],
                #                   labelStyle={'display': 'inline-block', 'marginRight': '20px'}),
                # ]),
            ], xs=12, sm=12, md=12, lg=10, xl=10),

        ], justify='around'),

    ], fluid=True),

    # ----------

    dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id='loading',
                    type='circle',
                    children=[
                        dash_table.DataTable(
                            id='forCSV-table',
                            columns=table_columns,
                            # the contents of the table
                            data=df_env.to_dict('records'),
                            editable=False,              # allow editing of data inside all cells
                            # allow filtering of data by user ('native') or not ('none')
                            filter_action="native",
                            # enables data to be sorted per-column by user or not ('none')
                            sort_action="native",
                            sort_mode="multi",         # sort across 'multi' or 'single' columns
                            # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                        # row_selectable="single",     # allow users to select 'multi' or 'single' rows
                                        # choose if user can delete a row (True) or not (False)
                            row_deletable=True,
                                        # selected_columns=[],        # ids of columns that user selects
                            selected_rows=[],           # indices of rows that user selects
                                        # all data is passed to the table up-front or not ('none')
                            page_action="native",
                            page_current=0,             # page number that user is on
                            page_size=30,                # number of rows visible per page
                            style_cell={                # ensure adequate header width when text is shorter than cell's text
                                'minWidth': 125, 'maxWidth': 300, 'width': 125, 'whiteSpace': 'normal', 'textAlign': 'left'
                            },
                            style_data={                # overflow cells' content into multiple lines
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            style_header={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            }
                        ),
                        html.Br(),

                        dbc.Button("Confirm and Submit",
                                   id="button-submit", outline=True, color="success", className="me-1"),
                        dbc.Button(id='btn-csv',
                                   children=[
                                       html.I(className="fa fa-download mr-1"), "Download to CSV"],
                                   color="info",
                                   className="mt-1"
                                   ),
                        dcc.Download(id="download-component-csv"),
                        html.Br(),

                        # Total rows count


                        html.Div(id='row-count3'),
                        html.Div(id='success_message'),
                    ]
                ),



            ], xs=12, sm=12, md=12, lg=12, xl=12),


            ], justify='around'),
    # ------------------------------------------
    dbc.Container([

        html.Br(),
        dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Div(id="analysis-info"),
                    dbc.Button(id='btn-params-info',
                               children=[
                                   html.I(className="fa fa-download mr-1"), "Download parameters text file"],
                               color="info",
                               className="mt-1",
                               style={'display': 'none'}
                               ),
                    dcc.Download(id="download-component-params"),


                ], xs=12, sm=12, md=12, lg=10, xl=10),

                ], justify='around'),

    ], fluid=True),






    # --------------------------
])

# -------------------------------------------------------------
# get env data


@app.callback(
    Output('forCSV-table', 'data'),
    [Input('button-confir-param', 'n_clicks'),
     State('BootstrapThreshold-slider2', 'value'),
     State('RF-distanceThreshold-slider2', 'value'),
     State('input_windowSize2', 'value'),
     State('input_stepSize2', 'value'),
     State('strategy-radio', 'value'),
     State('average-interval', 'value')
     ],
)
def update_table(n, bootstrap, rf, window_size, step_size, strategy, average_interval):

    if n is None:
        return None
    else:
        # Update the parameters of config files
        with open('config/config.yaml', 'r') as file:
            config = yaml.safe_load(file)

            # Update the values
            config['thresholds']['bootstrap_threshold'] = bootstrap
            config['thresholds']['rf_threshold'] = rf
            config['params']['window_size'] = window_size
            config['params']['step_size'] = step_size
            config['params']['strategy'] = strategy
            input_id = config['input']['input_name']
            config['params']['geo_file'] = 'config/' + input_id+'.csv'
            config['params']['seq_file'] = 'config/' + input_id+'.fa'
            # Write the updated dictionary back to the YAML file
            with open('config/config.yaml', 'w') as file:
                yaml.dump(config, file)
        df_seqGeo = geoData_manager.get_seq_MeanGeo(average_interval)
        table_data = df_seqGeo.to_dict('records')
        return table_data

# ------------------------------------------------------
# After submiting the filtered table, analysis will begin
# (1) Get dataframe
# (2) update feature_names based on columns' name (config.yaml)
# (3) update accession_lt based on df['id'] (config.yaml)
# (4) Create a text file inclue the id of Input, id of Analysis, id of Output --> using config file, user can download it (name a copy: ''config/params_info.txt'')
# (5) save df filtered as geo_file (csv format)
# ---------------------
# (6) download sequences from NCBI based on df['id'], then do MSA (multiple sequence alignment), save alignment file as seq_file (fasta format)
# (7) run snakemake workflow
# (8) In Neo4j create :Analysis node (save the info of config.yaml)
# (9) When Analysis finished, save output.csv info into Neo4j :Output node


@app.callback(
    Output('success_message', 'children'),
    Output('btn-params-info', 'style'),
    Input('button-submit', 'n_clicks'),
    State(component_id='forCSV-table',
          component_property="derived_virtual_data"),
    # prevent_initial_call=True
)
def get_paramsInfo(n_clicks, all_rows_data):
    if n_clicks is None:
        return dash.no_update
    else:
        dff = pd.DataFrame(all_rows_data)
        dff.dropna(inplace=True)
        analysisNode_name = neoCypher_manager.generate_unique_name("Analysis")
        outputNode_name = neoCypher_manager.generate_unique_name("Output")

        if dff.empty != True and len(dff) > 4:
            with open('config/config.yaml', 'r') as file:
                config = yaml.safe_load(file)
                # Update the values
            config['seqinfo']['accession_lt'] = dff['id'].tolist()  # (3)
            config['params']['feature_names'] = dff.columns.tolist()[3:]  # (2)
            config['analysis']['analysis_name'] = analysisNode_name
            config['analysis']['output_name'] = outputNode_name
            csv_file_name = config['params']['geo_file']
            dff.to_csv(csv_file_name, index=False, encoding='utf-8')  # (5)
            # -------
            aln_file_name = config['params']['seq_file']
            seq_beforeMSA_fname = aln_file_name + '_raw'
            if config['params']['data_type'] == 'aa':
                db_type = "protein"
            else:
                db_type = "nucleotide"
            accession_list = config['seqinfo']['accession_lt']
            # (6) download sequences from NCBI based on df['id'],

            seqData_manager.downFromNCBI(
                db_type, accession_list, seq_beforeMSA_fname)
            # (6) alignment
            seqData_manager.align_withMAFFT(seq_beforeMSA_fname, aln_file_name)
            # run aphylogeo snakemake workflow
            # Wait for 1 seconds
            # time.sleep(1)
            # delete redundant files
            shutil.rmtree('./results')
            os.mkdir('./results')
            # (7) run snakemake workflow
            os.system("snakemake --cores all")
            # (8) In Neo4j create :Analysis node (save the info of config.yaml)
            neoCypher_manager.addAnalysisNeo()

            # (9) When Analysis finished, save output.csv info into Neo4j :Output node
            neoCypher_manager.addOutputNeo()

            # Write the updated config dictionary back to the YAML file
            with open('config/config.yaml', 'w') as file:
                yaml.dump(config, file)

            success_message = dbc.Card([
                # (src="/assets/workflow.png", top=True),
                dbc.CardBody(
                    [
                        html.H4("Parameters Information",
                                className="card-title"),
                        html.H5('Input Id: {}'.format(
                            config['input']['input_name'])),
                        html.H5('Analysis Id: {}'.format(
                            config['analysis']['analysis_name'])),
                        html.H5('Output Id: {}'.format(
                            config['analysis']['output_name'])),

                        html.P(
                            """
                                    The results of the analysis can be retrieved by ID on the Output Exploration page.
                                    You can also explore the available analysis results on the Output Exploration page.
                                    """,
                            className="card-text",
                        ),
                        # dbc.CardLink(
                        #     "Github", href="https://github.com/tahiri-lab/aPhyloGeo-pipeline"),
                    ]
                ),
            ],
                # style={"width": "45%"},
            ),

            html.Div([
                html.H3('Parameters Information'),

            ])
            return success_message, {'display': 'block'}
        else:
            warning_message = dbc.Card([
                dbc.CardBody(
                    html.Div(
                        children=[
                            html.H5(
                                "Note: The number of samples should be greater than 4!",
                                style={'color': 'blue',
                                       'font-weight': 'bold'}
                            ),
                        ]
                    ),
                )
            ])
            return warning_message, {'display': 'none'}

# -----------------------------------------------------------------------
# for download button


@app.callback(
    Output("download-component-csv", "data"),
    Input("btn-csv", "n_clicks"),
    State('forCSV-table', "derived_virtual_data"),
    prevent_initial_call=True,
)
def func(n_clicks, all_rows_data):
    dff = pd.DataFrame(all_rows_data)
    if n_clicks is None:
        return dash.no_update
    else:
        return dcc.send_data_frame(dff.to_csv, "aphyloGeo_input.csv")


@app.callback(
    Output("download-component-params", "data"),
    Input("btn-params-info", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    if n_clicks is None:
        return dash.no_update
    else:
        with open('config/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        # Convert YAML data to text
        text = yaml.dump(config)
        return dict(content=text, filename="params_info.txt")

# ----------------------------------------------------------------------

# --------------------------------------------------------------
# get seq length and input node id


@app.callback(
    Output('textarea_id', 'value'),
    Output('seq-length-store', 'data'),
    Input('get_input_name', 'n_clicks')
)
def retrieve_config_values(n):
    if n is None:
        return None, None
    else:
        config = config_manager.read_config()
        if config['params']['data_type'] == 'dna':
            nodesLabel = 'Nucleotide'
        else:
            nodesLabel = 'Protein'
        seq_list = config['seqinfo']['accession_lt']
        ref_genes_len = neoCypher_manager.get_seq_length(nodesLabel, seq_list)
        print(ref_genes_len)
        input_name = config['input']['input_name']
        # message = f"Input Id: {input_name}"
        return input_name, ref_genes_len

    # ----------------------------------

# ------------------------------------
# view the value chosen


@app.callback(
    dash.dependencies.Output(
        'Average-interval-container', 'children'),
    [dash.dependencies.Input('average-interval', 'value')])
def update_output(value):
    return 'The period or duration for which the environment values will be averaged is {} days'.format(value)


@app.callback(
    dash.dependencies.Output(
        'BootstrapThreshold-slider-output-container2', 'children'),
    [dash.dependencies.Input('BootstrapThreshold-slider2', 'value')])
def update_output(value):
    return 'You have selected {:0.1f}%'.format(value)


@app.callback(
    dash.dependencies.Output(
        'RFThreshold-slider-output-container2', 'children'),
    [dash.dependencies.Input('RF-distanceThreshold-slider2', 'value')])
def update_output(value):
    return 'You have selected {:0.1f}%'.format(value)
# get seq length for the validation of 'sliding window size' and 'step size'
# By default, the length of 'ORF10'(117bp) was used as the ref_genes_len, since this is the minimun sequence length in our database
# Once user click the 'Get Input ID' button
# (1) sequence list in the config.yaml file calculate the minimum lengh of seq


@app.callback(
    dash.dependencies.Output('input_windowSize-container2', 'children'),
    [dash.dependencies.Input('input_stepSize2', 'value'),
     Input('seq-length-store', 'data'),
     ])
def update_output(stepSize, ref_genes_len):
    if ref_genes_len != None:
        if stepSize == None:
            value_max = int(ref_genes_len) - 1
        else:
            value_max = int(ref_genes_len) - 1 - stepSize
        return 'The input value must an integer from 1 to {}'.format(value_max)
    else:
        return 'The input value must an integer from 1 to 117'


@app.callback(
    dash.dependencies.Output('input_stepSize-container2', 'children'),
    [dash.dependencies.Input('input_windowSize2', 'value'),
     Input('seq-length-store', 'data'),
     ])
def update_output(windowSize, ref_genes_len):
    if ref_genes_len != None:
        if windowSize == None:
            value_max = int(ref_genes_len) - 1
        else:
            value_max = int(ref_genes_len) - 1 - windowSize
        return 'The input value must be an integer from 1 to {}'.format(value_max)
    else:
        return 'The input value must an integer from 1 to 117'


# -------------------------------------------------
@ app.callback(
    Output('row-count3', 'children'),
    [Input(component_id='forCSV-table',
           component_property="derived_virtual_data")]
)
def check_update(all_rows_data):
    dff = pd.DataFrame(all_rows_data)

    print("shape", dff.shape)

    row_count = html.H5("Selected Data Size: {}".format(len(dff))),
    return row_count
