import os
import time
import warnings

import h5py
import numpy as np
import yaml
import inspect

from lmfit import Model

from sklearn.neighbors import KernelDensity
import pynibs


def congruence_factor_curveshift_workhorse_stretch_correction(elm_idx_list, mep, mep_params, e, n_samples=100):
    """
    Worker function for congruence factor computation - call from multiprocessing.pool
    Calculates congruence factor for e = (E_mag, E_norm and/or E_tan) for given zaps and elements.
    The computations are parallelized in terms of element indices (elm_idx_list).
    n_samples are taken from fitted_mep, within the range of the mep object.

    Parameters
    ----------
    elm_idx_list : nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep : list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params : nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        - e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...]
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - e.g.: len(e) = n_cond,
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))
    n_samples : int, default=100
        Number of data points to generate discrete mep and e curves

    Returns
    -------
    congruence_factor : nparray of float [n_roi, n_datasets]
        Congruence factor in each element specified in elm_idx_list and for each input dataset
    """

    stepsize = 1e-1
    n_datasets = len(e[0])
    n_elm = len(elm_idx_list)
    n_conditions = len(mep)

    mep_params = np.array(mep_params).flatten()

    congruence_factor = np.empty((n_elm, n_datasets))

    # rearrange mep parameters to individual conditions
    mep_params_cond = []
    start_idx = 0
    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size

    del start_idx

    intensities = []
    intensities_min = []
    intensities_max = []
    stepsize_local_shift = []
    mep_curve = []

    # calculate mep curves per condition
    for i_cond in range(n_conditions):
        intensities.append(np.linspace(mep[i_cond].x_limits[0], mep[i_cond].x_limits[1], n_samples))
        mep_curve.append(mep[i_cond].eval(intensities[-1], mep_params_cond[i_cond]))
        intensities_min.append(mep[i_cond].x_limits[0])
        intensities_max.append(mep[i_cond].x_limits[1])

    for i_datasets in range(n_datasets):

        # calculate corresponding electric field values per condition
        for elm_idx, elmIdx in enumerate(elm_idx_list):
            e_curve = []
            stepsize_local_shift = []

            # get e-curves for reference solutions with n_samples
            for i_cond in range(n_conditions):
                e_curve.append(e[i_cond][i_datasets][elmIdx] * intensities[i_cond])
                stepsize_local_shift.append(e_curve[-1][1] - e_curve[-1][0])

            # KERNEL CODE STARTED HERE
            e_min = np.min(e_curve, axis=1)  # minima of electric field for every condition
            # ceil to .stepsize
            e_min = np.ceil(e_min / stepsize) * stepsize
            e_max = np.max(e_curve, axis=1)  # maxima of electric field for every condition
            e_max = np.floor(e_max / stepsize) * stepsize

            # find median mep cond
            e_mean = np.mean((e_max + e_min) / 2)

            # return NaN if xmax-xmin is smaller than stepsize
            if np.any(e_max - e_min <= stepsize):
                congruence_factor[elm_idx, i_datasets] = np.nan

            else:

                # find start and stop indices of e_x in global e array
                start_ind = np.empty(n_conditions, dtype=int)
                stop_ind = np.empty(n_conditions, dtype=int)
                e_x_global = np.arange(0, np.max(e_max) + stepsize, stepsize)

                for idx in range(n_conditions):
                    # lower boundary idx of e_x_cond in e_x_global
                    start_ind[idx] = pynibs.find_nearest(e_x_global, e_min[idx])

                    # upper boundary idx of e_x_cond in e_x_global
                    stop_ind[idx] = pynibs.find_nearest(e_x_global, e_max[idx])

                # get tau distances for all conditions vs reference condition
                # distances for ref,i == i,ref. i,i == 0. So only compute upper triangle of matrix
                ref_range = np.arange(n_conditions)
                t_cond = np.zeros((n_conditions, n_conditions))
                idx_range = list(reversed(np.arange(n_conditions)))

                for reference_idx in ref_range:
                    # remove this reference index from idx_range
                    idx_range.pop()
                    # # as we always measure the distance of the shorter mep_cond, save idx to store in matrix
                    # reference_idx_backup = copy.deepcopy(reference_idx)

                    for idx in idx_range:
                        idx_save = idx

                        # # restore correct reference idx
                        # reference_idx = copy.deepcopy(reference_idx_backup)

                        # # switch ref and idx, as we want to measure from short mep_y to avoid overshifting
                        # intens_range_mep = np.max(intensities[idx]) - np.min(intensities[idx])
                        # intens_range_ref = np.max(intensities[reference_idx]) - np.min(intensities[reference_idx])
                        #
                        # if intens_range_ref < intens_range_mep:
                        #     reference_idx, idx = idx, reference_idx

                        # get initially shifted mep curve
                        # e axis of initially shifted mep curve (just needed for length)
                        # e_mep = np.arange((e_min[reference_idx] - stepsize_local_shift[reference_idx]) /
                        #                   intensities_max[idx] * intensities_min[idx],
                        #                   (e_min[reference_idx] - stepsize_local_shift[reference_idx]),
                        #                   stepsize_local_shift[reference_idx])

                        # resampled intensity axis of initially shifted mep curve
                        intens_mep = np.linspace(intensities_min[idx],
                                                 intensities_max[idx],
                                                 ((e_min[reference_idx] - stepsize_local_shift[reference_idx]) -
                                                  ((e_min[reference_idx] - stepsize_local_shift[reference_idx]) /
                                                   intensities_max[idx] * intensities_min[idx])) /
                                                 stepsize_local_shift[reference_idx])

                        # ficticious e_mep value for initial shift (e'_mep)
                        e_mep_initial_shift = (e_min[reference_idx] - stepsize_local_shift[reference_idx]) / \
                                              intensities_max[idx]

                        # start index of initially shifted and stretched mep curve
                        start_idx_mep_initial_shift = pynibs.find_nearest(e_x_global,
                                                                          e_mep_initial_shift * intensities_min[idx])

                        mep_shift = mep[idx].eval(intens_mep, mep_params_cond[idx])

                        # determine length of mep curve in dependence on its location
                        max_e_mep_end = (e_max[reference_idx] + stepsize_local_shift[reference_idx]) * \
                                        intensities_max[idx] / intensities_min[idx]
                        len_e_ref = n_samples
                        len_e_mep_start = mep_shift.size
                        len_e_mep_end = np.ceil((max_e_mep_end - e_max[reference_idx] +
                                                 stepsize_local_shift[reference_idx]) /
                                                stepsize_local_shift[reference_idx])
                        # len_total = (len_e_mep_start + len_e_ref + len_e_mep_end + 2).astype(int)

                        # length of shifted curve as a function of position (gets longer while shifting)
                        len_mep_idx_shift = np.round(np.linspace(
                                len_e_mep_start,
                                len_e_mep_end,
                                len_e_mep_start + len_e_ref + 2 * stepsize_local_shift[reference_idx]))

                        # construct shift array (there are less 0 at the beginning and more at the end because the mep
                        # curve is stretched during shifting)
                        stepsize_local_shift_intens = (intensities_max[reference_idx] -
                                                       intensities_min[reference_idx]) / \
                                                      n_samples
                        min_intens_ref_prime = intensities_min[reference_idx] - stepsize_local_shift_intens * \
                                               (1 + len_e_mep_start)
                        max_intens_ref_prime = intensities_max[reference_idx] + stepsize_local_shift_intens * \
                                               (1 + len_e_mep_end)

                        shift_array = mep[reference_idx].eval(np.arange(min_intens_ref_prime,
                                                                        max_intens_ref_prime,
                                                                        stepsize_local_shift_intens),
                                                              mep_params_cond[reference_idx])

                        # generate index shift list to compare curves
                        slice_indices = np.outer(len_mep_idx_shift[:, np.newaxis],
                                                 np.linspace(0, 1, len_e_mep_start)[np.newaxis, :])
                        slice_indices = np.round(
                                np.add(slice_indices, np.arange(slice_indices.shape[0])[:, np.newaxis])).astype(int)

                        # the error is y-difference between mep[idx] and mep[reference].zero_padded
                        err = np.sqrt(np.sum((shift_array[slice_indices] - mep_shift) ** 2, axis=1))

                        # which shift leads to minimum error. remember that we don't start at 0-shift, so add start idx
                        t_cond[reference_idx, idx_save] = (start_idx_mep_initial_shift - start_ind[idx]) * stepsize + \
                                                          np.argmin(err) * stepsize_local_shift[reference_idx]

                # sum all errors and divide by e_mean over all conditions
                congruence_factor[elm_idx, i_datasets] = 1 / (
                        np.sqrt(np.sum(np.square(t_cond) * 2)) / e_mean / n_conditions / (n_conditions - 1))

    return congruence_factor


