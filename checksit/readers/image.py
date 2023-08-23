import subprocess as sp
import yaml

fields_within_standard = [
    "XMP-photoshop:Instructions",
    "XMP-photoshop:Headline",
    "XMP-dc:Description",
    "XMP-iptcExt:LocationCreatedLocationName",
    "XMP-iptcExt:LocationCreatedGPSAltitude",
    "XMP-iptcExt:LocationCreatedGPSLatitude",
    "XMP-iptcExt:LocationCreatedGPSLongitude",
    "XMP-iptcExt:LocationShownLocationName",
    "XMP-iptcExt:LocationShownGPSAltitude",
    "XMP-iptcExt:LocationShownGPSLatitude",
    "XMP-iptcExt:LocationShownGPSLongitude",
    "XMP-xmp:CreateDate",
    "XMP-xmp:MetadataDate",
    "XMP-iptcExt:TemporalCoverageFrom",
    "XMP-iptcExt:TemporalCoverageTo",
    "XMP-dc:Rights",
    "XMP-xmpRights:WebStatement",
    "XMP-photoshop:Credit",
    "XMP-dc:Title",
    "XMP-dc:Relation",
    "XMP-dc:Creator",
    "XMP-iptcCore:CreatorWorkEmail",
    "XMP-iptcExt:CreatorIdentifier",
    "XMP-iptcExt:ContributorName",
    "XMP-iptcExt:ContributorIdentifier",
    "XMP-iptcExt:ContributorRole"]

def get_output(cmd):
    subp = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return subp.stdout.read().decode("charmap"), subp.stderr.read().decode("charmap")


class ImageParser:

    def __init__(self, inpt, verbose=False):
        self.inpt = inpt
        self.verbose = verbose
        self.base_exiftool_arguments = ["exiftool", "-G1", "-j", "-c", "%+.6f"]
        self._find_exiftool()
        self._parse(inpt)

    def _parse(self, inpt):
        if self.verbose: print(f"[INFO] Parsing input: {inpt[:100]}...")
        self.global_attrs = {}
        exiftool_arguments = self.base_exiftool_arguments + [inpt]
        exiftool_return_string = sp.check_output(exiftool_arguments)
        raw_global_attrs = yaml.load(exiftool_return_string, Loader=yaml.SafeLoader)[0]
        for tag_name in raw_global_attrs.keys():
            if tag_name in fields_within_standard:
                value_type = type(raw_global_attrs[tag_name])
                if value_type == list:
                    self.global_attrs[tag_name] = str(raw_global_attrs[tag_name][0])
                else:
                    self.global_attrs[tag_name] = str(raw_global_attrs[tag_name])

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
            #print(line)
            #key_0 = line.split("\":",1)[0].strip()
            key_0 = line.split("=",1)[0].strip()
            key = key_0[1:]    #removes first character - unwanted quotation marks
            #print(key) #delete
            value = line.split("=",1)[1].strip()
            #value = line.split("\":",1)[1].strip()
            #value = value_0.replace('\n', '')  delete
            #print(value)   #delete
            attr_dict[key] = value
        return attr_dict

    def to_dict(self):
        return {"global_attributes": self.global_attrs, "inpt": self.inpt}


def read(fpath, verbose=False):
    return ImageParser(fpath, verbose=verbose)

