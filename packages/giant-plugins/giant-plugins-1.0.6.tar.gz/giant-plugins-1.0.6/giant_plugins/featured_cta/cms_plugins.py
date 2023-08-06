from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models

__all__ = ["FeaturedCTAPlugin"]


@plugin_pool.register_plugin
class FeaturedCTAPlugin(CMSPluginBase):
    """
    Plugin for featured CTA
    """

    model = models.FeaturedCTA
    name = "Featured CTA"
    render_template = "plugins/featured_cta.html"
