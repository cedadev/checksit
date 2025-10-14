"""Generic functions to be called by specs.

Functions intended to be the entry point for spec checks, and can do direct checks
(e.g. is a equal to b) or call to vocab and rule checks. All functions called by the
specs MUST return two lists, errors and warnings, even if one will always be empty, and
MUST take `skip_spellcheck` as a parameter, even if not used.
"""

from .utils import UNDEFINED, is_undefined
from .cvs import vocabs
from .rules import rules

import re
import numpy as np
import datetime as dt
from typing import List, Dict, Any, Set, Tuple, Optional, Union, Iterable

# date formate regex
# could be YYYY, YYYYmm, YYYYmmdd, YYYYmmdd-HH, YYYYmmdd-HHMM, YYYYmmdd-HHMMSS
DATE_REGEX = re.compile(
    r"^\d{4}$|^\d{6}$|^\d{8}$|^\d{8}-\d{2}$|^\d{8}-\d{4}$|^\d{8}-\d{6}$"
)
# YYYY, YYYYmm, YYYYmmdd, YYYYmmddHH, YYYYmmddHHMM, YYYYmmddHHMMSS
DATE_REGEX_GENERIC = re.compile(
    r"^\d{4}$|^\d{6}$|^\d{8}$|^\d{10}$|^\d{12}$|^\d{14}$"
)

def _get_bounds_var_ids(dct: Dict[str, Dict[str, Any]]) -> List[str]:
    """Find all boundary variables.

    Finds all variables that are boundary variables, based on variable name starting or
    ending with "bounds" or "bnds".

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "variables" as a key.

    Returns:
        List of boundary variable names.
    """
    return [
        var_id
        for var_id in dct["variables"]
        if (
            var_id.startswith("bounds_")
            or var_id.startswith("bnds_")
            or var_id.endswith("_bounds")
            or var_id.endswith("_bnds")
        )
    ]


def one_spelling_mistake(word: str) -> Set[str]:
    """All edits that are one edit away from `word`.

    Part of spell checking, finds all possible strings that have one error in them, for
    example one character missing, one extra character, two characters switched
    positions, or one character replaced with another. Letters are considered to be
    lower case a-z, digits 0-9, and the characters `.`, `_`, and `-`.
    Adapted from https://norvig.com/spell-correct.html

    Args:
        word: string to find all single edits from.

    Returns:
        Set of all possible single edits from `word`.
    """
    letters = "abcdefghijklmnopqrstuvwxyz0123456789._-"
    splits = [
        (word[:i], word[i:]) for i in range(1, len(word) + 1)
    ]  # 1 in range requires first letter to be correct
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def two_spelling_mistakes(word: str) -> Set[str]:
    """All edits that are two edits away from `word`.

    Part of spell checking, finds all possible strings that have two errors in them,
    taking the results from `one_spelling_mistake(word)` and checking for one spelling
    mistake in all those values.
    From https://norvig.com/spell-correct.html

    Args:
        word: string to find all double edits from.

    Returns:
        Set of all possible double edits from `word`.
    """
    return set(
        [e2 for e1 in one_spelling_mistake(word) for e2 in one_spelling_mistake(e1)]
    )


def search_close_match(search_for: str, search_in: Iterable[str]) -> str:
    """Find potential misspelt strings.

    Search within `search_in` to identify a string that is close to `search_for` as a
    potential misspelling.

    Args:
        search_for: correctly spelt string to search against.
        search_in: list of strings to search within for potentially misspelt string.

    Returns:
        String with message if potential misspelling found, otherwise empty string.
    """
    possible_close_edits = two_spelling_mistakes(search_for.lower())
    for s in search_in:
        if s.lower() in possible_close_edits:
            return f"'{s}' was found in this file, should this be '{search_for}'?"
    return ""


def check_var_attrs(
    dct: Dict[str, Dict[str, Any]],
    defined_attrs: List[str],
    ignore_bounds: bool = True,
    skip_spellcheck: bool = False,
) -> Tuple[List[str], List[str]]:
    """Check that variable attributes are defined.

    Checks that all given attributes are defined for all variables in file.

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "variables" as a key.
        defined_attrs: list of attributes to check exist in each variable in `dct`.
        ignore_bounds: ignore checking attributes in boundary variables. Default True.
        skip_spellcheck: skip looking for close misspelling of attribute if not found
          in variable. Default False.

    Returns:
        A list of errors and a list of warnings
    """
    errors = []
    warnings = []

    bounds_vars = _get_bounds_var_ids(dct)

    for var_id, var_dict in dct["variables"].items():
        if var_id in bounds_vars:
            continue

        for attr in defined_attrs:
            if is_undefined(var_dict.get(attr)):
                errors.append(
                    f"[variable**************:{var_id}]: Attribute '{attr}' must have a valid definition."
                )

    return errors, warnings


