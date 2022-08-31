from notifications.infrastructure.db.cache import CacheKeyBuilder


def base_key_factory(key_builder: CacheKeyBuilder, min_length: int, *args, **kwargs) -> str:
    """Фабрика по созданию ключей для кэша."""
    base_key: str = kwargs.pop("base_key")
    prefix: str | None = kwargs.pop("prefix", None)
    suffix: str | None = kwargs.pop("suffix", None)
    return key_builder.make_key(base_key, min_length=min_length, prefix=prefix, suffix=suffix)
