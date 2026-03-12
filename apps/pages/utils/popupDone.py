from dash import html

layout = html.Div(
    [
        html.Div(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Results completed!", className="title"),
                            html.Img(
                                src="../../assets/icons/check-circle.svg",
                                className="icon success-icon",
                                style={"width": "48px", "height": "48px", "marginBottom": "10px"},
                            ),
                            html.Div(
                                "Your phylogeographic analysis has finished.",
                                className="description",
                            ),
                            html.Div(
                                [
                                    html.A(
                                        "View Results",
                                        href="/results",
                                        className="button actions",
                                        id="view-results-link",
                                    ),
                                ],
                                className="popup-actions",
                            ),
                        ],
                        className="content",
                    ),
                ],
                className="popup hidden",
                id="popupDone",
            )
        ),
    ]
)