def check_global_attrs(
    dct: Dict[str, Dict[str, Any]],
    defined_attrs: Optional[List[str]] = None,
    vocab_attrs: Optional[Dict[str, str]] = None,
    regex_attrs: Optional[Dict[str, str]] = None,
    rules_attrs: Optional[Dict[str, str]] = None,
    skip_spellcheck: bool = False,
) -> Tuple[List[str], List[str]]:
    """Run checks against global attributes.

    Run series of checks against global attributes in file. Can check for any or all of:
      - defined_attrs (i.e. does the attribute exist),
      - vocab_attrs (i.e. does the value of the attribute match value defined in
        controlled vocabulary),
      - regex_attrs (i.e. does the value of the attribute match a regex expression),
      - rules_attrs (i.e. does the attribute value pass a defined rule).

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "global_attributes" as a key.
        defined_attrs: list of attributes to check exist and are defined.
        vocab_attrs: dictionary with attribute to check as keys and vocab rule to check
          against as value.
        regex_attrs: dictionary with attribute to check as keys and regex rule to check
          against as value.
        rules_attrs: dictionary with attribute to check as keys and rule to check
          against, and any options needed, as string value (e.g.
          "rule-func:string-of-length:3+"). See documentation on the `check` function
          in the `Rules` class for more information on formatting.
        skip_spellcheck: skip looking for close misspelling of attribute if not found
          in variable. Default False.

    Returns:
        A list of errors and a list of warnings
    """
    defined_attrs = defined_attrs or []
    vocab_attrs = vocab_attrs or {}
    regex_attrs = regex_attrs or {}
    rules_attrs = rules_attrs or {}

    errors = []
    warnings = []

    for attr in defined_attrs:
        if attr not in dct["global_attributes"]:
            errors.append(
                f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. "
                f"{search_close_match(attr, dct['global_attributes'].keys()) if not skip_spellcheck else ''}"
            )
        elif is_undefined(dct["global_attributes"].get(attr)):
            errors.append(
                f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'."
            )

    for attr in vocab_attrs:
        if attr not in dct["global_attributes"]:
            errors.append(
                f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. "
                f"{search_close_match(attr, dct['global_attributes'].keys()) if not skip_spellcheck else ''}"
            )
        elif is_undefined(dct["global_attributes"].get(attr)):
            errors.append(
                f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'."
            )
        else:
            errors.extend(
                vocabs.check(
                    vocab_attrs[attr],
                    dct["global_attributes"].get(attr),
                    label=f"[global-attributes:******:{attr}]***",
                )
            )

    for attr in regex_attrs:
        if attr not in dct["global_attributes"]:
            errors.append(
                f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. "
                f"{search_close_match(attr, dct['global_attributes'].keys()) if not skip_spellcheck else ''}"
            )
        elif is_undefined(dct["global_attributes"].get(attr)):
            errors.append(
                f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'."
            )
        elif not re.match(regex_attrs[attr], dct["global_attributes"].get(attr)):
            errors.append(
                f"[global-attributes:******:{attr}]: '{dct['global_attributes'].get(attr, UNDEFINED)}' "
                f"does not match regex pattern '{regex_attrs[attr]}'."
            )

    for attr in rules_attrs:
        if attr not in dct["global_attributes"]:
            errors.append(
                f"[global-attributes:**************:{attr}]: Attribute '{attr}' does not exist. "
                f"{search_close_match(attr, dct['global_attributes'].keys()) if not skip_spellcheck else ''}"
            )
        elif is_undefined(dct["global_attributes"].get(attr)):
            errors.append(
                f"[global-attributes:**************:{attr}]: No value defined for attribute '{attr}'."
            )
        else:
            rules_check_output = rules.check(
                rules_attrs[attr],
                dct["global_attributes"].get(attr),
                context=dct["inpt"],
                label=f"[global-attributes:******:{attr}]***",
            )
            warnings.extend(rules_check_output[1])
            errors.extend(rules_check_output[0])

    return errors, warnings


