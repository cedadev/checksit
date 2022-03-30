import os


def string_to_dict(s):
    return dict([x.split("=") for x in s.split(",")])


def string_to_list(s):
    return s.split(",")


def extension(file_path):
    return file_path.split(".")[-1]


def get_file_base(file_path):
    parts = os.path.basename(file_path).split("_")[:-1]
    return "_".join(parts)
