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
    
    PI_orcid_digits = value[-19:]
    PI_orcid_digits_only = PI_orcid_digits.replace("-", "")

    # Check that total the length is correct
    if len(value) != 37:    
        errors.append(f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX")
       
    # Check the start of the string (first 18 characters)
    elif (value[0:18] != orcid_string or
        
        # Check that the "-" are in the correct places
        value[22] != "-" or
        value[27] != "-" or
        value[32] != "-" or
        
        # Check that the last characters contain only "-" and digits
        not PI_orcid_digits_only.isdigit):

        errors.append(f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX")

    return errors


def list_of_names(value, context, extras=None, label=""):
    """
    A function to verify the names of people when a list of names may be provided
    """
    name_pattern = r'(.)+, (.)+ ?((.)+|((.)\.))'                # The format names should be written in

    warnings = []

    if type(value) == list:
        for i in value:
            if not re.fullmatch(name_pattern, i):
                warnings.append(f"{label} '{value}' should be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)> where appropriate")

    if type(value) == str:
        if not re.fullmatch(name_pattern, value):
            warnings.append(f"{label} '{value}' should be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)> where appropriate")

    return warnings


def headline(value, context, extras=None, label=""):
    """
    A function to verify the format of the Headline
    """
    warnings = []

    if len(value) > 150:
        warnings.append(f"{label} '{value}' should contain no more than one sentence")

    if value.count(".") >= 2:
        warnings.append(f"{label} '{value}' should contain no more than one sentence")

    if not value[0].isupper():
        warnings.append(f"{label} '{value}' should start with a capital letter")

    if len(value) < 10:
        warnings.append(f"{label} '{value}' should be at least 10 characters")

    return warnings


def title_check(value, context, extras=None, label=""):
    """
    A function to check if the title matches the system filename
    """
    errors = []

    if value != os.path.basename(context) :
        errors.append(f"{label} '{value}' must match the name of the file")

    return errors


def url_checker(value, context, extras=None, label=""):
    """
    A function to check if the url exists
    """
    warnings = []

    url = requests.get(value)   # get the url

    if url.status_code != 200:           # (200 means it exists and is up and reachable)
        warnings.append(f"{label} '{value}' is not a reachable url")

    return warnings


def relation_url_checker(value, context, extras=None, label=""):
    """
    A function to check if the url exists in the Relation field
    """
    errors = []
    
    if " " not in value:
        errors.append(f"{label} '{value}' should contain a space before the url")
    else:
        relation_url = value.partition(" ")[2]        # extract only the url part of the relation string
        url_checker(relation_url, context=None)

    return errors


def latitude(value, context, extras=None, label=""):
    """
    A function to check if the latitude is within -90 and +90
    """
    errors = []
    
    latitude = re.findall(r'[0-9]+', value)[0]
    int_latitude = int(latitude)

    if int_latitude > 90:
        errors.append(f"{label} '{value}' must be within -90 and +90 ")

    return errors


def longitude(value, context, extras=None, label=""):
    """
    A function to check if the longitude is within -180 and +180
    """
    errors = []
    
    longitude = re.findall(r'[0-9]+', value)[0]
    int_longitude = int(longitude)

    if int_longitude > 180:
        errors.append(f"{label} '{value}' must be within -180 and +180 ")

    return errors