def check_var_exists(
    dct: Dict[str, Dict[str, Any]],
    variables: List[str],
    skip_spellcheck: bool = False,
) -> Tuple[List[str], List[str]]:
    """Check that variables exist in file.

    Checks a list of variables to see if they exist in given file. Optional variables
    can be defined by having ":__OPTIONAL__" after the variable name. Missing optional
    variables will be returned as warnings, and other missing variables will be
    returned as errors.

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "variables" as a key.
        variables: list of variable names to check exist
        skip_spellcheck: skip looking for close misspelling of attribute if not found
          in variable. Default False.

    Returns:
        A list of errors and a list of warnings
    """
    errors = []
    warnings = []

    for var in variables:
        if ":__OPTIONAL__" in var:
            var = var.split(":")[0]
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


def check_dim_exists(
    dct: Dict[str, Dict[str, Any]],
    dimensions: List[str],
    skip_spellcheck: bool = False,
) -> Tuple[List[str], List[str]]:
    """Check that dimensions exist in file.

    Checks a list of dimensions to see if they exist in given file. Optional dimensions
    can be defined by having ":__OPTIONAL__" after the dimension name. Missing optional
    dimensions will be returned as warnings, and other missing dimensions will be
    returned as errors.

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "dimension" as a key.
        dimensions: list of dimension names to check exist
        skip_spellcheck: skip looking for close misspelling of attribute if not found
          in variable. Default False.

    Returns:
        A list of errors and a list of warnings
    """
    errors = []
    warnings = []

    for dim in dimensions:
        if ":__OPTIONAL__" in dim:
            dim = dim.split(":")[0]
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


def check_dim_regex(
    dct: Dict[str, Dict[str, Any]],
    regex_dims: List[str],
    skip_spellcheck: bool = False,
) -> Tuple[List[str], List[str]]:
    """Check dimension exists matching regex.

    For each regex string in `regex_dims`, checks if a dimension exists matching that
    regex. Optional dimensions can be specified by appending ":__OPTIONAL__" to the end
    of the regex string.

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "dimension" as a key.
        regex_dims: list of regex strings to check dimensions for matches.

    Returns:
        A list of errors and a list of warnings
    """
    errors = []
    warnings = []
    for regex_dim in regex_dims:
        if regex_dim.endswith(":__OPTIONAL__"):
            regex_dim = ":".join(regex_dim.split(":")[:-1])
            r = re.compile(regex_dim)
            matches = list(filter(r.match, dct["dimensions"].keys()))
            if len(matches) == 0:
                warnings.append(
                    f"[dimension**************:{regex_dim}]: No dimension matching optional regex check in file. "
                )
        else:
            r = re.compile(regex_dim)
            matches = list(filter(r.match, dct["dimensions"].keys()))
            if len(matches) == 0:
                errors.append(
                    f"[dimension**************:{regex_dim}]: No dimension matching regex check in file. "
                )
    return errors, warnings


