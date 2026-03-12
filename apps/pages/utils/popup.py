from components.email_input import create_email_input
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
                                        id="close-popup-btn",
                                        style={"width": "20px", "cursor": "pointer"},
                                    ),
                                ],
                                className="close",
                            ),
                            # Title
                            html.Div("Your results are on the way!", className="title", id="popup-title"),
                            # Icon
                            html.A(
                                [
                                    html.Img(
                                        src="../../assets/img/coffee-cup.gif",
                                        className="icon",
                                        id="popup-icon",
                                    ),
                                ],
                                href="https://www.flaticon.com/authors/freepik",
                                target="_blank",
                                className="link",
                                id="popup-icon-link",
                            ),
                            # Status message (will be updated dynamically)
                            html.Div(
                                "Starting pipeline...",
                                className="description status-message",
                                id="popup-status-message",
                            ),
                            # Navigation info
                            html.Div(
                                "You can navigate freely on the site while the analysis is running.",
                                className="description navigation-info",
                            ),
                            # Action buttons
                            html.Div(
                                [
                                    html.A("Go to Results Page", href="/results", className="button actions", id="popup-results-btn"),
                                ],
                                className="popup-actions",
                            ),
                            # Email section
                            html.Hr(style={"margin": "15px 0", "opacity": "0.3"}),
                            html.Div(
                                "Receive an email when your results are ready:",
                                className="description email-label",
                            ),
                            create_email_input(
                                input_id="email-input",
                            ),
                        ],
                        className="content",
                    ),
                ],
                className="popup hidden",
                id="popup",
            )
        ),
    ]
)
