from cms.plugin_base import CMSPluginBase
from django.utils.module_loading import import_string

from django.conf import settings


class ExtendedPluginBase(CMSPluginBase):
    """
    An extension of the plugin base to allow us to
    use getattr calls for some of the fields such as 
    form/formfields
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(settings, f"{self.get_upper_class_name()}_FORM"):
            self.form = self.get_form_class()

    def get_form_class(self):
        """
        Returns the form class to use with the plugin
        """
        return import_string(getattr(settings, f"{self.get_upper_class_name()}_FORM"))

    @classmethod
    def get_upper_class_name(cls):
        """
        Returns the uppercase of the class name
        as this is how it'll be set in the settings
        """
        return cls.__name__.upper()
