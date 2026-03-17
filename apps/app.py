import dash
import dash_bootstrap_components as dbc
from components.toast import create_toast_container
from dash import ctx, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dotenv import dotenv_values, load_dotenv
from flask import Flask

toast_container = create_toast_container()

load_dotenv()

ENV_CONFIG = {}
for key, value in dotenv_values().items():
    ENV_CONFIG[key] = value

LIGHT_THEME = {
    "--theme-icon": "url(../assets/icons/theme-light.svg)",
    "--switch-toggle-background": "rgb(230, 230, 230)",
    "--switch-toggle-border": "white 1px solid",
    "--text-color": "#1A1C1E",
    "--reverse-black-white-color": "#1A1C1E",
    "--reverse-white-black-color": "white",
    "--background-color": "#EBECF0",
    "--reverse-background-color": "#1A1C1E",
    "--icon-filter": "invert(0%) sepia(82%) saturate(7500%) hue-rotate(33deg) brightness(84%) contrast(115%)",
    "--reverse-icon-filter": "invert(100%) sepia(0%) saturate(0%) hue-rotate(109deg) brightness(106%) contrast(101%)",
    "--glass-style": "rgba(173, 173, 173, 0.5)",
    "--glass-overlay-style": "rgba(28, 28, 32, 0.5)",
    "--result-row-color": "#E7E7E7",
    "--black-and-white": "white",
    "--table-bg-color": "white",
    "--table-alt-row-color": "#F8F9FA",
    "--primary": "#FFFFFF",
    "--secondary": "#DBDBDB",
    "--secondary-hover": "#BFBFBF",
    "--text": "#1A1C1E",
    "--text-secondary": "#828282",
    "--background": "#EBECF0",
    "--action": "#B593DD",
    "--action-hover": "#9F79D6",
    "--action-soft-bg": "color-mix(in srgb, var(--action) 10%, transparent)",
    "--success": "#2DD4BF",
    "--success-soft-bg": "color-mix(in srgb, var(--success) 10%, transparent)",
    "--error": "#FF6262",
    "--pending": "#FFC107",
    "--border": "#e0d8ee",
}

DARK_THEME = {
    "--theme-icon": "url(../assets/icons/theme-dark.svg)",
    "--switch-toggle-background": "black",
    "--switch-toggle-border": "white 1px solid",
    "--text-color": "#E0E0E0",
    "--reverse-black-white-color": "white",
    "--reverse-white-black-color": "#1A1C1E",
    "--background-color": "#1A1C1E",
    "--reverse-background-color": "#EBECF0",
    "--icon-filter": "invert(100%) sepia(0%) saturate(0%) hue-rotate(109deg) brightness(106%) contrast(101%)",
    "--reverse-icon-filter": "invert(0%) sepia(82%) saturate(7500%) hue-rotate(33deg) brightness(84%) contrast(115%)",
    "--glass-style": "rgba(41, 40, 50, 0.5)",
    "--glass-overlay-style": "rgba(59, 58, 67, 0.5)",
    "--result-row-color": "#444444",
    "--black-and-white": "#111111",
    "--table-bg-color": "#111111",
    "--table-alt-row-color": "#141414",
    "--primary": "#2A2D31",
    "--secondary": "#2F343D",
    "--secondary-hover": "#4A5060",
    "--text": "#FFFFFF",
    "--text-secondary": "#A0A0A0",
    "--background": "#1A1C1E",
    "--action": "#9F74D0",
    "--action-hover": "#8B5FC2",
    "--action-soft-bg": "color-mix(in srgb, var(--action) 10%, transparent)",
    "--success": "#1FA391",
    "--success-soft-bg": "color-mix(in srgb, var(--success) 10%, transparent)",
    "--error": "#FF6262",
    "--border": "#2F343D",
}

path_params = {
    "Results": {"img": " /assets/icons/dashboard.svg", "name": "Check results"},
    "Homepage": {"img": "/assets/icons/house-solid.svg", "name": "Home"},
    "Getstarted": {"img": "/assets/icons/folder-upload.svg", "name": "Upload data"},
    "Settings": {"img": "/assets/icons/gear.svg", "name": "Settings"},
    "Help": {"img": "/assets/icons/question-circle.svg", "name": "Help"},
}

server = Flask(__name__)

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.SPACELAB],  # https://bootswatch.com/default/
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    server=server,
    use_pages=True,
)


