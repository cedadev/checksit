import os
import re
import json
from collections import deque
import requests


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

    def _load_from_url_ncas(self, vocab_id_url):
        vocab_id_url_base = vocab_id_url.split("/__latest__")[0]
        vocab_id_url_base = vocab_id_url_base.replace(
            "raw.githubusercontent.com", "github.com"
        )
        latest_version = requests.get(
            f"{vocab_id_url_base}/releases/latest"
        ).url.split("/")[-1]
        vocab_id_url = vocab_id_url.replace("__latest__", latest_version)
        res = requests.get(vocab_id_url.replace("__URL__", "https://"))
        if res.status_code == 200:
            vocab_list = res.json()
        else:
            print(f"[WARNING] Failed to load vocab: {vocab_id_url}")
        return vocab_list

    def _load_from_url_esacci(self, vocab_id_url):
        res = requests.get(vocab_id_url)
        if res.status_code == 200:
            js = res.json()

            if 'dataType' in vocab_id_url:
                vocab_list=sorted([altLabel[0]["@value"] for js_dct in js for key, altLabel in js_dct.items() if key.endswith("#altLabel")])
            elif 'product' in vocab_id_url:
                vocab_list=sorted([prefLabel[0]["@value"] for js_dct in js for key, prefLabel in js_dct.items() if key.endswith("#prefLabel")])
            else:
                print('ESA CCI vocab url not recognised.')
        else:
            print(f"[WARNING] Failed to load vocab: {vocab_id_url}")
        return vocab_list

    def _load_from_url(self, vocab_id):
        # Loads a specific vocabulary from a URL
        vocab_id_url = vocab_id.replace("__URL__", "https://")
        if (
            vocab_id_url.startswith("https://raw.githubusercontent.com")
            and "/__latest__/" in vocab_id_url
        ):
            vocab_list=self._load_from_url_ncas(vocab_id_url)
        elif (
            vocab_id_url.startswith("https://vocab.ceda.ac.uk")
        ):
            vocab_list=self._load_from_url_esacci(vocab_id_url)
        else:
            print(f"Vocabulary url provided is not recognised")

        self._vocabs[vocab_id] = vocab_list

    def __getitem__(self, vocab_id):
        # Enables dictionary access to individual vocabulary items
        if vocab_id not in self._vocabs:
            if vocab_id.startswith("__URL__"):
                self._load_from_url(vocab_id)
            else:
                self._load(vocab_id)

        return self._vocabs[vocab_id]

    def lookup(self, vocab_lookup):
        # A nested dictionary-style look-up using a string: vocab_lookup
        obj = self
        vocab_lookup = re.sub(f"^{vocabs_prefix}:", "", vocab_lookup)

        for i, key in enumerate(vocab_lookup.split(":")):
            if isinstance(obj, dict) or i == 0:
                if key in WILDCARD:
                    if i + 1 != len(vocab_lookup.split(":")):
                        obj = [obj[key] for key in obj.keys()]
                    else:
                        # WILDCARD used as last option, just get keys
                        obj = list(obj.keys())
                else:
                    obj = obj[key]
            else:
                if not isinstance(obj, list):
                    # sanity check
                    raise ValueError(f"Confused how we got here, obj = {obj}")
                elif key in WILDCARD:
                    raise ValueError(
                        f"Second WILDCARD ({WILDCARD}) in query {vocab_lookup} not allowed"
                    )
                else:
                    # obj should be list of dicts, creating list of values or dicts
                    obj = [d[key] for d in obj]

        return obj

    def check(self, vocab_lookup, value, label="", lookup=True, spec_verb=False):
        # Return a list of errors - empty list if no errors
        errors = []
        options = [self.lookup(vocab_lookup) if lookup else vocab_lookup][0]
        if spec_verb:
            print(f"Vocab lookup: {vocab_lookup}")

        if isinstance(options, list):
            if value not in options:
                errors.append(
                    f"{label} '{value}' not in vocab options: {options} (using: '{vocab_lookup}')"
                )
            else:
                if spec_verb:
                    print(f"Value: {value} is in list {options}")
        elif isinstance(options, dict):
            for key in options.keys():
                if key in value.keys():
                    errors.extend(
                        self.check(
                            options[key],
                            value[key],
                            label=f"{label}:{key}",
                            lookup=False,
                        )
                    )
                else:
                    errors.append(f"{label} does not have attribute '{key}'")
        elif value != options:
            errors.append(
                f"{label} '{value}' does not equal required vocab value: '{options}' (using: '{vocab_lookup}')"
            )

        return errors


vocabs = Vocabs()
