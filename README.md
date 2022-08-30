# Netflix Notifications
Сервис работы с уведомлениями в онлайн-кинотеатре _Netflix_.

## Сервисы
- Netflix Admin:
  - Панель администратора для управления онлайн-кинотеатром (редактирование фильмов, жанров, актеров)
  - https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL:
  - ETL пайплайн для синхронизации данных между БД сервиса Netflix Admin и Elasticsearch
  - https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API:
  - АПИ фильмов
  - https://github.com/ReznikovRoman/netflix-movies-api
- Netflix Auth API:
  - Сервис авторизации - управление пользователями и ролями
  - https://github.com/ReznikovRoman/netflix-auth-api
- Netflix UGC:
  - Сервис для работы с пользовательским контентом
  - https://github.com/ReznikovRoman/netflix-ugc
- Netflix Notifications:
  - Сервис для отправки уведомлений
  - https://github.com/ReznikovRoman/netflix-notifications

## Настройка и запуск
docker-compose содержат контейнеры:
 1. server
 2. traefik

Файлы docker-compose:
 1. `docker-compose.yml` - для локальной разработки.
 2. `tests/functional/docker-compose.yml` - для функциональных тестов.

Для запуска контейнеров нужно создать файл `.env` в корне проекта.

**Пример `.env`:**

```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Notifications
# Project
NN_DEBUG=1
NN_PROJECT_BASE_URL=http://api-notifications.localhost:8011
NN_SERVER_PORT=8004
NN_PROJECT_NAME=netflix-notifications
NN_API_V1_STR=/api/v1
NN_SERVER_NAME=localhost
NN_SERVER_HOSTS=http://api-notifications.localhost:8011
# Auth
NAA_SECRET_KEY=changeme
# Postgres
NN_DB_HOST=db
NN_DB_PORT=5432
NN_DB_NAME=netflix_notifications
NN_DB_USER=yandex
NN_DB_PASSWORD=netflix
# Redis
NN_REDIS_DECODE_RESPONSES=1
NN_REDIS_PORT=6379
NN_REDIS_URL=redis://redis-primary:6379/0
NN_REDIS_OM_URL=redis://@redis-primary:6379
# Celery
NN_CELERY_BROKER_URL=redis://redis-celery:6379/0
NN_CELERY_RESULT_BACKEND=redis://redis-celery:6379/0
# Flower
NN_FLOWER_PORT=8888
# Config
NN_USE_STUBS=0
NN_TESTING=0
NN_CI=1
```

### Запуск проекта:

Локально:
```shell
docker-compose build
docker-compose up
```

## Разработка
Синхронизировать окружение с `requirements.txt` / `requirements.dev.txt` (установит отсутствующие пакеты, удалит лишние, обновит несоответствующие версии):
```shell
make sync-requirements
```

Сгенерировать requirements.\*.txt files (нужно пере-генерировать после изменений в файлах requirements.\*.in):
```shell
make compile-requirements
```

Используем `requirements.local.in` для пакетов, которые нужно только разработчику. Обязательно нужно указывать _constraints files_ (-c ...)

Пример:
```shell
# requirements.local.txt

-c requirements.txt

ipython
```

### Тесты
Запуск тестов (всех, кроме функциональных) с экспортом переменных окружения из `.env` файла:
```shell
export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst) && make test
```

Для функциональных тестов нужно создать файл `.env` в папке ./tests/functional

**Пример `.env` (для корректной работы тестов надо подставить корректные значения для NAA):**
```dotenv
# Tests
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Notifications
# Project
NN_DEBUG=1
NN_PROJECT_BASE_URL=http://api-notifications.localhost:8011
NN_SERVER_PORT=8004
NN_PROJECT_NAME=netflix-notifications
NN_API_V1_STR=/api/v1
NN_SERVER_NAME=localhost
NN_SERVER_HOSTS=http://api-notifications.localhost:8011
# Auth
NAA_SECRET_KEY=changeme
# Postgres
NN_DB_HOST=db
NN_DB_PORT=5432
NN_DB_NAME=netflix_notifications
NN_DB_USER=yandex
NN_DB_PASSWORD=netflix
# Redis
NN_REDIS_DECODE_RESPONSES=1
NN_REDIS_PORT=6379
NN_REDIS_URL=redis://redis-primary:6379/0
NN_REDIS_OM_URL=redis://@redis-primary:6379
# Celery
NN_CELERY_BROKER_URL=redis://redis-celery:6379/0
NN_CELERY_RESULT_BACKEND=redis://redis-celery:6379/0
# Flower
NN_FLOWER_PORT=8888
# Config
NN_USE_STUBS=1
NN_TESTING=1
NN_CI=0
```

Запуск функциональных тестов:
```shell
cd ./tests/functional && docker-compose up test
```

Или через рецепт Makefile:
```shell
make dtf
```

### Code style:
Перед коммитом проверяем, что код соответствует всем требованиям:

```shell
make lint
```

### pre-commit:
Для настройки pre-commit:
```shell
pre-commit install
```

## Документация
Документация в формате OpenAPI 3 доступна по адресам:
- `${PROJECT_BASE_URL}/api/v1/docs` - Swagger
