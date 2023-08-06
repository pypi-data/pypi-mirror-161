from django.db import models

from cms.models import CMSPlugin
from filer.fields.image import FilerImageField
from mixins.models import URLMixin
from giant_plugins.utils import RichTextField


class PageCardBlock(CMSPlugin):
    """
    Model for the page card block plugin
    """

    LAYOUT_STACKED = "stacked"
    LAYOUT_LEFT_RIGHT = "left_right"
    LAYOUT_CHOICES = ((LAYOUT_STACKED, "Stacked"), (LAYOUT_LEFT_RIGHT, "Left/Right"))

    THEME_FULL_WIDTH = "full-width"
    THEME_CONTENT_WIDTH = "content-width"
    THEME_CHOICES = ((THEME_FULL_WIDTH, "Full width"), (THEME_CONTENT_WIDTH, "Content width"))

    BG_COLOUR_DARK = "dark"
    BG_COLOUR_LIGHT = "light"
    BG_COLOUR_CHOICES = ((BG_COLOUR_DARK, "Dark"), (BG_COLOUR_LIGHT, "Light"))

    layout = models.CharField(max_length=255, choices=LAYOUT_CHOICES, default=LAYOUT_LEFT_RIGHT)

    title = RichTextField(blank=True)
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default=THEME_CONTENT_WIDTH)
    background_colour = models.CharField(
        max_length=30, choices=BG_COLOUR_CHOICES, default=BG_COLOUR_LIGHT
    )

    def __str__(self):
        """
        String representation of the object
        """
        return f"Page card container {self.pk}"


class PageCard(CMSPlugin, URLMixin):
    """
    A model for an individual page card
    """

    title = models.CharField(max_length=255, blank=True)
    summary = models.CharField(max_length=140, blank=True, help_text="Limited to 140 characters")
    image = FilerImageField(related_name="+", on_delete=models.SET_NULL, null=True, blank=True)
    cta_text = models.CharField(max_length=50, default="Read more")

    def __str__(self):
        """
        String representation of the object
        """
        return f"Page Card #{self.pk}"
