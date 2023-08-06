from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models

__all__ = ["DonatePlugin"]


@plugin_pool.register_plugin
class DonatePlugin(CMSPluginBase):
    """
    Donate plugin
    """

    name = "Donate"
    model = models.Donate
    render_template = "plugins/donate.html"
