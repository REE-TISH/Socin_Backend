import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Socin_backend.settings')

app = Celery('Socin_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
