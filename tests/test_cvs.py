from checksit.cvs import vocabs
import pytest


def test_lookup():
    assert vocabs.lookup('__vocabs__:tests/test_instruments:test_instruments') == {'inst1': {"instrument_id": "inst1"}, "inst2": {"instrument_id": "inst2"}}
    assert vocabs.lookup('__vocabs__:tests/test_instruments:test_instruments:__all__') == ["inst1", "inst2"]
    assert vocabs.lookup('__vocabs__:tests/test_instruments:test_instruments:inst1') == {"instrument_id": "inst1"}
    assert vocabs.lookup('__vocabs__:tests/test_instruments:test_instruments:__all__:instrument_id') == ["inst1", "inst2"]
    with pytest.raises(ValueError):
        vocabs.lookup('__vocabs__:tests/test_instruments:test_instruments:__all__:__all__')

def test_check():
    assert vocabs.check('__vocabs__:tests/test_instruments:test_instruments:__all__:instrument_id', 'inst1', label = "Test") == []
    assert vocabs.check(
        "__vocabs__:tests/test_instruments:test_instruments:__all__:instrument_id", "inst3", label="Test",
    ) == [
        "Test 'inst3' not in vocab options: ['inst1', 'inst2'] (using: '__vocabs__:tests/test_instruments:test_instruments:__all__:instrument_id')"
    ]
    assert vocabs.check('__vocabs__:tests/test_platforms:test_platforms:plat1', {"platform_id": "plat1"}, label = "Test") == ["Test does not have attribute 'description'"]
    assert vocabs.check('__vocabs__:tests/test_platforms:test_platforms:plat1:platform_id', "plat1", label = "Test") == []
    assert vocabs.check('__vocabs__:tests/test_platforms:test_platforms:plat1:platform_id', "plat2", label = "Test") == ["Test 'plat2' does not equal required vocab value: 'plat1' (using: '__vocabs__:tests/test_platforms:test_platforms:plat1:platform_id')"]