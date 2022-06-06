from .utils import UNDEFINED, is_undefined
from .cvs import vocabs


def _get_bounds_var_ids(dct):
    return [var_id for var_id in dct["variables"] if (
            var_id.startswith("bounds_") or var_id.startswith("bnds_") or
            var_id.endswith("_bounds") or var_id.endswith("_bnds"))] 


def check_var_attrs(dct, defined_attrs, ignore_bounds=True):
    """
    Check that variable attributes are defined.

    E.g.: check-var-attrs:defined_attrs:long_name|units
    """
    errors = []
    bounds_vars = _get_bounds_var_ids(dct)

    for var_id, var_dict in dct["variables"].items():
        if var_id in bounds_vars: continue 

        for attr in defined_attrs:
            if is_undefined(var_dict.get(attr)):
                errors.append(f"[variable**************:{var_id}]: Attribute '{attr}' must have a valid definition.")

    return errors
 

def check_global_attrs(dct, defined_attrs=None, vocab_attrs=None):
    """
    Check that required global attributes are correct.

    E.g.: check-global-attrs:defined_attrs:source
          check-global-attrs:vocab_attrs:Conventions
    """
    defined_attrs = defined_attrs or []
    vocab_attrs = vocab_attrs or {}

    errors = []

    for attr in defined_attrs:
        if is_undefined(dct['global_attributes'].get(attr)):
            errors.append(f"[global-attributes:**************:{attr}]: Attribute '{attr}' must have a valid definition.")

    for attr in vocab_attrs:
        errors.extend(vocabs.check(vocab_attrs[attr], dct['global_attributes'].get(attr, UNDEFINED), label=f"[global-attributes:******:{attr}]***"))
 

    return errors
 
