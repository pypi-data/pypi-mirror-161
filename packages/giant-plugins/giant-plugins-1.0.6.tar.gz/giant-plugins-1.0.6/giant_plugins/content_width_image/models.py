from django.db import models

from cms.models import CMSPlugin
from filer.fields.image import FilerImageField


class ContentWidthImage(CMSPlugin):
    """
    Represents an image object
    """

    image = FilerImageField(
        related_name="+", verbose_name="Content Width Image", on_delete=models.SET_NULL, null=True,
    )
    alt_text = models.CharField(max_length=64, help_text="Image name", blank=True, default="")
    caption = models.CharField(max_length=255, help_text="Add a caption to the image")
    credit = models.CharField(max_length=255)

    def __str__(self):
        """
        String representation of the object
        """
        return f"Content Width Image {self.pk}"
