from collections import deque
import re
import yaml
import subprocess as sp
import sys

from ..cvs import vocabs, vocabs_prefix

def get_output(cmd):
    subp = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
    return subp.stdout.read().decode('utf-8')


class CDLParser:
    
    CDL_SPLITTERS = ("dimensions:", "variables:", "data:", "}")

    def __init__(self, inpt, verbose=False):
        self.inpt = inpt
        self.verbose = verbose
        self._parse(inpt)
        self._check_format()

    def _parse(self, inpt):
        if self.verbose: print(f"[INFO] Parsing input: {inpt[:100]}...")        
        if inpt.endswith(".nc"):
            self.cdl = get_output(f"ncdump -h {inpt}")
        elif inpt.endswith(".cdl"):
            self.cdl = open(inpt).read()
        else:
            self.cdl = inpt
       
        cdl_lines = self.cdl.strip().split("\n")

        # Add "data:" and "}" to the CDL if they are not present - to aid parsing
        if "data:" not in [i.strip() for i in cdl_lines]:
            cdl_lines.insert(-1, "data:")

        if cdl_lines[-1] != "}":
            cdl_lines.append("}")

        for s in self.CDL_SPLITTERS:
            if s not in cdl_lines:
                print(f"Please check your command - invalid file or CDL contents provided: '{inpt[:100]}...'")
                sys.exit(1)
 
        sections = self._get_sections(cdl_lines, split_patterns=self.CDL_SPLITTERS, start_at=1)

        # Re-split section 1 to separate variables from global attrs
        self.dimensions = self._ordered_dict(sections[0])
        self.variables, self.global_attrs = self._split_vars_globals(sections[1])

    def _check_format(self):
        self.fmt_errors = []

        source = self.global_attrs.get("source", "UNDEFINED")

        min_chars = 10
        if len(source) < min_chars:
           self.fmt_errors.append(f"[FORMAT:global_attributes:source] Must be at least {min_chars} characters, not {source}") 

    def _get_sections(self, lines, split_patterns, start_at):
        split_patterns = deque(split_patterns)
        splitter = split_patterns.popleft()

        sections = []
        current = []

        for i, line in enumerate(lines):
            if i < start_at or not line.strip(): continue

            if line.startswith(splitter):
                if current:
                    sections.append(current[:])
                    # print(len(sections))
                current = []

                if split_patterns:
                    splitter = split_patterns.popleft()
            else:
                line_no_comments = re.split(";\s+//.*$", line)[0].strip().rstrip(";").strip()
                if not line_no_comments.startswith("//"):
                    current.append(line_no_comments)
        
        return sections

    def _split_vars_globals(self, content):
        variables = []
        for i, line in enumerate(content):
            if line.startswith(":"): break
            variables.append(line)

        global_attrs = content[i:]
        return self._construct_variables(variables), self._ordered_dict(global_attrs)

    def _parse_var_dtype_dims(self, line):
        if self.verbose: print(f"PARSING LINE: {line}")
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
            return eval(", ".join([part.strip().rstrip("bBcCfFiIlLsS") for part in value.split(",")]))

    def _construct_variables(self, content):
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
            elif not var_id or not line.startswith(f"{var_id}:") and last_line.strip()[-1] != ",":
                # Add current collected variable to list if it exists
                if current: 
                    variables[var_id] = current.copy()

                var_id, dtype, dimensions = self._parse_var_dtype_dims(line)
                current = {"type": dtype, "dimension": ', '.join(dimensions)}
            else:
#                key, value = [x.strip() for x in line.split(":", 1)[1].split("=", 1)]
                # Send last key and last value (from last iteration of loop) and line to get new value
                key, value = self._parse_key_value_multiline_safe(line, key, value, variable_attr=True)
                current[key] = self._safe_parse_value(value)

            last_line = line
        else:
            variables[var_id] = current.copy()

        return variables

    def _parse_key_value_multiline_safe(self, line, last_key, last_value, variable_attr=False):
        # Caters for continuation lines for arrays of strings, etc
        if "=" in line:
            # A new (key, value) pair is found
            if variable_attr: # var attr
                key, value = [x.strip() for x in line.split(":", 1)[1].split("=", 1)]
            else:        # global attr
                key, value = [x.strip() for x in line.lstrip(":").split("=", 1)]
        else:
            # Assume a continuation of th last value, so set key to None
            key, value = last_key, last_value + " " + line.strip().rstrip(";")

        return key, value


    def _ordered_dict(self, content):
        resp = {}
        key = None
        value = None

        for line in content:
            if self.verbose: print(f"WORKING ON LINE: {line}")
            
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

    def to_yaml(self):
        return yaml.dump(self.to_dict(), Dumper=yaml.SafeDumper, 
                         default_flow_style=False, sort_keys=False)

    def to_dict(self):
        return {"dimensions": self.dimensions,
                "variables": self.variables,
                "global_attributes": self.global_attrs,
                "inpt": self.inpt}


def read(fpath, verbose=False):
    return CDLParser(fpath, verbose=verbose)
