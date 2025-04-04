import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectvendorr.settings')

# Create celery app
app = Celery('projectvendorr')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'send-daily-email-update': {
        'task': 'vendorapp.tasks.send_daily_email_update',
        'schedule': crontab(hour=9, minute=0),  # Runs daily at 9:00 AM
    },
}

# Export the app instance as 'celery'
celery = app