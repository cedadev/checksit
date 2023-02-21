from .utils import UNDEFINED, is_undefined
from .cvs import vocabs
from .rules import rules

import re

def _get_bounds_var_ids(dct):
    return [var_id for var_id in dct["variables"] if (
            var_id.startswith("bounds_") or var_id.startswith("bnds_") or
            var_id.endswith("_bounds") or var_id.endswith("_bnds"))] 


def edits1(word):
    """
    All edits that are one edit away from `word`.
    Adapted from https://norvig.com/spell-correct.html
    """
    letters    = 'abcdefghijklmnopqrstuvwxyz0123456789._-'
    splits     = [(word[:i], word[i:])    for i in range(1,len(word) + 1)]  # 1 in range requires first letter to be correct
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    #return [i for i in set(deletes + transposes + replaces + inserts) if i[-1] == word[-1]]  # require last letter to be correct
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    """
    All edits that are two edits away from `word`.
    From https://norvig.com/spell-correct.html
    """
    return [ e2 for e1 in edits1(word) for e2 in edits1(e1) ]

def search_close_match(search_for, search_in):
    possible_close_edits = edits2(search_for.lower())
    for s in search_in:
        if s.lower() in possible_close_edits:
            return f"'{s}' was found in this file, should this be '{search_for}'?"
    return ""


def check_var_attrs(dct, defined_attrs, ignore_bounds=True):
    """
    Check that variable attributes are defined.

    E.g.: check-var-attrs:defined_attrs:long_name|units
    """
    errors = []
    warnings = []

    bounds_vars = _get_bounds_var_ids(dct)

    for var_id, var_dict in dct["variables"].items():
        if var_id in bounds_vars: continue 

        for attr in defined_attrs:
            if is_undefined(var_dict.get(attr)):
                errors.append(f"[variable**************:{var_id}]: Attribute '{attr}' must have a valid definition.")

    return errors, warnings
 

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
    warnings = []

    for attr in defined_attrs:
        if attr not in dct['global_attributes']:
            errors.append(f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. {search_close_match(attr, dct['global_attributes'].keys())}")
        elif is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'.")

    for attr in vocab_attrs:
        if attr not in dct['global_attributes']:
            errors.append(f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. {search_close_match(attr, dct['global_attributes'].keys())}")
        elif is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'.")
        else:
            errors.extend(vocabs.check(vocab_attrs[attr], dct["global_attributes"].get(attr), label=f"[global-attributes:******:{attr}]***"))
    
    for attr in regex_attrs:
        if attr not in dct['global_attributes']:
            errors.append(f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. {search_close_match(attr, dct['global_attributes'].keys())}")
        elif is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'.")
        elif not re.match(regex_attrs[attr], dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:******:{attr}]: '{dct['global_attributes'].get(attr, UNDEFINED)}' does not match regex pattern '{regex_attrs[attr]}'.") 

    for attr in rules_attrs:
        #errors.extend(rules.check(rules_attrs[attr], dct['global_attributes'].get(attr, UNDEFINED), label=f"[global-attributes:******:{attr}]***"))
        if attr not in dct['global_attributes']:
            errors.append(f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. {search_close_match(attr, dct['global_attributes'].keys())}")
        elif is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'.")
        else:
            errors.extend(rules.check(rules_attrs[attr], dct['global_attributes'].get(attr), label=f"[global-attributes:******:{attr}]***"))


    return errors, warnings


def check_var_exists(dct, variables):
    """
    Check that variables exist

    E.g. check-var-exists:variables:time|altitude
    """
    errors = []
    warnings = []

    for var in variables:
        if ':__OPTIONAL__' in var:
            var = var.split(':')[0]
            if var not in dct["variables"].keys():
                warnings.append(f"[variable**************:{var}]: Optional variable does not exist in file. {search_close_match(var, dct['variables'].keys())}")
        else:
            if var not in dct["variables"].keys():
                errors.append(f"[variable**************:{var}]: Does not exist in file. {search_close_match(var, dct['variables'].keys())}")

    return errors, warnings


def check_dim_exists(dct, dimensions):
    """
    Check that variables exist

    E.g. check-dim-exists:dimensions:time|latitude
    """
    errors = []
    warnings = []

    for dim in dimensions:
        if ':__OPTIONAL__' in dim:
            dim = dim.split(':')[0]
            if dim not in dct["dimensions"].keys():
                warnings.append(f"[dimension**************:{dim}]: Optional dimension does not exist in file. {search_close_match(dim, dct['dimensions'].keys())}")
        else:
            if dim not in dct["dimensions"].keys():
                errors.append(f"[dimension**************:{dim}]: Does not exist in file. {search_close_match(dim, dct['dimensions'].keys())}")

    return errors, warnings 


def check_var(dct, variables, defined_attrs):
    """
    Check variables exist and have attributes defined.
    """
    errors = []
    warnings = []

    for var in variables:
        if ':__OPTIONAL__' in var:
            var = var.split(':')[0]
            if var not in dct["variables"].keys():
                warnings.append(f"[variable**************:{var}]: Optional variable does not exist in file. {search_close_match(var, dct['variables'].keys())}")
            else:
                for attr in defined_attrs:
                    if attr not in dct["variables"][var]:
                        errors.append(f"[variable**************:{var}]: Attribute '{attr}' does not exist. {search_close_match(attr, dct['variables'][var])}")
                    elif is_undefined(dct["variables"][var].get(attr)):
                        errors.append(f"[variable**************:{var}]: Attribute '{attr}' must have a valid definition.")
        else:
            if var not in dct["variables"].keys():
                errors.append(f"[variable**************:{var}]: Does not exist in file. {search_close_match(var, dct['variables'].keys())}")
            else:
                for attr in defined_attrs:
                    if attr not in dct["variables"][var]:
                        errors.append(f"[variable**************:{var}]: Attribute '{attr}' does not exist. {search_close_match(attr, dct['variables'][var])}")
                    elif is_undefined(dct["variables"][var].get(attr)):
                        errors.append(f"[variable**************:{var}]: Attribute '{attr}' must have a valid definition.")            

    return errors, warnings
