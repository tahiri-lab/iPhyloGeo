from dash import dcc, html

layout = html.Div(
    [
        html.Div(
            className="get-started",
            children=[
                html.Div(
                    [
                        html.Div(
                            id="name-error-message",
                            className="name-error-message",
                            children=[],
                        ),
                        # Input for dataset name - synced with main layout input-dataset
                        dcc.Input(
                            id="input-dataset-visible",
                            type="text",
                            placeholder="Enter dataset Name",
                            className="data-set-input",
                            value=""
                        ),
                    ],
                    className="dataset-input-container",
                ),
                html.Div(
                    [
                        html.Div(
                            "Submit", id="submit-dataset", className="button actions"
                        ),
                    ],
                    className="submit-button",
                ),
            ],
        ),
    ]
)