def congruence_factor_curveshift_workhorse_stretch_correction_new(mep, mep_params, e, n_samples=100, ref_idx=0):
    """
    Worker function for congruence factor computation - call from multiprocessing.pool
    Calculates congruence factor for e = (E_mag, E_norm and/or E_tan) for given zaps and elements.
    The computations are parallelized in terms of element indices (elm_idx_list).
    n_samples are taken from fitted_mep, within the range of the mep object.

    Parameters
    ----------
    mep : list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params : nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        - e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...]
    e : nparray of float [n_elm x n_cond]
        Electric field in elements
    n_samples : int, default=100
        Number of data points to generate discrete mep and e curves

    Returns
    -------
    congruence_factor : nparray of float [n_elm x 1]
        Congruence factor in each element specified in elm_idx_list and for each input dataset
    """

    # start = time.time()

    n_elm = e.shape[0]
    n_conditions = e.shape[1]
    c_idx = [idx for idx in np.arange(n_conditions) if idx != ref_idx]

    # rearrange mep parameters to individual conditions
    mep_params_cond = []
    start_idx = 0
    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size

    mep_params_ref = mep_params_cond[ref_idx]
    mep_params_c = [mep_params_cond[idx] for idx in c_idx]

    # stop = time.time()
    # print("Rearrange input data: {}s".format(stop-start))

    # start = time.time()
    # intensities max and min [n_curves]
    i_ref_min = mep[ref_idx].intensities[0]
    i_ref_max = mep[ref_idx].intensities[-1]

    i_c_min = np.array([mep[idx].intensities[0] for idx in c_idx])
    i_c_max = np.array([mep[idx].intensities[-1] for idx in c_idx])

    i_stepsize = (i_ref_max - i_ref_min) / (n_samples - 1)

    # number of samples before and after shift with stretch correction
    n_c_before = np.round((1 - i_c_min / i_c_max) / (i_ref_max / i_ref_min - 1) * n_samples)
    n_c_after = np.round((i_c_max / i_c_min - 1) / (1 - i_ref_min / i_ref_max) * n_samples)

    # evaluate curves
    i_ref_shift = np.arange(i_ref_min - max(n_c_before) * i_stepsize,
                            i_ref_max + max(n_c_after) * i_stepsize + i_stepsize,
                            i_stepsize)

    mep_ref_shift = mep[ref_idx].eval(i_ref_shift, mep_params_ref)
    # stop = time.time()
    # print("Calculate indices and vector lengths: {}s".format(stop-start))

    # start = time.time()
    err_min_idx = []
    for i, idx in enumerate(c_idx):
        # evaluate curves at resampled intensity axis
        i_c_shift = np.linspace(i_c_min[i], i_c_max[i], n_c_before[i])
        mep_c_shift = mep[idx].eval(i_c_shift, mep_params_c[i])
        # generate index shift list to compare curves
        slice_indices = np.outer(
                np.round(np.linspace(n_c_before[i], n_c_after[i], n_c_before[i] + n_samples))[:, np.newaxis],
                np.linspace(0, 1, n_c_before[i])[np.newaxis, :])
        slice_indices = np.round(slice_indices + np.arange(slice_indices.shape[0])[:, np.newaxis])
        slice_indices = (slice_indices + (np.max(n_c_before) - n_c_before[i])).astype(int)
        # the error is y-difference between mep[idx] and mep[reference].zero_padded
        err = np.sum((mep_ref_shift[slice_indices] - mep_c_shift) ** 2, axis=1)
        err_min_idx.append(np.argmin(err))
    # stop = time.time()
    # print("Slice indices and error estimation: {}s".format(stop-start))

    # start = time.time()

    # electric fields [n_elm x n_curves]
    e_ref = e[:, ref_idx][:, np.newaxis]
    e_c = e[:, c_idx]

    # determine stepsizes in intensity and electric field space
    e_max = np.hstack((i_ref_max, i_c_max)) * np.hstack((e_ref, e_c))
    e_min = np.hstack((i_ref_min, i_c_min)) * np.hstack((e_ref, e_c))
    e_mean = np.mean((e_max + e_min) / 2, axis=1)[:, np.newaxis]
    e_stepsize = e_ref * i_stepsize

    # determine initial shift in electric field space
    initial_shift = e_c * i_c_min - e_ref * i_ref_min * i_c_min / i_c_max

    # determine total shift
    total_shift = np.zeros((n_elm, n_conditions))
    total_shift[:, 1:] = initial_shift - e_stepsize * np.array(err_min_idx)[np.newaxis, :]

    # sum all errors and divide by e_mean over all conditions
    congruence_factor = (e_mean ** 2) / np.var(total_shift, axis=1)[:, np.newaxis]
    # stop = time.time()
    # print("Matrix operations: {}s".format(stop-start))

    return congruence_factor


def congruence_factor_curveshift_workhorse_stretch_correction_sign_new(mep, mep_params, e, n_samples=100, ref_idx=0):
    """
    Worker function for congruence factor computation - call from multiprocessing.pool
    Calculates congruence factor for e = (E_mag, E_norm and/or E_tan) for given zaps and elements.
    The computations are parallelized in terms of element indices (elm_idx_list).
    n_samples are taken from fitted_mep, within the range of the mep object.

    Parameters
    ----------
    mep : list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params : nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        - e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...]
    e : nparray of float [n_elm x n_cond]
        Electric field in elements
    n_samples : int, default=100
        Number of data points to generate discrete mep and e curves

    Returns
    -------
    congruence_factor : nparray of float [n_elm x 1]
        Congruence factor in each element specified in elm_idx_list and for each input dataset
    """

    # start = time.time()
    n_elm = e.shape[0]
    n_conditions = e.shape[1]
    err_min_idx = np.zeros((n_conditions, n_conditions))
    initial_shift = np.zeros((n_elm, n_conditions, n_conditions))
    x_mean = np.empty((1, n_conditions))
    e_stepsize = np.zeros((n_elm, n_conditions))

    mep_params_cond = []
    start_idx = 0

    mask_pos = e > 0
    mask_neg = e < 0

    mask_only_one_curve = np.logical_or(np.sum(mask_pos, axis=1) == 1, np.sum(mask_neg, axis=1) == 1)
    n_curves = np.ones(n_elm) * n_conditions
    n_curves[mask_only_one_curve] = n_conditions - 1

    # rearrange mep parameters to individual conditions
    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size
        x_mean[0, i_cond] = (mep[i_cond].x_limits[0] + mep[i_cond].x_limits[1]) / 2

    for ref_idx in range(n_conditions):
        c_idx = [idx for idx in np.arange(n_conditions) if idx != ref_idx]

        mep_params_ref = mep_params_cond[ref_idx]
        mep_params_c = [mep_params_cond[idx] for idx in c_idx]

        # stop = time.time()
        # print("Rearrange input data: {}s".format(stop-start))

        # start = time.time()
        # intensities max and min [n_curves]
        i_ref_min = np.min(mep[ref_idx].intensities)  # [0]
        i_ref_max = np.max(mep[ref_idx].intensities)  # [-1]

        i_c_min = np.array([np.min(mep[idx].intensities) for idx in c_idx])
        i_c_max = np.array([np.max(mep[idx].intensities) for idx in c_idx])

        i_stepsize = (i_ref_max - i_ref_min) / (n_samples - 1)

        # number of samples before and after shift with stretch correction
        n_c_before = np.round((1 - i_c_min / i_c_max) / (i_ref_max / i_ref_min - 1) * n_samples).astype(int)
        n_c_after = np.round((i_c_max / i_c_min - 1) / (1 - i_ref_min / i_ref_max) * n_samples)

        # evaluate curves
        i_ref_shift = np.arange(i_ref_min - max(n_c_before) * i_stepsize,
                                i_ref_max + max(n_c_after) * i_stepsize + i_stepsize,
                                i_stepsize)

        mep_ref_shift = mep[ref_idx].eval(i_ref_shift, mep_params_ref)
        # stop = time.time()
        # print("Calculate indices and vector lengths: {}s".format(stop-start))

        # start = time.time()

        for i, idx in enumerate(c_idx):
            # evaluate curves at resampled intensity axis
            i_c_shift = np.linspace(i_c_min[i], i_c_max[i], n_c_before[i])
            mep_c_shift = mep[idx].eval(i_c_shift, mep_params_c[i])
            # generate index shift list to compare curves
            slice_indices = np.outer(
                    np.round(np.linspace(n_c_before[i], n_c_after[i], n_c_before[i] + n_samples))[:, np.newaxis],
                    np.linspace(0, 1, n_c_before[i])[np.newaxis, :])
            slice_indices = np.round(slice_indices + np.arange(slice_indices.shape[0])[:, np.newaxis])
            slice_indices = (slice_indices + (np.max(n_c_before) - n_c_before[i])).astype(int)
            # the error is y-difference between mep[idx] and mep[reference].zero_padded
            err = np.sum((mep_ref_shift[slice_indices] - mep_c_shift) ** 2, axis=1)
            err_min_idx[ref_idx, idx] = np.argmin(err)

        # electric fields [n_elm x n_curves]
        e_ref = e[:, ref_idx][:, np.newaxis]
        e_c = e[:, c_idx]

        # determine stepsizes in intensity and electric field space
        e_stepsize[:, ref_idx] = (e_ref * i_stepsize).flatten()

        # determine initial shift in electric field space
        initial_shift[:, c_idx, ref_idx] = e_c * i_c_min - e_ref * i_ref_min * i_c_min / i_c_max

    # stop = time.time()
    # print("Slice indices and error estimation: {}s".format(stop-start))

    # start = time.time()

    mean_pos = np.array([np.mean(row[mask_pos[i, :]] * x_mean[0, mask_pos[i, :]]) for i, row in enumerate(e)])
    mean_neg = np.array([np.mean(row[mask_neg[i, :]] * x_mean[0, mask_neg[i, :]]) for i, row in enumerate(e)])

    # determine total shift
    total_shift_pos = []
    total_shift_neg = []

    for i_elm in range(n_elm):
        curve_idx_neg = np.where(mask_neg[i_elm, :])[0]
        curve_idx_pos = np.where(mask_pos[i_elm, :])[0]

        if curve_idx_neg.size != 0:
            ref_idx_neg = curve_idx_neg[0]
            total_shift_neg.append(initial_shift[i_elm, curve_idx_neg[1:], ref_idx_neg] -
                                   e_stepsize[i_elm, ref_idx_neg] * err_min_idx[ref_idx_neg, curve_idx_neg[1:]])
        else:
            total_shift_neg.append(np.array([]))

        if curve_idx_pos.size != 0:
            ref_idx_pos = curve_idx_pos[0]
            total_shift_pos.append(initial_shift[i_elm, curve_idx_pos[1:], ref_idx_pos] -
                                   e_stepsize[i_elm, ref_idx_pos] * err_min_idx[ref_idx_pos, curve_idx_pos[1:]])
        else:
            total_shift_pos.append(np.array([]))

    # total_shift_pos = initial_shift - e_stepsize * np.array(err_min_idx)[np.newaxis, :]
    # total_shift_neg =

    # total_shift = np.zeros((n_elm, n_conditions))
    # total_shift[:, 1:] = initial_shift - e_stepsize * np.array(err_min_idx)[np.newaxis, :]

    var_pos = np.array([np.sum(mask_pos[i, :]) * np.var(np.hstack((0, row))) for i, row in enumerate(total_shift_pos)])
    var_neg = np.array([np.sum(mask_neg[i, :]) * np.var(np.hstack((0, row))) for i, row in enumerate(total_shift_neg)])

    mean_pos[np.isnan(mean_pos)] = np.inf
    mean_neg[np.isnan(mean_neg)] = np.inf

    mean_pos[np.isnan(var_pos)] = np.inf
    mean_neg[np.isnan(var_neg)] = np.inf

    # var_pos[np.isnan(var_pos)] = 0
    # var_neg[np.isnan(var_neg)] = 0

    var = (var_pos / mean_pos ** 2 + var_neg / mean_neg ** 2) / n_curves

    congruence_factor = (1 / var)[:, np.newaxis]

    # stop = time.time()
    # print("Matrix operations: {}s".format(stop-start))

    return congruence_factor


