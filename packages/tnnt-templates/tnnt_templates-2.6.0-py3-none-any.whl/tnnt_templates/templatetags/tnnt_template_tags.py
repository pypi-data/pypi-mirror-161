"""
Template filter for Terra Nanotech templates
"""

# Django
from django.apps import apps
from django.template.defaulttags import register
from django.templatetags.static import static

# AA Templates: Terra Nanotech
from tnnt_templates import __version__


@register.filter
def startswith(value, arg):
    """
    Usage, {% if value|starts_with:"arg" %}
    """

    return value.startswith(arg)


@register.simple_tag
def tnnt_static(path: str) -> str:
    """
    Versioned static URL
    :param path:
    :type path:
    :return:
    :rtype:
    """

    static_url = static(path)
    versioned_url = static_url + "?v=" + __version__

    return versioned_url


@register.simple_tag
def is_app_installed(app_name):
    """
    Check if a Django app is installed

    Usage:
    ```django
    {% load my_filters %}

    {% is_app_installed "myapp" as is_myapp_installed %}
    {% if is_myapp_installed %}
        ...
    {% endif %}
    ```
    :param app_name:
    :return:
    """

    return apps.is_installed(app_name)
