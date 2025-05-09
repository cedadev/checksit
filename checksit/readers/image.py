"""Reader for image files.
"""
import subprocess as sp
import yaml
from typing import Tuple, Dict, Union

def get_output(cmd: str) -> Tuple[str, str]:
    """Get the output of a shell command.

    Args:
        cmd: The shell command to run.

    Returns:
        The output of the shell command.
    """
    subp = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return subp.stdout.read().decode("charmap"), subp.stderr.read().decode("charmap")


class ImageParser:
    """Parse an image file into dictionaries.

    Extract information from an image file into a dictionary for tags, labelled as
    `global_attributes` for use within `checksit`. This uses `exiftool` to extract the
    metadata from the image file.


    Attributes:
        inpt: The input file path.
        verbose: Print verbose output during parsing.
        base_exiftool_arguments: The arguments to pass to exiftool.
        global_attrs: The tag name and values from the image file.
        exiftool_location: The location on the machine of the exiftool executable.
        global_attrs: The metadata tags and values extracted from the image file.
    """
    def __init__(
        self,
        inpt: str,
        verbose: bool = False
    ) -> None:
        """Initialise the ImageParser and parse the input file.

        Args:
            inpt: The input file path.
            verbose: Print verbose output during parsing.
        """
        self.inpt = inpt
        self.verbose = verbose
        self.base_exiftool_arguments = ["exiftool", "-G1", "-j", "-c", "%+.6f"]
        self._find_exiftool()
        self._parse(inpt)

    def _parse(self, inpt: str) -> None:
        """Parse the input file using exiftool.

        Args:
            inpt: The input file path.
        """
        if self.verbose:
            print(f"[INFO] Parsing input: {inpt[:100]}...")
        self.global_attrs = {}
        exiftool_arguments = self.base_exiftool_arguments + [inpt]
        exiftool_return_string = sp.check_output(exiftool_arguments)
        raw_global_attrs = yaml.load(exiftool_return_string, Loader=yaml.SafeLoader)[0]
        for tag_name in raw_global_attrs.keys():
            value_type = type(raw_global_attrs[tag_name])
            if value_type == list:
                self.global_attrs[tag_name] = str(raw_global_attrs[tag_name][0])
            else:
                self.global_attrs[tag_name] = str(raw_global_attrs[tag_name])

    def _find_exiftool(self) -> None:
        """Find the location of exiftool on the machine.

        Raises:
            RuntimeError: If exiftool cannot be found on the machine.
        """
        if self.verbose:
            print("[INFO] Searching for exiftool...")
        which_output, which_error = get_output("which exiftool")
        if which_error.startswith("which: no exiftool in"):
            msg = (
                f"'exiftool' required to read image file metadata but cannot be found.\n"
                f"              Visit https://exiftool.org/ for information on 'exiftool'."
            )
            raise RuntimeError(msg)
        else:
            self.exiftool_location = which_output.strip()
            if self.verbose:
                print(f"[INFO] Found exiftool at {self.exiftool_location}.")

    def _attrs_dict(self, content_lines):
        attr_dict = {}
        for line in content_lines:
            if self.verbose:
                print(f"WORKING ON LINE: {line}")
            key_0 = line.split("=", 1)[0].strip()
            key = key_0[1:]  # removes first character - unwanted quotation marks
            value = line.split("=", 1)[1].strip()
            attr_dict[key] = value
        return attr_dict

    def to_dict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Convert the ImageParser object data to a dictionary.

        Returns:
            Dictionary containing metadata tags and values as "global_attributes", and
              the input file path as "inpt".
        """
        return {"global_attributes": self.global_attrs, "inpt": self.inpt}


def read(fpath: str, verbose: bool = False) -> ImageParser:
    """Read an image file and return an ImageParser object.

    Args:
        fpath: The path to the image file.
        verbose: Print verbose output during parsing.

    Returns:
        An ImageParser object containing the metadata tags and values.
    """
    return ImageParser(fpath, verbose=verbose)
