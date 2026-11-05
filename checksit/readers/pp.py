import cf
from .base import BaseReader
from typing import Dict

class PPHeader(BaseReader):
    def __init__(
        self,
        inpt: str,
        verbose: bool = False,
    ) -> None:
        """Initialise the PPHeader.

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
        fieldlist = cf.read(self.inpt)
        content = {"variables": {}}

        for field in fieldlist:
            sn = field.standard_name
            sh = list(field.shape)

            content["variables"][sn] = {"shape": sh}

        if "global_attributes" in content:
            self.global_attrs = content["global_attributes"]
        if "dimensions" in content:
            self.dimensions = content["dimensions"]
        if "variables" in content:
            self.variables = content["variables"]

