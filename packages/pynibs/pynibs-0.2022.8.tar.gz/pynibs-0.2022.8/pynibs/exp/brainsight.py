""" """
import io
import os
from collections import OrderedDict

import numpy as np
import pandas as pd

import pynibs


def write_targets_brainsight(targets, fn_out, names=None, overwrite=True):
    """
    Writes coil position and orientations in .txt file for import into Brainsight.

    Parameters
    ----------
    targets : ndarray of float [4 x 4 x N_targets]
        Tensor containing the 4x4 matrices with coil orientation and position
    fn_out : str
        Filename of output file
    names : list of str, optional, default: None
        Target names (If nothing is provided they will be numbered by their order)
    overwrite : bool, optional, default: True
        Overwrite existing .txt file

    Returns
    -------
    <file> .txt file containing the targets for import into Brainsight
    """

    targets = np.atleast_3d(targets)

    if names is None:
        names = [f"{i:04}" for i in range(targets.shape[2])]
    if isinstance(names, str):
        names = [names]
    assert targets.shape[:2] == (4, 4), 'Expecting array with shape (4, 4, N instrument marker).'

    if not fn_out.lower().endswith('.txt'):
        fn_out += '.txt'

    assert not os.path.exists(fn_out) or overwrite, '.txt file already exists. Remove or set overwrite=True.'

    with io.open(fn_out, 'w', newline='\n') as f:  # correct windows style would be \r\n, but Localite uses \n
        f.write('# Version: 12\n')
        f.write('# Coordinate system: NIfTI:Aligned\n')
        f.write('# Created by: pynibs\n')
        f.write('# Units: millimetres, degrees, milliseconds, and microvolts\n')
        f.write('# Encoding: UTF-8\n')
        f.write('# Notes: Each column is delimited by a tab. Each value within a column is delimited by a semicolon.\n')
        f.write('# Target Name	Loc. X	Loc. Y	Loc. Z	m0n0	m0n1	m0n2	m1n0	m1n1	m1n2	m2n0	m2n1	m2n2\n')

        for i_t in range(targets.shape[2]):
            f.write(f'{names[i_t]}\t' +
                    f'{targets[0, 3, i_t]:.4f}\t{targets[1, 3, i_t]:.4f}\t{targets[2, 3, i_t]:.4f}\t' +
                    f'{targets[0, 0, i_t]:.4f}\t{targets[1, 0, i_t]:.4f}\t{targets[2, 0, i_t]:.4f}\t' +
                    f'{targets[0, 1, i_t]:.4f}\t{targets[1, 1, i_t]:.4f}\t{targets[2, 1, i_t]:.4f}\t' +
                    f'{targets[0, 2, i_t]:.4f}\t{targets[1, 2, i_t]:.4f}\t{targets[2, 2, i_t]:.4f}\n')


def read_targets_brainsight(fn):
    """
    Reads target coil position and orientations from .txt file and returns it as 4 x 4 x N_targets numpy array.

    Parameters
    ----------
    fn : str
        Filename of output file.

    Returns
    -------
    m_nnav : ndarray of float [4 x 4 x N_targets]
        Tensor containing the 4x4 matrices with coil orientation and position.
    """
    with io.open(fn, 'r') as f:
        lines = f.readlines()
    start_idx = [i+1 for i, l in enumerate(lines) if l.startswith("# Target")][0]
    stop_idx = [i for i, l in enumerate(lines) if l.startswith("# Sample Name") or l.startswith("# Session Name")]

    if not stop_idx:
        stop_idx = len(lines)
    else:
        stop_idx = np.min(stop_idx)

    n_targets = stop_idx - start_idx
    names = ['' for _ in range(n_targets)]
    m_nnav = np.zeros((4, 4, n_targets))
    for i_loc, i_glo in enumerate(range(start_idx, stop_idx)):
        line = lines[i_glo].split(sep='\t')
        names[i_loc] = line[0]
        m_nnav[:3, 0, i_loc] = np.array(line[4:7]).astype(float)
        m_nnav[:3, 1, i_loc] = np.array(line[7:10]).astype(float)
        m_nnav[:3, 2, i_loc] = np.array(line[10:13]).astype(float)
        m_nnav[:3, 3, i_loc] = np.array(line[1:4]).astype(float)
        m_nnav[3, 3, i_loc] = 1
    return m_nnav


