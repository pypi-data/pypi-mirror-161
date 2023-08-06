from django.core.exceptions import ValidationError
from django.db import models

from cms.models import CMSPlugin
from giant_plugins.utils import RichTextField
from mixins.models import URLMixin

__all__ = ["FeaturedCTA"]


class FeaturedCTA(CMSPlugin, URLMixin):
    """
    Model for the featured cta plugin
    """

    title = RichTextField()
    caption = models.CharField(max_length=255, blank=True)
    cta_text = models.CharField(max_length=255)

    def __str__(self):
        """
        String representation of the object
        """
        return f"Featured CTA {self.pk}"

    def clean(self):
        """
        Ensure user selects either internal or external url
        """

        if not self.internal_link and not self.external_url:
            raise ValidationError("Please either choose a page or add a custom URL.")
