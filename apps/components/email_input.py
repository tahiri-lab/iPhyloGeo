"""
Reusable email input component with validation.
"""

import re

from dash import dcc, html

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_email(email):
    """Validate email format. Returns True if valid, False otherwise."""
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email))


def get_button_id(input_id):
    """Return the auto-derived button ID for a given input ID."""
    return f"{input_id}-button"


def get_error_id(input_id):
    """Return the auto-derived error ID for a given input ID."""
    return f"{input_id}-error"


def create_email_input(input_id, placeholder="Enter your email..."):
    """
    Create an email input component with built-in button and error message.

    Args:
        input_id: ID for the email input field. The button and error IDs
                  are auto-derived as '{input_id}-button' and '{input_id}-error'.
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
                        type="email",
                        placeholder=placeholder,
                    ),
                    html.Button(
                        "Send Email",
                        id=get_button_id(input_id),
                        n_clicks=0,
                        className="email-send-button",
                    ),
                ],
                className="email-input-row",
            ),
            html.Div(
                id=get_error_id(input_id),
                className="email-error",
            ),
        ],
        className="email-container",
    )

