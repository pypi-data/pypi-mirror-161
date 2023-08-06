""" Functions to import data from Localite TMS Navigator """
import os
from xml.etree import ElementTree as xmlt

import h5py
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm

import pynibs

def get_tms_elements(xml_paths, verbose=False):
    """
    Read needed elements out of the tms-xml-file.

    Parameters
    ----------
    xml_paths : list of str or str
        Paths to coil0-file and optionally coil1-file if there is no coil1-file, use empty string
    verbose : bool, optional, default: False
        Print output messages

    Returns
    -------
    coils_array : nparray of float [3xNx4x4]
        Coil0, coil1 and mean-value of N 4x4 coil-arrays
    ts_tms_lst : list of int [N]
        Timestamps of valid tms-measurements
    current_lst : list of int [N]
        Measured currents
    idx_invalid : list of int
        List of indices of invalid coil positions (w.r.t. all timestamps incl invalid)
    """
    if isinstance(xml_paths, str):
        xml_paths = [xml_paths]
    # handle case if there is no coil1
    if len(xml_paths) > 1 and not xml_paths[1]:
        xml_paths[1] = xml_paths[0]
    if len(xml_paths) == 1:
        xml_paths.append(xml_paths[0])

    # allocate new array and lists
    coils_array, ts_tms_lst, current_lst = np.empty([3, 0, 4, 4]), [], []

    # parse XML document
    coil0_tree, coil1_tree = xmlt.parse(xml_paths[0]), xmlt.parse(xml_paths[1])
    coil0_root, coil1_root = coil0_tree.getroot(), coil1_tree.getroot()

    # iterate over all 'TriggerMarker' tags
    i_stim = 0
    idx_invalid = []

    for coil0_tm, coil1_tm in zip(coil0_root.iter('TriggerMarker'), coil1_root.iter('TriggerMarker')):
        coil_array = np.empty([0, 1, 4, 4])

        # get tag were the matrix is
        coil0_ma, coil1_ma = coil0_tm.find('Matrix4D'), coil1_tm.find('Matrix4D')

        # get coil0
        coil_array = np.append(coil_array, read_coil(coil0_ma), axis=0)

        # if present, get coil1
        if xml_paths[0] == xml_paths[1]:
            coil_array = np.append(coil_array, np.identity(4)[np.newaxis, np.newaxis, :, :], axis=0)
        else:
            coil_array = np.append(coil_array, read_coil(coil1_ma), axis=0)

        # check for not valid coils and calculate mean value
        if not np.allclose(coil_array[0, 0, :, :], np.identity(4)) and \
                not np.allclose(coil_array[1, 0, :, :], np.identity(4)):
            coil_array = np.append(coil_array,
                                   np.expand_dims((coil_array[0, :, :, :] + coil_array[1, :, :, :]) / 2, axis=0),
                                   axis=0)
        elif np.allclose(coil_array[0, 0, :, :], np.identity(4)) and not np.allclose(coil_array[1, 0, :, :],
                                                                                     np.identity(4)):
            coil_array = np.append(coil_array, np.expand_dims(coil_array[1, :, :, :], axis=0), axis=0)
        elif np.allclose(coil_array[1, 0, :, :], np.identity(4)) and not np.allclose(coil_array[0, 0, :, :],
                                                                                     np.identity(4)):
            coil_array = np.append(coil_array, np.expand_dims(coil_array[0, :, :, :], axis=0), axis=0)
        else:
            idx_invalid.append(i_stim)
            if verbose:
                print("Removing untracked (and possibly accidental) coil position #{} (identity matrix)".format(i_stim))
            i_stim += 1
            continue

        # print(i_stim)
        i_stim += 1

        coils_array = np.append(coils_array, coil_array, axis=1)

        # get timestamp
        ts_tms_lst.append(int(coil0_tm.get('recordingTime')))

        # get current
        xml_rv = coil0_tm.find('ResponseValues')
        xml_va = xml_rv.findall('Value')

        # if valueA is NaN, compute dI/dt with amplitudeA
        if xml_va[0].get('response') == 'NaN':
            current_lst.append(str(round(float(xml_va[2].get('response')) * 1.4461)))  # was 1.38
        else:
            current_lst.append(xml_va[0].get('response'))

    return [coils_array, ts_tms_lst, current_lst, idx_invalid]


def read_coil(xml_ma):
    """
    Read coil-data from xml element.

    Parameters
    ----------
    xml_ma : xml-element
        Coil data

    Returns
    -------
    coil : nparray of float [4x4]
        Coil elements
    """
    # index2 for all coils from triggermarker
    coil = np.empty([1, 1, 4, 4])
    for coil_index1 in range(4):
        for coil_index2 in range(4):
            coil[0, 0, coil_index1, coil_index2] = (float(xml_ma.get('data' + str(coil_index1) + str(coil_index2))))
    return coil


