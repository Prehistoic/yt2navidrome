from dataclasses import dataclass

import yaml
from yaml.dumper import Dumper
from yaml.loader import FullLoader

from yt2navidrome.template.models.metadataparser import MetadataParser


@dataclass
class Template:
    """Represents the configuration required to download a YT video or playlist with yt-dlp"""

    name: str
    url: str
    playlist: bool
    parsers: list[MetadataParser]

    def summary(cls) -> str:
        template_type = "playlist" if cls.playlist else "video"
        return f"{cls.name} ({template_type}) -> {cls.url}"


# 1. Custom Representer (Python object -> YAML)
def template_representer(dumper: Dumper, data: Template) -> yaml.nodes.MappingNode:
    """
    Represents the Template dataclass instance as a YAML mapping.
    """
    return dumper.represent_mapping(
        "!Template", {"name": data.name, "url": data.url, "playlist": data.playlist, "parsers": data.parsers}
    )


# 2. Custom Constructor (YAML -> Python object)
def template_constructor(loader: FullLoader, node: yaml.nodes.MappingNode) -> Template:
    """
    Constructs a Template dataclass instance from a YAML mapping.
    """
    mapping = loader.construct_mapping(node, deep=True)
    return Template(**mapping)
