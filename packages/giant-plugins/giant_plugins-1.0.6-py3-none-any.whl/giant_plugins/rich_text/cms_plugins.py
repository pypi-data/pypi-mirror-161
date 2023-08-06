from cms.plugin_pool import plugin_pool

from giant_plugins.mixins import ExtendedPluginBase

from . import models

__all__ = ["RichTextPlugin"]


@plugin_pool.register_plugin
class RichTextPlugin(ExtendedPluginBase):
    """
    Rich text plugin
    """

    name = "Rich Text"
    model = models.RichText
    render_template = "plugins/rich_text.html"
