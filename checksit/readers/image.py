import subprocess as sp


def get_output(cmd):
    subp = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return subp.stdout.read().decode("charmap"), subp.stderr.read().decode("charmap")


class ImageParser:

    def __init__(self, inpt, verbose=False):
        self.inpt = inpt
        self.verbose = verbose
        self._find_exiftool()
        self._parse(inpt)

    def _parse(self, inpt):
        if self.verbose: print(f"[INFO] Parsing input: {inpt[:100]}...")
        self.content, _ = get_output(f"{self.exiftool_location} {inpt}")
        content_lines = self.content.strip().split("\n")
        self.global_attrs = self._attrs_dict(content_lines)

    def _find_exiftool(self):
        if self.verbose: print("[INFO] Searching for exiftool...")
        which_output, which_error = get_output("which exiftool")
        if which_error.startswith("which: no exiftool in"):
            msg = (
                f"'exiftool' required to read image file metadata but cannot be found.\n"
                f"              Visit https://exiftool.org/ for information on 'exiftool'."
            )
            raise RuntimeError(msg)
        else:
            self.exiftool_location = which_output.strip()
            if self.verbose: print(f"[INFO] Found exiftool at {self.exiftool_location}.")

    def _attrs_dict(self,content_lines):
        attr_dict = {}
        for line in content_lines:
            if self.verbose: print(f"WORKING ON LINE: {line}")
            key = line.split(":")[0].strip()
            value = line.split(":")[1].strip()
            attr_dict[key] = value
        return attr_dict

    def to_dict(self):
        return {"global_attributes": self.global_attrs}


def read(fpath, verbose=False):
    return ImageParser(fpath, verbose=verbose)

