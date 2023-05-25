import pandas as pd
import dash
import dash_cytoscape as cyto
from dash import dcc, html, ctx
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from dash import dash_table
from datetime import datetime

from app import app

from apps import config_manager
from apps import neoCypher_manager

# --------------------------


location_list, protein_list, lineage_list = neoCypher_manager.get_databaseProperties_list()
# print(location_list)
# print(protein_list)
# print(lineage_list)
# ------------------------------------------------------
# for lineage data search: creat a empty table at the begining (place holder)
# data_lineage = {
#     'Lineage': [],
#     'Earliest date': [],
#     'Latest Date': [],
#     'ISO code': [],
#     'Most Common Country': [],
#     'Rate': [],
# }


data_lineage = {
    'lineage': [],
    'earliest_date': [],
    'latest_date': [],
    'iso_code': [],
    'most_common_country': [],
    'rate': [],
}
df_lineage = pd.DataFrame(data_lineage)


# -----------------------------------------
layout = html.Div([
    html.Div(html.H2("Phylogeography"), style={"text-align": "center"}),
    html.Hr(),
    # ----------
    dbc.Container([

        # ----Row 1 begin -------
        dbc.Row([
            dbc.Col([

                # ------
                dbc.CardHeader(
                    dbc.Button(
                        "Exploration: Start with the lineage",
                        color="primary",
                        id="button-ExploreLineage",
                    )
                ),
                dbc.Collapse([
                    html.H5(
                        "Select the group(s) of lineage to be studied:"),

                    dbc.Card([
                        dbc.CardBody(
                            dbc.Checklist(

                                id='choice-lineage',
                                options=[{'label': x, 'value': x}
                                         for x in lineage_list],
                                inline='inline-block',
                                style={'display': 'flex',
                                       'flex-wrap': 'wrap', 'width': '100%'}
                            )
                        )
                    ]),
                    # --------------------
                    # dcc.Checklist(id='choice-lineage',
                    #               options=[{'label': x, 'value': x}
                    #                        for x in lineage_list],
                    #               labelStyle={'display': 'inline-block', 'marginRight': '20px'}),
                    # First dropdown for selecting DNA or Protein
                    html.H5(
                        "Select the type sequences data to be studied:"),
                    dcc.Dropdown(
                        id='type-dropdown',
                        options=[
                            {'label': 'Nucleotide', 'value': 'dna'},
                            {'label': 'Protein', 'value': 'protein'}
                        ],
                        value=None
                    ),
                    # Placeholder for the protein name radio items (initially hidden)
                    html.Div(id='protein-name-container', style={'display': 'none'}, children=[
                        dcc.RadioItems(
                            id='protein-name-radio',
                            options=[
                                {'label': i, 'value': i}
                                for i in protein_list
                            ],
                            value=None
                        )
                    ]),

                    dbc.Button("Confirm",
                               id="button-confir-lineage", outline=True, color="success", className="me-1"),
                    # Output for displaying the selected values
                    html.Div(id='output-container',
                             style={'margin-top': '20px'}),
                    # Valid message
                    html.Div(id='valid-message'),

                    # ------------------------------------
                    html.Hr(),

                    # ----Row 1-2: Dash Table (begin) -------
                    dbc.Row([
                        dbc.Col([
                            dcc.Loading(
                                id='loading',
                                type='circle',
                                children=[
                                    dash_table.DataTable(
                                        id='lineage-table',
                                        columns=[
                                            {"name": i, "id": i, "deletable": False,
                                             "selectable": False, "hideable": False}
                                            for i in df_lineage.columns
                                        ],
                                        # the contents of the table
                                        data=df_lineage.to_dict('records'),
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
                                        page_size=20,                # number of rows visible per page
                                        style_cell={                # ensure adequate header width when text is shorter than cell's text
                                            'minWidth': 95, 'maxWidth': 300, 'width': 95
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
                                    dbc.Button("Confirm samples Selection",
                                               id="button-confir-filter", outline=True, color="success", className="me-1"),
                                    html.Br(),

                                    # Total rows count
                                    html.Div(id='row-count'),
                                ]
                            ),


                        ], xs=12, sm=12, md=12, lg=12, xl=12),

                    ], justify='around'),
                    # ----Row 1-2 end ---
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([

                            dcc.Loading(
                                id='loading',
                                type='circle',
                                children=[
                                    html.Div(id='submit_message'),
                                    # html.Div(id='url-output'),
                                ]),

                        ], xs=12, sm=12, md=12, lg=12, xl=12),

                    ], justify='around'),

                    # ----Row 1-3: Cyto (begin) -------
                    dbc.Row([
                        dbc.Col([

                            html.Div(id='cyto-container')

                        ], xs=12, sm=12, md=12, lg=12, xl=12),

                    ], justify='around'),

                    # ------ Row 1-3 End ---------

                    # -----------------------------------------------------------------------------------------------------
                ],
                    id='exploreLineage', is_open=False,   # the Id of Collapse
                ),
                # ------------

            ], xs=12, sm=12, md=12, lg=12, xl=12),

        ], justify='around'),
        # ----Row 1: Collapse -- end ---
        html.Br(),
        html.Hr(),
        html.Br(),
        # ----Row 2 begin -------
        dbc.Row([
            dbc.Col([
                dbc.CardHeader(
                    dbc.Button(
                        "Exploration: Start with the location",
                        color="primary",
                        id="button-ExploreLocation",
                    )
                ),
                dbc.Collapse([
                    html.H5("Date Range Selection"),
                    dcc.DatePickerRange(
                        id='date-range-lineage',
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date",
                        display_format='YYYY-MM-DD',
                        min_date_allowed=datetime(2020, 1, 1),
                        max_date_allowed=datetime(2022, 12, 31),
                        initial_visible_month=datetime(2020, 1, 1),
                    ),
                    html.H5(
                        "Select the locations to be studied:"),
                    dbc.Card([
                        dbc.CardBody(
                            dbc.Checklist(
                                id='choice-location',
                                options=[{'label': x, 'value': x}
                                         for x in location_list],
                                inline='inline-block',
                                style={'display': 'flex',
                                       'flex-wrap': 'wrap', 'width': '100%'}
                            )
                        )
                    ]),

                    # dcc.Checklist(id='choice-location',
                    #               options=[{'label': x, 'value': x}
                    #                        for x in location_list],
                    #               labelStyle={'display': 'inline-block', 'marginRight': '20px'}),
                    # First dropdown for selecting DNA or Protein
                    html.H5(
                        "Select the type sequences data to be studied:"),
                    dcc.Dropdown(
                        id='type-dropdown2',
                        options=[
                            {'label': 'Nucleotide', 'value': 'dna'},
                            {'label': 'Protein', 'value': 'protein'}
                        ],
                        value=None
                    ),
                    # Placeholder for the protein name radio items (initially hidden)
                    html.Div(id='protein-name-container2', style={'display': 'none'}, children=[
                        dcc.RadioItems(
                            id='protein-name-radio2',
                            options=[
                                {'label': i, 'value': i}
                                for i in protein_list
                            ],
                            value=None
                        )
                    ]),

                    dbc.Button("Confirm",
                               id="button-confir-lineage2", outline=True, color="success", className="me-1"),
                    # Output for displaying the selected values
                    html.Div(id='output-container2',
                             style={'margin-top': '20px'}),
                    # Valid message
                    html.Div(id='valid-message2'),

                    # ------------------------------------
                    html.Hr(),

                    # ----Row 2-2: Dash Table (begin) -------
                    dbc.Row([
                        dbc.Col([
                            dcc.Loading(
                                id='loading',
                                type='circle',
                                children=[
                                    dash_table.DataTable(
                                        id='location-table',
                                        columns=[
                                            {"name": i, "id": i, "deletable": False,
                                             "selectable": False, "hideable": False}
                                            for i in df_lineage.columns
                                        ],
                                        # the contents of the table
                                        data=df_lineage.to_dict('records'),
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
                                        page_size=20,                # number of rows visible per page
                                        style_cell={                # ensure adequate header width when text is shorter than cell's text
                                            'minWidth': 95, 'maxWidth': 300, 'width': 95
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
                                    dbc.Button("Confirm samples Selection",
                                               id="button-confir-samples", outline=True, color="success", className="me-1"),
                                    html.Br(),

                                    # Total rows count

                                    html.Div(id='row-count2'),
                                ]
                            ),


                        ], xs=12, sm=12, md=12, lg=12, xl=12),

                    ], justify='around'),
                    # ----Row 2-2 end ---
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([

                            dcc.Loading(
                                id='loading',
                                type='circle',
                                children=[
                                    html.Div(id='submit_message2'),
                                    # html.Div(id='url-output2')
                                ]),

                        ], xs=12, sm=12, md=12, lg=12, xl=12),

                    ], justify='around'),



                    # ----Row 2-3: Cyto (begin) -------
                    dbc.Row([
                        dbc.Col([

                            html.Div(id='cyto-container2')

                        ], xs=12, sm=12, md=12, lg=12, xl=12),

                    ], justify='around'),

                    # ------ Row 2-3 End ---------

                ],
                    id='exploreLocation', is_open=False,   # the Id of Collapse
                ),




                # ----------we are in dbc.Row (2)------------------------------------------------------------------
            ], xs=12, sm=12, md=12, lg=12, xl=12),

        ], justify='around'),


        # ----Row 2 end ---



        # ---------------------





    ]),
])

