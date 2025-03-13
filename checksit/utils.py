"""Generic utility functions
"""

import os
import inspect
from typing import List, Dict, Callable, Any

UNDEFINED = "UNDEFINED"


def string_to_dict(s: str) -> Dict[str, str]:
    """Convert string value into dictionary.

    Takes a string value, splits string by comma into key-value pairs, splits the
    key-value pairs by "=", and creates a dictionary for those keys and values.

    Args:
        s: string to convert

    Returns:
        Dictionary from string value.
    """
    return dict([x.split("=") for x in s.split(",")])


def string_to_list(s: str) -> List[str]:
    """Convert string value into a list.

    Takes a string value, splits by comma, and returns the resulting list.

    Args:
        s: string to split

    Returns:
        List from string value.
    """
    return s.split(",")


def extension(file_path: str) -> str:
    """Return file extension of string file name.

    Returns the characters after the final "." in a string, which in a file name is
    typically the extension denoting the file type.

    Args:
        file_path: string of which to get the file extension

    Returns:
        File extension as string.
    """
    return file_path.split(".")[-1]


def get_file_base(file_path: str) -> str:
    """Return file name up to the final underscore.

    Splits the file name by underscores, and returns the string up to the final
    underscore. For use with file names in the template cache.

    Args:
        file_path: string of which to get the file base

    Returns:
        File base as string.
    """
    parts = os.path.basename(file_path).split("_")[:-1]
    return "_".join(parts)


def map_to_rule(func: Callable[...]) -> str:
    """Convert function name to spec file rule name.

    Convert the function name into the rule name used in the spec files by replacing
    underscores with hyphens. Underscores cannot be used in the spec files, so hyphens
    are used instead. This function is used with the `describe` functionality in
    printing out rules and their docstrings to terminal.

    Args:
        func: function to convert to rule name

    Returns:
        Rule name as string, with underscores replaced by hyphens.
    """
    return func.__name__.replace("_", "-")


def get_public_funcs(module: object) -> List[Callable[...]]:
    """Get all public functions from a module.

    Get all public functions from a given module. Public functions are those that do
    not begin with an underscore.

    Args:
        module: module from which to get public functions

    Returns:
        List of public functions from the module.
    """
    items = [item for item in dir(module) if item not in ["get_config"]]
    funcs = []

    for item in items:
        if item[0] != "_":
            prop = getattr(module, item)
            if inspect.isfunction(prop):
                funcs.append(prop)

    return funcs


def is_undefined(x: Any) -> bool:
    """Check if value is undefined.

    Args:
        x: value to check

    Returns:
        True if value is undefined, False otherwise.
    """
    return not x and x != 0
