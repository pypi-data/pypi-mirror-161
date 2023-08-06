from giant_plugins.multilink import cms_plugins


class TestMultiLinkPlugins:
    """
    Test case for the multilink plugin
    """

    def test_parent_template(self):
        """
        Test that the template of the parent plugin is correct
        """
        plugin = cms_plugins.MultiLinkBlockPlugin()
        assert plugin.render_template == "plugins/multilink/container.html"

    def test_child_template(self):
        """
        Test that the template of the child plugin is correct
        """
        plugin = cms_plugins.MultiLinkCardPlugin()
        assert plugin.render_template == "plugins/multilink/card.html"