def match_instrument_marker_file(xml_paths, im_path):
    """ Assign right instrument marker condition to every triggermarker (get instrument marker out of file).

    Parameters
    ----------
    xml_paths : list of str
        Paths to coil0-file and optionally coil1-file if there is no coil1-file, use empty string
    im_path : str
        Path to instrument-marker-file

    Returns
    -------
    coil_cond_lst : list of str
        Right conditions
    """

    tm_array, tms_time_arr, tms_cur_arr, tms_idx_invalid = get_tms_elements(xml_paths)
    # get coil mean value
    tm_array = tm_array[2]
    im_array, im_cond_lst = get_instrument_marker(im_path)

    # get indices of conditions
    im_index_lst, drop_idx = match_tm_to_im(tm_array, im_array, tms_time_arr, tms_cur_arr)

    # list to save conditions
    coil_cond_lst = []

    for cond_index in im_index_lst:
        coil_cond_lst.append(im_cond_lst[cond_index])
    return coil_cond_lst, drop_idx


def match_instrument_marker_string(xml_paths, condition_order):
    """
    Assign right instrument marker condition to every triggermarker (get instrument marker out of list of strings).

    Parameters
    ----------
    xml_paths : list of str
        Paths to coil0-file and optionally coil1-file if there is no coil1-file, use empty string
    condition_order : list of str
        Conditions in the right order

    Returns
    -------
    coil_cond_lst : list of strings containing the right conditions
    """
    drop_idx = []
    max_time_dif = 90000
    max_mep_dif = 7

    tm_pos_arr, tms_time_arr, tms_cur_arr, tms_idx_invalid = get_tms_elements(xml_paths)

    # get coil mean value
    tm_pos_arr = tm_pos_arr[2, :, :, :]

    # list for condition results
    conditions = []

    # index of instrument marker
    cond_idx = 0

    # iterate over all trigger marker
    for tm_index in range((tm_pos_arr.shape[0]) - 1):
        conditions.append(condition_order[cond_idx])
        if float(tms_cur_arr[tm_index]) == 0.:
            drop_idx.append(tm_index)
        tm_matrix_post = tm_pos_arr[tm_index + 1, :, :]
        tm_matrix = tm_pos_arr[tm_index, :, :]

        same_tm = arrays_similar(tm_matrix, tm_matrix_post)
        time_dif = tms_time_arr[tm_index + 1] - tms_time_arr[tm_index] > max_time_dif
        amp_dif = np.abs(float(tms_cur_arr[tm_index + 1]) - float(tms_cur_arr[tm_index])) > max_mep_dif
        if not same_tm and time_dif and amp_dif:
            arrays_similar(tm_matrix, tm_matrix_post)
            cond_idx += 1
            if cond_idx == len(condition_order):
                raise ValueError("Too many coil conditions found!")

    # assign last element to very last element
    conditions.append(conditions[-1])
    if cond_idx != len(condition_order) - 1:
        raise ValueError("Did not find all coil positions!")

    return conditions, drop_idx


def arrays_similar(tm_matrix, tm_matrix_post,  # , tm_mean_last,
                   pos_rtol=0, pos_atol=3.6, ang_rtol=.1, ang_atol=.1):
    """
    Compares angles and position for similarity.

    Splitting the comparison into angles and position is angebracht, as the absolute tolereance (atol) should be
    different for angles (degree) and position (millimeter) comparisons.

    Parameters:
    -----------
    tm_matrix: array-like, shape = (4,4)
        TMS Navigator triggermarker or instrument marker array

    tm_matrix_post: array-like, shape = (4,4)
        TMS Navigator triggermarker or instrument marker array

    tm_mean_last: array-like, shape = (4,4), optional
        Mean TMS Navigator triggermarker or instrument marker array for n zaps

    """
    # last_pos = True
    # last_ang = True
    # position
    pos = np.allclose(tm_matrix[0:3, 3], tm_matrix_post[0:3, 3], rtol=pos_rtol, atol=pos_atol)

    # angles
    ang = np.allclose(tm_matrix[0:3, 0:2], tm_matrix_post[0:3, 0:2], rtol=ang_rtol, atol=ang_atol)

    # if tm_mean_last is not None:
    #     last_pos = np.allclose(tm_matrix[0:3, 3], tm_mean_last[0:3, 3], rtol=pos_rtol, atol=pos_atol)
    #     last_ang = np.allclose(tm_matrix[0:3, 0:2], tm_mean_last[0:3, 0:2], rtol=ang_rtol, atol=ang_atol)

    next_same = pos and ang
    # last_same = last_pos and last_ang
    return next_same


