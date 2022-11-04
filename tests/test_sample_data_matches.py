"""
Tests to see that changes have not caused the contents of sample data files to be 
parsed into different content.
"""

import shelve
import os
import pytest

from deepdiff import DeepDiff
from pprint import pprint

from checksit.readers.cdl import read as read_cdl

from .common import TESTDATA_DIR

sample_fixture_dir = os.path.join(TESTDATA_DIR, "../sample-fixture")
SAMPLE_NCS_DIR = os.path.join(sample_fixture_dir, "sample-ncs")
sample_fixture_file = os.path.join(sample_fixture_dir, "sample-fixture")


sample_files = tuple(os.listdir(SAMPLE_NCS_DIR))


@pytest.mark.parametrize('fname', sample_files)
def test_regression_cdl_reader_matches_sample_fixture(fname):
    with shelve.open(sample_fixture_file) as sample_dict:
        fpath = os.path.join(SAMPLE_NCS_DIR, fname)
        content = read_cdl(fpath).to_dict()

        d1, d2 = sample_dict[fname], content
        assert DeepDiff(d1, d2) == {},  pprint(DeepDiff(d1, d2), indent=2)
        

        
