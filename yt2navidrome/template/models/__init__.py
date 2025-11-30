import yaml

from .argument import Argument, argument_constructor, argument_representer
from .metadataparser import MetadataParser, metadataparser_constructor, metadataparser_representer
from .postprocessor import PostProcessor, postprocessor_constructor, postprocessor_representer
from .template import Template, template_constructor, template_representer

__all__ = ["Argument", "PostProcessor", "MetadataParser", "Template"]


def setup_yaml_constructors() -> None:
    """Register all YAML constructors"""
    yaml.add_constructor("!Argument", argument_constructor)
    yaml.add_constructor("!PostProcessor", postprocessor_constructor)
    yaml.add_constructor("!MetadataParser", metadataparser_constructor)
    yaml.add_constructor("!Template", template_constructor)


def setup_yaml_representers() -> None:
    """Register all YAML representers"""
    yaml.add_representer(Argument, argument_representer)
    yaml.add_representer(PostProcessor, postprocessor_representer)
    yaml.add_representer(MetadataParser, metadataparser_representer)
    yaml.add_representer(Template, template_representer)