def congruence_factor_curveshift_workhorse_stretch_correction_variance(elm_idx_list, mep, mep_params, e, n_samples=100):
    """
    Worker function for congruence factor computation - call from multiprocessing.pool
    Calculates congruence factor for e = (E_mag, E_norm and/or E_tan) for given zaps and elements.
    The computations are parallelized in terms of element indices (elm_idx_list).
    n_samples are taken from fitted_mep, within the range of the mep object.

    Parameters
    ----------
    elm_idx_list : nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep : list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params : nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        - e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...]
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - e.g.: len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))
    n_samples : int, default=100
        Number of data points to generate discrete mep and e curves

    Returns
    -------
    congruence_factor : nparray of float [n_roi, n_datasets]
        Congruence factor in each element specified in elm_idx_list and for each input dataset
    """

    stepsize = 1e-1
    n_datasets = len(e[0])
    n_elm = len(elm_idx_list)
    n_conditions = len(mep)

    mep_params = np.array(mep_params).flatten()

    congruence_factor = np.empty((n_elm, n_datasets))

    # rearrange mep parameters to individual conditions
    mep_params_cond = []
    start_idx = 0
    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size

    del start_idx

    intensities = []
    intensities_min = []
    intensities_max = []
    stepsize_local_shift = []
    mep_curve = []

    # calculate mep curves per condition
    for i_cond in range(n_conditions):
        intensities.append(np.linspace(mep[i_cond].x_limits[0], mep[i_cond].x_limits[1], n_samples))
        mep_curve.append(mep[i_cond].eval(intensities[-1], mep_params_cond[i_cond]))
        intensities_min.append(mep[i_cond].x_limits[0])
        intensities_max.append(mep[i_cond].x_limits[1])

    for i_datasets in range(n_datasets):

        # calculate corresponding electric field values per condition
        for elm_idx, elmIdx in enumerate(elm_idx_list):

            e_curve = []
            stepsize_local_shift = []

            # get e-curves for reference solutions with n_samples
            for i_cond in range(n_conditions):
                e_curve.append(e[i_cond][i_datasets][elmIdx] * intensities[i_cond])
                stepsize_local_shift.append(e_curve[-1][1] - e_curve[-1][0])

            # KERNEL CODE STARTED HERE
            e_min = np.min(e_curve, axis=1)  # minima of electric field for every condition
            # ceil to .stepsize
            e_min = np.ceil(e_min / stepsize) * stepsize
            e_max = np.max(e_curve, axis=1)  # maxima of electric field for every condition
            e_max = np.floor(e_max / stepsize) * stepsize

            # find median mep cond
            e_mean = np.mean((e_max + e_min) / 2)

            # return NaN if xmax-xmin is smaller than stepsize
            if np.any(e_max - e_min <= stepsize):
                congruence_factor[elm_idx, i_datasets] = np.nan

            else:

                # find start and stop indices of e_x in global e array
                start_ind = np.empty(n_conditions, dtype=int)
                stop_ind = np.empty(n_conditions, dtype=int)
                e_x_global = np.arange(0, np.max(e_max) + stepsize, stepsize)

                for idx in range(n_conditions):
                    # lower boundary idx of e_x_cond in e_x_global
                    start_ind[idx] = pynibs.find_nearest(e_x_global, e_min[idx])

                    # upper boundary idx of e_x_cond in e_x_global
                    stop_ind[idx] = pynibs.find_nearest(e_x_global, e_max[idx])

                # get tau distances for all conditions vs reference condition
                # distances for ref,i == i,ref. i,i == 0. So only compute upper triangle of matrix
                ref_range = [0]  # np.arange(n_conditions)
                t_cond = np.zeros((n_conditions, n_conditions))
                idx_range = list(reversed(np.arange(n_conditions)))

                for reference_idx in ref_range:
                    # remove this reference index from idx_range
                    idx_range.pop()
                    # # as we always measure the distance of the shorter mep_cond, save idx to store in matrix
                    # reference_idx_backup = copy.deepcopy(reference_idx)

                    for idx in idx_range:
                        idx_save = idx

                        # # restore correct reference idx
                        # reference_idx = copy.deepcopy(reference_idx_backup)

                        # # switch ref and idx, as we want to measure from short mep_y to avoid overshifting
                        # intens_range_mep = np.max(intensities[idx]) - np.min(intensities[idx])
                        # intens_range_ref = np.max(intensities[reference_idx]) - np.min(intensities[reference_idx])
                        #
                        # if intens_range_ref < intens_range_mep:
                        #     reference_idx, idx = idx, reference_idx

                        # get initially shifted mep curve
                        # e axis of initially shifted mep curve (just needed for length)
                        # e_mep = np.arange((e_min[reference_idx] - stepsize_local_shift[reference_idx]) /
                        #                   intensities_max[idx] * intensities_min[idx],
                        #                   (e_min[reference_idx] - stepsize_local_shift[reference_idx]),
                        #                   stepsize_local_shift[reference_idx])

                        # resampled intensity axis of initially shifted mep curve
                        intens_mep = np.linspace(intensities_min[idx],
                                                 intensities_max[idx],
                                                 ((e_min[reference_idx] - stepsize_local_shift[reference_idx]) -
                                                  ((e_min[reference_idx] - stepsize_local_shift[reference_idx]) /
                                                   intensities_max[idx] * intensities_min[idx])) /
                                                 stepsize_local_shift[reference_idx])

                        # ficticious e_mep value for initial shift (e'_mep)
                        e_mep_initial_shift = (e_min[reference_idx] - stepsize_local_shift[reference_idx]) / \
                                              intensities_max[idx]

                        # start index of initially shifted and stretched mep curve
                        start_idx_mep_initial_shift = pynibs.find_nearest(e_x_global,
                                                                          e_mep_initial_shift * intensities_min[idx])

                        mep_shift = mep[idx].eval(intens_mep, mep_params_cond[idx])

                        # determine length of mep curve in dependence on its location
                        max_e_mep_end = (e_max[reference_idx] + stepsize_local_shift[reference_idx]) * \
                                        intensities_max[idx] / intensities_min[idx]
                        len_e_ref = n_samples
                        len_e_mep_start = mep_shift.size
                        len_e_mep_end = np.ceil((max_e_mep_end - e_max[reference_idx] +
                                                 stepsize_local_shift[reference_idx]) /
                                                stepsize_local_shift[reference_idx])
                        # len_total = (len_e_mep_start + len_e_ref + len_e_mep_end + 2).astype(int)

                        # length of shifted curve as a function of position (gets longer while shifting)
                        len_mep_idx_shift = np.round(np.linspace(
                                len_e_mep_start,
                                len_e_mep_end,
                                len_e_mep_start + len_e_ref + 2 * stepsize_local_shift[reference_idx]))

                        # construct shift array (there are less 0 at the beginning and more at the end because the mep
                        # curve is stretched during shifting)
                        # shift_array = np.zeros(len_total)
                        # shift_array[(len_e_mep_start + 1):(len_e_mep_start + 1 + len_e_ref)] = mep_curve[reference_idx]
                        stepsize_local_shift_intens = (intensities_max[reference_idx] -
                                                       intensities_min[reference_idx]) / \
                                                      float(n_samples - 1)
                        min_intens_ref_prime = intensities_min[reference_idx] - stepsize_local_shift_intens * \
                                               (1 + len_e_mep_start)
                        max_intens_ref_prime = intensities_max[reference_idx] + stepsize_local_shift_intens * \
                                               (1 + len_e_mep_end)

                        shift_array = mep[reference_idx].eval(np.arange(min_intens_ref_prime,
                                                                        max_intens_ref_prime,
                                                                        stepsize_local_shift_intens),
                                                              mep_params_cond[reference_idx])

                        # generate index shift list to compare curves
                        slice_indices = np.outer(len_mep_idx_shift[:, np.newaxis],
                                                 np.linspace(0, 1, len_e_mep_start)[np.newaxis, :])
                        slice_indices = np.round(
                                np.add(slice_indices, np.arange(slice_indices.shape[0])[:, np.newaxis])).astype(int)

                        # the error is y-difference between mep[idx] and mep[reference].zero_padded
                        err = np.sqrt(np.sum((shift_array[slice_indices] - mep_shift) ** 2, axis=1))

                        # which shift leads to minimum error. remember that we don't start at 0-shift, so add start idx
                        t_cond[reference_idx, idx_save] = (start_idx_mep_initial_shift - start_ind[idx]) * stepsize + \
                                                          np.argmin(err) * stepsize_local_shift[reference_idx]

                # sum all errors and divide by e_mean over all conditions
                congruence_factor[elm_idx, i_datasets] = 1 / (
                        np.var(t_cond[0, :]) / (e_mean ** 2))  # changed to squared e

    return congruence_factor


