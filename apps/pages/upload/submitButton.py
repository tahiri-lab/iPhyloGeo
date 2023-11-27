from dash import html, dcc

layout = html.Div([
    html.Div(
        className="get-started",
        children=[
            html.Div([
                html.Div(id='name-error-message', className='name-error-message', children=[]),
                dcc.Input(id="input-dataset", type="text", placeholder="Enter dataset Name", className="data-set-input"),
                #  html.Div("A popup will appear when results are completed.", className="info-popup"),
            ], className="dataset-input-container"),
            html.Div([
                html.Div(id='submit-button'),
                html.Div("Submit", id='submit-dataset', className="button actions"),
            ], className="submit-button")
        ],
    ),
])
