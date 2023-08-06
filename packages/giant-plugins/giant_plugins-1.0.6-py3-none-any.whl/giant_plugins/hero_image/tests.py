import pytest

from . import cms_plugins, models


class TestHeroImagePlugin:
    """
    Test case for the Hero Image Plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.HeroImagePlugin()
        assert plugin.render_template == "plugins/hero_image.html"


@pytest.mark.django_db
class TestHeroImageModel:
    """
    Test case for the Hero Image Model
    """

    def test_str(self):
        obj = models.HeroImage(pk=1)
        assert str(obj) == "Hero Image 1"