def merge_exp_data(subject, exp_idx, mesh_idx, coil_outlier_corr_cond=False,
                   remove_coil_skin_distance_outlier=True, coil_distance_corr=True,
                   verbose=False, plot=False):
    """
    Merge the TMS coil positions and the mep data into an experiment.hdf5 file.

    Parameters
    ----------
    subject : pynibs.Subject
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

    nii_exp_path_lst = subject.exp[exp_idx]['fn_mri_nii']
    # nii_conform_path = os.path.join(os.path.split(subject.mesh[mesh_idx]["fn_mesh_hdf5"])[0],
    #                                subject.id + "_T1fs_conform.nii.gz")
    nii_conform_path = subject.exp[exp_idx]["fn_mri_nii"][0][0]
    fn_exp_hdf5 = subject.exp[exp_idx]['fn_exp_hdf5'][0]
    fn_coil = subject.exp[exp_idx]['fn_coil'][0][0]
    fn_mesh_hdf5 = subject.mesh[mesh_idx]['fn_mesh_hdf5']
    temp_dir = os.path.join(os.path.split(subject.exp[exp_idx]['fn_exp_hdf5'][0])[0],
                            "pynibs.nnav2simnibs",
                            f"mesh_{mesh_idx}")
    fn_data = subject.exp[exp_idx]["fn_data"][0]

    # read Brainsight data
    ######################
    if verbose:
        print(f"Reading Brainsight data from file: {fn_data}")

    d_bs = OrderedDict()

    with io.open(fn_data, 'r') as f:
        lines = f.readlines()
    start_idx = [i + 1 for i, l in enumerate(lines) if l.startswith("# Sample Name")][0]
    stop_idx = [i for i, l in enumerate(lines) if l.startswith("# Session Name")]

    if not stop_idx:
        stop_idx = len(lines)
    else:
        stop_idx = np.min(stop_idx)

    n_stims = stop_idx - start_idx
    m_nnav = np.zeros((4, 4, n_stims))

    keys = lines[start_idx - 1].split('\t')
    keys[0] = keys[0].replace('# ', '')
    keys[-1] = keys[-1].replace('\n', '')

    # create brainsight dict
    for key in keys:
        d_bs[key] = []

    # collect data
    for i_loc, i_glo in enumerate(range(start_idx, stop_idx)):
        line = lines[i_glo].split(sep='\t')

        for i_key, key in enumerate(d_bs.keys()):
            if key in ["Sample Name", "Session Name", "Creation Cause", "Crosshairs Driver", "Date", "Time",
                       "EMG Channels"]:
                d_bs[key].append(line[i_key])
            else:
                if ";" in line[i_key]:
                    d_bs[key].append(np.array(line[i_key].split(';')).astype(float))

                else:
                    if line[i_key] != "(null)":
                        d_bs[key].append(float(line[i_key]))
                    else:
                        d_bs[key].append(float(-1))

            if key in ["Loc. X"]:
                m_nnav[0, 3, i_loc] = float(d_bs[key][-1])
            elif key in ["Loc. Y"]:
                m_nnav[1, 3, i_loc] = float(d_bs[key][-1])
            elif key in ["Loc. Z"]:
                m_nnav[2, 3, i_loc] = float(d_bs[key][-1])
            elif key in ["m0n0"]:
                m_nnav[0, 0, i_loc] = float(d_bs[key][-1])
            elif key in ["m0n1"]:
                m_nnav[1, 0, i_loc] = float(d_bs[key][-1])
            elif key in ["m0n2"]:
                m_nnav[2, 0, i_loc] = float(d_bs[key][-1])
            elif key in ["m1n0"]:
                m_nnav[0, 1, i_loc] = float(d_bs[key][-1])
            elif key in ["m1n1"]:
                m_nnav[1, 1, i_loc] = float(d_bs[key][-1])
            elif key in ["m1n2"]:
                m_nnav[2, 1, i_loc] = float(d_bs[key][-1])
            elif key in ["m2n0"]:
                m_nnav[0, 2, i_loc] = float(d_bs[key][-1])
            elif key in ["m2n1"]:
                m_nnav[1, 2, i_loc] = float(d_bs[key][-1])
            elif key in ["m2n2"]:
                m_nnav[2, 2, i_loc] = float(d_bs[key][-1])

            m_nnav[3, 3, i_loc] = 1

    # transform from brainsight to simnibs space
    ############################################
    if verbose:
        print(f"Transforming coil positions from Brainsight to SimNIBS space")
    print(nii_conform_path)

    m_simnibs = pynibs.nnav2simnibs(fn_exp_nii=nii_exp_path_lst[0][0],
                             fn_conform_nii=nii_conform_path,
                             m_nnav=m_nnav,
                             nnav_system="brainsight",
                             mesh_approach="headreco",
                             fiducials=None,
                             orientation='RAS',
                             fsl_cmd=None,
                             target='simnibs',
                             temp_dir=temp_dir,
                             rem_tmp=True,
                             verbose=verbose)

    # create dictionary containing stimulation and physiological data
    #################################################################
    if verbose:
        print(f"Creating dictionary containing stimulation and physiological data")

    current_scaling_factor = 1.43

    d = dict()
    d['coil_0'] = []
    d['coil_1'] = []
    d['coil_mean'] = []
    d['number'] = []
    d['condition'] = []
    d['current'] = []
    d['date'] = []
    d['time'] = []
    d['coil_sn'] = []
    d['patient_id'] = []

    for i in range(n_stims):
        d['coil_0'].append(m_simnibs[:, :, i])
        d['coil_1'].append(np.zeros((4, 4)) * np.NaN)
        d['coil_mean'].append(np.nanmean(np.stack((d['coil_0'][-1],
                                                   d['coil_1'][-1]), axis=2), axis=2))
        d['number'].append(d_bs['Index'][i])
        d['condition'].append(d_bs['Sample Name'][i])
        d['current'].append(1 * current_scaling_factor)
        d['date'].append(d_bs["Date"][i])
        d['time'].append(d_bs["Time"][i])
        d['coil_sn'].append(os.path.split(fn_coil)[1])
        d['patient_id'].append(subject.id)

        for key in d_bs.keys():
            if key not in ['Sample Name', 'Session Name', 'Index',
                           'Loc. X', 'Loc. Y', 'Loc. Z',
                           'm0n0', 'm0n1', 'm0n2',
                           'm1n0', 'm1n1', 'm1n2',
                           'm2n0', 'm2n1', 'm2n2',
                           'Date', 'Time'] and \
                    not (key.startswith('EMG Peak-to-peak') or
                         key.startswith('EMG Data')):

                try:
                    d[key].append(d_bs[key][i])
                except KeyError:
                    d[key] = []
                    d[key].append(d_bs[key][i])

    # add physiological raw data
    start_mep_ms = 18
    end_mep_ms = 35
    channels = np.arange(1, int(d["EMG Channels"][0]) + 1)

    if verbose:
        print(f"Postprocessing MEP data")
        if plot:
            print(" Creating MEP plots ...")

    for chan in channels:
        d[f"mep_raw_data_time_{chan}"] = []
        d[f"mep_filt_data_time_{chan}"] = []
        d[f"mep_raw_data_{chan}"] = []
        d[f"mep_filt_data_{chan}"] = []
        d[f"p2p_brainsight_{chan}"] = []
        d[f"p2p_{chan}"] = []
        d[f"mep_latency_{chan}"] = []

        for i in range(n_stims):
            if plot:
                fn_channel = os.path.join(os.path.split(subject.exp[exp_idx]["fn_data"][0])[0], "plots", str(chan))
                fn_plot = os.path.join(fn_channel, f"mep_{i:04}")
                os.makedirs(fn_channel, exist_ok=True)

            # filter data and calculate p2p values
            p2p, mep_filt_data, latency = pynibs.calc_p2p(sweep=d_bs[f"EMG Data {chan}"][i],
                                                          tms_pulse_time=d_bs[f"Offset"][i],
                                                          sampling_rate=1000 / d_bs["EMG Res."][i],
                                                          start_mep=start_mep_ms, end_mep=end_mep_ms,
                                                          measurement_start_time=float(d["EMG Start"][i]),
                                                          fn_plot=fn_plot)

            d[f"mep_raw_data_time_{chan}"].append(np.arange(d_bs["EMG Start"][i],
                                                            d_bs["EMG End"][i], d_bs["EMG Res."][i]))
            d[f"mep_filt_data_time_{chan}"].append(
                    np.arange(d_bs["EMG Start"][i], d_bs["EMG End"][i], d_bs["EMG Res."][i]))
            d[f"mep_raw_data_{chan}"].append(d_bs[f"EMG Data {chan}"][i])
            d[f"mep_filt_data_{chan}"].append(mep_filt_data)
            d[f"p2p_brainsight_{chan}"].append(d_bs[f"EMG Peak-to-peak {chan}"][i])
            d[f"p2p_{chan}"].append(p2p)
            d[f"mep_latency_{chan}"].append(latency)

    # set filename of experiment.hdf5
    if subject.exp[exp_idx]["fn_exp_hdf5"] is not None or subject.exp[exp_idx]["fn_exp_hdf5"] != []:
        fn_exp_hdf5 = subject.exp[exp_idx]["fn_exp_hdf5"][0]

    elif subject.exp[exp_idx]["fn_exp_csv"] is not None or subject.exp[exp_idx]["fn_exp_csv"] != []:
        fn_exp_hdf5 = subject.exp[exp_idx]["fn_exp_csv"][0]

    elif fn_exp_hdf5 is None or fn_exp_hdf5 == []:
        fn_exp_hdf5 = os.path.join(subject.subject_folder, "exp", exp_idx, "experiment.hdf5")

    # remove coil position outliers (in case of conditions)
    #######################################################
    if coil_outlier_corr_cond:
        if verbose:
            print("Removing coil position outliers")
        d = pynibs.coil_outlier_correction_cond(exp=d,
                                         outlier_angle=5.,
                                         outlier_loc=3.,
                                         fn_exp_out=fn_exp_hdf5)

    # perform coil <-> head distance correction
    ###########################################
    if coil_distance_corr:
        if verbose:
            print("Performing coil <-> head distance correction")
        d = pynibs.coil_distance_correction(exp=d,
                                     fn_geo_hdf5=fn_mesh_hdf5,
                                     remove_coil_skin_distance_outlier=remove_coil_skin_distance_outlier,
                                     fn_plot=os.path.split(fn_exp_hdf5)[0])

    # create dictionary of stimulation data
    #######################################
    d_stim_data = dict()
    d_stim_data["coil_0"] = d["coil_0"]
    d_stim_data["coil_1"] = d["coil_1"]
    d_stim_data["coil_mean"] = d["coil_mean"]
    d_stim_data["number"] = d["number"]
    d_stim_data["condition"] = d["condition"]
    d_stim_data["current"] = d["current"]
    d_stim_data["date"] = d["date"]
    d_stim_data["time"] = d["time"]
    d_stim_data["Creation Cause"] = d["Creation Cause"]
    d_stim_data["Offset"] = d["Offset"]

    # create dictionary of raw physiological data
    #############################################
    d_phys_data_raw = dict()
    d_phys_data_raw["EMG Start"] = d["EMG Start"]
    d_phys_data_raw["EMG End"] = d["EMG End"]
    d_phys_data_raw["EMG Res."] = d["EMG Res."]
    d_phys_data_raw["EMG Channels"] = d["EMG Channels"]
    d_phys_data_raw["EMG Window Start"] = d["EMG Window Start"]
    d_phys_data_raw["EMG Window End"] = d["EMG Window End"]

    for chan in channels:
        d_phys_data_raw[f"mep_raw_data_time_{chan}"] = d[f"mep_raw_data_time_{chan}"]
        d_phys_data_raw[f"mep_raw_data_{chan}"] = d[f"mep_raw_data_{chan}"]

    # create dictionary of postprocessed physiological data
    #######################################################
    d_phys_data_postproc = dict()

    for chan in channels:
        d_phys_data_postproc[f"mep_filt_data_time_{chan}"] = d[f"mep_filt_data_time_{chan}"]
        d_phys_data_postproc[f"mep_filt_data_{chan}"] = d[f"mep_filt_data_{chan}"]
        d_phys_data_postproc[f"p2p_brainsight_{chan}"] = d[f"p2p_brainsight_{chan}"]
        d_phys_data_postproc[f"p2p_{chan}"] = d[f"p2p_{chan}"]
        d_phys_data_postproc[f"mep_latency_{chan}"] = d[f"mep_latency_{chan}"]

    # create pandas dataframes from dicts
    #####################################
    df_stim_data = pd.DataFrame.from_dict(d_stim_data)
    df_phys_data_raw = pd.DataFrame.from_dict(d_phys_data_raw)
    df_phys_data_postproc = pd.DataFrame.from_dict(d_phys_data_postproc)

    # save in .hdf5 file
    if verbose:
        print(f"Saving experimental data to file: {fn_exp_hdf5}")
    df_stim_data.to_hdf(fn_exp_hdf5, "stim_data")
    df_phys_data_raw.to_hdf(fn_exp_hdf5, "phys_data/raw/EMG")
    df_phys_data_postproc.to_hdf(fn_exp_hdf5, "phys_data/postproc/EMG")

    # plot finally used mep data
    ############################
    ''' # done directly in 'calc_p2p' now to avoid code duplication
    if plot:
        if verbose:
            print("Creating MEP plots ...")
        sampling_rate = 1000 / d_bs["EMG Res."][0]

        # Compute start and stop idx according to sampling rate
        start_mep = int((18 / 1000.) * sampling_rate)
        end_mep = int((35 / 1000.) * sampling_rate)

        # compute tms pulse idx in samplerate space
        tms_pulse_sample = int(d[f"Offset"][0] * sampling_rate)

        for i_mep in tqdm(range(len(d["coil_0"]))):
            for i_channel, channel in enumerate(channels):
                sweep = d[f"mep_raw_data_{channel}"][i_mep]
                sweep_filt = d[f"mep_filt_data_{channel}"][i_mep]

                # get index for begin of mep search window
                # index_max_begin = np.argmin(sweep) + start_mep  # get TMS impulse # int(0.221 / 0.4 * sweep.size)
                # beginning of mep search window
                srch_win_start = tms_pulse_sample + start_mep  # get TMS impulse # in

                if srch_win_start >= sweep_filt.size:
                    srch_win_start = sweep_filt.size - 1

                # index_max_end = sweep_filt.size  # int(0.234 / 0.4 * sweep.size) + 1
                srch_win_end = srch_win_start + end_mep

                fn_channel = os.path.join(os.path.split(subject.exp[exp_idx]["fn_data"][0][0])[0], "plots",
                                          str(channel))

                if not os.path.exists(fn_channel):
                    os.makedirs(fn_channel)

                fn_plot = os.path.join(fn_channel, f"mep_{i_mep:04}")
                t = np.arange(len(sweep)) / sampling_rate
                sweep_min_idx = np.argmin(sweep_filt[srch_win_start:srch_win_end]) + srch_win_start
                sweep_max_idx = np.argmax(sweep_filt[srch_win_start:srch_win_end]) + srch_win_start

                plt.figure(figsize=[4.07, 3.52])
                plt.plot(t, sweep)
                plt.plot(t, sweep_filt)
                plt.scatter(t[sweep_min_idx], sweep_filt[sweep_min_idx], 15, color="r")
                plt.scatter(t[sweep_max_idx], sweep_filt[sweep_max_idx], 15, color="r")
                plt.plot(t, np.ones(len(t)) * sweep_filt[sweep_min_idx], linestyle="--", color="r", linewidth=1)
                plt.plot(t, np.ones(len(t)) * sweep_filt[sweep_max_idx], linestyle="--", color="r", linewidth=1)
                plt.grid()
                plt.legend(["raw", "filtered", "p2p"], loc='upper right')

                plt.xlim([np.max((d[f"Offset"][0] - 0.01, np.min(t))),
                          np.min((t[tms_pulse_sample + end_mep] + 0.1, np.max(t)))])
                plt.ylim([-1.1 * np.abs(sweep_filt[sweep_min_idx]), 1.1 * np.abs(sweep_filt[sweep_max_idx])])

                plt.xlabel("time in s", fontsize=11)
                plt.ylabel("MEP in mV", fontsize=11)
                plt.tight_layout()

                plt.savefig(fn_plot, dpi=200, transparent=True)
                plt.close()

    '''