# ----------------------------


@ app.callback(
    Output("exploreLocation", "is_open"),
    [Input("button-ExploreLocation", "n_clicks")],
    [State("exploreLocation", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@ app.callback(
    Output("exploreLineage", "is_open"),
    [Input("button-ExploreLineage", "n_clicks")],
    [State("exploreLineage", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
# ------------------------------------------
# select protein name


@ app.callback(
    Output('protein-name-container2', 'style'),
    Output('protein-name-radio2', 'value'),
    Input('type-dropdown2', 'value')
)
def display_protein_name_dropdown(value):
    if value == 'protein':
        return {'display': 'block'}, None
    else:
        return {'display': 'none'}, None


@ app.callback(
    Output('protein-name-container', 'style'),
    Output('protein-name-radio', 'value'),
    Input('type-dropdown', 'value')
)
def display_protein_name_dropdown(value):
    if value == 'protein':
        return {'display': 'block'}, None
    else:
        return {'display': 'none'}, None
# -----------------------------------------------
# Check seque type selected


@ app.callback(
    Output('output-container2', 'children'),
    Input('type-dropdown2', 'value'),
    Input('protein-name-radio2', 'value'),
    prevent_initial_call=True
)
def display_selected_values(type_value, protein_name):
    if type_value == 'protein':
        return f'Selected type: {type_value}, Protein name: {protein_name}'
    else:
        return f'Selected type: {type_value}'


@ app.callback(
    Output('output-container', 'children'),
    Input('type-dropdown', 'value'),
    Input('protein-name-radio', 'value'),
    prevent_initial_call=True
)
def display_selected_values(type_value, protein_name):
    if type_value == 'protein':
        return f'Selected type: {type_value}, Protein name: {protein_name}'
    else:
        return f'Selected type: {type_value}'


# --------------------------------------------
# filtering table update
@ app.callback(
    Output('location-table', 'data'),
    Output('valid-message2', 'children'),
    [Input('button-confir-lineage2', 'n_clicks'),
     State('date-range-lineage', 'start_date'),
     State('date-range-lineage', 'end_date'),
     State('choice-location', 'value'),
     State('type-dropdown2', 'value'),
     # State('protein-name-radio', 'value'),
     ],
)
def update_table(n, start_date_string, end_date_string, checklist_value, seqType_value):

    if n is None:
        return None, None
    else:
        if start_date_string and end_date_string and checklist_value and seqType_value:
            # -----------------Query data in Neo4j database(input: parameters; output: pandas Data Frame)---------------------------------
            start_date = datetime.strptime(
                start_date_string, '%Y-%m-%d').date()
            end_date = datetime.strptime(
                end_date_string, '%Y-%m-%d').date()
            query = f"""
                MATCH (n:Lineage) - [r: IN_MOST_COMMON_COUNTRY] -> (l: Location)
                WHERE n.earliest_date > datetime("{start_date.isoformat()}") AND n.earliest_date < datetime("{end_date.isoformat()}")
                AND l.location in {checklist_value}
                RETURN n.lineage as lineage, n.earliest_date as earliest_date, n.latest_date as latest_date, l.iso_code, l.location as most_common_country,  r.rate
                """
            # params = {"start_date_string": start_date_string,
            #           "end_date_string": end_date_string, "checklist_value": checklist_value}

            cols = ['lineage', 'earliest_date', 'latest_date', 'iso_code',
                    'most_common_country', 'rate']
            df = neoCypher_manager.queryToDataframe(query, cols)
            # Convert the 'Date' column to pandas datetime format
            df['earliest_date'] = pd.to_datetime(
                df['earliest_date'].apply(lambda x: x.to_native()))
            df['latest_date'] = pd.to_datetime(
                df['latest_date'].apply(lambda x: x.to_native()))

            # Format the 'Date' column as '%Y-%m-%d'
            df['earliest_date'] = df['earliest_date'].dt.strftime('%Y-%m-%d')
            df['latest_date'] = df['latest_date'].dt.strftime('%Y-%m-%d')

            # print(df)

            # print(q)
            # -----------------------Present the results in Dash Table --------------------------------------
            # Update DataTable
            table_data = df.to_dict('records')

            return table_data, None
        elif not start_date_string or not end_date_string:
            message = html.Div("Please select a date range.")
            return None, message
        elif not checklist_value:
            message = html.Div(
                "Please select at least one option from the checklist.")
            return None, message
        elif not seqType_value:
            message = html.Div(
                "Please select sequence type.")
            return None, message


@ app.callback(
    Output('lineage-table', 'data'),
    Output('valid-message', 'children'),
    [Input('button-confir-lineage', 'n_clicks'),
     State('choice-lineage', 'value'),
     State('type-dropdown', 'value'),
     # State('protein-name-radio', 'value'),
     ],
)
def update_table(n, checklist_value, seqType_value):

    if n is None:
        return None, None
    else:
        if checklist_value and seqType_value:
            # -----------------Query data in Neo4j database(input: parameters; output: pandas Data Frame)---------------------------------
            starts_with_conditions = " OR ".join(
                [f'n.lineage STARTS WITH "{char}"' for char in checklist_value])

            query = f"""
                MATCH (n:Lineage) - [r: IN_MOST_COMMON_COUNTRY] -> (l: Location)
                WHERE {starts_with_conditions}
                RETURN n.lineage as lineage, n.earliest_date as earliest_date, n.latest_date as latest_date, l.iso_code as iso_code, n.most_common_country as most_common_country,  r.rate as rate
                """
            # params = {"starts_with_conditions": starts_with_conditions}
            cols = ['lineage', 'earliest_date', 'latest_date', 'iso_code',
                    'most_common_country', 'rate']
            df = neoCypher_manager.queryToDataframe(query, cols)
            # Convert the 'Date' column to pandas datetime format
            df['earliest_date'] = pd.to_datetime(
                df['earliest_date'].apply(lambda x: x.to_native()))
            df['latest_date'] = pd.to_datetime(
                df['latest_date'].apply(lambda x: x.to_native()))

            # Format the 'Date' column as '%Y-%m-%d'
            df['earliest_date'] = df['earliest_date'].dt.strftime('%Y-%m-%d')
            df['latest_date'] = df['latest_date'].dt.strftime('%Y-%m-%d')

            # print(df)

            # print(q)
            # -----------------------Present the results in Dash Table --------------------------------------
            # Update DataTable
            table_data = df.to_dict('records')

            return table_data, None
        elif not checklist_value:
            message = html.Div(
                "Please select at least one option from the checklist.")
            return None, message
        elif not seqType_value:
            message = html.Div(
                "Please select sequence type.")
            return None, message


# ---------- Visual Cyto----------------------
@ app.callback(
    Output('row-count2', 'children'),
    Output('cyto-container2', 'children'),
    [
        Input(component_id='location-table',
              component_property="derived_virtual_data")]
)
def check_update(all_rows_data):
    dff = pd.DataFrame(all_rows_data)

    print("shape", dff.shape)

    row_count = html.H5("Selected Data Size: {}".format(len(dff))),
    mycyto = html.Div()
    if dff.empty != True:
        nodes_list = dff.lineage.unique().tolist(
        ) + dff.most_common_country.unique().tolist()
        elements = [{'data': {'id': id, 'label': id}} for id in nodes_list]
        dff = dff[['lineage', 'most_common_country', 'rate']]
        dff.rename(columns={"most_common_country": "source",
                            "lineage": "target", "rate": "weight"}, inplace=True)
        data_list = dff.to_dict('records')
        relations = [{'data': item} for item in data_list]
        elements.extend(relations)

        mycyto = cyto.Cytoscape(
            id='cytoscape-styling-2',
            # circle "random","preset","circle","concentric","grid","breadthfirst","cose","close-bilkent","cola","euler","spread","dagre","klay"
            layout={'name': 'circle'},
            style={'width': '100%', 'height': '400px'},
            elements=elements,
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {
                        'content': 'data(label)'
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'label': 'data(weight)'
                    }
                },
                {
                    'selector': '[weight > 30]',
                    'style': {
                        'line-color': 'blue',
                    }
                }
            ]
        )

    return row_count, mycyto


@app.callback(
    Output('row-count', 'children'),
    Output('cyto-container', 'children'),
    [
        Input(component_id='lineage-table',
              component_property="derived_virtual_data")]
)
def check_update(all_rows_data):
    dff = pd.DataFrame(all_rows_data)

    print("shape", dff.shape)

    row_count = html.H5("Selected Data Size: {}".format(len(dff))),
    mycyto = html.Div()
    if dff.empty != True:
        nodes_list = dff.lineage.unique().tolist(
        ) + dff.most_common_country.unique().tolist()
        elements = [{'data': {'id': id, 'label': id}} for id in nodes_list]
        dff = dff[['lineage', 'most_common_country', 'rate']]
        dff.rename(columns={"most_common_country": "source",
                            "lineage": "target", "rate": "weight"}, inplace=True)
        data_list = dff.to_dict('records')
        relations = [{'data': item} for item in data_list]
        elements.extend(relations)

        mycyto = cyto.Cytoscape(
            id='cytoscape-styling-2',
            # circle "random","preset","circle","concentric","grid","breadthfirst","cose","close-bilkent","cola","euler","spread","dagre","klay"
            layout={'name': 'circle'},
            style={'width': '100%', 'height': '400px'},
            elements=elements,
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {
                        'content': 'data(label)'
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'label': 'data(weight)'
                    }
                },
                {
                    'selector': '[weight > 30]',
                    'style': {
                        'line-color': 'blue',
                    }
                }
            ]
        )

    return row_count, mycyto
    # ---------------------------------------------
# save sample information to the database


@app.callback(
    Output('submit_message2', 'children'),
    Input('button-confir-samples', 'n_clicks'),
    Input('type-dropdown2', 'value'),
    Input('protein-name-radio2', 'value'),
    State(component_id='location-table',
          component_property="derived_virtual_data"),
    # prevent_initial_call=True
)
def get_sequences(n_clicks, seq_type, protein_name, all_rows_data):
    # print(n_clicks)
    if n_clicks is None:
        return dash.no_update
    else:
        dff = pd.DataFrame(all_rows_data)
        print('dff_size', dff.shape)
        if dff.empty != True:
            print(
                f'---------------submitted df-----location_filter---------Size {dff.shape}')
            # print(dff)
            inputNode_name = neoCypher_manager.generate_unique_name("Input")
            if seq_type == 'dna':
                config_manager.update_paramsYaml('data_type', seq_type)
                seq_accession_lt = neoCypher_manager.getNucleoIdFromSamplesFilter(
                    dff)
                print(seq_accession_lt)
                config_manager.update_seqinfoYaml(
                    'accession_lt', seq_accession_lt)
                neoCypher_manager.addInputNeo(
                    'Nucleotide', inputNode_name, seq_accession_lt)
            elif seq_type == 'protein':
                config_manager.update_paramsYaml('data_type', 'aa')
                seq_accession_lt = neoCypher_manager.getProteinIdFromSamplesFilter(
                    dff, protein_name)
                print(seq_accession_lt)
                config_manager.update_seqinfoYaml(
                    'accession_lt', seq_accession_lt)
                neoCypher_manager.addInputNeo(
                    'Protein', inputNode_name, seq_accession_lt)

            config_manager.update_inputYaml('input_name', inputNode_name)

            output_conrainer = dbc.CardBody([

                dcc.Markdown(
                    "The sample information to be analyzed has been successfully saved!", className="card-text"),

                dbc.CardLink("Next Step", href="parameters"),

            ]
            )

            return output_conrainer


@app.callback(
    Output('submit_message', 'children'),
    Input('button-confir-filter', 'n_clicks'),
    Input('type-dropdown', 'value'),
    Input('protein-name-radio', 'value'),
    State(component_id='lineage-table',
          component_property="derived_virtual_data"),
    # prevent_initial_call=True
)
def get_sequences(n_clicks, seq_type, protein_name, all_rows_data):
    if n_clicks is None:
        return dash.no_update
    else:
        dff = pd.DataFrame(all_rows_data)
        if dff.empty != True:
            print(
                f'---------------submitted df-------lineage_filter-------Size {dff.shape}')
            # print(dff)
            inputNode_name = neoCypher_manager.generate_unique_name("Input")
            if seq_type == 'dna':
                config_manager.update_paramsYaml('data_type', seq_type)
                seq_accession_lt = neoCypher_manager.getNucleoIdFromSamplesFilter(
                    dff)
                print(seq_accession_lt)
                config_manager.update_seqinfoYaml(
                    'accession_lt', seq_accession_lt)
                neoCypher_manager.addInputNeo(
                    'Nucleotide', inputNode_name, seq_accession_lt)
            elif seq_type == 'protein':
                config_manager.update_paramsYaml('data_type', 'aa')
                seq_accession_lt = neoCypher_manager.getProteinIdFromSamplesFilter(
                    dff, protein_name)
                print(seq_accession_lt)
                config_manager.update_seqinfoYaml(
                    'accession_lt', seq_accession_lt)
                neoCypher_manager.addInputNeo(
                    'Protein', inputNode_name, seq_accession_lt)

            config_manager.update_inputYaml('input_name', inputNode_name)

            output_conrainer = dbc.CardBody([

                dcc.Markdown(
                    "The sample information to be analyzed has been successfully saved!", className="card-text"),

                dbc.CardLink("Next Step", href="parameters"),

            ]
            )

            return output_conrainer
