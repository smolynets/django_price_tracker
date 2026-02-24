import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # 'run-daily-at-midnight': {
    #     'task': 'prices.tasks.run_daily_logic',
    #     'schedule': crontab(hour=0, minute=0),
    # },
    'test-every-minute': {
        'task': 'prices.tasks.run_daily_logic',
        'schedule': crontab(minute='*'),
    },
}
