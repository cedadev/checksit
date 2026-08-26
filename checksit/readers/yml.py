import yaml
from typing import List, Dict
from .base import BaseReader
"""
req_dicts = "dimensions", "variables", "global_attributes"

class YAMLFile:
    def __init__(self, fpath, content):
        self.inpt = fpath
        self._content = content
        for key in req_dicts:
            if key not in self._content:
                self._content[key] = {}

    def to_dict(self):
        return self._content


def read(fpath: str, verbose: bool = False) -> YAMLFile:
    d = yaml.load(open(fpath), Loader=yaml.SafeLoader)
    return YAMLFile(fpath, d)
"""

class YAMLFile(BaseReader):
    def __init__(
        self,
        inpt: str,
        verbose: bool = False,
    ) -> None:
        """Initialise the YAMLParser.

        Args:
            inpt: The input file path.
            verbose: Print verbose output during parsing
        """
        self.inpt = inpt
        self.verbose = verbose
        self.fmt_errors: List[str] = []
        self.global_attrs: Dict[str, str] = {}
        self.dimensions: Dict[str, str] = {}
        self.variables: Dict[str, Dict[str, str]] = {}

    def read(self) -> None:
        """Read YAML file"""
        content = yaml.load(open(self.inpt), Loader=yaml.SafeLoader)
        if "global_attributes" in content:
            self.global_attrs = content["global_attributes"]
        if "dimensions" in content:
            self.dimensions = content["dimensions"]
        if "variables" in content:
            self.variables = content["variables"]


