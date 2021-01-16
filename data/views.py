from rest_framework import viewsets

from .models import Video
from .serializers import VideoSerializer
from .filters import DynamicSearchFilter


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (DynamicSearchFilter,)
    queryset = Video.objects.all().order_by('-published_at')
    serializer_class = VideoSerializer
