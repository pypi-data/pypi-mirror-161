import os
import h5py
import scipy
import pynibs
import numpy as np
import multiprocessing.pool
import matplotlib.pyplot as plt
from _functools import partial
from sklearn.neighbors import KernelDensity


def workhorse_mc(idx_list, array, ele_idx_1, mode="cols"):
    """
    Determines mutual coherence for given zap indices in idx_list.

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    ele_idx_1 : ndarray of float [n_ele]
        Element indices for which the optimization is performed
    mode : str, optional, default: "cols"
        Set if the mutual coherence is calculated w.r.t. columns or rows ("cols", "rows")

    Returns
    -------
    res : ndarray of float [n_combs]
        Mutual coherence. Lower values indicate more orthogonal e-field combinations (better)
    """

    res = []
    array = array[:, ele_idx_1]

    if array.ndim == 1:
        array = array[:, np.newaxis]

    for ind in idx_list:
        if mode == "cols":
            res.append(pynibs.mutual_coherence(array[ind, :]))
        elif mode == "rows":
            res.append(pynibs.mutual_coherence(array[ind, :].transpose()))
        else:
            raise NotImplementedError("Specified mode not implemented. Choose 'rows' or 'cols'.")

    return res


# TODO Benjamin
def workhorse_corr(idx_list, array, ele_idx_1):
    """

    :param idx_list:
    :param array:
    :param ele_idx_1:
    :return:
    """
    array = array[:, ele_idx_1]

    if array.ndim == 1:
        array = array[:, np.newaxis]

    res = []

    for ind in idx_list:
        r = np.corrcoef(array[ind, :])
        res.append(np.mean(r[np.triu_indices(r.shape[0], k=1)]))

    return res


def workhorse_var(idx_list, array, ele_idx_1):
    array = array[:, ele_idx_1]

    if array.ndim == 1:
        array = array[:, np.newaxis]

    res = []

    for ind in idx_list:
        res.append(np.mean(np.var(array[ind, :], axis=0)))

    return res


def workhorse_smooth(idx_list, array, ele_idx_1):
    array = array[:, ele_idx_1]

    if array.ndim == 1:
        array = array[:, np.newaxis]

    res = []

    for ind in idx_list:
        res.append(np.var(np.mean(array[ind, :], axis=0)))

    return res


def workhorse_svd(idx_list, array, ele_idx_1):
    """
    Determines condition number for given zap indices in idx_list.

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    ele_idx_1 : ndarray of float [n_ele]
        Element indices for which the optimization is performed

    Returns
    -------
    res : ndarray of float [n_combs]
        Condition number. Lower values indicate more orthogonal e-field combinations (better)
    """
    array = array[:, ele_idx_1]

    if array.ndim == 1:
        array = array[:, np.newaxis]

    res = []

    for ind in idx_list:
        s = scipy.linalg.svd(array[ind, :], compute_uv=False)
        res.append(np.max(s)/np.min(s))

    return res


def workhorse_variability(idx_list, array, ele_idx_1):
    """
    Determines variability score for given zap indices in idx_list.

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    ele_idx_1 : ndarray of float [n_ele]
        Element indices for which the optimization is performed

    Returns
    -------
    res : ndarray of float [n_combs]
        Condition number. Lower values indicate more orthogonal e-field combinations (better)
    """
    array = array[:, ele_idx_1]

    if array.ndim == 1:
        array = array[:, np.newaxis]

    res = []

    for ind in idx_list:
        distances = np.zeros((array.shape[1], array.shape[1]))
        d = 0

        for col_idx in range(0, array.shape[1]-1):
            for row_idx in range(col_idx+1, array.shape[1]):
                distances[row_idx, col_idx] = np.linalg.norm(array[ind, row_idx] - array[ind, col_idx])
                d += distances[row_idx, col_idx]

        res.append(1/d)

    return res


def workhorse_dist(idx_list, array, ele_idx_1):
    """
    Determines distance score for given zap indices in idx_list.

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    ele_idx_1 : ndarray of float [n_ele]
        Element indices for which the optimization is performed

    Returns
    -------
    res : ndarray of float [n_combs]
        Distance based score. Lower values indicate more equidistant sampling (better)
    """
    res = np.zeros(len(idx_list))

    array_dist = array[:, ele_idx_1]

    if array_dist.ndim == 1:
        array_dist = array_dist[:, np.newaxis]

    e_max = np.max(array_dist, axis=0)
    e_min = np.min(array_dist, axis=0)

    for j, ind in enumerate(idx_list):
        p = np.vstack((e_min, array_dist[ind, :], e_max))
        d_var = np.zeros(array_dist.shape[1])

        for i in range(array_dist.shape[1]):
            p_sort = np.sort(p[:, i])

            if p_sort[0] == p_sort[1]:
                p_sort = p_sort[1:]

            if p_sort[-2] == p_sort[-1]:
                p_sort = p_sort[:-1]

            d_var[i] = np.var(np.diff(p_sort))

        res[j] = np.mean(d_var)

    return res


def workhorse_dist_svd(idx_list, array, ele_idx_1, ele_idx_2):
    """
    Determines distance score and condition number for given zap indices in idx_list. If c_max_idx is given,
    the distance based score is calculated only for this element.
    The condition number however is optimized for all elements in array

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    ele_idx_1 : ndarray of float [n_ele]
        Element indices for which the dist optimization is performed for
    ele_idx_2 : ndarray of float [n_ele]
        Element indices for which the svd optimization is performed for

    Returns
    -------
    res_dist : ndarray of float [n_combs]
        Distance based score. Lower values indicate more equidistant sampling (better)
    res_svd : ndarray of float [n_combs]
        Condition number. Lower values indicate more orthogonal e-field combinations (better)
    """
    res_dist = np.zeros(len(idx_list))
    res_svd = np.zeros(len(idx_list))

    array_dist = array[:, ele_idx_1]

    if array_dist.ndim == 1:
        array_dist = array_dist[:, np.newaxis]

    array_svd = array[:, ele_idx_2]

    if array_svd.ndim == 1:
        array_svd = array_svd[:, np.newaxis]

    e_max = np.max(array_dist, axis=0)
    e_min = np.min(array_dist, axis=0)

    for j, ind in enumerate(idx_list):

        # svd
        u, s, vh = scipy.linalg.svd(array_svd[ind, :])
        res_svd[j] = np.max(s)/np.min(s)

        # dist
        p = np.vstack((e_min, array_dist[ind, :], e_max))
        d_var = np.zeros(array_dist.shape[1])

        for i in range(array_dist.shape[1]):
            p_sort = np.sort(p[:, i])

            if p_sort[0] == p_sort[1]:
                p_sort = p_sort[1:]

            if p_sort[-2] == p_sort[-1]:
                p_sort = p_sort[:-1]

            d_var[i] = np.var(np.diff(p_sort))

        res_dist[j] = np.mean(d_var)

    return res_dist, res_svd


