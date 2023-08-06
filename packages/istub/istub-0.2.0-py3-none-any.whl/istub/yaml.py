"""
YAML utils.
"""
from typing import Any

import yaml
from yaml.dumper import SafeDumper
from yaml.loader import SafeLoader
from yaml.nodes import Node, ScalarNode


class MyDumper(SafeDumper):
    """
    Custom YAML dumper that replaces system paths to avoid snapshot mismatch.
    """

    def represent_data(self, data: Any) -> Node:
        """
        Proxy for represent_data to handle strings properly.
        """
        if isinstance(data, str):
            return self.represent_str(data)
        return super().represent_data(data)

    def represent_str(self, data: str) -> ScalarNode:
        """
        Represent strings as multiline strings.
        """
        if "\n" in data:
            return self.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return super().represent_str(data)

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        """
        Add indent for flow collections.
        """
        indentless = False
        super().increase_indent(flow, indentless)


def dumps(data: Any) -> str:
    """
    Dump data to YAML string.
    """
    return yaml.dump(
        data,
        Dumper=MyDumper,
        indent=2,
        sort_keys=False,
        default_flow_style=False,
    )


def loads(data: str) -> Any:
    """
    Load data from YAML string.
    """
    return yaml.load(data, Loader=SafeLoader)