def congruence_factor_variance_workhorse(elm_idx_list, mep, mep_params, e, old_style=True):
    """
    Worker function for congruence factor computation - call from multiprocessing.pool
    Calculates congruence factor for e = (E_mag, E_norm and/or E_tan) for given zaps and elements.

    Parameters
    ----------
    elm_idx_list: nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep: list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params: nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        (e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...])
    e: list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))
    old_style: boolean (default: True)
        True:  Weight var(x_0_prime(r)) with mean(e(r) * mean(Stimulator Intensity), taken from MEP object
        False: Weight var(x_0_prime(r)) with mean(E(r)), taken from e

    Returns
    -------
    congruence_factor: nparray of float [n_roi, n_datasets]
        Congruence factor in each element specified in elm_idx_list and for each input dataset
    """
    n_datasets = len(e[0])
    n_elm = len(elm_idx_list)
    n_conditions = len(mep)

    mep_params = np.array(mep_params).flatten()

    congruence_factor = np.empty((n_elm, n_datasets))

    # rearrange mep parameters to individual conditions
    mep_params_cond = []
    start_idx = 0
    # r_vec = np.empty((1, n_conditions))
    x0_vec = np.empty((1, n_conditions))
    x_mean = np.empty((1, n_conditions))

    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size
        # r_vec[0, i_cond] = mep_params_cond[i_cond][1]
        x0_vec[0, i_cond] = mep_params_cond[i_cond][0]
        x_mean[0, i_cond] = (mep[i_cond].x_limits[0] + mep[i_cond].x_limits[1]) / 2

    e_arr = np.array(e)

    for i_dataset in range(n_datasets):

        e_mat = np.array(e_arr[:, i_dataset, np.array(elm_idx_list).astype(int)]).transpose()

        # r_prime = 1 / e_mat * r_vec
        x0_prime = e_mat * x0_vec

        # var_r_prime = np.var(r_prime, axis=1)
        var_x0_prime = np.var(x0_prime, axis=1)

        # var_r_weight = 0
        # var_x0_weight = 1

        e_mean_vec = np.mean(e_mat * x_mean, axis=1)

        if old_style:
            congruence_factor[:, i_dataset] = e_mean_vec ** 2 / var_x0_prime
        else:
            congruence_factor[:, i_dataset] = np.mean(e_mat, axis=1) ** 2 / var_x0_prime

        # congruence_factor[:, i_datasets] = e_mean_vec / np.sqrt((var_r_weight * var_r_prime) ** 2 +
        #                                                         (var_x0_weight * var_x0_prime) ** 2)

    return congruence_factor


def congruence_factor_variance_sign_workhorse(elm_idx_list, mep, mep_params, e):
    """
    Worker function for congruence factor computation - call from multiprocessing.pool
    Calculates congruence factor for e = (E_mag, E_norm and/or E_tan) for given zaps and elements.

    Parameters
    ----------
    elm_idx_list: nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep: list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params: nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        (e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...])
    e: list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))

    Returns
    -------
    congruence_factor: nparray of float [n_roi, n_datasets]
        Congruence factor in each element specified in elm_idx_list and for each input dataset
    """
    n_datasets = len(e[0])
    n_elm = len(elm_idx_list)
    n_conditions = len(mep)

    mep_params = np.array(mep_params).flatten()

    congruence_factor = np.empty((n_elm, n_datasets))

    # rearrange mep parameters to individual conditions
    mep_params_cond = []
    start_idx = 0
    # r_vec = np.empty((1, n_conditions))
    x0_vec = np.empty((1, n_conditions))
    x_mean = np.empty((1, n_conditions))

    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size
        # r_vec[0, i_cond] = mep_params_cond[i_cond][1]
        x0_vec[0, i_cond] = mep_params_cond[i_cond][0]
        x_mean[0, i_cond] = (mep[i_cond].x_limits[0] + mep[i_cond].x_limits[1]) / 2

    e_arr = np.array(e)

    for i_dataset in range(n_datasets):
        e_mat = np.array(e_arr[:, i_dataset, np.array(elm_idx_list).astype(int)]).transpose()

        mask_pos = e_mat > 0
        mask_neg = e_mat < 0

        mask_only_one_curve = np.logical_or(np.sum(mask_pos, axis=1) == 1, np.sum(mask_neg, axis=1) == 1)
        n_curves = np.ones(n_elm) * n_conditions
        n_curves[mask_only_one_curve] = n_conditions - 1

        x0_prime = e_mat * x0_vec

        var_pos = np.array([np.sum(mask_pos[i, :]) * np.var(row[mask_pos[i, :]]) for i, row in enumerate(x0_prime)])
        var_neg = np.array([np.sum(mask_neg[i, :]) * np.var(row[mask_neg[i, :]]) for i, row in enumerate(x0_prime)])

        var_pos[np.isnan(var_pos)] = 0
        var_neg[np.isnan(var_neg)] = 0

        mean_pos = np.array([np.mean(row[mask_pos[i, :]] * x_mean[0, mask_pos[i, :]]) for i, row in enumerate(e_mat)])
        mean_neg = np.array([np.mean(row[mask_neg[i, :]] * x_mean[0, mask_neg[i, :]]) for i, row in enumerate(e_mat)])

        mean_pos[np.isnan(mean_pos)] = np.inf
        mean_neg[np.isnan(mean_neg)] = np.inf

        mean_pos[np.isnan(var_pos)] = np.inf
        mean_neg[np.isnan(var_neg)] = np.inf

        var = (var_pos / mean_pos ** 2 + var_neg / mean_neg ** 2) / n_curves

        congruence_factor[:, i_dataset] = 1 / var

    return congruence_factor


def congruence_factor_curveshift_workhorse(elm_idx_list, mep, mep_params, e, n_samples=100):
    """
    Worker function for congruence factor computation - call from multiprocessing.pool
    Calculates congruence factor for e = (E_mag, E_norm and/or E_tan) for given zaps and elements.
    The computations are parallelized in terms of element indices (elm_idx_list).
    n_samples are taken from fitted_mep, within the range of the mep object.

    Parameters
    ----------
    elm_idx_list : nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep : list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params : nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        - e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...]
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))
    n_samples : int, default=100
        Number of data points to generate discrete mep and e curves

    Returns
    -------
    congruence_factor: nparray of float [n_roi, n_datasets]
        Congruence factor in each element specified in elm_idx_list and for each input dataset

    """
    n_datasets = len(e[0])
    n_elm = len(elm_idx_list)
    n_conditions = len(mep)

    mep_params = np.array(mep_params).flatten()

    congruence_factor = np.empty((n_elm, n_datasets))

    # rearrange mep parameters to individual conditions
    mep_params_cond = []
    start_idx = 0
    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size

    del start_idx

    intensities = []
    mep_curve = []

    # calculate mep curves per condition
    for i_cond in range(n_conditions):
        intensities.append(np.arange(mep[i_cond].x_limits[0],
                                     mep[i_cond].x_limits[1],
                                     step=(mep[i_cond].x_limits[1] - mep[i_cond].x_limits[0]) / float(n_samples)))
        mep_curve.append(mep[i_cond].eval(intensities[-1], mep_params_cond[i_cond]))

    for i_datasets in range(n_datasets):

        # calculate corresponding electric field values per condition
        for elm_idx, elmIdx in enumerate(elm_idx_list):

            e_curve = []

            for i_cond in range(n_conditions):
                e_curve.append(e[i_cond][i_datasets][elmIdx] * intensities[i_cond])

            congruence_factor[elm_idx, i_datasets] = congruence_factor_curveshift_kernel(e_curve, mep_curve)
            # print("{}:{}".format(idx, len(elm_idx_list)))
    return congruence_factor