def match_tm_to_im(tm_array, im_array, tms_time_arr, tms_cur_arr):
    """
    Match triggermarker with instrumentmarker and get index of best fitting instrumentmarker.


    Parameters
    ----------
    tm_array : ndarray of float [Nx4x4]
        Mean-value of Nx4x4 coil matrices
    im_array : ndarray of float [Mx4x4]
        Instrument-marker-matrices

    Returns
    -------
    im_index_lst : list of int
        Indices of best fitting instrumentmarkers
    """
    max_time_dif = (tms_time_arr[1] - tms_time_arr[0]) * 3
    # max_mep_dif = 9

    im_index_lst = []
    drop_idx = []

    for tm_index in range(tm_array.shape[0]):
        # after first zap, check time diff
        if tm_index > 0:
            if tms_time_arr[tm_index] - tms_time_arr[tm_index - 1] < max_time_dif:
                im_index_lst.append(im_index_lst[-1])
                continue

        allclose_index_lst = []
        diff_small = []

        atol_ori = 0.4
        atol_pos = 3
        repeat = False

        # tm = tm_array[tm_index, :, :]

        # proc_diffs = np.argmin[procrustes(tm, im_array[i])[2] for i in range(im_array.shape[0])]

        # diffs = np.abs(tm - im_array)
        # diffs[0:3, 0:3] /= np.max(diffs[:, 0:3, 0:4], axis=0)
        # best_fit = np.argmin(np.array([np.sum(diffs[i]) for i in range(len(diffs))]))
        # small_diff_ori = int(np.argmin(np.array([np.sum(diffs[i][0:3, 0:3]) for i in range(len(diffs))])))
        # small_diff_pos = int(np.argmin(np.array([np.sum(diffs[i][0:3, 3]) for i in range(len(diffs))])))
        # a = rot_to_quat(tm[:3,:3])[1:]
        # b = [quaternion_diff(a, rot_to_quat(im_array[i, :3, :3])[1:]) for i in range(im_array.shape[0])]

        while not allclose_index_lst:
            if repeat:
                print(('Warning: Trigger marker #{:0>4}: No matching instrument marker within '
                       'atol_ori={} and atol_pos={}! Increasing tolerances by 0.1 and 0.5.'
                       .format(tm_index, atol_ori, atol_pos)))

                atol_ori = atol_ori + 0.1
                atol_pos = atol_pos + 0.5

            for im_index in range(im_array.shape[0]):

                # # check if arrays are close
                # if np.allclose(tm_array[tm_index, :, :], im_array[im_index, :, :], rtol=rtol):
                #     allclose_index_lst.append(im_index)

                # check if arrays are close
                diff = np.abs(tm_array[tm_index, :, :] - im_array[im_index, :, :])

                if (diff[0:3, 0:3] < atol_ori).all() and (diff[0:3, 3] < atol_pos).all():
                    diff_small.append(diff)
                    allclose_index_lst.append(im_index)

            if not allclose_index_lst:
                allclose_index_lst.append(-1)
                # repeat = True

        # if multiple arrays are close, choose value, with smallest difference
        if len(allclose_index_lst) > 1:
            smallest_value_index = int(np.argmin(np.array([np.sum(diff_small[i]) for i in range(len(diff_small))])))
            small_diff_ori = int(np.argmin(np.array([np.sum(diff_small[i][0:3, 0:3]) for i in range(len(diff_small))])))
            small_diff_pos = int(np.argmin(np.array([np.sum(diff_small[i][0:3, 3]) for i in range(len(diff_small))])))
            if not small_diff_ori == small_diff_pos:
                #     print allclose_index_lst
                print("Warning: Triggermarker #{:0>4}: " \
                      "Cannot decide for instrument marker , dropping this one. ".format(tm_index))
            #     drop_idx.append(tm_index)
            # im_index_lst.append(im_index_lst[-1])
            # else:
            # assert best_fit == allclose_index_lst[smallest_value_index]
            im_index_lst.append(allclose_index_lst[smallest_value_index])

        else:
            # assert best_fit == allclose_index_lst[0]
            im_index_lst.append(allclose_index_lst[0])

            # # if multile arrays are close, choose value,
            # where the difference to the instrument marker has the smallest
            # # frobenius norm
            # if len(allclose_index_lst) > 1:
            #     smallest_value_index = int(np.argmin(np.linalg.norm(im_array[allclose_index_lst, :, :] -
            #                                                         tm_array[tm_index, :, :], axis=(1, 2))))
            #     im_index_lst.append(allclose_index_lst[smallest_value_index])
            # else:
            #     im_index_lst.append(allclose_index_lst[0])

    return im_index_lst, drop_idx


def get_instrument_marker(im_path):
    return get_marker(im_path, 'InstrumentMarker')[:2]


