import os
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from logging.config import dictConfig
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@after_setup_logger.connect
def setup_loggers(logger, **kwargs):
    """
    CeleryワーカーのメインロガーにDjangoのLOGGING設定を適用する
    """
    dictConfig(settings.LOGGING)

@after_setup_task_logger.connect
def setup_task_loggers(logger, **kwargs):
    """
    Celeryの各タスクロガーにDjangoのLOGGING設定を適用する
    """
    dictConfig(settings.LOGGING)