def congruence_factor_curveshift_kernel(e_curve, mep_curve):
    """
    Curve congruence (overlap) measure for multiple MEP curves per element. Determines the average displacement
    between the MEP curves. The congruence factor is weighted by median(E) and summed up. This favors elements which
    have greater E, as these are more likely to produce MEPs.

    .. math::
        dE = \\begin{bmatrix}
            dE_{11} & dE_{12} & ... & dE_{1n} \\\\
            dE_{21} & dE_{22} & ... & dE_{2n} \\\\
            ...   & ...   & ... & ...   \\\\
            dE_{n1} & dE_{n2} & ... & dE_{nn} \\\\
            \\end{bmatrix}

    -> congruence_factor ~ np.linalg.norm(dE)/median(E)/n_cond/2

    Parameters
    ----------
    e_curve: list of nparray of float [n_cond]
        List over all conditions of electric field values corresponding to the mep amplitudes
    mep_curve: list of nparray of float [n_cond]
        List over all conditions of mep values corresponding to the electric field

    Returns
    -------
    congruence_factor: float
        Congruence factor for the n_cond electric field and MEP curves
    """

    stepsize = 1e-1
    n_condition = len(mep_curve)
    e_min = np.min(e_curve, axis=1)  # minima of electric field for every condition
    # ceil to .stepsize
    e_min = np.ceil(e_min / stepsize) * stepsize
    e_max = np.max(e_curve, axis=1)  # maxima of electric field for every condition
    e_max = np.floor(e_max / stepsize) * stepsize

    # return NaN if xmax-xmin is smaller than stepsize
    if np.any(e_max - e_min <= stepsize):
        return np.nan

    else:
        # stepsize-wise e over all conditions. we only need the length of this and first elm
        e_all_cond = np.arange(np.min(e_min), np.max(e_max) + stepsize, stepsize)

        e_len = len(e_all_cond)
        # mep_arr = []
        mep_y_all_cond = []
        start_ind = np.empty(n_condition, dtype=int)
        stop_ind = np.empty(n_condition, dtype=int)
        # e_x_cond_all = []
        for idx in range(n_condition):
            # x range for e for conditions, stepsize wise
            e_x_cond = np.arange(e_min[idx], e_max[idx], stepsize)
            # e_x_cond_all.append(e_x_con   d)

            # interpolate mep values to stepsize width
            mep_y_all_cond.append(np.interp(e_x_cond, e_curve[idx], mep_curve[idx]))
            # mep_y_all_cond.append(mep_y_cond)

            # setup zero spaced array
            # global_e_mep_arr = np.zeros(e_len)
            # mep_arr_cond[:] = np.random.rand(int(e_len)) * 3

            # lower boundary idx of e_x_cond in e_arr
            start_idx = int((e_x_cond[0] - np.min(e_min)) / stepsize)
            stop_idx = start_idx + len(e_x_cond)
            stop_ind[idx] = stop_idx
            start_ind[idx] = start_idx

            # overwrite e_x_cond range of mep_arr_cond with interpolated mep values
            # global_e_mep_arr[start_idx:stop_idx] = mep_y_cond
            # mep_arr_cond[start_idx + len(e_x_cond):] = mep_y_cond[-1] # tailing last
            # mep_arr.append(global_e_mep_arr)

        # find median mep cond
        e_mean = np.mean((e_max + e_min) / 2)

        # get tau distances for all conditions vs median condition
        # distances for ref,i == i,ref. i,i == 0. So only compute upper triangle of matrix
        ref_range = np.arange(n_condition)
        t_cond = np.zeros((n_condition, n_condition))
        idx_range = list(reversed(np.arange(n_condition)))
        # min_err_idx_lst_all = []
        for reference_idx in ref_range:
            # remove this reference index from idx_range
            idx_range.pop()
            # as we always measure the distance of the shorter mep_cond, save idx to store in matrix
            reference_idx_backup = reference_idx
            # min_err_idx_lst = np.zeros((n_condition, 1))
            # t = np.zeros((n_condition, 1))
            for idx in idx_range:
                # print((reference_idx, idx))
                idx_save = idx
                # restore correct reference idx
                reference_idx = reference_idx_backup

                # get lengths of mep_y
                len_mep_idx = mep_y_all_cond[idx].shape[0]
                len_mep_ref = mep_y_all_cond[reference_idx].shape[0]

                # switch ref and idx, as we want to measure from short mep_y
                if len_mep_idx < len_mep_ref:
                    reference_idx, idx = idx, reference_idx
                    len_mep_idx, len_mep_ref = len_mep_ref, len_mep_idx

                # and paste reference mep values. errors will be measured against this array
                # create array: global e + 2* len(mep[idx])
                shift_array = np.zeros(2 * len_mep_idx + len_mep_ref)
                shift_array[len_mep_idx:(len_mep_idx + len_mep_ref)] = mep_y_all_cond[reference_idx]

                # shift mep[idx] step wise over the shift_array and measure error

                # instead of for loop, I'll use multple slices:
                # slice_indices[0] is 0-shifting
                # slice_indices[1] is 1-shifting,...
                # we start shifting at start_ind[reference_idx], because range left of that is only 0
                # we stop shifting after len_mep_idx + e_len - stop_ind[reference_idx] times
                # slice_indices.shape == (len_mep_idx + e_len - stop_ind[reference_idx], len_mep_idx)
                slice_indices = np.add(np.arange(len_mep_idx),
                                       np.arange(len_mep_idx + len_mep_ref)[:, np.newaxis])

                # compute error vectorized
                # the error is y-difference between mep[idx] and mep[reference].zero_padded
                err = np.sqrt(np.sum((shift_array[slice_indices] - mep_y_all_cond[idx]) ** 2, axis=1))

                # 3 times slower for loop version:
                # for step in range(len_mep_idx + e_len):
                #     err[step] = np.sqrt(np.sum(np.square(shift_array[step:len_mep_idx+step] -
                #                                          mep_y_all_cond[idx]))) / len_mep_idx

                # which shift leads to minimum error. remember that we don't start at 0-shift, so add start index
                if stop_ind[idx] >= start_ind[reference_idx]:
                    min_err_idx = np.abs(start_ind[reference_idx] - stop_ind[idx]) - np.argmin(err)
                else:
                    min_err_idx = np.abs(start_ind[reference_idx] - stop_ind[idx]) + np.argmin(err)
                # min_err_idx_lst[idx] = min_err_idx

                # rescale min_error_idx to real E values
                t_cond[reference_idx_backup, idx_save] = min_err_idx * stepsize

        # sum all errors and divide by e_mean over all conditions
        congruence_factor = 1 / (np.sqrt(np.sum(np.square(t_cond) * 2)) / e_mean / n_condition / (n_condition - 1))

        return congruence_factor


