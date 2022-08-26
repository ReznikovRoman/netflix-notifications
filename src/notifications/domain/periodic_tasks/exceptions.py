from http import HTTPStatus

from notifications.common.exceptions import NetflixNotificationsError


class UnknownCeleryTaskError(NetflixNotificationsError):
    """Неизвестная Celery задача, которая недоступна в панели администратора."""

    message = "Unknown celery task. Check if it is registered."
    code = "unknown_celery_task"
    status_code: int = HTTPStatus.BAD_REQUEST