def check_var(
    dct: Dict[str, Dict[str, Any]],
    variable: Union[str, List[str]],
    defined_attrs: List[str],
    rules_attrs: Optional[Dict[str, str]] = None,
    skip_spellcheck: bool = False,
) -> Tuple[List[str], List[str]]:
    """Check variable exists and attributes defined and/or meet rules.

    For a given variable, check it exists, all `defined_attrs` exist as variable
    attributes, and all `rules_attrs` are met for variable attributes. Variable can be
    marked as an optional variable by appending ":__OPTIONAL__" to the variable name -
    if optional variable does not exist this message is returned as a warning, all
    other messages are returned as errors.

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "global_attributes" as a key.
        variable: variable to check. If list, only first variable is checked.
        defined_attrs: list of attributes to check exist and are defined.
        rules_attrs: dictionary with attribute to check as keys and rule to check
          against, and any options needed, as string value (e.g.
          "rule-func:string-of-length:3+"). See documentation on the `check` function
          in the `Rules` class for more information on formatting.
        skip_spellcheck: skip looking for close misspelling of attribute if not found
          in variable. Default False.

    Returns:
        A list of errors and a list of warnings
    """
    errors = []
    warnings = []

    rules_attrs = rules_attrs or {}

    if isinstance(variable, list):
        variable = variable[0]
    if ":__OPTIONAL__" in variable:
        variable = variable.split(":")[0]
        if variable not in dct["variables"].keys():
            warnings.append(
                f"[variable**************:{variable}]: Optional variable does not exist in file. "
                f"{search_close_match(variable, dct['variables'].keys()) if not skip_spellcheck else ''}"
            )
        else:
            for attr in defined_attrs:
                if isinstance(attr, dict) and len(attr.keys()) == 1:
                    for key, value in attr.items():
                        attr = f"{key}: {value}"
                attr_key = attr.split(":")[0]
                attr_value = ":".join(attr.split(":")[1:])
                if attr_key not in dct["variables"][variable]:
                    errors.append(
                        f"[variable**************:{variable}]: Attribute '{attr_key}' does not exist. "
                        f"{search_close_match(attr_key, dct['variables'][variable]) if not skip_spellcheck else ''}"
                    )
                elif "<derived from file>" in attr_value:
                    # work this out
                    pass
                elif attr_key == "flag_values":
                    attr_value = attr_value.strip(",")
                    attr_value = [int(i.strip("b")) for i in attr_value.split(",")]
                    attr_value = np.array(attr_value, dtype=np.int8)
                    if not (
                        (
                            len(dct["variables"][variable].get(attr_key))
                            == len(attr_value)
                        )
                        and np.all(
                            dct["variables"][variable].get(attr_key) == attr_value
                        )
                    ):
                        errors.append(
                            f"[variable**************:{variable}]: Attribute '{attr_key}' must have definition '{attr_value}', "
                            f"not '{dct['variables'][variable].get(attr_key)}'."
                        )
                elif not str(dct["variables"][variable].get(attr_key)) == attr_value:
                    errors.append(
                        f"[variable**************:{variable}]: Attribute '{attr_key}' must have definition '{attr_value}', "
                        f"not '{dct['variables'][variable].get(attr_key).encode('unicode_escape').decode('utf-8')}'."
                    )

            for attr in rules_attrs:
                if isinstance(attr, dict) and len(attr.keys()) == 1:
                    for key, value in attr.items():
                        attr = f"{key}:{value}"
                attr_key = attr.split(":")[0]
                attr_rule = ":".join(attr.split(":")[1:])
                if attr_key not in dct["variables"][variable]:
                    if not (
                        attr_key == "standard_name" and attr_rule.split(":")[1] == "allow-proposed"
                    ):
                        errors.append(
                            f"[variable:**************:{variable}]: Attribute '{attr_key}' does not exist. "
                            f"{search_close_match(attr_key, dct['variables'][variable].keys()) if not skip_spellcheck else ''}"
                        )
                    else:
                        rule_errors, rule_warnings = rules.check(
                            attr_rule,
                            dct["variables"][variable].get(attr_key),
                            context=dct["variables"][variable].get("proposed_standard_name"),
                            label=f"[variables:******:{variable}]***",
                        )
                        errors.extend(rule_errors)
                        warnings.extend(rule_warnings)
                elif is_undefined(dct["variables"][variable].get(attr_key)):
                    errors.append(
                        f"[variable:**************:{variable}]: No value defined for attribute '{attr_key}'."
                    )
                elif attr_rule.startswith("rule-func:same-type-as"):
                    var_checking_against = attr_rule.split(":")[-1]
                    rule_errors, rule_warnings = rules.check(
                        attr_rule,
                        dct["variables"][variable].get(attr_key),
                        context=dct["variables"][var_checking_against].get("type"),
                        label=f"[variables:******:{attr_key}]***",
                    )
                    errors.extend(rule_errors)
                    warnings.extend(rule_warnings)
                elif attr_rule.strip() == ("rule-func:check-qc-flags"):
                    rule_errors, rule_warnings = rules.check(
                        attr_rule,
                        dct["variables"][variable].get("flag_values"),
                        context=dct["variables"][variable].get("flag_meanings"),
                        label=f"[variable******:{variable}]: ",
                    )
                    errors.extend(rule_errors)
                    warnings.extend(rule_warnings)
                else:
                    rule_errors, rule_warnings = rules.check(
                        attr_rule,
                        dct["variables"][variable].get(attr_key),
                        label=f"[variables:******:{variable}] Value of attribute '{attr_key}' -",
                    )
                    errors.extend(rule_errors)
                    warnings.extend(rule_warnings)

    else:
        if variable not in dct["variables"].keys():
            errors.append(
                f"[variable**************:{variable}]: Variable does not exist in file. "
                f"{search_close_match(variable, dct['variables'].keys()) if not skip_spellcheck else ''}"
            )
        else:
            for attr in defined_attrs:
                if isinstance(attr, dict) and len(attr.keys()) == 1:
                    for key, value in attr.items():
                        attr = f"{key}: {value}"
                attr_key = attr.split(":")[0]
                attr_value = ":".join(attr.split(":")[1:])
                if attr_key not in dct["variables"][variable]:
                    errors.append(
                        f"[variable**************:{variable}]: Attribute '{attr_key}' does not exist. "
                        f"{search_close_match(attr_key, dct['variables'][variable]) if not skip_spellcheck else ''}"
                    )
                elif "<" in attr_value:
                    # work this out
                    pass
                elif not str(dct["variables"][variable].get(attr_key)) == attr_value:
                    errors.append(
                        f"[variable**************:{variable}]: Attribute '{attr_key}' must have definition '{attr_value}', "
                        f"not '{dct['variables'][variable].get(attr_key)}'."
                    )

            for attr in rules_attrs:
                if isinstance(attr, dict) and len(attr.keys()) == 1:
                    for key, value in attr.items():
                        attr = f"{key}:{value}"
                attr_key = attr.split(":")[0]
                attr_rule = ":".join(attr.split(":")[1:])
                if attr_key not in dct["variables"][variable]:
                    if not (
                        attr_key == "standard_name" and attr_rule.split(":")[1] == "allow-proposed"
                    ):
                        errors.append(
                            f"[variable:**************:{variable}]: Attribute '{attr_key}' does not exist. "
                            f"{search_close_match(attr_key, dct['variables'][variable].keys()) if not skip_spellcheck else ''}"
                        )
                    else:
                        rule_errors, rule_warnings = rules.check(
                            attr_rule,
                            dct["variables"][variable].get(attr_key),
                            context=dct["variables"][variable].get("proposed_standard_name"),
                            label=f"[variables:******:{variable}]***",
                        )
                        errors.extend(rule_errors)
                        warnings.extend(rule_warnings)
                #if attr_key not in dct["variables"][variable]:
                #    errors.append(
                #        f"[variable:**************:{variable}]: Attribute '{attr_key}' does not exist. "
                #        f"{search_close_match(attr_key, dct['variables'][variable].keys()) if not skip_spellcheck else ''}"
                #    )
                #elif is_undefined(dct["variables"][variable].get(attr_key)):
                #    errors.append(
                #        f"[variable:**************:{variable}]: No value defined for attribute '{attr_key}'."
                #    )
                elif attr_rule.startswith("rule-func:same-type-as"):
                    var_checking_against = attr_rule.split(":")[-1]
                    rule_errors, rule_warnings = rules.check(
                        attr_rule,
                        dct["variables"][variable].get(attr_key),
                        context=dct["variables"][var_checking_against].get("type"),
                        label=f"[variables:******:{attr_key}]***",
                    )
                    errors.extend(rule_errors)
                    warnings.extend(rule_warnings)
                elif attr_rule.strip() == "rule-func:check-qc-flags":
                    rule_errors, rule_warnings = rules.check(
                        attr_rule,
                        dct["variables"][variable].get("flag_values"),
                        context=dct["variables"][variable].get("flag_meanings"),
                        label=f"[variable******:{variable}]: ",
                    )
                    errors.extend(rule_errors)
                    warnings.extend(rule_warnings)
                else:
                    rule_errors, rule_warnings = rules.check(
                        attr_rule,
                        dct["variables"][variable].get(attr_key),
                        label=f"[variables:******:{variable}] Value of attribute '{attr_key}' -",
                    )
                    errors.extend(rule_errors)
                    warnings.extend(rule_warnings)

    return errors, warnings


