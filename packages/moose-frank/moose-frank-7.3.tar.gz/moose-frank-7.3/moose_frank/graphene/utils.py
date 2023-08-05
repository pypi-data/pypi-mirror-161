from importlib import import_module

from django.core.exceptions import ImproperlyConfigured


def _get_module_method(path_name):
    if not path_name:
        return
    module_name, method_name = path_name.rsplit(".", 1)
    try:
        mod = import_module(module_name)
    except ImportError as e:
        raise ImproperlyConfigured(
            ('Error importing module %s: "%s"' % (module_name, e))
        )
    return getattr(mod, method_name)
