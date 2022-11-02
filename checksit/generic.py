from .utils import UNDEFINED, is_undefined
from .cvs import vocabs
from .rules import rules

import re

def _get_bounds_var_ids(dct):
    return [var_id for var_id in dct["variables"] if (
            var_id.startswith("bounds_") or var_id.startswith("bnds_") or
            var_id.endswith("_bounds") or var_id.endswith("_bnds"))] 


def check_var_attrs(dct, defined_attrs, ignore_bounds=True):
    """
    Check that variable attributes are defined.

    E.g.: check-var-attrs:defined_attrs:long_name|units
    """
    errors = []
    bounds_vars = _get_bounds_var_ids(dct)

    for var_id, var_dict in dct["variables"].items():
        if var_id in bounds_vars: continue 

        for attr in defined_attrs:
            if is_undefined(var_dict.get(attr)):
                errors.append(f"[variable**************:{var_id}]: Attribute '{attr}' must have a valid definition.")

    return errors
 

def check_global_attrs(dct, defined_attrs=None, vocab_attrs=None, regex_attrs=None, rules_attrs=None):
    """
    Check that required global attributes are correct.

    E.g.: check-global-attrs:defined_attrs:source
          check-global-attrs:vocab_attrs:Conventions
    """
    defined_attrs = defined_attrs or []
    vocab_attrs = vocab_attrs or {}
    regex_attrs = regex_attrs or {}
    rules_attrs = rules_attrs or {}

    errors = []

    for attr in defined_attrs:
        if is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: Attribute '{attr}' must have a valid definition.")

    for attr in vocab_attrs:
        errors.extend(vocabs.check(vocab_attrs[attr], dct['global_attributes'].get(attr, UNDEFINED), label=f"[global-attributes:******:{attr}]***"))
    
    for attr in regex_attrs:
        if is_undefined(dct['global_attributes'].get(attr)) or not re.match(regex_attrs[attr], dct['global_attributes'].get(attr, UNDEFINED)):
            errors.append(f"[global-attributes:******:{attr}]: '{dct['global_attributes'].get(attr, UNDEFINED)}' does not match regex pattern '{regex_attrs[attr]}'.") 

    for attr in rules_attrs:
        errors.extend(rules.check(rules_attrs[attr], dct['global_attributes'].get(attr, UNDEFINED), label=f"[global-attributes:******:{attr}]***"))


    return errors


def check_var_exists(dct, variables):
    """
    Check that variables exist

    E.g. check-var-exists:variables:time|altitude
    """
    errors = []

    for var in variables:
        if var not in dct["variables"].keys():
            errors.append(f"[variable**************:{var}]: Does not exist in file.")

    return errors


def check_dim_exists(dct, dimensions):
    """
    Check that variables exist

    E.g. check-dim-exists:dimensions:time|latitude
    """
    errors = []

    for dim in dimensions:
        if dim not in dct["dimensions"].keys():
            errors.append(f"[dimension**************:{dim}]: Does not exist in file.")

    return errors 

def check_var(dct, variables, defined_attrs):
    """
    Check variables exist and have attributes defined.
    """
    errors = []
    for var in variables:
        if var not in dct["variables"].keys():
            errors.append(f"[variable**************:{var}]: Does not exist in file.")
        else:
            for attr in defined_attrs:
                if is_undefined(dct["variables"][var].get(attr)):
                    errors.append(f"[variable**************:{var}]: Attribute '{attr}' must have a valid definition.")            

    return errors
