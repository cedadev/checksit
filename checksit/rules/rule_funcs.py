import os

from . import processors

# Decorator to run preprocessors on content

def _preprocess(value, preprocessors):
    preprocessors = preprocessors or []

    for processor in preprocessors:
        value = getattr(processors, processor.replace("-", "_"))(value)

    return value


def match_file_name(value, context, preprocessors=None):
    file_name = os.path.basename(context["file_path"])
    value = _preprocess(value, preprocessors)
    errors = []

    if value != file_name:
        errors.append(f"'{value}' does not match file name: '{file_name}'")

    return errors


