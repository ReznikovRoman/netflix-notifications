from http import HTTPStatus

from notifications.common.exceptions import NetflixNotificationsError


class InvalidNotificationTypeError(NetflixNotificationsError):
    """Неверный тип уведомления."""

    message = "Notification type is invalid"
    code = "invalid_notification_type"
    status_code: int = HTTPStatus.BAD_REQUEST


class NotificationCooldownError(NetflixNotificationsError):
    """Кулдаун отправки уведомлений."""

    message = "Notification service is in cooldown, try to send a request later"
    code = "notification_cooldown"
    status_code = HTTPStatus.REQUEST_TIMEOUT
