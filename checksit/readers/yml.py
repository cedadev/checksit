import yaml

req_dicts = "dimensions", "variables", "global_attributes"

class YAMLFile:
    def __init__(self, fpath, content):
        self.inpt = fpath
        self._content = content
        for key in req_dicts:
            if key not in self._content:
                self._content[key] = {}        

    def to_dict(self):
        return self._content


def read(fpath, verbose=False):
    d = yaml.load(open(fpath), Loader=yaml.SafeLoader)
    return YAMLFile(fpath, d)