def get_marker(im_path, markertype):
    """
    Read instrument-marker and conditions from Neuronavigator .xml-file.

    Parameters
    ----------
    im_path : str or list of str
        Path to instrument-marker-file

    Returns
    -------
    im_array : np.array of float [Mx4x4]
        Instrument-marker-matrices
    im_cond_lst : list of str
        Labels of the instrument-marker-conditions
    im_marker_times : list of float
        Onset times
    """
    if isinstance(im_path, str):
        return get_single_marker_file(im_path, markertype)

    elif isinstance(im_path, list):
        # if multiple triggermarker files are provided, pick a marker with data
        im_array, marker_descriptions, marker_times = [], [], []

        # get data from all files
        for im in im_path:
            im_array_t, marker_descriptions, marker_times = get_single_marker_file(im, markertype)
            im_array.append(im_array_t)

        # get indices for all files where markers are empty
        empty_arr = []
        for arr in im_array:  # arr = im_array[0]
            empty_arr.append(markers_are_empty(arr))
        # assert np.all(np.sum(np.array(empty_arr).astype(int), axis=0) == 1)

        # go through the zaps and pick a marker with data.
        idx = []
        tmp = 0
        for i in range(len(im_array[0])):
            for j in range(len(im_array)):
                if not empty_arr[j][i]:
                    tmp = j
                # if all are empty, just use the last value (is empty anyway)
            idx.append(tmp)  # append

        # build marker idx based on idx
        final_arr = []
        for it, i in enumerate(idx):
            final_arr.append(im_array[i][it])
        return np.array(final_arr), marker_descriptions, marker_times
    else:
        raise NotImplementedError(f"type {type(im_path)} not implemented.")


def markers_are_empty(arr):
    return [marker_is_empty(arr[i, :, :]) for i in range(arr.shape[0])]


def marker_is_empty(arr):
    return np.all(arr == np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))


def get_single_marker_file(im_path, markertype):
    """
        Read instrument-marker and conditions from Neuronavigator .xml-file.

        Parameters
        ----------
        im_path : str or list of str
            Path to instrument-marker-file

        Returns
        -------
        im_array : np.array of float [Mx4x4]
            Instrument-marker-matrices
        im_cond_lst : list of str
            Labels of the instrument-marker-conditions
        """
    im_array = np.empty([0, 4, 4])
    marker_descriptions = []
    marker_times = []
    # parse XML document
    im_tree = xmlt.parse(im_path)
    im_root = im_tree.getroot()
    # iterate over all 'InstrumentMarker' tags
    for marker_i in im_root.iter(markertype):
        marker_array = np.empty([1, 4, 4])
        # get tag were the matrix is
        if markertype == 'InstrumentMarker':
            marker_object = marker_i.find('Marker')
            marker_descriptions.append(marker_object.get('description'))
            matrix4d = marker_object.find('Matrix4D')

        elif markertype == 'TriggerMarker':
            matrix4d = marker_i.find('Matrix4D')
            marker_descriptions.append(marker_i.get('description'))
            marker_times.append(marker_i.get('recordingTime'))
        # get values
        for im_index1 in range(4):
            for im_index2 in range(4):
                marker_array[0, im_index1, im_index2] = (float(matrix4d.get('data' + str(im_index1) + str(im_index2))))
        im_array = np.append(im_array, marker_array, axis=0)

    return im_array, marker_descriptions, marker_times


def read_triggermarker_localite(fn_xml):
    """
    Read instrument-marker and conditions from neuronavigator .xml-file.

    Parameters
    ----------
    fn_xml : str
        Path to TriggerMarker.xml file
        (e.g. Subject_0/Sessions/Session_YYYYMMDDHHMMSS/TMSTrigger/TriggerMarkers_Coil1_YYYYMMDDHHMMSS.xml)

    Returns
    -------
    list of
        m_nnav : ndarray of float [4x4xN]
            Neuronavigation coordinates of N stimuli (4x4 matrices)
        didt : ndarray of float [N]
            Rate of change of coil current in (A/us)
        stim_int : ndarray of float [N]
            Stimulator intensity in (%)
        descr : list of str [N]
            Labels of the instrument-marker-conditions
        rec_time : list of str [N]
            Recording time in ms
    """

    m_nnav = np.empty([4, 4, 0])
    descr = []
    stim_int = []
    didt = []
    rec_time = []

    # parse XML document
    im_tree = xmlt.parse(fn_xml)
    im_root = im_tree.getroot()

    # iterate over all 'InstrumentMarker' tags
    for im_iter in im_root.iter('TriggerMarker'):
        m = np.empty([4, 4, 1])

        # read description
        descr.append(im_iter.get('description'))
        rec_time.append(im_iter.get('recordingTime'))

        # read di/dt and stimulator intensity
        im_rv = im_iter.find('ResponseValues').findall('Value')

        for _im_rv in im_rv:
            # di/dt
            if _im_rv.get('key') == "valueA":
                didt.append(float(_im_rv.get('response')))
            # stimulator intensity
            elif _im_rv.get('key') == "amplitudeA":
                stim_int.append(float(_im_rv.get('response')))

        # read matrix
        im_ma = im_iter.find('Matrix4D')

        for im_index1 in range(4):
            for im_index2 in range(4):
                m[im_index1, im_index2, 0] = (float(im_ma.get('data' + str(im_index1) + str(im_index2))))
        m_nnav = np.append(m_nnav, m, axis=2)

    didt = np.array(didt)
    stim_int = np.array(stim_int)

    return [m_nnav, didt, stim_int, descr, rec_time]


