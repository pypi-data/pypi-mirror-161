from django.utils.translation import gettext_lazy
from importlib.metadata import version

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    name = "pretix_extended_api"
    verbose_name = "Extended API"

    class PretixPluginMeta:
        name = gettext_lazy("Extended API")
        author = "Python Italia"
        description = gettext_lazy(
            "Extend the REST API to expose more information needed by PyCon Italia"
        )
        visible = True
        version = version("pretix-plugin-extended-api")
        category = "API"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = "pretix_extended_api.PluginApp"