def workhorse_dist_mc(idx_list, array, ele_idx_1, ele_idx_2, mode="cols"):
    """
    Determines distance score and mutual coherence for given zap indices in idx_list. If c_max_idx is given,
    the distance based score is calculated only for this element.
    The condition number however is optimized for all elements in array

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    mode : str, optional, default: "cols"
        Set if the mutual coherence is calculated w.r.t. columns or rows ("cols", "rows")
    ele_idx_1 : ndarray of float [n_ele]
        Element indices for which the dist optimization is performed for
    ele_idx_2 : ndarray of float [n_ele]
        Element indices for which the mc optimization is performed for

    Returns
    -------
    res_dist : ndarray of float [n_combs]
        Distance based score. Lower values indicate more equidistant sampling (better)
    res_mc : ndarray of float [n_combs]
        Mutual coherence. Lower values indicate more orthogonal e-field combinations (better)
    """
    res_dist = np.zeros(len(idx_list))
    res_mc = np.zeros(len(idx_list))

    array_dist = array[:, ele_idx_1]

    if array_dist.ndim == 1:
        array_dist = array_dist[:, np.newaxis]

    array_mc = array[:, ele_idx_2]

    if array_mc.ndim == 1:
        array_mc = array_mc[:, np.newaxis]

    e_max = np.max(array_dist, axis=0)
    e_min = np.min(array_dist, axis=0)

    for j, ind in enumerate(idx_list):

        # mc
        if mode == "cols":
            res_mc[j] = pynibs.mutual_coherence(array_mc[ind, :])
        elif mode == "rows":
            res_mc[j] = pynibs.mutual_coherence(array_mc[ind, :].transpose())
        else:
            raise NotImplementedError("Specified mode not implemented. Choose 'rows' or 'cols'.")

        # dist
        p = np.vstack((e_min, array_dist[ind, :], e_max))
        d_var = np.zeros(array_dist.shape[1])

        for i in range(array_dist.shape[1]):
            p_sort = np.sort(p[:, i])

            if p_sort[0] == p_sort[1]:
                p_sort = p_sort[1:]

            if p_sort[-2] == p_sort[-1]:
                p_sort = p_sort[:-1]

            d_var[i] = np.var(np.diff(p_sort))

        res_dist[j] = np.mean(d_var)

    return res_dist, res_mc


def workhorse_coverage_prepare(idx_list, array, zap_idx):
    """Prepares coverage calculation.
    Determines coverage distributions for elements in idx_list given the zaps in zap_idx

    Parameters
    ----------
    idx_list : list [n_ele]
        Index lists of elements.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    zap_idx : ndarray of int
        Included zaps in coverage distribution.

    Returns
    -------
    x : ndarray of float [200 x n_ele]
        x-values of coverage distributions, defined in interval [0, 1] (element wise normalized electric field)
    y : ndarray of float [200 x n_ele]
        y-values of coverage distributions (element wise probability of already included e-fields)
    """

    n_x = 200

    x = np.zeros((n_x, len(idx_list)))
    y = np.zeros((n_x, len(idx_list)))

    kde = KernelDensity(bandwidth=0.03, kernel='gaussian')

    for j, ind in enumerate(idx_list):
        e_min = np.min(array[:, ind])
        e_max = np.max(array[:, ind])
        e_samples = (array[zap_idx, ind] - e_min) / (e_max - e_min)

        if not isinstance(e_samples, np.ndarray):
            e_samples = np.array([e_samples])

        kde_ele = kde.fit(e_samples[:, np.newaxis])
        x[:, j] = np.linspace(0, 1, n_x)
        y[:, j] = np.exp(kde_ele.score_samples(x[:, j][:, np.newaxis]))

    return x, y


def workhorse_coverage(idx_list, array, x, y, ele_idx_1):
    """
    Determine coverage score (likelihood) for given zap indices in idx_list

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    x : ndarray of float [200 x n_ele]
        x-values of coverage distributions, defined in interval [0, 1] (element wise normalized electric field)
    y : ndarray of float [200 x n_ele]
        y-values of coverage distributions (element wise probability of already included e-fields)
    ele_idx_1 : ndarray of float [n_roi]
        Element indices for which the coverage optimization is performed for

    Returns
    -------
    res : ndarray of float [n_combs]
        Coverage score (likelihood) for given electric field combinations. Lower values indicate that the
        new zap fills a gap which was not covered before.
    """

    p_e = np.zeros(len(idx_list))

    array = array[:, ele_idx_1]

    if array.ndim == 1:
        array = array[:, np.newaxis]

    for j, ind in enumerate(idx_list):
        p_e_zap = np.zeros(array.shape[1])

        # normalized e-fields of this zap in all elements
        e_zap = (array[ind[-1], :] - np.min(array, axis=0)) / (np.max(array, axis=0) - np.min(array, axis=0))

        # determine e-field coverage probability for every element
        for i_ele in range(array.shape[1]):
            p_e_zap[i_ele] = np.interp(x=e_zap[i_ele], xp=x[:, i_ele], fp=y[:, i_ele])

        # accumulate e-field coverage over ever elements using log-likelihood
        p_e_zap[p_e_zap <= 0] = 1e-100
        p_e[j] = np.sum(p_e_zap)

    return p_e


def workhorse_fim(idx_list, array, ele_idx_1, e_opt, c=None):
    """
    Determine difference between e-fields and optimal e-field determined using the Fisher Information Matrix.

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    ele_idx_1 : ndarray of float [n_roi]
        Element indices for which the fim optimization is performed for
    e_opt : ndarray of float [n_roi]
        Optimal electric field value(s) (target) determined by FIM method
    c : ndarray of float [n_ele], optional, default: None
        Congruence factor map normalized to 1 (whole ROI) used to weight the difference between the optimal e-field
        and the candidate e-field. If None, no weighting is applied.

    Returns
    -------
    res : ndarray of float [n_combs]
        Difference between e-fields and optimal e-field.
    """

    if c is None:
        c = np.ones(array.shape[1])

    res = np.zeros(len(idx_list))

    array = array[:, ele_idx_1]

    if array.ndim == 1:
        array = array[:, np.newaxis]

    for j, ind in enumerate(idx_list):
        res[j] = np.linalg.norm((e_opt - array[ind[-1], ele_idx_1]) * c[ele_idx_1])

    return res


def workhorse_fim_svd(idx_list, array, ele_idx_1, ele_idx_2, e_opt, c=None):
    """
    Determine difference between e-fields and optimal e-field determined using the Fisher Information Matrix and
    condition number.

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    ele_idx_1 : ndarray of float [n_roi_1]
        Element indices for which the fim optimization is performed for
    ele_idx_2 : ndarray of float [n_roi_2]
        Element indices for which the svd optimization is performed for
    e_opt : float
        Optimal electric field value (target) determined by FIM method
    c : ndarray of float [n_ele], optional, default: None
        Congruence factor map normalized to 1 (whole ROI) used to weight the difference between the optimal e-field
        and the candidate e-field. If None, no weighting is applied.

    Returns
    -------
    res_fim : ndarray of float [n_combs]
        Difference between e-fields and optimal e-field.
    res_svd : ndarray of float [n_combs]
        Condition number. Lower values indicate more orthogonal e-field combinations (better)
    """

    if c is None:
        c = np.ones(array.shape[1])

    res_fim = np.zeros(len(idx_list))
    res_svd = np.zeros(len(idx_list))

    array_fim = array[:, ele_idx_1]

    if array_fim.ndim == 1:
        array_fim = array_fim[:, np.newaxis]

    array_svd = array[:, ele_idx_2]

    if array_svd.ndim == 1:
        array_svd = array_svd[:, np.newaxis]

    for j, ind in enumerate(idx_list):
        # fim
        intensity = np.mean(array_fim[ind[-1], :] / e_opt)
        res_fim[j] = np.linalg.norm((e_opt - intensity * array_fim[ind[-1], :]) * c[ele_idx_1])

        # svd
        u, s, vh = scipy.linalg.svd(array_svd[ind, :])
        res_svd[j] = np.max(s)/np.min(s)

    return res_fim, res_svd