def NavbarComponent(children):
    return html.Div(children=children, className="nav-bar-container", id="nav-bar")


app.layout = html.Div(
    [
        # Global progress bar for pipeline status (visible on all pages)
        html.Div(
            html.Div(className="progress-bar-fill", id="progress-bar-fill"),
            className="progress-bar hidden",
            id="progress-bar",
        ),
        # Global stores for pipeline status
        dcc.Store(id="global-pipeline-status", storage_type="session", data=None),
        dcc.Store(id="global-result-id", storage_type="session", data=None),
        # Interval for polling pipeline status globally
        dcc.Interval(
            id="global-pipeline-interval",
            interval=2000,
            n_intervals=0,
            disabled=True,
        ),
        dcc.Location(id="url", refresh=False),
        html.Div(
            [
                NavbarComponent(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(id="dummy-output"),
                                        html.Img(
                                            src="/assets/icons/bars.svg",
                                            id="lab-burger",
                                            className="burger",
                                        ),
                                        html.Div(
                                            "Tahiri Lab",
                                            id="lab-name",
                                            className="lab-name",
                                        ),
                                    ],
                                    id="lab-container",
                                    className="lab-container",
                                ),
                            ],
                            className="nav-bar",
                        ),
                        html.Div(
                            [
                                dcc.Link(
                                    [
                                        html.Div(
                                            html.Img(
                                                src=path_params["Homepage"]["img"],
                                                className="icon",
                                            ),
                                            className="icon-wrapper",
                                        ),
                                        html.Div("Home", className="text"),
                                    ],
                                    href="/",
                                    id="nav-link-home",
                                    className="nav-item nav-item-top",
                                ),
                                dcc.Link(
                                    [
                                        html.Div(
                                            html.Img(
                                                src=path_params["Getstarted"]["img"],
                                                className="icon",
                                            ),
                                            className="icon-wrapper",
                                        ),
                                        html.Div("Upload data", className="text"),
                                    ],
                                    href="/getStarted",
                                    id="nav-link-getstarted",
                                    className="nav-item nav-item-top",
                                ),
                                dcc.Link(
                                    [
                                        html.Div(
                                            html.Img(
                                                src=path_params["Results"]["img"],
                                                className="icon",
                                            ),
                                            className="icon-wrapper",
                                        ),
                                        html.Div("Check results", className="text"),
                                    ],
                                    href="/results",
                                    id="nav-link-results",
                                    className="nav-item nav-item-top",
                                ),
                            ],
                            id="nav-link",
                            className="nav-link-container",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            html.Img(
                                                src="/assets/icons/sun.svg",
                                                className="icon",
                                                id="theme-icon",
                                            ),
                                            className="icon-wrapper",
                                        ),
                                        html.Div("Night mode", className="text", id="theme-text"),
                                    ],
                                    id="theme-switch",
                                    className="nav-item nav-item-bottom theme-toggle-btn",
                                ),
                                dcc.Store(id="theme-store", storage_type="local", data=True),
                                html.Div(id="theme-switch-output", style={"display": "none"}),
                                dcc.Link(
                                    [
                                        html.Div(
                                            html.Img(
                                                src="/assets/icons/gear.svg",
                                                className="icon",
                                            ),
                                            className="icon-wrapper",
                                        ),
                                        html.Div("Settings", className="text"),
                                    ],
                                    href="/settings",
                                    id="nav-link-settings",
                                    className="nav-item nav-item-bottom",
                                ),
                                dcc.Link(
                                    [
                                        html.Div(
                                            html.Img(
                                                src="/assets/icons/question-circle.svg",
                                                className="icon",
                                            ),
                                            className="icon-wrapper",
                                        ),
                                        html.Div("Help", className="text"),
                                    ],
                                    href="/help",
                                    id="nav-link-help",
                                    className="nav-item nav-item-bottom",
                                ),
                                html.A(
                                    [
                                        html.Div(
                                            html.Img(
                                                src="/assets/icons/github.svg",
                                                className="icon",
                                            ),
                                            className="icon-wrapper",
                                        ),
                                        html.Div("Visit our GitHub", className="text"),
                                    ],
                                    target="_blank",
                                    href="https://github.com/tahiri-lab",
                                    className="nav-item nav-item-bottom",
                                ),
                            ],
                            className="bottom-section",
                        ),
                    ]
                ),
                html.Div(
                    dash.page_container,
                    className="page-content",
                ),
                toast_container,
            ],
            id="themer",
            className="app-layout",
        ),
    ]
)

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="navbar_function"),
    Output("dummy-output", "children"),  # needed for the callback to trigger
    Input("lab-burger", "n_clicks"),
    prevent_initial_call=True,
)


