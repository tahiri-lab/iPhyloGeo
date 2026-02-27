"""
Reusable settings section components.
Provides create_settings_section and create_field helpers for building
consistent settings forms across the application.
"""

from dash import html


def create_settings_section(title, children, icon_src=None):
    """
    Create a styled settings section with an icon placeholder + title header.

    Args:
        title: Section title text (e.g., "Genetic parameters")
        children: List of Dash components (fields/rows) inside the section
        icon_src: Optional path to an icon image. If None, a placeholder div is shown.

    Returns:
        html.Div: A styled settings section
    """
    if icon_src:
        icon = html.Div(
            className="settings-section-icon",
            style={
                "mask-image": f"url({icon_src})",
                "-webkit-mask-image": f"url({icon_src})",
            }
        )
    else:
        icon = html.Div(className="settings-section-icon placeholder")

    return html.Div(
        [
            html.Div(
                [icon, html.H3(title, className="settings-section-title")],
                className="settings-section-header",
            ),
            html.Div(children, className="settings-grid"),
        ],
        className="settings-section",
    )


def create_field(label, component):
    """
    Create a labeled form field.

    Args:
        label: Label text for the field
        component: A Dash input or dropdown component

    Returns:
        html.Div: A styled field with label + component
    """
    return html.Div(
        [
            html.Label(label, className="settings-field-label"),
            component,
        ],
        className="settings-field",
    )
