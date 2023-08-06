from . import cms_plugins


class TestShareThisPagePlugin:
    """
    Test case for the Share This Page plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.ShareThisPagePlugin()
        assert plugin.render_template == "plugins/share_this_page.html"
