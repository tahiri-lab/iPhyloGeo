from components.email_input import create_email_input
from dash import html
from utils.i18n import t


def get_layout(lang="en"):
    return html.Div(
        [
            html.Div(
                html.Div(
                    [
                        html.Div(
                            [
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
                                html.Div(
                                    t("upload.popup.title", lang),
                                    className="title",
                                    id="popup-title",
                                ),
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
                                ),
                                html.Div(
                                    t("upload.popup.description-delay", lang),
                                    className="description",
                                    id="popup-status-message",
                                ),
                                html.Div(
                                    t("upload.popup.description-email", lang),
                                    className="description",
                                ),
                                create_email_input(
                                    input_id="email-input",
                                    placeholder=t("upload.email.placeholder", lang),
                                    button_text=t("upload.email.send", lang),
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


layout = get_layout()
