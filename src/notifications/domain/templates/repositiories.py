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

    async def get_by_slug(self, slug: str, /) -> Template:
        """Получение шаблона по слагу."""
        try:
            return await self.model.find((self.model.slug == slug)).first()
        except RedisNotFoundError:
            raise NotFoundError()

    async def get_all(self) -> list[Template]:
        """Получение списка сохраненных шаблонов уведомлений."""
        return await self._redis_repository.model.find().all()

    async def update_content_by_slug(self, slug: str, content: str) -> Template:
        """Обновление контента/содержимого шаблона по слагу."""
        template = await self.get_by_slug(slug)
        template.content = content
        return await template.save()

    async def delete_by_slug(self, slug: str, /) -> None:
        """Удаление шаблона по слагу."""
        try:
            await self.model.find((self.model.slug == slug)).delete()
        except RedisNotFoundError:
            raise NotFoundError()