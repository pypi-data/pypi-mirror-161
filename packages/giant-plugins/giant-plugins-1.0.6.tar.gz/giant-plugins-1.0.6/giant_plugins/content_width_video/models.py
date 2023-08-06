from cms.models import CMSPlugin
from django.db import models
from filer.fields.image import FilerImageField
from mixins.models import VideoURLMixin


class ContentWidthVideo(CMSPlugin, VideoURLMixin):
    """
    Represents a content width video object
    """

    image = FilerImageField(
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=128, blank=True)
    caption = models.CharField(max_length=128)
    alt_text = models.CharField(max_length=128, blank=True, default="")
    display_image = models.BooleanField(default=True)

    def __str__(self):
        """
        String representation of the object
        """
        return f"Content Width Video {self.pk}"

    def get_video_id(self):
        """
        Return the youtube video ID
        """
        youtube_id = parse_qs(urlparse(self.youtube_url).query)["v"][0]
        return youtube_id

    def fallback_thumbnail(self):
        """
        Returns a fallback thumbnail for the video
        """

        return f"https://img.youtube.com/vi/{self.get_video_id()}/maxresdefault.jpg"
