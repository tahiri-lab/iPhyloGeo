import dash_bootstrap_components as dbc
from dash import callback, html, register_page
from dash.dependencies import Input, Output
from utils.i18n import LANGUAGE_LIST, t

register_page(__name__, path="/")

external_stylesheets = [
    {
        "href": "https://use.fontawesome.com/releases/v6.1.1/css/all.css",
        "rel": "stylesheet",
        "integrity": "sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf",
        "crossorigin": "anonymous",
    }
]

def layout():
    from flask import request
    lang = request.cookies.get("lang", "en")
    return html.Div(
        [
            html.Div(
                className="home-page",
                children=[
                    html.Div(id="background-video"),
                    html.Div(
                        className="main-text",
                        children=[
                            html.Div(t("home.title", lang), className="title", id="home-title"),
                            html.Div(
                                [
                                    html.Span(
                                        t("home.subtitle-prefix", lang),
                                        id="home-subtitle-prefix",
                                    ),
                                    html.A(
                                        [
                                            html.Span(t("home.learn-more", lang), id="home-learn-more"),
                                            html.Img(
                                                src="../assets/icons/up-right-from-square-solid.svg",
                                                className="icon",
                                            ),
                                        ],
                                        target="_blank",
                                        href="https://tahirinadia.github.io/",
                                        className="url",
                                    ),
                                ],
                                className="sub-title",
                            ),
                            dbc.NavLink(
                                t("home.get-started", lang),
                                href="/getStarted",
                                id="themes",
                                className="button primary",
                                active="exact",
                            ),
                        ],
                    ),
                ],
            ),
        ]
    )


@callback(
    Output("background-video", "children"), Input("theme-store", "data")
)
def update_background_video(is_dark):
    """
    Update the background video according to the theme.
    Args:
        is_dark: boolean, True if dark theme is selected, False if light theme is selected.
    Returns:
        The background video element.
    """
    if is_dark is None:
        is_dark = True  # default matches store default

    if not is_dark:
        return html.Video(
            src="/assets/videos/indexPhylogeo_light.mp4",
            autoPlay=True,
            loop=True,
            muted=True,
            controls=False,
            className="home-page__video",
        )

    return html.Video(
        src="/assets/videos/indexPhylogeo.mp4",
        autoPlay=True,
        loop=True,
        muted=True,
        controls=False,
        className="home-page__video",
    )


@callback(
    Output("home-title", "children"),
    Output("home-subtitle-prefix", "children"),
    Output("home-learn-more", "children"),
    Output("themes", "children"),
    Input("language-store", "data"),
)
def update_home_language(language):
    lang = language if language in LANGUAGE_LIST else "en"
    return (
        t("home.title", lang),
        t("home.subtitle-prefix", lang),
        t("home.learn-more", lang),
        t("home.get-started", lang),
    )
