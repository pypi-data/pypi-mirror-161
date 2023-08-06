import pytest

from . import models, cms_plugins


class TestDonatePlugin:
    """
    Test case for the Donate Plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.DonatePlugin()
        assert plugin.render_template == "plugins/donate.html"


class TestDonate:
    def test_build_url(self):
        """
        Test the url property outputs the correctly formatted
        url
        """
        obj = models.Donate(campaign="donate", donation_url="www.example.com",)

        assert obj.url == "www.example.com/donate/"
