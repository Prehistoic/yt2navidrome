from dataclasses import dataclass

import yaml
from yaml.dumper import Dumper
from yaml.loader import FullLoader

from yt2navidrome.template.models.argument import Argument


@dataclass
class PostProcessor:
    """Represents a post processor used to refined metadata
    already parsed with the MetadataParser"""

    action: str
    input: str | list[str]
    output: str
    args: list[Argument] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.input, str):
            self.input = [self.input]

    def summary(self) -> str:
        return f"{self.output} = {self.action} (input={self.input}, args {' | '.join([arg.summary() for arg in self.args or []])})"


# 1. Custom Representer (Python object -> YAML)
def postprocessor_representer(dumper: Dumper, data: PostProcessor) -> yaml.nodes.MappingNode:
    """
    Represents the PostProcessor dataclass instance as a YAML mapping.
    """
    mapping = {
        "action": data.action,
        "input": data.input,
        "output": data.output,
    }
    if data.args:
        mapping.update({"args": data.args})

    return dumper.represent_mapping("!PostProcessor", mapping)


# 2. Custom Constructor (YAML -> Python object)
def postprocessor_constructor(loader: FullLoader, node: yaml.nodes.MappingNode) -> PostProcessor:
    """
    Constructs a PostProcessor dataclass instance from a YAML mapping.
    """
    mapping = loader.construct_mapping(node, deep=True)
    return PostProcessor(**mapping)
