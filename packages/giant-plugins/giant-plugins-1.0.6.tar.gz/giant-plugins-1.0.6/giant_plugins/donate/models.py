from django.db import models

from cms.models import CMSPlugin


class Donate(CMSPlugin):
    """
    Plugin for a Donate element
    """

    campaign = models.CharField(max_length=255)
    donation_url = models.URLField()
    title = models.CharField(max_length=255, blank=True)
    text = models.TextField(blank=True)

    def __str__(self):
        """
        String representation of the plugin object
        """
        return f"Donate {self.pk}. Campaign: {self.campaign}"

    @property
    def url(self):
        """
        Build URL
        """
        return f"{self.donation_url}/{self.campaign}/"
