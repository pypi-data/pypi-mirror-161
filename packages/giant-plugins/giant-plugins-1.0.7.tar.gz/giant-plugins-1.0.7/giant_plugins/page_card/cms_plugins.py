from cms.plugin_pool import plugin_pool

from giant_plugins.mixins import ExtendedPluginBase

from . import models

__all__ = ["PageCardBlockPlugin", "PageCardPlugin"]


@plugin_pool.register_plugin
class PageCardBlockPlugin(ExtendedPluginBase):
    """
    Plugin for the page card block model
    """

    model = models.PageCardBlock
    name = "Page Cards Block"
    render_template = "plugins/page_card/container.html"
    allow_children = True
    child_classes = ["PageCardPlugin"]


@plugin_pool.register_plugin
class PageCardPlugin(ExtendedPluginBase):
    """
    Plugin for page card model
    """

    model = models.PageCard
    name = "Page Card"
    render_template = "plugins/page_card/item.html"
    require_parent = True
    parent_class = ["PageCardBlockPlugin"]
