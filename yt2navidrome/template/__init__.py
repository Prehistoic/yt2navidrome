from .models import setup_yaml_constructors, setup_yaml_representers
from .reader import TemplateReader

__all__ = ["TemplateReader"]

# Setup all YAML constructors and representers
setup_yaml_constructors()
setup_yaml_representers()
