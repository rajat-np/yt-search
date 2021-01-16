from django.db import models

# Create your models here.
class Video(models.Model):
    source_id = models.CharField(max_length=50)
    title = models.TextField()
    description = models.TextField(blank=True)
    published_at = models.DateTimeField()
    thumbnails = models.JSONField()

    def __str__(self):
        return self.title
