from cms.plugin_pool import plugin_pool

from giant_plugins.mixins import ExtendedPluginBase

from . import models

__all__ = ["ContentWidthImagePlugin"]


@plugin_pool.register_plugin
class ContentWidthImagePlugin(ExtendedPluginBase):
    """
    Image plugin
    """

    name = "Content Width Image"
    model = models.ContentWidthImage
    render_template = "plugins/content_width_image.html"
