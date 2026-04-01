"""
Result card component.
Displays a result card with name, status badge, dates and access button.
"""

from dash import dcc, html

from components.badge import create_badge
from utils.i18n import t


def create_result_card(
    name,
    status,
    created_at=None,
    expired_at=None,
    remaining_time=None,
    result_id=None,
    lang="en",
):
    """
    Create a result card component.

    Args:
        name: The name/title of the result
        status: Status of the result ('success', 'pending', 'error')
        created_at: Creation date string (e.g., "03/05/2024")
        expired_at: Expiration date string (e.g., "03/05/2024")
        result_id: The ID of the result for the link

    Returns:
        html.Div: Result card component
    """
    # Determine badge class based on status
    # Possible statuses: pending, complete, error, climatic_trees, alignment, genetic_trees, output
    status_lower = status.lower() if status else ""

    if status_lower == "error":
        status_class = "error"
        status_text = t("results.card.status.error", lang)
    elif status_lower == "complete":
        status_class = "success"
        status_text = t("results.card.status.success", lang)
    else:
        status_class = "pending"
        status_text = t("results.card.status.in-progress", lang)

    # Build date info if provided
    date_info = []
    if created_at:
        date_info.append(
            html.Div(
                [
                    html.Img(src="/assets/icons/calendar.svg", className="result-card__date-icon-calendar"),
                    html.Span(f"{t('results.card.created', lang)} {created_at}"),
                ],
                className="result-card__date",
            )
        )
    if remaining_time:
        date_info.append(
            html.Div(
                [
                    html.Img(src="/assets/icons/clock.svg", className="result-card__date-icon"),
                    html.Span(remaining_time),
                ],
                className="result-card__date",
            )
        )
    elif expired_at:
        date_info.append(
            html.Div(
                [
                    html.Img(src="/assets/icons/clock.svg", className="result-card__date-icon"),
                    html.Span(f"{t('results.card.expired', lang)} {expired_at}"),
                ],
                className="result-card__date",
            )
        )

    return dcc.Link(
        [
            # Left section with title, badge and dates
            html.Div(
                [
                    # Title, badge, and progress bar
                    html.Div(
                        [
                            html.Div(name, className="result-card__title"),
                            create_badge(
                                status_text,
                                background_color=f"var(--{status_class})",
                                text_color="var(--text)",
                            ),
                        ],
                        className="result-card__header",
                    ),
                    # Dates row
                    html.Div(
                        date_info,
                        className="result-card__dates",
                    ) if date_info else None,
                ],
                className="result-card__content",
            ),
            # Right section with access button
            html.Div(
                [
                    html.Span(t("results.card.access", lang), className="result-card__access-text"),
                    html.Span("›", className="result-card__access-arrow"),
                ],
                className="result-card__access",
            ),
        ],
        href=f"/result/{result_id}" if result_id else "#",
        className=f"result-card result-card--{status_class}",
        refresh=False
    )
