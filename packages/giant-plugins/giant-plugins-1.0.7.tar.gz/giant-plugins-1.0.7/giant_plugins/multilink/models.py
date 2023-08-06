from django.db import models

from cms.models import CMSPlugin
from giant_plugins.utils import RichTextField
from mixins.models import URLMixin


class MultiLinkBlock(CMSPlugin):
    """
    Model for the MultiLink block. Container class which
    allows for displaying multiple cards
    """

    text = RichTextField(verbose_name="Text", blank=True)

    def __str__(self):
        return f"MultiLink card container #{self.pk}"


class MultiLinkCard(CMSPlugin):
    """
    Holds one or more links and details for a multilink card
    via the Link model
    """

    title = models.CharField(max_length=255)

    def __str__(self):
        """
        Returns the string representation of the object
        """
        return f"Multilink card #{self.pk}"

    def copy_relations(self, oldinstance):
        self.links.all().delete()

        for link in oldinstance.links.all():
            link.pk = None
            link.card = self
            link.save()


class Link(URLMixin):
    """
    Stores a title and link to be used on the card
    """

    card = models.ForeignKey(
        to=MultiLinkCard, null=True, on_delete=models.SET_NULL, related_name="links"
    )
    link_text = models.CharField(max_length=255)

    def __str__(self):
        return f"Link {self.pk} for {self.card}"
