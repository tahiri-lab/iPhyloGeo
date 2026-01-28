"""
Reusable toast notification component.
Displays a notification popup in the bottom right corner.
"""

from dash import dcc, html


def create_toast_container():
    """
    Create the toast container that will hold all toast notifications.
    This should be added to the main app layout once.

    Returns:
        html.Div: Container for toast notifications with a store for messages
    """
    return html.Div(
        [
            dcc.Store(id="toast-store", data=None),
            dcc.Interval(
                id="toast-interval", interval=4000, n_intervals=0, disabled=True
            ),
            html.Div(
                id="toast-container",
                className="toast-container",
                children=[],
            ),
        ]
    )


def create_toast_message(message, toast_type="info"):
    """
    Create a toast message component.

    Args:
        message: The message to display
        toast_type: Type of toast - 'info', 'success', 'warning', 'error'

    Returns:
        html.Div: Toast message component
    """
    return html.Div(
        message,
        className=f"toast-message {toast_type}",
    )
