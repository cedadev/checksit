from checksit.cvs import vocabs
import pytest

lookups = {
    '__vocabs__:ukcp18:variables:season_year':
        {'dimensions': ['time'], 'units': '1', 'dtype': 'int', 'long_name': 'season_year'},
    '__vocabs__:ukcp18:collection': 
        ['land-cpm', 'land-derived', 'land-gcm', 'land-indices', 'land-prob', 'land-rcm', 'land-rcm-gwl', 'marine-sim'],
    '__vocabs__:cf-netcdf:Conventions':
        ["CF-1.5", "CF-1.6"],
    '__vocabs__:ukcp18:__all__':
        ['collection', 'variables'],
    '__vocabs__:AMF_CVs/2.0.0/AMF_product_surface-met_variable:product_surface-met_variable:__all__:units':
        ["hPa", "K", "%", "m s-1", "degree", "mm", "mm hr-1", "hits cm-2", "hits cm-2 hr-1", "W m-2", "W m-2", "W m-2", "W m-2", "1", "1", "1", "1", "1", "1", "1", "1", "1"]
}


#for lookup, exp_value in lookups.items():
#    value = vocabs.lookup(lookup)
#    assert exp_value == value

@pytest.mark.parametrize("test_input, expected", lookups.items())
def test_vocab_lookup(test_input, expected):
    value = vocabs.lookup(test_input)
    assert expected == value

#for lookup, exp_value in lookups.items():
#    value = vc._lookup(lookup)
#    assert exp_value == value

