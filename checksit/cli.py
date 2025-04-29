"""Console script for checksit."""

__author__ = """Ag Stephens"""
__contact__ = "ag.stephens@stfc.ac.uk"
__copyright__ = "Copyright 2022 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import click
import os
from typing import Optional, List, Tuple

from .utils import string_to_dict, string_to_list
from .check import check_file
from .summary import summarise
from . import describer
from . import specs


@click.group()
def main():
    """Console script for checker."""
    return 0


@main.command()
@click.argument("file_paths", nargs=-1)
@click.option("-m", "--mappings", default=None)
@click.option("-r", "--rules", default=None)
@click.option("-s", "--specs", default=None)
@click.option("-i", "--ignore-attrs", default=None)
@click.option("-G", "--ignore-all-globals", default=False)
@click.option("-D", "--ignore-all-dimensions", default=False)
@click.option("-V", "--ignore-all-variables", default=False)
@click.option("-A", "--ignore-all-variable-attrs", default=False)
@click.option("--auto-cache/--no-auto-cache", default=False)
@click.option("-l", "--log-mode", default="standard")
@click.option("-v", "--verbose/--no-verbose", default=False)
@click.option("-t", "--template", default="auto")
@click.option("-w", "--ignore-warnings", is_flag=True)
@click.option("-p", "--skip-spellcheck", is_flag=True)
def check_files(
    file_paths: Tuple[str,...],
    mappings: Optional[str] = None,
    rules: Optional[str] = None,
    specs: Optional[str] = None,
    ignore_attrs: Optional[str] = None,
    ignore_all_globals: bool = False,
    ignore_all_dimensions: bool = False,
    ignore_all_variables: bool = False,
    ignore_all_variable_attrs: bool = False,
    auto_cache: bool = False,
    log_mode: str = "standard",
    verbose: bool = False,
    template: str = "auto",
    ignore_warnings: bool = False,
    skip_spellcheck: bool = False,
):
    """CLI call to check a number of files against a set of rules, specs or templates.

    Reads options from the command line and calls the check_file function to check the
    compliance of each file against a set of rules, specs or templates. If any of
    `mappings`, `rules`, `specs` or `ignore_attrs` are provided as a string, they will
    be converted to the appropriate data type.

    Args:
        file_paths: Paths to the files to check.
        mappings: Map variable names between name used in file and name in template.
          Format should be `<template variable name>=<file variable name>`. Multiple
          mappings should be separated by a comma.
        rules: Specific rules to use to check items. Format should be
          `<what to check>=<rule type>:<function/check>[:<extras>[:<extras>...]]`.
          Multiple rules should be separated by a comma.
        specs: Specific specs to use to check items. Format should be `<spec file>` or
          `<spec folder>/<spec file>`. File location and path relative to the specs
          folder in the checksit repository. Multiple specs should be separated by a
          comma.
        ignore_attrs: Attributes to ignore when checking variables. Multiple attributes
          should be separated by a comma.
        ignore_all_globals: Not implemented yet.
        ignore_all_dimensions: Not implemented yet.
        ignore_all_variables: Not implemented yet.
        ignore_all_variable_attrs: Not implemented yet.
        auto_cache: Store the file in the template cache for future use as a template.
        log_mode: How the output should be printed. Options are "standard" (default)
          and "compact".
        verbose: Print additional information to the console.
        template: Template to use for checking. Options are "auto" (default), "off", or
          `<template file>`. File location is relative to the top level of the checksit
          repository.
        ignore_warnings: Ignore warnings when checking the file, only return errors.
        skip_spellcheck: Skip the spellcheck in rules and functions that utilise spell
          checking.
    """

    if (
        ignore_all_globals
        or ignore_all_dimensions
        or ignore_all_variables
        or ignore_all_variable_attrs
    ):
        raise Exception("Options not implemented yet!!!!!")

    if mappings is not None:
        mappings = string_to_dict(mappings)

    if rules is not None:
        rules = string_to_dict(rules)

    if specs is not None:
        specs = string_to_list(specs)

    if ignore_attrs is not None:
        ignore_attrs = string_to_list(ignore_attrs)

    for file_path in file_paths:
        check_file(
            file_path,
            template=template,
            mappings=mappings,
            extra_rules=rules,
            specs=specs,
            ignore_attrs=ignore_attrs,
            auto_cache=auto_cache,
            verbose=verbose,
            log_mode=log_mode,
            ignore_warnings=ignore_warnings,
            skip_spellcheck=skip_spellcheck,
        )


