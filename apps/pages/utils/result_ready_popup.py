from dash import html

layout = html.Div(
    [
        html.Div(
            html.Div(
                [
                    html.Div(
                        [
                            # Close button
                            html.Div(
                                [
                                    html.Img(
                                        src="../../assets/icons/close.svg",
                                        className="icon close-icon",
                                        id="close-result-ready-popup-btn",
                                        style={"width": "20px", "cursor": "pointer"},
                                    ),
                                ],
                                className="close",
                            ),
                            # Title
                            html.Div("Results are ready!", className="title"),
                            # Action buttons
                            html.Div(
                                [
                                    html.A("View Results", href="/results", className="button actions", id="ready-popup-results-btn"),
                                ],
                                className="popup-actions",
                            ),
                        ],
                        className="content result-ready-content",
                    ),
                ],
                className="popup hidden",
                id="result-ready-popup",
            )
        ),
    ]
)
