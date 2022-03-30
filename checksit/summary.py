import os
import re
import glob
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
                if c > count: count = c

    return count


def summarise(log_files=None, log_directory=None, verbose=False):
    log_files = log_files or find_log_files(log_directory)

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
    err_cols = [f"err_{i:02d}" for i in range(n_cols-len(known_cols)+1)]
    headers = known_cols + err_cols
    print(f"Headers: {headers}")

    li = []
    count = 0

    for filename in log_files:
        df = pd.read_csv(filename, sep=sep, index_col=None, header=None, names=headers)
        df = df.replace({"^\s*|\s*$":""}, regex=True)
        df["logfile"] = os.path.basename(filename)
        count += len(df)
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    df = df.fillna("")

    print(f"The length of the `df` matches the count? {len(df)}, {count}")
    fatals = len(df[df["highest_error"].str.contains("FATAL")])
    print(f"[INFO] Found {fatals} FATAL errors.")

    all_errors = []
    for err_col in err_cols:
        all_errors.extend(list(set(
            [f"{err} [found in {int(df[df[err_col] == err][err_col].value_counts())} file(s)]" 
            for err in df[err_col].unique()])))

    all_errors = sorted(set(all_errors))
    print(f"[INFO] {len(all_errors)} found. They are...")

    for err in all_errors:
        print(f"\t\t{err}")
 

