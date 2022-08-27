# Netflix Notifications
Сервис для работы с уведомлениями.

## Технологии
- FastAPI
- PostgreSQL
  - Основное хранилище
- Celery
  - Распределенная очередь сообщений
  - [celery-sqlalchemy-scheduler](https://github.com/AngelLiang/celery-sqlalchemy-scheduler)
    - Бэкенд для celery-beat на основе SQLAlchemy

## АПИ
- M2M (Machine to Machine)
  - Отправка уведомления конкретному пользователю
    - `POST /api/v1/notifications`
    - Клиент может указать slug шаблона для использования в письме `template_slug`:
      - Если шаблон указан, то текст в `content` игнорируется
      - Если шаблон не указан, то необходимо обязательно заполнить поле `content`
    - Каждый запрос сопровождается контекстом для рендеринга шаблона. Контекст содержит:
      - значения, необходимые для рендеринга шаблона `template_slug` (если такой шаблон указан)
      - `context` необязателен для заполнения
    - Клиент может указать тип `notification_type` сообщения:
      - email: отправка уведомления на почту
      - На данном этапе реализована только отправка на почту,
        в будущем можно добавлять и другие типы (пуш-уведомление на телефон, websocket и др.)
    - Клиент может указать приоритет `priority` сообщения:
      - urgent: сообщение будет отправлено в специально выделенную очередь и будет обработано как можно быстрее
      - common: сообщение будет отправлено в общую и обработано в стандартном порядке
      - default: сообщение будет обработано в стандартном порядке
      - XXX: сообщение с любым другим значением `priority` (кроме "urgent", "notifications" и "default")
        будет отправлено в очередь по умолчанию
    - Тело запроса
      ```json
        {
          "subject": "Welcome, user!",
          "notification_type": "email",
          "priority": "common",
          "recipient_list": [
            "user@gmail.com"
          ],
          "content": "XXX",
          "template_slug": "example_slug",
          "context": {
            "var": "value"
          }
        }
      ```
    - Тело ответа
      ```json
        {
          "notification_id": "b55d75e5-8193-4cbf-9383-0cfeff3bf140",
          "queue": "common"
        }
      ```
  - Получение списка шаблонов писем
    - `GET /api/v1/templates`
    - Тело ответа
      ```json
        [
          {
            "pk": "b55d75e5-8193-4cbf-9383-0cfeff3bf140",
            "name": "Greeting email",
            "slug": "greeting_email"
          }
        ]
      ```
  - Создание нового шаблона письма
    - `POST /api/v1/templates`
    - Тело запроса
      ```json
        {
          "name": "Greeting email",
          "slug": "greeting_email",
          "content": "Welcome, {{ full_name }}!"
        }
      ```
    - Тело ответа
      ```json
        {
          "pk": "b55d75e5-8193-4cbf-9383-0cfeff3bf140",
          "name": "Greeting email",
          "slug": "greeting_email",
          "content": "Welcome, {{ full_name }}!"
        }
      ```
  - Редактирование шаблона письма
    - `PATCH /api/v1/templates/{template_slug}`
    - Тело запроса
      ```json
        {
          "name": "Greeting email v2",
          "content": "Welcome, {{ first_name }}!"
        }
      ```
  - Удаление шаблона письма
    - `DELETE /api/v1/templates/{template_slug}`
- Admin Panel
  - Получение списка зарегистрированных celery задач
    - `GET /api/v1/tasks`
    - Тело ответа
      ```json
        [
          {
            "task_id": "b55d75e5-8193-4cbf-9383-0cfeff3bf140",
            "slug": "send_email"
          }
        ]
      ```
  - Создание новой периодической задачи
    - `POST /api/v1/periodic-tasks`
    - one_off: задача запустится только один раз
    - Тело запроса
      ```json
        {
          "name": "Digest every 7 days",
          "task_id": "b55d75e5-8193-4cbf-9383-0cfeff3bf140",
          "template_id": "b55d75e5-8193-4cbf-9383-0cfeff3bf140",
          "crontab_schedule": "0 0 * * 0",
          "one_off": false
        }
      ```
