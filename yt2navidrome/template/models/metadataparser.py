from dataclasses import dataclass

import yaml
from yaml.dumper import Dumper
from yaml.loader import FullLoader

from yt2navidrome.template.models import PostProcessor


@dataclass
class MetadataParser:
    """Represents a parser used to process video information
    and convert it into metadata for the downloaded video file"""

    source: str
    pattern: str
    post_processors: list[PostProcessor] | None = None

    def summary(self) -> str:
        return f"{self.source} = {self.pattern}"


# 1. Custom Representer (Python object -> YAML)
def metadataparser_representer(dumper: Dumper, data: MetadataParser) -> yaml.nodes.MappingNode:
    """
    Represents the MetadataParser dataclass instance as a YAML mapping.
    """
    mapping = {
        "source": data.source,
        "pattern": data.pattern,
    }
    if data.post_processors:
        mapping.update({"post_processors": data.post_processors})

    return dumper.represent_mapping("!MetadataParser", mapping)


# 2. Custom Constructor (YAML -> Python object)
def metadataparser_constructor(loader: FullLoader, node: yaml.nodes.MappingNode) -> MetadataParser:
    """
    Constructs a MetadataParser dataclass instance from a YAML mapping.
    """
    mapping = loader.construct_mapping(node, deep=True)
    return MetadataParser(**mapping)
