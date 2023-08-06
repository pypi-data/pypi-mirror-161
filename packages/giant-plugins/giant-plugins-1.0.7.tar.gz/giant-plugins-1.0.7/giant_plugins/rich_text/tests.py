import pytest

from . import cms_plugins, models


class TestPageCardPlugin:
    """
    Test case for the Rich Text Plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.RichTextPlugin()
        assert plugin.render_template == "plugins/rich_text.html"


@pytest.mark.django_db
class TestPageCardModel:
    """
    Test case for the Rich Text Model
    """

    @pytest.fixture
    def plugin_instance(self):
        return models.RichText(
            text="<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Pellentesque pellentesque odio vel eros tempor bibendum."
            "Sed consequat cursus sapien vel ultricies."
            "Duis lorem lorem, ornare.</p>"
        )

    def test_str(self, plugin_instance):
        """
        Test string property
        """
        instance = plugin_instance
        assert str(instance) == instance.excerpt

    def test_strip_tags(self, plugin_instance):
        """
        Test the strip_tags property correctly removes the tags
        """
        instance = plugin_instance

        assert "<p>" not in instance.plain_text

    def test_excerpt(self, plugin_instance):
        """
        Test the truncation method returns the correct number of words
        """

        instance = plugin_instance
        word_count = len(instance.excerpt.split())
        assert word_count <= 20
