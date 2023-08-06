from cms.plugin_pool import plugin_pool

from giant_plugins.mixins import ExtendedPluginBase

from . import models

__all__ = ["HeroImagePlugin"]


@plugin_pool.register_plugin
class HeroImagePlugin(ExtendedPluginBase):
    """
    CMS plugin for the Image Hero model
    """

    model = models.HeroImage
    name = "Image Hero"
    render_template = "plugins/hero_image.html"
