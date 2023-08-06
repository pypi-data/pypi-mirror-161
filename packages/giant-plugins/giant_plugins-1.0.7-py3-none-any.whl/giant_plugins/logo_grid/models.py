from django.db import models

from cms.models import CMSPlugin
from filer.fields.image import FilerImageField
from mixins.models import URLMixin


class LogoBlock(CMSPlugin):
    """
    Model for the Client block plugin.
    """

    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        """
        String representation of the block plugin
        """
        return f"Logo block {self.pk}"


class LogoCard(CMSPlugin, URLMixin):
    """
    Model for the client card plugin
    """

    logo = FilerImageField(related_name="company_logo", null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        """
        Return a string representation of the object
        """
        return f"Logo card {self.pk}"
