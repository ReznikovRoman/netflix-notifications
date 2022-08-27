from fastapi import APIRouter

from .handlers import dashboard, m2m, misc, templates

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(m2m.router)
api_v1_router.include_router(templates.router, prefix="/templates")
api_v1_router.include_router(dashboard.router)
api_v1_router.include_router(misc.router)
