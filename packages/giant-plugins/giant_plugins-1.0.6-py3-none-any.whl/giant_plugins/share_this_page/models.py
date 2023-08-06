from cms.models import CMSPlugin

from django.db import models


class ShareThisPage(CMSPlugin):
    """
    Plugin for a share this page block
    """

    linkedin = models.BooleanField(
        default=False, help_text="Check this to show the LinkedIn share button"
    )
    facebook = models.BooleanField(
        default=False, help_text="Check this to show the Facebook share button"
    )
    email = models.BooleanField(
        default=False, help_text="Check this to show the Email share button"
    )
    twitter = models.BooleanField(
        default=False, help_text="Check this to show the Twitter share button"
    )
    whatsapp = models.BooleanField(
        default=False, help_text="Check this to show the Whatsapp share button"
    )

    def __str__(self):
        """
        String representation of the Share plugin instance
        """
        return f"Share plugin {self.pk}"
