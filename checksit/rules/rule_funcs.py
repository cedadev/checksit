import os
import re
from datetime import datetime
import requests
from urllib.request import urlopen
import numpy as np
import sys

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
    value matches one of options defined in extras
    default rule splitter is '|' and defined in checksit.ini file
    """
    options = [x.strip() for x in extras[0].split(rule_splitter)]
    errors = []

    if value not in options:
        errors.append(f"{label} '{value}' must be one of: '{options}'")

    return errors


def match_one_or_more_of(value, context, extras=None, label=""):
    """
    String value or list value must match one of more of list given in extras
    """

    def as_set(x, sep):
        return set([i.strip() for i in x.split(sep)])

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
    min_length = int(re.match(r"^(\d+)\+?", spec).groups()[0])

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

    match = False
    for f in ["%Y:%m:%d %H:%M:%S", "%Y:%m:%d %H:%M:%S.%f"]:
        if match == False:
            try:
                match = value == datetime.strptime(value, f).strftime(f)
            except ValueError:
                pass

    if not match:
        errors.append(
            f"{label} '{value}' needs to be of the format YYYY:MM:DD hh:mm:ss or YYYY:MM:DD hh:mm:ss.s"
        )

    return errors


def validate_orcid_ID(value, context, extras=None, label=""):
    """
    A function to verify the format of an orcid ID
    """
    orcid_string = "https://orcid.org/"  # required format of start of the string

    errors = []

    PI_orcid_digits = value[-19:]
    PI_orcid_digits_only = PI_orcid_digits.replace("-", "")

    # Check that total the length is correct
    if len(value) != 37:
        errors.append(
            f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"
        )

    # Check the start of the string (first 18 characters)
    elif (
        value[0:18] != orcid_string
        or
        # Check that the "-" are in the correct places
        value[22] != "-"
        or value[27] != "-"
        or value[32] != "-"
        or
        # Check that the last characters contain only "-" and digits (plus 'X' for last digit)
        not (
            PI_orcid_digits_only.isdigit()
            or (
                PI_orcid_digits_only[0:15].isdigit() and PI_orcid_digits_only[15] == "X"
            )
        )
    ):

        errors.append(
            f"{label} '{value}' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"
        )

    return errors


def list_of_names(value, context, extras=None, label=""):
    """
    A function to verify the names of people when a list of names may be provided
    """
    name_pattern = (
        r"(.)+, (.)+ ?((.)+|((.)\.))"  # The format names should be written in
    )
    character_name_pattern = r"[A-Za-z_À-ÿ\-\'\ \.\,]+"

    warnings = []

    if type(value) == list:
        for i in value:
            if not re.fullmatch(name_pattern, i):
                warnings.append(
                    f"{label} '{value}' should be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)> where appropriate"
                )
            if not re.fullmatch(character_name_pattern, i):
                warnings.append(
                    f"{label} '{value}' - please use characters A-Z, a-z, À-ÿ where appropriate"
                )

    if type(value) == str:
        if not re.fullmatch(name_pattern, value):
            warnings.append(
                f"{label} '{value}' should be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)> where appropriate"
            )
        if not re.fullmatch(character_name_pattern, value):
            warnings.append(
                f"{label} '{value}' - please use characters A-Z, a-z, À-ÿ where appropriate"
            )

    return warnings


def headline(value, context, extras=None, label=""):
    """
    A function to verify the format of the Headline
    """
    warnings = []

    if value == "":
        warnings.append(f"{label} '{value}' should not be empty")

    else:
        if len(value) > 150:
            warnings.append(
                f"{label} '{value}' should contain no more than one sentence"
            )

        if value.count(".") >= 2:
            warnings.append(
                f"{label} '{value}' should contain no more than one sentence"
            )

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

    if value != os.path.basename(context):
        errors.append(f"{label} '{value}' must match the name of the file")

    return errors


def url_checker(value, context, extras=None, label=""):
    """
    A function to check if the url exists
    """
    warnings = []

    try:
        url = urlopen(value)
    except:
        warnings.append(f"{label} '{value}' is not a reachable url")
    else:
        if url.getcode() != 200:  # (200 means it exists and is up and reachable)
            warnings.append(f"{label} '{value}' is not a reachable url")
    finally:
        return warnings


def relation_url_checker(value, context, extras=None, label=""):
    """
    A function to check if Relation field is in the correct format, and that the url exists
    """
    errors = []

    if " " not in value:
        errors.append(f"{label} '{value}' should contain a space before the url")
    else:
        relation_url = value.partition(" ")[
            2
        ]  # extract only the url part of the relation string
        if url_checker(relation_url, context, extras, label) != []:
            errors.extend(
                url_checker(relation_url, context, extras, label)
            )  # check the url exists using the url_checker() function defined above

    return errors


def latitude(value, context, extras=None, label=""):
    """
    A function to check if the latitude is within -90 and +90
    """
    errors = []

    latitude = re.findall(r"[0-9]+", value)
    int_latitude = int(latitude[0])
    dec_latitude = int(latitude[1])

    if int_latitude > 90 or (int_latitude == 90 and dec_latitude > 0):
        errors.append(f"{label} '{value}' must be within -90 and +90 ")

    return errors


def longitude(value, context, extras=None, label=""):
    """
    A function to check if the longitude is within -180 and +180
    """
    errors = []

    longitude = re.findall(r"[0-9]+", value)
    int_longitude = int(longitude[0])
    dec_longitude = int(longitude[1])

    if int_longitude > 180 or (int_longitude == 180 and dec_longitude > 0):
        errors.append(f"{label} '{value}' must be within -180 and +180 ")

    return errors


def ceda_platform(value, context, extras=None, label=""):
    """
    A function to check if the platform is in the CEDA catalogue API
    """
    errors = []
    api_result = requests.get(
        f"http://api.catalogue.ceda.ac.uk/api/v2/identifiers.json/?url={value}"
    )
    if (len(api_result.json()["results"]) == 1) and (
        api_result.json()["results"][0]["relatedTo"]["short_code"] == "plat"
    ):
        legit_platform = True
    else:
        legit_platform = False

    if not legit_platform:
        errors.append(
            f"{label} '{value}' is not a valid platform in the CEDA catalogue"
        )

    return errors


def ncas_platform(value, context, extras=None, label=""):
    """
    A function to check if the platform is in the NCAS platform list
    """
    errors = []

    latest_version = requests.get(
        "https://github.com/ncasuk/ncas-data-platform-vocabs/releases/latest"
    ).url.split("/")[-1]

    result = requests.get(
        f"https://raw.githubusercontent.com/ncasuk/ncas-data-platform-vocabs/{latest_version}/AMF_CVs/AMF_platform.json"
    )
    ncas_platforms = result.json()["platform"].keys()

    if value not in ncas_platforms:
        errors.append(f"{label} '{value}' is not a valid NCAS platform")

    return errors


def check_qc_flags(value, context, extras=None, label=""):
    """
    A function to check flag_values and flag_meanings
    value - flag_values
    context - flag_meanings
    """
    errors = []

    meanings = context.split(" ")

    # check flag_values are correctly formatted (should be array of bytes)
    if not (isinstance(value, np.ndarray) or isinstance(value, tuple)):
        errors.append(
            f"{label} QC flag_values must be an array or tuple of byte values, not '{type(value)}'."
        )

    # check there are at least two values and they start with 0 and 1
    if not len(value) >= 2:
        errors.append(f"{label} There must be at least two QC flag values.")
    elif not (np.all(value[:2] == [0, 1]) or np.all(value[:2] == (0, 1))):
        errors.append(f"{label} First two QC flag_values must be '[0, 1]'.")

    # check there are at least two meanings and the first two are correct
    if not len(meanings) >= 2:
        errors.append(
            f"{label} There must be at least two QC flag meanings (space separated)."
        )
    elif not np.all(meanings[:2] == ["not_used", "good_data"]):
        errors.append(
            f"{label} First two QC flag_meanings must be 'not_used' and 'good_data'."
        )

    # check number of values is same as number of meanings
    if not len(value) == len(meanings):
        errors.append(
            f"{label} Number of flag_values must equal number of flag_meanings."
        )

    return errors


def check_utc_date_iso_format(value, context, extras=None, label=""):
    """
    Check date given is in ISO 8601 format and in UTC
    value - date string
    """
    errors = []

    if sys.version_info < (3,11): # python datetime changed its recognition of ISO format from 3.11 onward
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        elif re.fullmatch(r"(\+|-)\d{4}", value[-5:]):
            value = f"{value[:-2]}:{value[-2:]}"
    try:
        dt = datetime.fromisoformat(value)
        if (dt.utcoffset() != None) and (dt.utcoffset().total_seconds() != 0):
            errors.append(f"{label} Date string '{value}' not in UTC.")
    except ValueError:
        errors.append(f"{label} Date string '{value}' not in ISO 8601 format.")
    except:
        raise

    return errors


def allow_proposed(value, context, extras=None, label=""):
    """
    Check for proposed_standard_name if standard_name not given
    value - value of the standard_name attribute
    context - value of the proposed_standard_name attribute
    extras - value to match
    """
    errors = []

    if extras != None and isinstance(extras, list):
        extras = extras[0]

    if value != extras and context != extras:
        errors.append(f"{label} does not contain standard_name or proposed_standard_name with value '{extras}'")

    return errors