def workhorse_fim_mc(idx_list, array, ele_idx_1, ele_idx_2, e_opt, c=None, mode="rows"):
    """
    Determine difference between e-fields and optimal e-field determined using the Fisher Information Matrix and
    mutual coherence.

    Parameters
    ----------
    idx_list : list of lists [n_combs][n_zaps]
        Index lists of zaps containing different possible combinations. Usually only the last index changes.
    array : ndarray of float [n_zaps x n_ele]
        Electric field for different coil positions and elements
    ele_idx_1 : ndarray of float [n_roi_1]
        Element indices for which the fim optimization is performed for
    ele_idx_2 : ndarray of float [n_roi_2]
        Element indices for which the mc optimization is performed for
    e_opt : float
        Optimal electric field value (target) determined by FIM method
    c : ndarray of float [n_ele], optional, default: None
        Congruence factor map normalized to 1 (whole ROI) used to weight the difference between the optimal e-field
        and the candidate e-field. If None, no weighting is applied.

    Returns
    -------
    res_fim : ndarray of float [n_combs]
        Difference between e-fields and optimal e-field.
    res_mc : ndarray of float [n_combs]
        Mutual coherence. Lower values indicate more orthogonal e-field combinations (better)
    """

    if c is None:
        c = np.ones(array.shape[1])

    res_fim = np.zeros(len(idx_list))
    res_mc = np.zeros(len(idx_list))

    array_fim = array[:, ele_idx_1]

    if array_fim.ndim == 1:
        array_fim = array_fim[:, np.newaxis]

    array_mc = array[:, ele_idx_2]

    if array_mc.ndim == 1:
        array_mc = array_mc[:, np.newaxis]

    for j, ind in enumerate(idx_list):
        # fim
        res_fim[j] = np.linalg.norm((e_opt - array_fim[ind[-1], :]) * c[ele_idx_1])

        # mc
        if mode == "cols":
            res_mc[j] = pynibs.mutual_coherence(array_mc[ind, :])
        elif mode == "rows":
            res_mc[j] = pynibs.mutual_coherence(array_mc[ind, :].transpose())
        else:
            raise NotImplementedError("Specified mode not implemented. Choose 'rows' or 'cols'.")

    return res_fim, res_mc


