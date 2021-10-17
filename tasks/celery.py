from __future__ import absolute_import, unicode_literals

import os

from celery import Celery, Task
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WeXlog.settings')

#app = Celery('tasks', brocker=settings.CELERY_BROKER_URL, backend=settings.CELERY_BACKEND, include=['WeXlog.tasks'])
app = Celery("tasks", include=['WeXlog.tasks'])
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

if __name__ == '__main__':
    app.start()

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
