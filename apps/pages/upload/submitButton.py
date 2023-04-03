from dash import html

layout = html.Div([
    html.Div(
        className="getStarted",
        children=[
            html.Div([
                html.Div(id='sumbit_button'),
                html.Div("Submit", id='submit_dataSet', className="button actions"),
            ], className="submitButton")
        ],
    ),
])