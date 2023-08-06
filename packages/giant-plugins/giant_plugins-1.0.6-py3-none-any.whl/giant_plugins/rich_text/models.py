from django.utils.html import strip_tags
from django.utils.text import Truncator

from cms.models import CMSPlugin
from giant_plugins.utils import RichTextField


class RichText(CMSPlugin):
    """
    Represents rich text block using wysiwyg editor
    """

    text = RichTextField(verbose_name="Text")

    def __str__(self):
        """
        String representation of the object
        """
        return self.excerpt

    @property
    def plain_text(self):
        """
        Returns the rich text without any HTML
        """
        return strip_tags(self.text)

    @property
    def excerpt(self):
        """
        Returns an excerpt of the text in plain text
        """
        return Truncator(self.plain_text).words(num=20)
