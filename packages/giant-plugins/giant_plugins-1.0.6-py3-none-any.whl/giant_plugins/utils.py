"""Contains classes which are required for some of the plugins"""
import json

from typing import Optional

from django.conf import settings
from django.contrib.admin import options
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms import Media, Textarea
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.safestring import mark_safe


def get_setting(setting: str) -> Optional[object]:
    """Return the provided setting, or None."""
    return getattr(settings, setting, None)


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super().default(obj)


class SummernoteWidget(Textarea):
    """
    Used to render WYSIWYG into the backend of the site.
    """

    def __init__(self, attrs=None, editor_options=None):
        super().__init__(attrs)
        self.editor_options = (
            editor_options or get_setting("WYSIWYG_CONFIG") or get_setting("SUMMERNOTE_CONFIG")
        )

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""
        attrs["data-config"] = self.js_config
        cls = attrs.get("class", "")
        attrs["class"] = (
            cls + " uninitialised wysiwyg-init" if cls else "uninitialised wysiwyg-init"
        )
        final_attrs = self.build_attrs(self.attrs, attrs, name=name)
        return mark_safe(f"<textarea{flatatt(final_attrs)}>\r\n{force_text(value)}</textarea>")

    def build_attrs(self, base_attrs, extra_attrs=None, **kwargs):
        """
        Helper function for building an attribute dictionary.
        This is combination of the same method from Django<=1.10 and Django1.11+
        """
        attrs = dict(base_attrs, **kwargs)
        if extra_attrs:
            attrs.update(extra_attrs)
        return attrs

    @property
    def js_config(self):
        """
        Outputs config as JSON object for redactor.js to load
        """
        return json.dumps(self.editor_options, cls=LazyEncoder)

    @property
    def media(self):
        """
        Returns media files for django to output
        """
        css = {"all": ("vendor/summernote/summernote-lite.min.css",)}
        js = (
            "vendor/summernote/summernote-lite.min.js",
            "vendor/summernote/init.js",
        )

        return Media(css=css, js=js)


class RichTextField(models.TextField):
    """
    Override the default widget for Textfield to use Summernote WYSIWYG
    """

    def formfield(self, **kwargs):
        defaults = {"widget": get_setting("WYSIWYG_WIDGET") or SummernoteWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


options.FORMFIELD_FOR_DBFIELD_DEFAULTS[RichTextField] = {
    "widget": get_setting("WYSIWYG_WIDGET") or SummernoteWidget
}
