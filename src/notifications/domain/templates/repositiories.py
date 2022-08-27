from aredis_om import NotFoundError as RedisNotFoundError

from notifications.common.exceptions import ConflictError, NotFoundError
from notifications.infrastructure.db.repositories import RedisRepository

from .models import Template


class TemplateRepository:
    """Репозиторий для работы с данными шаблонов."""

    model = Template

    def __init__(self, redis_repository: RedisRepository[Template]) -> None:
        assert isinstance(redis_repository, RedisRepository)
        self._redis_repository = redis_repository

    async def create(self, template: Template, /) -> Template:
        """Создание нового шаблона."""
        try:
            await self.get_by_slug(template.slug)
        except NotFoundError:
            obj = await template.save()
            return obj
        else:
            raise ConflictError(message=f"Template with slug <{template.slug}> already exists.")

    async def get_or_create(self, template: Template, /) -> tuple[Template, bool]:
        """Получение шаблона по слагу или создание нового.

        Если шаблон не найден, то будет создан новый с заданными названием и содержимым.
        """
        default_template, created = await self._redis_repository.get_or_create(
            defaults={"content": template.content, "name": template.name},
            slug=template.slug,
        )
        return default_template, created

    async def get_by_slug(self, slug: str, /) -> Template:
        """Получение шаблона по слагу."""
        try:
            return await self.model.find((self.model.slug == slug)).first()
        except RedisNotFoundError:
            raise NotFoundError(f"There is no template with slug <{slug}>.")

    async def get_all(self) -> list[Template]:
        """Получение списка сохраненных шаблонов уведомлений."""
        return await self._redis_repository.model.find().all()

    async def update_fields_by_slug(self, slug: str, *, update_fields: dict) -> Template:
        """Обновление шаблона по слагу."""
        template = await self.get_by_slug(slug)
        for field, value in update_fields.items():
            if field == "slug":
                continue
            setattr(template, field, value)
        return await template.save()

    async def delete_by_slug(self, slug: str, /) -> None:
        """Удаление шаблона по слагу."""
        try:
            await self.model.find((self.model.slug == slug)).delete()
        except RedisNotFoundError:
            raise NotFoundError()
