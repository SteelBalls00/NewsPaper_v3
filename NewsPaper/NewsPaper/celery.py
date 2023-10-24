import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'action_every_monday_8am': {
        'task': 'news.tasks.notify_about_weekly_post',
        # 'schedule': 5,
        'schedule': crontab(minute='00', hour='08', day_of_week='monday'),
    },
    'action_for_send_notifications': {
        'task': 'news.tasks.send_notifications',
        'schedule': 5,
    },
}

app.autodiscover_tasks()