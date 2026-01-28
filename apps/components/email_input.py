"""
Reusable email input component with validation.
"""

import re

from dash import dcc, html

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Style constants for callbacks to use
NORMAL_INPUT_STYLE = {"border": "1px solid #ccc"}
ERROR_INPUT_STYLE = {"border": "1px solid red"}


def validate_email(email):
    """Validate email format. Returns True if valid, False otherwise."""
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email))


def create_email_input(
    input_id, button_id, error_id, placeholder="Enter your email..."
):
    """
    Create an email input component with button and error message.

    Args:
        input_id: ID for the email input field
        button_id: ID for the submit button
        error_id: ID for the error message div
        placeholder: Placeholder text for the input

    Returns:
        html.Div containing the email input, button, and error message
    """
    return html.Div(
        [
            html.Div(
                [
                    dcc.Input(
                        id=input_id,
                        type="text",
                        placeholder=placeholder,
                        style=NORMAL_INPUT_STYLE,
                    ),
                    html.Button(
                        "Send Email",
                        id=button_id,
                        n_clicks=0,
                        style={
                            "fontFamily": "Calibri",
                            "color": "white",
                            "backgroundColor": "#AD00FA",
                            "border": "none",
                            "borderRadius": "10px",
                            "fontSize": "18px",
                            "marginLeft": "10px",
                            "boxShadow": "rgba(0, 0, 0, 0.35) 0 5px 15px",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                },
            ),
            html.Div(
                id=error_id,
                style={
                    "color": "red",
                    "fontSize": "12px",
                    "marginTop": "5px",
                    "textAlign": "center",
                },
            ),
        ],
        className="email-container",
    )
