import os
import re
import pytest
from numbers import Number

from checksit.rules import rules as r
from checksit.rules.rule_funcs import match_file_name, string_of_length, match_one_of, match_one_or_more_of, validate_image_date_time, validate_orcid_ID, list_of_names, headline, title_check, url_checker, relation_url_checker, latitude, longitude

# rule_funcs.py
def test_match_file_name():
    file_path = "happy_netcdf"
    value = "happy_NetCDF.nc"
    context = {"file_path": file_path}
    assert len(match_file_name(value, context)) == 1
    assert len(match_file_name(value, context, ["lowercase"])) == 1
    assert len(match_file_name(value, context, ["lowercase", "no_extension"])) == 0


def test_string_of_length():
    # Test that the function correctly handles strings of the minimum length
    assert string_of_length('abc', {}, ['3'], 'Test') == []
    assert string_of_length('abcd', {}, ['3+'], 'Test') == []

    # Test that the function correctly handles strings shorter than the minimum length
    assert string_of_length('ab', {}, ['3'], 'Test') == ["Test 'ab' must be exactly 3 characters"]
    assert string_of_length('ab', {}, ['3+'], 'Test') == ["Test 'ab' must be at least 3 characters"]

    # Test that the function correctly handles strings longer than the minimum length
    assert string_of_length('abcd', {}, ['3'], 'Test') == ["Test 'abcd' must be exactly 3 characters"]
    assert string_of_length('abcd', {}, ['3+'], 'Test') == []

    # Test that the function correctly handles empty strings
    assert string_of_length('', {}, ['0'], 'Test') == []
    assert string_of_length('', {}, ['1'], 'Test') == ["Test '' must be exactly 1 characters"]
    assert string_of_length('', {}, ['1+'], 'Test') == ["Test '' must be at least 1 characters"]


def test_match_one_of():
    # Test that the function correctly handles valid inputs
    assert match_one_of('apple', {}, ['apple|banana|orange'], 'Test') == []

    # Test that the function correctly handles invalid inputs
    assert match_one_of('kiwi', {}, ['apple|banana|orange'], 'Test') == ["Test 'kiwi' must be one of: '['apple', 'banana', 'orange']'"]

    # Test that the function correctly handles empty strings
    assert match_one_of('', {}, ['apple|banana|orange'], 'Test') == ["Test '' must be one of: '['apple', 'banana', 'orange']'"]


def test_match_one_or_more_of():
    # Test that the function correctly handles valid inputs
    assert match_one_or_more_of('apple,banana', {}, ['apple|banana|orange'], 'Test') == []
    assert match_one_or_more_of('apple', {}, ['apple|banana|orange'], 'Test') == []

    # Test that the function correctly handles invalid inputs
    assert match_one_or_more_of('apple,kiwi', {}, ['apple|banana|orange'], 'Test') == ["Test 'apple,kiwi' must be one or more of: '['apple', 'banana', 'orange']'"]
    assert match_one_or_more_of('kiwi', {}, ['apple|banana|orange'], 'Test') == ["Test 'kiwi' must be one or more of: '['apple', 'banana', 'orange']'"]

    # Test that the function correctly handles empty strings
    assert match_one_or_more_of('', {}, ['apple|banana|orange'], 'Test') == ["Test '' must be one or more of: '['apple', 'banana', 'orange']'"]


def test_validate_image_date_time():
    # Test that the function correctly handles valid date-time strings
    assert validate_image_date_time('2022:01:01 12:00:00', {}, label = 'Test') == []
    assert validate_image_date_time('2022:01:01 12:00:00.000000', {}, label = 'Test') == []

    # Test that the function correctly handles invalid date-time strings
    assert validate_image_date_time('2022-01-01 12:00:00', {}, label = 'Test') == ["Test '2022-01-01 12:00:00' needs to be of the format YYYY:MM:DD hh:mm:ss or YYYY:MM:DD hh:mm:ss.s"]
    assert validate_image_date_time('2022:01:01 12:00', {}, label = 'Test') == ["Test '2022:01:01 12:00' needs to be of the format YYYY:MM:DD hh:mm:ss or YYYY:MM:DD hh:mm:ss.s"]
    assert validate_image_date_time('2022:01:01', {}, label = 'Test') == ["Test '2022:01:01' needs to be of the format YYYY:MM:DD hh:mm:ss or YYYY:MM:DD hh:mm:ss.s"]
    assert validate_image_date_time('2022:01:01 12:00:00.00', {}, label = 'Test') == ["Test '2022:01:01 12:00:00.00' needs to be of the format YYYY:MM:DD hh:mm:ss or YYYY:MM:DD hh:mm:ss.s"]

    # Test that the function correctly handles empty strings
    assert validate_image_date_time('', {}, label = 'Test') == ["Test '' needs to be of the format YYYY:MM:DD hh:mm:ss or YYYY:MM:DD hh:mm:ss.s"]


