from dataclasses import dataclass
from typing import Any

import yaml
from yaml.dumper import Dumper
from yaml.loader import FullLoader


@dataclass
class Argument:
    """Represents an argument for the PostProcessor action"""

    key: str
    value: Any

    def summary(self) -> str:
        return f"{self.key}={self.value}"


# 1. Custom Representer (Python object -> YAML)
def argument_representer(dumper: Dumper, data: Argument) -> yaml.nodes.MappingNode:
    """
    Represents the Argument dataclass instance as a YAML mapping.
    """
    return dumper.represent_mapping(
        "!Argument",
        {
            "key": data.key,
            "value": data.value,
        },
    )


# 2. Custom Constructor (YAML -> Python object)
def argument_constructor(loader: FullLoader, node: yaml.nodes.MappingNode) -> Argument:
    """
    Constructs a Argument dataclass instance from a YAML mapping.
    """
    mapping = loader.construct_mapping(node, deep=True)
    return Argument(**mapping)
