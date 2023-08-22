import os
import re
from datetime import datetime
import requests

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
    

def validate_image_date_time(value, context, extras=None, label=""):
    """
    A function to indifity if a date-time value is compatible with the NCAS image standard
    """
    errors = []

    try:
        if value != datetime.strptime(value, "%Y:%m:%d %H:%M:%S").strftime("%Y:%m:%d %H:%M:%S") and value != datetime.strptime(value, "%Y:%m:%d #%H:%M:%S.%f").strftime("%Y:%m:%d %H:%M:%S.%f"):
            errors.append(f"{label} '{value}' needs to be of the format YYYY:MM:DD hh:mm:ss or YYYY:MM:DD hh:mm:ss.s")
    except ValueError:
        errors.append(f"{label} '{value}' needs to be of the format YYYY:MM:DD hh:mm:ss or YYYY:MM:DD hh:mm:ss.s")
    
    return errors


def validate_orcid_ID(value, context, extras=None, label=""):
    """
    A function to verify the format of an orcid ID
    """
    orcid_string = "https://orcid.org/"                                     # required format of start of the string
    
    errors = []

    # Check the start of the string (first 18 characters)
    if value[0:18] != orcid_string:
        errors.append(f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX")

    # Check that the "-" are in the correct places
    if value[22] != "-":
        errors.append(f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX")
    if value[27] != "-":
        errors.append(f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX")
    if value[32] != "-":
        errors.append(f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX")

    # Check that the last characters contain only "-" and digits
    PI_orcid_digits = value[-19:]
    PI_orcid_digits_only = PI_orcid_digits.replace("-", "")
    if not PI_orcid_digits_only.isdigit:
        errors.append(f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX")

    # Check that total the length is correct
    if len(value) != 37:
        errors.append(f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX")

    return errors


def list_of_names(value, context, extras=None, label=""):
    """
    A function to verify the names of people when a list of names may be provided
    """
    name_pattern = r'(\D+), (\D+) ((\D+)|([A-Z]\.))'                # The format names should be written in

    errors = []

    if type(value) == list:
        for i in value:
            if not re.fullmatch(name_pattern, i):
                errors.append(f"{label} '{value}' needs to be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)>")

    if type(value) == str:
        if not re.fullmatch(name_pattern, value):
            errors.append(f"{label} '{value}' needs to be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)>")

    return errors


def headline(value, context, extras=None, label=""):
    """
    A function to verify the format of the Headline
    """
    warnings = []

    if len(value) > 150:
        warnings.append(f"{label} '{value}' should contain no more than one sentence")

    if value.count(".") >= 2:
        warnings.append(f"{label} '{value}' should contain no more than one sentence")

    if not value[1].isupper():
        warnings.append(f"{label} '{value}' should start with a capital letter")

    if len(value) < 10:
        warnings.append(f"{label} '{value}' should be at least 10 characters")

    return warnings


# def title_check(value, context, extras=None, label=""):
#     """
#     A function to check if the title matches the system filename
#     """
#     errors = []
#     import pdb; pdb.set_trace()
#     if value != os.path.basename(inpt) : #????
#         errors.append(f"{label} '{value}' should match the system filename")

#     return errors


def url_checker(value, context, extras=None, label=""):
    """
    A function to check if the url exists
    """
    warnings = []

    url = requests.get(value)   # get the url

    if url.status_code != 200:           # (200 means it exists and is up and reachable)
        print(url.status_code)    #delete
        warnings.append(f"{label} '{value}' is not a reachable url")

    return warnings

def relation_url_checker(value, context, extras=None, label=""):
    """
    A function to check if the url exists in the Relation field
    """
    warnings = []
    
    relation_url = value.partition(" ")[2]        # extract only the url part of the relation string
    
    url = requests.get(relation_url)   # get the url

    if url.status_code != 200:           # (200 means it exists and is up and reachable)
        warnings.append(f"{label} '{value}' is not a reachable url")

    return warnings
