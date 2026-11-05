import yaml
from typing import List, Dict
from .base import BaseReader

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


