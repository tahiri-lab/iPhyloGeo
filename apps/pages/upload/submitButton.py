from dash import html, dcc

layout = html.Div([
    html.Div(
        className="getStarted",
        children=[
            html.Div([
                html.Div(id='name_error_message', className='name_error_message', children=[]),
                dcc.Input(id="input_dataSet", type="text", placeholder="Enter DataSet Name", className="dataSetInput"),
            ], className="dataSetInputContainer"),
            html.Div([
                html.Div(id='sumbit_button'),
                html.Div("Submit", id='submit_dataSet', className="button actions"),
            ], className="submitButton")
        ],
    ),
])
