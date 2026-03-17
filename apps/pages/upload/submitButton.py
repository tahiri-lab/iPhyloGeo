from dash import dcc, html

layout = html.Div(
    className="submit-section",
    children=[
        html.Div(
            "Analyse data",
            className="analyse-title",
        ),
        html.P(
            "Select columns to analyze",
            className="field-label",
        ),
        dcc.Checklist(
            id="col-analyze",
            options=[],
            value=[],
            className="col-analyze-cards",
            labelStyle={"display": "flex"},
        ),
        html.Div(
            id="column-error-message",
            className="field-error-message",
            children=[],
        ),
        html.P("Enter dataset name", className="field-label"),
        dcc.Input(
            id="input-dataset",
            type="text",
            placeholder="Enter dataset Name",
            className="dataset-input",
            value="",
        ),
        html.Div(
            id="name-error-message",
            className="field-error-message name-error-message",
            children=[],
        ),
        html.Div(
            [
                html.Div(id="submit-button"),
                html.Div(
                    "Submit", id="submit-dataset", className="submit-btn",
                ),
            ],
            className="submit-btn-wrapper",
        ),
    ],
)
