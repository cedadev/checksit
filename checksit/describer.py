from .utils import get_public_funcs, map_to_rule
from .rules import rule_funcs


def describe(check_ids=None, verbose=False):
    all_funcs = get_public_funcs(rule_funcs)

    if not check_ids:
        check_funcs = [(map_to_rule(func), func) for func in all_funcs]
    else:
        check_funcs = []
        func_dict = dict([(map_to_fule(func), func) for func in all_funcs])

        for check_id in check_ids:
            if check_id in func_dict:
                check_funcs.append((check_id, func_dict[check_id]))

    print("Functional check descriptions:")
    for check_id, check_func in check_funcs:
     
        print(f"\n{check_id}:\n\tFunction: {check_func.__name__}\n\tDescription:")
        print("\n\t".join([line for line in check_func.__doc__.split("\n")]))

