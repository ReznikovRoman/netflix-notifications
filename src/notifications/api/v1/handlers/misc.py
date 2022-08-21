from dependency_injector.wiring import inject

from fastapi import APIRouter

router = APIRouter(
    tags=["misc"],
)


@router.get("/healthcheck", summary="'Здоровье' сервиса")
@inject
async def healthcheck():
    """Проверка состояния сервиса."""
    return {"status": "ok"}
