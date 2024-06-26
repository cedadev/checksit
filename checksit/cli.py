"""Console script for checksit."""

__author__ = """Ag Stephens"""
__contact__ = "ag.stephens@stfc.ac.uk"
__copyright__ = "Copyright 2022 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import click
import os

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
    file_path,
    mappings=None,
    rules=None,
    specs=None,
    ignore_attrs=None,
    ignore_all_globals=False,
    ignore_all_dimensions=False,
    ignore_all_variables=False,
    ignore_all_variable_attrs=False,
    auto_cache=False,
    log_mode="standard",
    verbose=False,
    template="auto",
    ignore_warnings=False,
    skip_spellcheck=False,
):

    if (
        ignore_all_globals
        or ignore_all_dimensions
        or ignore_all_variables
        or ignore_all_variable_attrs
    ):
        raise Exception("Options not implemented yet!!!!!")

    if mappings:
        mappings = string_to_dict(mappings)

    if rules:
        rules = string_to_dict(rules)

    if specs:
        specs = string_to_list(specs)

    if ignore_attrs:
        ignore_attrs = string_to_list(ignore_attrs)

    return check_file(
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
    log_files=None,
    log_directory=None,
    show_files=False,
    exclude=None,
    exclude_file=None,
    verbose=False,
):

    if exclude:
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

    return summarise(
        log_files,
        log_directory=log_directory,
        show_files=show_files,
        exclude=exclude,
        verbose=verbose,
    )


@main.command()
@click.argument("check_ids", nargs=-1, default=None)
@click.option("--verbose/--no-verbose", default=False)
def describe(check_ids=None, verbose=False):
    return describer.describe(check_ids, verbose=verbose)


@main.command()
@click.argument("spec_ids", nargs=-1, default=None)
@click.option("--verbose/--no-verbose", default=False)
def show_specs(spec_ids=None, verbose=False):
    return specs.show_specs(spec_ids, verbose=verbose)


if __name__ == "__main__":
    main()
