import os
import re
import json
from collections import deque
from numbers import Number

from . import rule_funcs
from ..config import get_config
conf = get_config()

rules_prefix = conf["settings"]["rules_prefix"]


class Rules:

    def __init__(self):

        _NOT_APPLICABLE_RULES = "(N/A)|(NA)|(N A)|(n/a)|(na)|(n a)|" \
                 "(Not Applicable)|(Not applicable)|(Not available)|(Not Available)|" \
                 "(not applicable)|(not available)"

        self.static_regex_rules = {
            "integer": {
                "regex-rule": r"-?\d+", 
                "example": "10"
            },
            "valid-email": {
                "regex-rule": r"[^@\s]+@[^@\s]+\.[^\s@]+",
                "example": ""
            },
            "valid-url": {
                "regex-rule": r"https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+)?",
                "example": "https://github.com"
            },
            "valid-url-or-na": {
                "regex-rule": r"(https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+))|" + _NOT_APPLICABLE_RULES,
                "example": "https://github.com"
            },
            "match:vN.M": {
                "regex-rule": r"v\d\.\d",
                "example": "v1.0"
            },
            "datetime": {
                "regex-rule": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?",
                "example": "2023-11-17T15:00:00"
            },
            "datetime-or-na": {
                 "regex-rule": "(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?)|" + _NOT_APPLICABLE_RULES,
                 "example": "2023-11-17T15:00:00"
            },
            "number": {
                "regex-rule": r"-?\d+(\.\d+)?",
                "example": "10.5"
            }
        }

    def _map_type_rule(self, type_rule):
        mappings = {
            "number": Number,
            "integer": int,
            "int": int,
            "float": float,
            "string": str,
            "str": str
        }
        return mappings[type_rule]

    def check(self, rule_lookup, value, context=None, label=""):
        if not context:
            context = {}

        # Return a list of errors - empty list if no errors
        errors = []

        rule_lookup = re.sub(f"^{rules_prefix}:", "", rule_lookup)

        if rule_lookup.startswith("rule-func:"):
            rule_comps = rule_lookup.split(":")
            rule_func = getattr(rule_funcs, rule_comps[1].replace("-", "_"))
            extras = rule_comps[2:]
            errors.extend(rule_func(value, context, extras, label=label))

        elif rule_lookup.startswith("type-rule"):
            type_rule = rule_lookup.split(":")[1]

            if not isinstance(value, self._map_type_rule(type_rule)):
                errors.append(f"{label} Value '{value}' is not of required type: '{type_rule}'.")
        
        elif rule_lookup.startswith("regex:"):
            pattern = ':'.join(rule_lookup.split(":")[1:])  # in case pattern has colons in it, e.g. a URL 
            if not re.match(f"^{pattern}$", value):
                errors.append(f"{label} Value '{value}' does not match regular expression: '{pattern}'.")

        elif rule_lookup.startswith("regex-rule:"):
            regex_rule = rule_lookup.split(":", 1)[1]

            if regex_rule in self.static_regex_rules:
                pattern = self.static_regex_rules[regex_rule]["regex-rule"]

                if not re.match("^" + pattern + "$", value):
                    errors.append(f"{label} Value '{value}' does not match regex rule: '{regex_rule}' - Example valid value '{self.static_regex_rules[regex_rule]['example']}'.")

            else:
                raise Exception(f"Rule not found with rule ID: {rule_lookup}.")

        else:
            raise Exception(f"Rule not found with rule ID: {rule_lookup}.")

        return errors


rules = Rules()

