from click.testing import CliRunner
from checksit import cli
import os
from .common import TESTDATA_DIR


def test_ncas_general_specs():
    """
    Test checksit finds correct specs for NCAS GENERAL file
    """
    runner = CliRunner()
    result = runner.invoke(cli.check, ["-p", os.path.join(TESTDATA_DIR, "netcdf/ncas-instrument_platform_20230101_surface-met_v1.0.nc")])
    output = result.output
    templ_used = output.split("Template: ")[1].split("\n")[0]
    specs_used = output.split("Spec Files: ")[1].split("\n")[0]
    assert templ_used == "OFF"
    assert specs_used == "['ncas-amof-2.0.0/amof-file-name', 'ncas-amof-2.0.0/amof-common-land', 'ncas-amof-2.0.0/amof-surface-met', 'ncas-amof-2.0.0/amof-global-attrs']"