from django.test import TestCase

from giant_plugins.gallery import cms_plugins


class TestGalleryPlugins(TestCase):
    """
    Test case for the gallery plugin
    """

    def test_parent_template(self):
        """
        Test that the template of the parent plugin is correct
        """
        plugin = cms_plugins.GalleryBlockPlugin()
        assert plugin.render_template == "plugins/gallery/container.html"

    def test_child_template(self):
        """
        Test that the template of the child plugin is correct
        """
        plugin = cms_plugins.GalleryImagePlugin()
        assert plugin.render_template == "plugins/gallery/item.html"