def test_validate_orcid_ID():
    # Test that the function correctly handles valid ORCID IDs
    assert validate_orcid_ID('https://orcid.org/0000-0002-1825-0097', {}, label='Test') == []
    assert validate_orcid_ID('https://orcid.org/1234-5678-9012-3456', {}, label='Test') == []

    # Test that the function correctly handles ORCID IDs with incorrect lengths
    assert validate_orcid_ID('https://orcid.org/0000-0002-1825-009', {}, label='Test') == ["Test 'https://orcid.org/0000-0002-1825-009' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"]
    assert validate_orcid_ID('https://orcid.org/1234-5678-9012-34567', {}, label='Test') == ["Test 'https://orcid.org/1234-5678-9012-34567' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"]

    # Test that the function correctly handles ORCID IDs with incorrect formats
    assert validate_orcid_ID('https://orcid.org/0000-0002-1825-009Z', {}, label='Test') == ["Test 'https://orcid.org/0000-0002-1825-009Z' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"]
    assert validate_orcid_ID('https://orcid.org/1234-5678-9012-345X', {}, label='Test') == ["Test 'https://orcid.org/1234-5678-9012-345X' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"]
    assert validate_orcid_ID('https://orcid.org/1234-5678-9012-3456-', {}, label='Test') == ["Test 'https://orcid.org/1234-5678-9012-3456-' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"]
    assert validate_orcid_ID('https://orcid.org/1234-5678-9012-3456X', {}, label='Test') == ["Test 'https://orcid.org/1234-5678-9012-3456X' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"]

    # Test that the function correctly handles empty strings
    assert validate_orcid_ID('', {}, label='Test') == ["Test '' needs to be of the format https://orcid.org/XXXX-XXXX-XXXX-XXXX"]


def test_list_of_names():
    # Test that the function correctly handles valid names
    assert list_of_names('Doe, John', {}, label='Test') == []
    assert list_of_names('Doe, John J.', {}, label='Test') == []
    assert list_of_names(['Doe, John', 'Smith, Jane'], {}, label='Test') == []

    # Test that the function correctly handles names with incorrect formats
    assert list_of_names('John Doe', {}, label='Test') == ["Test 'John Doe' should be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)> where appropriate"]
    assert list_of_names('Doe John', {}, label='Test') == ["Test 'Doe John' should be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)> where appropriate"]
    assert list_of_names(['Doe, John', 'Jane Smith'], {}, label='Test') == ["Test '['Doe, John', 'Jane Smith']' should be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)> where appropriate"]

    # Test that the function correctly handles names with invalid characters
    assert list_of_names('Doe, J0hn', {}, label='Test') == ["Test 'Doe, J0hn' - please use characters A-Z, a-z, À-ÿ where appropriate"]
    assert list_of_names('Doe, John!', {}, label='Test') == ["Test 'Doe, John!' - please use characters A-Z, a-z, À-ÿ where appropriate"]
    assert list_of_names(['Doe, John', 'Smith, J@ne'], {}, label='Test') == ["Test '['Doe, John', 'Smith, J@ne']' - please use characters A-Z, a-z, À-ÿ where appropriate"]

    # Test that the function correctly handles empty strings
    assert list_of_names('', {}, label='Test') == ["Test '' should be of the format <last name>, <first name> <middle initials(s)> or <last name>, <first name> <middle name(s)> where appropriate", "Test '' - please use characters A-Z, a-z, À-ÿ where appropriate"]
    assert list_of_names([], {}, label='Test') == []


def test_headline():
    # Test that the function correctly handles valid headlines
    assert headline('This is a valid headline.', {}, label='Test') == []
    assert headline('This headline is exactly 150 characters long ' + 'a' * 105, {}, label='Test') == []
    assert headline('This headline is exactly 10 characters.', {}, label='Test') == []

    # Test that the function correctly handles headlines longer than 150 characters
    assert headline('This headline is longer than 150 characters.' + 'a' * 120, {}, label='Test') == ["Test 'This headline is longer than 150 characters." + "a" * 120 + "' should contain no more than one sentence"]

    # Test that the function correctly handles headlines with more than one sentence
    assert headline('This is a headline. It has two sentences.', {}, label='Test') == ["Test 'This is a headline. It has two sentences.' should contain no more than one sentence"]

    # Test that the function correctly handles headlines that do not start with a capital letter
    assert headline('this headline does not start with a capital letter.', {}, label='Test') == ["Test 'this headline does not start with a capital letter.' should start with a capital letter"]

    # Test that the function correctly handles headlines shorter than 10 characters
    assert headline('Too short', {}, label='Test') == ["Test 'Too short' should be at least 10 characters"]

    # Test that the function correctly handles empty strings
    assert headline('', {}, label='Test') == ["Test '' should not be empty"]


