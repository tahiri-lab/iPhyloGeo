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
                                # html.Div([
                                #     html.Img(src='../../assets/icons/close.svg', className="icon", id="close_popup"),
                                # ], className="close"),
                                html.Div(t("upload.popup-done.title", lang), className="title"),
                                html.A(
                                    t("upload.popup-done.link-results", lang),
                                    href="/results",
                                    id="popup-done-link",
                                    className="description",
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


layout = get_layout()