@app.callback(
    Output("theme-store", "data"),
    Output("theme-switch-output", "children"),
    Input("theme-switch", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def toggle_theme(n_clicks, current_theme):
    """
    Toggle theme when theme switch button is clicked.
    Args:
        n_clicks: number of clicks on the theme button
        current_theme: current theme state (True = dark, False = light)
    Returns:
        theme-store: new theme state
        theme-switch-output: string representation of new theme state
    """
    new_theme = not current_theme if current_theme is not None else False
    return new_theme, str(new_theme)


@app.callback(
    Output("themer", "style"),
    Output("theme-icon", "src"),
    Output("theme-text", "children"),
    Input("theme-store", "data"),
)
def update_color(is_dark):
    """
    Args:
        is_dark: boolean, True if dark theme is selected, False if light theme is selected.
    Returns:
        themer: dict, css style for the theme
        theme-icon: src path for the theme icon
        theme-text: string, text for the theme switch
    """
    if is_dark:
        return DARK_THEME, "/assets/icons/sun.svg", "Light mode"
    else:
        return LIGHT_THEME, "/assets/icons/moon.svg", "Night mode"


@app.callback(
    Output("toast-container", "children"),
    Output("toast-interval", "disabled"),
    Input("toast-store", "data"),
    Input("toast-interval", "n_intervals"),
    prevent_initial_call=True,
)
def display_toast(toast_data, n_intervals):
    """Display toast notification when toast-store is updated."""
    triggered_id = ctx.triggered_id

    if triggered_id == "toast-interval":
        return [], True

    if toast_data and isinstance(toast_data, dict):
        message = toast_data.get("message", "")
        toast_type = toast_data.get("type", "info")
        toast_element = html.Div([
            message,
            html.Div(className="toast-progress")
        ], className=f"toast-message {toast_type}")
        return [toast_element], False
    return [], True


@app.callback(
    Output("progress-bar", "className"),
    Output("progress-bar-fill", "style"),
    Output("global-pipeline-interval", "disabled"),
    Output("toast-store", "data", allow_duplicate=True),
    Input("global-pipeline-interval", "n_intervals"),
    Input("global-pipeline-status", "data"),
    State("global-result-id", "data"),
    prevent_initial_call=True,
)
def update_global_progress_bar(n_intervals, pipeline_status, result_id):
    """
    Update the global progress bar based on estimated time and elapsed time.
    """
    import utils.background_tasks as background_tasks

    if not result_id or not pipeline_status:
        return "progress-bar hidden", {"width": "0%"}, True, dash.no_update

    # Get current status from background tasks (includes progress based on time)
    status_info = background_tasks.get_task_status(result_id)
    status = status_info.get("status", "unknown")

    # Get time-based progress (calculated in get_task_status)
    progress = status_info.get("progress", 0)
    progress_style = {"width": f"{progress}%"}

    if status.lower() == "complete":
        return "progress-bar hidden", {"width": "100%"}, True, dash.no_update
    elif status.lower() == "error":
        error_msg = status_info.get("error", "Unknown error")
        return "progress-bar hidden", {"width": "0%"}, True, {"message": f"Pipeline error: {error_msg}", "type": "error"}
    else:
        return "progress-bar", progress_style, False, dash.no_update


# Clientside callback to copy to clipboard when share button is clicked
app.clientside_callback(
    """
    function(n_clicks, href) {
        if (n_clicks && n_clicks > 0) {
            navigator.clipboard.writeText(href);
        }
        return '';
    }
    """,
    Output("dummy-share-result-output", "children"),
    Input("share-result-btn", "n_clicks"),
    State("url", "href"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    host = ENV_CONFIG["URL"]
    port = ENV_CONFIG["PORT"]
    if "http://" in host:
        host = host.replace("http://", "")

    print("Starting server... on ", host + ":" + port)

    app_dev = ENV_CONFIG["APP_ENV"]

    app.run(
        debug=False if app_dev == "prod" else True,
        port=port,
        host=host,
    )
