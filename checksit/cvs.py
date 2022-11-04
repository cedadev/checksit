import os
import re
import json
from collections import deque


from .config import get_config
conf = get_config()

vocabs_dir = conf["settings"]["vocabs_dir"]
vocabs_prefix = conf["settings"]["vocabs_prefix"]

WILDCARD = ["__all__"]


class Vocabs:
    def __init__(self):
        # Creates: self._vocabs = {}
        self._vocabs = {}

    def _load(self, vocab_id):
        # Loads a specific vocabulary file based on the vocab_id
        vocab_file = os.path.join(vocabs_dir, f"{vocab_id}.json")
        self._vocabs[vocab_id] = json.load(open(vocab_file))

    def __getitem__(self, vocab_id):
        # Enables dictionary access to individual vocabulary items
        if vocab_id not in self._vocabs:
            self._load(vocab_id)

        return self._vocabs[vocab_id] 

    def lookup(self, vocab_lookup):
        # A nested dictionary-style look-up using a string: vocab_lookup
        obj = self
        vocab_lookup = re.sub(f"^{vocabs_prefix}:", "", vocab_lookup)

        for i,key in enumerate(vocab_lookup.split(":")):
            if key in WILDCARD:
                if i+1 != len(vocab_lookup.split(":")):
                    raise ValueError(f"WILDCARD {key} only allowed as last argument")
                else:
                    obj = list(obj.keys())
            else:
                obj = obj[key]

        return obj

#     def OLD_lookup(self, lookup):
# Used to have a special "__key__" lookup. not needed now.
#         # Parses a lookup string (from a template) and then looks up the vocabulary
#         # to return an item or a list of items
#         lookup = re.sub("^__vocabs__:", "", lookup)
#         self._load_vocab(lookup)
#         comps = deque(lookup.split(":"))
#         item = self.vocabs

#         while comps:
#             comp = comps.popleft()
#             if comp == "__key__":
#                 item = item.keys()
#             elif isinstance(item, list):
#                 item = [i[comp] for i in item if i.get(comp)]
#             else:
#                 item = item[comp]

#         return item

    def check(self, vocab_lookup, value, label="", lookup=True):
        # Return a list of errors - empty list if no errors
        errors = []
        options = [ self.lookup(vocab_lookup) if lookup else vocab_lookup ][0]

        if isinstance(options, list):
            if value not in options:
                errors.append(f"{label} '{value}' not in vocab options: {options} (using: '{vocab_lookup}')")
        elif isinstance(options, dict):
            for key in options.keys():
                if key in value.keys():
                    errors.extend(self.check(options[key], value[key], label = f"{label}:{key}", lookup=False))
                else:
                    errors.append(f"{label} does not have attribute '{key}'")
        elif value != options:
            errors.append(f"{label} '{value}' does not equal required vocab value: '{options}' (using: '{vocab_lookup}')")

        return errors



vocabs = Vocabs()