def stimulation_threshold(elm_idx_list, mep, mep_params, n_samples, e, c_factor_percentile=95, mep_threshold=0.5,
                          c_factor=None, c_function=None, t_function=None):
    """
    Computes the stimulation threshold in terms of the electric field in [V/m]. The threshold is defined as the
    electric field value where the mep exceeds mep_threshold. The average value is taken over all mep curves in each
    condition and over an area where the congruence factor exceeds c_factor_percentile.

    Parameters
    ----------
    elm_idx_list : nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep : list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params : nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        (e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...])
    n_samples : int
        Number of data points to generate discrete mep and e curves
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))
    c_factor_percentile : float
        Percentile of the c_factor taken into account for the threshold evaluation. Only c_factors are considered
        exceeding this.
    mep_threshold : float
        MEP value in [mV], which has to be exceeded for threshold definition
    c_factor : nparray of float [n_roi, n_datasets]
        Congruence factor in each element specified in elm_idx_list and for each input dataset
    c_function : fun
        Defines the function to use during c_gpc to calculate the congruence factor
        - congruence_factor_curveshift_workhorse: determines the average curve shift (without stretch correction)
        - congruence_factor_curveshift_workhorse_stretch_correction: determines the average curve shift
          (with stretch correction)
        - congruence_factor_curveshift_workhorse_stretch_correction_variance: determines the average curve shift
          (with stretch correction and variance)
        - congruence_factor_variance_workhorse: evaluates the variance of the shifting and stretching parameters
    t_function : fun
        Defines the function to determine the stimulation_threshold
        - stimulation_threshold_mean_mep_threshold: uses mep_threshold to determine the corresponding e_threshold over
        all conditions and takes the average values as the stimulation threshold
        - stimulation_threshold_pynibs.sigmoid: Fits a new pynibs.sigmoid using all datapoints in the mep-vs-E space and
           evaluates the threshold from the turning point or the intersection of the derivative in the crossing point
           with the e-axis

    Returns
    -------
    stim_threshold_avg: float
        Average stimulation threshold in [V/m] where c_factor is greater than c_factor_percentile
    """

    if e:
        n_datasets = len(e[0])
    n_conditions = len(mep)
    mep_params = np.array(mep_params).flatten()

    # rearrange mep parameters to individual conditions
    mep_params_cond = []
    start_idx = 0

    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size

    # calculate mep curves per condition
    mep_curve = []
    intensities = []

    for i_cond in range(n_conditions):
        intensities.append(np.linspace(mep[i_cond].x_limits[0], mep[i_cond].x_limits[1], n_samples))
        mep_curve.append(mep[i_cond].eval(intensities[-1], mep_params_cond[i_cond]))

    # determine congruence factor, if not provided
    if not c_factor.any():
        if c_function == congruence_factor_curveshift_workhorse or \
                c_function == congruence_factor_curveshift_workhorse_stretch_correction or \
                c_function == congruence_factor_curveshift_workhorse_stretch_correction_variance:
            c_factor = c_function(elm_idx_list,
                                  mep=mep,
                                  mep_params=mep_params,
                                  n_samples=n_samples,
                                  e=e)

        elif c_function == congruence_factor_variance_workhorse:
            c_factor = c_function(elm_idx_list,
                                  mep=mep,
                                  mep_params=mep_params,
                                  e=e)

    # determine elements where the congruence factor exceeds c_factor_percentile
    elm_idx = []
    c_factor_percentile_value = []

    for i_data in range(n_datasets):
        c_factor_percentile_value.append(np.percentile(c_factor[np.logical_not(np.isnan(c_factor[:, i_data])), i_data],
                                                       c_factor_percentile))
        elm_idx.append(np.where(c_factor[:, i_data] > c_factor_percentile_value[i_data])[0])

    if t_function == stimulation_threshold_mean_mep_threshold:
        stim_threshold_avg, stim_threshold_std = \
            stimulation_threshold_mean_mep_threshold(elm_idx=elm_idx,
                                                     mep_curve=mep_curve,
                                                     intensities=intensities,
                                                     e=e,
                                                     mep_threshold=mep_threshold)

    elif t_function == stimulation_threshold_sigmoid:
        stim_threshold_avg, stim_threshold_std = \
            stimulation_threshold_sigmoid(elm_idx=elm_idx,
                                          mep_curve=mep_curve,
                                          intensities=intensities,
                                          e=e,
                                          mep_threshold=mep_threshold)

    elif t_function == stimulation_threshold_intensity:
        stim_threshold_avg = \
            stimulation_threshold_intensity(mep_curve=mep_curve,
                                            intensities=intensities,
                                            mep_threshold=mep_threshold)
        stim_threshold_std = np.nan

    else:
        raise NotImplementedError('Provided t_function not implemented yet!')

    return stim_threshold_avg, stim_threshold_std


def stimulation_threshold_mean_mep_threshold(elm_idx, mep_curve, intensities, e, mep_threshold):
    """
    Determines the stimulation threshold by calculating the average electric field over all conditions, where the
    mep curves exceed the value of mep_threshold (in [mV]).

    Parameters
    ----------
    elm_idx : list [n_datasets] of nparray of int [n_elements]
        Element indices where the congruence factor exceeds a certain percentile (defined during the call of
        stimulation_threshold())
    mep_curve : list [n_conditions] of nparray of float [n_samples]
        MEP values for every conditions
    intensities : list [n_conditions] of nparray of float [n_samples]
        To the MEP values corresponding stimulator intensities in [A/us]
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))
    mep_threshold : float
        MEP value in [mV], which has to be exceeded for threshold definition

    Returns
    -------
    stim_threshold_avg : float
        Average stimulation threshold in [V/m] where c_factor is greater than c_factor_percentile
    """

    n_conditions = len(mep_curve)
    n_datasets = len(e[0])

    # determine electric field values exceeding mep_threshold in this elements
    stim_threshold_cond = [np.zeros((elm_idx[i_data].size, n_conditions)) * np.nan for i_data in range(n_datasets)]
    stim_threshold_avg = [np.nan for _ in range(n_datasets)]
    stim_threshold_std = [np.nan for _ in range(n_datasets)]

    for i_cond in range(n_conditions):
        e_threshold_idx = np.where(mep_curve[i_cond] > mep_threshold)[0]

        if e_threshold_idx.any():
            for i_data in range(n_datasets):
                stim_threshold_cond[i_data][:, i_cond] = e[i_cond][i_data][elm_idx[i_data]] * \
                                                         intensities[i_cond][e_threshold_idx[0]]

    for i_data in range(n_datasets):
        stim_threshold_avg[i_data] = np.mean(
                stim_threshold_cond[i_data][np.logical_not(np.isnan(stim_threshold_cond[i_data]))])
        stim_threshold_std[i_data] = np.std(
                stim_threshold_cond[i_data][np.logical_not(np.isnan(stim_threshold_cond[i_data]))])

    return stim_threshold_avg, stim_threshold_std


def stimulation_threshold_sigmoid(elm_idx, mep_curve, intensities, e, mep_threshold):
    """
    Determines the stimulation threshold by calculating an equivalent pynibs.sigmoid over all conditions. The
    stimulation threshold is the electric field value where the mep curves exceed the value of mep_threshold (in [mV]).

    Parameters
    ----------
    elm_idx : list [n_datasets] of nparray of int [n_elements]
        Element indices where the congruence factor exceeds a certain percentile (defined during the call of
        stimulation_threshold())
    mep_curve : list [n_conditions] of nparray of float [n_samples]
        MEP curve values for every conditions
    intensities : list [n_conditions] of nparray of float [n_samples]
        To the MEP values corresponding stimulator intensities in [A/us]
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))
    mep_threshold : float
        MEP value in [mV], which has to be exceeded for threshold definition

    Returns
    -------
    stim_threshold_avg : float
        Average stimulation threshold in [V/m] where c_factor is greater than c_factor_percentile
    """

    n_conditions = len(mep_curve)
    n_datasets = len(e[0])
    stim_threshold_elm = [[] for _ in range(n_datasets)]
    stim_threshold_avg = [[] for _ in range(n_datasets)]
    stim_threshold_std = [[] for _ in range(n_datasets)]

    # accumulate all data values in one array
    mep_curve_all = np.hstack(mep_curve)

    for i_data in range(n_datasets):
        print(('Evaluating stimulation threshold for dataset {}/{}'.format(i_data + 1, n_datasets)))
        n_elms = len(elm_idx[i_data])
        stim_threshold_elm[i_data] = np.zeros(n_elms) * np.nan

        for i_elm, elm in enumerate(elm_idx[i_data]):
            print((' > Element {}/{}'.format(i_elm, n_elms)))

            # accumulate all data values in one array
            e_all = []

            for i_cond in range(n_conditions):
                e_all.append(e[i_cond][i_data][elm] * intensities[i_cond])
            e_all = np.hstack(e_all)

            # fit data to function
            mep = pynibs.Mep(intensities=e_all, mep=mep_curve_all, intensity_min_threshold=0, mep_min_threshold=0)
            mep.fit = mep.run_fit_multistart(pynibs.sigmoid,
                                             x=e_all,
                                             y=mep_curve_all,
                                             p0=[70, 0.6, 2],
                                             constraints=None,
                                             verbose=False,
                                             n_multistart=20)

            # read out optimal function parameters from best fit
            try:
                for p in ['x0', 'r', 'amp']:
                    mep.popt.append(mep.fit.best_values[p])

                mep.popt = np.asarray(mep.popt)
                mep.cvar = np.asarray(mep.fit.covar)
                mep.pstd = np.sqrt(np.diag(mep.cvar))
                mep.fun = pynibs.sigmoid

                # determine stimulation threshold
                e_fit = np.linspace(np.min(e_all), np.max(e_all), 200)
                mep_fit = mep.eval_opt(e_fit)
                e_threshold_idx = np.where(mep_fit > mep_threshold)[0]

                # ###
                # import matplotlib.pyplot as plt
                # plt.plot(e_all, mep_curve_all, linestyle='', marker='o', )
                # plt.plot(e_fit, mep_fit, color='r')
                # ###

                if e_threshold_idx.any():
                    stim_threshold_elm[i_data][i_elm] = e_fit[e_threshold_idx[0]]

            except (AttributeError, ValueError):
                print(' > Warning: pynibs.sigmoid in element could not be fitted!')
                stim_threshold_elm[i_data][i_elm] = np.nan

        # determine mean threshold over all elements
        stim_threshold_avg[i_data] = np.mean(stim_threshold_elm[i_data]
                                             [np.logical_not(np.isnan(stim_threshold_elm[i_data]))])
        stim_threshold_std[i_data] = np.std(stim_threshold_elm[i_data]
                                            [np.logical_not(np.isnan(stim_threshold_elm[i_data]))])

    return stim_threshold_avg, stim_threshold_std


