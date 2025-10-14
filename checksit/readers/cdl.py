"""Reader for CDL files and netCDF files.
"""
from collections import deque
import re
import yaml
import subprocess as sp
import sys
from typing import Tuple, List, Dict, Union

from ..cvs import vocabs, vocabs_prefix


def get_output(cmd: str) -> str:
    """Get the output of a shell command.

    Args:
        cmd: The shell command to run.

    Returns:
        The output of the shell command.
    """
    subp = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
    return subp.stdout.read().decode("utf-8")


class CDLParser:
    """Parse a CDL file or netCDF file into dictionaries.

    Extract information from netCDF files or CDL files into a dictionaries for
    attributes, variables and dimensions. NetCDF files are first converted to CDL using
    ncdump.

    Attributes:
        inpt: The input file path or CDL content.
        verbose: Print verbose output during parsing.
        cdl: The CDL content of the input file.
        dimensions: The dimensions of the netCDF file.
        variables: The variables of the netCDF file.
        global_attrs: The global attributes of the netCDF file.
        fmt_errors: A list of format errors found during parsing.
    """

    CDL_SPLITTERS = ("dimensions:", "variables:", "data:", "}")

    def __init__(
        self,
        inpt: str,
        verbose: bool = False,
    ) -> None:
        """Initialise the CDLParser and parse the input file.

        Args:
            inpt: The input file path or CDL content.
            verbose: Print verbose output during parsing
        """
        self.inpt = inpt
        self.verbose = verbose
        self.fmt_errors = []
        self._parse(inpt)
        self._check_format()

    def _parse(self, inpt: str) -> None:
        """Parse the input file or CDL content into dictionaries.

        Args:
            inpt: The input file path or CDL content.
        """
        if self.verbose:
            print(f"[INFO] Parsing input: {inpt[:100]}...")
        if inpt.endswith(".nc"):
            self.cdl = get_output(f"ncdump -h {inpt}")
        elif inpt.endswith(".cdl"):
            self.cdl = open(inpt).read()
        else:
            self.cdl = inpt

        cdl_lines: List[str] = self.cdl.strip().split("\n")

        # Add "data:" and "}" to the CDL if they are not present - to aid parsing
        if "data:" not in [i.strip() for i in cdl_lines]:
            cdl_lines.insert(-1, "data:")

        if cdl_lines[-1] != "}":
            cdl_lines.append("}")

        for s in self.CDL_SPLITTERS:
            if s not in cdl_lines:
                print(
                    f"Please check your command - invalid file or CDL contents provided: '{inpt[:100]}...'"
                )
                sys.exit(1)

        sections = self._get_sections(
            cdl_lines, split_patterns=self.CDL_SPLITTERS, start_at=1
        )

        # Re-split section 1 to separate variables from global attrs
        self.dimensions = self._ordered_dict(sections[0])
        self.variables, self.global_attrs = self._split_vars_globals(sections[1])

    def _check_format(self) -> None:
        source = self.global_attrs.get("source", "UNDEFINED")

        min_chars = 10
        if len(source) < min_chars:
            self.fmt_errors.append(
                f"[FORMAT:global_attributes:source] Must be at least {min_chars} characters, not {source}"
            )

    def _get_sections(
        self,
        lines: List[str],
        split_patterns: Tuple[str, ...],
        start_at: int,
    ) -> List[List[str]]:
        """Split the CDL content into sections based on the split patterns.

        Args:
            lines: The CDL content split into lines.
            split_patterns: The patterns to split the CDL content on.
            start_at: The line number to start splitting from.

        Returns:
            A list of sections of the CDL content.
        """
        split_patterns = deque(split_patterns)
        splitter = split_patterns.popleft()

        sections: List[List[str]] = []
        current: List[str] = []

        for i, line in enumerate(lines):
            if i < start_at or not line.strip():
                continue

            if line.startswith(splitter):
                if current:
                    sections.append(current[:])
                    # print(len(sections))
                current = []

                if split_patterns:
                    splitter = split_patterns.popleft()
            else:
                line_no_comments = (
                    re.split(r";\s+//.*$", line)[0].strip().rstrip(";").strip()
                )
                if not line_no_comments.startswith("//"):
                    current.append(line_no_comments)

        return sections

    def _split_vars_globals(
        self,
        content: List[str]
    ) -> Tuple[Dict[str, Dict[str, str]], Dict[str, str]]:
        """Split the variables and global attributes from the CDL content.

        The start of the global attributes section in the CDL file is marked by the
        comment "// global attributes:", which is ignored before due to being a
        comment. Each global attribute in the CDL file starts with a colon, and all are
        after the variable data.

        Args:
            content: The CDL content split into lines.

        Returns:
            A tuple containing the variable and global attribute dictionaries.
        """
        variables: List[str] = []
        for i, line in enumerate(content):
            if line.startswith(":"):
                break
            variables.append(line)

        global_attrs: List[str] = content[i:]
        return self._construct_variables(variables), self._ordered_dict(global_attrs)

    def _parse_var_dtype_dims(self, line: str) -> Tuple[str, str, List[str]]:
        """Get variable name, type and dimensions from a line in the CDL content.

        Args:
            line: The line to parse.

        Returns:
            A tuple containing the variable name, data type and dimensions.
        """
        if self.verbose:
            print(f"PARSING LINE: {line}")
        dtype, var_info = line.strip().split(" ", 1)
        var_id = var_info.split("(")[0]
        dim_info = line.replace(f"{dtype} {var_id}", "").strip()
        dimensions = dim_info.strip("()").replace(" ", "").split(",")
        return var_id, dtype, dimensions

    def _safe_parse_value(self, value):
        if value in ("NaN", "NaNf", "UNLIMITED"):
            value = f'"{value}"'

        try:
            return eval(value)
        except:
            # Remove datatype suffixes and parse as list if commas are in value
            return eval(
                ", ".join(
                    [part.strip().rstrip("bBcCfFiIlLsS") for part in value.split(",")]
                )
            )

    def _construct_variables(self, content: List[str]) -> Dict[str, Dict[str, str]]:
        """Construct a dictionary of variables from the CDL content.

        Args:
            content: The CDL content split into lines.

        Returns:
            A dictionary of variables with their attributes.
        """
        variables = {}
        var_id = None
        current = None

        # Set defaults for key and value so they can be sent to multiline parser even if not set
        key = None
        value = None

        for line in content:
            if re.match(f"^{vocabs_prefix}:[0-9a-zA-Z_-]+:variables:", line):
                vocab_var_id = line.split(":")[3]
                vocab_lookup = line.split(":", 1)[-1]
                variables[vocab_var_id] = vocabs.lookup(vocab_lookup)
            elif (
                not var_id
                or not line.startswith(f"{var_id}:")
                and last_line.strip()[-1] != ","
            ):
                # Add current collected variable to list if it exists
                if current:
                    variables[var_id] = current.copy()

                var_id, dtype, dimensions = self._parse_var_dtype_dims(line)
                if dimensions == [""]:
                    dimensions = "--none--"
                else:
                    dimensions = ", ".join(dimensions)
                current = {"type": dtype, "dimension": dimensions}
            else:
                #                key, value = [x.strip() for x in line.split(":", 1)[1].split("=", 1)]
                # Send last key and last value (from last iteration of loop) and line to get new value
                key, value = self._parse_key_value_multiline_safe(
                    line, key, value, variable_attr=True
                )
                if key in current.keys():
                    if current[key] != self._safe_parse_value(value) and self.verbose:
                        print(
                            f"[WARNING] Variable attribute '{key}' for variable '{var_id}' already exists,"
                            f" not overwriting existing value '{current[key]}' with new value '{value}'"
                        )
                    self.fmt_errors.append(
                        f"[DUPLICATE:variable:{var_id}:{key}] Variable attribute '{key}' for variable '{var_id}' defined multiple times"
                    )
                else:
                    current[key] = self._safe_parse_value(value)

            last_line = line
        else:
            variables[var_id] = current.copy()

        return variables

    def _parse_key_value_multiline_safe(
        self, line: str, last_key: str, last_value: str, variable_attr: bool = False
    ) -> Tuple[str, str]:
        """Cater for values over multiple lines in CDL files.

        If an attribute value is printed over multiple lines in the CDL file, this
        function makes sure the whole value is attributed to the correct key.
        """
        # Caters for continuation lines for arrays of strings, etc
        if "=" in line:
            # A new (key, value) pair is found
            if variable_attr:  # var attr
                key, value = [x.strip() for x in line.split(":", 1)[1].split("=", 1)]
            else:  # global attr
                key, value = [x.strip() for x in line.lstrip(":").split("=", 1)]
        else:
            # Assume a continuation of th last value, so set key to None
            key, value = last_key, last_value + " " + line.strip().rstrip(";")

        return key, value

    def _ordered_dict(self, content: List[str]) -> Dict[str, str]:
        """Construct a dictionary from a list of attribute string.

        Attributes in CDL format are in the form "key = value;". This function parses a
        list of strings into a dictionary, with the key being the string before the
        equals sign and the value being the string after the equals sign. Some
        attribute values may reach over multiple lines, this function calls out to
        another to parse these correctly.

        Args:
            content: The list of strings to parse.

        Returns:
            A dictionary of the strings parsed into key-value pairs.
        """
        resp = {}
        key = None
        value = None

        for line in content:
            if self.verbose:
                print(f"WORKING ON LINE: {line}")

            # Cater for continuation lines for arrays of strings, etc
            #            if "=" in line:
            # A new (key, value) pair is found
            #                key, value = [x.strip() for x in line.lstrip(":").split("=", 1)]
            #            else:
            # Assume a continuation of th last value
            #                value += " " + line.strip()
            # Send last key and last value (from last iteration of loop) and line to get new value
            key, value = self._parse_key_value_multiline_safe(line, key, value)

            # This will overwrite the previous value - which is safe if a continuation happened
            # as the key is the same as last time
            resp[key] = self._safe_parse_value(value)

        return resp

    def to_yaml(self) -> str:
        """Return the parsed CDL content as a YAML string.

        Returns:
            A YAML string of the parsed CDL content.
        """
        return yaml.dump(
            self.to_dict(),
            Dumper=yaml.SafeDumper,
            default_flow_style=False,
            sort_keys=False,
        )

    def to_dict(self) -> Dict[str, Union[Dict[str, str], Dict[str, Dict[str, str]], str, List[str]]]:
        """Return the parsed CDL content as a dictionary.

        Returns:
            A dictionary of the parsed CDL content, with keys "dimensions",
              "variables", "global_attributes" and "inpt", where "inpt" is the input
              file path or CDL content.
        """
        return {
            "dimensions": self.dimensions,
            "variables": self.variables,
            "global_attributes": self.global_attrs,
            "inpt": self.inpt,
        }


def read(fpath: str, verbose: bool = False) -> CDLParser:
    """Read a CDL file or netCDF file and parse it into a CDLParser object.

    Args:
        fpath: The file path to read.
        verbose: Print verbose output during parsing.

    Returns:
        A CDLParser object containing the parsed CDL content.
    """
    return CDLParser(fpath, verbose=verbose)
