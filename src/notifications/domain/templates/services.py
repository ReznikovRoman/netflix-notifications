from typing import Any

from jinja2 import BaseLoader, Environment, TemplateSyntaxError

from notifications.helpers import SLUG_REGEX

from .exceptions import InvalidSlugError, InvalidTemplateContentError
from .models import Template
from .repositiories import TemplateRepository


class TemplateService:
    """Сервис для работы с шаблонами уведомлений."""

    def __init__(self, template_repository: TemplateRepository) -> None:
        assert isinstance(template_repository, TemplateRepository)
        self._template_repository = template_repository

    async def create_new(self, template: Template) -> Template:
        """Создание нового шаблона уведомления."""
        self._validate_slug(template.slug)
        self.validate_content(template.content)
        return await self._template_repository.create(template)

    async def get_all(self) -> list[Template]:
        """Получение списка всех шаблонов уведомлений."""
        return await self._template_repository.get_all()

    async def get_by_slug(self, slug: str, /) -> Template:
        """Получение шаблона уведомления по слагу."""
        return await self._template_repository.get_by_slug(slug)

    async def update_content_by_slug(self, slug: str, *, content: str) -> Template:
        """Обновление содержания шаблона по его слагу."""
        self._validate_slug(slug)
        self.validate_content(content)
        return await self._template_repository.update_content_by_slug(slug, content)

    async def delete_by_slug(self, slug: str, /) -> None:
        """Удаление шаблона по слагу."""
        self._validate_slug(slug)
        await self._template_repository.delete_by_slug(slug)

    @staticmethod
    def render_template_from_string(content: str, *, context: dict[str, Any]) -> str:
        """Рендеринг шаблона/строки с помощью переданного контекста."""
        rendered_template = Environment(loader=BaseLoader()).from_string(content).render(**context)
        return rendered_template

    @staticmethod
    def validate_content(content: str, /) -> None:
        """Валидация содержимого шаблона.

        Проверка на совместимость с Jinja2.
        """
        try:
            Environment(loader=BaseLoader()).from_string(content).render()
        except TemplateSyntaxError:
            raise InvalidTemplateContentError()

    @staticmethod
    def _validate_slug(slug: str, /) -> None:
        if not SLUG_REGEX.match(slug):
            raise InvalidSlugError()