def stimulation_threshold_intensity(mep_curve, intensities, mep_threshold):
    """
    Determines the stimulation threshold of one particular condition (usually the most sensitive e.g. M1-45). The
    stimulation threshold is the stimulator intensity value in [A/us] where the mep curves exceed the value of
    mep_threshold (in [mV]).

    Parameters
    ----------
    mep_curve: list [1] of nparray of float [n_samples]
        MEP curve values for every conditions
    intensities: list [1] of nparray of float [n_samples]
        To the MEP values corresponding stimulator intensities in [A/us]
    mep_threshold: float
        MEP value in [mV], which has to be exceeded for threshold definition

    Returns
    -------
    stim_threshold_avg: float
        Average stimulation threshold in [V/m] where c_factor is greater than c_factor_percentile
    """

    stim_threshold = np.nan
    i_threshold_idx = np.where(mep_curve[0] > mep_threshold)[0]

    if i_threshold_idx.any():
        stim_threshold = intensities[0][i_threshold_idx[0]]

    return stim_threshold


def rsd_inverse_workhorse(elm_idx_list, mep, e):
    """
    Worker function for RSD inverse computation after Bungert et al. (2017) [1]- call from multiprocessing.pool
    Calculates the RSD inverse for e = (E_mag, E_norm and/or E_tan) for given zaps and elements.
    The computations are parallelized in terms of element indices (elm_idx_list).

    Parameters
    ----------
    elm_idx_list : nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep : list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - e.g.: len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))

    Returns
    -------
    rsd_inv : nparray of float [n_roi, n_datasets]
        RSD inverse in each element specified in elm_idx_list and for each input dataset

    Notes
    -----
    .. [1] Bungert, A., Antunes, A., Espenhahn, S., & Thielscher, A. (2016).
       Where does TMS stimulate the motor cortex? Combining electrophysiological measurements and realistic field
       estimates to reveal the affected cortex position. Cerebral Cortex, 27(11), 5083-5094.
    """

    n_datasets = len(e[0])
    n_elm = len(elm_idx_list)
    n_conditions = len(mep)

    rsd_inv = np.empty((n_elm, n_datasets))
    mt_vec = np.empty((1, n_conditions))

    for i_cond in range(n_conditions):
        mt_vec[0, i_cond] = mep[i_cond].mt

    e_arr = np.array(e)

    for i_dataset in range(n_datasets):
        e_mat = np.array(e_arr[:, i_dataset, np.array(elm_idx_list).astype(int)]).transpose()

        std_vec = np.std(e_mat * mt_vec, axis=1)

        mean_vec = np.mean(e_mat * mt_vec, axis=1)

        rsd_inv[:, i_dataset] = 1 - (std_vec / mean_vec)

    return rsd_inv


def e_focal_workhorse(elm_idx_list, e):
    """
    Worker function to determine the site of stimulation after Aonuma et al. (2018) [1] - call from multiprocessing.pool
    Calculates the site of stimulation for e = (E_mag, E_norm and/or E_tan) for given zaps and elements by multiplying
    the electric fields with each other. The computations are parallelized in terms of element indices (elm_idx_list).

    Parameters
    ----------
    elm_idx_list : nparray [chunksize]
        List of element indices, the congruence factor is computed for
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - e.g.: len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))

    Returns
    -------
    e_focal : nparray of float [n_roi, n_datasets]
        Focal electric field in each element specified in elm_idx_list and for each input dataset

    Notes
    -----
    .. [1] Aonuma, S., Gomez-Tames, J., Laakso, I., Hirata, A., Takakura, T., Tamura, M., & Muragaki, Y. (2018).
       A high-resolution computational localization method for transcranial magnetic stimulation mapping.
       NeuroImage, 172, 85-93.
    """

    n_datasets = len(e[0])
    n_elm = len(elm_idx_list)
    n_conditions = len(e)

    e_focal = np.ones((n_elm, n_datasets))

    for i_dataset in range(n_datasets):
        for i_cond in range(n_conditions):
            e_focal[:, i_dataset] *= e[i_cond][i_dataset][elm_idx_list]

    return e_focal


def e_cog_workhorse(elm_idx_list, mep, mep_params, e):
    """
    Worker function for electric field center of gravity (e_cog) )computation after Opitz et al. (2013) [1]
    - call from multiprocessing.pool. Calculates the e_cog for e = (E_mag, E_norm and/or E_tan) for given zaps
    and elements. The electric field is weighted by the mean MEP amplitude (turning point of the sigmoid) and summed up.
    The computations are parallelized in terms of element indices (elm_idx_list).

    Parameters
    ----------
    elm_idx_list : nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep : list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params: nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        (e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...])
    e : list of list of nparray of float [n_cond][n_datasets][n_elm]
        Tuple of n_datasets of the electric field to compute the congruence factor for, e.g. (e_mag, e_norm, e_tan)
        Each dataset is a list over all conditions containing the electric field component of interest
        - e.g.: len(e) = n_cond
        - len(e[0]) = n_comp (e.g: e_mag = e[0]))

    Returns
    -------
    e_cog : nparray of float [n_roi, n_datasets]
        RSD inverse in each element specified in elm_idx_list and for each input dataset

    Notes
    -----
    .. [1] Opitz, A., Legon, W., Rowlands, A., Bickel, W. K., Paulus, W., & Tyler, W. J. (2013).
       Physiological observations validate finite element models for estimating subject-specific electric field
       distributions induced by transcranial magnetic stimulation of the human motor cortex. Neuroimage, 81, 253-264.
    """

    n_datasets = len(e[0])
    n_elm = len(elm_idx_list)
    n_conditions = len(mep)

    mep_params = np.array(mep_params).flatten()
    mep_params_cond = []
    start_idx = 0
    e_cog = np.empty((n_elm, n_datasets))
    mep_mean_vec = np.empty((1, n_conditions))
    intensity_mep_mean_vec = np.empty((1, n_conditions))

    # extract parameters
    for i_cond in range(n_conditions):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep[i_cond].popt.size)])
        start_idx = start_idx + mep[i_cond].popt.size

        # stimulator intensity in [A/us] for mean MEP amplitude, i.e. turning point of pynibs.sigmoid (1st para of
        # sigmoid)
        intensity_mep_mean_vec[0, i_cond] = mep[i_cond].popt[0]

        # mean MEP amplitude (function value at 1st parameter of pynibs.sigmoid)
        mep_mean_vec[0, i_cond] = mep[i_cond].eval(mep_params_cond[-1][0], mep_params_cond[-1])

    e_arr = np.array(e)

    for i_dataset in range(n_datasets):
        e_mat = np.array(e_arr[:, i_dataset, np.array(elm_idx_list).astype(int)]).transpose()
        e_cog[:, i_dataset] = np.sum(e_mat * (intensity_mep_mean_vec * mep_mean_vec), axis=1)

    return e_cog


