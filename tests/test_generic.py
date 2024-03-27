import checksit.generic as cg
import numpy as np


def test_spelling_mistake_checks():
    # Test that the function correctly generates all one-delete mistakes
    assert len(cg.one_spelling_mistake("abc")) == 195
    assert len(cg.one_spelling_mistake("abcdefg")) == 507
    assert len(cg.two_spelling_mistakes("abc")) == 16306
    assert len(cg.two_spelling_mistakes("abcdefg")) == 118314


def test_search_close_match():
    # Test that the function correctly finds a close match
    assert cg.search_close_match('abc', ['abd', 'abe', 'abf']) == "'abd' was found in this file, should this be 'abc'?"

    # Test that the function correctly handles no close matches
    assert cg.search_close_match('abc', ['def', 'ghi', 'jkl']) == ""

    # Test that the function correctly handles case sensitivity
    assert cg.search_close_match('abc', ['ABD', 'ABE', 'ABF']) == "'ABD' was found in this file, should this be 'abc'?"

    # Test that the function correctly handles an empty search_in list
    assert cg.search_close_match('abc', []) == ""

    # Test that the function correctly handles an empty search_for string
    assert cg.search_close_match('', ['abd', 'abe', 'abf']) == ""


def test_check_var_attrs():
    # Test that the function correctly identifies missing attributes
    dct = {
        "variables": {
            "var1": {"long_name": "Variable 1", "units": "m"},
            "var2": {"long_name": "Variable 2"}
        }
    }
    defined_attrs = ["long_name", "units"]
    errors, warnings = cg.check_var_attrs(dct, defined_attrs)
    assert errors == ["[variable**************:var2]: Attribute 'units' must have a valid definition."]
    assert warnings == []

    # Test that the function correctly handles empty attributes
    dct = {
        "variables": {
            "var1": {"long_name": "", "units": "m"},
            "var2": {"long_name": "Variable 2", "units": ""}
        }
    }
    errors, warnings = cg.check_var_attrs(dct, defined_attrs)
    assert errors == ["[variable**************:var1]: Attribute 'long_name' must have a valid definition.", "[variable**************:var2]: Attribute 'units' must have a valid definition."]
    assert warnings == []

    # Test that the function correctly handles variables with all attributes defined
    dct = {
        "variables": {
            "var1": {"long_name": "Variable 1", "units": "m"},
            "var2": {"long_name": "Variable 2", "units": "kg"}
        }
    }
    errors, warnings = cg.check_var_attrs(dct, defined_attrs)
    assert errors == []
    assert warnings == []

    # Test that the function correctly handles an empty dct
    dct = {"variables": {}}
    errors, warnings = cg.check_var_attrs(dct, defined_attrs)
    assert errors == []
    assert warnings == []


