import os
import inspect

UNDEFINED = "UNDEFINED"


def string_to_dict(s):
    return dict([x.split("=") for x in s.split(",")])


def string_to_list(s):
    return s.split(",")


def extension(file_path):
    return file_path.split(".")[-1]


def get_file_base(file_path):
    parts = os.path.basename(file_path).split("_")[:-1]
    return "_".join(parts)


def map_to_rule(func):
    return func.__name__.replace("_", "-")


def get_public_funcs(module):
    items = [item for item in dir(module) if item not in ["get_config"]]
    funcs = []

    for item in items:
        if item[0] != "_":
            prop = getattr(module, item)
            if inspect.isfunction(prop):
                funcs.append(prop)

    return funcs


def is_undefined(x):
    return not x and x != 0
