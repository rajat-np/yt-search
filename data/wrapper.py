import googleapiclient.discovery
import googleapiclient.errors
from django.conf import settings

from .models import Video


class YoutubeWrapper(object):
    """
    Wrapper class to fetch, process and save youtube api data.
    """

    api_service_name = "youtube"
    api_version = "v3"
    search_query = settings.YOUTUBE_QUERY

    def client_init(self, api_key):
        """
        Initialize youtube api client.

        :param api_key: API key obtained from a project with Youtube
                        Data API enabled.
        """
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name,
            self.api_version,
            developerKey=api_key,
        )

    def get_data(self, published_after=None):
        """
        Fetch videos data from youtube API

        Iterate over all the YOUTUBE_API_KEY to find a valid API_KEY.
        Break the loop when the request is processed without any error
        or check for the next API_KEY.

        :param published_after: time after which data should be fetched
                                from the API.
        :return: list of videos information or an empty list.
        """
        for api_key in settings.YOUTUBE_API_KEY:
            try:
                self.client_init(api_key)
                request = self.youtube.search().list(
                    type="video",
                    part="snippet",
                    order="date",
                    q=self.search_query,
                    publishedAfter=published_after,
                )
                response = request.execute()
                break
            except googleapiclient.errors.HttpError:
                continue
        return response.get("items", [])

    def extract_data(self, item):
        """
        Extract required data from the video item to be saved in the database.

        :param item: video item returned from the youtube API.
        :return: formatted data according to the db fields
        """
        source_id = item.get("id").get("videoId")
        snippet = item.get("snippet", {})
        title = snippet.get("title")
        description = snippet.get("description")
        published_at = snippet.get("publishedAt")
        thumbnails = snippet.get("thumbnails")
        return {
            "source_id": source_id,
            "title": title,
            "description": description,
            "published_at": published_at,
            "thumbnails": [thumbnails],
        }

    def save_data(self):
        """
        Save formatted video data to db

        Use published_at of last video to get data which is published after that time.
        Assuming query remains same.
        Loop over all video items to initialize a list of Video Objects and use Django's
        bulk_create to create all items at once.
        """
        last_video = Video.objects.last()
        items = self.get_data(
            last_video.published_at.isoformat() if last_video else None
        )
        videos = [Video(**self.extract_data(item)) for item in items]
        Video.objects.bulk_create(videos, ignore_conflicts=True)