def test_check_global_attrs():
    # Test that the function correctly identifies missing attributes
    dct = {
        "global_attributes": {
            "attr1": "",
            "attr2": "value2",
            "attr3": "inst1"
        },
        "inpt": "filename"
    }
    defined_attrs = ["attr2", "attr4"]
    errors, warnings = cg.check_global_attrs(dct, defined_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:**************:attr4]: Attribute 'attr4' does not exist. "]
    assert warnings == []

    # Test that the function correctly handles empty attributes
    defined_attrs = ["attr1", "attr2"]
    errors, warnings = cg.check_global_attrs(dct, defined_attrs)
    assert errors == ["[global-attributes:**************:attr1]: No value defined for attribute 'attr1'."]
    assert warnings == []

    # Test that the function correctly handles defined_attrs when all attributes are defined
    defined_attrs = ["attr2", "attr3"]
    errors, warnings = cg.check_global_attrs(dct, defined_attrs)
    assert errors == []
    assert warnings == []

    # Test function handles non-existent attributes with vocab checks correctly
    vocab_attrs = {
        "attr4": "__vocabs__:tests/test_products:test_products"
    }
    errors, warnings = cg.check_global_attrs(dct, vocab_attrs = vocab_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:**************:attr4]: Attribute 'attr4' does not exist. "]
    assert warnings == []

    # Test function handles undefined attributes with vocab checks correctly
    vocab_attrs = {
        "attr1": "__vocabs__:tests/test_platforms:test_platforms:__all__"
    }
    errors, warnings = cg.check_global_attrs(dct, vocab_attrs = vocab_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:**************:attr1]: No value defined for attribute 'attr1'."]
    assert warnings == []

    # Test function handles incorrect values with vocab checks correctly
    vocab_attrs = {
        "attr2": "__vocabs__:tests/test_platforms:test_platforms:__all__"
    }
    errors, warnings = cg.check_global_attrs(dct, vocab_attrs = vocab_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:******:attr2]*** 'value2' not in vocab options: ['plat1', 'plat2'] (using: '__vocabs__:tests/test_platforms:test_platforms:__all__')"]
    assert warnings == []

    # Test function handles correct values with vocab checks correctly
    vocab_attrs = {
        "attr3": "__vocabs__:tests/test_instruments:test_instruments:__all__"
    }
    errors, warnings = cg.check_global_attrs(dct, vocab_attrs = vocab_attrs, skip_spellcheck=True)
    assert errors == []
    assert warnings == []

    # Test function handles non-existent attributes with regex checks correctly
    regex_attrs = {
        "attr4": r"\d{4}-\d{2}-\d{2}"
    }
    errors, warnings = cg.check_global_attrs(dct, regex_attrs = regex_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:**************:attr4]: Attribute 'attr4' does not exist. "]
    assert warnings == []

    # Test function handles undefined attributes with regex checks correctly
    regex_attrs = {
        "attr1": r"\d{4}-\d{2}-\d{2}"
    }
    errors, warnings = cg.check_global_attrs(dct, regex_attrs = regex_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:**************:attr1]: No value defined for attribute 'attr1'."]
    assert warnings == []

    # Test function handles incorrect values with regex checks correctly
    regex_attrs = {
        "attr2": r"\d{4}-\d{2}-\d{2}"
    }
    errors, warnings = cg.check_global_attrs(dct, regex_attrs = regex_attrs, skip_spellcheck=True)
    assert errors == [r"[global-attributes:******:attr2]: 'value2' does not match regex pattern '\d{4}-\d{2}-\d{2}'."]
    assert warnings == []

    # Test function handles correct values with regex checks correctly
    regex_attrs = {
        "attr3": r"inst\d"
    }
    errors, warnings = cg.check_global_attrs(dct, regex_attrs = regex_attrs, skip_spellcheck=True)
    assert errors == []
    assert warnings == []

    # Test function handles non-existent attributes with rules checks correctly
    rules_attrs = {
        "attr4": "rule-func:string-of-length:5"
    }
    errors, warnings = cg.check_global_attrs(dct, rules_attrs = rules_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:**************:attr4]: Attribute 'attr4' does not exist. "]
    assert warnings == []

    # Test function handles undefined attributes with rules checks correctly
    rules_attrs = {
        "attr1": "rule-func:string-of-length:5"
    }
    errors, warnings = cg.check_global_attrs(dct, rules_attrs = rules_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:**************:attr1]: No value defined for attribute 'attr1'."]
    assert warnings == []

    # Test function handles incorrect values with rules checks correctly
    rules_attrs = {
        "attr2": "rule-func:string-of-length:5"
    }
    errors, warnings = cg.check_global_attrs(dct, rules_attrs = rules_attrs, skip_spellcheck=True)
    assert errors == ["[global-attributes:******:attr2]*** 'value2' must be exactly 5 characters"]
    assert warnings == []

    # Test function handles correct values with rules checks correctly
    rules_attrs = {
        "attr3": "rule-func:string-of-length:5"
    }
    errors, warnings = cg.check_global_attrs(dct, rules_attrs = rules_attrs, skip_spellcheck=True)
    assert errors == []
    assert warnings == []

    # Test that the function correctly handles an empty dct
    dct = {"global_attributes": {}}
    defined_attrs = ["attr1", "attr2"]
    errors, warnings = cg.check_global_attrs(dct, defined_attrs)
    assert errors == ["[global-attributes:**************:attr1]: Attribute 'attr1' does not exist. ", "[global-attributes:**************:attr2]: Attribute 'attr2' does not exist. "]
    assert warnings == []


