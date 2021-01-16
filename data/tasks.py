from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import task
from datetime import timedelta

from .wrapper import YoutubeWrapper


@periodic_task(run_every=timedelta(seconds=30))
def save_search_result():
    wrapper = YoutubeWrapper()
    wrapper.save_data()
