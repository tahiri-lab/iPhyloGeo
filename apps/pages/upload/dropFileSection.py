from tkinter import S
import dash_bootstrap_components as dbc
from dash import dcc, html, State, Input, Output, clientside_callback,callback
from dash.dependencies import Input, Output, ClientsideFunction
from utils import utils
from .meteo import paramsMeteo
from .geo import params

layout = html.Div([
    html.Div(id='output_file_drop_position_prev'), # use only to store output value
    html.Div(id='output_file_drop_position_next'), # use only to store output value
    html.Div(id='upload-data-output'), # use only to store output value
    html.Div(children=[
        html.Div(
            className="DropFileSection",
            id="drop_file_section",
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
                                    ], className="dropContent"),
                                ], className="dropContainer", id="dropContainer"),
                                # Allow multiple files to be uploaded
                                multiple=True
                            ),
                            html.Div([
                                dcc.Textarea(
                                    cols='60', rows='8',
                                    value='Textarea content initialized\nwith multiple lines of text',
                                    className="textArea hidden", id='manualField'
                                ),
                            ], ),
                            html.Div('Insert my data manually', id="manualInsert", className="ManualInsertText")
                        ], className="dropZone"),
                    ], id='options', className="container"),
                    dbc.NavLink([
                        html.Div([
                            html.Div('Don’t know where to start ?', className="title"),
                            html.Div('No worries, let’s try with some of our already made example.',
                                     className="description"),
                        ], className="content"),
                        html.Img(src='../../assets/icons/arrow-circle-right.svg', className="icon"),
                    ], href='/apps/getStarted', id='themes', className="helper primary", active="exact"),
                    html.Div([
                        html.Div("Previous", id='drop_option_choice_prev', className="button actions"),
                        html.Div("Next", id='drop_option_choice_next', className="button actions"),
                    ], className="buttonPack"),
                ], className="DropFileSectionInside"),
            ],
        ),
    ],),
],)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='next_option_function'
    ),
    Output("output_file_drop_position_prev", "children"), # needed for the callback to trigger
    [Input("drop_option_choice_prev", "n_clicks"),
     Input("choice_section", "id"),], # This is where we want the button to redirect the user
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='next_option_function'
    ),
    Output("output_file_drop_position_next", "children"), # needed for the callback to trigger
    [Input("drop_option_choice_next", "n_clicks"),
     Input("params_section", "id"),], # This is where we want the button to redirect the user
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='show_text_field'
    ),
    Output("manualField", "children"), # needed for the callback to trigger
    Input("manualInsert", "n_clicks"),
    prevent_initial_call=True,
)



# Section backend ## TODO: brainstorming to name this section
