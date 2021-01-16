from datetime import timedelta

from celery.decorators import periodic_task
from django.conf import settings

from .wrapper import YoutubeWrapper

FETCH_INTERVAL = settings.FETCH_INTERVAL


@periodic_task(run_every=timedelta(seconds=FETCH_INTERVAL))
def save_search_result():
    wrapper = YoutubeWrapper()
    wrapper.save_data()
