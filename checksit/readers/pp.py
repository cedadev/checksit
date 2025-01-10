import sys
import cf

req_dicts = "dimensions", "variables", "global_attributes"

class PPHeader:
    def __init__(self, fpath, content):
        self.inpt = fpath
        self._content = content
        for key in req_dicts:
            if key not in self._content:
                self._content[key] = {}

    def to_dict(self):
        return self._content


def read(fpath: str, verbose: bool = False) -> PPHeader:
    fieldlist = cf.read(fpath)
    d = {"variables": {}}

    for field in fieldlist:
        sn = field.standard_name
        sh = list(field.shape)

        d["variables"][sn] = {"shape": sh}

    return PPHeader(fpath, d)


