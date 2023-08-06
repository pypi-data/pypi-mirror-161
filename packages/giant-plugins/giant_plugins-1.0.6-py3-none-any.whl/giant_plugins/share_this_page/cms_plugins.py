from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models

__all__ = ["ShareThisPagePlugin"]


@plugin_pool.register_plugin
class ShareThisPagePlugin(CMSPluginBase):
    """
    Share this page plugin
    """

    name = "Share This Page"
    model = models.ShareThisPage
    render_template = "plugins/share_this_page.html"
