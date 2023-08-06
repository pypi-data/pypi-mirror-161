from django.db import models

from cms.models import CMSPlugin


class KeyStatBlock(CMSPlugin):
    """
    Model for the Key Statistics block
    """

    def __str__(self):
        """
        String representation of the object
        """
        return f"Key Statistics container {self.pk}"


class KeyStatCard(CMSPlugin):
    """
    Model for the Key Statistic card plugin. Uses rich text to allow the use of subscript
    """

    large_text = models.CharField(max_length=16)
    small_text = models.CharField(max_length=48)

    def __str__(self):
        return f"Key Statistics card {self.pk}"
