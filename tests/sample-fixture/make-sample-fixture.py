import os
import glob
import json
import shelve

from checksit.readers.cdl import read as read_cdl


d = {}

for cdl in glob.glob("sample-ncs/*.cdl"):
    fname = os.path.basename(cdl)
    
    d[fname] = read_cdl(cdl).to_dict()


with shelve.open("sample-fixture") as db:
    for fname in d:
        db[fname] = d[fname]




