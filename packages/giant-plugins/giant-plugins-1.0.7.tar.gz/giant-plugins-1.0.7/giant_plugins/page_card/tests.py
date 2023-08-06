import pytest

from . import cms_plugins, models


class TestPageCardPlugin:
    """
    Test case for the PageCard Plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.PageCardPlugin()
        assert plugin.render_template == "plugins/page_card/item.html"

    def test_block_template(self):
        """
        Test that the template of the plugin block is correct
        """
        plugin = cms_plugins.PageCardBlockPlugin()
        assert plugin.render_template == "plugins/page_card/container.html"


@pytest.mark.django_db
class TestPageCardModel:
    """
    Test case for the PageCard Model
    """

    def test_str(self):
        obj = models.PageCard.objects.create()
        assert str(obj) == "Page Card #1"
