from checksit.cvs import vocabs, vc


lookups = {
    'vocabs:ukcp18:variables:season_year':
        {'dimensions': ['time'], 'units': '1', 'dtype': 'int', 'long_name': 'season_year'},
    'vocabs:ukcp18:collection': 
        ['land-cpm', 'land-derived', 'land-gcm', 'land-indices', 'land-prob', 'land-rcm', 'land-rcm-gwl', 'marine-sim'],
    'vocabs:cf-netcdf:Conventions':
        ["CF-1.5", "CF-1.6"]
}


for lookup, exp_value in lookups.items():
    value = vocabs.lookup(lookup)
    assert exp_value == value


for lookup, exp_value in lookups.items():
    value = vc._lookup(lookup)
    assert exp_value == value

