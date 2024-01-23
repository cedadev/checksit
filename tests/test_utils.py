import checksit.utils as cu 
import pytest


def test_string_to_dict():
    # Test that the function correctly converts a string to a dictionary
    s = "key1=value1,key2=value2,key3=value3"
    d = cu.string_to_dict(s)
    assert d == {"key1": "value1", "key2": "value2", "key3": "value3"}

    # Test that the function handles an empty string
    s = ""
    with pytest.raises(ValueError):
        d = cu.string_to_dict(s)

    # Test that the function correctly handles a string with no equals signs
    s = "key1,key2,key3"
    with pytest.raises(ValueError):
        d = cu.string_to_dict(s)

    # Test that the function correctly handles a string with multiple equals signs in a pair
    s = "key1=value1=value1,key2=value2,key3=value3"
    with pytest.raises(ValueError):
        d = cu.string_to_dict(s)

    # Test that the function correctly handles a string with no commas
    s = "key1=value1"
    d = cu.string_to_dict(s)
    assert d == {"key1": "value1"}

    # Test that the function correctly handles a string with spaces
    s = "key1 = value1, key2 = value2, key3 = value3"
    d = cu.string_to_dict(s)
    assert d == {"key1 ": " value1", " key2 ": " value2", " key3 ": " value3"}