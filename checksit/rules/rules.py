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
            "datetime": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?",
            "datetime-or-na": 
                 r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?)|" + _NOT_APPLICABLE_RULES,
            "number": r"-?\d+(\.\d+)?",
            "location": r'(.)+(\,\ )(.)+',
            "latitude-image": r'[\+|\-]?[0-9]{1,2}\.[0-9]{0,6}',
            "longitude-image": r'[\+|\-]?1?[0-9]{1,2}\.[0-9]{0,6}',
            "title": r'(.)+_(.)+_([1-2][0-9][0-9][0-9])([0][0-9]|[1][0-2])?([0-2][0-9]|[3][0-1])?-?([0-1][0-9]|[2][0-3])?([0-5][0-9])?([0-5][0-9])?_(.)+_v([0-9]+)\.([0-9]+)\.(png|PNG|jpg|JPG|jpeg|JPEG)',
            "title-data-product": r'(.)+_(.)+_([1-2][0-9][0-9][0-9])([0][0-9]|[1][0-2])?([0-2][0-9]|[3][0-1])?-?([0-1][0-9]|[2][0-3])?([0-5][0-9])?([0-5][0-9])?_(plot|photo)((.)+)?_v([0-9]+)\.([0-9]+)\.(png|PNG|jpg|JPG|jpeg|JPEG)',
            "name-format": r'(.)+, (.)+ ?((.)+|((.)\.))',
            "name-characters": r'[A-Za-z_À-ÿ\-\'\ \.\,]+',
            "altitude-image-warning": r'-?\d+\sm',    # should be integers only for images
            "altitude-image": r'-?\d+(\.\d+)?\sm',
            "ncas-email": r'[^@\s]+@ncas.ac.uk'
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
        warnings = []

        rule_lookup = re.sub(f"^{rules_prefix}:", "", rule_lookup)

        rule_lookup_list = rule_lookup.split(", ")

        for i in rule_lookup_list:

            if i.startswith("rule-func:"):
                rule_comps = i.split(":")
                rule_func = getattr(rule_funcs, rule_comps[1].replace("-", "_"))
                extras = rule_comps[2:]
                errors.extend(rule_func(value, context, extras, label=label))

            elif i.startswith("rule-func-warning:"):
                rule_comps = i.split(":")
                rule_func = getattr(rule_funcs, rule_comps[1].replace("-", "_"))
                extras = rule_comps[2:]
                warnings.extend(rule_func(value, context, extras, label=label))

            elif i.startswith("type-rule"):
                type_rule = i.split(":")[1]

                if not isinstance(value, self._map_type_rule(type_rule)):
                    errors.append(f"{label} Value '{value}' is not of required type: '{type_rule}'.")
                
            elif i.startswith("regex-warning:"):
                pattern = ':'.join(i.split(":")[1:])  # in case pattern has colons in it, e.g. a URL 
                if not re.match(f"^{pattern}$", value):
                    warnings.append(f"{label} Value '{value}' does not match regular expression: '{pattern}'.")

            elif i.startswith("regex:"):
                pattern = ':'.join(i.split(":")[1:])  # in case pattern has colons in it, e.g. a URL 
                if not re.match(f"^{pattern}$", value):
                    errors.append(f"{label} Value '{value}' does not match regular expression: '{pattern}'.")

            elif i.startswith("regex-rule-warning:"):
                regex_rule = i.split(":", 1)[1]

                if regex_rule in self.static_regex_rules:
                    pattern = self.static_regex_rules[regex_rule]

                    if not re.match("^" + pattern + "$", value):
                        warnings.append(f"{label} Value '{value}' does not match regex rule: '{regex_rule}'.")

                else:
                    raise Exception(f"Rule not found with rule ID: {rule_lookup}.")

            elif i.startswith("regex-rule:"):
                regex_rule = i.split(":", 1)[1]

                if regex_rule in self.static_regex_rules:
                    pattern = self.static_regex_rules[regex_rule]

                    if not re.match("^" + pattern + "$", value):
                        errors.append(f"{label} Value '{value}' does not match regex rule: '{regex_rule}'.")

                else:
                    raise Exception(f"Rule not found with rule ID: {rule_lookup}.")
            
            else:
                raise Exception(f"Rule not found with rule ID: {rule_lookup}.")

        return errors, warnings


rules = Rules()

