import os

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
    file_name = os.path.basename(context["file_path"])
    value = _preprocess(value, extras)
    errors = []

    if value != file_name:
        errors.append(f"{label} '{value}' does not match file name: '{file_name}'")

    return errors


def match_one_of(value, context, extras=None, label=""):
    options = [x.strip() for x in extras[0].split(rule_splitter)]
    errors = []

    if value not in options:
        errors.append(f"{label} '{value}' must be one of: '{options}'")

    return errors


def match_one_or_more_of(value, context, extras=None, label=""):
    def as_set(x, sep): return set([i.strip() for i in x.split(sep)])
    options = as_set(extras[0], rule_splitter)
    values = as_set(value, ",")

    errors = []

    if not values.issubset(options) or len(values) == 0:
        errors.append(f"{label} '{value}' must be one or more of: '{sorted(options)}'")

    return errors
