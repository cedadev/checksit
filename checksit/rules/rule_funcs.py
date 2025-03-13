"""Rule functions for checks.

This module contains functions that are used to check values against rules. Each
function takes a value and returns a list of errors if the value does not meet the
rule.
"""

import os
import re
from datetime import datetime
import requests
from urllib.request import urlopen
import numpy as np
import sys
from typing import List, Dict, Optional, Any, Union

from . import processors
from ..config import get_config

conf = get_config()
rule_splitter = conf["settings"].get("rule_splitter", "|")


def _preprocess(value: str, preprocessors: Optional[List[str]]) -> str:
    """Run value through preprocessors.

    Preprocess value by running it through preprocessor functions. Functions are
    defined in the processors module. Hyphens in the preprocessors (e.g. from specs)
    are replaced with underscores.

    Args:
        value: value to preprocess
        preprocessors: list of preprocessor functions to run

    Returns:
        Preprocessed value as string.
    """
    preprocessors = preprocessors or []

    for processor in preprocessors:
        value = getattr(processors, processor.replace("-", "_"))(value)

    return value


def match_file_name(
    value: str,
    context: Dict[str, str],
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check if value matches the file name.

    Check if the value matches the file name. The file name is extracted from the context
    dictionary, which should contain the file path as a value with the key 'file_path'.

    Args:
        value: value to check
        context: dictionary containing the file path
        extras: list of preprocessors to run on the value
        label: label to prepend to error message returned

    Returns:
        List of errors.
    """
    file_name = os.path.basename(context["file_path"])
    value = _preprocess(value, extras)
    errors = []

    if value != file_name:
        errors.append(f"{label} '{value}' does not match file name: '{file_name}'")

    return errors


def match_one_of(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check if value matches one of the options.

    Check if the value matches one of the options defined in the extras list. The
    options are separated by the rule splitter, which is defined in the checksit.ini
    file. The default rule splitter is '|'.

    Args:
        value: value to check
        extras: list with string of options to match, options separated by rule
          splitter (default '|')
        label: label to prepend to error message returned

    Returns:
        List with error string if no match found.
    """
    options = [x.strip() for x in extras[0].split(rule_splitter)]
    errors = []

    if value not in options:
        errors.append(f"{label} '{value}' must be one of: '{options}'")

    return errors


def match_one_or_more_of(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check one or more values for matches against options.

    Check if the value or values given can be found in the options list specified in
    `extras`. The options in `extras` are a string separated by the rule splitter, and
    the `value` is a string with values separated by commas. Checks if all values are
    found within the options.

    Args:
        value: value to check
        extras: list with string of options to match, options separated by rule
          splitter (default '|')
        label: label to prepend to error message returned

    Returns:
        List with error string if no match found.
    """

    def as_set(x, sep):
        return set([i.strip() for i in x.split(sep)])

    options = as_set(extras[0], rule_splitter)
    values = as_set(value, ",")

    errors = []

    if not values.issubset(options) or len(values) == 0:
        errors.append(f"{label} '{value}' must be one or more of: '{sorted(options)}'")

    return errors


def string_of_length(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check string is of a certain length.

    Check if the string is of a certain length. The length is defined in the extras
    list, which should contain the length as a string. If the length is followed by a
    '+' sign, the string must be at least that length. If the length is not followed by
    a '+', the string must be exactly that length.

    Args:
        value: value to check
        extras: list with length as string
        label: label to prepend to error message returned

    Returns:
        List with error string if length does not match.
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


def validate_image_date_time(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check value meets date and time format.

    Check if the value meets the date and time format that is expected for the
    NCAS-Image standard. The expected format is 'YYYY:MM:DD HH:MM:SS' or
    'YYYY:MM:DD HH:MM:SS.s'.

    Args:
        value: value to check
        label: label to prepend to error message returned

    Returns:
        List with error string if date and time format does not match.
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


def validate_orcid_ID(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check value meets ORCID URL format.

    Check if the value meets the ORCID URL format (i.e.
    https://orcid.org/XXXX-XXXX-XXXX-XXXX).

    Args:
        value: value to check
        label: label to prepend to error message returned

    Returns:
        List with error string if ORCID ID format does not match.
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


def list_of_names(
    value: Union[str, List[str]],
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check list of names matches expected pattern.

    Check if a given name or list of names matches the expected pattern. The pattern
    is <last name>, <first name> <middle initials(s)> or <last name>, <first name>
    <middle name(s)>. Designed for checks with the NCAS-Image standard.

    Args:
        value: name(s) to check
        label: label to prepend to error message returned

    Returns:
        List with error string if name format does not match.
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


def headline(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check value is valid for NCAS Image headline tag.

    Check if the value is valid for the NCAS Image headline tag. The headline should
    be a single sentence, starting with a capital letter, and should not exceed 150
    characters.

    Args:
        value: value to check
        label: label to prepend to error message returned

    Returns:
        List with error string if headline format does not match.
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


def title_check(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check if title matches the filename.

    For NCAS-Image standard, check if the value (from the title tag) matches the name
    of the file (given in the context).

    Args:
        value: value to check
        context: file path
        label: label to prepend to error message returned

    Returns:
        List with error string if title does not match file name.
    """
    errors = []

    if value != os.path.basename(context):
        errors.append(f"{label} '{value}' must match the name of the file")

    return errors


def url_checker(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check URL exists and is reachable.

    Args:
        value: URL to check
        label: label to prepend to error message returned

    Returns:
        List with error string if URL is not reachable.
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


def relation_url_checker(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = ""
) -> List[str]:
    """Check relation field is in the correct format and that the url exists.

    Designed for checking the Relation tag matches the expected format in the
    NCAS-Image standard, and the URL is reachable using the `url_checker` function.

    Args:
        value: value to check
        label: label to prepend to error message returned

    Returns:
        List with error string if Relation tag does not match expected format or URL is
          not reachable
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


def latitude(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check if the value is within -90 and +90

    Args:
        value: value to check
        label: label to prepend to error message returned

    Returns:
        List with error string if latitude is not within -90 and +90
    """
    errors = []

    latitude = re.findall(r"[0-9]+", value)
    int_latitude = int(latitude[0])
    dec_latitude = int(latitude[1])

    if int_latitude > 90 or (int_latitude == 90 and dec_latitude > 0):
        errors.append(f"{label} '{value}' must be within -90 and +90 ")

    return errors


def longitude(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check if the value is within -180 and +180

    Args:
        value: value to check
        label: label to prepend to error message returned

    Returns:
        List with error string if longitude is not within -180 and +180
    """
    errors = []

    longitude = re.findall(r"[0-9]+", value)
    int_longitude = int(longitude[0])
    dec_longitude = int(longitude[1])

    if int_longitude > 180 or (int_longitude == 180 and dec_longitude > 0):
        errors.append(f"{label} '{value}' must be within -180 and +180 ")

    return errors


def ceda_platform(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check if the platform is in the CEDA catalogue API

    Attempt to find the platform in the CEDA catalogue API, at
    `http://api.catalogue.ceda.ac.uk/api/v2/identifiers.json/?url={value}`.

    Args:
        value: platform value to check
        label: label to prepend to error message returned

    Returns:
        List with error string if platform is not in the CEDA catalogue
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


def ncas_platform(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check if the platform is in the NCAS platform list

    Attempt to find the platform in the NCAS platform list, in the latest release of
    `https://github.com/ncasuk/ncas-data-platform-vocabs`.

    Args:
        value: platform value to check
        label: label to prepend to error message returned

    Returns:
        List with error string if platform is not in the NCAS platform list
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


def check_qc_flags(
    value: Any,
    context: str,
    extras: Optional[List[str]] = None,
    label: str = ""
) -> List[str]:
    """Check QC flag values and meanings meet NCAS-General requirements

    Checks the QC flag values and meanings. The flag values must be an array or tuple
    of byte values, with at least two values, starting with 0 and 1. The flag meanings
    must be space separated and the first two must start with 'not_used' and
    'good_data'. The number of flag values must equal the number of flag meanings.

    Args:
        value: flag values, as defined in the netCDF file
        context: flag meanings, as defined in the netCDF file
        label: label to prepend to error message returned

    Returns:
        List with error string if QC flag values and meanings do not meet requirements
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


def check_utc_date_iso_format(
    value: str,
    context: Any,
    extras: Optional[List[str]] = None,
    label: str = "",
) -> List[str]:
    """Check date given is in ISO 8601 format and in UTC

    Args:
        value: date string to check
        label: label to prepend to error message returned

    Returns:
        List with error string if date string does not meet
    """
    errors = []

    original_value = value
    if sys.version_info < (3,11): # python datetime changed its recognition of ISO format from 3.11 onward
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        elif re.fullmatch(r"(\+|-)\d{4}", value[-5:]):
            value = f"{value[:-2]}:{value[-2:]}"
    try:
        dt = datetime.fromisoformat(value)
        if (dt.utcoffset() != None) and (dt.utcoffset().total_seconds() != 0):
            errors.append(f"{label} Date string '{original_value}' not in UTC.")
    except ValueError:
        errors.append(f"{label} Date string '{original_value}' not in ISO 8601 format.")
    except:
        raise

    return errors


def allow_proposed(value, context, extras=None, label=""):
    """Check for proposed_standard_name if standard_name not given

    Used in CFRadial and the NCAS-Radar standard, this function takes the value of both
    the `standard_name` attribute and the `proposed_standard_name` attribute (if they
    exist) and compares each to the expected value, as given in `extras`.

    Args:
        value: value of the standard_name attribute
        context: value of the proposed_standard_name attribute
        extras: list of expected values
        label: label to prepend to error message returned

    Returns:
        List with error string if neither value matches the expected value
    """
    errors = []

    if extras != None and isinstance(extras, list):
        extras = extras[0]

    if value != extras and context != extras:
        errors.append(f"{label} does not contain standard_name or proposed_standard_name with value '{extras}'")

    return errors


