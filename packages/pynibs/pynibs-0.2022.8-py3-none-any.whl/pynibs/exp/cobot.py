import datetime
import json
import os

import h5py
import numpy as np
import pandas as pd

import pynibs
from pynibs import coil_distance_correction_matsimnibs


def merge_exp_data_cobot(subject, exp_idx, mesh_idx, coil_outlier_corr_cond=False,
                         remove_coil_skin_distance_outlier=True, coil_distance_corr=True,
                         verbose=False, plot=False):
    """
    Merge the TMS coil positions and the mep data into an experiment.hdf5 file.

    Parameters
    ----------
    subject : pyfempp.subject
        Subject object
    exp_idx : str
        Experiment ID
    mesh_idx : str
        Mesh ID
    coil_outlier_corr_cond : bool
        Correct outlier of coil position and orientation (+-2 mm, +-3 deg) in case of conditions
    remove_coil_skin_distance_outlier : bool
        Remove outlier of coil position lying too far away from the skin surface (+- 5 mm)
    coil_distance_corr : bool
        Perform coil <-> head distance correction (coil is moved towards head surface until coil touches scalp)
    verbose : bool
        Plot output messages
    plot : bool, optional, default: False
        Plot MEPs and p2p evaluation
    """
    try:
        import biosig
    except ImportError:
        ImportError("Please install biosig from pynibs/pkg/biosig folder!")
        return

    fn_exp_hdf5 = subject.exp[exp_idx]["fn_exp_hdf5"][0]

    # 1) EMG
    cfs_fn = subject.exp[exp_idx]["fn_data"][0][0]
    cfs_header = json.loads(biosig.header(cfs_fn))
    cfs_emg = biosig.data(cfs_fn)

    num_sweeps = cfs_header["NumberOfSweeps"]

    total_num_samples = cfs_header["NumberOfSamples"]
    samples_per_sweep = int(total_num_samples / num_sweeps)
    sampling_rate = int(cfs_header["Samplingrate"])
    time = np.linspace(0, samples_per_sweep, samples_per_sweep) / sampling_rate
    num_channels = cfs_emg.shape[1]

    tms_pulse_time = subject.exp[exp_idx]['tms_pulse_time']
    # drop_mep_idx = None  # Which MEPs to remove before matching
    start_mep_ms = 18
    end_mep_ms = 40
    fn_plot = None

    # cfs_data_column = range(num_channels)
    d = dict()

    # get timestamps
    tms_pulse_timedelta = datetime.timedelta()
    # get hour, minute and second
    time_mep_list = []
    trigger_event_idcs = []
    # convert time string into integer
    for event in cfs_header["EVENT"]:
        date = datetime.datetime.strptime(event["TimeStamp"], '%Y-%b-%d %H:%M:%S')

        # we are interested in the tms pulse time, so add it to ts
        date += tms_pulse_timedelta
        time_mep_list.append(date)

        # compute indices in data block corresponding to the events
        if event["TYP"] == "0x7ffe":
            trigger_event_idcs.append(
                    round(event["POS"] * cfs_header["Samplingrate"])
            )

    num_sweeps = min(num_sweeps, len(trigger_event_idcs))

    for c_idx in range(num_channels):
        # Use emg data startinng from the index of the first trigger event
        # assumptions:
        # - after an initial offset all emg data were captured consecutively
        # - the first emg data frame may be captured without an explicit TMS
        #   tigger (eg. by checking the "write to disk" option)
        # - if we had dropouts in between the emg data block (not just at the
        #   beginning) we would need to adhere to the entire trigger_event_indices
        #   list.
        channel_emg = np.reshape(
                cfs_emg[trigger_event_idcs[0]:, c_idx],
                (num_sweeps, samples_per_sweep)
        )

        d[f"mep_raw_data_time_{c_idx}"] = []
        d[f"mep_filt_data_time_{c_idx}"] = []
        d[f"mep_raw_data_{c_idx}"] = []
        d[f"mep_filt_data_{c_idx}"] = []
        d[f"p2p_{c_idx}"] = []
        d[f"mep_latency_{c_idx}"] = []

        for s_idx in range(0, num_sweeps):
            if plot:
                fn_channel = os.path.join(os.path.split(subject.exp[exp_idx]["fn_data"][0][0])[0], "plots", str(c_idx))
                fn_plot = os.path.join(fn_channel, f"mep_{s_idx:04}")
                os.makedirs(fn_channel, exist_ok=True)

            # filter data and calculate p2p values
            p2p, mep_filt_data, latency = pynibs.calc_p2p(
                    sweep=channel_emg[s_idx],
                    tms_pulse_time=tms_pulse_time,
                    sampling_rate=sampling_rate,
                    start_mep=start_mep_ms,
                    end_mep=end_mep_ms,
                    measurement_start_time=0,
                    fn_plot=fn_plot
            )

            d[f"mep_raw_data_time_{c_idx}"].append(time)
            d[f"mep_filt_data_time_{c_idx}"].append(time)
            d[f"mep_raw_data_{c_idx}"].append(channel_emg[s_idx])
            d[f"mep_filt_data_{c_idx}"].append(mep_filt_data)
            d[f"p2p_{c_idx}"].append(p2p)
            d[f"mep_latency_{c_idx}"].append(latency)

    # 2) coil positions
    csv_fn = subject.exp[exp_idx]["fn_tms_nav"][0][0]
    out_coil_pos_fn = os.path.join(os.path.dirname(csv_fn), "coilpos")

    csv_coil_pos_data = pd.read_csv(csv_fn)
    centers = csv_coil_pos_data[['pos_x', 'pos_y', 'pos_z']].to_numpy()
    m0 = csv_coil_pos_data[['o_x', 'o_y', 'o_z']].to_numpy()
    m1 = csv_coil_pos_data[['n_x', 'n_y', 'n_z']].to_numpy()
    m2 = csv_coil_pos_data[['a_x', 'a_y', 'a_z']].to_numpy()

    matsimnibs = np.zeros((centers.shape[0], 4, 4))
    matsimnibs[:, 3, :3] = centers
    matsimnibs[:, 0, :3] = m0
    matsimnibs[:, 1, :3] = m1
    matsimnibs[:, 2, :3] = m2
    matsimnibs[:, 3, 3] = 1
    matsimnibs_t = matsimnibs.transpose()

    fn_matsimnibs_out = os.path.join(os.path.dirname(out_coil_pos_fn), "matsimnibs.hdf5")
    with h5py.File(fn_matsimnibs_out, 'w') as matsimnibs_hf5:
        matsimnibs_hf5["matsimnibs"] = matsimnibs_t

    '''
    # remove coil position outliers (in case of conditions)
    #######################################################
    if coil_outlier_corr_cond:
        if verbose:
            print("Removing coil position outliers")
        d = coil_outlier_correction_cond(exp=d,
                                         outlier_angle=5.,
                                         outlier_loc=3.,
                                         fn_exp_out=fn_exp_hdf5)
    '''

    # perform coil <-> head distance correction
    fn_mesh_hdf5 = subject.mesh[mesh_idx]['fn_mesh_hdf5']
    if coil_distance_corr:
        if verbose:
            print("Performing coil <-> head distance correction")
        matsimnibs_t = coil_distance_correction_matsimnibs(matsimnibs=matsimnibs_t,
                                                           fn_mesh_hdf5=fn_mesh_hdf5,
                                                           distance=1,
                                                           remove_coil_skin_distance_outlier=remove_coil_skin_distance_outlier)

    d["coil_0"] = []
    for i in range(centers.shape[0]):
        d["coil_0"].append(matsimnibs_t[:, :, i])
    d["condition"] = csv_coil_pos_data['idx'].to_numpy()
    d["coil_mean"] = d["coil_0"]

    # 3) save in "experiment.hdf5"
    coil_0_np = np.array(d['coil_0'])
    from pynibs import write_coil_pos_hdf5
    write_coil_pos_hdf5(
            fn_hdf=out_coil_pos_fn,
            centers=coil_0_np[:, :3, 3],  # np.array(centers),
            m0=coil_0_np[:, :3, 0],  # np.array(m0),
            m1=coil_0_np[:, :3, 1],  # np.array(m1),
            m2=coil_0_np[:, :3, 2],  # np.array(m2),
            overwrite=True
    )

    # create dictionary of stimulation data
    #######################################
    d_stim_data = dict()
    d_stim_data["coil_0"] = d["coil_0"]
    d_stim_data["number"] = csv_coil_pos_data["idx"].to_numpy()
    d_stim_data["current"] = csv_coil_pos_data["didt"].to_numpy()
    d_stim_data["date"] = csv_coil_pos_data["date"].to_list()
    d_stim_data["time"] = csv_coil_pos_data["time"].to_list()
    d_stim_data["coil_type"] = csv_coil_pos_data["coil_type"].to_list()

    # create dictionary of raw physiological data
    #############################################
    d_phys_data_raw = dict()
    # d_phys_data_raw["EMG Start"] = []
    # d_phys_data_raw["EMG End"] = []
    # d_phys_data_raw["EMG Res."] = []
    # d_phys_data_raw["EMG Channels"] = []
    d_phys_data_raw["EMG Window Start"] = [start_mep_ms] * num_sweeps
    d_phys_data_raw["EMG Window End"] = [end_mep_ms] * num_sweeps

    for chan in range(num_channels):
        d_phys_data_raw[f"mep_raw_data_time_{chan}"] = d[f"mep_raw_data_time_{chan}"]
        d_phys_data_raw[f"mep_raw_data_{chan}"] = d[f"mep_raw_data_{chan}"]

    # create dictionary of postprocessed physiological data
    #######################################################
    d_phys_data_postproc = dict()

    for chan in range(num_channels):
        d_phys_data_postproc[f"mep_filt_data_time_{chan}"] = d[f"mep_filt_data_time_{chan}"]
        d_phys_data_postproc[f"mep_filt_data_{chan}"] = d[f"mep_filt_data_{chan}"]
        d_phys_data_postproc[f"p2p_{chan}"] = d[f"p2p_{chan}"]
        d_phys_data_postproc[f"mep_latency_{chan}"] = d[f"mep_latency_{chan}"]

    # create pandas dataframes from dicts
    #####################################
    df_stim_data = pd.DataFrame.from_dict(d_stim_data)
    df_phys_data_raw = pd.DataFrame.from_dict(d_phys_data_raw)
    df_phys_data_postproc = pd.DataFrame.from_dict(d_phys_data_postproc)

    # save in .hdf5 file
    df_stim_data.to_hdf(fn_exp_hdf5, "stim_data")
    df_phys_data_raw.to_hdf(fn_exp_hdf5, "phys_data/raw/EMG")
    df_phys_data_postproc.to_hdf(fn_exp_hdf5, "phys_data/postproc/EMG")

    print("Done.")
