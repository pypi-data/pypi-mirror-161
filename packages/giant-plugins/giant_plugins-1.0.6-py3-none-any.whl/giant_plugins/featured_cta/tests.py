from . import cms_plugins, models


class TestFeaturedCTAPlugin:
    """
    Test case for the featured cta
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.FeaturedCTAPlugin()
        assert plugin.render_template == "plugins/featured_cta.html"


class TestFeaturedCTAModel:
    """
    Test case for the featured cta Model
    """

    def test_str(self):
        obj = models.FeaturedCTA(pk=1)
        assert str(obj) == "Featured CTA 1"
