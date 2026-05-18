import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sonali_bank.settings')

app = Celery('sonali_bank')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'delete-old-pending-applications': {
        'task': 'accounts.tasks.delete_old_pending_applications',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}