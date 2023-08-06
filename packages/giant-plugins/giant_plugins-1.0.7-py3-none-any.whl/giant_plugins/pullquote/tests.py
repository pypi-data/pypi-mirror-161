import pytest

from . import cms_plugins, models


class TestPageCardPlugin:
    """
    Test case for the pullquote Plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.PullQuotePlugin()
        assert plugin.render_template == "plugins/pullquote/item.html"

    def test_block_template(self):
        """
        Test that the template of the plugin block is correct
        """
        plugin = cms_plugins.PullQuoteBlockPlugin()
        assert plugin.render_template == "plugins/pullquote/container.html"


@pytest.mark.django_db
class TestPageCardModel:
    """
    Test case for the pullquote Model
    """

    def test_str(self):
        obj = models.PullQuote.objects.create()
        assert str(obj) == "Pull quote 1"
