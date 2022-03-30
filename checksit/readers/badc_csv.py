#https://github.com/cedadev/badc-csv/blob/main/badctextfile.py
from .badctextfile import BADCTextFile

req_dicts = "dimensions", "variables", "global_attributes"


class BADCCSVHeader:
    def __init__(self, fpath, content):
        self.inpt = fpath
        self._content = content
        for key in req_dicts:
            if key not in self._content:
                self._content[key] = {}        

    def to_dict(self):
        return self._content


def read(fpath, verbose=False):
    bm = BADCTextFile(open(fpath))._metadata
    d = {"global_attributes": dict(bm.globalRecords)}
         # "variables": bm.varRecords} 
    return BADCCSVHeader(fpath, d)


