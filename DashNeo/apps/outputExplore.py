import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from dash import dash_table
from apps import neoCypher_manager
from app import app


# -----------------------------------------
# output teble
data_output = {
    'window_position': [],
    'feature': [],
    'bootstrap_average': [],
    'normalized_RF': []
}

df_output = pd.DataFrame(data_output)
# -----------------------------------------
layout = html.Div([
    html.Div(html.H2("Phylogeography Output"), style={"text-align": "center"}),
    html.Hr(),
    # ----------
    dbc.Container([

        # ----Row 1 begin -------
        dbc.Row([
            dbc.Col([

                # ------
                dbc.CardHeader(
                    dbc.Button(
                        "Explore output by Output Id",
                        color="primary",
                        id="button-check-outputId",
                    )
                ),
                dbc.Collapse([
                    html.H5("Search output by Output Id"),
                    dcc.Input(id="check-by-outputId", type="text",
                              placeholder="Enter Output Id", value='',
                              style={'width': '65%', 'marginRight': '20px'}),

                    dbc.Button("Confirm",
                               id="button-confir-outputId", outline=True, color="success", className="me-1"),


                    dbc.Row([
                        dbc.Col([
                            # Valid message
                            html.Div(id='valid-message-output'),
                            html.Br(),

                            dcc.Loading(
                                id='loading',
                                type='circle',
                                children=[
                                    dash_table.DataTable(
                                        id='output-table',
                                        columns=[
                                            {"name": i, "id": i, "deletable": False,
                                             "selectable": False, "hideable": False}
                                            for i in df_output.columns
                                        ],
                                        # the contents of the table
                                        data=df_output.to_dict('records'),
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
                                            'minWidth': 95, 'maxWidth': 95, 'width': 95
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
                                    # html.Br(),

                                    html.Br(),
                                    dbc.Button(id='btn-csv2',
                                               children=[
                                                   html.I(className="fa fa-download mr-1"), "Download to CSV"],
                                               color="info",
                                               className="mt-1"
                                               ),
                                    dcc.Download(id="download-component-csv2"),
                                    html.Br(),


                                    html.Div(),
                                ]
                            ),


                        ], xs=12, sm=12, md=12, lg=12, xl=12),

                    ], justify='around'),

                    # ------------------------------------------------------
                ],
                    id='exploreOutput', is_open=False,   # the Id of Collapse
                ),
                # ------------

            ], xs=12, sm=12, md=12, lg=12, xl=12),

        ], justify='around'),


        # ----Row 1 end ---
        html.Hr(),
        html.Br(),

        # ----Row 1-2: output (begin) -------



        # ----Row 1-2 end ---
        html.Br(),
        html.Hr(),
        html.Br(),



        # ----Row 2 begin -------
        dbc.Row([
            dbc.Col([

                html.Div(),

            ], xs=12, sm=12, md=12, lg=12, xl=12),

        ], justify='around'),


        # ----Row 2 end ---


    ]),
])

# ----------------------------

# for download button


@app.callback(
    Output("download-component-csv2", "data"),
    Input("btn-csv2", "n_clicks"),
    State('output-table', "derived_virtual_data"),
    prevent_initial_call=True,
)
def func(n_clicks, all_rows_data):
    dff = pd.DataFrame(all_rows_data)
    if n_clicks is None:
        return dash.no_update
    else:
        return dcc.send_data_frame(dff.to_csv, "aphyloGeo_output.csv")


@app.callback(
    Output("exploreOutput", "is_open"),
    [Input("button-check-outputId", "n_clicks")],
    [State("exploreOutput", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
# -------------------


@app.callback(
    Output('output-table', 'data'),
    Output('valid-message-output', 'children'),
    [Input('button-confir-outputId', 'n_clicks'),
     State('check-by-outputId', 'value'),
     ],
)
def update_table(n, id_value):

    if n is None:
        return None, None
    else:
        if id_value:
            df = neoCypher_manager.get_outputdf(id_value)
            # Update DataTable
            table_data = df.to_dict('records')

            return table_data, None
        else:
            message = html.Div(
                "Please enter the Output Id")
            return None, message
