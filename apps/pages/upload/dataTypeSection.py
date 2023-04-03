from dash import html, Input, Output, ctx, callback
from dash.dependencies import Input, Output


layout = html.Div([
    html.Div(id='output_option_position'), # use only to store output value
    html.Div(children=[
        html.Div(
            className="ChoiceSection",
            id="choice_section",
            children=[
                html.Div([
                    html.Div('How are you going to change the world today ?', className="title"),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Img(src='../../assets/icons/meteorological.svg', className="img"),
                            ], className="optionImage"),
                            html.Div('Upload Meteorological data', className="title"),
                            html.Div('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.',
                                     className="description"),
                        ], id='meteo', className="option"),
                        html.Div([
                            html.Div([
                                html.Img(src='../../assets/icons/genetic.svg', className="img"),
                            ], className="optionImage"),
                            html.Div('Upload Genetic data', className="title"),
                            html.Div('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.',
                                     className="description"),
                        ], id='genetic', className="option"),
                        html.Div([
                            html.Div([
                                html.Img(src='../../assets/icons/meteo-genetic.svg', className="img"),
                            ], className="optionImage"),
                            html.Div('Upload Meteorological and Genetic data', className="title"),
                            html.Div('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.',
                                     className="description"),
                        ], id='meteoGene', className="option"),
                    ], id='options', className="container"),
                    html.Div("Next", id='option_choice_next', className="button actions"),
                ], className="choiceSectionInside"),
            ],
        ),
    ],),
],)


# clientside_callback(
#     ClientsideFunction(
#         namespace='clientside',
#         function_name='next_option_function'
#     ),
#     Output("output_option_position", "children"), # needed for the callback to trigger
#     [Input("option_choice_next", "n_clicks"),
#      Input("drop_file_section", "id"),], # This is where we want the button to redirect the user
#     prevent_initial_call=True,
# )

# Callback to style the selected option
@callback(
        Output('meteo', 'className'),
        Output('genetic', 'className'),
        Output('meteoGene', 'className'),
          [Input('meteo', 'n_clicks'),
            Input('genetic', 'n_clicks'),
            Input('meteoGene', 'n_clicks')],
          prevent_initial_call=True,
)

def choose_option(meteo, genetic, meteoGene):
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return ('option selected' if button_id == 'meteo' else 'option',
            'option selected' if button_id == 'genetic' else 'option',
            'option selected' if button_id == 'meteoGene' else 'option')

# @callback(
#         Output('third-section', 'children'), # showing or not the params section
#           [Input('meteo', 'n_clicks'),
#             Input('genetic', 'n_clicks'),
#             Input('meteoGene', 'n_clicks')],
#           prevent_initial_call=True,
# )
#
# def choose_option(meteo, genetic, meteoGene):
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#     # return (upload_MeteorologicalDataset.layout if button_id == 'meteo' else '',
#     #         params.layout if button_id == 'genetic' else '',
#     #         params.layout if button_id == 'meteoGene' else '')
#     return (params.layout if button_id == 'genetic' else '',
#             params.layout if button_id == 'meteoGene' else '')