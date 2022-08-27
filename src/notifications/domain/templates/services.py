from typing import Any

from jinja2 import BaseLoader, Environment, TemplateSyntaxError

from notifications.api.v1.schemas import TemplateUpdate
from notifications.helpers import SLUG_REGEX
from notifications.infrastructure.emails.constants import TEMPLATES_DIR

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

    async def create_default_template(self, name: str, slug: str, filename: str) -> Template:
        """Создание шаблона по умолчанию.

        Если шаблон уже существует, то новый создан не будет.
        """
        self._validate_slug(slug)
        template = Template(name=name, slug=slug, content=self.extract_content_from_file(filename))
        default_template, _ = await self._template_repository.get_or_create(template)
        return default_template

    async def get_all(self) -> list[Template]:
        """Получение списка всех шаблонов уведомлений."""
        return await self._template_repository.get_all()

    async def get_by_slug(self, slug: str, /) -> Template:
        """Получение шаблона уведомления по слагу."""
        self._validate_slug(slug)
        return await self._template_repository.get_by_slug(slug)

    async def update_by_slug(self, slug: str, *, updated_template: TemplateUpdate) -> Template:
        """Обновление шаблона по его слагу."""
        self._validate_slug(slug)
        if updated_content := updated_template.content:
            self.validate_content(updated_content)
        fields_to_update = updated_template.dict(exclude_none=True)
        return await self._template_repository.update_fields_by_slug(slug, update_fields=fields_to_update)

    async def delete_by_slug(self, slug: str, /) -> None:
        """Удаление шаблона по слагу."""
        self._validate_slug(slug)
        await self._template_repository.delete_by_slug(slug)

    @staticmethod
    def extract_content_from_file(filename: str, /) -> str:
        """Получение содержимого из файла."""
        with open(TEMPLATES_DIR / filename, "r") as file:
            return file.read()

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
