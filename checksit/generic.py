from .utils import UNDEFINED, is_undefined
from .cvs import vocabs
from .rules import rules

import re
import numpy as np
import datetime as dt

def _get_bounds_var_ids(dct):
    return [var_id for var_id in dct["variables"] if (
            var_id.startswith("bounds_") or var_id.startswith("bnds_") or
            var_id.endswith("_bounds") or var_id.endswith("_bnds"))] 


def one_spelling_mistake(word):
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
    return set(deletes + transposes + replaces + inserts)

def two_spelling_mistakes(word): 
    """
    All edits that are two edits away from `word`.
    From https://norvig.com/spell-correct.html
    """
    return set([ e2 for e1 in one_spelling_mistake(word) for e2 in one_spelling_mistake(e1) ])

def search_close_match(search_for, search_in):
    possible_close_edits = two_spelling_mistakes(search_for.lower())
    for s in search_in:
        if s.lower() in possible_close_edits:
            return f"'{s}' was found in this file, should this be '{search_for}'?"
    return ""


def check_var_attrs(dct, defined_attrs, ignore_bounds=True, skip_spellcheck=False):
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
 

def check_global_attrs(dct, defined_attrs=None, vocab_attrs=None, regex_attrs=None, rules_attrs=None, skip_spellcheck=False):
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
            errors.append(
                f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. "
                f"{search_close_match(attr, dct['global_attributes'].keys()) if not skip_spellcheck else ''}"
            )
        elif is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'.")

    for attr in vocab_attrs:
        if attr not in dct['global_attributes']:
            errors.append(
                f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. "
                f"{search_close_match(attr, dct['global_attributes'].keys()) if not skip_spellcheck else ''}"
            )
        elif is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'.")
        else:
            errors.extend(vocabs.check(vocab_attrs[attr], dct["global_attributes"].get(attr), label=f"[global-attributes:******:{attr}]***"))
    
    for attr in regex_attrs:
        if attr not in dct['global_attributes']:
            errors.append(
                f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. "
                f"{search_close_match(attr, dct['global_attributes'].keys()) if not skip_spellcheck else ''}"
            )
        elif is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'.")
        elif not re.match(regex_attrs[attr], dct['global_attributes'].get(attr)):
            errors.append(
                f"[global-attributes:******:{attr}]: '{dct['global_attributes'].get(attr, UNDEFINED)}' "
                f"does not match regex pattern '{regex_attrs[attr]}'."
            ) 

    for attr in rules_attrs:
        if attr not in dct['global_attributes']:
            errors.append(
                f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. "
                f"{search_close_match(attr, dct['global_attributes'].keys()) if not skip_spellcheck else ''}"
            )
        elif is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'.")
        else:
            errors.extend(rules.check(rules_attrs[attr], dct['global_attributes'].get(attr), label=f"[global-attributes:******:{attr}]***"))


    return errors, warnings


def check_var_exists(dct, variables, skip_spellcheck=False):
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
                warnings.append(
                    f"[variable**************:{var}]: Optional variable does not exist in file. "
                    f"{search_close_match(var, dct['variables'].keys()) if not skip_spellcheck else ''}"
                )
        else:
            if var not in dct["variables"].keys():
                errors.append(
                    f"[variable**************:{var}]: Does not exist in file. "
                    f"{search_close_match(var, dct['variables'].keys()) if not skip_spellcheck else ''}"
                )

    return errors, warnings


def check_dim_exists(dct, dimensions, skip_spellcheck=False):
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
                warnings.append(
                    f"[dimension**************:{dim}]: Optional dimension does not exist in file. "
                    f"{search_close_match(dim, dct['dimensions'].keys()) if not skip_spellcheck else ''}"
                )
        else:
            if dim not in dct["dimensions"].keys():
                errors.append(
                    f"[dimension**************:{dim}]: Does not exist in file. "
                    f"{search_close_match(dim, dct['dimensions'].keys()) if not skip_spellcheck else ''}"
                )

    return errors, warnings 


