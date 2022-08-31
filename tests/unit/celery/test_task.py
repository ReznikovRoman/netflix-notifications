import pytest
from celery.result import AsyncResult

test_key = "test-key"


def dummy_task(addend_a: int, addend_b: int) -> int:
    return addend_a + addend_b


@pytest.fixture
def task_factory(request, celery_app):
    def _task_factory(**kwargs):
        return celery_app.task(name=request.node.nodeid, **kwargs)(dummy_task)
    return _task_factory


class TestCeleryTask:
    """Тестирование переопределенного класса `celery.Task`."""

    def test_acquire_lock(self, task_factory, redis_client):
        """Установка блокировки работает корректно."""
        task = task_factory(lock_ttl=3)

        acquired_1 = task.acquire_lock(test_key)
        acquired_2 = task.acquire_lock(test_key)
        redis_client.flushdb()
        acquired_3 = task.acquire_lock(test_key)

        assert acquired_1 is True
        assert acquired_2 is False
        assert acquired_3 is True

    def test_acquire_lock_force(self, task_factory):
        """Установка блокировки с флагом `force` работает корректно."""
        task = task_factory(lock_ttl=100)

        acquired_1 = task.acquire_lock(test_key)
        acquired_2 = task.acquire_lock(test_key, force=True)

        assert acquired_1 is True
        assert acquired_2 is True

    def test_delay(self, task_factory, redis_client):
        """Задачи, отправленные в очередь методом `delay`, работают корректно."""
        task = task_factory(lock_ttl=3)

        result_1 = task.delay(1, addend_b=2)
        result_2 = task.delay(3, addend_b=4)
        redis_client.flushdb()
        result_3 = task.delay(5, addend_b=6)

        assert isinstance(result_1, AsyncResult)
        assert result_2 is None
        assert isinstance(result_3, AsyncResult)
        assert result_3.get() == 11

    def test_delay_force(self, task_factory):
        """Задачи, отправленные в очередь методом `delay` с установленным флагом `force`, работают корректно."""
        task = task_factory(lock_ttl=100)

        result_1 = task.delay(1, addend_b=2)
        result_2 = task.delay(3, addend_b=4, force=True)

        assert isinstance(result_1, AsyncResult)
        assert isinstance(result_2, AsyncResult)
        assert result_2.get() == 7

    def test_delay_without_lock_ttl(self, task_factory):
        """Задачи, отправленные в очередь методом `delay` без настройки ttl, работают корректно."""
        task = task_factory()

        result_1 = task.delay(1, addend_b=2)
        result_2 = task.delay(3, addend_b=4)

        assert isinstance(result_1, AsyncResult)
        assert isinstance(result_2, AsyncResult)
        assert result_2.get() == 7

    def test_apply_async(self, task_factory, redis_client):
        """Задачи, отправленные в очередь методом `apply_async`, работают корректно."""
        task = task_factory(lock_ttl=3)

        result_1 = task.apply_async((1,), {"addend_b": 2})
        result_2 = task.apply_async((3,), {"addend_b": 4})
        redis_client.flushdb()
        result_3 = task.apply_async((5,), {"addend_b": 6})

        assert isinstance(result_1, AsyncResult)
        assert result_2 is None
        assert isinstance(result_3, AsyncResult)
        assert result_3.get() == 11

    def test_apply_async_force(self, task_factory):
        """Задачи, отправленные в очередь методом `apply_async` с установленным флагом `force`, работают корректно."""
        task = task_factory(lock_ttl=100)

        result_1 = task.apply_async((1,), {"addend_b": 2})
        result_2 = task.apply_async((3,), {"addend_b": 4}, force=True)

        assert isinstance(result_1, AsyncResult)
        assert isinstance(result_2, AsyncResult)
        assert result_2.get() == 7

    def test_apply_async_without_lock_ttl(self, task_factory):
        """Задачи, отправленные в очередь методом `apply_async` без настройки ttl, работают корректно."""
        task = task_factory()

        result_1 = task.apply_async((1,), {"addend_b": 2})
        result_2 = task.apply_async((3,), {"addend_b": 4})

        assert isinstance(result_1, AsyncResult)
        assert isinstance(result_2, AsyncResult)
        assert result_2.get() == 7
