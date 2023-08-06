from django.db import models

from cms.models import CMSPlugin
from filer.fields.image import FilerImageField

from mixins.models import URLMixin


class HeroImage(CMSPlugin, URLMixin):
    """
    Model for the Image Hero plugin
    """

    RATIO_SQUARE = "square"
    RATIO_4_3 = "4_3"
    RATIO_16_9 = "16_9"
    RATIO_21_9 = "21_9"
    RATIO_CHOICES = [
        (RATIO_SQUARE, "Square"),
        (RATIO_4_3, "4:3"),
        (RATIO_16_9, "16:9"),
        (RATIO_21_9, "21:9"),
    ]

    title = models.CharField(max_length=255, blank=True)
    strapline = models.CharField(max_length=255, blank=True)
    image = FilerImageField(related_name="+", on_delete=models.SET_NULL, null=True)
    height = models.CharField(
        max_length=255,
        choices=RATIO_CHOICES,
        default=RATIO_SQUARE,
        help_text="We recommend selecting the aspect ratio that most closely matches the image that you are using."
        " We will use this to aid with the image position.",
    )
    cta_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        """
        String representation of the object
        """
        return f"Hero Image {self.pk}"