def check_var(dct, variable, defined_attrs, skip_spellcheck=False):
    """
    Check variable exists and has attributes defined.
    """
    errors = []
    warnings = []

    if isinstance(variable, list):
        variable = variable[0]
    if ':__OPTIONAL__' in variable:
        variable = variable.split(':')[0]
        if variable not in dct["variables"].keys():
            warnings.append(
                f"[variable**************:{variable}]: Optional variable does not exist in file. "
                f"{search_close_match(variable, dct['variables'].keys()) if not skip_spellcheck else ''}"
            )
        else:
            for attr in defined_attrs:
                if isinstance(attr, dict) and len(attr.keys()) == 1:
                    for key,value in attr.items():
                        attr = f'{key}: {value}'
                attr_key = attr.split(':')[0]
                attr_value = ':'.join(attr.split(':')[1:])
                if attr_key not in dct["variables"][variable]:
                    errors.append(
                        f"[variable**************:{variable}]: Attribute '{attr_key}' does not exist. "
                        f"{search_close_match(attr_key, dct['variables'][variable]) if not skip_spellcheck else ''}"
                    )
                elif '<derived from file>' in attr_value:
                    # work this out
                    pass
                elif attr_key == 'flag_values':
                    attr_value = attr_value.strip(',')
                    attr_value = [ int(i.strip('b')) for i in attr_value.split(',') ]
                    attr_value = np.array(attr_value, dtype=np.int8)
                    if not np.all(dct["variables"][variable].get(attr_key) == attr_value):
                        errors.append(
                            f"[variable**************:{variable}]: Attribute '{attr_key}' must have definition {attr_value}, "
                            f"not {dct['variables'][variable].get(attr_key) if skip_spellcheck else ''}."
                        )
                #elif attr_key == 'flag_meanings':
                #    print(attr_value)
                #    print(dct["variables"][variable].get(attr_key))
                elif not str(dct["variables"][variable].get(attr_key)) == attr_value:
                    errors.append(
                        f"[variable**************:{variable}]: Attribute '{attr_key}' must have definition {attr_value}, "
                        f"not {dct['variables'][variable].get(attr_key).encode('unicode_escape').decode('utf-8')}."
                    )
    else:
        if variable not in dct["variables"].keys():
            errors.append(
                f"[variable**************:{variable}]: Optional variable does not exist in file. "
                f"{search_close_match(variable, dct['variables'].keys()) if not skip_spellcheck else ''}"
            )
        else:
            for attr in defined_attrs:
                attr_key = attr.split(':')[0]
                attr_value = ':'.join(attr.split(':')[1:]) 
                if attr_key not in dct["variables"][variable]:
                    errors.append(
                        f"[variable**************:{variable}]: Attribute '{attr_key}' does not exist. "
                        f"{search_close_match(attr_key, dct['variables'][variable]) if not skip_spellcheck else ''}"
                    )
                elif '<' in attr_value:
                    # work this out
                    pass
                elif not dct["variables"][variable].get(attr_key) == attr_value:
                    errors.append(
                        f"[variable**************:{variable}]: Attribute '{attr_key}' must have definition {attr_value}, "
                        f"not {dct['variables'][variable].get(attr_key)}."
                    )

    return errors, warnings


def check_file_name(file_name, vocab_checks=None, **kwargs):
    """
    Checks format of file name

    Works for NCAS-GENERAL, would work for NCAS-RADAR if radar scan type is added as data product
    """
    vocab_checks = vocab_checks or {}
    errors = []
    warnings = []
    file_name_parts = file_name.split("_")

    # check instrument name
    if "instrument" in vocab_checks.keys():
        if vocabs.check(vocab_checks["instrument"], file_name_parts[0], label="_") != []:
            errors.append(f"[file name]: Invalid file name format - unknown instrument {file_name_parts[0]}")
    else:
        msg = "No instrument vocab defined in specs"
        raise KeyError(msg)

    # check platform
    if "platform" in vocab_checks.keys():
        if vocabs.check(vocab_checks["platform"], file_name_parts[1], label="_") != []:
            errors.append(f"[file name]: Invalid file name format - unknown platform {file_name_parts[1]}")
    else:
        msg = "No platform vocab defined in specs"
        raise KeyError(msg)
    
    # check date format
    # could be yyyy, yyyymm, yyyymmdd, yyyymmdd-HH, yyyymmdd-HHMM, yyyymmdd-HHMMSS
    # first checks format, then date validity 
    if not re.match("^\d{4}$|^\d{6}$|^\d{8}$|^\d{8}-\d{2}$|^\d{8}-\d{4}$|^\d{8}-\d{6}$", file_name_parts[2]):
        errors.append(f"[file name]: Invalid file name format - bad date format {file_name_parts[2]}")
    else:
        fmts = ("%Y", "%Y%m", "%Y%m%d", "%Y%m%d-%H", "%Y%m%d-%H%M", "%Y%m%d-%H%M%S")
        valid_date_found = False
        for f in fmts:
            try:
                t = dt.datetime.strptime(file_name_parts[2], f)
                valid_date_found = True
                break
            except ValueError:
                pass 
        if not valid_date_found:
            errors.append(f"[file name]: Invalid file name format - invalid date in file name {file_name_parts[2]}")

    # check data product
    if "data_product" in vocab_checks.keys():
        if vocabs.check(vocab_checks["data_product"], file_name_parts[3], label="_") != []:
            errors.append(f"[file name]: Invalid file name format - unknown data product {file_name_parts[3]}")
    else:
        msg = "No data product vocab defined in specs"
        raise KeyError(msg)

    # check version number format
    if not re.match("^v\d.\d$", file_name_parts[-1].split(".nc")[0]):
        errors.append(f"[file name]: Invalid file name format - incorrect file version number {file_name_parts[-1].split('.nc')[0]}")

    # check number of options - max length of splitted file name
    if len(file_name_parts) > 8:
        errors.append(f"[file name]: Invalid file name format - too many options in file name")

    return errors, warnings