def get_optimal_coil_positions(e_matrix, criterion, n_stim, ele_idx_1=None, ele_idx_2=None, fn_out_hdf5=None, n_cpu=4,
                               zap_idx_opt=None, fun=None, p=None, c=None, weights=None,
                               overwrite=True, verbose=True, fn_coilpos_hdf5=None, start_zap_idx=0):
    """
    Determine set of optimal coil positions for TMS regression analysis.

    Parameters
    ----------
    e_matrix : ndarray of float [n_stim, n_ele]
        Matrix containing the electric field values in the ROI
    criterion : str
        Optimization criterion:
        - "mc_cols": Minimization of mutual coherence between columns
        - "mc_rows": Minimization of mutual coherence between rows
        - "svd": Minimization of condition number
        - "dist": Equal distant sampling
        - "dist_svd": Minimization of condition number and equidistant sampling
        - "dist_mc_cols": Minimization of mutual coherence between columns and equidistant sampling
        - "dist_mc_rows": Minimization of mutual coherence between rows and equidistant sampling
        - "coverage": Maximizes the electric field coverage
        - "variability": Maximizes variability between elements
    n_stim : int
        Maximum number of stimulations
    ele_idx_1 : ndarray of int, optional, default: None
        Element indices the first optimization goal is performed for, If None, all elements are consiered
    ele_idx_2 : ndarray of int, optional, default: None
        Element indices the first optimization goal is performed for. If None, all elements are consiered
    n_cpu : int
        Number of threads
    fn_out_hdf5 : str, optional, default: None
        Returns the list of optimal zap indices if fn_out_hdf5 is None, otherwise, save the results in .hdf5 file.
        Filename of output .hdf5 file where the zap index lists are saved in subfolder "zap_index_lists"
        - "zap_index_lists/0": [213]
        - "zap_index_lists/1": [213, 5]
        - etc
    zap_idx_opt : list of int, optional, default: None
        List of already selected optimal coil positions
        (those are ignored in the optimization and will not be picked again)
    fun : function object
        Function object defined in interval [0, 1]. (only needed for fim optimization)
    p : list of dict [n_ele], optional, default: None
        List of dicts containing the parameter estimates (whole ROI). The keys are the parameter names of fun.
        (only needed for fim and dist optimization)
    c : ndarray of float [n_ele], optional, default: None
        Congruence factor in each ROI element. Used to weight fim and dist optimization.
        (only needed for fim and dist optimization)
    weights : list of float [2], optional, default: [0.5, 0.5]
        Weights of optimization criteria in case of multiple goal functions (e.g. fim_svd). Higher weight means higher
        importance for the respective criteria. By default both optimization criteria are weighted equally [0.5, 0.5].
    overwrite : bool, optional, default: True
        Overwrite existing solutions or read existing hdf5 file and continue optimization
    verbose : bool, optional, default: True
        Print output messages
    fn_coilpos_hdf5 : str
        File containing the corresponding coil positions and orientations (centers, m0, m1, m2)
    start_zap_idx : int, optional, default: 0
        First zap index to start greedy search

    Returns
    -------
    zap_idx_e_opt : list of int [n_stim]
        Optimal zap indices
    <File> .hdf5 file
        Output file containing the zap index lists
    """

    if weights is None:
        weights = [0.5, 0.5]
    if zap_idx_opt is not None and fn_out_hdf5 is not None and (os.path.exists(fn_out_hdf5) and not overwrite):
        raise ValueError("zap_idx_opt and fn_out_hdf5 given... please choose whether to load optimal zap indices from "
                         "file or given explicitly as list")

    e = e_matrix
    x = np.zeros((1, 1))
    y = np.zeros((1, 1))

    if ele_idx_1 is None:
        ele_idx_1 = np.arange(e.shape[1])

    if ele_idx_2 is None:
        ele_idx_2 = np.arange(e.shape[1])

    if c is not None:
        c = c / np.max(c)

    zap_idx_e_opt = [0 for _ in range(n_stim)]
    crit = np.zeros(n_stim)

    if zap_idx_opt is not None:
        kmax = len(zap_idx_opt)-1
        zap_idx_e_opt[len(zap_idx_opt)-1] = zap_idx_opt
        idx_rem = [i for i in range(e.shape[0]) if i not in zap_idx_e_opt[int(kmax)]]
    else:
        kmax = 0
        zap_idx_e_opt[0] = [start_zap_idx]
        idx_rem = [i for i in range(1, e.shape[0])]

    if fn_coilpos_hdf5 is not None:
        with h5py.File(fn_coilpos_hdf5, "r") as f:
            centers = f["centers"][:]
            m0 = f["m0"][:]
            m1 = f["m1"][:]
            m2 = f["m2"][:]

    pool = multiprocessing.Pool(n_cpu)

    if fn_out_hdf5 is not None:
        if not overwrite and os.path.exists(fn_out_hdf5):
            # load already present optimization results
            with h5py.File(fn_out_hdf5, "r") as f:

                kmax = 0

                try:
                    keys = f[f"zap_index_lists"].keys()
                    crit = f["criterion"][:]

                    for k in keys:
                        zap_idx_e_opt[int(k)] = list(f[f"zap_index_lists/{k}"][:])

                        if int(k) > kmax:
                            kmax = int(k)

                    # check if loaded sequence starts with the same zap index as intended
                    if zap_idx_e_opt[0] != [start_zap_idx]:
                        kmax = 0
                        zap_idx_e_opt = [0 for _ in range(n_stim)]
                        zap_idx_e_opt[0] = [start_zap_idx]
                        if verbose:
                            print(f"Loaded sequence does not start with specified start idx (restarting optimization)")
                            print(f"=================================================================================")
                    else:
                        if verbose:
                            print(f"Loading optimal index set for n={kmax+1}")
                            print(f"====================================")

                except KeyError:
                    pass

                idx_rem = [i for i in range(e.shape[0]) if i not in zap_idx_e_opt[kmax]]

        else:
            # save first zap
            with h5py.File(fn_out_hdf5, "w") as f:
                f.create_dataset(f"zap_index_lists/0", data=zap_idx_e_opt[0])

    for i in range(kmax+1, n_stim):
        if verbose:
            # if kmax == 0:
            #     print(f"Initializing greedy algorithm for n={i}")
            #     print(f"=====================================")
            #     print(f" >>> Chosen index: {start_zap_idx}")

            print(f"Calculating optimal idx for n={i+1}")
            print(f"==================================")

        # prepare calculations for "coverage" criterion
        if criterion == "coverage":
            workhorse_prepare = partial(workhorse_coverage_prepare, array=e, zap_idx=zap_idx_e_opt[i-1])
            ele_idx_list_chunks = pynibs.compute_chunks([j for j in range(e.shape[1])], n_cpu)
            res = pool.map(workhorse_prepare, ele_idx_list_chunks)

            for j in range(len(res)):
                if j == 0:
                    x = res[0][0]
                    y = res[0][1]
                else:
                    x = np.hstack((x, res[j][0]))
                    y = np.hstack((y, res[j][1]))

            workhorse_partial = partial(workhorse_coverage, array=e, x=x, y=y)

        if "fim" in criterion:

            # normalize e-field to [0, 1]
            x = (e[zap_idx_opt, :][:, ele_idx_1] - np.min(e[:, ele_idx_1], axis=0)) / \
                (np.max(e[:, ele_idx_1], axis=0) - np.min(e[:, ele_idx_1], axis=0))

            # determine optimal e-fields for next zap
            e_opt_norm = np.zeros(len(ele_idx_1))
            for i_ele, e_idx_1 in enumerate(ele_idx_1):
                e_opt_norm[i_ele] = pynibs.get_optimal_sample_fim(fun=fun, x=x[:, i_ele], p=p[e_idx_1])

            e_opt = e_opt_norm * (np.max(e[:, ele_idx_1], axis=0) - np.min(e[:, ele_idx_1], axis=0)) + \
                    np.min(e[:, ele_idx_1], axis=0)

        if criterion == "svd":
            workhorse_partial = partial(workhorse_svd, array=e, ele_idx_1=ele_idx_1)

        elif criterion == "dist":
            workhorse_partial = partial(workhorse_dist, array=e, ele_idx_1=ele_idx_1)

        elif criterion == "mc_cols":
            e = e - np.mean(e[:, ele_idx_1], axis=1)[:, np.newaxis]
            workhorse_partial = partial(workhorse_mc, array=e, ele_idx_1=ele_idx_1, mode="cols")

        elif criterion == "mc_rows":
            workhorse_partial = partial(workhorse_mc, array=e, ele_idx_1=ele_idx_1, mode="rows")

        elif criterion == "variability":
            workhorse_partial = partial(workhorse_variability, array=e, ele_idx_1=ele_idx_1)

        elif criterion == "dist_mc_cols":
            if weights[0] == 0:
                workhorse_partial = partial(workhorse_mc, array=e, ele_idx_1=ele_idx_2, mode="cols")
            elif weights[1] == 0:
                workhorse_partial = partial(workhorse_dist, array=e, ele_idx_1=ele_idx_1)
            else:
                workhorse_partial = partial(workhorse_dist_mc, array=e, ele_idx_1=ele_idx_1, ele_idx_2=ele_idx_2,
                                            mode="cols")

        elif criterion == "dist_mc_rows":
            if weights[0] == 0:
                workhorse_partial = partial(workhorse_mc, array=e, ele_idx_1=ele_idx_2, mode="rows")
            elif weights[1] == 0:
                workhorse_partial = partial(workhorse_dist, array=e, ele_idx_1=ele_idx_1)
            else:
                workhorse_partial = partial(workhorse_dist_mc, array=e, ele_idx_1=ele_idx_1, ele_idx_2=ele_idx_2,
                                            mode="rows")

        elif criterion == "dist_svd":
            if weights[0] == 0:
                workhorse_partial = partial(workhorse_svd, array=e, ele_idx_1=ele_idx_2)
            elif weights[1] == 0:
                workhorse_partial = partial(workhorse_dist, array=e, ele_idx_1=ele_idx_1)
            else:
                workhorse_partial = partial(workhorse_dist_svd, array=e, ele_idx_1=ele_idx_1, ele_idx_2=ele_idx_2)

        elif criterion == "fim":
            workhorse_partial = partial(workhorse_fim, array=e, ele_idx_1=ele_idx_1, e_opt=e_opt, c=c)

        elif criterion == "fim_svd":
            if weights[0] == 0:
                workhorse_partial = partial(workhorse_svd, array=e, ele_idx_1=ele_idx_2)
            elif weights[1] == 0:
                workhorse_partial = partial(workhorse_fim, array=e, ele_idx_1=ele_idx_1, e_opt=e_opt, c=c)
            else:
                workhorse_partial = partial(workhorse_fim_svd, array=e, ele_idx_1=ele_idx_1, ele_idx_2=ele_idx_2,
                                            e_opt=e_opt, c=c)

        elif criterion == "fim_mc_rows":
            if weights[0] == 0:
                workhorse_partial = partial(workhorse_mc, array=e, ele_idx_1=ele_idx_2, mode="rows")
            elif weights[1] == 0:
                workhorse_partial = partial(workhorse_fim, array=e, ele_idx_1=ele_idx_1, e_opt=e_opt, c=c)
            else:
                workhorse_partial = partial(workhorse_fim_mc, array=e, ele_idx_1=ele_idx_1, ele_idx_2=ele_idx_2,
                                            e_opt=e_opt, c=c, mode="rows")

        elif criterion == "fim_mc_cols":
            if weights[0] == 0:
                workhorse_partial = partial(workhorse_mc, array=e, ele_idx_1=ele_idx_2, mode="cols")
            elif weights[1] == 0:
                workhorse_partial = partial(workhorse_fim, array=e, ele_idx_1=ele_idx_1, e_opt=e_opt, c=c)
            else:
                workhorse_partial = partial(workhorse_fim_mc, array=e, ele_idx_1=ele_idx_1, ele_idx_2=ele_idx_2,
                                            e_opt=e_opt, c=c, mode="cols")

        else:
            raise NameError(f"criterion: {criterion} not implemented")

        # determine criterion
        idx_list = []
        for j in range(len(idx_rem)):
            idx_list.append(zap_idx_e_opt[i-1] + [idx_rem[j]])

        idx_list_chunks = pynibs.compute_chunks(idx_list, n_cpu)
        res = pool.map(workhorse_partial, idx_list_chunks)

        # extract best solution (multiple objectives)
        if type(res[0]) is tuple:

            for j in range(len(res)):
                if j == 0:
                    res_all = np.vstack(res[j]).transpose()
                else:
                    res_all = np.vstack((res_all, np.vstack(res[j]).transpose()))

            # filter nans # TODO: not to 1e6 -> max of each opt criterion (column)
            res_all[np.isnan(res_all)] = 1e6
            res_all[res_all == 0] = 1e-6

            # normalize both optimization criteria to [0, 1]
            res_all = (res_all - np.min(res_all, axis=0)) / (np.max(res_all, axis=0) - np.min(res_all, axis=0))

            # weight optimization criteria
            res_all = res_all * weights

            # find the best solution with the lowest sum
            res_all_sum = np.sum(res_all, axis=1)
            idx_best = np.argmin(res_all_sum)
            crit[i] = res_all_sum[idx_best]

        # extract best solution (single objective)
        else:
            # filter nans
            res = np.concatenate(res)
            res[np.isnan(res)] = 1e6

            # find best solution
            idx_best = np.argmin(res)
            crit[i] = res[idx_best]

        if verbose:
            print(f" >>> Best index: {idx_rem[idx_best]}, criterion: {crit[i]}")

        zap_idx_e_opt[i] = zap_idx_e_opt[i-1] + [idx_rem[idx_best]]
        idx_rem = [k for k in idx_rem if k != idx_rem[idx_best]]

        if fn_out_hdf5 is not None:
            # save results
            with h5py.File(fn_out_hdf5, "a") as f:
                try:
                    del f["criterion"]
                except (RuntimeError, KeyError):
                    f.create_dataset("criterion", data=crit)

                try:
                    f.create_dataset(f"zap_index_lists/{i}", data=zap_idx_e_opt[i])
                except (RuntimeError, KeyError):
                    if overwrite:
                        del f[f"zap_index_lists/{i}"]
                        f.create_dataset(f"zap_index_lists/{i}", data=zap_idx_e_opt[i])
                    else:
                        print(f"Could not write zap_index_lists/{i}. Dataset already exists.")

                if fn_coilpos_hdf5 is not None:
                    try:
                        del f["centers"], f["m0"], f["m1"], f["m2"]
                    except (RuntimeError, KeyError):
                        if overwrite:
                            f.create_dataset("centers", data=centers[zap_idx_e_opt[i], :])
                            f.create_dataset("m0", data=m0[zap_idx_e_opt[i], :])
                            f.create_dataset("m1", data=m1[zap_idx_e_opt[i], :])
                            f.create_dataset("m2", data=m2[zap_idx_e_opt[i], :])

    pool.close()
    pool.join()

    if fn_out_hdf5 is None:
        return zap_idx_e_opt[-1]
    else:
        with h5py.File(fn_out_hdf5, "a") as f:
            try:
                f.create_dataset(f"zap_index_list", data=np.array(zap_idx_e_opt[-1])[:, np.newaxis])
            except (RuntimeError, KeyError):
                if overwrite:
                    del f[f"zap_index_list"]
                    f.create_dataset(f"zap_index_list", data=np.array(zap_idx_e_opt[-1])[:, np.newaxis])
                else:
                    print(f"Could not write zap_index_list. Dataset already exists.")

            if fn_coilpos_hdf5 is not None:
                m0_opt_reshaped = np.hstack((m0[zap_idx_e_opt[-1], :],
                                             np.zeros((len(zap_idx_e_opt[-1]), 1)))).T[:, np.newaxis, :]
                m1_opt_reshaped = np.hstack((m1[zap_idx_e_opt[-1], :],
                                             np.zeros((len(zap_idx_e_opt[-1]), 1)))).T[:, np.newaxis, :]
                m2_opt_reshaped = np.hstack((m2[zap_idx_e_opt[-1], :],
                                             np.zeros((len(zap_idx_e_opt[-1]), 1)))).T[:, np.newaxis, :]
                centers_opt_reshaped = np.hstack((centers[zap_idx_e_opt[-1], :],
                                                  np.ones((len(zap_idx_e_opt[-1]), 1)))).T[:, np.newaxis, :]
                matsimnibs = np.concatenate((m0_opt_reshaped,
                                             m1_opt_reshaped,
                                             m2_opt_reshaped,
                                             centers_opt_reshaped), axis=1)

                try:
                    f.create_dataset("centers", data=centers[zap_idx_e_opt[-1], :])
                    f.create_dataset("m0", data=m0[zap_idx_e_opt[-1], :])
                    f.create_dataset("m1", data=m1[zap_idx_e_opt[-1], :])
                    f.create_dataset("m2", data=m2[zap_idx_e_opt[-1], :])
                    f.create_dataset("matsimnibs", data=matsimnibs)
                except (RuntimeError, KeyError):
                    if overwrite:
                        del f["centers"], f["m0"], f["m1"], f["m2"]
                        f.create_dataset("centers", data=centers[zap_idx_e_opt[-1], :])
                        f.create_dataset("m0", data=m0[zap_idx_e_opt[-1], :])
                        f.create_dataset("m1", data=m1[zap_idx_e_opt[-1], :])
                        f.create_dataset("m2", data=m2[zap_idx_e_opt[-1], :])
                        f.create_dataset("matsimnibs", data=matsimnibs)
                    else:
                        print(f"Could not write centers, m0, m1, m2 ... Dataset already exists.")


