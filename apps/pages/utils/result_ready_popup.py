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
                                            id="close-result-ready-popup-btn",
                                            style={"width": "20px", "cursor": "pointer"},
                                        ),
                                    ],
                                    className="close",
                                ),
                                html.Div(t("upload.popup-done.title", lang), className="title"),
                                html.Div(
                                    [
                                        html.A(t("upload.popup-done.link-results", lang), href="/results", className="button actions", id="ready-popup-results-btn"),
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


layout = get_layout()
