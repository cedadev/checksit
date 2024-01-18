import pytest
import json
from checksit.specs import show_specs


def test_show_specs_all(capsys):
    # Call the function
    show_specs(["tests/test"])

    # Capture the output of the print statements
    captured = capsys.readouterr()

    # Check that the print function was called with the correct arguments
    expected_output = (
        'Specifications:\n\ntests/test:\n{\n    "var-requires": {\n'
        '        "func": "checksit.generic.check_var_attrs",\n        "params": {\n'
        '            "defined_attrs": [\n                "long_name"\n            ]\n'
        '        }\n    },\n    "required-global-attrs": {\n'
        '        "func": "checksit.generic.check_dim_exists",\n        "params": {\n'
        '            "dimensions": [\n                "time"\n'
        '            ]\n        }\n    }\n}\n'
        )
    assert captured.out == expected_output


def test_show_specs_none_specified(capsys):
    # When no spec is specified, all specs in specs/groups are shown
    show_specs([])
    captured_empty = capsys.readouterr()

    show_specs(["ceda-base"])
    captured_ceda_base = capsys.readouterr()

    assert captured_empty.out == captured_ceda_base.out