def test_title_check():
    # Test that the function correctly handles titles that match the filename
    assert title_check('happy_netcdf', "/path/to/file/happy_netcdf", label='Test') == []
    assert title_check('happy_NetCDF.nc', "/path/to/file/happy_NetCDF.nc", label='Test') == []

    # Test that the function correctly handles titles that do not match the filename
    assert title_check('sad_netcdf', "/path/to/file/happy_netcdf", label='Test') == ["Test 'sad_netcdf' must match the name of the file"]
    assert title_check('happy_NetCDF.nc', "/path/to/file/sad_NetCDF.nc", label='Test') == ["Test 'happy_NetCDF.nc' must match the name of the file"]

    # Test that the function correctly handles empty titles
    assert title_check('', "/path/to/file/happy_netcdf", label='Test') == ["Test '' must match the name of the file"]


def test_url_checker():
    # Test that the function correctly handles a reachable URL
    assert url_checker("https://www.example.com", {}, label="Test") == []

    # Test that the function correctly handles an unreachable URL
    assert url_checker("https://www.nonexistenturl.com", {}, label="Test") == ["Test 'https://www.nonexistenturl.com' is not a reachable url"]

    # Test that the function correctly handles an existing but unreachable URL
    assert url_checker("https://www.example.com/nonexistentpage", {}, label="Test") == ["Test 'https://www.example.com/nonexistentpage' is not a reachable url"]

    # Test that the function correctly handles an empty URL
    assert url_checker("", {}, label="Test") == ["Test '' is not a reachable url"]


def test_relation_url_checker():
    # Test that the function correctly handles valid inputs
    assert relation_url_checker('relation https://example.com', {}, label='Test') == []

    # Test that the function correctly handles inputs without a space
    assert relation_url_checker('relationhttps://example.com', {}, label='Test') == ["Test 'relationhttps://example.com' should contain a space before the url"]

    # Test that the function correctly handles inputs with an invalid URL
    assert relation_url_checker('relation https://', {}, label='Test') == ["Test 'https://' is not a reachable url"]

    # Test that the function correctly handles empty strings
    assert relation_url_checker('', {}, label='Test') == ["Test '' should contain a space before the url"]


def test_latitude():
    # Test that the function correctly handles valid latitudes
    assert latitude('45.1234', {}, label='Test') == []
    assert latitude('-90.0000', {}, label='Test') == []
    assert latitude('90.0000', {}, label='Test') == []

    # Test that the function correctly handles invalid latitudes
    assert latitude('90.0001', {}, label='Test') == ["Test '90.0001' must be within -90 and +90 "]
    assert latitude('-90.0001', {}, label='Test') == ["Test '-90.0001' must be within -90 and +90 "]
    assert latitude('100.0000', {}, label='Test') == ["Test '100.0000' must be within -90 and +90 "]


def test_longitude():
    # Test that the function correctly handles valid longitudes
    assert longitude('45.1234', {}, label='Test') == []
    assert longitude('-180.0000', {}, label='Test') == []
    assert longitude('180.0000', {}, label='Test') == []

    # Test that the function correctly handles invalid longitudes
    assert longitude('180.0001', {}, label='Test') == ["Test '180.0001' must be within -180 and +180 "]
    assert longitude('-180.0001', {}, label='Test') == ["Test '-180.0001' must be within -180 and +180 "]
    assert longitude('200.0000', {}, label='Test') == ["Test '200.0000' must be within -180 and +180 "]


# rules.py
def _test_type(_type, value):
    return r.check(f"type-rule:{_type}", value)

