import pytest

from . import cms_plugins, models


class TestContentWidthImagePlugin:
    """
    Test case for the ContentWidthImage Plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.ContentWidthImagePlugin()
        assert plugin.render_template == "plugins/content_width_image.html"


@pytest.mark.django_db
class TestContentWidthImageModel:
    """
    Test case for the ContentWidthImage Model
    """

    def test_str(self):
        obj = models.ContentWidthImage.objects.create()
        assert str(obj) == "Content Width Image 1"
