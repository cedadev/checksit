import os
import re
import json
from collections import deque

from . import rule_funcs
from ..config import get_config
conf = get_config()

# vocabs_dir = conf["settings"]["vocabs_dir"]
rules_prefix = conf["settings"]["rules_prefix"]


class Rules:
    # def __init__(self):
    #     self._vocabs = {}

    # def _load(self, vocab_id):
    #     # Loads a specific vocabulary file based on the vocab_id
    #     vocab_file = os.path.join(vocabs_dir, f"{vocab_id}.json")
    #     self._vocabs[vocab_id] = json.load(open(vocab_file))

    # def __getitem__(self, vocab_id):
    #     # Enables dictionary access to individual vocabulary items
    #     if vocab_id not in self._vocabs:
    #         self._load(vocab_id)

    #     return self._vocabs[vocab_id] 

    # def lookup(self, rule_lookup):
    #     # A nested dictionary-style look-up using a string: vocab_lookup

    #     obj = self
    #     vocab_lookup = re.sub(f"^{rules_prefix}:", "", rule_lookup)

    #     for key in rule_lookup.split(":"):
    #         obj = obj[key]

    #     return obj

    def check(self, rule_lookup, value, context=None):
        if not context:
            context = {}

        # Return a list of errors - empty list if no errors
        errors = []

        rule_lookup = re.sub(f"^{rules_prefix}:", "", rule_lookup)

        if rule_lookup.startswith("rule_func:"):
            rule_comps = rule_lookup.split(":")
            rule_func = getattr(rule_funcs, rule_comps[1].replace("-", "_"))
            processors = rule_comps[2:]
            errors.extend(rule_func(value, context, processors))
        
        elif rule_lookup.startswith("regex:"):
            pattern = rule_lookup.split(":")[1]
            if not re.match(f"^{pattern}$", value):
                errors.append(f"Value '{value}' does not match regular expression: '{pattern}'.")

        else:
            raise Exception(f"Rule not found with rule ID: {rule_lookup}.")

        return errors


rules = Rules()


def GlobalAttrCheck():
        try:
            attr = row["Name"]
            rule = row["Compliance checking rules"]
            assert attr and rule
        except (KeyError, AssertionError):
            raise InvalidRowError()

        # Regexes for exact matches in the rule column
        _NOT_APPLICABLE_RULES = "(N/A)|(NA)|(N A)|(n/a)|(na)|(n a)|" \
                 "(Not Applicable)|(Not applicable)|(Not available)|(Not Available)|" \
                 "(not applicable)|(not available)"

        static_rules = {
            "Integer": r"-?\d+",
            "Valid email": r"[^@\s]+@[^@\s]+\.[^\s@]+",
            "Valid URL": r"https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+)?",
            "Valid URL _or_ N/A": r"(https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+))|" + _NOT_APPLICABLE_RULES,
            "Match: vN.M": r"v\d\.\d",
            "Match: YYYY-MM-DDThh:mm:ss\.\d+": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?",
            "Match: YYYY-MM-DDThh:mm:ss\.\d+ _or_ N/A": 
                 "(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?)|" + _NOT_APPLICABLE_RULES,
            "Exact match: <number> m": r"-?\d+(\.\d+)? m"
        }
        # Regexes based on a regex in the rule column
        regex_rules = {
            r"String: min (?P<count>\d+) characters?":
                lambda m: r".{" + str(m.group("count")) + r",}",
            r"One of:\s+(?P<choices>.+)":
                lambda m: r"(" + "|".join([i.strip() for i in m.group("choices").split(",")]) + r")"
        }

        regex = None
        
        try:
            regex = static_rules[rule]
        except KeyError:
            for rule_regex, func in regex_rules.items():

                match = re.match(rule_regex, rule)

                if match:
                    regex = func(match)
                    break

        if regex is None:
            # Handle 'exact match' case where need to look at other columns
            fixed_val_col = "Fixed Value"
            if (fixed_val_col in row
                and rule.lower() in ("exact match", "exact match of text to the left")):

                regex = re.escape(row["Fixed Value"])
            elif rule.lower() in ("exact match in vocabulary"):
                use_attr_check = "vocab"
                vocabulary_ref = "ncas:amf"
                vocab_options = row["Vocabulary"].split()
                vocab_lookup = ''
                for this_option in vocab_options:
                    this_term, this_lookup = this_option.split(":")
                    vocab_lookup = vocab_lookup + this_term + ":data:" + this_lookup + " "
                
                vocabulary_ref = "ncas:amf"
            else:
                raise ValueError(
                    "Unrecognised global attribute check rule: {}".format(rule)
                )

        if regex is not None:
            use_attr_check = "regex"

        if use_attr_check == "regex":
            check_details = {
                "attr": attr,
                "regex": regex,
                "use_attr_check": use_attr_check
            }
        elif use_attr_check == "vocab":
            check_details = {
                "attr": attr,
                "vocab_lookup": vocab_lookup,
                "vocabulary_ref": vocabulary_ref,
                "use_attr_check": use_attr_check
            }
        # Need to work out how to do this one
        elif use_attr_check == "selection":
            check_details = {
                "attr": attr
                
            }

        return check_details        