def online_optimization(fn_subject_hdf5, fn_roi_ss_indices_hdf5, fn_out_hdf5, fn_stimsites_hdf5, e_matrix, mep,
                        mesh_idx, roi_idx, n_zaps_init=3, criterion_init="mc_rows", criterion="coverage", n_cpu=4,
                        threshold=0.8, weights=None, eps0=0.01, eps0_dist=1, exponent=5, perc=99,
                        n_refit=0, fun=pynibs.sigmoid, verbose=True):
    """
    Performs virtual online optimization to determine the congruence factor. After an initial set of coil positions,
    the algorithm iteratively optimizes the next coil position based on the virtually measured MEP data.

    Parameters
    ----------
    fn_subject_hdf5 : str
        Filename of subject .hdf5 file
    fn_roi_ss_indices_hdf5 : str
        Filename of .hdf5 file containing the element indices of the subsampled ROI in f["roi_indices"]
    e_matrix : ndarray of float [n_zaps x n_ele]
        Electric field matrix
    mep : ndarray of float [n_zaps]
        Motor evoked potentials for every stimulation
    fn_out_hdf5 : str
        Filename of .hdf5 output file containing the coil positions and the congruence factor maps for every iteration
    fn_stimsites_hdf5 : str
        Filename of the .hdf5 file containing the stimulation sites in "centers", "m0", "m1", "m2"
    mesh_idx : int
        Mesh index
    roi_idx : int
        ROI index
    n_zaps_init : int, optional, default: 3
        Number of initial samples optimized using optimization criterion specified in "criterion_init"
    criterion_init : str, optional, default: "mc_rows"
        Optimization criterion for which the initial samples are optimized (e.g. "mc_rows", "svd", ...)
    criterion : str, optional, default: "coverage"
        Optimization criterion for which the online optimization is performed (e.g. "coverage", "mc_rows", "svd", ...)
    n_cpu : int, optional, dfault: 4
        Number of CPU cores to use
    threshold : float, optional, default: 0.1
        Threshold between [0 ... 1] of the maximal congruence factor. Elements where c > threshold * max(c)
        are included in the online optimization to select the next optimal coil position.
    weights : list of float [2], optional, default: [0.5, 0.5]
        Weights of optimization criteria in case of multiple goal functions (e.g. fim_svd). Higher weight means higher
        importance for the respective criteria. By default both optimization criteria are weighted equally [0.5, 0.5].
    eps0 : float, optional, default: 0.01
        First error threshold to terminate the online optimization. The normalized root mean square deviation is
        calculated between the current and the previous solution. If the error is lower than eps0 for 3 times in a row,
        the online optimization terminates and returns the results.
    eps0_dist : float, optional, default: 1
        Second error threshold to terminate the online optimization. The geodesic distance in mm of the hotspot is
        calculated between the current and the previous solution. If the error is lower than eps0_dist for 3 times
        in a row, the online optimization terminates and returns the results.
    exponent : float, optional, default: 5
        Exponent the congruence factor map is scaled c**exponent
    perc : float, optional, default: 99
        Percentile the congruence factor map is normalized (between 0 and 100)
    n_refit : int, optional, default: 0
        Number of refit iterations. No refit is applied if n_refit=0.
    fun : function object, optional, default: pynibs.linear
        Function to use to determine the congruence factor (e.g. pynibs.linear, pynibs.sigmoid, ...)
    verbose : bool, optional, default: True
        Plot output messages

    Returns
    -------
    <file> .hdf5 file
        Results output file containing the coil positions and the congruence factor maps for every iteration

    """
    if weights is None:
        weights = [0.5, 0.5]
    print("Starting online congruence factor optimization:")
    print("===============================================")
    print(f" > fn_subject_hdf5:          {fn_subject_hdf5}")
    print(f" > fn_roi_ss_indices_hdf5:   {fn_roi_ss_indices_hdf5}")
    print(f" > fn_stimsites_hdf5:        {fn_stimsites_hdf5}")
    print(f" > fn_out_hdf5:              {fn_out_hdf5}")
    print(f" > e_matrix:                 shape: {e_matrix.shape}")
    print(f" > mep:                      shape: {mep.shape}")
    print(f" > mesh_idx:                 {mesh_idx}")
    print(f" > roi_idx:                  {roi_idx}")
    print(f" > n_zaps_init:              {n_zaps_init}")
    print(f" > criterion_init:           {criterion_init}")
    print(f" > criterion:                {criterion}")
    print(f" > n_cpu:                    {n_cpu}")
    print(f" > threshold:                {threshold}")
    print(f" > weights:                  {weights}")
    print(f" > eps0:                     {eps0}")
    print(f" > eps0_dist:                {eps0_dist}")
    print(f" > exponent:                 {exponent}")
    print(f" > perc:                     {perc}")
    print(f" > n_refit:                  {n_refit}")
    print(f" > fun:                      {fun.__name__}")
    print(f" > verbose:                  {verbose}")
    print("")

    zap_idx = dict()
    c = dict()

    # load subject
    if verbose:
        print(f"Loading subject")
    subject = pynibs.load_subject(fn_subject_hdf5)

    # load ROI and perform subsampling
    if verbose:
        print(f"Loading ROI and perform subsampling")
    roi = pynibs.load_roi_surface_obj_from_hdf5(subject.mesh[mesh_idx]['fn_mesh_hdf5'])[roi_idx]
    con = roi.node_number_list
    points = roi.node_coord_mid

    with h5py.File(fn_roi_ss_indices_hdf5, "r") as f:
        ele_idx_ss = f["roi_indices"][:]

    # e-fields
    if verbose:
        print(f"Loading electric field from regression.hdf5")
    n_ele = e_matrix.shape[1]

    # loading coil positions and create matsimnibs [4x4] matrices
    with h5py.File(fn_stimsites_hdf5, "r") as f:
        centers_all = f["centers"][:]
        m0_all = f["m0"][:]
        m1_all = f["m1"][:]
        m2_all = f["m2"][:]

    coil_mean = dict()
    current_dict = dict()

    for i in range(centers_all.shape[0]):
        coil_mean[str(i)] = np.hstack((m0_all[i, :][:, np.newaxis],
                                       m1_all[i, :][:, np.newaxis],
                                       m2_all[i, :][:, np.newaxis],
                                       centers_all[i, :][:, np.newaxis]))
        current_dict[str(i)] = 1

    # determine initial number of optimal samples
    if verbose:
        print(f"Determine optimal coil positions for initial number of {n_zaps_init} samples using {criterion_init}")

    zap_idx_opt = pynibs.get_optimal_coil_positions(e_matrix=e_matrix,
                                                    ele_idx_1=ele_idx_ss,
                                                    ele_idx_2=None,
                                                    criterion=criterion_init,
                                                    n_stim=n_zaps_init,
                                                    fn_out_hdf5=None,
                                                    n_cpu=n_cpu,
                                                    zap_idx_opt=None,
                                                    weights=weights,
                                                    overwrite=False,
                                                    verbose=True)

    # determine initial c-factor map for all N (not existing in real life)
    if verbose:
        print(f"Determine reference c-factor map (N)")

    c_ref_n = pynibs.regress_data(elm_idx_list=np.arange(n_ele),
                                  e_matrix=e_matrix,
                                  mep=mep,
                                  zap_idx=None,
                                  fun=fun,
                                  n_refit=n_refit,
                                  n_cpu=n_cpu,
                                  con=con,
                                  return_fits=False,
                                  refit_discontinuities=True)

    ref_n = c_ref_n.flatten()**exponent
    ref_n = ref_n / np.percentile(ref_n, perc)

    c_max_idx_N = np.argmax(c_ref_n)

    ##########################################################################
    #
    # Robot measures initial offline optimal coil positions and collects MEPs
    #
    ##########################################################################

    # determine initial c-factor map (after robot measured first offline optimal coil positions)
    if verbose:
        print(f"Determine initial c-factor map")

    c_init, p = pynibs.regress_data(elm_idx_list=np.arange(n_ele),
                                    e_matrix=e_matrix,
                                    mep=mep,
                                    zap_idx=zap_idx_opt,
                                    fun=fun,
                                    n_refit=n_refit,
                                    n_cpu=n_cpu,
                                    con=con,
                                    return_fits=True,
                                    refit_discontinuities=True)
    ref = c_init.flatten()**exponent
    ref = ref / np.percentile(ref, perc)

    eps = [eps0 + 1 for _ in range(len(zap_idx_opt))]
    eps_n = [eps0 + 1 for _ in range(len(zap_idx_opt))]

    gdist = [eps0_dist + 1 for _ in range(len(zap_idx_opt))]
    gdist_n = [eps0_dist + 1 for _ in range(len(zap_idx_opt))]

    for i in range(len(zap_idx_opt)):
        zap_idx[str(i)] = zap_idx_opt[:(i+1)]
        c[str(i)] = np.zeros(ref.shape)

    c[str(n_zaps_init-1)] = c_init

    n_zaps = [i for i in range(1, n_zaps_init+1)]

    # Start online optimization loop
    while not ((np.array(eps[-3:]) < eps0).all() and (np.array(gdist[-3:]) < eps0_dist).all()):

        if "fim" in criterion or "dist_" in criterion:
            # find elements with values greater than threshold
            mask_perc = ref >= threshold*np.max(ref)
            ele_idx_1 = np.where(mask_perc)[0]
            ele_idx_2 = ele_idx_ss

        else:
            ele_idx_1 = ele_idx_ss
            ele_idx_2 = ele_idx_ss

        # optimize coil positions for subset of ROI elements
        if verbose:
            print(f"Optimizing next coil position for ROI_1: {len(ele_idx_1)} / ROI_2: {len(ele_idx_2)} elements "
                  f"using {criterion}")

        n_zaps.append(n_zaps[-1] + 1)
        zap_idx_opt = pynibs.get_optimal_coil_positions(e_matrix=e_matrix,
                                                        ele_idx_1=ele_idx_1,
                                                        ele_idx_2=ele_idx_2,
                                                        criterion=criterion,
                                                        n_stim=n_zaps[-1],
                                                        fn_out_hdf5=None,
                                                        n_cpu=n_cpu,
                                                        zap_idx_opt=zap_idx_opt,
                                                        fun=fun,
                                                        p=p,
                                                        c=ref,
                                                        weights=weights,
                                                        overwrite=False,
                                                        verbose=True)
        key = str(len(zap_idx_opt)-1)
        zap_idx[key] = zap_idx_opt

        ##########################################################################
        #
        # Robot measures next optimal coil position
        #
        ##########################################################################

        # determine updated c-factor map
        if verbose:
            print(f"Determine c-factor map for {len(zap_idx_opt)} zaps")

        c[key], p = pynibs.regress_data(elm_idx_list=np.arange(n_ele),
                                        e_matrix=e_matrix,
                                        mep=mep,
                                        zap_idx=zap_idx_opt,
                                        fun=fun,
                                        n_refit=n_refit,
                                        n_cpu=n_cpu,
                                        con=con,
                                        return_fits=True,
                                        refit_discontinuities=True)
        arr = c[key].flatten()**exponent
        arr = arr / np.percentile(arr, perc)

        ##########################################################################
        #
        # Plot updated c-factor map
        #
        ##########################################################################

        # determine NRMSD w.r.t. previous solution
        eps.append(pynibs.nrmsd(arr, ref))

        if verbose:
            print(f"NRMSD to previous solution: {eps[-1]}")

        # determine NRMSD w.r.t. global solution (not existing in real life)
        eps_n.append(pynibs.nrmsd(arr, ref_n))

        if verbose:
            print(f"NRMSD to global solution: {eps_n[-1]}")

        # determine geodesic distance w.r.t. previous solution
        nodes_dist, tris_dist = pynibs.geodesic_dist(nodes=points, tris=con, source=np.argmax(c[key]),
                                                     source_is_node=False)
        gdist.append(tris_dist[np.argmax(c[str(len(zap_idx_opt)-2)])])

        if verbose:
            print(f"GDIST to previous solution: {gdist[-1]:.3f} mm")

        # determine geodesic distance w.r.t. global solution (not existing in real life)
        gdist_n.append(tris_dist[c_max_idx_N])

        if verbose:
            print(f"GDIST to global solution: {gdist_n[-1]:.3f} mm")

        # set current solution as ref
        ref = arr

    eps_n = np.array(eps_n)
    eps = np.array(eps)
    gdist_n = np.array(gdist_n)
    gdist = np.array(gdist)
    n_zaps = np.array(n_zaps)

    if verbose:
        print(f"Saving results to {fn_out_hdf5}")

    with h5py.File(fn_out_hdf5, "w") as f:
        f.create_dataset("nrmsd", data=eps_n)
        f.create_dataset("nrmsd_n_1", data=eps)
        f.create_dataset("gdist", data=gdist_n)
        f.create_dataset("gdist_n_1", data=gdist)
        f.create_dataset("n_zaps", data=n_zaps)
        f.create_dataset(f"c_ref", data=c_ref_n)

        for key in zap_idx:
            f.create_dataset(f"zap_index_lists/{key}", data=zap_idx[key])
            f.create_dataset(f"c/{key}", data=c[key])

            n_zaps_tmp = len(zap_idx[key])
            centers = np.zeros((n_zaps_tmp, 3))
            m0 = np.zeros((n_zaps_tmp, 3))
            m1 = np.zeros((n_zaps_tmp, 3))
            m2 = np.zeros((n_zaps_tmp, 3))
            current = np.zeros((n_zaps_tmp, 1))

            for i, j in enumerate(zap_idx[key]):
                centers[i, :] = coil_mean[str(j)][0:3, 3]
                m0[i, :] = coil_mean[str(j)][0:3, 0]
                m1[i, :] = coil_mean[str(j)][0:3, 1]
                m2[i, :] = coil_mean[str(j)][0:3, 2]
                current[i, 0] = current_dict[str(j)]

            f.create_dataset(f"centers/{key}", data=centers)
            f.create_dataset(f"m0/{key}", data=m0)
            f.create_dataset(f"m1/{key}", data=m1)
            f.create_dataset(f"m2/{key}", data=m2)
            f.create_dataset(f"current/{key}", data=current)

    # create geo .hdf5
    fn_geo_hdf5 = os.path.splitext(fn_out_hdf5)[0] + "_geo.hdf5"
    pynibs.write_geo_hdf5_surf(out_fn=fn_geo_hdf5,
                               points=points,
                               con=con,
                               replace=True,
                               hdf5_path='/mesh')

    # write xdmf file with optimal results
    if verbose:
        print(f"Creating .xdmf ...")

    pynibs.write_temporal_xdmf(hdf5_fn=fn_out_hdf5,
                               data_folder='c',
                               coil_center_folder="centers",
                               coil_ori_0_folder="m0",
                               coil_ori_1_folder="m1",
                               coil_ori_2_folder="m2",
                               coil_current_folder="current",
                               hdf5_geo_fn=fn_geo_hdf5,
                               overwrite_xdmf=True,
                               verbose=False)

    # plot results
    fn_plot_nrmsd = os.path.splitext(fn_out_hdf5)[0] + "_nrmsd.png"
    fn_plot_gdist = os.path.splitext(fn_out_hdf5)[0] + "_gdist.png"

    if verbose:
        print(f"Plotting results to {fn_plot_nrmsd}")

    sort_idx = np.argsort(n_zaps)
    n_zaps = n_zaps[sort_idx]
    eps_n = eps_n[sort_idx]
    eps = eps[sort_idx]

    # nrmsd (n vs N) error
    plt.plot(n_zaps[n_zaps_init:], eps_n[n_zaps_init:], color="r")

    # nrmsd (n vs n-1) error
    plt.plot(n_zaps[n_zaps_init:], eps[n_zaps_init:], color="b")

    # 5% error bar
    plt.plot(np.array([n_zaps[4], n_zaps[-1]]), np.array([0.05, 0.05]), "r--")

    # 1% error bar
    plt.plot(np.array([n_zaps[4], n_zaps[-1]]), np.array([0.01, 0.01]), "b--")

    plt.grid()
    plt.xlabel("n", fontsize=11)
    plt.ylabel("NRMSD", fontsize=11)
    plt.ylim([0, 0.2])
    # plt.xscale("log")
    plt.title("Convergence analysis of online optimization", fontsize=11)
    plt.legend(["n vs N", "n vs (n-1)"])
    plt.savefig(fn_plot_nrmsd)
    plt.close()

    # gdist (n vs N) error
    plt.plot(n_zaps[n_zaps_init:], gdist_n[n_zaps_init:], color="r")

    # gdist (n vs n-1) error
    plt.plot(n_zaps[n_zaps_init:], gdist[n_zaps_init:], color="b")

    # 1% error bar
    plt.plot(np.array([n_zaps[4], n_zaps[-1]]), np.array([1, 1]), "b--")

    plt.grid()
    plt.xlabel("n", fontsize=11)
    plt.ylabel("GDIST", fontsize=11)
    plt.title("Convergence analysis of online optimization", fontsize=11)
    plt.legend(["n vs N", "n vs (n-1)"])
    plt.savefig(fn_plot_gdist)
    plt.close()

    if verbose:
        print("DONE")


