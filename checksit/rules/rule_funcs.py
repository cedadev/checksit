import os
import re

from . import processors
from ..config import get_config

conf = get_config()
rule_splitter = conf["settings"].get("rule_splitter", "|")


def _preprocess(value, preprocessors):
    preprocessors = preprocessors or []

    for processor in preprocessors:
        value = getattr(processors, processor.replace("-", "_"))(value)

    return value


def match_file_name(value, context, extras=None, label=""):
    """
    Matches file name to value...

    Example usage:
     - match-file-name:lowercase:no-extension
     - match-file-name:uppercase
     - match-file-name

    """
    file_name = os.path.basename(context["file_path"])
    value = _preprocess(value, extras)
    errors = []

    if value != file_name:
        errors.append(f"{label} '{value}' does not match file name: '{file_name}'")

    return errors


def match_one_of(value, context, extras=None, label=""):
    """
    Matches only one of...
    """
    options = [x.strip() for x in extras[0].split(rule_splitter)]
    errors = []

    if value not in options:
        errors.append(f"{label} '{value}' must be one of: '{options}'")

    return errors


def match_one_or_more_of(value, context, extras=None, label=""):
    """
    Matches one of more of...
    """
    def as_set(x, sep): return set([i.strip() for i in x.split(sep)])
    options = as_set(extras[0], rule_splitter)
    values = as_set(value, ",")

    errors = []

    if not values.issubset(options) or len(values) == 0:
        errors.append(f"{label} '{value}' must be one or more of: '{sorted(options)}'")

    return errors


def string_of_length(value, context, extras=None, label=""):
    """
    Matches string of length...
    """
    spec = extras[0]
    min_length = int(re.match("^(\d+)\+?", spec).groups()[0])

    errors = []

    if spec.endswith("+"):
        if len(value) < min_length:
            errors.append(f"{label} '{value}' must be at least {min_length} characters")
    elif len(value) != min_length:
        errors.append(f"{label} '{value}' must be exactly {min_length} characters")

    return errors
