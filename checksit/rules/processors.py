import os


def lowercase(value):
    return value.lower()


def uppercase(value):
    return value.upper()


def no_extension(value):
    return os.path.splitext(value)[0]