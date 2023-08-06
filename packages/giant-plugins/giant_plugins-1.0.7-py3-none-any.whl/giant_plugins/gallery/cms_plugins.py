from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from giant_plugins.gallery import models


@plugin_pool.register_plugin
class GalleryBlockPlugin(CMSPluginBase):
    """
    Plugin for the gallery block model
    """

    model = models.GalleryBlock
    name = "Gallery Block"
    render_template = "plugins/gallery/container.html"
    allow_children = True
    child_classes = ["GalleryImagePlugin"]


@plugin_pool.register_plugin
class GalleryImagePlugin(CMSPluginBase):
    """
    Plugin for the gallery image model
    """

    model = models.GalleryImage
    name = "Gallery Image"
    render_template = "plugins/gallery/item.html"
    require_parent = True
    parent_class = ["GalleryBlockPlugin"]
