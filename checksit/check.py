import os
import sys
import glob
import tempfile
import re
import difflib
import yaml

from .cvs import vocabs, vocabs_prefix
from .rules import rules, rules_prefix
from .readers import pp, badc_csv, cdl, yml
from .utils import get_file_base, extension
from .config import get_config

UNDEFINED = "UNDEFINED"
conf = get_config()
self_check_context = {}


class Checker:

    def __init__(self, template="auto", mappings=None, extra_rules=None, ignore_attrs=None, 
                auto_cache=False, verbose=False, log_mode="standard"):
        self.template = template
        self.mappings = mappings or {}
        self.extra_rules = extra_rules or {}
        self.ignore_attrs = ignore_attrs or []
        self.auto_cache = auto_cache
        self.verbose = verbose
        self.log_mode = log_mode
        self._check_context = {}

    def _update_check_context(self, file_path, template):
        self._check_context["file_path"] = file_path
        self._check_context["size"] = os.path.getsize(file_path)
        self._check_context["template"] = template

    def _compare_items(self, rec, tmpl, key, label, mappings=None, 
                      extra_rules=None, ignore_attrs=None):

        mappings = mappings or self.mappings
        extra_rules = extra_rules or self.extra_rules
        ignore_attrs = ignore_attrs or self.ignore_attrs
        errors = []

        label_key = f"{label}:{key}"

        if label_key in ignore_attrs:
            # Ignore if told to ignore
            return errors

        # Map key if required
        rec_key = mappings.get(key, key)

        if isinstance(tmpl[key], dict):
            errors.extend(self._compare_dicts(rec, tmpl, key, mappings=mappings, ignore_attrs=ignore_attrs))
        else:
            tmpl_value = str(tmpl[key])

            if label_key in conf["settings"]["excludes"]:
                pass
            elif key.startswith(f"{vocabs_prefix}:"):
                errors.extend(vocabs.check(tmpl[key], rec.get(rec_key, UNDEFINED), label=label_key))
            elif tmpl_value.startswith(f"{vocabs_prefix}:"):
                errors.extend(vocabs.check(tmpl[key], rec.get(rec_key, UNDEFINED), label=label_key))
            # Rule defined in template value
            elif tmpl_value.startswith(f"{rules_prefix}:"):
                errors.extend(rules.check(tmpl[key], rec.get(rec_key, UNDEFINED), 
                              context=self._check_context, label=label_key))
            # Rule defined in `extra_rules` dictionary
            elif [rule for rule in extra_rules if rule.startswith(label_key)]:
                rule_key = [rule for rule in extra_rules if rule.startswith(label_key)][0]
                rule = extra_rules[rule_key]
                errors.extend(rules.check(rule, rec.get(rec_key, UNDEFINED), 
                              context=self._check_context, label=label_key))
            # Else...
            elif tmpl[key] != rec.get(rec_key, UNDEFINED):
                errors.append(f"{label_key}: '{rec.get(rec_key, UNDEFINED)}' does not match expected: '{tmpl[key]}'")

        return errors

    def _compare_dicts(self, record, template, label, mappings=None, ignore_attrs=None):
        mappings = mappings or self.mappings
        errors = []
        # list_types = [] #"variables" #- no longer used - as comparisons need key/values

        do_sort = False
        if label in ("dimensions", "global_attributes"):
            do_sort = True

        # if label in list_types:
        #     tmpl = template[label]
        #     rec = record[label]

        #     if len(tmpl) != len(rec):
        #         errors.append(f"[ERROR] Number of '{label}' items differs between template ({len(tmpl)}) and record ({len(rec)})")
        #     else:
        #         for i in range(len(tmpl)):
        #             t = tmpl[i]
        #             r = rec[i]
        #             for key in t:
        #                 errors.extend(self.compare_items(r, t, key, label=label, mappings=mappings, ignore_attrs=ignore_attrs))
        # else:

        # Recursively check dicts
        tmpl = template[label]
        rec_key = mappings.get(label, label)

        if rec_key in record:
            rec = record[rec_key]

            keys = tmpl.keys()
            if do_sort: keys = sorted(keys)

            for key in keys:
                errors.extend(self._compare_items(rec, tmpl, key, label=label, mappings=mappings, 
                              ignore_attrs=ignore_attrs))

        else:
            errors.append(f"Expected item '{label}' not found in data file.")

        return errors
                        
    def _check_file(self, file_content, template, mappings=None, extra_rules=None,
                        ignore_attrs=None, log_mode="standard", fmt_errors=None):
 
        if hasattr(file_content, "to_dict"):
            record = file_content.to_dict()

        if hasattr(template, "to_dict"):
            template = template.to_dict()

        if log_mode == "standard":
            print("\n\n---------------- Running checks ------------------\n")

        sections = "dimensions", "variables", "global_attributes"
        errors = getattr(file_content, "fmt_errors", [])

        for section in sections:
            errs = self._compare_dicts(record, template, section, mappings=mappings, ignore_attrs=ignore_attrs)
            errors.extend([f"[{section}] {err}" for err in errs])

        if log_mode == "compact":
            highest = "ERROR" if len(errors) > 0 else "NONE" 
            print(f"{highest} | {len(errors)} ", end="")
            err_string = " | ".join([err.replace("|", "__VERTICAL_BAR_REPLACED__") for err in errors])
            if err_string:
                print(f"| {err_string}") 

        else:
            if errors:
                print(f"[FAILED] with {len(errors)} errors:\n")
                for i, error in enumerate(errors):
                    count = i + 1
                    print(f"\t{count:02d}. {error}")
            else:
                print("[INFO] File is compliant!")            

    def check_file(self, file_path, template="auto", mappings=None, extra_rules=None, ignore_attrs=None, 
                auto_cache=False, verbose=False, log_mode="standard"):

        try:
            fp = FileParser()
            file_content = fp.parse_file_header(file_path, verbose=verbose)
        except Exception as err:
            if log_mode == "compact":
                print(f"{file_path} | ABORTED | FATAL | Cannot parse input file")
                sys.exit(1)
            else:
                raise Exception(err)

        # if template == "auto":
        #     template = self._template_from_config(file_path, verbose)
        # elif not os.path.isfile(template):
        #     if log_mode == "compact":
        #         print(f"{file_path} | ABORTED | FATAL | Cannot find template file specified")
        #         sys.exit(1)
        #     else:
        #         raise Exception(f"Cannot find specified template file: {template}")

        # tmpl = self.parse_file_header(template, auto_cache=auto_cache, verbose=verbose)

        tm = TemplateManager(auto_cache=auto_cache, verbose=verbose, log_mode=log_mode)
        tmpl = tm.get(file_path, template=template)

        self._update_check_context(file_path, template)

        if verbose:
            print("\n--- Template dictionary:\n", tmpl.to_dict())
            print("\n--- Datafile dictionary:\n", file_content.to_dict())

        if log_mode == "compact":
            print(f"{file_path} | {tmpl.inpt} | ", end="")
        else:
            print(f"\nRunning with:\n\tTemplate: {tmpl.inpt}\n\tDatafile: {file_content.inpt}")

        self._check_file(file_content, template=tmpl, mappings=mappings, extra_rules=extra_rules, 
                        ignore_attrs=ignore_attrs, log_mode=log_mode)


