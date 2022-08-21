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
    - `POST /api/v1/notifications?template_slug=xxx`
    - Клиент может указать slug шаблона для использования в письме через query параметр `template_slug`
    - Каждый запрос сопровождается контекстом для рендеринга шаблона. Контекст содержит:
      - content: основной текстовый блок с контентом
      - xxx: другие значения, необходимые для рендеринга шаблона `template_slug` (если такой шаблон указан)
    - Клиент может указать приоритет `priority` сообщения:
      - urgent: сообщение будет отправлено в специально выделенную очередь и будет обработано как можно быстрее
      - emails: сообщение будет отправлено в выделенную очередь для электронных писем и обработано в стандартном порядке
      - default: сообщение будет обработано в стандартном порядке
      - XXX: сообщение с любым другим значением `priority` (кроме "urgent", "notifications" и "default")
        будет отправлено в очередь по умолчанию
    - Тело запроса
      ```json
        {
          "recipient_list": [
            "user@gmail.com"
          ],
          "subject": "Welcome, user!",
          "priority": "emails",
          "context": {
            "content": "John, thanks for signing up."
          }
        }
      ```
    - Тело ответа
      ```json
        {
          "message_id": "b55d75e5-8193-4cbf-9383-0cfeff3bf140",
          "queue": "emails"
        }
      ```
  - Получение списка шаблонов писем
    - `GET /api/v1/templates`
    - Тело ответа
      ```json
        [
          {
            "template_id": "b55d75e5-8193-4cbf-9383-0cfeff3bf140",
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
          "template_id": "b55d75e5-8193-4cbf-9383-0cfeff3bf140"
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
