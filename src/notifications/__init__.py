from notifications.main import create_app

app = create_app()
celery_app = app.celery_app