def test_type_rules():
    tt = _test_type

    _type = "number"
    for value in 3.4, -4:
        assert tt(_type, value) == ([], [])
        print('sarah test', tt(_type, value))

    for value in "3", "3.4", ["hi"]:
        assert tt(_type, value) != ([], [])

    _type = "float"
    for value in [3.4]:
        assert tt(_type, value) == ([], [])

    for value in "3", 3, ["hi"]:
        assert tt(_type, value) != ([], [])

    _type = "integer"
    for value in [3]:
        assert tt(_type, value) == ([], [])

    for value in "3", 3.5, ["hi"]:
        assert tt(_type, value) != ([], [])

    _type = "string"
    for value in "3", "hi":
        assert tt(_type, value) == ([], [])

    for value in 3, 4.5, ["hi"]:
        assert tt(_type, value) != ([], [])

# static regex rule tests
@pytest.fixture
def rules():
    return r.static_regex_rules

def test_integer_rule(rules):
    assert re.fullmatch(rules['integer'], '123')
    assert re.fullmatch(rules['integer'], '-123')
    assert not re.fullmatch(rules['integer'], '123.45')
    assert not re.fullmatch(rules['integer'], 'abc')
    assert not re.fullmatch(rules['integer'], '')

def test_valid_email_rule(rules):
    assert re.fullmatch(rules['valid-email'], 'test@example.com')
    assert re.fullmatch(rules['valid-email'], 'test.test@example.com')
    assert not re.fullmatch(rules['valid-email'], 'test@example')
    assert not re.fullmatch(rules['valid-email'], 'test@.com')
    assert not re.fullmatch(rules['valid-email'], 'test@com')

def test_valid_url_rule(rules):
    assert re.fullmatch(rules['valid-url'], 'https://example.com')
    assert re.fullmatch(rules['valid-url'], 'http://example.com')
    assert not re.fullmatch(rules['valid-url'], 'htp://example.com')
    assert not re.fullmatch(rules['valid-url'], 'https:/example.com')
    assert not re.fullmatch(rules['valid-url'], 'https://example')

def test_valid_url_or_na_rule(rules):
    assert re.fullmatch(rules['valid-url-or-na'], 'https://example.com')
    assert re.fullmatch(rules['valid-url-or-na'], 'http://example.com')
    assert re.fullmatch(rules['valid-url-or-na'], 'N/A')
    assert not re.fullmatch(rules['valid-url-or-na'], 'htp://example.com')
    assert not re.fullmatch(rules['valid-url-or-na'], 'https:/example.com')
    assert not re.fullmatch(rules['valid-url-or-na'], 'nan')

def test_match_vN_M_rule(rules):
    assert re.fullmatch(rules['match:vN.M'], 'v1.0')
    assert re.fullmatch(rules['match:vN.M'], 'v2.1')
    assert not re.fullmatch(rules['match:vN.M'], 'v10')
    assert not re.fullmatch(rules['match:vN.M'], 'v1.01')
    assert not re.fullmatch(rules['match:vN.M'], 'v.1.0')

def test_datetime_rule(rules):
    assert re.fullmatch(rules['datetime'], '2022-01-01T00:00:00')
    assert re.fullmatch(rules['datetime'], '2022-01-01T00:00:00.123')
    assert not re.fullmatch(rules['datetime'], '2022-01-01 00:00:00')
    assert not re.fullmatch(rules['datetime'], '2022-01-01T00:00')
    assert not re.fullmatch(rules['datetime'], '2022-01-01')

def test_datetime_or_na_rule(rules):
    assert re.fullmatch(rules['datetime-or-na'], '2022-01-01T00:00:00')
    assert re.fullmatch(rules['datetime-or-na'], '2022-01-01T00:00:00.123')
    assert re.fullmatch(rules['datetime-or-na'], 'N/A')
    assert re.fullmatch(rules['datetime-or-na'], 'NA')
    assert re.fullmatch(rules['datetime-or-na'], 'Not Applicable')
    assert not re.fullmatch(rules['datetime-or-na'], '2022-01-01 00:00:00')
    assert not re.fullmatch(rules['datetime-or-na'], '2022-01-01T00:00')
    assert not re.fullmatch(rules['datetime-or-na'], '2022-01-01')

def test_number_rule(rules):
    assert re.fullmatch(rules['number'], '123.45')
    assert re.fullmatch(rules['number'], '-123.45')
    assert not re.fullmatch(rules['number'], '-123.')
    assert not re.fullmatch(rules['number'], 'abc')
    assert not re.fullmatch(rules['number'], '')
    assert not re.fullmatch(rules['number'], '123.45abc')

def test_location_rule(rules):
    assert re.fullmatch(rules['location'], 'City, Country')
    assert re.fullmatch(rules['location'], 'City, Country, State')
    assert not re.fullmatch(rules['location'], 'City Country')
    assert not re.fullmatch(rules['location'], 'City,')
    assert not re.fullmatch(rules['location'], ',Country')

