# Django
from django.apps import AppConfig

from . import __version__


class YfTemplatesConfig(AppConfig):
    name = "yf_templates"
    label = "yf_templates"
    verbose_name = f"Yulai Federation Auth Templates v{__version__}"
