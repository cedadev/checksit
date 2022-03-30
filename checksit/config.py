import os
from configparser import ConfigParser
from itertools import chain

# Global CONFIG used by other packages
_CONFIG = None

ini_file = "checksit.ini"


def get_config(package=None):
    global _CONFIG

    if True:  # not _CONFIG:
        _load_config(package)

    return _CONFIG


def _gather_config_files(package=None):
    conf_files = []
    _config = os.path.join(os.path.dirname(__file__), "etc", ini_file)

    if not os.path.isfile(_config):
        print(f"[WARN] Cannot load default config file from: {_config}")
    else:
        conf_files.append(_config)
    if package:
        pkg_config = os.path.join(os.path.dirname(package.__file__), "etc", ini_file)
        if os.path.isfile(pkg_config):
            conf_files.append(pkg_config)

    # add system config in: /etc/
    sys_config = os.path.abspath(os.path.join(os.sep, "etc", ini_file))
    if os.path.isfile(sys_config):
        conf_files.append(sys_config)

    CHECKSIT_CONFIG = "CHECKSIT_CONFIG"
    if CHECKSIT_CONFIG in os.environ:
        conf_files.extend(os.environ[CHECKSIT_CONFIG].split(":"))

    return conf_files


def _to_list(i):
    return i.split()


def _to_dict(i):
    if not i.strip():
        return {}
    return dict([_.split(":") for _ in i.strip().split("\n")])


def _to_int(i):
    return int(i)


def _to_float(i):
    return float(i)


def _to_boolean(i):
    if i != "False" and i != "True":
        raise Exception(
            f"{i} is not valid for boolean field - you must use either True or False"
        )
    else:
        return eval(i)


def _chain_config_types(conf, keys):
    return chain(*[conf.get("config_data_types", key).split() for key in keys])


def _get_mappers(conf):
    mappers = {}

    for key in _chain_config_types(conf, ["lists", "extra_lists"]):
        mappers[key] = _to_list

    for key in _chain_config_types(conf, ["dicts", "extra_dicts"]):
        mappers[key] = _to_dict

    for key in _chain_config_types(conf, ["ints", "extra_ints"]):
        mappers[key] = _to_int

    for key in _chain_config_types(conf, ["floats", "extra_floats"]):
        mappers[key] = _to_float

    for key in _chain_config_types(conf, ["booleans", "extra_booleans"]):
        mappers[key] = _to_boolean

    return mappers


def _load_config(package=None):
    global _CONFIG

    conf_files = _gather_config_files(package)
    conf = ConfigParser()

    conf.read(conf_files)
    config = {}

    mappers = _get_mappers(conf)

    for section in conf.sections():
        config.setdefault(section, {})

        for key in conf.options(section):

            value = conf.get(section, key)

            if key in mappers:
                value = mappers[key](value)

            config[section][key] = value

    _post_process(config)

    _CONFIG = config


def _post_process(config):
    """
    Post-processes the contents of the config file to modify sections based on
    certain rules.
    Returns None.
    """
    for name in [n for n in config.keys() if n.startswith("project:")]:
        _modify_fixed_path_mappings(config, name)


def _modify_fixed_path_mappings(config, name):
    """
    Expands the contents of `fixed_path_mappings` based on other fixed path modifiers`.
    Returns None - changes contents in place.
    """
    d = config[name]

    fp_mappings = "fixed_path_mappings"
    fp_modifiers = "fixed_path_modifiers"

    if fp_mappings not in d or fp_modifiers not in d:
        return

    mappings = d[fp_mappings].copy()

    for modifier in d[fp_modifiers]:
        items = d[fp_modifiers][modifier].split()
        mappings = _expand_mappings(mappings, modifier, items)

    d[fp_mappings] = mappings.copy()


def _expand_mappings(mappings, modifier, items):
    """
    Expands mappings by replacing modifier with list of items
    in each case.
    """
    result = {}

    for key, value in mappings.items():
        lookup = "{" + modifier + "}"

        if lookup in key or lookup in value:
            for item in items:
                result[key.replace(lookup, item)] = value.replace(lookup, item)
        else:
            result[key] = value

    return result
