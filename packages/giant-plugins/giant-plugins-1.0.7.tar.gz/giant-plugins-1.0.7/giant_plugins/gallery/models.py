from django.db import models

from cms.models import CMSPlugin
from filer.fields.image import FilerImageField


class GalleryBlock(CMSPlugin):
    """
    Model for the Gallery block. Container class which
    allows for displaying multiple images
    """

    class Display:
        # Mimic Django3 TextChoices for backwards compatibility
        CAROUSEL = "carousel"
        THUMBNAILS = "thumbnails"
        choices = tuple((v, v.title()) for v in [CAROUSEL, THUMBNAILS])

    display = models.CharField(max_length=255, choices=Display.choices, default=Display.CAROUSEL)

    def __str__(self):
        """
        Returns the string representation of the object
        """
        return f"Gallery plugin {self.pk}"


class GalleryImage(CMSPlugin):
    """
    Holds an image and details for a gallery image item
    """

    image = FilerImageField(related_name="+", on_delete=models.SET_NULL, null=True)
    photo_credit = models.CharField(
        max_length=255, blank=True, help_text="This will only be displayed on the modal"
    )
    caption = models.CharField(
        max_length=255, blank=True, help_text="This will only be displayed on the modal"
    )

    def __str__(self):
        return f"Gallery image {self.pk}"
