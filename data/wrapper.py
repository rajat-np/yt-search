import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from django.conf import settings

from .models import Video


class YoutubeWrapper(object):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    api_service_name = 'youtube'
    api_version = 'v3'

    def client_init(self, api_key):
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name,
            self.api_version,
            developerKey=api_key,
        )

    def get_data(self, published_after=None):
        for api_key in settings.YOUTUBE_API_KEY:
            try:
                self.client_init(api_key)
                request = self.youtube.search().list(
                    type='video',
                    part='snippet',
                    order='date',
                    q='cricket',
                    publishedAfter=published_after
                )
                response = request.execute()
                break
            except googleapiclient.errors.HttpError:
                continue
        return response['items']

    def extract_data(self, item):
        source_id = item.get('id').get('videoId')
        snippet = item.get('snippet', {})
        title = snippet.get('title')
        description = snippet.get('description')
        published_at = snippet.get('publishedAt')
        thumbnails = snippet.get('thumbnails')
        return {
            'source_id': source_id,
            'title': title,
            'description': description,
            'published_at': published_at,
            'thumbnails': [thumbnails]
        }

    def save_data(self):
        last_video = Video.objects.last()
        items = self.get_data(
            last_video.published_at.isoformat() if last_video else None
        )
        videos = [
            Video(**self.extract_data(item))
            for item in items
        ]
        Video.objects.bulk_create(
            videos,
            ignore_conflicts=True
        )