def merge_exp_data_localite(subject, coil_outlier_corr_cond, remove_coil_skin_distance_outlier, coil_distance_corr,
                            exp_idx=0, mesh_idx=0, drop_mep_idx=None, mep_onsets=None, cfs_data_column=None,
                            channels=None, verbose=False, plot=False):
    """
    Merge the TMS coil positions (TriggerMarker) and the mep data into an experiment.hdf5 file.

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
    drop_mep_idx : List of int or None
        Which MEPs to remove before matching.
    mep_onsets : List of int or None (Default: None)
        If there are multiple .cfs per TMS Navigator sessions, onsets in [ms] of .cfs. E.g.: [0, 71186].
    cfs_data_column : int or list of int
        Column(s) of dataset in .cfs file.
    channels : list of str
        List of channel names
    verbose : bool
        Plot output messages
    plot : bool, optional, default: False
        Plot MEPs and p2p evaluation
    """
    if channels is None:
        channels = ["channel_0"]
    mep_paths_lst = subject.exp[exp_idx]['fn_data']
    tms_paths_lst = subject.exp[exp_idx]['fn_tms_nav']
    im_lst = subject.exp[exp_idx]['cond']
    nii_exp_path_lst = subject.exp[exp_idx]['fn_mri_nii']
    nii_conform_path = os.path.join(subject.mesh[mesh_idx]["mesh_folder"], subject.mesh[mesh_idx]["fn_mri_conform"])
    fn_exp_hdf5 = subject.exp[exp_idx]['fn_exp_hdf5'][0]
    fn_coil = subject.exp[exp_idx]['fn_coil']
    fn_mesh_hdf5 = subject.mesh[mesh_idx]['fn_mesh_hdf5']
    temp_dir = os.path.join(os.path.split(subject.exp[exp_idx]['fn_exp_hdf5'][0])[0],
                            "nnav2simnibs",
                            f"mesh_{mesh_idx}")
    subject_obj = subject

    # allocate dict
    dict_lst = []

    # handle instrument marker
    if len(im_lst) < len(tms_paths_lst):
        for _ in range(len(tms_paths_lst)):
            im_lst.append(im_lst[0])

    # handle coil serial numbers
    coil_sn_lst = pynibs.get_coil_sn_lst(fn_coil)

    # get TMS pulse onset
    tms_pulse_time = subject.exp[exp_idx]['tms_pulse_time']

    # iterate over all files
    if mep_onsets is None:
        mep_onsets = [None] * len(mep_paths_lst)

    len_conds = []

    for cfs_paths, tms_paths, coil_sn, nii_exp_path, im, mep_onsets \
            in zip(mep_paths_lst, tms_paths_lst, coil_sn_lst, nii_exp_path_lst, im_lst, mep_onsets):
        dict_lst.extend(pynibs.combine_nnav_mep(xml_paths=tms_paths,
                                         cfs_paths=cfs_paths,
                                         im=im,
                                         coil_sn=coil_sn,
                                         nii_exp_path=nii_exp_path,
                                         nii_conform_path=nii_conform_path,
                                         patient_id=subject.id,
                                         tms_pulse_time=tms_pulse_time,
                                         drop_mep_idx=drop_mep_idx,
                                         mep_onsets=mep_onsets,
                                         cfs_data_column=cfs_data_column,
                                         temp_dir=temp_dir,
                                         channels=channels,
                                         nnav_system=subject_obj.exp[exp_idx]["nnav_system"],
                                         mesh_approach=subject_obj.mesh[mesh_idx]["approach"],
                                         plot=plot))

        if len(len_conds) == 0:
            len_conds.append(len(dict_lst))
        else:
            len_conds.append(len(dict_lst) - len_conds[-1])

    # convert list of dict to dict of list
    results_dct = pynibs.list2dict(dict_lst)

    # check if we have a single pulse TMS experiments where every pulse is one condition
    single_pulse_experiment = np.zeros(len(len_conds))

    start = 0
    stop = len_conds[0]
    for i in range(len(len_conds)):
        if len(np.unique(np.array(results_dct["condition"])[start:stop])) == len_conds[i]:
            single_pulse_experiment[i] = True

        if i < (len(len_conds) - 1):
            start = stop
            stop = stop + len_conds[i + 1]

    # redefine condition vector because in case of multiple .cfs files and .xml files the conditions may double
    if single_pulse_experiment.all():
        results_dct["condition"] = np.arange(len(dict_lst))

    # reformat coil positions to 4x4 matrices
    coil_0 = np.zeros((4, 4, len(dict_lst)))
    coil_1 = np.zeros((4, 4, len(dict_lst)))
    coil_mean = np.zeros((4, 4, len(dict_lst)))

    # coil_0[3, 3, :] = 1
    # coil_1[3, 3, :] = 1
    # coil_mean[3, 3, :] = 1

    for m in range(4):
        for n in range(4):
            coil_0[m, n, :] = results_dct[f"coil0_{m}{n}"]
            coil_1[m, n, :] = results_dct[f"coil1_{m}{n}"]
            coil_mean[m, n, :] = results_dct[f"coil_mean_{m}{n}"]

            results_dct.pop(f"coil0_{m}{n}")
            results_dct.pop(f"coil1_{m}{n}")
            results_dct.pop(f"coil_mean_{m}{n}")

    coil_0 = np.split(coil_0, coil_0.shape[2], axis=2)
    coil_1 = np.split(coil_1, coil_1.shape[2], axis=2)
    coil_mean = np.split(coil_mean, coil_mean.shape[2], axis=2)

    coil_0 = [c.reshape((4, 4)) for c in coil_0]
    coil_1 = [c.reshape((4, 4)) for c in coil_1]
    coil_mean = [c.reshape((4, 4)) for c in coil_mean]

    results_dct["coil_0"] = coil_0
    results_dct["coil_1"] = coil_1
    results_dct["coil_mean"] = coil_mean

    results_dct["current"] = [float(c) for c in results_dct["current"]]

    # coil outlier correction
    if subject_obj.exp[exp_idx]["fn_exp_hdf5"] is not None or subject_obj.exp[exp_idx]["fn_exp_hdf5"] != []:
        fn_exp_hdf5 = subject_obj.exp[exp_idx]["fn_exp_hdf5"][0]

    elif subject_obj.exp[exp_idx]["fn_exp_csv"] is not None or subject_obj.exp[exp_idx]["fn_exp_csv"] != []:
        fn_exp_hdf5 = subject_obj.exp[exp_idx]["fn_exp_csv"][0]

    elif fn_exp_hdf5 is None or fn_exp_hdf5 == []:
        fn_exp_hdf5 = os.path.join(subject_obj.subject_folder, "exp", exp_idx, "experiment.hdf5")

    # remove coil position outliers (in case of conditions)
    #######################################################
    if coil_outlier_corr_cond:
        print("Removing coil position outliers")
        results_dct = pynibs.coil_outlier_correction_cond(exp=results_dct,
                                                   outlier_angle=5.,
                                                   outlier_loc=3.,
                                                   fn_exp_out=fn_exp_hdf5)

    # perform coil <-> head distance correction
    ###########################################
    if coil_distance_corr:
        print("Performing coil <-> head distance correction")
        results_dct = pynibs.coil_distance_correction(exp=results_dct,
                                               fn_geo_hdf5=fn_mesh_hdf5,
                                               remove_coil_skin_distance_outlier=remove_coil_skin_distance_outlier,
                                               fn_plot=os.path.split(fn_exp_hdf5)[0])

    # plot finally used mep data
    ############################
    if plot:
        print("Creating MEP plots ...")
        sampling_rate = pynibs.get_mep_sampling_rate(cfs_paths[0])

        # Compute start and stop idx according to sampling rate
        start_mep = int((20 / 1000.) * sampling_rate)
        end_mep = int((35 / 1000.) * sampling_rate)

        # compute tms pulse idx in samplerate space
        tms_pulse_sample = int(tms_pulse_time * sampling_rate)

        for i_mep in tqdm(range(len(results_dct["mep_raw_data"]))):
            for i_channel, channel in enumerate(channels):
                # TODO: merge this code with calc_p2p
                sweep = results_dct["mep_raw_data"][i_mep][i_channel, :]
                sweep_filt = results_dct["mep_filt_data"][i_mep][i_channel, :]

                # get index for begin of mep search window
                # index_max_begin = np.argmin(sweep) + start_mep  # get TMS impulse # int(0.221 / 0.4 * sweep.size)
                # beginning of mep search window
                srch_win_start = tms_pulse_sample + start_mep  # get TMS impulse # in

                if srch_win_start >= sweep_filt.size:
                    srch_win_start = sweep_filt.size - 1

                # index_max_end = sweep_filt.size  # int(0.234 / 0.4 * sweep.size) + 1
                srch_win_end = srch_win_start + end_mep - start_mep

                fn_channel = os.path.join(os.path.split(cfs_paths[0])[0], "plots", channel)

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

                plt.xlim([np.max((tms_pulse_time - 0.01, np.min(t))),
                          np.min((t[tms_pulse_sample + end_mep] + 0.1, np.max(t)))])
                plt.ylim([-1.1 * np.abs(sweep_filt[sweep_min_idx]), 1.1 * np.abs(sweep_filt[sweep_max_idx])])

                plt.xlabel("time in s", fontsize=11)
                plt.ylabel("MEP in mV", fontsize=11)
                plt.tight_layout()

                plt.savefig(fn_plot, dpi=200, transparent=True)
                plt.close()

    # Write experimental data to hdf5
    ###############################################
    # stimulation data
    df_stim_data = pd.DataFrame.from_dict(results_dct)
    df_stim_data = df_stim_data.drop(columns=["mep"])
    df_stim_data = df_stim_data.drop(columns=["mep_raw_data_time"])
    df_stim_data = df_stim_data.drop(columns=["mep_filt_data"])
    df_stim_data = df_stim_data.drop(columns=["mep_raw_data"])

    # raw data
    phys_data_raw_emg = {"time": results_dct["mep_raw_data_time"]}

    for chan_idx, chan in enumerate(channels):
        results_dct[f"mep_raw_data_{chan}"] = [sweep[chan_idx, :] for sweep in results_dct["mep_raw_data"]]
        phys_data_raw_emg[f"mep_raw_data_{chan}"] = results_dct[f"mep_raw_data_{chan}"]

    df_phys_data_raw_emg = pd.DataFrame.from_dict(phys_data_raw_emg)

    # post-processed data
    phys_data_postproc_emg = {"time": results_dct["mep_raw_data_time"]}

    for chan_idx, chan in enumerate(channels):
        phys_data_postproc_emg[f"mep_filt_data_{chan}"] = [sweep[chan_idx, :] for sweep in results_dct["mep_filt_data"]]
        phys_data_postproc_emg[f"p2p_{chan}"] = [mep[chan_idx] for mep in results_dct["mep"]]
        phys_data_postproc_emg[f"mep_latency_{chan}"] = [lat[chan_idx] for lat in results_dct["mep_latency"]]

    df_phys_data_postproc_emg = pd.DataFrame.from_dict(phys_data_postproc_emg)

    # save in .hdf5 file
    df_stim_data.to_hdf(fn_exp_hdf5, "stim_data")
    # df_stim_data[['coil_mean']].to_hdf(fn_exp_hdf5, "stim_data")
    # [print(type(df_stim_data[['coil_mean']].iloc[0].values)) for i in range(df_stim_data.shape[0])]
    # df_stim_data.columns
    df_phys_data_postproc_emg.to_hdf(fn_exp_hdf5, "phys_data/postproc/EMG")
    df_phys_data_raw_emg.to_hdf(fn_exp_hdf5, "phys_data/raw/EMG")

    with h5py.File(fn_exp_hdf5, "a") as f:
        f.create_dataset(name="stim_data/info/channels", data=np.array(channels).astype("|S"))


