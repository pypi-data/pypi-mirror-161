""" Utility functions for working with fear conditioning data. """
from pathlib import Path
from scipy import stats
import numpy as np
import pandas as pd


def resample_data(df, freq=10):
    """
    Resamples data to a specified frequency. Converts index to Timedelta,
    and uses .resample() to resample data.

    Args:
        df (DataFrame): DataFrame object containing data from load_session_data()
        freq (int): New frequency of data. Defaults to 10.

    Returns:
        DataFrame: Resampled DataFrame
    """
    period = 1 / freq  # might need to use round(, ndigits=3) if getting error with freq
    df_list = []
    for idx in df["Animal"].unique():
        # temporary df for specific subject
        df_subj = df.loc[df["Animal"] == idx, :]
        # convert index to TimeDeltaIndex for resampling
        df_subj.index = df_subj["time"]
        df_subj.index = pd.to_timedelta(df_subj.index, unit="s")
        df_subj = df_subj.resample(f"{period}S").mean()
        # interpolate if there are NaNs
        if pd.isnull(df_subj["time"]) is True:
            df_subj = df_subj.interpolate()
        df_subj.loc[:, "Animal"] = idx
        df_subj["time"] = df_subj.index.total_seconds()
        df_list.append(df_subj)

    df = pd.concat(df_list).reset_index(drop=True)
    # resample also moves 'Animal' to end of DataFrame, put it back at start
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index("Animal")))
    df = df.reindex(columns=cols)

    return df


def trial_normalize(df, yvar):
    """
    Trial-normalize data aligned to a stimulus onset.

    Args:
        df (DataFrame): Trial-level data
        yvar (str): Column in df to trial-normalize.

    Returns:
        DataFrame: Adds column named {yvar}_znorm to df.
    """
    subj_zdata = []
    for idx in df["Animal"].unique():
        df_temp = df.loc[df["Animal"] == idx, :]
        znorm_vals = []
        for i in df_temp["Trial"].unique():
            znorm_vals.append(stats.zscore(df_temp.loc[(df_temp["Trial"] == i), yvar]))
            # flatten normalized values from each trial into one array
            znorm_vals_flat = [item for sublist in znorm_vals for item in sublist]
        subj_zdata.append(znorm_vals_flat)
    # flatten normalized values from each subject
    df[f"{yvar}_znorm"] = [item for sublist in subj_zdata for item in sublist]

    return df


def label_phases(df, session):
    """
    Label DataFrame with 'Phases' (used to trial average data)

    Args:
        df (DataFrame): Data to label.
        session (str): Session to load times for, by default 'train'.

    Returns:
        DataFrame: DataFrame with new Phase column.
    """
    df = find_tfc_components(df, session)
    df.loc[:, "Phase"] = df.loc[:, "Component"]
    # label tone, trace, and iti for all protocols
    df.loc[df["Phase"].str.contains("tone"), "Phase"] = "tone"
    df.loc[df["Phase"].str.contains("trace"), "Phase"] = "trace"
    df.loc[df["Phase"].str.contains("iti"), "Phase"] = "iti"
    # label shock phases for training data
    df.loc[df["Phase"].str.contains("shock"), "Phase"] = "shock"

    return df


def tfc_comp_times(session_name="train"):
    """
    Load component times for TFC protocols.

    Args:
        session_name (str): Session name to load times. Defaults to "train".

    Returns:
        DataFrame: DataFrame of protocol component times.
    """
    curr_dir = str(Path(__file__).parents[1]) + "/docs/"
    comp_labs_file = curr_dir + "TFC phase comps.xlsx"

    return pd.read_excel(comp_labs_file, sheet_name=session_name)


def find_tfc_components(df, session="train"):
    """
    Label pandas DataFrame with TFC session components.
    """
    comp_labs = tfc_comp_times(session_name=session)
    session_end = max(comp_labs["end"])
    df_new = df.drop(df[df["time"] >= session_end].index)
    # search for time in sec, index into comp_labels
    # for start and end times
    for i in range(len(comp_labs["phase"])):
        df_new.loc[
            df_new["time"].between(comp_labs["start"][i], comp_labs["end"][i]),
            "Component",
        ] = comp_labs["phase"][i]

    return df_new


def trials_df(
    df,
    session="train",
    yvar="AvgMotion",
    normalize=True,
    trial_start=-20,
    iti_dur=120,
    us_dur=2,
):
    """
    1. Creates a dataframe of "Trial data", from (trial_start, trial_end) around each CS onset
    2. Normalizes dFF for each trial to the avg dFF of each trial's pre-CS period

    ! Session must be a sheet name in 'TFC phase components.xlsx'

    Args:
        df (DataFrame): Session data to calculate trial-level data.
        session (str): Name of session used to label DataFrame. Defaults to "train".
        yvar (str): Name of data to trial-normalize. Defaults to "AvgMotion".
        normalize (bool, optional): Normalize yvar to baseline of each trial. Defaults to True.
        trial_start (int): Start of trial. Defaults to -20.
        iti_dur (int): End of trial. Defaults to 120.
        us_dur (int): US duration used to calculate trial time. Defaults to 2.

    Returns:
        DataFrame: Trial-level data with `yvar` trial-normalized.
    """

    df = label_phases(df, session=session)
    comp_labs = tfc_comp_times(session_name=session)
    tone_idx = [
        tone for tone in range(len(comp_labs["phase"])) if "tone" in comp_labs["phase"][tone]
    ]
    shock_idx = [
        shk for shk in range(len(comp_labs["phase"])) if "shock" in comp_labs["phase"][shk]
    ]
    # determine number of tone trials from label
    n_trials = len(tone_idx)
    n_subjects = len(df.Animal.unique())
    trial_num = int(1)
    # subset trial data (-20 prior to CS --> 100s after trace/shock)
    for tone, shock in zip(tone_idx, shock_idx):
        start = comp_labs.loc[tone, "start"] + trial_start
        end = comp_labs.loc[shock, "end"] + iti_dur + trial_start
        df.loc[(start <= df.time) & (df.time < end), "Trial"] = int(trial_num)
        trial_num += 1
    # remove extra time points
    df = df.dropna().reset_index(drop=True)
    # check if last_trial contains extra rows and if so, drop them
    first_trial = df.query("Trial == Trial.unique()[0]")
    last_trial = df.query("Trial == Trial.unique()[-1]")
    extra_row_cnt = last_trial.shape[0] - first_trial.shape[0]
    df = df[:-extra_row_cnt] if extra_row_cnt > 0 else df
    df.loc[:, "Trial"] = df.loc[:, "Trial"].astype(int)
    # create common time_trial
    n_trial_pts = len(df.query("Animal == Animal[0] and Trial == Trial[0]"))
    time_trial = np.linspace(trial_start, iti_dur + abs(trial_start) + us_dur, n_trial_pts)
    df["time_trial"] = np.tile(np.tile(time_trial, n_trials), n_subjects)
    # normalize data
    if normalize:
        return trial_normalize(df, yvar=yvar)
    else:
        return df
