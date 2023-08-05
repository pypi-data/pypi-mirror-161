"""Save VideoFreeze data"""

from pathlib import Path
from .expt_config import load_expt_config
from .fc_data import load_fc_data, add_group_labels, get_phase_data


def save_data(session_list, expt_config=None, phase_data=True):
    """
    Saves a .csv file of the cleaned VideoFreeze component data.

    Args:
        session_list (list): List of sessions (must be in expt_config["sessions"])
        expt_config (dict): expt_config file used to provide save directories.
                            If none is provided, it will search through the cwd for one to load.
        phase_data (bool, optional): Whether or not to also save phase data. Defaults to True.
    """

    if not expt_config:
        config_pth = list(Path.cwd().glob("*.yml"))[0]
        expt_config = load_expt_config(config_pth)

    proc_data_path = f'{expt_config["dirs"]["data"]}/processed'
    # make proc_data_path if it doesn't exist
    Path(proc_data_path).mkdir(parents=True, exist_ok=True)

    for ses in session_list:
        session_data_file = expt_config["dirs"]["data"] + f"/raw/{expt_config['sessions'][ses]}"
        # load and label session data
        df = load_fc_data(session_data_file, session=ses)
        df = add_group_labels(df, expt_config["group_ids"])
        # save component data to csv
        comp_data_filename = f"{proc_data_path}/{expt_config['experiment']}_{ses}_components.csv"
        print(f"Saving {comp_data_filename}")
        df.to_csv(f"{comp_data_filename}", index=False)

        # save phase data
        if phase_data:
            df_phase = get_phase_data(df, hue="Group")
            phase_data_filename = f"{proc_data_path}/{expt_config['experiment']}_{ses}_phase.csv"
            print(f"Saving {phase_data_filename}")
            df_phase.to_csv(f"{phase_data_filename}", index=False)
