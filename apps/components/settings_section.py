"""
Reusable page section components.
Provides create_settings_section and create_field helpers for building
consistent page layouts across the application (settings, help, results, etc.).
"""

from dash import html


def create_settings_section(title, children, icon_src=None):
    """
    Create a styled page section with an icon + title header.

    Args:
        title: Section title text (e.g., "Genetic parameters")
        children: List of Dash components (fields/rows) inside the section
        icon_src: Optional path to an SVG icon. If None, a placeholder div is shown.

    Returns:
        html.Div: A styled page section
    """
    if icon_src:
        icon = html.Div(
            className="page-section-icon",
            style={
                "mask-image": f"url({icon_src})",
                "-webkit-mask-image": f"url({icon_src})",
            }
        )
    else:
        icon = html.Div(className="page-section-icon placeholder")

    return html.Div(
        [
            html.Div(
                [icon, html.H3(title, className="page-section-title")],
                className="page-section-header",
            ),
            html.Div(children, className="page-grid"),
        ],
        className="page-section",
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
            html.Label(label, className="page-field-label"),
            component,
        ],
        className="page-field",
    )
