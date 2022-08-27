from http import HTTPStatus

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends

from notifications.containers import Container
from notifications.domain.messages import NotificationDispatcherService

from ..schemas import NotificationIn, NotificationShortDetails

router = APIRouter(
    tags=["M2M"],
)


@router.post(
    "/notifications",
    response_model=NotificationShortDetails,
    summary="Отправка уведомления",
    status_code=HTTPStatus.ACCEPTED,
)
@inject
async def send_notification(
    notification: NotificationIn, *,
    notification_dispatcher: NotificationDispatcherService = Depends(
        Provide[Container.notification_dispatcher_service],
    ),
):
    """Отправка одного уведомления пользователю."""
    notification_details = await notification_dispatcher.dispatch_notification(notification)
    return notification_details
