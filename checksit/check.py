"""Initiate checks and file reading.

This module contains the main classes and functions for initialising template, rule and
spec checks on data files, as well as parsing the data files and managing templates.
"""

import os
import sys
import glob
import re
import difflib
import yaml
import urllib.request
import urllib.error
from typing import Optional, Union, List, Dict, Tuple

from .cvs import vocabs, vocabs_prefix
from .rules import rules, rules_prefix
from .readers import pp, badc_csv, cdl, yml, image
from .specs import SpecificationChecker
from .utils import get_file_base, extension, UNDEFINED
from .config import get_config
from .make_specs import make_amof_specs

AMOF_CONVENTIONS = ['"CF-1.6, NCAS-AMF-2.0.0"']
GENERAL_CONVENTION_PREFIXES = ["NCAS-AMF", "NCAS-AMOF", "NCAS-GENERAL"]
RADAR_CONVENTION_PREFIXES = ["NCAS-RADAR"]
IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]
conf = get_config()


class Checker:
    """Manage and intialise checks on data files.

    This class manages the initialisation of checks on data files, including retrieving
    the default specs if required for NCAS data files, and handles the printing of the
    results of the checks.

    Attributes:
        template: Template to use for checking. Options are "auto" (default), "off", or
          `<template file>`. File location is relative to the top level of the checksit
          repository.
        mappings: Dictionary of mappings to use when checking data files. Keys are the
          template keys and values are the data file keys.
        extra_rules: Dictionary of extra rules to use when checking data files. Keys are
          the template keys and values are the rules to apply.
        specs: List of spec files to use when checking data files. File location and path
          relative to the specs folder in the checksit repository.
        ignore_attrs: List of attributes to ignore when checking variables.
        auto_cache: Store the file in the template cache for future use as a template.
        log_mode: How the output should be printed. Options are "standard" (default) and
          "compact".
        verbose: Print additional information.
        ignore_warnings: Ignore warnings when checking the file, only return errors.
        skip_spellcheck: Skip the spellcheck in rules and functions that utilise spell
          checking.
    """

    def __init__(
        self,
        template: str = "auto",
        mappings: Optional[Dict[str, str]] = None,
        extra_rules: Optional[Dict[str, str]] = None,
        specs: Optional[List[str]] = None,
        ignore_attrs: Optional[List[str]] = None,
        auto_cache: bool = False,
        verbose: bool = False,
        log_mode: str = "standard",
        ignore_warnings: bool = False,
        skip_spellcheck: bool = False,
    ) -> None:
        """Initialise the Checker class.

        Args:
            template: Template to use for checking. Options are "auto" (default), "off",
              or `<template file>`. File location is relative to the top level of the
              checksit repository.
            mappings: Dictionary of mappings to use when checking data files. Keys are the
              template keys and values are the data file keys.
            extra_rules: Dictionary of extra rules to use when checking data files. Keys
              are the template keys and values are the rules to apply.
            specs: List of spec files to use when checking data files. File location and
              path relative to the specs folder in the checksit repository.
            ignore_attrs: List of attributes to ignore when checking variables.
            auto_cache: Store the file in the template cache for future use as a template.
            log_mode: How the output should be printed. Options are "standard" (default)
              and "compact".
            verbose: Print additional information.
            ignore_warnings: Ignore warnings when checking the file, only return errors.
            skip_spellcheck: Skip the spellcheck in rules and functions that utilise spell
              checking.
        """
        self.template = template
        self.mappings = mappings or {}
        self.extra_rules = extra_rules or {}
        self.specs = specs or []
        self.ignore_attrs = ignore_attrs or []
        self.auto_cache = auto_cache
        self.ignore_warnings = ignore_warnings
        self.verbose = verbose
        self.log_mode = log_mode
        self.skip_spellcheck = skip_spellcheck
        self._check_context = {}

    def _update_check_context(self, file_path: str, template: str) -> None:
        self._check_context["file_path"] = file_path
        self._check_context["size"] = os.path.getsize(file_path)
        self._check_context["template"] = template

    def _compare_items(
        self, rec, tmpl, key, label, mappings=None, extra_rules=None, ignore_attrs=None
    ):

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
            errors.extend(
                self._compare_dicts(
                    rec, tmpl, key, mappings=mappings, ignore_attrs=ignore_attrs
                )
            )
        else:
            tmpl_value = str(tmpl[key])

            if label_key in conf["settings"]["excludes"]:
                pass
            elif key.startswith(f"{vocabs_prefix}:"):
                errors.extend(
                    vocabs.check(
                        tmpl[key], rec.get(rec_key, UNDEFINED), label=label_key
                    )
                )
            elif tmpl_value.startswith(f"{vocabs_prefix}:"):
                errors.extend(
                    vocabs.check(
                        tmpl[key], rec.get(rec_key, UNDEFINED), label=label_key
                    )
                )
            # Rule defined in template value
            elif tmpl_value.startswith(f"{rules_prefix}:"):
                errors.extend(
                    rules.check(
                        tmpl[key],
                        rec.get(rec_key, UNDEFINED),
                        context=self._check_context,
                        label=label_key,
                    )
                )
            # Rule defined in `extra_rules` dictionary
            elif [rule for rule in extra_rules if rule.startswith(label_key)]:
                rule_key = [rule for rule in extra_rules if rule.startswith(label_key)][
                    0
                ]
                rule = extra_rules[rule_key]
                errors.extend(
                    rules.check(
                        rule,
                        rec.get(rec_key, UNDEFINED),
                        context=self._check_context,
                        label=label_key,
                    )
                )
            # Else...
            elif tmpl[key] != rec.get(rec_key, UNDEFINED):
                errors.append(
                    f"{label_key}: '{rec.get(rec_key, UNDEFINED)}' does not match expected: '{tmpl[key]}'"
                )

        return errors

    def _compare_dicts(self, record, template, label, mappings=None, ignore_attrs=None):
        mappings = mappings or self.mappings
        errors = []

        do_sort = False
        if label in ("dimensions", "global_attributes"):
            do_sort = True

        # Recursively check dicts
        tmpl = template[label]
        rec_key = mappings.get(label, label)

        if rec_key in record:
            rec = record[rec_key]

            keys = tmpl.keys()
            if do_sort:
                keys = sorted(keys)

            for key in keys:
                errors.extend(
                    self._compare_items(
                        rec,
                        tmpl,
                        key,
                        label=label,
                        mappings=mappings,
                        ignore_attrs=ignore_attrs,
                    )
                )

        else:
            errors.append(f"Expected item '{label}' not found in data file.")

        return errors

    def _check_file(
        self,
        file_content: Union[cdl.CDLParser, image.ImageParser, pp.PPHeader, badc_csv.BADCCSVHeader, yml.YAMLFile],
        template: Union[cdl.CDLParser, image.ImageParser, pp.PPHeader, badc_csv.BADCCSVHeader, yml.YAMLFile, str],
        mappings: Optional[Dict[str, str]] =None,
        extra_rules: Optional[Dict[str, str]] = None,
        specs: Optional[List[str]] = None,
        ignore_attrs: Optional[List[str]] = None,
        log_mode: str = "standard",
        #fmt_errors=None,
        ignore_warnings: bool =False,
        skip_spellcheck: bool = False,
    ) -> None:
        """Check the content of a file against a template and specs.

        Args:
            file_content: Content of the file to check.
            template: Template to use for checking. Options are "auto" (default), "off",
              or `<template file>`. File location is relative to the top level of the
              checksit repository.
            mappings: Dictionary of mappings to use when checking data files. Keys are the
              template keys and values are the data file keys.
            extra_rules: Dictionary of extra rules to use when checking data files. Keys
              are the template keys and values are the rules to apply.
            specs: List of spec files to use when checking data files. File location and
              path relative to the specs folder in the checksit repository.
            ignore_attrs: List of attributes to ignore when checking variables.
            log_mode: How the output should be printed. Options are "standard" (default)
              and "compact".
            ignore_warnings: Ignore warnings when checking the file, only return errors.
            skip_spellcheck: Skip the spellcheck in rules and functions that utilise spell
              checking.
        """
        if hasattr(file_content, "to_dict"):
            record = file_content.to_dict()

        if hasattr(template, "to_dict"):
            template = template.to_dict()

        if log_mode == "standard":
            print("\n\n---------------- Running checks ------------------\n")

        # Create a container for collecting errors
        errors = getattr(file_content, "fmt_errors", [])
        warnings = []

        # Use check specifications if requested
        specs = specs or self.specs

        for spec in specs:
            sr = SpecificationChecker(spec)
            if "file-name" in spec:
                spec_errors, spec_warnings = sr.run_checks(
                    file_content.inpt.split("/")[-1]
                )
            else:
                spec_errors, spec_warnings = sr.run_checks(
                    record, skip_spellcheck=skip_spellcheck
                )
            errors.extend(spec_errors)
            warnings.extend(spec_warnings)

        if template == "off" and log_mode == "standard":
            print("[WARNING] Template checks switched off!")
        elif template != "off":
            sections = "dimensions", "variables", "global_attributes"

            for section in sections:
                errs = self._compare_dicts(
                    record,
                    template,
                    section,
                    mappings=mappings,
                    ignore_attrs=ignore_attrs,
                )
                errors.extend([f"[{section}] {err}" for err in errs])

        if log_mode == "compact":
            if len(errors) > 0:
                highest = "ERROR"
                endstr = ""
                number = len(errors)
            elif len(warnings) > 0 and not ignore_warnings:
                highest = "WARNING"
                endstr = "\n"
                number = len(warnings)
            else:
                highest = "NONE"
                endstr = "\n"
                number = 0
            print(f"{highest} | {number} ", end=endstr)
            err_string = " | ".join(
                [err.replace("|", "__VERTICAL_BAR_REPLACED__") for err in errors]
            )
            if err_string:
                print(f"| {err_string}")

        else:
            if errors:
                print(f"[FAILED] with {len(errors)} errors:\n")
                for i, error in enumerate(errors):
                    count = i + 1
                    print(f"\t{count:02d}. {error}")
                compliant = False
            else:
                compliant = True

            if warnings and not ignore_warnings:
                print(f"\n[WARNING] {len(warnings)} warnings about file:\n")
                for i, warning in enumerate(warnings):
                    count = i + 1
                    print(f"\t{count:02d}. {warning}")

            if compliant:
                print("[INFO] File is compliant!")

    def _get_ncas_specs(
        self,
        file_path: str,
        file_content: Union[cdl.CDLParser, image.ImageParser, pp.PPHeader, badc_csv.BADCCSVHeader, yml.YAMLFile],
        log_mode: str = "standard",
        verbose: bool = False,
    ) -> Tuple[str, List[str]]:
        """Get the correct specs for NCAS data files.

        Args:
            file_path: Path to the file to check.
            file_content: Content of the file to check.
            log_mode: How the output should be printed. Options are "standard" (default)
              and "compact".
            verbose: Print additional information.

        Returns:
            Template and list of specs to use for checking the file.
        """
        template = "auto"
        specs = None
        # find appropriate specs depending on convention
        if file_path.split(".")[-1] == "nc" and ":Conventions" in file_content.cdl:
            conventions = (
                file_content.cdl.split(":Conventions =")[1].split(";")[0].strip()
            )
            # NCAS-GENERAL file
            if any(
                name in conventions.upper()
                for name in GENERAL_CONVENTION_PREFIXES
            ):
                if verbose:
                    print("\nNCAS-AMOF file detected, finding correct spec files")
                    print("Finding correct AMOF version...")
                version_number = (
                    conventions[conventions.index("NCAS-") :]
                    .split("-")[2]
                    .replace('"', "")
                )
                if version_number.count(".") == 1:
                    version_number = f"{version_number}.0"
                spec_folder = f"ncas-amof-{version_number}"
                if verbose:
                    print(f"  {version_number}")

                # check specs exist for that version
                specs_dir = os.path.join(
                    conf["settings"].get("specs_dir", "./specs"),
                    f"groups/{spec_folder}",
                )
                if not os.path.exists(specs_dir):
                    if verbose:
                        print(
                            f"Specs for version NCAS-GENERAL-{version_number} not found, attempting download..."
                        )
                    try:
                        vocabs_dir = os.path.join(
                            conf["settings"].get("vocabs_dir", "./checksit/vocabs"),
                            f"AMF_CVs/{version_number}",
                        )
                        cvs = urllib.request.urlopen(
                            f"https://github.com/ncasuk/AMF_CVs/tree/v{version_number}/AMF_CVs"
                        )
                        data = cvs.readlines()
                        if not os.path.exists(specs_dir):
                            os.mkdir(specs_dir)
                        if not os.path.exists(vocabs_dir):
                            os.mkdir(vocabs_dir)
                        for line in data:
                            if (
                                f'href="/ncasuk/AMF_CVs/blob/v{version_number}/AMF_CVs'
                                in line.decode()
                            ):
                                json_file = (
                                    line.decode().split('href="')[1].split('">')[0]
                                )
                                if json_file.startswith("/ncasuk/AMF_CVs/blob/"):
                                    cv = urllib.request.urlopen(
                                        f"https://raw.githubusercontent.com{json_file.replace('/blob','')}"
                                    )
                                    json_file_name = json_file.split("/")[-1]
                                    with open(
                                        f"{vocabs_dir}/{json_file_name}", "w"
                                    ) as f:
                                        _ = f.write(cv.read().decode())
                        make_amof_specs(version_number)
                        if verbose:
                            print("  Downloaded of specs successful")
                    except urllib.error.HTTPError:
                        if log_mode == "compact":
                            print(
                                f"{file_path} | ABORTED | FATAL | Cannot download data for NCAS-AMOF-{version_number}"
                            )
                        else:
                            print(
                                f"[ERROR]: Cannot download data for NCAS-AMOF-{version_number}."
                            )
                            print("Aborting...")
                        sys.exit()
                    except PermissionError:
                        if log_mode == "compact":
                            print(
                                f"{file_path} | ABORTED | FATAL | Permission Error when trying to create folders or files within checksit."
                            )
                        else:
                            print(
                                f"[ERROR]: Permission Error when trying to create folders or files within checksit."
                            )
                            print(
                                f"Please talk to your Admin about installing data for NCAS-AMOF-{version_number}."
                            )
                        sys.exit()
                    except:
                        raise

                # get deployment mode and data product, to then get specs
                deployment_mode = (
                    file_content.cdl.split(":deployment_mode =")[1]
                    .split(";")[0]
                    .strip()
                    .strip('"')
                )
                deploy_spec = f"{spec_folder}/amof-common-{deployment_mode}"
                product = file_path.split("/")[-1].split("_")[3]
                product_spec = f"{spec_folder}/amof-{product}"
                specs = [
                    f"{spec_folder}/amof-file-name",
                    deploy_spec,
                    product_spec,
                    f"{spec_folder}/amof-global-attrs",
                ]
                # don't need to do template check
                template = "off"

            # NCAS-Radar
            elif any(
                name in conventions.upper()
                for name in RADAR_CONVENTION_PREFIXES
            ):
                version_number = (
                    conventions[conventions.index("NCAS-") :]
                    .split("-")[2]
                    .split(" ")[0]
                    .replace('"', "")
                )
                if version_number.count(".") == 1:
                    version_number = f"{version_number}.0"
                template = "off"
                spec_names = [
                    "coordinate-variables",
                    "dimensions",
                    "global-attrs",
                    "global-variables",
                    "instrument-parameters",
                    "location-variables",
                    "moment-variables",
                    "radar-calibration",
                    "radar-parameters",
                    "sensor-pointing-variables",
                    "sweep-variables",
                ]
                specs = [f"ncas-radar-{version_number}/{spec}" for spec in spec_names]

        elif (
            file_path.split(".")[-1].lower() in IMAGE_EXTENSIONS
            and "XMP-photoshop:Instructions" in file_content.global_attrs.keys()
        ):
            conventions = file_content.global_attrs["XMP-photoshop:Instructions"]
            if (
                "National Centre for Atmospheric Science Image Metadata Standard"
                in file_content.global_attrs["XMP-photoshop:Instructions"].replace(
                    "\n", " "
                )
            ):
                if verbose:
                    print("\nNCAS-IMAGE file detected, finding correct spec files")
                    print("Finding correct IMAGE version...")
                version_number = (
                    conventions.replace("\n", " ")
                    .split("Metadata Standard ")[1]
                    .split(":")[0]
                )
                spec_folder = f"ncas-image-{version_number}"
                if verbose:
                    print(f"  {version_number}")
                specs_dir = os.path.join(
                    conf["settings"].get("specs_dir", "./specs"),
                    f"groups/{spec_folder}",
                )
                if not os.path.exists(specs_dir):
                    print(
                        f"[ERROR] specs for NCAS-IMAGE {version_number} can not be found."
                    )
                    print("Aborting...")
                    sys.exit()
                product = file_path.split("/")[-1].split("_")[3]
                product_spec = f"{spec_folder}/amof-{product}"
                specs = [product_spec, f"{spec_folder}/amof-image-global-attrs"]
                template = "off"

        return template, specs

    def check_file(
        self,
        file_path: str,
        template: str = "auto",
        mappings: Optional[Dict[str, str]] = None,
        extra_rules: Optional[Dict[str, str]] = None,
        specs: Optional[List[str]] = None,
        ignore_attrs: Optional[List[str]] = None,
        auto_cache: bool = False,
        verbose: bool = False,
        log_mode: str = "standard",
        ignore_warnings: bool = False,
        skip_spellcheck: bool = False,
    ) -> None:
        """Check a data file against a template or specs.

        Read in the given file, checks specified options for template and specs, and
        gets NCAS specs if required.

        Args:
            file_path: Path to the file to check.
            template: Template to use for checking. Options are "auto" (default), "off",
              or `<template file>`. File location is relative to the top level of the
              checksit repository.
            mappings: Dictionary of mappings to use when checking data files. Keys are the
              template keys and values are the data file keys.
            extra_rules: Dictionary of extra rules to use when checking data files. Keys
              are the template keys and values are the rules to apply.
            specs: List of spec files to use when checking data files. File location and
              path relative to the specs folder in the checksit repository.
            ignore_attrs: List of attributes to ignore when checking variables.
            auto_cache: Store the file in the template cache for future use as a template.
            log_mode: How the output should be printed. Options are "standard" (default)
              and "compact".
            verbose: Print additional information.
            ignore_warnings: Ignore warnings when checking the file, only return errors.
            skip_spellcheck: Skip the spellcheck in rules and functions that utilise spell
              checking.
        """
        try:
            fp = FileParser()
            file_content = fp.parse_file_header(file_path, verbose=verbose)
        except Exception as err:
            if log_mode == "compact":
                print(f"{file_path} | ABORTED | FATAL | Cannot parse input file")
                sys.exit(1)
            else:
                raise Exception(err)

        ### Check for NCAS data files and gather specs ###
        # if template and specs are "default" values, check to see if
        # file is an ncas file (file name starts with NCAS instrument name or NCAS mentioned in Conventions)
        is_ncas_file = (
            "global_attrs" in dir(file_content) and (
                (
                    "Conventions" in file_content.global_attrs.keys() and
                    "ncas-" in file_content.global_attrs["Conventions"].lower()
                ) or (
                    "XMP-photoshop:Instructions" in file_content.global_attrs.keys() and
                    "national centre for atmospheric science" in file_content.global_attrs["XMP-photoshop:Instructions"].lower()
                )
            )
        )
        if (
            template == "auto"
            and specs == None
            and (is_ncas_file or file_path.split("/")[-1].startswith("ncas-"))
        ):
            template, specs = self._get_ncas_specs(
                file_path, file_content, log_mode=log_mode, verbose=verbose
            )

        if template == "off":
            tmpl = template
            tmpl_input = "OFF"
        else:
            tm = TemplateManager(
                auto_cache=auto_cache, verbose=verbose, log_mode=log_mode
            )
            tmpl = tm.get(file_path, template=template)
            tmpl_input = tmpl.inpt

        self._update_check_context(file_path, template)

        if verbose:
            if tmpl == "off":
                print("\n--- NOT USING Template CHECK!")
            else:
                print("\n--- Template dictionary:\n", tmpl.to_dict())

            print("\n--- Datafile dictionary:\n", file_content.to_dict())

        if log_mode == "compact":
            print(f"{file_path} | {tmpl_input} | ", end="")
        else:
            print(
                f"\nRunning with:\n\tTemplate: {tmpl_input}\n\tSpec Files: {specs}\n\tDatafile: {file_content.inpt}"
            )

        self._check_file(
            file_content,
            template=tmpl,
            mappings=mappings,
            extra_rules=extra_rules,
            specs=specs,
            ignore_attrs=ignore_attrs,
            log_mode=log_mode,
            ignore_warnings=ignore_warnings,
            skip_spellcheck=skip_spellcheck,
        )


