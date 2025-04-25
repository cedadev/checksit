"""Load and check against controlled vocabularies.

This module provides a class to load controlled vocabularies, either from JSON files or
from URLs. It also provides a method to check a value against a controlled vocabulary.
"""
import os
import re
import json
import requests
from typing import Dict, List, Union, Any
import time


from .config import get_config

conf = get_config()

vocabs_dir: str = conf["settings"]["vocabs_dir"]
vocabs_prefix: str = conf["settings"]["vocabs_prefix"]

WILDCARD = ["__all__"]


class Vocabs:
    """Load and check against controlled vocabularies.

    This class provides methods to load controlled vocabularies from JSON files or from
    URLs on GitHub or the CEDA Vocab Service. It also provides a method to check a
    value against a value or list of values from those controlled vocabularies.

    Attributes:
        _vocabs: A dictionary of controlled vocabularies, where the keys are the
            vocabulary IDs and the values are the vocabularies themselves.
    """
    def __init__(self) -> None:
        """Initialise the Vocabs class."""
        self._vocabs = {}

    def _load(self, vocab_id: str) -> None:
        """Load a specific vocabulary file based on the vocab_id.

        Loads vocabulary file from the vocabs directory and stores it in the _vocabs
        dictionary.

        Args:
            vocab_id: The name of the vocabulary to load, without the ".json" ending.
        """
        vocab_file = os.path.join(vocabs_dir, f"{vocab_id}.json")
        self._vocabs[vocab_id] = json.load(open(vocab_file))

    def _load_from_url_github(self, vocab_id_url: str) -> Dict[str, Any]:
        """Load a specific vocabulary from a GitHub URL.

        Loads vocabulary file from a GitHub URL and stores it in the _vocabs
        dictionary. If the URL contains "__latest__", it will be replaced with the
        latest release version of the repository.

        Args:
            vocab_id_url: The URL of the vocabulary to load.

        Returns:
            The JSON loaded vocabulary.
        """
        vocab_list = {}
        vocab_id_url_base = vocab_id_url.split("/__latest__")[0]
        vocab_id_url_base = vocab_id_url_base.replace(
            "raw.githubusercontent.com", "github.com"
        )
        if "/__latest__/" in vocab_id_url:
            latest_version = self._get_url(
                f"{vocab_id_url_base}/releases/latest"
            ).url.split("/")[-1]
            vocab_id_url = vocab_id_url.replace("__latest__", latest_version)
        res = self._get_url(vocab_id_url.replace("__URL__", "https://"))
        if res.status_code != 200:
            print(f"[WARNING] Failed to load vocab: {vocab_id_url}")
            return vocab_list
        vocab_list = res.json()

        return vocab_list

    def _load_from_url_esacci(self, vocab_id_url: str) -> List[str]:
        """Load a specific vocabulary for ESA CCI.

        Loads vocabulary file for the European Space Agency Climate Change Initiative
        format from the CEDA Vocab Server and return values in that vocabulary.

        Args:
            vocab_id_url: The URL of the vocabulary to load.

        Returns:
            List of values from the vocabulary.
        """
        vocab_list = []
        res = requests.get(vocab_id_url)
        if res.status_code != 200:
            print(f"[WARNING] Failed to load vocab: {vocab_id_url}")
            return vocab_list
        js = res.json()

        if 'dataType' in vocab_id_url:
            vocab_list=sorted([altLabel[0]["@value"] for js_dct in js for key, altLabel in js_dct.items() if key.endswith("#altLabel")])
        elif 'product' in vocab_id_url:
            vocab_list=sorted([prefLabel[0]["@value"] for js_dct in js for key, prefLabel in js_dct.items() if key.endswith("#prefLabel")])
        else:
            print(f"[WARNING] ESA CCI vocab url not recognised: {vocab_id_url}")

        return vocab_list

    def _load_from_url(self, vocab_id: str) -> None:
        """Load specific vocabulary from URL.

        Loads a controlled vocabulary from either GitHub or the CEDA Vocab Server and
        saves it in the class' _vocabs attribute. Vocabulary should start with
        "__URL__" instead of "https://".

        Args:
            vocab_id: URL of vocabulary to load.
        """
        # Loads a specific vocabulary from a URL
        vocab_id_url = vocab_id.replace("__URL__", "https://")
        if (
            vocab_id_url.startswith("https://raw.githubusercontent.com")
        ):
            vocab_list=self._load_from_url_github(vocab_id_url)
        elif (
            vocab_id_url.startswith("https://vocab.ceda.ac.uk")
        ):
            vocab_list=self._load_from_url_esacci(vocab_id_url)
        else:
            print(f"Vocabulary url provided is not recognised: {vocab_id_url}")

        self._vocabs[vocab_id] = vocab_list

    def _get_url(self, url: str) -> requests.Response:
        """GET a URL, retrying on timeout or HTTP 429 error.

        Args:
            url: URL to GET.

        Returns:
            Response from the GET request.
        """
        try:
            res = requests.get(url)
            if res.status_code == 429:
                time.sleep(10)
                res = self._get_url(url)
        except TimeoutError:
            time.sleep(10)
            res = self._get_url(url)
        except:
            raise
        return res

    def __getitem__(self, vocab_id: str) -> Union[Dict[str, Any], List[str]]:
        """Enable dictionary access to individual vocabulary items.

        Access vocabularies as keys of the class. Loads vocabulary if not already
        loaded, and returns the vocabulary.

        Args:
            vocab_id: Vocabulary to get.

        Returns:
            Vocabulary as dictionary or vocabulary items as list.
        """
        if vocab_id not in self._vocabs:
            if vocab_id.startswith("__URL__"):
                self._load_from_url(vocab_id)
            else:
                self._load(vocab_id)

        return self._vocabs[vocab_id]

    def lookup(
        self,
        vocab_lookup: str,
    ) -> Union[Dict[str, Any], List[str], str, int, float]:
        """Nested dictionary-style look-up for value(s) in a vocabulary.

        Iterates through a vocabulary to find the value(s) to that are required for the
        check. The string "__all__" can be used once within the vocab_lookup. If
        "__all__" is the last key in the lookup, this will return a list of all the
        keys at that stage in the vocabulary file. If it comes before, e.g.
        "__all__:type", then it will return the value of "type" from every dictionary
        at the "__all__" level in the vocabulary.

        Args:
            vocab_lookup: String that states which vocabulary to use and what value(s)
              within the vocabulary to use. Should be of format
              "path/to/vocab_id:keys:in:vocab:file".

        Returns:
            Value, list of values, or dictionary of data from vocabulary.
        """
        obj = self
        vocab_lookup = re.sub(f"^{vocabs_prefix}:", "", vocab_lookup)

        for i, key in enumerate(vocab_lookup.split(":")):
            if i == 0:
                obj = obj[key]
            elif isinstance(obj, dict):
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

    def check(
        self,
        vocab_lookup: Union[str, List[Union[str, int, float]]],
        value: Any,
        label: str = "",
        lookup: bool = True,
        spec_verb: bool = False,
    ):
        """Checks value or values against value or values in vocabulary.

        Checks whether a given value (or values) matches the value or values at a given
        location in a controlled vocabulary. Controlled vocabulary is a JSON file
        either within the vocabs directory, or at a given URL. For vocabulary files in
        the vocab directory, the vocab_lookup should start
        "__vocabs__:path/to/file:..." (NOTE without the ".json" extension), and
        vocabularies accessed by a URL should start
        "__URL__:www.website.com/vocab_file.json:..." (NOTE without the "https://" at
        the start, but with the ".json" extension). Each key within the vocabulary file
        that leads to the value(s) required should follow and be separated by a colon.
        vocab_lookup could also be a list of values to check directly against - in this
        case, set `lookup` to False.
        Returns list of error messages for values not found in vocabulary.

        Args:
            vocab_lookup: Vocabulary to use and path to value(s) in vocabulary.
            value: Value(s) to check against vocabulary.
            label: Text to prepend to error messages.
            lookup: Find vocabulary from file or URL (True, default), or use
              `vocab_lookup` as the vocabulary to use (False).
            spec_verb: Print information about vocab check.

        Returns:
            List of messages where value(s) can not be found in vocabulary.
        """
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