@main.command()
@click.argument("file_path")
@click.option("-m", "--mappings", default=None)
@click.option("-r", "--rules", default=None)
@click.option("-s", "--specs", default=None)
@click.option("-i", "--ignore-attrs", default=None)
@click.option("-G", "--ignore-all-globals", default=False)
@click.option("-D", "--ignore-all-dimensions", default=False)
@click.option("-V", "--ignore-all-variables", default=False)
@click.option("-A", "--ignore-all-variable-attrs", default=False)
@click.option("--auto-cache/--no-auto-cache", default=False)
@click.option("-l", "--log-mode", default="standard")
@click.option("-v", "--verbose/--no-verbose", default=False)
@click.option("-t", "--template", default="auto")
@click.option("-w", "--ignore-warnings", is_flag=True)
@click.option("-p", "--skip-spellcheck", is_flag=True)
def check(
    file_path: str,
    mappings: Optional[str] = None,
    rules: Optional[str] = None,
    specs: Optional[str] = None,
    ignore_attrs: Optional[str] = None,
    ignore_all_globals: bool = False,
    ignore_all_dimensions: bool = False,
    ignore_all_variables: bool = False,
    ignore_all_variable_attrs: bool = False,
    auto_cache: bool = False,
    log_mode: str = "standard",
    verbose: bool = False,
    template: str = "auto",
    ignore_warnings: bool = False,
    skip_spellcheck: bool = False,
):
    """CLI call to check a file against a set of rules, specs or templates.

    Reads options from the command line and calls the check_file function to check the
    compliance of a file against a set of rules, specs or templates. If any of
    `mappings`, `rules`, `specs` or `ignore_attrs` are provided as a string, they will
    be converted to the appropriate data type.

    Args:
        file_path: Path to the file to check.
        mappings: Map variable names between name used in file and name in template.
          Format should be `<template variable name>=<file variable name>`. Multiple
          mappings should be separated by a comma.
        rules: Specific rules to use to check items. Format should be
          `<what to check>=<rule type>:<function/check>[:<extras>[:<extras>...]]`.
          Multiple rules should be separated by a comma.
        specs: Specific specs to use to check items. Format should be `<spec file>` or
          `<spec folder>/<spec file>`. File location and path relative to the specs
          folder in the checksit repository. Multiple specs should be separated by a
          comma.
        ignore_attrs: Attributes to ignore when checking variables. Multiple attributes
          should be separated by a comma.
        ignore_all_globals: Not implemented yet.
        ignore_all_dimensions: Not implemented yet.
        ignore_all_variables: Not implemented yet.
        ignore_all_variable_attrs: Not implemented yet.
        auto_cache: Store the file in the template cache for future use as a template.
        log_mode: How the output should be printed. Options are "standard" (default)
          and "compact".
        verbose: Print additional information to the console.
        template: Template to use for checking. Options are "auto" (default), "off", or
          `<template file>`. File location is relative to the top level of the checksit
          repository.
        ignore_warnings: Ignore warnings when checking the file, only return errors.
        skip_spellcheck: Skip the spellcheck in rules and functions that utilise spell
          checking.
    """

    if (
        ignore_all_globals
        or ignore_all_dimensions
        or ignore_all_variables
        or ignore_all_variable_attrs
    ):
        raise Exception("Options not implemented yet!!!!!")

    if mappings is not None:
        mappings = string_to_dict(mappings)

    if rules is not None:
        rules = string_to_dict(rules)

    if specs is not None:
        specs = string_to_list(specs)

    if ignore_attrs is not None:
        ignore_attrs = string_to_list(ignore_attrs)

    check_file(
        file_path,
        template=template,
        mappings=mappings,
        extra_rules=rules,
        specs=specs,
        ignore_attrs=ignore_attrs,
        auto_cache=auto_cache,
        verbose=verbose,
        log_mode=log_mode,
        ignore_warnings=ignore_warnings,
        skip_spellcheck=skip_spellcheck,
    )


@main.command()
@click.argument("log_files", nargs=-1, default=None)
@click.option("-d", "--log-directory", default=None)
@click.option("--show-files/--no-show-files", default=False)
@click.option("-x", "--exclude", default=None)
@click.option("-e", "--exclude-file", default=None)
@click.option("--verbose/--no-verbose", default=False)
def summary(
    log_files: Optional[List[str]] = None,
    log_directory: Optional[str] = None,
    show_files: bool = False,
    exclude: Optional[str] = None,
    exclude_file: Optional[str] = None,
    verbose: bool = False,
):
    """CLI call to summarise the contents of log files.

    Reads options from the command line and calls the summarise function to summarise
    log files output from the check function when "log_mode" is set to "compact". Can
    take either a list of log files, or a directory which contains log files. If the
    `exclude` option is provided, it will be converted to a list.

    Args:
        log_files: List of log files to summarise.
        log_directory: Directory where the log files are located.
        show_files: Print the files in which the errors occur.
        exclude: Patterns to exclude from the summary. Multiple patterns should be
          separated by a comma.
        exclude_file: File containing patterns to exclude from the summary. Each pattern
          should be on a new line.
        verbose: Print additional information to the console.
    """

    if exclude is not None:
        exclude = string_to_list(exclude)
    else:
        exclude = []

    if exclude_file:
        if not os.path.isfile(exclude_file):
            raise Exception(f"'--exclude-file' does not point to a valid file")

        with open(exclude_file) as exfile:
            exclude.extend(
                [
                    exclude_pattern
                    for exclude_pattern in exfile
                    if exclude_pattern.strip()
                ]
            )

    summarise(
        log_files,
        log_directory=log_directory,
        show_files=show_files,
        exclude=exclude,
        verbose=verbose,
    )


@main.command()
@click.argument("check_ids", nargs=-1, default=None)
@click.option("--verbose/--no-verbose", default=False)
def describe(check_ids: Optional[List[str]] = None, verbose: bool = False):
    """CLI call to describe rules.

    Reads options from the command line and calls the describe function to print the
    docstring of a given rule or set of rules. If no rule given, docstrings for all
    rules are printed.

    Args:
        check_ids: List of rules to describe.
        verbose: Print additional information to the console.
    """
    describer.describe(check_ids, verbose=verbose)


@main.command()
@click.argument("spec_ids", nargs=-1, default=None)
def show_specs(spec_ids: Optional[List[str]] = None):
    """CLI call to show details of specs.

    Reads options from the command line and calls the show_specs function to print the
    contents of a given spec or set of specs. If no spec given, contents of specs
    within the `specs/groups` folder in the checksit repository are printed.

    Args:
        spec_ids: List of specs to show.
    """
    specs.show_specs(spec_ids)


if __name__ == "__main__":
    main()
