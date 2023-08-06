from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from giant_plugins.key_stats import models

__all__ = ["KeyStatBlockPlugin", "KeyStatCardPlugin"]


@plugin_pool.register_plugin
class KeyStatBlockPlugin(CMSPluginBase):
    """
    Plugin for the key statistic block model
    """

    model = models.KeyStatBlock
    name = "Key Statistics"
    render_template = "plugins/key_stats/container.html"
    allow_children = True
    child_classes = ["KeyStatCardPlugin"]


@plugin_pool.register_plugin
class KeyStatCardPlugin(CMSPluginBase):
    """
    Plugin for key statistics card model
    """

    model = models.KeyStatCard
    name = "Statistic"
    render_template = "plugins/key_stats/card.html"
    require_parent = True
    parent_class = ["KeyStatBlockPlugin"]