def test_latitude_image_rule(rules):
    assert re.fullmatch(rules['latitude-image'], '+12.345678')
    assert re.fullmatch(rules['latitude-image'], '-12.345678')
    assert not re.fullmatch(rules['latitude-image'], '123.45')
    assert not re.fullmatch(rules['latitude-image'], '+123.456789')
    assert not re.fullmatch(rules['latitude-image'], '-123.456789')

def test_longitude_image_rule(rules):
    assert re.fullmatch(rules['longitude-image'], '+123.45678')
    assert re.fullmatch(rules['longitude-image'], '-123.45678')
    assert not re.fullmatch(rules['longitude-image'], '123')
    assert not re.fullmatch(rules['longitude-image'], '+1234.56789')
    assert not re.fullmatch(rules['longitude-image'], '-1234.56789')

def test_title_rule(rules):
    assert re.fullmatch(rules['title'], 'prefix_suffix_2022_v1.0.png')
    assert re.fullmatch(rules['title'], 'prefix_suffix_2022_v1.0.jpg')
    assert not re.fullmatch(rules['title'], 'prefix_suffix_2022_v1.0.txt')
    assert not re.fullmatch(rules['title'], 'prefix_suffix_2022_v1.png')
    assert not re.fullmatch(rules['title'], 'prefix_suffix_2022_v1.0')

def test_title_data_product_rule(rules):
    assert re.fullmatch(rules['title-data-product'], 'prefix_suffix_2022_plot_v1.0.png')
    assert re.fullmatch(rules['title-data-product'], 'prefix_suffix_2022_photo_v1.0.jpg')
    assert not re.fullmatch(rules['title-data-product'], 'prefix_suffix_2022_v1.0.txt')
    assert not re.fullmatch(rules['title-data-product'], 'prefix_suffix_2022_plot_v1.png')
    assert not re.fullmatch(rules['title-data-product'], 'prefix_suffix_2022_plot_v1.0')

def test_name_format_rule(rules):
    assert re.fullmatch(rules['name-format'], 'Last, First M.')
    assert re.fullmatch(rules['name-format'], 'Last, First')
    assert not re.fullmatch(rules['name-format'], 'First Last')
    assert not re.fullmatch(rules['name-format'], 'Last, First, M.')
    assert not re.fullmatch(rules['name-format'], 'Last First M.')

def test_name_characters_rule(rules):
    assert re.fullmatch(rules['name-characters'], 'John_Doe')
    assert re.fullmatch(rules['name-characters'], 'John-Doe')
    assert not re.fullmatch(rules['name-characters'], 'John Doe!')
    assert not re.fullmatch(rules['name-characters'], 'John Doe@')
    assert not re.fullmatch(rules['name-characters'], 'John Doe#')

def test_altitude_image_warning_rule(rules):
    assert re.fullmatch(rules['altitude-image-warning'], '123 m')
    assert re.fullmatch(rules['altitude-image-warning'], '-123 m')
    assert not re.fullmatch(rules['altitude-image-warning'], '123.45 m')
    assert not re.fullmatch(rules['altitude-image-warning'], '123')
    assert not re.fullmatch(rules['altitude-image-warning'], '123m')

def test_altitude_image_rule(rules):
    assert re.fullmatch(rules['altitude-image'], '123.45 m')
    assert re.fullmatch(rules['altitude-image'], '-123.45 m')
    assert not re.fullmatch(rules['altitude-image'], '123')
    assert not re.fullmatch(rules['altitude-image'], '123.45')
    assert not re.fullmatch(rules['altitude-image'], '123.45m')

def test_ncas_email_rule(rules):
    assert re.fullmatch(rules['ncas-email'], 'test@ncas.ac.uk')
    assert re.fullmatch(rules['ncas-email'], 'test.test@ncas.ac.uk')
    assert not re.fullmatch(rules['ncas-email'], 'test@example.com')
    assert not re.fullmatch(rules['ncas-email'], 'test@ncas.com')
    assert not re.fullmatch(rules['ncas-email'], 'test@ncas.ac')

def test_map_type_rule():
    assert r._map_type_rule('number') == Number
    assert r._map_type_rule('integer') == int
    assert r._map_type_rule('int') == int
    assert r._map_type_rule('float') == float
    assert r._map_type_rule('string') == str
    assert r._map_type_rule('str') == str
    with pytest.raises(KeyError):
        r._map_type_rule('nonexistent')