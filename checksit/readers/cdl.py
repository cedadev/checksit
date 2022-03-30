from collections import deque
import re
import yaml
import subprocess as sp

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
                raise Exception(f"Invalid file or CDL contents provided: '{inpt[:100]}...'")
 
        sections = self._get_sections(cdl_lines, split_patterns=self.CDL_SPLITTERS, start_at=1)

        # Re-split section 1 to separate variables from global attrs
        self.dimensions = self._ordered_dict(sections[0])
        self.variables, self.global_attrs = self._split_vars_globals(sections[1])

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
        
#        if self.verbose: print("RETURNING:", sections)
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

    def _construct_variables(self, content):
        variables = {}
        var_id = None
        current = None

        for line in content:
            if re.match(f"^{vocabs_prefix}:[0-9a-zA-Z_-]+:variables:", line):
                vocab_var_id = line.split(":")[3]
                vocab_lookup = line.split(":", 1)[-1]
                variables[vocab_var_id] = vocabs.lookup(vocab_lookup)
            elif not var_id or not line.startswith(f"{var_id}:"):
                # Add current collected variable to list if it exists
                if current: 
                    variables[var_id] = current.copy()

                var_id, dtype, dimensions = self._parse_var_dtype_dims(line)
                current = {"dtype": dtype, "dimensions": dimensions}
            else:
                key, value = [x.strip() for x in line.split(":", 1)[1].split("=", 1)]
                value = self._fix_value(value)
                try:
                    current[key] = eval(value)
                except:
                    # Try stripping float "f" suffix, and try for list in case value
                    # is an array
                    current[key] = eval(", ".join([part.strip().rstrip("f") for part in value.split(",")]))
#                    current[key] = eval(value.rstrip("f"))
        else:
            variables[var_id] = current.copy()

        return variables

    def _ordered_dict(self, content):
        resp = {}
        for line in content:
            if self.verbose: print(f"WORKING ON LINE: {line}")
            key, value = [x.strip() for x in line.lstrip(":").split("=", 1)]
            value = self._fix_value(value)
            resp[key] = eval(value)

        return resp

    def _fix_value(self, value):
        if value in ("NaN", "UNLIMITED"):
            value = f'"{value}"'
        return value 

    def to_yaml(self):
        return yaml.dump(self.to_dict(), Dumper=yaml.SafeDumper, 
                         default_flow_style=False, sort_keys=False)

    def to_dict(self):
        return {"dimensions": self.dimensions,
                "variables": self.variables,
                "global_attributes": self.global_attrs}


def read(fpath, verbose=False):
    return CDLParser(fpath, verbose=verbose)
