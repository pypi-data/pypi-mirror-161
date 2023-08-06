# Giant Plugins

A re-usable package which can be used in any project that requires a base set of plugins. 

This will include a small set of plugins that are used in a large number of projects, but will not necessarily cover the full requirements. It will also provide a RichText field which can be used in other areas of the project
The RichText field uses ![summernote](https://github.com/summernote/summernote/) for styling the WYSIWYG widget.


Supported Django versions:

- Django 2.2, 3.2

Supported django CMS versions:

- django CMS 3.8, 3.9

> &#x26a0;&#xfe0f; Release 1.0.0 and above are NOT compatible with
> versions < 1 due to model name changes and a migration reset. Only upgrade to
> this version if you are aware of what changes need to be made

## Installation

To install with the package manager, run:

    $ poetry add giant-plugins

You should then add `"giant_plugins"` to the `INSTALLED_APPS` in `base.py`. Move to "C 

The structure of these files is slightly different than the norm, allowing for more control
over which plugins are added to the Django project. In order to add the plugins it is
advised to create a `PLUGINS` variable in your settings file which will be appended to the
`INSTALLED_APPS`. The following snippet will install all of the currently available plugins (note that this should be tweaked to suit your needs):

```
PLUGINS = [
    "giant_plugins.content_width_image",
    "giant_plugins.content_width_video",
    "giant_plugins.donate",
    "giant_plugins.featured_cta",
    "giant_plugins.hero_image",
    "giant_plugins.logo_grid",
    "giant_plugins.page_card",
    "giant_plugins.pullquote",
    "giant_plugins.rich_text",
    "giant_plugins.share_this_page",
    "giant_plugins.gallery",
    "giant_plugins.key_stats",
    "giant_plugins.multilink",
]

INSTALLED_APPS = [...] + PLUGINS
```
Once these have been added as such you can now run the `migrate` command and create the tables for the
installed plugins.

## Configuration

If you do not have a default WYSIWYG config then you can use the following settings:

```
SUMMERNOTE_CONFIG = (
    {
        "iframe": True,
        "summernote": {
            "airMode": False,
            # Change editor size
            "width": "100%",
            "height": "480",
            "lang": None,
            "toolbar": [
                ["style", ["style"]],
                ["font", ["bold", "underline", "clear"]],
                ["fontname", ["fontname"]],
                ["color", ["color"]],
                ["para", ["ul", "ol", "paragraph"]],
                ["table", ["table"]],
                ["insert", ["link", "picture", "video"]],
                ["view", ["fullscreen", "codeview", "help"]],
            ],
        },
    },
)

```

In order to specify a form to use for a specific plugin you should add something like this to your settings file:

```
<PLUGIN_NAME>_FORM = "<path.to.form.FormClass>"
```

Where PLUGIN_NAME is the capitalised name of the plugin (e.g `TEXTWITHIMAGEPLUGIN_FORM`) and the path to the form class as a string so it can be imported.

## Local development

In order to run `django-admin` commands you will need to set the `DJANGO_SETTINGS_MODULE` variable by running

    $ export DJANGO_SETTINGS_MODULE=settings

When adding a plugin you should add the new plugin to the `PLUGINS` variable in your settings file
and to this README.



 ## Preparing for release
 
 In order to prep the package for a new release on TestPyPi and PyPi there is one key thing that you need to do. You need to update the version number in the `pyproject.toml`.
 This is so that the package can be published without running into version number conflicts. The version numbering must also follow the Semantic Version rules which can be found here https://semver.org/.
 
 
 ## Publishing
 
 Publishing a package with poetry is incredibly easy. Once you have checked that the version number has been updated (not the same as a previous version) then you only need to run two commands.
 
    $ `poetry build` 

will package the project up for you into a way that can be published.
 
    $ `poetry publish`

will publish the package to PyPi. You will need to enter the username and password for the account which can be found in the company password manager