def get_fim_sample(fun, x, p):
    """
    Get Fisher Information Matrix of one single sample.

    Parameters
    ----------
    fun : function object
        Function object the fisher information matrix is calculated for. The sample is passed as the first argument.
    x : float
        Sample passed to function
    p : dict
        Dictionary containing the parameter estimates. The keys are the parameter names of fun.

    Returns
    -------
    fim_matrix : ndarray of float [n_params x n_params]
        Fisher information matrix
    """

    # read function arguments
    params = p.keys()

    # determine gradient of function w.r.t. parameters using forward approximation
    dfdp = np.zeros(len(params))

    for i, para in enumerate(params):
        # copy original params dict
        p_dp = dict()

        for pa in params:
            p_dp[pa] = p[pa]

        # perturb parameter
        dp = p[para] / 1000
        p_dp[para] = p[para] + dp

        # determine gradient with forward approximation
        dfdp[i] = (fun(x, **p_dp) - fun(x, **p)) / dp

    fim_matrix = np.outer(dfdp, dfdp)

    return fim_matrix


def get_det_fim(x, fun, p, fim_matrix):
    """
    Updates the Fisher Information Matrix and returns the negative determinant based on the sample x.
    It is a score how much information the additional sample yields.

    Parameters
    ----------
    fun : function object
        Function object defined in interval [0, 1].
    x : float
        Single sample location (interval [0, 1])
    p : dict
        Dictionary containing the parameter estimates. The keys are the parameter names of fun.
    fim_matrix : ndarray of float [n_params x n_params]
        Fisher Information Matrix

    Returns
    -------
    det : float
        Determinant of the Fisher Information Matrix after adding sample x
    """
    fim_matrix_sample = fim_matrix + get_fim_sample(fun=fun, x=x, p=p)
    sign, logdet = np.linalg.slogdet(fim_matrix_sample)

    return -sign*np.exp(logdet)


