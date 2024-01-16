import os
import re
import pytest

from checksit.rules import rules as r
from checksit.rules.rule_funcs import match_file_name


def test_match_file_name():
    file_path = "happy_netcdf"
    value = "happy_NetCDF.nc"
    context = {"file_path": file_path}
    assert len(match_file_name(value, context)) == 1
    assert len(match_file_name(value, context, ["lowercase"])) == 1
    assert len(match_file_name(value, context, ["lowercase", "no_extension"])) == 0

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
    assert re.fullmatch(rules['number'], '-123.')
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