from giant_plugins.key_stats import cms_plugins


class TestKeyStatPlugins:
    """
    Test case for the key statistic plugins
    """

    def test_parent_template(self):
        """
        Test that the template of the parent plugin is correct
        """
        plugin = cms_plugins.KeyStatBlockPlugin()
        assert plugin.render_template == "plugins/key_stats/container.html"

    def test_child_template(self):
        """
        Test that the template of the child plugin is correct
        """
        plugin = cms_plugins.KeyStatCardPlugin()
        assert plugin.render_template == "plugins/key_stats/card.html"
