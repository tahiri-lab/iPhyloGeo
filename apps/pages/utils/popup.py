from components.email_input import create_email_input
from dash import html

layout = html.Div(
    [
        html.Div(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Your results are on the way!", className="title"),
                            html.A(
                                [
                                    html.Img(
                                        src="../../assets/img/coffee-cup.gif",
                                        className="icon",
                                    ),
                                ],
                                href="https://www.flaticon.com/authors/freepik",
                                target="_blank",
                                className="link",
                            ),
                            html.Div(
                                "This may take a few minutes.", className="description"
                            ),
                            html.Div(
                                "Enter your email to receive a notification once your results are ready.",
                                className="description",
                            ),
                            create_email_input(
                                input_id="email-input",
                                button_id="send-email-button",
                                error_id="email-error-message",
                                placeholder="Enter your email...",
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
