from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cars.settings')

app = Celery('cars')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# app.worker_max_memory_per_child = 50000
#
# CELERY_QUEUES = (
#     Queue('high', Exchange('high'), routing_key='high'),
#     Queue('normal', Exchange('normal'), routing_key='normal'),
#     Queue('low', Exchange('low'), routing_key='low'),
# )
# CELERY_DEFAULT_QUEUE = 'normal'
# CELERY_DEFAULT_EXCHANGE = 'normal'
# CELERY_DEFAULT_ROUTING_KEY = 'normal'
# CELERY_ROUTES = {
#     # -- HIGH PRIORITY QUEUE -- #
#     'myapp.tasks.check_payment_status': {'queue': 'high'},
#     # -- LOW PRIORITY QUEUE -- #
#     'myapp.tasks.close_session': {'queue': 'low'},
# }

app.conf.beat_schedule = {
    'update_autoRia_every_hour': {
        'task': 'parsers.tasks.upd_ria',
        'schedule': crontab(minute=30, hour='*/3'),
        'args': (3,),
        # 'options': {"queue": 'normal'}
        # 'options': {"expires": 10799, 'max_retries': 0}

    },
    # 'upd_ab_every_hour': {
    #     'task': 'parsers.tasks.upd_ab',
    #     'schedule': crontab(minute=1, hour='*/2'),
    #     # 'args': (3,),
    #     'options': {"queue": 'low'}
    #     # 'options': {"expires": 10799, 'max_retries': 0}
    #
    # },
    # 'inner_ab_every_hour': {
    #     'task': 'parsers.tasks.inner_ab',
    #     'schedule': crontab(minute=49, hour='*/2'),
    #     # 'args': (3,),
    #     'options': {"queue": 'low'}
    # },
    # 'inner_olx_every_30_minutes': {
    #     'task': 'parsers.tasks.inner_olx',
    #     'schedule': crontab(minute='*/20'),
    # },
    # 'updater_olx_every_30_minutes': {
    #     'task': 'parsers.tasks.updater_olx',
    #     'schedule': crontab(hour='*/2'),
    # }
}
