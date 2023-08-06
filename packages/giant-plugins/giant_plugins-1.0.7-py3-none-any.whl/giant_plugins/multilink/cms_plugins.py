from django.contrib import admin

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from giant_plugins.multilink import models

__all__ = ["MultiLinkBlockPlugin", "MultiLinkCardPlugin"]


class LinkInlineAdmin(admin.StackedInline):
    model = models.Link
    extra = 1
    fields = [
        "link_text",
        "internal_link",
        "external_url",
    ]


@plugin_pool.register_plugin
class MultiLinkBlockPlugin(CMSPluginBase):
    """
    Plugin for the multilink block model
    """

    model = models.MultiLinkBlock
    name = "MultiLink Block"
    render_template = "plugins/multilink/container.html"
    allow_children = True
    child_classes = ["MultiLinkCardPlugin"]


@plugin_pool.register_plugin
class MultiLinkCardPlugin(CMSPluginBase):
    """
    Plugin for the multilink card model
    """

    model = models.MultiLinkCard
    name = "MultiLink Card"
    render_template = "plugins/multilink/card.html"
    require_parent = True
    parent_class = ["MultiLinkBlockPlugin"]
    exclude = ["file"]
    inlines = [LinkInlineAdmin]
