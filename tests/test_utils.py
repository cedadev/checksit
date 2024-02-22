import checksit.utils as cu 
import pytest
import inspect


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


def test_string_to_list():
    # Test that the function correctly converts a string to a list
    s = "value1,value2,value3"
    lst = cu.string_to_list(s)
    assert lst == ["value1", "value2", "value3"]

    # Test that the function handles an empty string
    s = ""
    lst = cu.string_to_list(s)
    assert lst == [""]

    # Test that the function correctly handles a string with no commas
    s = "value1"
    lst = cu.string_to_list(s)
    assert lst == ["value1"]

    # Test that the function correctly handles a string with spaces
    s = "value1, value2, value3"
    lst = cu.string_to_list(s)
    assert lst == ["value1", " value2", " value3"]

    # Test that the function correctly handles a string with trailing comma
    s = "value1,value2,value3,"
    lst = cu.string_to_list(s)
    assert lst == ["value1", "value2", "value3", ""]

    # Test that the function correctly handles a string with leading comma
    s = ",value1,value2,value3"
    lst = cu.string_to_list(s)
    assert lst == ["", "value1", "value2", "value3"]


def test_extension():
    # Test that the function correctly identifies the extension of a file
    file_path = "/path/to/file.txt"
    ext = cu.extension(file_path)
    assert ext == "txt"

    # Test that the function correctly handles a file with multiple dots in the name
    file_path = "/path/to/file.name.with.multiple.dots.txt"
    ext = cu.extension(file_path)
    assert ext == "txt"

    # Test that the function correctly handles a file with a dot at the start of the name
    file_path = "/path/to/.file"
    ext = cu.extension(file_path)
    assert ext == "file"

    # Test that the function correctly handles a file with a dot at the end of the name
    file_path = "/path/to/file."
    ext = cu.extension(file_path)
    assert ext == ""

    # Test that the function correctly handles an empty string
    file_path = ""
    ext = cu.extension(file_path)
    assert ext == ""


def test_get_file_base():
    # Test that the function correctly gets the base of a file name with one underscore
    file_path = "/path/to/file_base.txt"
    base = cu.get_file_base(file_path)
    assert base == "file"

    # Test that the function correctly gets the base of a file name with multiple underscores
    file_path = "/path/to/file_base_part2_part3.txt"
    base = cu.get_file_base(file_path)
    assert base == "file_base_part2"

    # Test that the function correctly gets the base of a file name with an underscore at the start
    file_path = "/path/to/_file.txt"
    base = cu.get_file_base(file_path)
    assert base == ""

    # Test that the function correctly gets the base of a file name with an underscore at the end
    file_path = "/path/to/file_.txt"
    base = cu.get_file_base(file_path)
    assert base == "file"

    # Test that the function correctly handles an empty string
    file_path = ""
    base = cu.get_file_base(file_path)
    assert base == ""


def test_map_to_rule():
    # Test that the function correctly maps a function name with one underscore
    class TestClass:
        def test_func_one():
            pass
    rule = cu.map_to_rule(TestClass.test_func_one)
    assert rule == "test-func-one"

    # Test that the function correctly maps a function name with multiple underscores
    class TestClass:
        def test_func_multiple_underscores():
            pass
    rule = cu.map_to_rule(TestClass.test_func_multiple_underscores)
    assert rule == "test-func-multiple-underscores"

    # Test that the function correctly maps a function name with no underscores
    class TestClass:
        def testfuncnone():
            pass
    rule = cu.map_to_rule(TestClass.testfuncnone)
    assert rule == "testfuncnone"

    # Test that the function correctly maps a function name with an underscore at the start
    class TestClass:
        def _test_func_start():
            pass
    rule = cu.map_to_rule(TestClass._test_func_start)
    assert rule == "-test-func-start"

    # Test that the function correctly maps a function name with an underscore at the end
    class TestClass:
        def test_func_end_():
            pass
    rule = cu.map_to_rule(TestClass.test_func_end_)
    assert rule == "test-func-end-"


def test_is_undefined():
    # Test that the function correctly identifies None as undefined
    assert cu.is_undefined(None)

    # Test that the function correctly identifies an empty string as undefined
    assert cu.is_undefined("")

    # Test that the function correctly identifies an empty list as undefined
    assert cu.is_undefined([])

    # Test that the function correctly identifies an empty dictionary as undefined
    assert cu.is_undefined({})

    # Test that the function correctly identifies zero as not undefined
    assert not cu.is_undefined(0)

    # Test that the function correctly identifies a non-empty string as not undefined
    assert not cu.is_undefined("non-empty string")

    # Test that the function correctly identifies a non-empty list as not undefined
    assert not cu.is_undefined(["non-empty list"])

    # Test that the function correctly identifies a non-empty dictionary as not undefined
    assert not cu.is_undefined({"key": "value"})


def test_get_public_funcs():
    # Test that the function correctly gets the public functions of a module
    funcs = cu.get_public_funcs(cu)
    assert all([inspect.isfunction(func) for func in funcs])
    assert all([func.__name__[0] != "_" for func in funcs])
    assert "get_config" not in [func.__name__ for func in funcs]

    # Test that the function correctly handles a module with no public functions
    class TestModule:
        def _private_func():
            pass
    funcs = cu.get_public_funcs(TestModule)
    assert funcs == []

    # Test that the function correctly handles a module with only private functions
    class TestModule:
        def _private_func():
            pass
        def get_config():
            pass
    funcs = cu.get_public_funcs(TestModule)
    assert funcs == []

    # Test that the function correctly handles a module with both public and private functions
    class TestModule:
        def public_func():
            pass
        def _private_func():
            pass
    funcs = cu.get_public_funcs(TestModule)
    assert len(funcs) == 1
    assert funcs[0].__name__ == "public_func"