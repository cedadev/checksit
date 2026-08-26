#https://github.com/cedadev/badc-csv/blob/main/badctextfile.py
from .badctextfile import BADCTextFile
from .base import BaseReader
from typing import List, Dict
"""
req_dicts = "dimensions", "variables", "global_attributes"


class BADCCSVHeader:
    def __init__(self, fpath, content):
        self.inpt = fpath
        self._content = content
        for key in req_dicts:
            if key not in self._content:
                self._content[key] = {}

    def to_dict(self):
        return self._content


def read(fpath: str, verbose: bool = False) -> BADCCSVHeader:
    bm = BADCTextFile(open(fpath))._metadata
    d = {"global_attributes": dict(bm.globalRecords)}
         # "variables": bm.varRecords}
    return BADCCSVHeader(fpath, d)
"""
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
        self.fmt_errors: List[str] = []
        self.global_attrs: Dict[str, str] = {}
        self.dimensions: Dict[str, str] = {}
        self.variables: Dict[str, Dict[str, str]] = {}

    def read(self) -> None:
        """Read BADC CSV file"""
        content = BADCTextFile(open(self.inpt))._metadata
        self.global_attrs = dict(content.globalRecords)
