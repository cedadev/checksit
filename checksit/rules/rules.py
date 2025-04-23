"""Handle rule checks for a given value.

This module contains the `Rules` class, which is used to check a value against a set of
rules. Available rules fall into four categories: rule functions, type rules, regex,
and regex rules. Rule functions are specifically defined functions that take a value and
return a list of errors if the value does not meet the rule. Type rules are simple type
checks, such as checking if a value is an integer or a string. Regex checks are custom
regular expressions that a value must match to be considered valid. Regex rules are
custom regular expressions that a value must match to be considered valid, and are
defined in the `static_regex_rules` dictionary.
"""

import os
import re
import json
from collections import deque
from numbers import Number
from typing import List, Union, Tuple, Dict

from . import rule_funcs
from ..config import get_config

conf = get_config()

rules_prefix = conf["settings"]["rules_prefix"]


class Rules:
    """Handle rule checks for a given value.

    This class is used to check a value against a set of rules. Available rules fall
    into four categories: rule functions, type rules, regex, and regex rules.

    Attributes:
        static_regex_rules: dictionary of static regex rules, with the key as the rule
            name and the value as a dictionary containing the regex rule and an example
            valid value
    """
    def __init__(self):
        """Initialise the Rules class.

        Initialise an instance of the Rules class and set the static regex rules used
        for `regex-rule` checks.
        """
        _NOT_APPLICABLE_RULES = (
            "(N/A)|(NA)|(N A)|(n/a)|(na)|(n a)|"
            "(Not Applicable)|(Not applicable)|(Not available)|(Not Available)|"
            "(not applicable)|(not available)"
        )

        self.static_regex_rules = {
            "integer": {"regex-rule": r"-?\d+", "example": "10"},
            "valid-email": {
                "regex-rule": r"[^@\s]+@[^@\s]+\.[^\s@]+",
                "example": "sam@example.com",
            },
            "valid-url": {
                "regex-rule": r"https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+)?",
                "example": "https://github.com",
            },
            "valid-url-or-na": {
                "regex-rule": r"(https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+)?)|"
                + _NOT_APPLICABLE_RULES,
                "example": "https://github.com",
            },
            "match:vN.M": {"regex-rule": r"v\d\.\d", "example": "v1.0"},
            "datetime": {
                "regex-rule": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?",
                "example": "2023-11-17T15:00:00",
            },
            "datetimeZ": {
                "regex-rule": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z",
                "example": "2023-11-17T15:00:00Z"
            },
            "datetime-or-na": {
                "regex-rule": r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?)|"
                + _NOT_APPLICABLE_RULES,
                "example": "2023-11-17T15:00:00",
            },
            "number": {"regex-rule": r"-?\d+(\.\d+)?", "example": "10.5"},
            "location": {
                "regex-rule": r"(.)+(\,\ )(.)+",
                "example": "Chilbolton Atmospheric Observatory, Chilbolton, Hampshire, UK",
            },
            "latitude-image": {
                "regex-rule": r"[\+|\-]?[0-9]{1,2}\.[0-9]{0,6}",
                "example": "12.345678",
            },
            "longitude-image": {
                "regex-rule": r"[\+|\-]?1?[0-9]{1,2}\.[0-9]{0,6}",
                "example": "123.456789",
            },
            "title": {
                "regex-rule": r"(.)+_(.)+_([1-2][0-9][0-9][0-9])([0][0-9]|[1][0-2])?([0-2][0-9]|[3][0-1])?-?([0-1][0-9]|[2][0-3])?([0-5][0-9])?([0-5][0-9])?(_.+)?_v([0-9]+)\.([0-9]+)\.(png|PNG|jpg|JPG|jpeg|JPEG)",
                "example": "ncas-cam-9_cao_20210623-215001_v1.0.jpg",
            },
            "title-data-product": {
                "regex-rule": r"(.)+_(.)+_([1-2][0-9][0-9][0-9])([0][0-9]|[1][0-2])?([0-2][0-9]|[3][0-1])?-?([0-1][0-9]|[2][0-3])?([0-5][0-9])?([0-5][0-9])?_(plot|photo)((.)+)?_v([0-9]+)\.([0-9]+)\.(png|PNG|jpg|JPG|jpeg|JPEG)",
                "example": "ncas-cam-9_cao_20210623-215001_photo_v1.0.jpg",
            },
            "name-format": {
                "regex-rule": r"([^,])+, ([^,])+( ?[^,]+|((.)\.))",
                "example": "Jones, Sam",
            },
            "name-characters": {
                "regex-rule": r"[A-Za-z_À-ÿ\-\'\ \.\,]+",
                "example": "Jones, Sam",
            },
            "altitude-image-warning": {
                "regex-rule": r"-?\d+\sm",  # should be integers only for images
                "example": "123 m",
            },
            "altitude-image": {
                "regex-rule": r"-?\d+(\.\d+)?\sm",
                "example": "123.45 m",
            },
            "ncas-email": {
                "regex-rule": r"[^@\s]+@ncas.ac.uk",
                "example": "sam.jones@ncas.ac.uk",
            },
        }

    def _map_type_rule(self, type_rule: str) -> type:
        """Map a string to a Python type.

        Args:
            type_rule: string representing the type

        Returns:
            Python type corresponding to the type_rule string.
        """
        mappings = {
            "number": Number,
            "integer": int,
            "int": int,
            "float": float,
            "string": str,
            "str": str,
        }
        return mappings[type_rule]

    def check(
        self,
        rule_lookup: str,
        value: Union[str, int, float, Number],
        context: Union[str, Dict[str, str], None] = None,
        label: str = "",
    ) -> Tuple[List[str], List[str]]:
        """Check a value against a set of rules.

        Check a value against a set of rules, returning a list of errors and warnings
        if the value does not meet the rules. The rules are defined in the rule_lookup
        string, which is a concatenation of rule IDs separated by '||'. The rule IDs
        correspond to rule functions, type rules, regex, and regex rules.

        Args:
            rule_lookup: string of rule IDs separated by '||'
            value: value to check
            context: additional context needed for some checks
            label: label for the value being checked

        Returns:
            Tuple of lists of errors and warnings.
        """
        if not context:
            context = {}

        # Return a list of errors - empty list if no errors
        errors = []
        warnings = []

        rule_lookup = re.sub(f"^{rules_prefix}:", "", rule_lookup)

        rule_lookup_list = rule_lookup.split("||")

        for i in rule_lookup_list:

            if i.split(":")[0].endswith("-warning"):
                output = warnings
            else:
                output = errors

            if i.startswith("rule-func"):
                rule_comps = i.split(":")
                rule_func = getattr(rule_funcs, rule_comps[1].replace("-", "_"))
                extras = [":".join(rule_comps[2:])]
                output.extend(rule_func(value, context, extras, label=label))

            elif i.startswith("type-rule"):
                type_rule = i.split(":")[1]

                if not isinstance(value, self._map_type_rule(type_rule)):
                    output.append(
                        f"{label} Value '{value}' is not of required type: '{type_rule}'."
                    )

            elif i.startswith("regex-rule"):
                regex_rule = i.split(":", 1)[1]

                if regex_rule in self.static_regex_rules:
                    pattern = self.static_regex_rules[regex_rule]["regex-rule"]

                    if not re.match("^" + pattern + "$", value):
                        output.append(
                            f"{label} Value '{value}' does not match regex rule: '{regex_rule}' - Example valid value '{self.static_regex_rules[regex_rule]['example']}'."
                        )

                else:
                    raise Exception(f"Regex rule not found with rule ID: {i}.")

            elif i.startswith("regex"):
                pattern = i.split(":", 1)[
                    1
                ]  # in case pattern has colons in it, e.g. a URL
                if not re.match(f"^{pattern}$", value):
                    output.append(
                        f"{label} Value '{value}' does not match regular expression: '{pattern}'."
                    )

            else:
                raise Exception(f"Rule not found with rule ID: {i}.")

        return errors, warnings


rules = Rules()