def check_file_name(
    file_name: str,
    vocab_checks: Optional[Dict[str, str]] = None,
    rule_checks: Optional[Dict[str, str]] = None,
    skip_spellcheck: bool = False
) -> Tuple[List[str], List[str]]:
    """Checks format of NCAS-GENERAL file name.

    Checks format of NCAS-GENERAL file name is correct. Requires vocab checks for
    "instrument" and "data_product", plus rule_check for "platform", to be defined.

    Args:
        file_name: Name of NCAS-GENERAL file.
        vocab_checks: Dictionary with "instrument" and "data_product" as keys, and
          vocabs for each as values.
        rule_checks: Dictionary with "platform" as key, and rule check for platform as
          value.
        skip_spellcheck: skip looking for close misspelling of attribute if not found
          in variable. Default False.

    Returns:
        A list of errors and a list of warnings
    """
    vocab_checks = vocab_checks or {}
    rule_checks = rule_checks or {}
    errors = []
    warnings = []
    file_name_parts = file_name.split("_")

    # check instrument name
    if "instrument" in vocab_checks.keys():
        if (
            vocabs.check(vocab_checks["instrument"], file_name_parts[0], label="_")
            != []
        ):
            errors.append(
                f"[file name]: Invalid file name format - unknown instrument '{file_name_parts[0]}'"
            )
    else:
        msg = "No instrument vocab defined in specs"
        raise KeyError(msg)

    # check platform
    if "platform" in rule_checks.keys():
        if rules.check(
            rule_checks["platform"],
            file_name_parts[1],
            label="[file name]: Invalid file name format -",
        ) != ([], []):
            rule_errors, rule_warnings = rules.check(
                rule_checks["platform"],
                file_name_parts[1],
                label="[file name]: Invalid file name format -",
            )
            if rule_errors != []:
                errors.extend(rule_errors)
            if rule_warnings != []:
                warnings.extend(rule_warnings)
    else:
        msg = "No platform rule defined in specs"
        raise KeyError(msg)

    # check date format
    # could be yyyy, yyyymm, yyyymmdd, yyyymmdd-HH, yyyymmdd-HHMM, yyyymmdd-HHMMSS
    # first checks format, then date validity
    if not DATE_REGEX.match(file_name_parts[2]):
        errors.append(
            f"[file name]: Invalid file name format - bad date format '{file_name_parts[2]}'"
        )
    else:
        fmts = ("%Y", "%Y%m", "%Y%m%d", "%Y%m%d-%H", "%Y%m%d-%H%M", "%Y%m%d-%H%M%S")
        valid_date_found = False
        for f in fmts:
            try:
                _ = dt.datetime.strptime(file_name_parts[2], f)
                valid_date_found = True
                break
            except ValueError:
                pass
        if not valid_date_found:
            errors.append(
                f"[file name]: Invalid file name format - invalid date in file name '{file_name_parts[2]}'"
            )

    # check data product
    if "data_product" in vocab_checks.keys():
        if (
            vocabs.check(vocab_checks["data_product"], file_name_parts[3], label="_")
            != []
        ):
            errors.append(
                f"[file name]: Invalid file name format - unknown data product '{file_name_parts[3]}'"
            )
    else:
        msg = "No data product vocab defined in specs"
        raise KeyError(msg)

    # check version number format
    version_component = file_name_parts[-1].split(".nc")[0]
    if not re.match(r"^v\d.\d$", version_component):
        errors.append(
            f"[file name]: Invalid file name format - incorrect file version number '{version_component}'"
        )

    # check number of options - max length of splitted file name
    if len(file_name_parts) > 8:
        errors.append(
            f"[file name]: Invalid file name format - too many options in file name"
        )

    return errors, warnings


