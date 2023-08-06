# Django
from django.apps import AppConfig

from . import __version__


class TemplateConfig(AppConfig):
    name = "sev3rance_auth_templates"
    label = "sev3rance_auth_templates"
    verbose_name = "Sev3rance Alliance Auth Templates v{version}".format(
        version=__version__
    )