def test_check_var_exists():
    # Test that the function correctly identifies missing variables
    dct = {
        "variables": {
            "var1": {"long_name": "Variable 1", "units": "m"},
            "var2": {"long_name": "Variable 2", "units": "kg"}
        }
    }
    variables = ["var1", "var3"]
    errors, warnings = cg.check_var_exists(dct, variables, skip_spellcheck=True)
    assert errors == ["[variable**************:var3]: Does not exist in file. "]
    assert warnings == []

    # Test that the function correctly handles optional variables
    variables = ["var1", "var3:__OPTIONAL__"]
    errors, warnings = cg.check_var_exists(dct, variables, skip_spellcheck=True)
    assert errors == []
    assert warnings == ["[variable**************:var3]: Optional variable does not exist in file. "]

    # Test that the function correctly handles variables that exist
    variables = ["var1", "var2"]
    errors, warnings = cg.check_var_exists(dct, variables)
    assert errors == []
    assert warnings == []

    # Test that the function correctly handles an empty dct
    dct = {"variables": {}}
    variables = ["var1", "var2"]
    errors, warnings = cg.check_var_exists(dct, variables)
    assert errors == ["[variable**************:var1]: Does not exist in file. ", "[variable**************:var2]: Does not exist in file. "]
    assert warnings == []


def test_check_dim_exists():
    # Test that the function correctly identifies missing dimensions
    dct = {
        "dimensions": {
            "dim1": {"long_name": "Dimension 1", "units": "m"},
            "dim2": {"long_name": "Dimension 2", "units": "kg"}
        }
    }
    dimensions = ["dim1", "dim3"]
    errors, warnings = cg.check_dim_exists(dct, dimensions, skip_spellcheck=True)
    assert errors == ["[dimension**************:dim3]: Does not exist in file. "]
    assert warnings == []

    # Test that the function correctly handles optional dimensions
    dimensions = ["dim1", "dim3:__OPTIONAL__"]
    errors, warnings = cg.check_dim_exists(dct, dimensions, skip_spellcheck=True)
    assert errors == []
    assert warnings == ["[dimension**************:dim3]: Optional dimension does not exist in file. "]

    # Test that the function correctly handles dimensions that exist
    dimensions = ["dim1", "dim2"]
    errors, warnings = cg.check_dim_exists(dct, dimensions)
    assert errors == []
    assert warnings == []

    # Test that the function correctly handles an empty dct
    dct = {"dimensions": {}}
    dimensions = ["dim1", "dim2"]
    errors, warnings = cg.check_dim_exists(dct, dimensions)
    assert errors == ["[dimension**************:dim1]: Does not exist in file. ", "[dimension**************:dim2]: Does not exist in file. "]
    assert warnings == []


def test_check_var():
    # Test that the function correctly identifies missing variables
    dct = {
        "variables": {
            "var1": {"long_name": "Variable 1", "units": "m", "flag_values": np.array([0,1,2], dtype=np.int8)},
            "var2": {"long_name": "Variable 2", "units": "kg"},
            "var4": {"flag_values": "0b, 1b, 2b"}
        }
    }
    variable = "var3"
    defined_attrs = ["long_name:Variable 3", "units:s"]
    errors, warnings = cg.check_var(dct, variable, defined_attrs, skip_spellcheck=True)
    assert errors == ["[variable**************:var3]: Variable does not exist in file. "]
    assert warnings == []

    # Test that the function correctly handles optional variables
    variable = "var3:__OPTIONAL__"
    errors, warnings = cg.check_var(dct, variable, defined_attrs, skip_spellcheck=True)
    assert errors == []
    assert warnings == ["[variable**************:var3]: Optional variable does not exist in file. "]

    # Test that the function correctly handles variables that exist
    variable = "var1:__OPTIONAL__"
    defined_attrs = ["long_name:Variable 1", "units:m"]
    errors, warnings = cg.check_var(dct, variable, defined_attrs)
    assert errors == []
    assert warnings == []

    # Test that the function correctly identifies missing attributes
    variable = "var2"
    defined_attrs = ["long_name:Variable 2", "units:kg", "attr3:value 3"]
    errors, warnings = cg.check_var(dct, variable, defined_attrs, skip_spellcheck=True)
    assert errors == ["[variable**************:var2]: Attribute 'attr3' does not exist. "]
    assert warnings == []

    variable = "var2:__OPTIONAL__"
    defined_attrs = ["long_name:Variable 2", "units:kg", "attr3:value 3"]
    errors, warnings = cg.check_var(dct, variable, defined_attrs, skip_spellcheck=True)
    assert errors == ["[variable**************:var2]: Attribute 'attr3' does not exist. "]
    assert warnings == []

    # Test that the function correctly identifies incorrect attributes
    variable = "var2"
    defined_attrs = ["long_name:Variable 2", "units:s"]
    errors, warnings = cg.check_var(dct, variable, defined_attrs, skip_spellcheck=True)
    assert errors == ["[variable**************:var2]: Attribute 'units' must have definition 's', not 'kg'."]
    assert warnings == []

    variable = "var2:__OPTIONAL__"
    defined_attrs = ["long_name:Variable 2", "units:s"]
    errors, warnings = cg.check_var(dct, variable, defined_attrs, skip_spellcheck=True)
    assert errors == ["[variable**************:var2]: Attribute 'units' must have definition 's', not 'kg'."]
    assert warnings == []

    # Test that the function correctly handles badly formatted flag_values
    variable = "var4:__OPTIONAL__"
    defined_attrs = ["flag_values:0b, 1b, 2b"]
    errors, warnings = cg.check_var(dct, variable, defined_attrs, skip_spellcheck=True)
    assert errors == ["[variable**************:var4]: Attribute 'flag_values' must have definition '[0 1 2]', not '0b, 1b, 2b'."]
    assert warnings == []


    # Test that the function correctly handles attributes with all values defined
    variable = "var1:__OPTIONAL__"
    defined_attrs = ["long_name:Variable 1", "units:m", "flag_values:0b, 1b, 2b"]
    errors, warnings = cg.check_var(dct, variable, defined_attrs)
    assert errors == []
    assert warnings == []

    # Test that the function correctly handles an empty dct
    variable = "var2"
    dct = {"variables": {}}
    errors, warnings = cg.check_var(dct, variable, defined_attrs)
    assert errors == ["[variable**************:var2]: Variable does not exist in file. "]
    assert warnings == []