def merge_exp_data_rt(subject, coil_outlier_corr_cond, remove_coil_skin_distance_outlier, coil_distance_corr,
                      cond=None, exp_idx=0, mesh_idx=0, drop_trial_idx=None, verbose=False, plot=False):
    """
    Merge the TMS coil positions (TriggerMarker) and the mep data into an experiment.hdf5 file.

    Parameters
    ----------
    subject : pynibs.subject
        Subject object
    exp_idx : str
        Experiment ID
    mesh_idx : str
        Mesh ID
    coil_outlier_corr_cond : bool
        Correct outlier of coil position and orientation (+-2 mm, +-3 deg) in case of conditions
    cond : string
        Which condition to analyse
    remove_coil_skin_distance_outlier : bool
        Remove outlier of coil position lying too far away from the skin surface (+- 5 mm)
    coil_distance_corr : bool
        Perform coil <-> head distance correction (coil is moved towards head surface until coil touches scalp)
    drop_trial_idx : List of int or None
        Which MEPs to remove before matching.
    verbose : bool
        Plot output messages
    plot : bool, optional, default: False
        Plot MEPs and p2p evaluation
    """
    behavior_paths_lst = subject.exp[exp_idx]['fn_data']
    tms_paths_lst = subject.exp[exp_idx]['fn_tms_nav']
    im_lst = subject.exp[exp_idx]['cond']
    nii_exp_path_lst = subject.exp[exp_idx]['fn_mri_nii']
    nii_conform_path = os.path.join(subject.mesh[mesh_idx]["mesh_folder"], subject.mesh[mesh_idx]["fn_mri_conform"])
    fn_exp_hdf5 = subject.exp[exp_idx]['fn_exp_hdf5'][0]
    fn_coil = subject.exp[exp_idx]['fn_coil']
    fn_mesh_hdf5 = subject.mesh[mesh_idx]['fn_mesh_hdf5']
    temp_dir = os.path.join(os.path.split(subject.exp[exp_idx]['fn_exp_hdf5'][0])[0],
                            "nnav2simnibs",
                            f"mesh_{mesh_idx}")
    subject_obj = subject

    # allocate dict
    dict_lst = []

    # handle instrument marker
    if len(im_lst) < len(tms_paths_lst):
        for _ in range(len(tms_paths_lst)):
            im_lst.append(im_lst[0])

    # handle coil serial numbers
    coil_sn_lst = pynibs.get_coil_sn_lst(fn_coil)

    # get TMS pulse onset
    tms_pulse_time = subject.exp[exp_idx]['tms_pulse_time']

    len_conds = []

    for behavior_paths, tms_paths, coil_sn, nii_exp_path, im \
            in zip(behavior_paths_lst, tms_paths_lst, coil_sn_lst, nii_exp_path_lst, im_lst):
        dict_lst.extend(pynibs.combine_nnav_rt(xml_paths=tms_paths,
                                        behavior_paths=behavior_paths,
                                        im=im,
                                        coil_sn=coil_sn,
                                        nii_exp_path=nii_exp_path,
                                        nii_conform_path=nii_conform_path,
                                        patient_id=subject.id,
                                        drop_trial_idx=drop_trial_idx,
                                        temp_dir=temp_dir,
                                        cond=cond,
                                        nnav_system=subject_obj.exp[exp_idx]["nnav_system"],
                                        mesh_approach=subject_obj.mesh[mesh_idx]["approach"],
                                        plot=plot))

        if len(len_conds) == 0:
            len_conds.append(len(dict_lst))
        else:
            len_conds.append(len(dict_lst) - len_conds[-1])

    # convert list of dict to dict of list
    results_dct = pynibs.list2dict(dict_lst)

    # check if we have a single pulse TMS experiments where every pulse is one condition
    single_pulse_experiment = np.zeros(len(len_conds))

    results_dct["condition"] = np.arange(len(dict_lst))

    # reformat coil positions to 4x4 matrices
    coil_0 = np.zeros((4, 4, len(dict_lst)))
    coil_1 = np.zeros((4, 4, len(dict_lst)))
    coil_mean = np.zeros((4, 4, len(dict_lst)))

    # coil_0[3, 3, :] = 1
    # coil_1[3, 3, :] = 1
    # coil_mean[3, 3, :] = 1

    for m in range(4):
        for n in range(4):
            coil_0[m, n, :] = results_dct[f"coil0_{m}{n}"]
            coil_1[m, n, :] = results_dct[f"coil1_{m}{n}"]
            coil_mean[m, n, :] = results_dct[f"coil_mean_{m}{n}"]

            results_dct.pop(f"coil0_{m}{n}")
            results_dct.pop(f"coil1_{m}{n}")
            results_dct.pop(f"coil_mean_{m}{n}")

    coil_0 = np.split(coil_0, coil_0.shape[2], axis=2)
    coil_1 = np.split(coil_1, coil_1.shape[2], axis=2)
    coil_mean = np.split(coil_mean, coil_mean.shape[2], axis=2)

    coil_0 = [c.reshape((4, 4)) for c in coil_0]
    coil_1 = [c.reshape((4, 4)) for c in coil_1]
    coil_mean = [c.reshape((4, 4)) for c in coil_mean]

    results_dct["coil_0"] = coil_0
    results_dct["coil_1"] = coil_1
    results_dct["coil_mean"] = coil_mean

    results_dct["current"] = [float(c) for c in results_dct["current"]]

    # coil outlier correction
    if subject_obj.exp[exp_idx]["fn_exp_hdf5"] is not None or subject_obj.exp[exp_idx]["fn_exp_hdf5"] != []:
        fn_exp_hdf5 = subject_obj.exp[exp_idx]["fn_exp_hdf5"][0]

    elif subject_obj.exp[exp_idx]["fn_exp_csv"] is not None or subject_obj.exp[exp_idx]["fn_exp_csv"] != []:
        fn_exp_hdf5 = subject_obj.exp[exp_idx]["fn_exp_csv"][0]

    elif fn_exp_hdf5 is None or fn_exp_hdf5 == []:
        fn_exp_hdf5 = os.path.join(subject_obj.subject_folder, "exp", exp_idx, "experiment.hdf5")

    # remove coil position outliers (in case of conditions)
    #######################################################
    if coil_outlier_corr_cond:
        print("Removing coil position outliers")
        results_dct = pynibs.coil_outlier_correction_cond(exp=results_dct,
                                                   outlier_angle=5.,
                                                   outlier_loc=3.,
                                                   fn_exp_out=fn_exp_hdf5)

    # perform coil <-> head distance correction
    ###########################################
    if coil_distance_corr:
        print("Performing coil <-> head distance correction")
        results_dct = pynibs.coil_distance_correction(exp=results_dct,
                                               fn_geo_hdf5=fn_mesh_hdf5,
                                               remove_coil_skin_distance_outlier=remove_coil_skin_distance_outlier,
                                               fn_plot=os.path.split(fn_exp_hdf5)[0])

    # plot finally used mep data
    ############################
    if plot:
        raise NotImplementedError("Plotting is not implemented yet.")

    # Write experimental data to hdf5
    ###############################################
    # stimulation data
    stim_dict = {
        'date': results_dct['date'],
        'coil_sn': results_dct['coil_sn'],
        'patient_id': results_dct['patient_id'],
        'coil_0': results_dct['coil_0'],
        'coil_1': results_dct['coil_1'],
        'coil_mean': results_dct['coil_mean'],
        'current': results_dct['current'],
        'time_tms': results_dct['ts_tms'],
    }
    df_stim_data = pd.DataFrame.from_dict(stim_dict)

    behave_dict = {
        'number': results_dct['number'],
        'rt': results_dct['rt'],
        'time_trial': results_dct['time_trial']
    }
    df_behave_data = pd.DataFrame.from_dict(behave_dict)

    # save in .hdf5 file
    df_stim_data.to_hdf(fn_exp_hdf5, "stim_data")
    df_behave_data.to_hdf(fn_exp_hdf5, "behavioral_data")