def check_generic_file_name(
    file_name: str,
    vocab_checks: Optional[Dict[str, str]] = None,
    segregator: Optional[Dict[str, str]] = None,
    extension: Optional[Dict[str, str]] = None,
    spec_verbose: Optional[Dict[str, str]] = None,
    skip_spellcheck: bool = False
) -> Tuple[List[str], List[str]]:
    """Checks file name against series of vocab checks.

    For a given file_name, splits name into parts based on the segregator and checks
    each part based on vocab_checks.

    Args:
        file_name: Name of the file to check.
        vocab_checks: Dictionary of vocab checks for each part of the file name. Keys
          must be "field00", "field01" e.t.c., and values for each are the vocab checks
          for each section.
        segregator: Character on which to split the file name. Should be dictionary
          with key "seg" and value being the character to separate on. Default
          segregator is "_".
        extension: File extension. Should be dictionary with key "ext" and value being
          the file extension. Default file extension is ".test".
        spec_verbose: Print additional information. Can be defined in the spec file,
          which gets passed through as dictionary. Should have key "spec_verb" and
          value True/False.
        skip_spellcheck: skip looking for close misspelling of attribute if not found
          in variable. Default False.

    Returns:
        A list of errors and a list of warnings
    """
    # Requires yaml file containing a list of file name fields and segregators
    # Loop over each file field and segregator until there are no more
    # check against defined file extension

    vocab_checks = vocab_checks or {}
    try:
        seg = segregator["seg"]
    except:
        seg='_'
    try:
        ext = extension["ext"]
    except:
        ext = '.test'
    try:
        spec_verb = spec_verbose["spec_verb"]
    except:
        spec_verb = False

    errors = []
    warnings = []

    # get filename parts
    if not isinstance(file_name,str):
        raise ValueError

    extracted_name = file_name.replace(ext,'')
    file_name_parts = extracted_name.split(seg)

    if spec_verb:
        print(f"File name: {file_name}")
        print(f"Segregator: {seg}")
        print(f"Extension: {ext}")
        print(f"All file name parts: {file_name_parts}")

    # Loop over file name parts
    for idx, key in enumerate(file_name_parts):
        if spec_verb:
            print('')
            print(idx, key)
        num=f"{idx:02}"

        # Check if number of file name parts matches the number of fields specified in the user-defined yaml file
        if len(vocab_checks) < len(file_name_parts):
            errors.append(
                        f"[file name]: Number of file name fields ({len(file_name_parts)}) is greater than the {len(vocab_checks)} fields expected."
                    )
            if spec_verb:
                print(errors[-1])
            break
        elif len(vocab_checks) > len(file_name_parts):
            errors.append(
                        f"[file name]: Number of file name fields ({len(file_name_parts)}) is less than the {len(vocab_checks)} fields expected."
                    )
            if spec_verb:
                print(errors[-1])
            break
        else:
            field=vocab_checks["field"+num]

            if field.startswith('__vocabs__') or field.startswith('__URL__'):
                # VOCAB (config or URL)
                if (
                        vocabs.check(field, key, spec_verb=spec_verb)
                        != []
                    ):
                        errors.append(
                            f"[file name]: Unknown field '{key}' in vocab {field}."
                        )
                        if spec_verb:
                            print(errors[-1])

            elif field.startswith('__date__'):
                # DATE REGEX
                datefmts=(field.split(":"))[1]
                fmts=(datefmts.split(","))
                if spec_verb:
                    print(f"Valid date formats: {fmts}")

                if not DATE_REGEX_GENERIC.match(key):
                    errors.append(
                        f"[file name]: Expecting date/time - bad date format '{key}'"
                    )
                    if spec_verb:
                        print(errors[-1])
                else:
                    valid_date_found = False
                    for f in fmts:
                        try:
                            _ = dt.datetime.strptime(key, f)
                            valid_date_found = True
                            break
                        except ValueError:
                            pass
                    if valid_date_found:
                        if spec_verb:
                            print(f"Date string {key} matches the required format")
                    else:
                        errors.append(
                            f"[file name]: Invalid date/time string '{key}'. Date/time should take the form YYYY[MM[DD[HH[MM[SS]]]]], where the fields in brackets are optional."
                        )
                        if spec_verb:
                            print(errors[-1])

            elif field.startswith('__version__'):
                # FILE/PRODUCT VERSION
                verfmt=(field.split(":"))[1]
                if re.match(verfmt, key):
                    if spec_verb:
                        print(f"File version {key} matches the required format")
                else:
                    errors.append(
                        f"[file name]: Invalid file version '{key}'. File versions should take the form n{{1,}}[.n{{1,}}]."
                    )
                    if spec_verb:
                        print(errors[-1])

            else:
                # FIELD NOT RECOGNISED
                errors.append(
                            f"[file name]: {field} field type not recognised."
                        )
                if spec_verb:
                    print(errors[-1])

    return errors, warnings


