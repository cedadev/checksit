import os

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
    return len(r.check(f"type-rule:{_type}", value))

def test_type_rules():
    tt = _test_type

    _type = "number"
    for value in 3.4, -4:
        assert tt(_type, value) == 0

    for value in "3", "3.4", ["hi"]:
        assert tt(_type, value) == 1

    _type = "float"
    for value in [3.4]:
        assert tt(_type, value) == 0

    for value in "3", 3, ["hi"]:
        assert tt(_type, value) == 1

    _type = "integer"
    for value in [3]:
        assert tt(_type, value) == 0

    for value in "3", 3.5, ["hi"]:
        assert tt(_type, value) == 1

    _type = "string"
    for value in "3", "hi":
        assert tt(_type, value) == 0

    for value in 3, 4.5, ["hi"]:
        assert tt(_type, value) == 1

def test_regex_rules():
    rule = "regex-rule:integer"
    assert r.check(rule, "-1") == []
    assert r.check(rule, "500") == []
    assert r.check(rule, "1.3") != []

    rule = "regex-rule:valid-email"
    assert r.check(rule, "freda.bloggs@amail.com") == []
    assert r.check(rule, "@amail.com") != []
    assert r.check(rule, "freda.bloggs@") != []

    rule = "regex-rule:valid-url"
    assert r.check(rule, "https://github.com/") == []
    assert r.check(rule, "https://") != []
    assert r.check(rule, "github.com") != []

    rule = "regex-rule:match:vN.M"
    assert r.check(rule, "v1.0") == []
    assert r.check(rule, "1.0") != []
    assert r.check(rule, "v1") != []

    rule = "regex-rule:number"
    assert r.check(rule, "42") == []
    assert r.check(rule, "-42") == []
    assert r.check(rule, "forty two") != []

def test_rule_funcs():
    rule = "rule-func:match-one-of:butcher|baker|candle stick maker"
    assert r.check(rule, "butcher") == []
    assert r.check(rule, "candle stick maker") == []
    assert r.check(rule, "butcher's son") != []
    assert r.check(rule, "butcher, baker") != []

    rule = "rule-func:match-one-or-more-of:butcher|baker|candle stick maker"
    assert r.check(rule, "butcher") == []
    assert r.check(rule, "candle stick maker") == []
    assert r.check(rule, "butcher's son") != []
    assert r.check(rule, "butcher, baker") == []
    assert r.check(rule, "butcher, butcher's son") != []

    rule = "rule-func:string-of-length:8"
    assert r.check(rule, "checksit") == []
    assert r.check(rule, "check") != []
    assert r.check(rule, "checksit check") != []

    rule = "rule-func:string-of-length:8+"
    assert r.check(rule, "checksit") == []
    assert r.check(rule, "check") != []
    assert r.check(rule, "checksit check") == []

#TODO: Add checks for all the published rules 
#TODO: Add checks for some regular expressions to check they are executed correctly
