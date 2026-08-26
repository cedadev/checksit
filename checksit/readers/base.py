from abc import ABC, abstractmethod
from typing import List, Dict, Union

class BaseReader(ABC):
    inpt: str
    verbose: bool
    fmt_errors: List[str]
    global_attrs: Dict[str, str]
    dimensions: Dict[str, str]
    variables: Dict[str, Dict[str, str]]

    @abstractmethod
    def read(self) -> None:
        """Read file"""
        pass

    def to_dict(self) -> Dict[str, Union[Dict[str, str], Dict[str, Dict[str, str]], str]]:
        """Convert parsed data into dict

        Returns:
            dictionary mess
        """
        return {
            "dimensions": self.dimensions,
            "variables": self.variables,
            "global_attributes": self.global_attrs,
            "inpt": self.inpt,
        }