def check_radar_moment_variables(
    dct: Dict[str, Dict[str, Any]],
    exist_attrs: Optional[List[str]] = None,
    rule_attrs: Optional[Dict[str, str]] = None,
    one_of_attrs: Optional[List[str]] = None,
    skip_spellcheck: bool = False
) -> Tuple[List[str], List[str]]:
    """Finds moment variables in radar file and checks attributes of those variables.

    Finds all the moment variables in a radar file based on the existence of the
    "coordinates" attribute, and for all of those variables checks all the attributes
    listed in "exist_attrs" exist, all of the rules listed in "rule_attrs" are met, and
    one of the attributes in each string in "one_of_attrs" are defined.

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "global_attributes" as a key.
        exist_attrs: list of attributes to check exist.
        rules_attrs: dictionary with attribute to check as keys and rule to check
          against, and any options needed, as string value (e.g.
          "rule-func:string-of-length:3+"). See documentation on the `check` function
          in the `Rules` class for more information on formatting.
        one_of_attrs: list of attribute choices. Each string in the list should have a
          number of attributes separated by "|", and one of those attributes in each
          string should be present as an attribute in each variable.
        skip_spellcheck: skip looking for close misspelling of attribute if not found
          in variable. Default False.

    Returns:
        A list of errors and a list of warnings
    """
    exist_attrs = exist_attrs or []
    rule_attrs = rule_attrs or {}
    one_of_attrs = one_of_attrs or []

    errors = []
    warnings = []

    moment_variables = []
    for radarvariable, radarattributes in dct["variables"].items():
        if (
            isinstance(radarattributes, dict)
            and "coordinates" in radarattributes.keys()
        ):
            moment_variables.append(radarvariable)

    for variable in moment_variables:
        for attr in exist_attrs:
            if attr not in dct["variables"][variable]:
                errors.append(
                    f"[variable**************:{variable}]: Attribute '{attr}' does not exist. "
                    f"{search_close_match(attr, dct['variables'][variable]) if not skip_spellcheck else ''}"
                )
        for attr in rule_attrs:
            if isinstance(attr, dict) and len(attr.keys()) == 1:
                for key, value in attr.items():
                    attr = f"{key}:{value}"
            attr_key = attr.split(":")[0]
            attr_rule = ":".join(attr.split(":")[1:])
            if attr_key not in dct["variables"][variable]:
                errors.append(
                    f"[variable:**************:{variable}]: Attribute '{attr_key}' does not exist. "
                    f"{search_close_match(attr_key, dct['variables'][variable].keys()) if not skip_spellcheck else ''}"
                )
            elif is_undefined(dct["variables"][variable].get(attr_key)):
                errors.append(
                    f"[variable:**************:{variable}]: No value defined for attribute '{attr_key}'."
                )
            else:
                rule_errors, rule_warnings = rules.check(
                    attr_rule,
                    dct["variables"][variable].get(attr_key),
                    label=f"[variables:******:{variable}] Value of attribute '{attr_key}' -",
                )
                errors.extend(rule_errors)
                warnings.extend(rule_warnings)
        for attrs in one_of_attrs:
            attr_options = attrs.split("|")
            matches = 0
            for attr in attr_options:
                if attr in dct["variables"][variable]:
                    matches += 1
            if matches == 0:
                errors.append(
                    f"[variable:**************:{variable}]: One attribute of '{attr_options}' must be defined."
                )
            elif matches > 1:
                errors.append(
                    f"[variable:**************:{variable}]: Only one of '{attr_options}' should be defined, {matches} found."
                )
    return errors, warnings


def check_defined_only(
    dct: Dict[str, Dict[str, Any]],
    all_global_attrs: List[str],
    all_dimensions: List[str],
    all_variables: List[str],
    skip_spellcheck: bool = False,
 ):
    """Checks that only defined global attributes, dimensions and variables are present.

    Args:
        dct: dictionary of file data, as made by the `to_dict()` function in each
          reader class, with "variables", "dimensions" and "global_attributes" as keys.
        all_global_attrs: list of all allowed global attributes.
        all_dimensions: list of all allowed dimensions.
        all_variables: list of all allowed variables.

    Returns:
        A list of errors and a list of warnings
    """
    errors = []
    warnings = []
    for attr in dct['global_attributes']:
        if attr not in all_global_attrs:
            errors.append(f"[global-attributes:**************:{attr}]: Invalid global attribute '{attr}' found in file.")
    for dim in dct['dimensions']:
        if dim not in all_dimensions:
            errors.append(f"[dimension**************:{dim}]: Invalid dimension '{dim}' found in file.")
    for var in dct['variables']:
        if var not in all_variables:
            errors.append(f"[variable**************:{var}]: Invalid variable '{var}' found in file.")
    return errors, warnings
