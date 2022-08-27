from http import HTTPStatus

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends

from notifications.containers import Container
from notifications.domain.templates import Template, TemplateService

from ..schemas import TemplateIn, TemplateList, TemplateUpdate

router = APIRouter(
    tags=["Templates"],
)


@router.post("", response_model=Template, summary="Создание шаблона", status_code=HTTPStatus.CREATED)
@inject
async def create_template(
    template: TemplateIn, *,
    template_service: TemplateService = Depends(Provide[Container.template_service]),
):
    """Создание нового шаблона уведомления."""
    return await template_service.create_new(Template(**template.dict()))


@router.get("", response_model=list[TemplateList], summary="Список шаблонов")
@inject
async def get_templates(
    *,
    template_service: TemplateService = Depends(Provide[Container.template_service]),
):
    """Получение списка сохраненных шаблонов."""
    return await template_service.get_all()


@router.patch("/{template_slug}", response_model=Template, summary="Обновление шаблона")
@inject
async def update_template_content(
    template_slug: str, template: TemplateUpdate, *,
    template_service: TemplateService = Depends(Provide[Container.template_service]),
):
    """Обновление шаблона по его слагу."""
    return await template_service.update_by_slug(template_slug, updated_template=template)


@router.delete("/{template_slug}", summary="Удаление шаблона", status_code=HTTPStatus.NO_CONTENT)
@inject
async def delete_template(
    template_slug: str, *,
    template_service: TemplateService = Depends(Provide[Container.template_service]),
):
    """Удаление шаблона по его слагу."""
    return await template_service.delete_by_slug(template_slug)
