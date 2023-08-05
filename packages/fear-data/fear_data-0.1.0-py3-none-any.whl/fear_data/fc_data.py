"""Script used to load, process, and analyze fear conditioning data."""
import csv
import pandas as pd
import numpy as np


def _load_raw_data(data_file):

    # internal function
    def _find_start_row(data_file, start_row="Experiment"):

        """Uses regex to find the first row of data."""

        with open(data_file, "rt") as f:
            reader = csv.reader(f)
            file_rows = [row for row in reader]
        for count, value in enumerate(file_rows, start=0):
            if start_row in value:
                return count

    # convert training file to pandas df
    df = pd.read_csv(data_file, skiprows=_find_start_row(data_file))
    # drop NaNs that can get inserted into
    df = df.replace("nan", np.NaN).dropna(thresh=2).reset_index()
    # bug from VideoFreeze on some csv files, convert Animal to str
    if df["Animal"].dtype is np.dtype("float64") or df["Animal"].dtype is np.dtype(
        "int64"
    ):
        df.loc[:, "Animal"] = df["Animal"].astype("int").astype("str")
    # drop and rename columns
    old_col_list = [
        "Animal",
        "Group",
        "Component Name",
        "Pct Component Time Freezing",
        "Avg Motion Index",
    ]
    # reindex to drop extraneous cols
    df = df.reindex(columns=old_col_list)
    # rename columns to remove spaces in colnames
    new_col_list = ["Animal", "Group", "Component", "PctFreeze", "AvgMotion"]
    new_cols = {
        key: val
        for (key, val) in zip(df.reindex(columns=old_col_list).columns, new_col_list)
    }
    df = df.rename(columns=new_cols)

    return df


def add_group_labels(df, group_dict, sex_dict=None):

    df = df.copy()
    # Fill in Group info
    for key, val in group_dict.items():
        df.loc[df["Animal"].isin(val), "Group"] = key
    if sex_dict:
        for key, val in sex_dict.items():
            df.loc[df["Animal"].isin(val), "Sex"] = key

    return df.dropna(axis=1)


def load_fc_data(data_file, session):
    # load and clean data

    def get_baseline_vals(df):
        """Get values up to the first 'tone' component"""
        new_list = []
        for item in df["Component"]:
            if item.lower() not in ["tone-1", "tone-01"]:
                new_list.append(item)
            else:
                break
        new_list = [str(item) for item in new_list]
        return new_list

    # load session data
    df = _load_raw_data(data_file)
    # clean up df
    if "context" in session:
        df["Component"] = df["Component"].astype("int")
        df["Phase"] = "context"
    else:
        df["Component"] = [
            df["Component"][x].lower() for x in range(len(df["Component"]))
        ]
        df["Phase"] = df["Component"]
        baseline_vals = get_baseline_vals(df)
        # add column to denote phase of each bin
        df.loc[df["Phase"].isin(baseline_vals), "Phase"] = "baseline"
        df.loc[df["Phase"].str.contains("tone"), "Phase"] = "tone"
        df.loc[df["Phase"].str.contains("trace"), "Phase"] = "trace"
        df.loc[~df["Phase"].isin(["baseline", "tone", "trace"]), "Phase"] = "iti"

    df = df.reindex(
        columns=[
            "Animal",
            "Sex",
            "Group",
            "Phase",
            "Component",
            "PctFreeze",
            "AvgMotion",
        ]
    )

    return df


def get_phase_data(df, hue=None):
    """
    Group DataFrame by 'Phase'. Used for plotting data by Phase.


    Args:
        df (DataFrame): Data to group by trial phase.
        hue (str, optional): Specify a grouping variable (e.g., Group, AAV, etc). Defaults to None.

    Returns:
        DataFrame: Data grouped by Phase.
    """
    df = df.copy()
    groupby_list = ["Animal", "Phase"]

    if hue:
        groupby_list.append(hue)

    return df.groupby(groupby_list, as_index=False).mean().dropna()
