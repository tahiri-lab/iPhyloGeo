import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, clientside_callback, ClientsideFunction

layout = html.Div([
    html.Div(id='output-file-drop-position-next'),  # use only to store output value
    html.Div(id='upload-data-output'),  # use only to store output value
    html.Div(children=[
        html.Div(
            className="drop-file-section",
            id="drop-file-section",
            children=[
                html.Div([
                    html.Div('Please drop your file right here', className="title"),
                    html.Div([
                        html.Div([
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    html.A([
                                        html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                                        html.Div('Drag and Drop or Select Files', className="text"),
                                    ], className="drop-content"),
                                ], className="drop-container", id="drop-container"),
                                multiple=True  # Allow multiple files to be uploaded
                            ),
                            # WIP : add a button to insert the data manually
                            # html.Div([
                            #     dcc.Textarea(
                            #         cols='60', rows='8',
                            #         value='',
                            #         className="textArea hidden", id='manual-field'
                            #     ),
                            # ], ),
                            # html.Div('Insert my data manually', id="manual-insert", className="manuel-insert-text"),
                        ], className="drop-zone"),
                    ], id='options', className="container"),
                    dbc.NavLink([
                        html.Div([
                            html.Div('Don’t know where to start ?', className="title"),
                            html.Div('No worries, let’s try with some of our already made example.',
                                     className="description"),
                        ], className="content"),
                        html.Img(src='../../assets/icons/arrow-circle-right.svg', className="icon arrow"),
                    ], href='/apps/getStarted', id='themes', className="helper primary", active="exact"),
                    html.Div([
                        html.Div("Next", id='drop-option-choice-next', className="button actions"),
                    ], className="button-pack"),
                ], className="drop-file-section-inside"),
            ],
        ),
    ],),
],)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='next_option_function'
    ),
    Output("output-file-drop-position-next", "children"),  # needed for the callback to trigger
    [Input("drop-option-choice-next", "n_clicks"),
     Input("params-sections", "id")],  # This is where we want the button to redirect the user
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='show_text_field'
    ),
    Output("manual-field", "children"),  # needed for the callback to trigger
    Input("manual-insert", "n_clicks"),
    prevent_initial_call=True,
)
