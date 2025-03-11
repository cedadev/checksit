"""Describe checksit rule functions.

Module that provides function that prints out rule functions and their descriptions in
a human readable format.
"""

from .utils import get_public_funcs, map_to_rule
from .rules import rule_funcs
from typing import List, Optional

def describe(check_ids: Optional[List[str]] = None, verbose: bool = False) -> None:
    """Print out rule functions and description.

    Prints out name and description for given rule function or functions in a human
    readable format. Endpoint for the `checksit describe` CLI command. If no functions
    are specified, descriptions for all rule functions are printed.

    Args:
        check_ids: name of function, or names of functions, to describe.
    """
    all_funcs = get_public_funcs(rule_funcs)

    if not check_ids:
        check_funcs = [(map_to_rule(func), func) for func in all_funcs]
    else:
        check_funcs = []
        func_dict = dict([(map_to_rule(func), func) for func in all_funcs])

        for check_id in check_ids:
            if check_id in func_dict:
                check_funcs.append((check_id, func_dict[check_id]))

    print("Functional check descriptions:")
    for check_id, check_func in check_funcs:

        print(f"\n{check_id}:\n\tFunction: {check_func.__name__}\n\tDescription:")
        print("\n\t".join([line for line in check_func.__doc__.split("\n")]))
