import os
import glob
import json
import yaml
import importlib

from .config import get_config


conf = get_config()
specs_dir = os.path.join(conf["settings"].get("specs_dir", "./specs"), "groups")


def _parse_specs(spec_files):
    return dict([(os.path.basename(f)[:-4], yaml.load(open(f), Loader=yaml.SafeLoader)) for f in spec_files])


def load_specs(spec_ids=None):
    spec_ids = spec_ids or []
    spec_files = [f"{specs_dir}/{spec_id}.yml" for spec_id in spec_ids] or \
                 glob.glob(f"{specs_dir}/*.yml")

    return _parse_specs(spec_files) 
     

def show_specs(spec_ids=None, verbose=False):
    
    all_specs = load_specs(spec_ids)
    spec_ids_names = tuple([(spec_id.split("/")[-1]) for spec_id in spec_ids])

    if not spec_ids:
        specs = all_specs
    else:
        specs = [(spec_ids[spec_ids_names.index(spec_id)], spec) for (spec_id, spec) in all_specs.items() if spec_id in spec_ids_names]

    print("Specifications:")
    for spec_id, spec in specs:
     
        print(f"\n{spec_id}:")
        print(json.dumps(spec, indent=4).replace("\\\\", "\\"))


class SpecificationChecker:

    def __init__(self, spec_id):
        self._setup(spec_id)

    def _setup(self, spec_id):
        self.spec_id = spec_id
        self.spec = load_specs([spec_id])[spec_id.split("/")[-1]]

    def _run_check(self, record, check_dict, skip_spellcheck=False):
        d = check_dict
        parts = d["func"].split(".")

        mod_path, func = ".".join(parts[:-1]), parts[-1]
        func = getattr(importlib.import_module(mod_path), func)

        params = d["params"]
        params["skip_spellcheck"] = skip_spellcheck
        return func(record, **params)

    def run_checks(self, record, skip_spellcheck=False):
        errors = []
        warnings = []

        for check_id, check_dict in self.spec.items():
            check_errors, check_warnings = self._run_check(
                                               record, check_dict, skip_spellcheck=skip_spellcheck
                                           )
            errors.extend(check_errors)
            warnings.extend(check_warnings) 

        return errors, warnings
