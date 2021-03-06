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
            "integer": r"-?\d+",
            "valid-email": r"[^@\s]+@[^@\s]+\.[^\s@]+",
            "valid-url": r"https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+)?",
            "valid-url-or-na": r"(https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+))|" + _NOT_APPLICABLE_RULES,
            "match:vN.M": r"v\d\.\d",
            "datetime": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?",
            "datetime-or-na": 
                 "(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?)|" + _NOT_APPLICABLE_RULES,
            "number": r"-?\d+(\.\d+)?"
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
            pattern = rule_lookup.split(":")[1]
            if not re.match(f"^{pattern}$", value):
                errors.append(f"{label} Value '{value}' does not match regular expression: '{pattern}'.")

        elif rule_lookup.startswith("regex-rule:"):
            regex_rule = rule_lookup.split(":", 1)[1]

            if regex_rule in self.static_regex_rules:
                pattern = self.static_regex_rules[regex_rule]

                if not re.match("^" + pattern + "$", value):
                    errors.append(f"{label} Value '{value}' does not match regex rule: '{regex_rule}'.")

            else:
                raise Exception(f"Rule not found with rule ID: {rule_lookup}.")

        else:
            raise Exception(f"Rule not found with rule ID: {rule_lookup}.")

        return errors


rules = Rules()

