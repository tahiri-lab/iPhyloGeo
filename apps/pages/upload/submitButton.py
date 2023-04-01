from dash import dcc, html, State, Input, Output, clientside_callback,callback


layout = html.Div([
    html.Div(
        className="getStarted",
        children=[
            html.Div(id='testOutput'),
            html.Div("Submit", id='submit_dataSet', className="button actions"),
        ]
    ),
])