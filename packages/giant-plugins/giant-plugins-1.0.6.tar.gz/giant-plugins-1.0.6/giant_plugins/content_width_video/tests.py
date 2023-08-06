import pytest

from . import cms_plugins, models


class TestContentWidthVideoPlugin:
    """
    Test case for the ContentWidthVideo Plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.ContentWidthVideoPlugin()
        assert plugin.render_template == "plugins/content_width_video.html"


@pytest.mark.django_db
class TestContentWidthVideoModel:
    """
    Test case for the ContentWidthVideo Model
    """

    def test_str(self):
        obj = models.ContentWidthVideo.objects.create()
        assert str(obj) == "Content Width Video 1"
