# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['giant_plugins',
 'giant_plugins.content_width_image',
 'giant_plugins.content_width_image.migrations',
 'giant_plugins.content_width_video',
 'giant_plugins.content_width_video.migrations',
 'giant_plugins.donate',
 'giant_plugins.donate.migrations',
 'giant_plugins.featured_cta',
 'giant_plugins.featured_cta.migrations',
 'giant_plugins.gallery',
 'giant_plugins.gallery.migrations',
 'giant_plugins.hero_image',
 'giant_plugins.hero_image.migrations',
 'giant_plugins.key_stats',
 'giant_plugins.key_stats.migrations',
 'giant_plugins.logo_grid',
 'giant_plugins.logo_grid.migrations',
 'giant_plugins.multilink',
 'giant_plugins.multilink.migrations',
 'giant_plugins.page_card',
 'giant_plugins.page_card.migrations',
 'giant_plugins.pullquote',
 'giant_plugins.pullquote.migrations',
 'giant_plugins.rich_text',
 'giant_plugins.rich_text.migrations',
 'giant_plugins.share_this_page',
 'giant_plugins.share_this_page.migrations']

package_data = \
{'': ['*'],
 'giant_plugins': ['static/vendor/summernote/*',
                   'static/vendor/summernote/font/*',
                   'static/vendor/summernote/lang/*',
                   'static/vendor/summernote/plugin/databasic/*',
                   'static/vendor/summernote/plugin/hello/*',
                   'static/vendor/summernote/plugin/specialchars/*',
                   'templates/plugins/*',
                   'templates/plugins/gallery/*',
                   'templates/plugins/key_stats/*',
                   'templates/plugins/logo_grid/*',
                   'templates/plugins/multilink/*',
                   'templates/plugins/page_card/*',
                   'templates/plugins/pullquote/*']}

install_requires = \
['django-filer', 'giant-mixins']

setup_kwargs = {
    'name': 'giant-plugins',
    'version': '1.0.6',
    'description': 'Adds a generic list of plugins for use within projects',
    'long_description': '# Giant Plugins\n\nA re-usable package which can be used in any project that requires a base set of plugins. \n\nThis will include a small set of plugins that are used in a large number of projects, but will not necessarily cover the full requirements. It will also provide a RichText field which can be used in other areas of the project\nThe RichText field uses ![summernote](https://github.com/summernote/summernote/) for styling the WYSIWYG widget.\n\n\nSupported Django versions:\n\n- Django 2.2, 3.2\n\nSupported django CMS versions:\n\n- django CMS 3.8, 3.9\n\n> &#x26a0;&#xfe0f; Release 1.0.0 and above are NOT compatible with\n> versions < 1 due to model name changes and a migration reset. Only upgrade to\n> this version if you are aware of what changes need to be made\n\n## Installation\n\nTo install with the package manager, run:\n\n    $ poetry add giant-plugins\n\nYou should then add `"giant_plugins"` to the `INSTALLED_APPS` in `base.py`. Move to "C \n\nThe structure of these files is slightly different than the norm, allowing for more control\nover which plugins are added to the Django project. In order to add the plugins it is\nadvised to create a `PLUGINS` variable in your settings file which will be appended to the\n`INSTALLED_APPS`. The following snippet will install all of the currently available plugins (note that this should be tweaked to suit your needs):\n\n```\nPLUGINS = [\n    "giant_plugins.content_width_image",\n    "giant_plugins.content_width_video",\n    "giant_plugins.donate",\n    "giant_plugins.featured_cta",\n    "giant_plugins.hero_image",\n    "giant_plugins.logo_grid",\n    "giant_plugins.page_card",\n    "giant_plugins.pullquote",\n    "giant_plugins.rich_text",\n    "giant_plugins.share_this_page",\n    "giant_plugins.gallery",\n    "giant_plugins.key_stats",\n    "giant_plugins.multilink",\n]\n\nINSTALLED_APPS = [...] + PLUGINS\n```\nOnce these have been added as such you can now run the `migrate` command and create the tables for the\ninstalled plugins.\n\n## Configuration\n\nIf you do not have a default WYSIWYG config then you can use the following settings:\n\n```\nSUMMERNOTE_CONFIG = (\n    {\n        "iframe": True,\n        "summernote": {\n            "airMode": False,\n            # Change editor size\n            "width": "100%",\n            "height": "480",\n            "lang": None,\n            "toolbar": [\n                ["style", ["style"]],\n                ["font", ["bold", "underline", "clear"]],\n                ["fontname", ["fontname"]],\n                ["color", ["color"]],\n                ["para", ["ul", "ol", "paragraph"]],\n                ["table", ["table"]],\n                ["insert", ["link", "picture", "video"]],\n                ["view", ["fullscreen", "codeview", "help"]],\n            ],\n        },\n    },\n)\n\n```\n\nIn order to specify a form to use for a specific plugin you should add something like this to your settings file:\n\n```\n<PLUGIN_NAME>_FORM = "<path.to.form.FormClass>"\n```\n\nWhere PLUGIN_NAME is the capitalised name of the plugin (e.g `TEXTWITHIMAGEPLUGIN_FORM`) and the path to the form class as a string so it can be imported.\n\n## Local development\n\nIn order to run `django-admin` commands you will need to set the `DJANGO_SETTINGS_MODULE` variable by running\n\n    $ export DJANGO_SETTINGS_MODULE=settings\n\nWhen adding a plugin you should add the new plugin to the `PLUGINS` variable in your settings file\nand to this README.\n\n\n\n ## Preparing for release\n \n In order to prep the package for a new release on TestPyPi and PyPi there is one key thing that you need to do. You need to update the version number in the `pyproject.toml`.\n This is so that the package can be published without running into version number conflicts. The version numbering must also follow the Semantic Version rules which can be found here https://semver.org/.\n \n \n ## Publishing\n \n Publishing a package with poetry is incredibly easy. Once you have checked that the version number has been updated (not the same as a previous version) then you only need to run two commands.\n \n    $ `poetry build` \n\nwill package the project up for you into a way that can be published.\n \n    $ `poetry publish`\n\nwill publish the package to PyPi. You will need to enter the username and password for the account which can be found in the company password manager\n',
    'author': 'Will-Hoey',
    'author_email': 'will.hoey@giantdigital.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/giantmade/giant-plugins',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