class TemplateManager:
    """Finds and reads template file for checking data files.

    Attributes:
        auto_cache: Store the file in the template cache for future use as a template.
        verbose: Print additional information.
        log_mode: How the output should be printed. Options are "standard" (default) and
          "compact".
    """

    def __init__(
        self,
        auto_cache: bool = False,
        verbose: bool = False,
        log_mode: str = "standard"
    ):
        """Initialise the TemplateManager class.

        Args:
            auto_cache: Store the file in the template cache for future use as a template.
            verbose: Print additional information.
            log_mode: How the output should be printed. Options are "standard" (default)
              and "compact".
        """
        self.auto_cache = auto_cache
        self.verbose = verbose
        self.log_mode = log_mode

    def get(
        self,
        file_path: str,
        template: str = "auto",
    ) -> Union[cdl.CDLParser, image.ImageParser, pp.PPHeader, badc_csv.BADCCSVHeader, yml.YAMLFile]:
        """Get the template for checking a data file.

        If template is "auto", will try to find a suitable template based on the file
        to be checked. If template is a file path, will check if the file exists, and
        will use that file as the template.

        Args:
            file_path: Path to the file to check.
            template: Template to use for checking. Options are "auto" (default), or
              `<template file>`.

        Returns:
            Template object to use for checking the file.
        """
        if template == "auto":
            template = self._get_template_from_config(file_path)
        elif not os.path.isfile(template):
            if self.log_mode == "compact":
                print(
                    f"{file_path} | ABORTED | FATAL | Cannot find template file specified"
                )
                sys.exit(1)
            else:
                raise Exception(f"Cannot find specified template file: {template}")

        fp = FileParser()
        tmpl = fp.parse_file_header(
            template, auto_cache=self.auto_cache, verbose=self.verbose
        )
        return tmpl

    def _get_template_from_config(self, file_path: str) -> str:
        # Loop through datasets in config to find appropriate template (cached or in archive)
        dsets = [key.split(":")[1] for key in conf if key.startswith("dataset:")]

        for dset in dsets:
            config = conf[f"dataset:{dset}"]

            if "regex_path" in config and re.search(config["regex_path"], file_path):
                return self._get_template_by_dataset(file_path, config)
            elif "regex_file" in config and re.match(
                config["regex_file"], os.path.basename(file_path)
            ):
                return self._get_template_by_dataset(file_path, config)
        else:
            return self._get_template_from_cache(file_path)

    def _get_template_by_dataset(self, file_path: str, config: Dict[str, str]) -> str:
        if "template" in config:
            return config["template"]
        elif "template_cache" in config:
            return self._get_template_from_cache(file_path, config["template_cache"])
        else:
            raise Exception("No rule for finding the template")

    def _get_template_from_cache(
        self,
        file_path: str,
        template_cache: Optional[str] = None,
    ) -> str:
        if not template_cache:
            template_cache = conf["settings"]["default_template_cache_dir"]

        tmpl_base = get_file_base(file_path)

        if self.verbose:
            print(f"[INFO] Searching for exact match for: {tmpl_base}")
        matches = glob.glob(f"{template_cache}/{tmpl_base}_*.cdl")

        if matches:
            match = matches[0]
            if self.verbose:
                print(f"[INFO] Found exact match: {match}")
        else:
            if self.verbose:
                print("[WARNING] Failed to find exact match, so trying nearest...")
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
    """Parse input file into format for checksit.
    """

    def parse_file_header(
            self,
            file_path: str,
            auto_cache: bool = False,
            verbose: bool = False
        ) -> Union[cdl.CDLParser, image.ImageParser, pp.PPHeader, badc_csv.BADCCSVHeader, yml.YAMLFile]:
        """Parse the header of a file to determine the file type and read the content.

        Determines the correct reader to use based on the file extension, and then uses
        the read function in that reader to parse the file into a format that can be
        used for checksit checks. If auto_cache is True, will also write the data from
        the file to the template cache.

        Args:
            file_path: Path to the file to parse.
            auto_cache: Store the file in the template cache for future use as a template.
            verbose: Print additional information.
        """
        ext = extension(file_path)

        if ext in ("nc", "cdl"):
            reader = cdl
        elif ext in ("pp"):
            reader = pp
        elif ext in ("txt"):
            reader = badc_csv
        elif ext in ("yml"):
            reader = yml
        elif ext.lower() in IMAGE_EXTENSIONS:
            reader = image
        else:
            raise Exception(f"No known reader for file with extension: {ext}")

        content = reader.read(file_path, verbose=verbose)

        if auto_cache:
            base = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(
                conf["settings"]["default_template_cache_dir"], base
            )

            if reader == cdl:
                # Special case for NetCDF files using CDL
                with open(f"{output_path}.cdl", "w") as writer:
                    writer.write(content.cdl)
            else:
                # All others use YAML
                with open(f"{output_path}.yml", "w") as writer:
                    yaml.dump(
                        content.to_dict(),
                        writer,
                        Dumper=yaml.SafeDumper,
                        default_flow_style=False,
                        sort_keys=False,
                    )

        return content


def check_file(file_path: str, **kwargs) -> None:
    """Entry script for checking a file.

    Passes options through to the check_file function in the Checker class.

    Args:
        file_path: Path to the file to check.
        **kwargs: Keyword arguments to pass to the Checker class and
          Checker.check_file function.
    """
    ch = Checker(**kwargs)
    ch.check_file(file_path, **kwargs)
