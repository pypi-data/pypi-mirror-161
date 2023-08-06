from cms.plugin_pool import plugin_pool

from giant_plugins.mixins import ExtendedPluginBase

from . import models

__all__ = ["ContentWidthVideoPlugin"]


@plugin_pool.register_plugin
class ContentWidthVideoPlugin(ExtendedPluginBase):
    """
    Content width video plugin
    """

    name = "Content Width Video"
    model = models.ContentWidthVideo
    render_template = "plugins/content_width_video.html"
