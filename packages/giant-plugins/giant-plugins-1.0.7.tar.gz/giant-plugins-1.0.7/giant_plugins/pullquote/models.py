from django.db import models
from django.utils.translation import ugettext as _
from filer.fields.image import FilerImageField
from giant_plugins.utils import RichTextField

from cms.models import CMSPlugin


class PullQuoteBlock(CMSPlugin):
    """
    Block for the quotes to sit in
    """

    pass


class PullQuote(CMSPlugin):
    """
    Model for a pull quote plugin
    """

    TEXT_SIDE_RIGHT = "right"
    TEXT_SIDE_LEFT = "left"
    TEXT_SIDE_CHOICES = ((TEXT_SIDE_RIGHT, "Right"), (TEXT_SIDE_LEFT, "Left"))

    text_side = models.CharField(
        max_length=255,
        choices=TEXT_SIDE_CHOICES,
        default=TEXT_SIDE_RIGHT
    )
    quote = RichTextField()
    caption = models.CharField(max_length=255, blank=True)
    image = FilerImageField(
        related_name="+",
        blank=True,
        null=True,
        help_text="Choose an optional image",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        """
        String representation of the object
        """
        return f"Pull quote {self.pk}"
