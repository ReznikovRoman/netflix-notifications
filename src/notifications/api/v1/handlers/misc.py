from fastapi import APIRouter

router = APIRouter(
    tags=["misc"],
)


@router.get("/healthcheck", summary="'Здоровье' сервиса")
async def healthcheck():
    """Проверка состояния сервиса."""
    return {"status": "ok"}