def test_check_file_name():
    # Test that the function correctly identifies invalid instrument name
    vocab_checks = {
        "instrument": "__vocabs__:tests/test_instruments:test_instruments:__all__",
        "data_product": "__vocabs__:tests/test_products:test_products"
    }
    rule_checks = {
        "platform": "rule-func:match-one-of:plat1|plat2"
    }
    file_name = "inst3_plat1_20220101_prod1_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == ["[file name]: Invalid file name format - unknown instrument 'inst3'"]
    assert warnings == []

    # Test that the function correctly identifies invalid platform name
    file_name = "inst1_plat3_20220101_prod1_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == ["[file name]: Invalid file name format - 'plat3' must be one of: '['plat1', 'plat2']'"]
    assert warnings == []

    # Test that the function correctly identifies invalid date format
    file_name = "inst1_plat1_2022010_prod1_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == ["[file name]: Invalid file name format - bad date format '2022010'"]
    assert warnings == []

    # Test that the function correctly identifies invalid date
    file_name = "inst1_plat1_20221301_prod1_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == ["[file name]: Invalid file name format - invalid date in file name '20221301'"]
    assert warnings == []

    # Test that the function correctly identifies invalid data product
    file_name = "inst1_plat1_20220101_prod3_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == ["[file name]: Invalid file name format - unknown data product 'prod3'"]
    assert warnings == []

    # Test that the function correctly identifies invalid version number format
    file_name = "inst1_plat1_20220101_prod1_v10.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == ["[file name]: Invalid file name format - incorrect file version number 'v10'"]
    assert warnings == []

    # Test that the function correctly identifies too many options in file name
    file_name = "inst1_plat1_20220101_prod1_option1_option2_option3_option4_option5_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == ["[file name]: Invalid file name format - too many options in file name"]
    assert warnings == []

    # Test that the function correctly handles multiple errors
    file_name = "inst3_plat3_20220101_prod1_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == ["[file name]: Invalid file name format - unknown instrument 'inst3'","[file name]: Invalid file name format - 'plat3' must be one of: '['plat1', 'plat2']'"]
    assert warnings == []

    # Test that the function correctly handles valid file names
    file_name = "inst1_plat1_20220101_prod1_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == []
    assert warnings == []

    file_name = "inst1_plat1_20220101_prod1_opt1_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == []
    assert warnings == []

    file_name = "inst1_plat1_20220101_prod1_opt1_opt2_opt3_v1.0.nc"
    errors, warnings = cg.check_file_name(file_name, vocab_checks, rule_checks)
    assert errors == []
    assert warnings == []
