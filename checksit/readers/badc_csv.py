#https://github.com/cedadev/badc-csv/blob/main/badctextfile.py
from .badctextfile import BADCTextFile
from .base import BaseReader
from typing import Dict

class BADCCSVHeader(BaseReader):
    def __init__(
        self,
        inpt: str,
        verbose: bool = False,
    ) -> None:
        """Initialise the BADCCSVHeader.

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
        """Read BADC CSV file"""
        content = BADCTextFile(open(self.inpt))._metadata
        self.global_attrs = dict(content.globalRecords)
