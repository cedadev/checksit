import os
import re
import glob
from collections import defaultdict, OrderedDict as OD

import pandas as pd


def find_log_files(dr=None):
    dr = dr or "."
    return glob.glob(f"{dr}/*.log")


def get_max_column_count(files, sep):
    count = 0
    for f in files:
        with open(f) as reader:
            for line in reader:
                c = line.count(sep)
                if c > count:
                    count = c

    return count


def do_exclude(err, exclude_patterns):
    for exclude_pattern in exclude_patterns:
        if exclude_pattern in err:
            return True

    return False


def summarise(
    log_files=None, log_directory=None, show_files=False, exclude=None, verbose=False
):
    log_files = log_files or find_log_files(log_directory)
    exclude_patterns = exclude or []

    if len(log_files) == 0:
        print("[ERROR] No log files found!")
        return

    if verbose:
        print(f"[INFO] Reading {len(log_files)} files:")
        print(f"\t{log_files[0]} ...to... {log_files[-1]}")

    sep = "|"

    n_cols = get_max_column_count(log_files, sep)
    print(f"[INFO] Max cols: {n_cols}")

    known_cols = ["filepath", "template", "highest_error", "error_count"]
    err_cols = [f"err_{i:02d}" for i in range(n_cols - len(known_cols) + 1)]
    headers = known_cols + err_cols
    print(f"Headers: {headers}")

    li = []
    count = 0

    for filename in log_files:
        df = pd.read_csv(filename, sep=sep, index_col=None, header=None, names=headers)
        df = df.replace({r"^\s*|\s*$": ""}, regex=True)
        df["logfile"] = os.path.basename(filename)
        count += len(df)
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    df = df.fillna("")

    print(f"The length of the `df` matches the count? {len(df)}, {count}")
    fatals = len(df[df["highest_error"].str.contains("FATAL")])
    print(f"[INFO] Found {fatals} FATAL errors.")

    errors_by_type = defaultdict(list)

    for err_col in err_cols:
        for err in df[err_col].unique():
            err = err.strip()
            if not err or do_exclude(err, exclude_patterns):
                continue

            filepaths = sorted(df[df[err_col] == err]["filepath"])
            errors_by_type[err].extend(filepaths)

    all_errors = OD()
    for err in sorted(errors_by_type):
        filepaths = errors_by_type[err]
        all_errors[err] = sorted(filepaths)

    print(f"[INFO] {len(all_errors)} found. They are...")

    for err in all_errors:
        filepaths = all_errors[err]
        print(f"\t\t{err} [found in {len(filepaths)} file(s)]")

    if show_files:
        print("\n------- File paths --------\n")

        for err in all_errors:
            print(f"\t\t{err}")
            for filepath in all_errors[err]:
                print(f"\t\t\t{filepath}")
