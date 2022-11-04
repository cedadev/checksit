"""
Tests to see that changes have not caused the contents of sample data files to be 
parsed into different content.
"""

import shelve
import os

from deepdiff import DeepDiff
from pprint import pprint


from checksit.readers.cdl import read as read_cdl

SAMPLE_NCS_DIR = "./sample-ncs"
sample_fixture_file = "./sample-fixture"



if 1:
    sample_dict = shelve.open(sample_fixture_file)

    for fname in sorted(sample_dict):
        fpath = os.path.join(SAMPLE_NCS_DIR, fname)
        content = read_cdl(fpath).to_dict()        

        d1, d2 = sample_dict[fname], content
        assert DeepDiff(d1, d2) == {},  pprint(DeepDiff(d1, d2), indent=2)
        


        
