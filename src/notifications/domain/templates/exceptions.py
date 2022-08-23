from http import HTTPStatus

from notifications.common.exceptions import NetflixNotificationsError


class InvalidSlugError(NetflixNotificationsError):
    """Некорректный слаг у шаблона."""

    message = "Slug is invalid"
    code = "invalid_template_slug"
    status_code: int = HTTPStatus.BAD_REQUEST


class InvalidTemplateContentError(NetflixNotificationsError):
    """Некорректное тело шаблона."""

    message = "Template content is invalid"
    code = "invalid_template_content"
    status_code: int = HTTPStatus.BAD_REQUEST
