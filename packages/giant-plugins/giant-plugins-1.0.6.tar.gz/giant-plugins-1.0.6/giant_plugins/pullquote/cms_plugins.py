from cms.plugin_pool import plugin_pool

from giant_plugins.mixins import ExtendedPluginBase

from . import models

__all__ = ["PullQuotePlugin", "PullQuoteBlockPlugin"]


@plugin_pool.register_plugin
class PullQuoteBlockPlugin(ExtendedPluginBase):
    """
    Plugin base for the quote block
    """

    model = models.PullQuoteBlock
    name = "Pull Quote Block"
    render_template = "plugins/pullquote/container.html"
    allow_children = True
    child_classes = ["PullQuotePlugin"]


@plugin_pool.register_plugin
class PullQuotePlugin(ExtendedPluginBase):
    """
    Plugin base for pull quote model
    """

    model = models.PullQuote
    name = "Pull Quote"
    render_template = "plugins/pullquote/item.html"
