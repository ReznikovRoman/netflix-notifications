from http import HTTPStatus

from notifications.common.exceptions import NetflixNotificationsError


class InvalidNotificationTypeError(NetflixNotificationsError):
    """Неверный тип уведомления."""

    message = "Notification type is invalid"
    code = "invalid_notification_type"
    status_code: int = HTTPStatus.BAD_REQUEST