def init_fim_matrix(fun, x, p):
    """
    Initializes the Fisher Information Matrix based on the samples given in x.

    Parameters
    ----------
    fun : function object
        Function object defined in interval [0, 1].
    x : ndarray of float
        Initial sample locations (interval [0, 1])
    p : dict
        Dictionary containing the parameter estimates. The keys are the parameter names of fun.

    Returns
    -------
    fim_matrix : ndarray of float [n_params x n_params]
        Fisher Information Matrix
    """
    fim_matrix = np.zeros((len(p), len(p)))

    for i in range(len(x)):
        fim_matrix += get_fim_sample(fun=fun, x=x[i], p=p)

    return fim_matrix


def get_optimal_sample_fim(fun, p, x=None):
    """
    Determines optimal location of next sample by maximizing the determinant of the Fisher Information Matrix.

    Parameters
    ----------
    fun : function object
        Function object (interval [0, 1]).
    x : ndarray of float, optional, default: None
        Previous sample locations (interval [0, 1]).
    p : dict
        Dictionary containing the parameter estimates. The keys are the parameter names of fun.

    Returns
    -------
    x_opt : float
        Optimal location of next sample (interval [0, 1]).
    """
    # initialize fim matrix with initial samples
    if x is None:
        fim_matrix = np.zeros((len(p), len(p)))
    else:
        fim_matrix = init_fim_matrix(fun=fun, x=x, p=p)

    # run optimization
    # res = minimize(fun=get_det_fim,
    #                method="trust-constr",
    #                bounds=((0, 1),),
    #                x0=np.array([0.5]),
    #                args=(fun, p, fim_matrix),
    #                options={"finite_diff_rel_step": 0.05, "xtol": 0.01})

    # res = minimize(fun=get_det_fim,
    #                 method="SLSQP",
    #                 x0=np.array([0.5]),
    #                 bounds=((0, 1),),
    #                 args=(fun, p, fim_matrix),
    #                 options={'disp': None, "eps": 0.001, "ftol": 1e-12}) #,
    # return res.x[0]

    x_bf = np.linspace(0, 1, 200)
    det = np.zeros(len(x_bf))
    for i in range(len(x_bf)):
        det[i] = get_det_fim(x=x_bf[i], fun=fun, p=p, fim_matrix=fim_matrix)

    x_opt = x_bf[np.argmin(det)]

    return x_opt
