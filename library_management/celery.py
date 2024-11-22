from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')

app = Celery('library_management')

# Use Django settings and specify the CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all installed Django apps
app.autodiscover_tasks()

app.conf.update(
    worker_pool='solo',  # For Windows
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')