import os
import pytest

from checksit.readers.cdl import read as read_cdl

from .common import TESTDATA_DIR


"""
def check(file_path, mappings=None, rules=None, ignore_attrs=None, ignore_all_globals=False,
          ignore_all_dimensions=False, ignore_all_variables=False, ignore_all_variable_attrs=False,
          auto_cache=False, log_mode="standard", verbose=False, template="auto"):

"""

def test_cdl_reader_multiline_parser_1():
    cci_file = os.path.join(TESTDATA_DIR, "esacci/ESACCI-GHG-L2-CH4-CO-TROPOMI-WFMD-20171110-fv2.cdl")
    resp = read_cdl(cci_file)

    d = resp.to_dict()
    assert d["variables"]["pressure_levels"]["comment"] == \
        ("Pressure levels define the boundaries of the averaging kernel and a priori profile layers.\n",
        "Levels are ordered from surface to top of atmosphere.")

    assert d["global_attributes"]["summary"] == \
        ("Weighting Function Modified DOAS (WFMD) was adjusted to simultaneously retrieve column-averaged dry air\n",
        "mole fractions of atmospheric methane and carbon monoxide from the shortwave-infrared (SWIR) nadir spectra\n",
        "of the TROPOMI instrument onboard Sentinel-5 Precursor.")


@pytest.mark.xfail(reason="File contains badly defined number attributes in strings - so let it fail for now.")
def test_cdl_reader_multiline_parser_2():
    cci_file = os.path.join(TESTDATA_DIR, "esacci/ESACCI-GHG-L2-CO2-GOSAT2-SRFP-20191231-fv2.cdl")
    resp = read_cdl(cci_file)

    d = resp.to_dict()


def test_cdl_reader_netcdf():
    ncfile = os.path.join(TESTDATA_DIR, "netcdf/test_netcdf.nc")
    resp = read_cdl(ncfile)

    d = resp.to_dict()
    assert sorted(d.keys()) == sorted(["global_attributes", "dimensions", "variables", "inpt"])
    assert list(d["global_attributes"].keys()) == ["test_attribute_name"]
    assert d["global_attributes"]["test_attribute_name"] == "test_attribute_value"
    assert list(d["variables"].keys()) == ["T"]
    assert sorted(d["dimensions"].keys()) == sorted(["x", "y", "z"])
    assert d["inpt"] == ncfile