class TemplateManager:

    def __init__(self, auto_cache=False, verbose=False, log_mode="standard"):
        self.auto_cache = auto_cache
        self.verbose = verbose
        self.log_mode = log_mode

    def get(self, file_path, template="auto"):
        if template == "auto":
            template = self._get_template_from_config(file_path)
        elif not os.path.isfile(template):
            if self.log_mode == "compact":
                print(f"{file_path} | ABORTED | FATAL | Cannot find template file specified")
                sys.exit(1)
            else:
                raise Exception(f"Cannot find specified template file: {template}")

        fp = FileParser()
        tmpl = fp.parse_file_header(template, auto_cache=self.auto_cache, verbose=self.verbose)
        return tmpl

    def _get_template_from_config(self, file_path):
        # Loop through datasets in config to find appropriate template (cached or in archive)
        dsets = [key.split(":")[1] for key in conf if key.startswith("dataset:")]

        for dset in dsets:
            config = conf[f"dataset:{dset}"]

            if "regex_path" in config and re.search(config["regex_path"], file_path):
                return self._get_template_by_dataset(file_path, config) 
            elif "regex_file" in config and re.match(config["regex_file"], os.path.basename(file_path)):
                return self._get_template_by_dataset(file_path, config)
        else:
            return self._get_template_from_cache(file_path) 

    def _get_template_by_dataset(self, file_path, config):
        if "template" in config:
            return config["template"]
        elif "template_cache" in config:
            return self._get_template_from_cache(file_path, config["template_cache"]) 
        else:
            raise Exception("No rule for finding the template")

    def _get_template_from_cache(self, file_path, template_cache=None):
        if not template_cache:
            template_cache = conf["settings"]["default_template_cache_dir"]

        tmpl_base = get_file_base(file_path)

        if self.verbose: print(f"[INFO] Searching for exact match for: {tmpl_base}")
        matches = glob.glob(f"{template_cache}/{tmpl_base}_*.cdl")

        if matches:
            match = matches[0] 
            if self.verbose: print(f"[INFO] Found exact match: {match}")
        else:
            if self.verbose: print("[WARNING] Failed to find exact match, so trying nearest...")
            templates = os.listdir(template_cache)
            matches = difflib.get_close_matches(tmpl_base, templates)

            if matches:
                match = os.path.join(template_cache, matches[0])
            else: 
                match = conf["settings"].get("default_template")

        if not match:
            raise Exception(f"Unable to choose a template for: {file_path}")

        return match


class FileParser:

    def parse_file_header(self, file_path, auto_cache=False, verbose=False):
        ext = extension(file_path)

        if ext in ("nc", "cdl"):
            reader = cdl
        elif ext in ("pp"):
            reader = pp
        elif ext in ("txt"):
            reader = badc_csv
        elif ext in ("yml"):
            reader = yml
        else:
            raise Exception(f"No known reader for file with extension: {ext}")

        content = reader.read(file_path, verbose=verbose)

        if auto_cache:
            base = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(conf["settings"]["default_template_cache_dir"], base)

            if reader == cdl:
                # Special case for NetCDF files using CDL
                with open(f"{output_path}.cdl", "w") as writer:
                    writer.write(content.cdl)
            else:
                # All others use YAML
                with open(f"{output_path}.yml", "w") as writer:
                    yaml.dump(content.to_dict(), writer, Dumper=yaml.SafeDumper, 
                            default_flow_style=False, sort_keys=False)
                
        return content


def check_file(file_path, **kwargs):
    ch = Checker(**kwargs)
    return ch.check_file(file_path, **kwargs)