def extract_condition_combination(fn_config_cfg, fn_results_hdf5, conds, fn_out_prefix):
    """
    Extract and plot congruence factor results for specific condition combinations from permutation analysis.

    Parameters
    ----------
    fn_config_cfg : str
        Filename of config file the permutation study was cinducted with
        (e.g. .../probands/29965.48/results/electric_field/22_cond_coil_corrected/5-of-22_cond_coil_corrected_Weise.cfg
    fn_results_hdf5 : str
        Filename of results file generated by 00_run_c_standard_compute_all_permutations.py containing congruence
        factors and condition combinations.
        (e.g. /data/pt_01756/probands/29965.48/results/congruence_factor/22_cond_coil_corrected/2_of_20_cond/
        simulations/results.hdf5)
    conds : list of str [n_cond]
        List containing condition combinations to extract and plot.
        (e.g. ['P_0', 'I_225', 'M1_0', 'I_675', 'P_225'])
    fn_out_prefix : str
        Prefix of output filenames of *_data.xdmf, *_data.hdf5 and *_geo.hdf5

    Returns
    -------
    <fn_out_prefix_data.xdmf> : .xdmf file
        Output file linking *_data.hdf5 and *_geo.hdf5 file to plot in paraview.
    <fn_out_prefix_data.hdf5> : .hdf5 file
        Output .hdf5 file containing the data.
    <fn_out_prefix_geo.xdmf> : .hdf5 file
        Output .hdf5 file containing the geometry information.
    """

    # Read config file
    with open(fn_config_cfg, 'r') as f:
        config = yaml.load(f)

    # Initialize parameters
    ###############################################
    fn_subject = config['fn_subject']
    roi_idx = config['roi_idx']
    mesh_idx = config['mesh_idx']
    e_qoi = ['mag', 'norm', 'tan']
    n_qoi = len(e_qoi)

    # load subject object
    subject = pynibs.load_subject(fn_subject)
    mesh_folder = subject.mesh[mesh_idx]["mesh_folder"]

    # loading roi
    roi = pynibs.load_roi_surface_obj_from_hdf5(subject.mesh[mesh_idx]['fn_mesh_hdf5'])

    # load results file
    c_extracted = []

    print((" > Loading results file: {} ...".format(fn_results_hdf5)))
    with h5py.File(fn_results_hdf5) as f:
        # extract condition combination
        print(' > Loading condition labels ...')
        cond_comb = f['conds'][:]

        print(' > Determining condition combination index ...')
        conds_idx = [idx for idx, c in enumerate(cond_comb) if set(c) == set(conds)][0]

        print(' > Loading corresponding congruence factor results ...')
        for qoi_idx, qoi in enumerate(e_qoi):
            e_tri_idx = list(range(0, f['c'].shape[0], n_qoi))
            e_tri_idx = [mag + qoi_idx for mag in e_tri_idx]
            c_extracted.append(f['c'][e_tri_idx, conds_idx][:])

    # map data to whole brain surface
    print(" > Mapping c-factor map to brain surface...")
    c_mapped = pynibs.map_data_to_surface(datasets=[c_extracted[qoi_idx][:, np.newaxis] for qoi_idx in range(n_qoi)],
                                          points_datasets=[roi[roi_idx].node_coord_mid] * n_qoi,
                                          con_datasets=[roi[roi_idx].node_number_list] * n_qoi,
                                          fname_fsl_gm=os.path.join(mesh_folder, subject.mesh[mesh_idx]['fn_lh_gm']),
                                          fname_fsl_wm=os.path.join(mesh_folder, subject.mesh[mesh_idx]['fn_lh_wm']),
                                          delta=subject.roi[mesh_idx][roi_idx]['delta'],
                                          input_data_in_center=True,
                                          return_data_in_center=True,
                                          data_substitute=-1)

    # recreate complete midlayer surface to write in .hdf5 geo file
    points_midlayer, con_midlayer = pynibs.make_GM_WM_surface(
            gm_surf_fname=os.path.join(mesh_folder, subject.mesh[mesh_idx]['fn_lh_gm']),
            wm_surf_fname=os.path.join(mesh_folder, subject.mesh[mesh_idx]['fn_lh_wm']),
            delta=subject.roi[mesh_idx][roi_idx]['delta'],
            x_roi=None,
            y_roi=None,
            z_roi=None,
            layer=1,
            fn_mask=None)

    # write output files
    # save .hdf5 _geo file
    print(" > Creating .hdf5 geo file of mapped and roi only data ...")
    pynibs.write_geo_hdf5_surf(out_fn=fn_out_prefix + '_geo.hdf5',
                               points=points_midlayer,
                               con=con_midlayer,
                               replace=True,
                               hdf5_path='/mesh')

    pynibs.write_geo_hdf5_surf(out_fn=fn_out_prefix + '_geo_roi.hdf5',
                               points=roi[roi_idx].node_coord_mid,
                               con=roi[roi_idx].node_number_list,
                               replace=True,
                               hdf5_path='/mesh')

    # save .hdf5 _data file
    print(" > Creating .hdf5 data file of mapped and roi only data ...")
    pynibs.write_data_hdf5_surf(data=c_mapped,
                                data_names=['c_' + e_qoi[qoi_idx] for qoi_idx in range(n_qoi)],
                                data_hdf_fn_out=fn_out_prefix + '_data.hdf5',
                                geo_hdf_fn=fn_out_prefix + '_geo.hdf5',
                                replace=True)

    pynibs.write_data_hdf5_surf(data=[c_extracted[qoi_idx][:, np.newaxis] for qoi_idx in range(n_qoi)],
                                data_names=['c_' + e_qoi[qoi_idx] for qoi_idx in range(n_qoi)],
                                data_hdf_fn_out=fn_out_prefix + '_data_roi.hdf5',
                                geo_hdf_fn=fn_out_prefix + '_geo_roi.hdf5',
                                replace=True)


def dvs_likelihood(params, x, y, verbose=True, normalize=False, bounds=[(1, 2), (1, 2)]):
    start = time.time()

    # extract parameters
    p = np.zeros(len(params) - 2)

    for i, p_ in enumerate(params):
        if i == 0:
            sigma_x = p_
        elif i == 1:
            sigma_y = p_
        else:
            p[i - 2] = p_

    # denormalize parameters from [0, 1] to bounds
    if normalize:
        sigma_x = sigma_x * (bounds[0][1] - bounds[0][0]) + bounds[0][0]
        sigma_y = sigma_y * (bounds[1][1] - bounds[1][0]) + bounds[1][0]

        for i, p_ in enumerate(p):
            p[i] = p[i] * (bounds[i + 2][1] - bounds[i + 2][0]) + bounds[i + 2][0]

    if sigma_x < 0:
        sigma_x = 0

    if sigma_y < 0:
        sigma_y = 0

    # determine posterior of DVS model with test data
    x_pre = np.linspace(np.min(x), np.max(x), 200000)
    x_post = x_pre + np.random.normal(loc=0., scale=sigma_x, size=len(x_pre))
    y_post = pynibs.sigmoid(x_post, p=p) + np.random.normal(loc=0., scale=sigma_y, size=len(x_pre))

    # bin data
    n_bins = 50
    dx_bins = (np.max(x_pre) - np.min(x_pre)) / n_bins
    x_bins_loc = np.linspace(np.min(x_pre) + dx_bins / 2, np.max(x_pre) - dx_bins / 2, n_bins)

    # determine probabilities of observations
    kde = KernelDensity(bandwidth=0.01, kernel='gaussian')

    l = []

    for i in range(n_bins):
        mask = np.logical_and(x_pre >= (x_bins_loc[i] - dx_bins / 2), x_pre < (x_bins_loc[i] + dx_bins / 2))
        mask_data = np.logical_and(x >= (x_bins_loc[i] - dx_bins / 2), x < (x_bins_loc[i] + dx_bins / 2))

        if np.sum(mask_data) == 0:
            continue

        # determine kernel density estimate
        try:
            kde_bins = kde.fit(y_post[mask][:, np.newaxis])
        except ValueError:
            warnings.warn("kde.fit(y_post[mask][:, np.newaxis]) yield NaN ... skipping bin")
            continue

        # get probability densities at data
        kde_y_post_bins = np.exp(kde_bins.score_samples(y[mask_data][:, np.newaxis]))

        l.append(kde_y_post_bins)

    l = np.concatenate(l)

    # mask out zero probabilities
    l[l == 0] = 1e-100

    # determine log likelihood
    l = np.sum(np.log10(l))

    stop = time.time()

    if verbose:
        parameter_str = [f"p[{i_p}]={p_:.5f}" for i_p, p_ in enumerate(p)]
        print(f"Likelihood: {l:.1f} / sigma_x={sigma_x:.2f}, sigma_y={sigma_y:.2f}  " +
              ", ".join(parameter_str) + f"({stop - start:.2f} sec)")

    return -l


def single_fit(x, y, fun):
    """
    Performs a single fit and returns fit object

    Parameters
    ----------
    x : ndarray of float
        x-values
    y : ndarray of float
        y-values
    fun : function object
        Function object used to fit

    Returns
    -------
    fit : gmodel fit object
        Fit object
    """
    params = inspect.getfullargspec(fun).args[1:]

    limits = dict()
    init_vals = dict()

    if fun == pynibs.linear:
        log_scale = False
        limits["m"] = [-100, 100]
        limits["n"] = [-100, 100]

        init_vals["m"] = 0.3
        init_vals["n"] = -1

    if fun == pynibs.exp0:
        log_scale = False
        limits["x0"] = [0, 1000]
        limits["r"] = [1e-12, 100]

        init_vals["x0"] = np.mean(x)  # 40
        init_vals["r"] = 10 / np.max(x)

    if fun == pynibs.sigmoid:
        log_scale = False

        limits["x0"] = [0, 1000]
        limits["amp"] = [1e-12, 1000]
        limits["r"] = [1e-12, 100]

        init_vals["x0"] = np.mean(x)  # 70
        init_vals["amp"] = np.max(y)
        init_vals["r"] = 10 / np.max(x)

    if fun == pynibs.sigmoid4:
        log_scale = False

        limits["x0"] = [0, 1000]
        limits["amp"] = [1e-12, 1000]
        limits["r"] = [1e-12, 100]
        limits["y0"] = [1e-12, 10]

        init_vals["x0"] = np.mean(x)  # 70
        init_vals["amp"] = np.max(y)
        init_vals["r"] = 10 / np.max(x)
        init_vals["y0"] = 1e-2

    if fun == pynibs.sigmoid_log:
        log_scale = True

        limits["x0"] = [0, 1000]
        limits["amp"] = [1e-12, 1000]
        limits["r"] = [1e-12, 100]

        init_vals["x0"] = np.mean(x)  # 50
        init_vals["amp"] = np.max(y)
        init_vals["r"] = 10 / np.max(x)

    if fun == pynibs.sigmoid4_log:
        log_scale = True

        limits["x0"] = [0, 1000]
        limits["amp"] = [1e-12, 1000]
        limits["r"] = [1e-12, 100]
        limits["y0"] = [1e-6, 1e-1]

        init_vals["x0"] = np.mean(x)  # 50
        init_vals["amp"] = np.max(y)
        init_vals["r"] = 10 / np.max(x)
        init_vals["y0"] = 1e-2

    if log_scale:
        y = np.log10(y)

    # set up gmodel
    gmodel = Model(fun)

    for p in params:
        gmodel.set_param_hint(p, value=init_vals[p], min=limits[p][0], max=limits[p][1])

    gmodel.make_params()

    # perform fit
    fit = gmodel.fit(y, x=x)

    return fit
