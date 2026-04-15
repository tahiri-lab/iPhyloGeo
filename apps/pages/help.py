import dash
from dash import Input, Output, callback, dcc, html
from components.page_section import create_page_section
from utils.i18n import LANGUAGE_LIST, t

dash.register_page(__name__, path="/help")


def get_layout(lang="en"):
    return html.Div(
        className="page-container",
        children=[
            html.Div(t("help.title", lang), className="title"),
            html.Div(
                className="page-card",
                children=[
                    create_page_section(
                        t("help.section-upload", lang),
                        icon_src="/assets/icons/folder-upload.svg",
                        children=[
                            html.Div(
                                children=[
                                    html.H3(t("help.section-upload-subtitle", lang)),
                                    dcc.Markdown(t("help.section-upload-intro", lang), className="help-text"),
                                    dcc.Markdown(t("help.section-upload-axis-selection", lang), className="help-text"),
                                    dcc.Markdown(t("help.section-upload-pre-analysis", lang), className="help-text"),
                                    dcc.Markdown(t("help.section-upload-visualization-benefits", lang), className="help-text"),
                                ],
                                className="help-section-content",
                            ),
                        ],
                    ),
                    create_page_section(
                        t("help.section-results", lang),
                        icon_src="/assets/icons/eye.svg",
                        children=[
                            html.Div(
                                children=[
                                    dcc.Markdown(t("help.section-results-body", lang), className="help-text"),
                                ],
                                className="help-section-content",
                            ),
                        ],
                    ),
                    create_page_section(
                        t("help.section-settings", lang),
                        icon_src="/assets/icons/gears.svg",
                        children=[
                            html.Div(
                                children=[
                                    dcc.Markdown(t("help.section-settings-body", lang), className="help-text"),
                                ],
                                className="help-section-content",
                            ),
                        ],
                    ),
                    create_page_section(
                        t("help.section-tests", lang),
                        icon_src="/assets/icons/flask.svg",
                        children=[
                            html.Div(
                                children=[
                                    dcc.Markdown(t("help.section-tests-body", lang), className="help-text"),
                                ],
                                className="help-section-content",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def layout():
    from flask import request
    lang = request.cookies.get("lang", "en")
    return html.Div(id="help-page-content", children=get_layout(lang))


@callback(Output("help-page-content", "children"), Input("language-store", "data"))
def update_help_language(language):
    lang = language if language in LANGUAGE_LIST else "en"
    return get_layout(lang)
