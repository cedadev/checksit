"""Load and parse specs and run spec checks.

Class and functions to handle loading and printing of specs, and running checks defined
in specs.
"""

import os
import glob
import json
import yaml
import importlib
import sys
from typing import List, Dict, Any, Union, Optional, Tuple
from .config import get_config

SpecCheck = Dict[str, Union[str, Dict[str, Any]]]
SpecFile = Dict[str, SpecCheck]

conf = get_config()
specs_dir = os.path.join(conf["settings"].get("specs_dir", "./specs"), "groups")


def _parse_specs(spec_files: List[str]) -> Dict[str, SpecFile]:
    """Parses specs into dictionary.

    Loads each spec file listed into a dictionary as a dictionary. The name of the spec
    file is used as for the keys, with the specs themselves as the values. The
    dictionary for each spec has string values as keys (whose actual values are
    irrelevant), with another dictionary as the value. This dictionary will have two
    keys, "func" and "params" - "func" contains the name and path of the checksit
    function to use, and "params" contains a dictionary of the parameters to use in the
    function. For example:
    ```
    {
      "spec-file-name": {
        "var-requires0": {
          "func": "checksit.generic.func-name",
          "params": {"param1": "value", "param2": ["value1", "value2"]}},
        "var-requires1": {...},
      },
      "spec-file-name2": {...},
    }
    ```

    Args:
        spec_files: names with file path of the spec files to parse

    Returns:
        Dictionary of loaded specs.
    """
    return dict(
        [
            (os.path.basename(f)[:-4], yaml.load(open(f), Loader=yaml.SafeLoader))
            for f in spec_files
        ]
    )


def load_specs(spec_ids: Optional[List[str]] = None) -> Dict[str, SpecFile]:
    """Loads specs into dictionary.

    For a given list of spec file names, appends the specs directory (by default
    "specs/groups") and loads all specs. If no specs are given, all specs in the specs
    directory (but not in subdirectories) are loaded.

    Args:
        spec_ids: names of spec files to load

    Returns:
        Dictionary of loaded specs.
    """
    spec_ids = spec_ids or []
    spec_files = [f"{specs_dir}/{spec_id}.yml" for spec_id in spec_ids] or glob.glob(
        f"{specs_dir}/*.yml"
    )

    return _parse_specs(spec_files)


def show_specs(spec_ids: Optional[List[str]] = None) -> None:
    """Print out information on specs.

    For a given list of spec file names, prints the specs to output. If no spec file
    name is given, all specs in the spec directory (by default "specs/groups"), but not
    in subdirectories, are printed.

    Args:
        spec_ids: name of spec files to print
    """
    all_specs = load_specs(spec_ids)
    spec_ids_names = tuple([(spec_id.split("/")[-1]) for spec_id in spec_ids])

    if not spec_ids:
        specs = all_specs.items()
    else:
        specs = [
            (spec_ids[spec_ids_names.index(spec_id)], spec)
            for (spec_id, spec) in all_specs.items()
            if spec_id in spec_ids_names
        ]

    print("Specifications:")
    for spec_id, spec in specs:
        print(f"\n{spec_id}:")
        print(json.dumps(spec, indent=4).replace("\\\\", "\\"))


class SpecificationChecker:
    """Manage checks from spec files.

    Load spec from file and run the checks against record.

    Attributes:
        spec_id: Name of spec file.
        spec: Spec loaded in as dictionary.
    """

    def __init__(self, spec_id: str) -> None:
        """Initialise the class for the given spec file.

        Args:
            spec_id: name of the spec file.
        """
        self._setup(spec_id)

    def _setup(self, spec_id: str) -> None:
        """Setup class attributes and load spec.

        Sets class attributes and loads in the spec file.

        Args:
            spec_id: name of spec file.
        """
        self.spec_id = spec_id
        self.spec = load_specs([spec_id])[spec_id.split("/")[-1]]

    def _run_check(
        self,
        record: Dict[str, Union[Dict[str, str], Dict[str, Dict[str, str]], str]],
        check_dict: SpecCheck,
        skip_spellcheck: bool = False,
    ) -> Tuple[List[str], List[str]]:
        """Runs specific check from spec against record.

        Args:
            record: dictionary of file content from file parser `to_dict()` function.
            check_dict: dictionary with individual spec check, with keys "func" and
              "params".
            skip_spellcheck: Skip the spellcheck in rules and functions that utilise
              spell checking.

        Returns:
            List of errors and list of warnings from check.
        """
        d = check_dict
        parts = d["func"].split(".")

        mod_path, func = ".".join(parts[:-1]), parts[-1]
        # Import the module if not already imported
        if mod_path not in sys.modules:
            importlib.import_module(mod_path)
        func = getattr(sys.modules[mod_path], func)

        params = d["params"]
        params["skip_spellcheck"] = skip_spellcheck
        return func(record, **params)

    def run_checks(
        self,
        record: Dict[str, Union[Dict[str, str], Dict[str, Dict[str, str]], str]],
        skip_spellcheck: bool = False,
    ) -> Tuple[List[str], List[str]]:
        """Runs checks in spec against record.

        Takes the record of a file, as produced by the `to_dict()` function from the
        file parser, and checks it against the checks specified in the spec file.

        Args:
            record: dictionary of file content from file parser `to_dict()` function.
            skip_spellcheck: Skip the spellcheck in rules and functions that utilise
              spell checking.

        Returns:
            List of errors and list of warnings from all spec file checks.
        """
        errors = []
        warnings = []

        for _, check_dict in self.spec.items():
            check_errors, check_warnings = self._run_check(
                record, check_dict, skip_spellcheck=skip_spellcheck
            )
            errors.extend(check_errors)
            warnings.extend(check_warnings)

        return errors, warnings
