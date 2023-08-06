# See: https://realpython.com/python37-new-features/#customization-of-module-attributes

from importlib import import_module, resources

PLUGINS = {}


def register_plugin(func):
    """Decorator to register plug-ins"""
    name = func.__name__
    PLUGINS[name] = func
    return func


def register_stitcher(name):
    """Decorator to register stitcher plug-ins"""

    def decorator(func):
        PLUGINS[name] = func
        return func

    return decorator


def get_plugin(name):
    return __getattr__(name)


def __getattr__(name):
    """Return a named plugin"""
    try:
        return PLUGINS[name]
    except KeyError:
        _import_plugins()
        if name in PLUGINS:
            return PLUGINS[name]
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            ) from None


def __dir__():
    """List available plug-ins"""
    _import_plugins()
    return list(PLUGINS.keys())


def _import_plugins():
    """Import all resources to register plug-ins"""
    for name in resources.contents(__name__):
        if name.endswith(".py"):
            import_module(f"{__name__}.{name[:-3]}")
