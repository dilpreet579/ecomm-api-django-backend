import os
from celery import Celery

# set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("ecomm_api")

# read config from Django settings, namespace CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")

# auto-discover tasks from all installed apps
app.autodiscover_tasks()
