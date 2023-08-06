from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models

__all__ = ["LogoBlockPlugin", "LogoCardPlugin"]


@plugin_pool.register_plugin
class LogoBlockPlugin(CMSPluginBase):
    """
    Plugin class for the Client card block
    """

    model = models.LogoBlock
    name = "Logo Grid Block"
    render_template = "plugins/logo_grid/container.html"
    allow_children = True
    child_classes = ["LogoCardPlugin"]


@plugin_pool.register_plugin
class LogoCardPlugin(CMSPluginBase):
    """
    Plugin for client card model
    """

    model = models.LogoCard
    name = "Logo Card"
    render_template = "plugins/logo_grid/item.html"
    require_parent = True
    parent_class = ["LogoBlockPlugin"]
