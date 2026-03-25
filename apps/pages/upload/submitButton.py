from dash import dcc, html
from utils.i18n import t


def get_layout(lang="en"):
    return html.Div(
        className="submit-section",
        children=[
            html.Div(
                t("upload.submit.analyse-data", lang),
                className="analyse-title",
            ),
            html.P(
                t("upload.submit.select-columns", lang),
                className="field-label",
            ),
            dcc.Checklist(
                id="col-analyze",
                options=[],
                value=[],
                className="col-analyze-cards",
                labelStyle={"display": "flex"},
            ),
            html.Div(
                id="column-error-message",
                className="field-error-message",
                children=[],
            ),
            html.P(t("upload.submit.enter-dataset-name", lang), className="field-label"),
            dcc.Input(
                id="input-dataset",
                type="text",
                placeholder=t("upload.submit.placeholder-dataset-name", lang),
                className="dataset-input",
                value="",
            ),
            html.Div(
                id="name-error-message",
                className="field-error-message name-error-message",
                children=[],
            ),
            html.Div(
                [
                    html.Div(
                        t("upload.submit.submit", lang), id="submit-dataset", className="submit-btn",
                    ),
                ],
                className="submit-btn-wrapper",
            ),
        ],
    )


layout = get_layout()
