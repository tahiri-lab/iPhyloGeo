from dash import html


def create_badge(text, background_color=None, text_color=None, class_name=""):
    """Create a reusable badge with configurable colors."""
    classes = "app-badge"
    if class_name:
        classes = f"{classes} {class_name}"

    style = {}
    if background_color is not None:
        style["--badge-bg-color"] = background_color
    if text_color is not None:
        style["--badge-text-color"] = text_color

    return html.Span(
        text,
        className=classes,
        style=style,
    )
