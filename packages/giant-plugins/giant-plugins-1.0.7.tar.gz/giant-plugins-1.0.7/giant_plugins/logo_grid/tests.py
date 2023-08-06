from . import cms_plugins, models


class TestLogoModels:
    def test_block_str(self):
        """
        Test the string representation of the plugin
        """

        plugin = models.LogoBlock(pk=1)
        assert str(plugin) == "Logo block 1"

    def test_card_str(self):
        """
        Test the string representation of the plugin
        """

        plugin = models.LogoCard(pk=1)
        assert str(plugin) == "Logo card 1"

    def test_absolute_url_link(self):
        """
        Test bool is True when link is set
        """
        plugin = models.LogoCard(external_url="www.example.com")
        assert plugin.get_absolute_url()
        assert plugin.get_absolute_url() == "www.example.com"


class TestLogoPlugins:
    def test_block_template(self):
        """
        Test that the template of the block plugin is correct
        """
        container_plugin = cms_plugins.LogoBlockPlugin()
        assert container_plugin.render_template == "plugins/logo_grid/container.html"

    def test_card_template(self):
        """
        Test that the template of the card plugin is correct
        """
        item_plugin = cms_plugins.LogoCardPlugin()
        assert item_plugin.render_template == "plugins/logo_grid/item.html"
