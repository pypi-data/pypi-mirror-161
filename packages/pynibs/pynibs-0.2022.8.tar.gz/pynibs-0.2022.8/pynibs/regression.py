import os
import time
import h5py
import inspect
import warnings
import multiprocessing
import pandas as pd
import numpy as np
import scipy.stats
from lmfit import Model
from scipy.linalg import svd
from functools import partial
from scipy.stats import linregress
from collections import OrderedDict
from numpy.linalg import lstsq, pinv
from sklearn.linear_model import LinearRegression
import pynibs


class Element(object):
    """ Fit Element object class """

    def __init__(self, x, y, ele_id, fun=pynibs.sigmoid4, score_type="R2", select_signed_data=False, constants=None):
        """ Initializes Fit Element instance """
        self.x = x
        self.y = y
        self.y_passed = self.y
        self.fun = fun
        self.ele_id = ele_id
        self.init_vals = dict()
        self.random_vals_init_range = dict()
        self.limits = dict()
        self.status = True
        self.log_scale = False
        self.select_signed_data = select_signed_data
        self.score_type = score_type
        self.score = None
        self.best_values = None
        self.r2_lin = None
        self.gmodel = None
        self.fit = None
        self.residual = None
        self.var_y = np.var(self.y)
        self.var_y_passed = self.var_y

        self.norm_y = np.linalg.norm(self.y)
        self.param_names = None

        if constants is None:
            self.constants = {}

        # select whether the fit is performed for positive or negative data by running an initial linear fit
        # select the data, which yields a fit with a lower p-value; removes unused x and y data
        if self.select_signed_data:
            if not ((self.x < 0).all() or (self.x > 0).all()):
                self.run_select_signed_data()

        # set initial values of
        self.setup_model()

    def set_init_vals(self, value):
        """ Sets initial values in self.init_vals and gmodel instance """
        for key in value.keys():
            self.init_vals[key] = value[key]
            self.gmodel.param_hints[key]['value'] = value[key]

        self.gmodel.make_params()

    def set_limits(self, value):
        """ Sets limits in self.limits and gmodel instance """
        for key in value.keys():
            self.limits[key] = value[key]
            self.gmodel.param_hints[key]['min'], self.gmodel.param_hints[key]['max'] = value[key]

        self.gmodel.make_params()

    def set_constants(self, value):
        """ Sets constants in self.constants and gmodel instance """
        for key in value.keys():
            self.constants[key] = value[key]
            self.gmodel.param_hints[key]['value'] = value[key]
            self.gmodel.param_hints[key]['vary'] = False

        self.gmodel.make_params()

    def setup_model(self):
        """ Setup model parameters (limits, initial values, etc. ...) """
        x_min = np.min(self.x)
        x_max = np.max(self.x)
        y_min = np.min(self.y)
        y_max = np.max(self.y)

        # set up gmodel
        self.gmodel = Model(self.fun)
        self.param_names = self.gmodel.param_names

        # create the param_hints OrderedDict
        for p in self.gmodel.param_names:
            self.gmodel.param_hints[p] = OrderedDict()

        if self.fun == pynibs.linear:
            # linear function starts with generic and same values for each element
            self.set_limits({"m": [-100, 100], "n": [-100, 100]})
            self.set_init_vals({"m": 0.3, "n": -1})
            self.random_vals_init_range = {"m": [0, 100], "n": [0, .3]}

        elif self.fun == pynibs.exp0:
            self.set_limits({"x0": [0, 1000], "r": [1e-12, 100]})
            self.set_init_vals({"x0": 10, "r": .1})
            self.random_vals_init_range = {"x0": [0, 10], "r": [0, .2]}

        elif self.fun in [pynibs.sigmoid, pynibs.sigmoid_log, pynibs.sigmoid4, pynibs.sigmoid4_log]:

            if self.fun == pynibs.sigmoid_log or self.fun == pynibs.sigmoid4_log:
                self.log_scale = True
                self.y_passed = np.log10(self.y)
                self.var_y_passed = np.var(self.y_passed)

            if self.fun == pynibs.sigmoid4_log and y_min <= 0:
                y0 = 1e-3
            elif (self.fun == pynibs.sigmoid4_log and y_min > 0) or self.fun == pynibs.sigmoid4:
                y0 = y_min
            else:
                y0 = 0

            if (self.x < 0).all():
                y1 = y_max
                y2 = y_min
                x1 = x_max
                x2 = x_min
            else:
                y1 = y_min
                y2 = y_max
                x1 = x_min
                x2 = x_max

            # set initial amp to maximum of y-data
            amp = y_max

            # set initial x_0 to 3/4 of x-data range
            x0 = x1 + 3 / 4 * (x2 - x1)

            # set initial r slope to slope of tangent over middle of 25% e-range
            r = 16 / (x_max - x_min) * (y2 - y1) / (amp - y0)

            factor = 100
            self.set_init_vals({"x0": x0,
                                "amp": amp,
                                "r": r})
            self.random_vals_init_range = {"x0": [np.min((0, 3 * x0)), np.max((0, 3 * x0))],
                                           "amp": [np.min((0, 3 * amp)), np.max((0, 3 * amp))],
                                           "r": [np.min((0, 3 * r)), np.max((0, 3 * r))]}
            self.set_limits({"x0": [np.min((0, self.init_vals["x0"] * factor)),
                                    np.max((0, self.init_vals["x0"] * factor))],
                             "amp": [np.min((1e-12, self.init_vals["amp"] * factor)),
                                     np.max((1e-12, self.init_vals["amp"] * factor))],
                             "r": [np.min((1e-12, self.init_vals["r"] * factor)),
                                   np.max((1e-12, self.init_vals["r"] * factor))]})

            if self.fun == pynibs.sigmoid4:
                self.set_init_vals({"y0": y0})
                self.random_vals_init_range["y0"] = [1e-12, y0 * 3]
                self.set_limits({"y0": [1e-12, y_max]})
            elif self.fun == pynibs.sigmoid4_log:
                self.set_init_vals({"y0": y0})
                self.random_vals_init_range["y0"] = [1e-12, y0 * 3]
                self.set_limits({"y0": [1e-12, y_max]})

        elif self.fun == pynibs.dummy_fun:
            self.set_limits({"a": [0, 1]})
            self.set_init_vals({"a": 1})
            self.random_vals_init_range["a"] = [0, 1]
        else:
            raise NotImplementedError(self.fun)

    def set_random_init_vals(self):
        """ Set random initial values """
        init_vals_new = dict()

        for p in self.init_vals.keys():
            init_vals_new[p] = np.random.rand() * \
                               (self.random_vals_init_range[p][1] - self.random_vals_init_range[p][0]) \
                               - self.random_vals_init_range[p][0]

        self.set_init_vals(init_vals_new)

    def run_select_signed_data(self):
        """ Selects positive or negative data by performing an initial linear fit by comparing the resulting p-values,
        slopes and R2 values. Either positive or negative data (w.r.t. x-axis) yielding a fit with a p-value < 0.05,
        a positive slope and the higher R2 value is used and the remaining data with the other sign is omitted
        from the analysis """
        mask_pos = self.x > 0
        mask_neg = np.logical_not(mask_pos)

        # fit positive data (perform the regression when we have at least 20 data points to stabilize results)
        if np.sum(mask_pos) > 20:
            s_pos = scipy.stats.linregress(x=self.x[mask_pos], y=self.y[mask_pos])
            p_pos = s_pos.pvalue
            b_pos = s_pos.slope
            residual = s_pos.slope * self.x[mask_pos] + s_pos.intercept - self.y[mask_pos]
            r2_pos = 1 - np.var(residual) / np.var(self.y[mask_pos])
        else:
            p_pos = 1
            r2_pos = np.NaN
            b_pos = -1

        # fit negative data (perform the regression when we have at least 20 data points to stabilize results)
        if np.sum(mask_neg) > 20:
            s_neg = scipy.stats.linregress(x=self.x[mask_neg], y=self.y[mask_neg])
            p_neg = s_neg.pvalue
            b_neg = s_neg.slope
            residual = s_neg.slope * self.x[mask_neg] + s_neg.intercept - self.y[mask_neg]
            r2_neg = 1 - np.var(residual) / np.var(self.y[mask_neg])
        else:
            p_neg = 1
            r2_neg = np.NaN
            b_neg = 1

        # only use data with p < 0.001 and when slopes show an increase of y-data with increasing |x|-data otherwise,
        # set status to False to indicate that the fit is omitted and set score to NaN
        pos_valid = False
        neg_valid = False

        if (b_pos > 0) and (p_pos < 0.001):
            pos_valid = True
        if (b_neg < 0) and (p_neg < 0.001):
            neg_valid = True

        if pos_valid and not neg_valid:
            self.x = self.x[mask_pos]
            self.y = self.y[mask_pos]
            self.r2_lin = r2_pos
        elif neg_valid and not pos_valid:
            self.x = self.x[mask_neg]
            self.y = self.y[mask_neg]
            self.r2_lin = r2_neg
        elif pos_valid and neg_valid:
            if r2_pos > r2_neg:
                self.x = self.x[mask_pos]
                self.y = self.y[mask_pos]
                self.r2_lin = r2_pos
            else:
                self.x = self.x[mask_neg]
                self.y = self.y[mask_neg]
                self.r2_lin = r2_neg
        else:
            self.status = False
            self.score = np.NaN

        self.var_y = np.var(self.y)
        self.norm_y = np.linalg.norm(self.y)

        if self.log_scale:
            self.y_passed = np.log10(self.y)
        else:
            self.y_passed = self.y

    def run_fit(self, max_nfev=1000):
        """ Perform data fit """

        fit = self.gmodel.fit(self.y_passed, x=self.x,
                              calc_covar=False, method="leastsq", max_nfev=max_nfev, scale_covar=False)
        self.best_values = fit.best_values
        self.residual = fit.residual

        self.calc_score()

    def calc_score(self):
        """ Determine goodness-of-fit score """
        # R2
        if self.score_type == "R2":
            self.score = 1 - np.var(self.residual) / self.var_y_passed

        # Relative standard error of regression
        elif self.score_type == "SR":
            self.score = 1 - np.linalg.norm(self.residual) / self.norm_y

        else:
            raise NotImplementedError(f"{self.score_type} not implemented ... ")


def workhorse_element_run_fit(element, max_nfev=10):
    """ Workhorse to run single Element fit. If status is False, the element will not be fitted. """
    if element.status:
        element.run_fit(max_nfev=max_nfev * len(element.x))

    return element


def workhorse_element_init(ele_id, e_matrix, mep, fun, score_type, select_signed_data, constants):
    """ Workhorse to initialize Elements. """
    element = Element(x=e_matrix[:, ele_id],
                      y=mep,
                      ele_id=ele_id,
                      fun=fun,
                      score_type=score_type,
                      select_signed_data=select_signed_data,
                      constants=constants)
    return element


def regress_data(e_matrix, mep, elm_idx_list=None, element_list=None, fun=pynibs.sigmoid4, n_cpu=4, con=None,
                 n_refit=50, zap_idx=None, return_fits=False, score_type="R2",
                 verbose=False, pool=None, refit_discontinuities=True, select_signed_data=False):
    """
    Mass-univariate nonlinear regressions on raw MEP_{AMP} ~ E.
    That is, for each element in elm_idx_list, it's E (mag | norm | tan) for each zap regressed on the raw MEP
    amplitude. An element wise r2 score is returned.
    The function reads the precomputed array of E-MEP data from an .hdf5 file.

    Parameters
    ----------
    e_matrix : np.ndarray of float
         (n_zaps, n_ele) Electric field matrix
    mep : ndarray of float
        (n_zaps,) Motor evoked potential for each stimulation
    elm_idx_list : np.ndarray of int or list of int
        (n_zaps,) List containing the element indices the fit is performed for
    element_list : list of Element object instances, optional
        [n_ele] Already initialized pynibs.Element objects. Initialization will be skipped if not provided.
    fun : pynibs.exp.Mep
        A function of pynibs.exp.Mep (exp0, sigmoid, sigmoid4, ...)
    n_cpu : int
        Number of threads, if n_cpu=1 no parallel pool will be opened and all calculations are done in serial
    con : np.ndarray of float, optional
        (n_roi, 3 or 4) Connectivity matrix of ROI. Needed in case of refit for discontinuity checks
    n_refit : int, default: 50
        Maximum number of refits of zero elements. No refit is applied in case of n_refit = 0.
    zap_idx : np.ndarray of int or list of int, optional
        Which e/mep pairs to use.
    return_fits : bool, optional
        Return fit objects containing the parameter estimates
    score_type : str, default: "R2"
        Error measure of fit:
        - "R2": R2 score (Model variance / Total variance); linear fits: [0, 1], 1 ... perfect fit
        - "SR": Relative standard error of regression (1 - Error 2-norm / Data 2-norm); [-Inf, 1], 1 ... perfect fit
    verbose : bool, default: False
        Plot output messages
    pool : multiprocessing.Pool()
        pool instance to use
    refit_discontinuities : bool, default: True
        Refit discontinuous elements. If True, provide _con_

    Returns
    -------
    score : np.ndarray of float (n_roi, n_qoi)
        Score for each element
    best_values : list of dict (n_ele)
        List of parameter fits
    """
    if zap_idx is None:
        zap_idx = np.array(range(e_matrix.shape[0]))
    if isinstance(zap_idx, list):
        zap_idx = np.array(zap_idx)

    refit_thr = 1e-6
    constants = None

    if elm_idx_list is None:
        elm_idx_list = np.arange(e_matrix.shape[1])

    if fun == pynibs.dummy_fun:
        c_all = np.random.random(len(elm_idx_list))

        if return_fits:
            best_values = [{"a": 1} for _ in range(len(elm_idx_list))]
            return c_all, best_values
        else:
            return c_all

    # shuffle elements because some of them need longer to compute
    # (in this way it is distributed more equally over all cores)
    np.random.shuffle(elm_idx_list)
    # if not isinstance(elm_idx_list, np.ndarray):
    #     elm_idx_list = np.array(elm_idx_list)
    # elm_idx_list_shuffle_idx = np.argsort(elm_idx_list).astype(int)
    # elm_idx_list = elm_idx_list.tolist()

    # Setting up parallelization
    ####################################################################
    if n_cpu > 1:
        if not pool:
            n_cpu_available = multiprocessing.cpu_count()
            n_cpu = min(n_cpu, n_cpu_available, len(elm_idx_list))
            pool = multiprocessing.Pool(n_cpu)
            local_pool = True

            if verbose:
                print(" > Setting up multiprocessing using {}/{} cores".format(n_cpu, n_cpu_available))
        else:
            local_pool = False  # close pool only if created locally
            if verbose:
                print(" > Using provided pool object")

        # defining workhorses
        workhorse_partial = partial(workhorse_element_run_fit,
                                    max_nfev=10)

        workhorse_init_partial = partial(workhorse_element_init,
                                         e_matrix=e_matrix[zap_idx],
                                         mep=mep[zap_idx],
                                         fun=fun,
                                         score_type=score_type,
                                         select_signed_data=select_signed_data,
                                         constants=constants)
    else:
        local_pool = False
        if verbose:
            print(" > Running computations with n_cpu=1.")

    # initialize elements
    ####################################################################
    if element_list is None:
        start = time.time()
        if n_cpu <= 1:
            element_list = [Element(x=e_matrix[zap_idx, ele_id],
                                    y=mep[zap_idx],
                                    ele_id=ele_id,
                                    fun=fun,
                                    score_type=score_type,
                                    select_signed_data=select_signed_data,
                                    constants=constants) for ele_id in elm_idx_list]
        else:
            element_list = pool.map(workhorse_init_partial, elm_idx_list)
        stop = time.time()
        if verbose:
            print(f"Initialized {len(elm_idx_list)} elements: {stop - start:2.2f} s")

    # run fit
    ####################################################################
    start = time.time()

    if n_cpu <= 1:
        for ele in element_list:
            ele.run_fit(max_nfev=10 * len(ele.x))
    else:
        element_list = pool.map(workhorse_partial, element_list)

    stop = time.time()

    if verbose:
        print(f"Determined scores: {stop - start:2.2f} s")

    if fun == pynibs.linear:
        n_refit = 0
        refit_discontinuities = False
        print("Skipping refit for linear fits ...")

    # refit elements
    ####################################################################
    if n_refit > 0:

        # refit bad elements
        ####################################################################
        i_refit = 0
        while i_refit < n_refit:

            # get index in Element_list of elements where refit should be performed
            ele_idx_refit = [i_ele for i_ele, ele in enumerate(element_list) if ele.score < refit_thr]
            element_list_refit = [element_list[i_ele] for i_ele in ele_idx_refit]

            if len(element_list_refit) > 0:

                if verbose:
                    print(f" > Performing refit for {len(element_list_refit)} zero elements ...")

                # set random start values
                for ele in element_list_refit:
                    ele.set_random_init_vals()

                start = time.time()

                if n_cpu == 1:
                    for ele in element_list_refit:
                        ele.run_fit(max_nfev=10 * len(ele.x))
                else:
                    element_list_refit = pool.map(workhorse_partial, element_list_refit)

                stop = time.time()

                if verbose:
                    print(f"Determined scores: {stop - start:2.2f} s")

                # replace new fits if they have higher scores than the old ones
                for i_ele, ele_idx_re in enumerate(ele_idx_refit):
                    if element_list_refit[i_ele].score > element_list[ele_idx_re].score:
                        element_list[ele_idx_re] = element_list_refit[i_ele]

                i_refit += 1
            else:
                break

    # sort elements for discontinuity check
    element_list = [ele for _, ele in sorted(zip(elm_idx_list, element_list))]

    # find discontinuities and refit
    ##################################################################
    if refit_discontinuities:

        if len(element_list) > 1:
            score = np.array([ele.score for ele in element_list])
            not_fitted_elms = np.array([idx for idx, ele in enumerate(element_list) if np.isnan(ele.score)])
            idx_disc, idx_neighbor = pynibs.get_indices_discontinuous_data(data=score,
                                                                           con=con,
                                                                           neighbor=True,
                                                                           deviation_factor=2,
                                                                           not_fitted_elms=not_fitted_elms)
            element_list_disc = [element_list[i_ele] for i_ele in idx_disc]

            if len(idx_disc) > 0:
                if verbose:
                    print(f" > Performing refit for {len(idx_disc)} discontinuous elements ...")

                # refit for discontinuous elements
                if len(idx_disc) > 0:
                    # set start values from neighbors
                    for i_ele, idx_ne in zip(range(len(idx_disc)), idx_neighbor):
                        element_list_disc[i_ele].set_init_vals(element_list[idx_ne].best_values)

                    start = time.time()

                    if n_cpu == 1:
                        for ele in element_list_disc:
                            ele.run_fit(max_nfev=10 * len(ele.x))
                    else:
                        element_list_disc = pool.map(workhorse_partial, element_list_disc)

                    stop = time.time()

                    if verbose:
                        print(f"Determined scores: {stop - start:2.2f} s")

                    # replace new fits if they have higher scores than the old ones
                    for i_ele, ele_idx_re in enumerate(idx_disc):
                        if element_list_disc[i_ele].score > element_list[ele_idx_re].score:
                            element_list[ele_idx_re] = element_list_disc[i_ele]

    score = np.array([ele.score for ele in element_list])

    if local_pool:
        pool.close()
        pool.join()

    if return_fits:
        best_values = np.array([ele.best_values for ele in element_list])
        return score, best_values
    else:
        return score


def sing_elm_raw(elm_idx_list, mep_lst, mep_params, e, alpha=1000):
    """
    Mass-univariate ridge regressions on raw MEP_{AMP} ~ E.
    That is, for each element in elm_idx_list, it's E (mag | norm | tan) for each zap regressed on the raw MEP
    amplitude. An element wise sklearn.metrics.regression.r2_score is returned.


    elm_idx_list: nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep: list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params: nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        (e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...])
    e: nparray of float with e.shape == (n_elm, n_cond, n_qoi)
            array of the electric field to compute the r2 factor for, e.g. (e_mag, e_norm, e_tan)

    Returns
    -------
    r2: nparray of float [n_roi, n_datasets]
        R^2 for each element in elm_idx_list
    """
    from pandarallel import pandarallel
    pandarallel.initialize(verbose=0)

    def cartesian_product(*arrays):
        """
        Fast implementation to get cartesian product of two arrays.

        cartesian_product([a,b,c],[2,3]) =
             [a, 2
              a, 3
              b, 2
              b, 3
              c, 2
              c, 3]
        """
        la = len(arrays)
        dtype = np.result_type(*arrays)
        arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
        for i, a in enumerate(np.ix_(*arrays)):
            arr[..., i] = a
        return arr.reshape(-1, la)

    n_eqoi = e.shape[2]
    n_cond = e.shape[1]
    n_elm = e.shape[0]
    assert n_cond == len(mep_lst)
    scores = None
    reg_r2 = np.empty((n_elm, n_eqoi))

    for qoi_idx in range(n_eqoi):
        # t_q = time.time()
        x = pd.DataFrame()
        index_shift = 0
        amplitudes = np.array(())

        start = time.time()
        for mep_i, mep in enumerate(mep_lst):
            # condition wise, as we stimulated with different intensities per conditions

            # for each element in roi, one datapoint for each zap.
            current = cartesian_product(e[:, mep_i, qoi_idx], mep.intensities)

            # index is iteration of zaps over all conditions
            index = cartesian_product(e[:, mep_i, qoi_idx], np.arange(len(mep.intensities)))[:, 1]
            index += index_shift
            index_shift = index[-1] + 1

            # el is range(n_elements) * n_zaps_in_condition
            el_idx = np.repeat(np.arange(e.shape[0]), len(mep.intensities))

            # intensity * e
            e_zap = np.multiply(current[:, 0], current[:, 1])

            # put all together
            x_cond = pd.DataFrame(data={"index": index.astype(int),
                                        "el": el_idx,
                                        "e": e_zap})
            amplitudes = np.append(amplitudes, mep.mep)
            # "current": current[:, 1],
            # "mep": mep[:,1]})

            # x_cond['condition'] = mep_i
            x = x.append(x_cond)

        stop = time.time()
        print(f"Prepare dataset t = {stop - start}")
        # x.shape is now (n_zaps*n_elms, 3)

        # reshape to (n_zaps, n_elms)
        start = time.time()
        x = x.pivot(index="index", columns="el", values="e")
        stop = time.time()
        print(f"Pivot t = {stop - start}")

        do_reg_poly = False
        do_reg_linear = True
        reg = LinearRegression()

        if do_reg_poly:
            # fn = "/data/pt_01756/tmp/reg/mean_data_roi_lasso.hdf5"
            # print "creating polynomial features"
            # poly = PolynomialFeatures(2, interaction_only=True, include_bias=False)
            # x_pol = poly.fit_transform(x.iloc[:,:-3])
            # print "fitting regressor"
            # reg.fit(x_pol, x['mep'])
            # with h5py.File(fn, 'a') as f:
            #     f.create_dataset(name='/data/tris/' + e,
            #                      data=reg.coef_[:E.shape[0]])
            #     e_poly = []
            #     # get interaction mapped back to elemens
            #     for el in range(E.shape[0]):
            #         print "getting indices for interactions"
            #         idx = [i for i, s in enumerate(poly.get_feature_names()) if 'x{} '.format(el + 1) in s]
            #         e_poly.append(np.sum(reg.coef_[idx]))
            #     f.create_dataset(name='/data/tris/' + e + '_poly',
            #                      data=e_poly)
            # data_qoi_tmp = e_poly
            raise NotImplementedError

        elif do_reg_linear:
            # Do one regression per element.
            # r_t = time.time()

            def get_score(x_i):
                """Helper function do be used by pd.apply() to speed up things.

                Params:
                -------
                x_i: pd.Series
                 Column with e for a single elm.

                Returns:
                --------
                r2 for amplitudes ~ E
                """
                # x_i = x_i.reshape(-1, 1)
                reg.fit(x_i.reshape(-1, 1), amplitudes)
                return reg.score(x_i.reshape(-1, 1), amplitudes)

            # apply get_score function column wise
            start = time.time()
            # scores = x.parallel_apply(get_score, axis=0, raw=True)
            scores = x.transpose().swifter.apply(get_score, axis=1, raw=True)
            stop = time.time()
            print(f"Fit and score t = {stop - start}")
            # print "all_reg: {}".format(time.time() - r_t)

        reg_r2[:, qoi_idx] = np.array(scores)
        # data.append(data_qoi_tmp)

        # print "qoi {}: {}".format(qoi_idx, time.time() - t_q)

    return reg_r2


def write_regression_hdf5(fn_exp_hdf5, fn_reg_hdf5, qoi_path_hdf5, qoi_phys, e_results_folder, qoi_e, roi_idx,
                          conds_exclude):
    """
    Reads the stimulation intensities from the experiment.hdf5 file.
    Reads the qoi from the experiment.hdf5 file.
    Reads the electric fields from the electric field folder.
    Weights the electric field voxel wise with the respective intensities
    and writes an .hdf5 file containing the preprocessed data (pandas dataframe).

    fn_exp_hdf5: str
        Filename of the experiment.hdf5 file
    fn_reg_hdf5: str
        Filename of output regression.hdf5 file
    qoi_path_hdf5: str
        Path in experiment.hdf5 file pointing to the pandas dataframe containing the qoi
        (e.g.: "phys_data/postproc/EMG")
    qoi: str
        Name of QOI the congruence factor is calculated with
        (e.g.: "p2p")
    fn_e_results: str
        Folder containing the electric fields
        (e.g.: "/data/pt_01756/probands/13061.30/results/electric_field/1")
    qoi_e: str or list of str
        Quantities of the electric field used to calculate the congruence factor (e.g. ["E", "E_norm", "E_tan"]
        Has to be included in e.hdf5 -> e.g.: "data/midlayer/roi_surface/1/E"
    roi_idx: int
        ROI index
    conds_exclude: str or list of str
        Conditions to exclude

    Returns
    -------
    <File>: .hdf5 file
        File containing the intensity (current) scaled E-fields of the conditions in the ROI.
        Saved in datasets with the same name as qoi_e ["E", "E_norm", "E_tan"]
    """

    def cartesian_product(*arrays):
        """
        Fast implementation to get cartesian product of two arrays.

        cartesian_product([a,b,c],[2,3]) =
             [a, 2
              a, 3
              b, 2
              b, 3
              c, 2
              c, 3]
        """
        la = len(arrays)
        dtype = np.result_type(*arrays)
        arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
        for i, a in enumerate(np.ix_(*arrays)):
            arr[..., i] = a
        return arr.reshape(-1, la)

    if conds_exclude is not list:
        conds_exclude = [conds_exclude]

    if type(qoi_e) is not list:
        qoi_e = [qoi_e]

    # read dataframe of stimulation data
    df_stim_data = pd.read_hdf(fn_exp_hdf5, "stim_data")  # type: pd.DataFrame
    conds = np.unique(df_stim_data["condition"])
    conds = [c for c in conds if c not in conds_exclude]

    # read dataframe of postproc containing the qoi
    df_qoi = pd.read_hdf(fn_exp_hdf5, qoi_path_hdf5)  # type: pd.DataFrame

    n_conds = len(conds)
    n_qoi_e = len(qoi_e)
    n_ele = 0

    # read electric fields
    for i_c, c in enumerate(conds):

        # read electric field
        fn_e_hdf5 = os.path.join(e_results_folder, c, 'simulations', 'e.hdf5')
        print(" > Loading electric field from file: {}".format(fn_e_hdf5))
        f = h5py.File(fn_e_hdf5, 'r')

        # generate E array in first iteration
        if i_c == 0:
            n_ele = f[f"data/midlayer/roi_surface/{roi_idx}/{qoi_e[0]}"][:].shape[0]

            # np.array [n_ele x n_zaps x n_qoi]
            e = np.zeros((n_ele, n_conds, n_qoi_e))

        # midlayer E
        for i_q_e, q_e in enumerate(qoi_e):
            e[:, i_c, i_q_e] = f[f"data/midlayer/roi_surface/{roi_idx}/{q_e}"][:]

    print("\n")

    # scale electric fields with respective intensities
    for i_q_e, q_e in enumerate(qoi_e):
        print(f"Preparing regression datasets for {q_e}")
        print(f"========================================")
        x = pd.DataFrame()
        index_shift = 0
        qoi_amplitudes = np.array(())

        start = time.time()
        for i_c, c in enumerate(conds):
            # extract stimulation intensity and qoi amplitude for condition
            mask = df_stim_data["condition"].values == c
            stim_intensity = df_stim_data.loc[mask, "current"].values

            # for each element in roi, one datapoint for each zap.
            e_stim_intensity = cartesian_product(e[:, i_c, i_q_e], stim_intensity)

            # intensity * e
            e_scaled = np.multiply(e_stim_intensity[:, 0], e_stim_intensity[:, 1])

            # index is iteration of zaps over all conditions
            index = cartesian_product(e[:, i_c, i_q_e], np.arange(len(stim_intensity)))[:, 1]
            index += index_shift
            index_shift = index[-1] + 1

            # el is range(n_elements) * n_zaps_in_condition
            el_idx = np.repeat(np.arange(n_ele), len(stim_intensity))

            # put all together
            x_cond = pd.DataFrame(data={"index": index.astype(int),
                                        "el": el_idx,
                                        "e": e_scaled})

            qoi_amplitudes = np.append(qoi_amplitudes, df_qoi.loc[mask, qoi_phys].values)

            x = x.append(x_cond)

        stop = time.time()
        print(f"Prepare dataset: t = {stop - start}")
        # x.shape is now (n_zaps*n_elms, 3)

        # reshape to (n_zaps, n_elms)
        start = time.time()
        x = x.pivot(index="index", columns="el", values="e")
        x["qoi_amplitudes"] = qoi_amplitudes
        stop = time.time()
        print(f"Pivot: t = {stop - start}")

        start = time.time()
        x.to_hdf(fn_reg_hdf5, q_e)
        stop = time.time()
        print(f"Write hdf5: t = {stop - start}")
        print(f"\n")


def ridge_from_hdf5(elm_idx_list, fn_reg_hdf5, qoi_path_hdf5, zap_idx=None):
    """
    Mass-univariate ridge regressions on raw MEP_{AMP} ~ E.
    That is, for each element in elm_idx_list, it's E (mag | norm | tan) for each zap regressed on the raw MEP
    amplitude. An element wise sklearn.metrics.regression.r2_score is returned.
    The function reads the precomputed array of E-MEP data from an .hdf5 file.
    Always uses all cores of a machine!

    elm_idx_list : list of int
        List containing the element indices the fit is performed for
    fn_hdf5 : str
        Filename (incl. path) containing the precomputed E-MEP dataframes
    qoi_path_hdf5 : str
        Path in .hdf5 file to dataset of electric field qoi
    zap_idx : np.ndarray [n_zaps], optional, default: None
        Indices of zaps the congruence factor is calculated with (default: all)

    Returns
    -------
    r2 : nparray of float [n_roi, n_datasets]
        R^2 for each element in elm_idx_list
    """

    x = pd.read_hdf(fn_reg_hdf5, qoi_path_hdf5)  # type: pd.DataFrame

    # use all stimuli if zap_idx is not provided
    if zap_idx is None:
        zap_idx = np.arange(x.shape[0])

    n_zaps = x.shape[0]
    mask = np.zeros(n_zaps).astype(bool)
    mask[zap_idx] = True
    qoi_amplitudes = x.loc[mask, "qoi_amplitudes"].values
    x = x.drop("qoi_amplitudes", axis=1)

    def get_score(x_i):
        """Helper function do be used by pd.apply() to speed up things.

        Params:
        -------
        x_i: pd.Series
         Column with e for a single elm.

        Returns:
        --------
        r2 for amplitudes ~ E
        """

        reg.fit(x_i.reshape(-1, 1), qoi_amplitudes)
        return reg.score(x_i.reshape(-1, 1), qoi_amplitudes)

    reg = LinearRegression()

    # apply get_score function column (element) wise
    # start = time.time()
    r2 = x.loc[mask, elm_idx_list].apply(get_score, axis=0, raw=True)
    # stop = time.time()
    # print(f"Fit and score t = {stop - start}")

    return np.array(r2)[:, np.newaxis]


def fit_elms(elm_idx_list, e_matrix, mep, zap_idx=None,
             fun=pynibs.sigmoid4, init_vals=None, limits=None, log_scale=False,
             constants=None, max_nfev=None, bad_elm_idx=None, score_type="R2",  # mask_e_field=None,
             verbose=False):
    """
    Workhorse for Mass-univariate nonlinear regressions on raw MEP_{AMP} ~ E.
    That is, for each element in elm_idx_list, it's E (mag | norm | tan) for each zap regressed on the raw MEP
    amplitude. An element wise r2 score is returned.

    Parameters
    ----------
    elm_idx_list : list of int or ndarray
        List containing the element indices the fit is performed for
    e_matrix : ndarray of float [n_zaps x n_ele]
        Electric field matrix
    mep : ndarray of float [n_zaps]
        Motor evoked potentials for every stimulation
    zap_idx : np.ndarray [n_zaps], optional, default: None
        Indices of zaps the congruence factor is calculated with (default: all)
    fun : str
        A function name of pynibs.exp.Mep (exp0, sigmoid)
    init_vals : np.ndarray of dict
        Dictionary containing the initial values for each element as ndarray [len(elm_idx_list)].
        The keys are the free parameters of fun, e.g. "x0", "amp", etc
    limits : pd.DataFrame
        Dictionary containing the limits of each parameter for each element e.g.: limits["x0"][elm_idx] = [min, max]
    log_scale : bool, optional, default: False
        Log-transform data before fit (necessary for functions defined in the log domain)
    constants : dict of <string>:<num>, optional, default: None
        key:value pair of model parameters not to optimize.
    max_nfev : int, default: None
        Max fits, passed to model.fit() as max_nfev=max_nfev*len(x).
    bad_elm_idx : ndarray
        Indices of elements not to fit, with indices corresponding to indices (not values) of elm_idx_list
    score_type : str, optional, default: "R2"
        Goodness of fit measure; Choose SR for nonlinear fits and R2 or SR for linear fits:
        - "R2": R2 score (Model variance / Total variance) [0, 1] for linear models; 0: bad fit; 1: perfect fit
        - "SR": Relative standard error of regression (1 - Error 2-norm / Data 2-norm) [-inf, 1]; 1: perfect fit
    mask_e_field : ndarray of bool [n_zaps x n_ele], optional, default: None
        Mask indicating for which e-field (and mep) values the fit is performed for. Changes for normal component in
        each element because of the sign and p-values. If None, all data is used in each element.
    verbose : bool, optional, default: False
        Print verbosity information

    Returns
    -------
    r2 : ndarray of float [n_roi, 1]
        R2 for each element in elm_idx_list
    best_values : ndarray of object
        Fit parameters returned from the optimizer
    """
    str_pref = "Main"
    start = time.time()
    try:
        str_pref = f"{multiprocessing.current_process()._identity[0]:0>2} "
    except:
        pass

    # use all stimuli if zap_idx is not provided
    if zap_idx is not None:
        e_matrix = e_matrix[zap_idx, :]
        mep = mep.iloc[zap_idx]
    n_zaps = e_matrix.shape[0]

    if bad_elm_idx is None:
        bad_elm_idx = set(np.array([]))

    best_values = [0] * len(elm_idx_list)
    r2 = np.zeros((len(elm_idx_list),)) - 10

    if fun == pynibs.dummy_fun:
        return r2, np.array(best_values)

    if max_nfev is not None:
        max_nfev = n_zaps * max_nfev

    # set up gmodel
    gmodel = Model(fun)

    # create the param_hints ordereddict only once.
    for p in gmodel.param_names:
        gmodel.param_hints[p] = OrderedDict()

    param_hints = gmodel.param_hints
    make_params = gmodel.make_params
    param_names = gmodel.param_names

    if limits is not None:
        limits_p = list(limits.columns)
    else:
        limits_p = set()

    if init_vals is not None:
        inits_p = list(init_vals.columns)
        if constants is not None:
            inits_p = np.setdiff1d(inits_p, list(constants.keys()))
    else:
        inits_p = set()

    constants_elmwise = {}
    if constants is not None:
        for p in param_names:
            if p in constants:
                param_hints[p]['vary'] = False

                try:
                    len(constants[p])
                    constants_elmwise[p] = constants[p]
                except TypeError:
                    param_hints[p]['value'] = constants[p]

    # transform mep to log domain
    if log_scale:
        qoi = np.log10(mep)
    else:
        qoi = mep

    qoi_norm = np.linalg.norm(qoi)
    qoi_var = np.var(qoi)
    best_values = {k: [] for k in init_vals.keys()}
    # loop over elements
    for i, elm_idx in enumerate(elm_idx_list):
        if i in bad_elm_idx:
            [best_values[k].append(0) for k, v in best_values.items()]
            continue
        for p in limits_p:
            # set limits
            # skip the set_param_hin function and do this by hand
            param_hints[p]['min'], param_hints[p]['max'] = limits.iloc[i][p]

        for p in inits_p:
            # set initial values
            param_hints[p]['value'] = init_vals.iloc[i][p]

        for p in constants_elmwise:
            param_hints[p]['value'] = constants_elmwise[p][i]
        make_params()

        # perform fit (for some reason, sigmoid4_log function generates NaN, which I can not reproduce)
        # I catch the fitting error (ValueError) and set an r2 score of -1, such that it will go into the refit

        e_elm = e_matrix[:, elm_idx]
        # set max_nfev to a reasonable range
        fit = gmodel.fit(qoi, x=e_elm,
                         calc_covar=False, method="leastsq", max_nfev=max_nfev, scale_covar=False)
        [best_values[k].append(v) for k, v in fit.best_values.items()]

        # calculate goodness-of-fit score
        if score_type == "R2":
            # "R2"
            r2[i] = 1 - np.var(fit.residual) / qoi_var
        elif score_type == "SR":
            # Relative standard error of regression
            r2[i] = 1 - np.linalg.norm(fit.residual) / qoi_norm  # TODO: what is this??
            # np.sqrt(np.sum(fit.residual**2) / len(mep)) # <- this should be the correct S
            # print(f"Diff: "
            #       f"{np.round((1 - np.linalg.norm(fit.residual) / qoi_norm) -
            #       np.sqrt(np.sum(fit.residual**2) / len(mep)),2)}")
        elif score_type == 'BIC':
            r2[i] = -fit.bic
        elif score_type == 'AIC':
            r2[i] = fit.aic
        else:
            raise ValueError(f"Error score '{score_type}' not implemented ... ")
    if verbose:
        if len(elm_idx_list) == 0:
            elm_time = 0.0
        else:
            elm_time = (time.time() - start) / len(elm_idx_list)

        print(f"Proc{str_pref}:    > fit_elms workhorse: done "
              f"({time.time() - start:.2f} s, {elm_time:2.4} s/elm, "
              f"mean R2: {np.mean(r2):2.2f})")
    return r2, pd.DataFrame().from_dict(best_values)


# def nl_hdf5_workhorse_idx(elm_idx_list, e_matrix, mep,
#                           fun=sigmoid4, zap_idx=None, init_vals=None, limits=None, log_scale=False,
#                           constants=None, max_nfev=None,
#                           verbose=False):
#     """
#     Workhorse for Mass-univariate nonlinear regressions on raw MEP_{AMP} ~ E.
#     That is, for each element in elm_idx_list, it's E (mag | norm | tan) for each zap regressed on the raw MEP
#     amplitude. An element wise r2 score is returned.
#     The function reads the precomputed array of E-MEP data from an .hdf5 file.
#
#     Parameters
#     ----------
#     elm_idx_list : list of int
#         List containing the element indices the fit is performed for
#     e_matrix : ndarray of float [n_zaps x n_ele]
#         Electric field matrix
#     mep : ndarray of float [n_zaps]
#         Motor evoked potentials for every stimulation
#     zap_idx : np.array [n_zaps], optional, default: None
#         Indices of zaps the congruence factor is calculated with (default: all)
#     fun : str
#         A function name of pynibs.exp.Mep (exp0, sigmoid)
#     init_vals : dict
#         Dictionary containing the initial values for each element as ndarray [len(elm_idx_list)].
#         The keys are the free parameters of fun, e.g. "x0", "amp", etc
#     limits : dict
#         Dictionary containing the limits of each parameter for each element e.g.: limits["x0"][elm_idx] = [min, max]
#     log_scale : bool, optional, default: False
#         Log-transform data before fit (necessary for functions defined in the log domain)
#     constants : dict of <string>:<num>, optional, default: None
#         key:value pair of model parameters not to optimize.
#     bad_elm_idx : ndarray
#         Indices of elements not to fit.
#     max_nfev : int, default: None
#         Max fits, passed to model.fit() as max_nfev=max_nfev*len(x).
#     verbose : bool, optional, default: False
#         Print verbosity information
#
#     Returns
#     -------
#     r2 : ndarray of float [n_roi, 1]
#         R2 for each element in elm_idx_list
#     fit : fit objects
#         Fit objects returned from the optimizers
#     """
#     # from matplotlib import pyplot as plt
#     str_pref = "Main"
#     start = time.time()
#     try:
#         str_pref = f"{multiprocessing.current_process()._identity[0]:0>2} "
#     except:
#         pass
#
#     # use all stimuli if zap_idx is not provided
#     if zap_idx is not None:
#         zap_idx = np.arange(e_matrix.shape[0])
#         mask = np.zeros(e_matrix.shape[0]).astype(bool)
#         mask[zap_idx] = True
#         e_matrix = e_matrix[mask]
#         mep = mep[mask]
#     n_zaps = e_matrix.shape[0]
#
#     # if verbose:
#     #     print(f"Proc{str_pref}:    > regression_nl_hdf5_workhorse: "
#     #           f"starting ({e_matrix.shape[1]} elms / {n_zaps} zaps)")
#
#     best_values = [0] * e_matrix.shape[1]
#     r2 = np.zeros((e_matrix.shape[1],)) - 10
#
#     if fun == dummy_fun:
#         return r2, best_values
#
#     if max_nfev is not None:
#         max_nfev = n_zaps * max_nfev
#
#     if log_scale:
#         mep = np.log10(mep)
#
#     # set up gmodel
#     gmodel = Model(fun)
#
#     # create the param_hints ordereddict only once.
#     for p in gmodel.param_names:
#         gmodel.param_hints[p] = OrderedDict()
#
#     # compute variance only once
#     var_qoi = np.var(mep)
#
#     param_hints = gmodel.param_hints
#     make_params = gmodel.make_params
#     param_names = gmodel.param_names
#     if limits is not None:
#         limits_p = param_names
#     else:
#         limits_p = set()
#
#     if init_vals is not None :
#         inits_p = list(init_vals.keys())
#         if constants is not None:
#             inits_p = np.setdiff1d(inits_p, list(constants.keys()))
#     else:
#         inits_p = set()
#
#     if constants is not None:
#         for p in param_names:
#             if p in constants:
#                 param_hints[p]['value'] = constants[p]
#                 param_hints[p]['vary'] = False
#
#     #         # set_param_hint(p, value=constants[p], vary=False)
#     for i, elm in enumerate(elm_idx_list):
#         for p in limits_p:
#             # set limits
#             # skip the set_param_hint function and do this by hand
#             param_hints[p]['min'], param_hints[p]['max'] = limits[p][elm]
#
#         for p in inits_p:
#             # set initial values
#             param_hints[p]['value'] = init_vals[p][elm]
#             # set_param_hint(p, value=init_vals[p][elm_idx])
#
#         make_params()
#
#         # perform fit (for some reason, sigmoid4_log function generates NaN, which I can not reproduce)
#         # I catch the fitting error (ValueError) and set an r2 score of -1, such that it will go into the refit
#
#         try:
#             # set max_nfev to a reasonable range
#             fit = gmodel.fit(mep, x=e_matrix[:, i],
#                              calc_covar=False, method="leastsq", max_nfev=max_nfev, scale_covar=False)
#             best_values[i] = fit.best_values
#
#             # calculate R2 score
#             # times1.append(fit.nfev)
#             # mid2 = time.time()
#             if log_scale:
#                 # this could be optimized by pow(10)
#                 residual = 10 ** fit.best_fit - 10 ** qoi_amplitudes
#                 r2[i] = 1 - np.var(residual) / np.var(10 ** qoi_amplitudes)
#
#             else:
#                 r2[i] = 1 - np.var(fit.residual) / var_qoi
#
#         except ValueError:
#             print(f"value error: {i}: {elm}")
#             pass
#
#     if verbose:
#         print(f"Proc{str_pref}:    > regression_nl_hdf5_workhorse: done "
#               f"({time.time() - start:.2f} s, "
#               f"{(time.time() - start) / len(elm_idx_list):2.4} s/elm, "
#               f"mean R2: {np.mean(r2):2.2f})")
#     # f"Done at {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}, pid: {os.getpid()}")
#     return r2, np.array(best_values)


def nl_hdf5(elm_idx_list=None, fn_reg_hdf5=None, qoi_path_hdf5=None, e_matrix=None, mep=None, fun=pynibs.sigmoid4,
            zap_idx=None, n_cpu=4, con=None, n_refit=50, return_fits=False, score_type="R2", verbose=False, pool=None,
            refit_discontinuities=True):
    """
    Mass-univariate nonlinear regressions on raw MEP_{AMP} ~ E.
    That is, for each element in elm_idx_list, it's E (mag | norm | tan) for each zap regressed on the raw MEP
    amplitude. An element wise r2 score is returned.
    The function reads the precomputed array of E-MEP data from an .hdf5 file.

    Parameters
    ----------
    elm_idx_list : ndarray of int
        List containing the element indices the fit is performed for
    fn_reg_hdf5 : str
        Filename (incl. path) containing the precomputed E-MEP dataframes
    qoi_path_hdf5: Union[str, list[str]]
        Path in .hdf5 file to dataset of electric field qoi e.g.: ["E", "E_norm", "E_tan"]
    e_matrix : ndarray of float [n_zaps x n_ele]
        Electric field matrix
    mep : ndarray of float [n_zaps]
        Motor evoked potentials for every stimulation
    zap_idx : np.array [n_zaps], optional, default: None
        Indices of zaps the congruence factor is calculated with (default: all)
    fun : pynibs.exp.Mep function
        A function of pynibs.exp.Mep (exp0, sigmoid)
    n_cpu : int
        Number of threads
    con : ndarray of float [n_roi, 3 or 4], optional, default: None
        Connectivity matrix of ROI (needed in case of refit because of discontinuity check)
    n_refit : int, optional, default: 50
        Maximum number of refits of zero elements. No refit is applied in case of n_refit = 0.
    return_fits : bool, optional, default: False
        Return fit objects containing the parameter estimates
    score_type : str, optional, default: "R2"
        Error measure of fit:
        - "R2": R2 score (Model variance / Total variance); linear fits: [0, 1], 1 ... perfect fit
        - "SR": Relative standard error of regression (1 - Error 2-norm / Data 2-norm); [-Inf, 1], 1 ... perfect fit
    verbose : bool, optional, default: False
        Plot output messages
    pool : multiprocessing.Pool()
        pool instance to use.
    refit_discontinuities : bool, optional, default: True
        Run refit for discontinuous elements at the end

    Returns
    -------
    r2 : ndarray of float [n_roi, n_qoi]
        R2 for each element in elm_idx_list
    """
    refit_thr = 1e-6

    if elm_idx_list is None:
        elm_idx_list = np.arange(e_matrix.shape[1])

    if fun == pynibs.dummy_fun:
        c_all = np.random.random(len(elm_idx_list))

        if return_fits:
            best_values = [{"a": 1} for _ in range(len(elm_idx_list))]
            return c_all, best_values
        else:
            return c_all

    if qoi_path_hdf5 is None:
        qoi_path_hdf5 = ["e_matrix"]

    if fn_reg_hdf5 is not None and qoi_path_hdf5 is not None:
        df_reg = pd.read_hdf(fn_reg_hdf5, qoi_path_hdf5)  # type: pd.DataFrame
        e_matrix = df_reg.values[:, :-1]
        mep = df_reg.loc[:, "qoi_amplitudes"].values

    elif e_matrix is None or mep is None:
        raise ValueError("Please provide e_matrix and mep or fn_reg_hdf5 and qoi_path_hdf5!")

    if n_refit > 0 and con is None:
        raise ValueError("Please provide connectivity matrix (con) in case of refit!")

    # shuffle elements because some of them need longer to compute
    # (in this way it is distributed more equally over all cores)
    np.random.shuffle(elm_idx_list)
    if not isinstance(elm_idx_list, np.ndarray):
        elm_idx_list = np.array(elm_idx_list)
    elm_idx_list_shuffle_idx = np.argsort(elm_idx_list).astype(int)
    elm_idx_list = elm_idx_list.tolist()

    # Setting up parallelization
    if not pool:
        n_cpu_available = multiprocessing.cpu_count()
        n_cpu = min(n_cpu, n_cpu_available, len(elm_idx_list))
        pool = multiprocessing.Pool(n_cpu)
        local_pool = True

        if verbose:
            print(" > Setting up multiprocessing using {}/{} cores".format(n_cpu, n_cpu_available))
    else:
        local_pool = False  # close pool only if created locally
        if verbose:
            print(" > Using provided pool object")
    if n_cpu > 1:
        elm_idx_list_chunks = pynibs.compute_chunks(elm_idx_list, n_cpu)
    elif len(elm_idx_list) == 1:
        elm_idx_list_chunks = [elm_idx_list]
    elif n_cpu == 1:
        elm_idx_list_chunks = [elm_idx_list]
    else:
        raise ValueError(f'n_cpu={n_cpu} is invalid. ')

    # setting up initial values and limits
    if verbose:
        print(f" > Setting up initial values and limits for {fun.__name__} function (from {fun.__module__})!")

    log_scale, limits, init_vals, max_vals_refit = get_model_init_values(fun=fun,
                                                                         elm_idx_list=elm_idx_list,
                                                                         e_matrix=e_matrix,
                                                                         mep=mep,
                                                                         mask_e_field=None)

    if verbose:
        print(" > Calculating congruence factor ...")

    if type(qoi_path_hdf5) is not list:
        qoi_path_hdf5 = [qoi_path_hdf5]

    c_all = np.zeros((len(elm_idx_list), len(qoi_path_hdf5)))
    best_values = None
    # loop over electric field QOIs
    for i_q, q in enumerate(qoi_path_hdf5):
        workhorse_partial = partial(fit_elms,
                                    e_matrix=e_matrix,
                                    mep=mep,
                                    fun=fun,
                                    zap_idx=zap_idx,
                                    init_vals=init_vals,
                                    limits=limits,
                                    log_scale=log_scale,
                                    max_nfev=10,
                                    score_type=score_type,
                                    verbose=verbose)

        start = time.time()
        res = pool.map(workhorse_partial, elm_idx_list_chunks, chunksize=1)
        stop = time.time()
        if verbose:
            # print(len(elm_idx_list_chunks))
            print(f"Determine c-factors for {q} / {qoi_path_hdf5}: {stop - start:2.2f} s")

        best_values = []
        c = None
        for i in range(len(res)):
            if i == 0:
                c = res[i][0]
                best_values = res[i][1]
            else:
                if c.ndim < 2:
                    c = c[:, np.newaxis]
                if res[i][0].ndim < 2:
                    c = np.vstack((c, res[i][0][:, np.newaxis]))
                else:
                    c = np.vstack((c, res[i][0]))
                best_values += res[i][1]

        # resort c values
        c = c[elm_idx_list_shuffle_idx]
        best_values = [best_values[i] for i in elm_idx_list_shuffle_idx]
        elm_idx_list = np.array(elm_idx_list)[elm_idx_list_shuffle_idx].astype(list)

        # refit elements
        ####################################################################
        if n_refit > 0:
            params = inspect.getfullargspec(fun).args[1:]

            # refit bad elements
            ####################################################################
            i_refit = 0
            while i_refit < n_refit:
                idx_refit = np.where(c < refit_thr)[0]

                if len(idx_refit) > 0:
                    if verbose:
                        print(f" > Performing refit for {len(idx_refit)} zero elements ...")

                    # set random start values
                    if len(idx_refit) > 0:
                        for p in params:
                            for idx_re in idx_refit:
                                init_vals[p][idx_re] = max_vals_refit[p][idx_re] * np.random.rand()
                                # init_vals[p][idx_re] = init_vals[p][idx_re] + \
                                #                        max_vals_refit[p][idx_re] * (np.random.rand() - 0.5)

                        if n_cpu > 1:
                            elm_idx_list_chunks_zero = pynibs.compute_chunks(np.array(elm_idx_list)[idx_refit].tolist(),
                                                                             n_cpu)
                        elif len(elm_idx_list[idx_refit]) == 1:
                            elm_idx_list_chunks_zero = [elm_idx_list[idx_refit]]
                        else:  # n_cpu == 1:
                            elm_idx_list_chunks_zero = [elm_idx_list[idx_refit]]

                        workhorse_partial = partial(fit_elms,
                                                    e_matrix=e_matrix,
                                                    mep=mep,
                                                    fun=fun,
                                                    zap_idx=zap_idx,
                                                    init_vals=init_vals,
                                                    limits=limits,
                                                    log_scale=log_scale,
                                                    max_nfev=100,
                                                    score_type=score_type,
                                                    verbose=verbose)
                        start = time.time()
                        res_refit = pool.map(workhorse_partial, elm_idx_list_chunks_zero)
                        stop = time.time()

                        if verbose:
                            print(f"Determine c-factors (refit) for {q} / {qoi_path_hdf5}: {stop - start} s")

                        best_values_refit = []
                        c_refit = None
                        for i in range(len(res_refit)):
                            if i == 0:
                                c_refit = res_refit[i][0]
                                best_values_refit = res_refit[i][1]
                            else:
                                if c_refit.ndim < 2:
                                    c_refit = c_refit[:, np.newaxis]
                                if res_refit[i][0].ndim < 2:
                                    c_refit = np.vstack((c_refit, res_refit[i][0][:, np.newaxis]))
                                else:
                                    c_refit = np.vstack((c_refit, res_refit[i][0]))
                                best_values_refit += res_refit[i][1]

                        # overwrite old values with refitted ones if r2/sr score was higher,
                        # keep old value otherwise
                        for i_c_re, c_re in enumerate(c_refit):
                            if c_re < c[idx_refit[i_c_re]]:
                                c[idx_refit[i_c_re]] = c_re
                                best_values[idx_refit[i_c_re]] = best_values_refit[i_c_re]

                        i_refit += 1
                else:
                    break

            # find discontinuities and refit
            ##################################################################
            if refit_discontinuities and len(c) > 1:
                idx_disc, idx_neighbor = pynibs.get_indices_discontinuous_data(data=c,
                                                                               con=con,
                                                                               neighbor=True,
                                                                               deviation_factor=2)
                idx_disc = np.array(idx_disc)

                if len(idx_disc) > 0:
                    if verbose:
                        print(f" > Performing refit for {len(idx_disc)} discontinuous elements ...")

                    # refit for discontinuous elements
                    if len(idx_disc) > 0:
                        # set start values from neighbors
                        for p in params:
                            for idx_re, idx_ne in zip(idx_disc, idx_neighbor):
                                init_vals[p][idx_re] = best_values[idx_ne][p]

                        if n_cpu > 1:
                            elm_idx_list_chunks_disc = pynibs.compute_chunks(np.array(elm_idx_list)[idx_disc].tolist(),
                                                                             n_cpu)
                        elif len(elm_idx_list[idx_disc]) == 1:
                            elm_idx_list_chunks_disc = [elm_idx_list[idx_disc]]
                        else:  # n_cpu == 1:
                            elm_idx_list_chunks_disc = [elm_idx_list[idx_disc]]

                        start = time.time()
                        res_refit = pool.map(workhorse_partial, elm_idx_list_chunks_disc)
                        stop = time.time()

                        if verbose:
                            print(f"Determined c-factors (discontinuous refit) for "
                                  f"{q} / {qoi_path_hdf5}: {stop - start} s")

                        best_values_refit = []
                        c_refit = None
                        for i in range(len(res_refit)):
                            if i == 0:
                                c_refit = res_refit[i][0]
                                best_values_refit = res_refit[i][1]
                            else:
                                if c_refit.ndim < 2:
                                    c_refit = c_refit[:, np.newaxis]
                                if res_refit[i][0].ndim < 2:
                                    c_refit = np.vstack((c_refit, res_refit[i][0][:, np.newaxis]))
                                else:
                                    c_refit = np.vstack((c_refit, res_refit[i][0]))
                                best_values_refit += res_refit[i][1]

                        c[idx_disc] = c_refit

                        for j, i in enumerate(idx_disc):
                            best_values[i] = best_values_refit[j]

        c_all[:, i_q] = c.flatten()

    if local_pool:
        pool.close()
        pool.join()

    if return_fits:
        return c_all, best_values
    else:
        return c_all


def get_model_init_values(fun, elm_idx_list, e_matrix, mep, mask_e_field=None,
                          rem_empty_hints=True):
    """
    Calc appropriate init, limit, and max values for models fits depending on the data. If negative and positive x-data
    is present in case of e.g. normal component values are set according to the side (positive or negative)
    where more values are present. When more positive x-axis values are present, negative x-axis values will be ignored.
    When more negative x-axis values are present, the absolute values will be taken and the positive values are ignored.

    Only parameters for sigmoid* are optimized.

    Parameters
    ----------
    fun : pyfempp.exp.Mep
        IO curve function object
    elm_idx_list : np.ndarray of int
        Array containing the element indices the fit is performed for
    e_matrix : ndarray of float [n_zaps x n_ele]
        Electric field matrix
    mep : ndarray of float [n_zaps]
        Motor evoked potentials for every stimulation
    mask_e_field : ndarray of bool [n_zaps x n_ele], optional, default: None
        Mask indicating for which e-field (and mep) values the fit is performed for. Changes for normal component in
        each element because of the sign and p-values. If None, all data is used in each element.
    rem_empty_hints: bool, default: True
        Remove any non-filled param hints from limits dict.

    Returns
    -------
    log_scale : bool
        Log scale
    limits : dict of list [n elm_index_list]
        Element-wise limit values for function fitting.
    init_vals : dict of list [n elm_index_list]
        Element-wise init values for function fitting.
    max_vals_refit : dict of list [n elm_index_list]
        Element-wise perturbation range for refitting function.
    """
    init_vals = dict()
    max_vals_refit = dict()
    limits = dict()

    if mask_e_field is None:
        mask_e_field = np.ones(e_matrix.shape).astype(bool)

    # get functions-specific argument names
    params = inspect.getfullargspec(fun).args[1:]
    for p in params:
        init_vals[p] = []
        max_vals_refit[p] = []
        limits[p] = []

    if fun == pynibs.linear:
        # linear function starts with generic and same values for each element
        for _ in range(len(elm_idx_list)):
            limits["m"].append([-100, 100])
            limits["n"].append([-100, 100])

            init_vals["m"].append(0.3)
            init_vals["n"].append(-1)

            max_vals_refit["m"].append(100)
            max_vals_refit["n"].append(.3)

    elif fun == pynibs.exp0:
        for _ in range(len(elm_idx_list)):
            limits["x0"].append([0, 1000])
            limits["r"].append([1e-12, 100])

            # init_vals["x0"].append(40)
            init_vals["x0"].append(1)
            init_vals["r"].append(.1)

            # max_vals_refit["x0"].append(100)
            max_vals_refit["x0"].append(10)
            max_vals_refit["r"].append(.2)

    elif fun == pynibs.sigmoid or fun == pynibs.sigmoid_log:
        # limits["x0"] = [[0, 1000] for _ in range(len(elm_idx_list))]
        # limits["amp"] = [[1e-12, 1000] for _ in range(len(elm_idx_list))]
        # limits["r"] = [[1e-12, 100] for _ in range(len(elm_idx_list))]

        for _, elm in enumerate(elm_idx_list):
            e_elm = np.abs(e_matrix[mask_e_field[:, elm], elm])

            # x0 first guess: center between e_min, e_max
            e_min = np.min(e_elm)
            e_max = np.max(e_elm)

            x_0 = e_min + np.max(e_elm) / 2
            init_vals["x0"].append(x_0)

            amp = np.max(mep)
            init_vals["amp"].append(amp)  # largest MEP

            # r0 initial: slope from max_mep/min_mep over middle 50% of e-range
            # r = 8 / np.max(e_elm) * ((np.max(mep) - np.min(mep)) / (e_max - e_min))
            r = (np.max(mep) - np.min(mep)) / (e_max - e_min)
            init_vals["r"].append(r)

            # max_vals_refit["x0"].append(200)
            max_vals_refit["x0"].append(3 * x_0)
            max_vals_refit["amp"].append(3 * amp)
            max_vals_refit["r"].append(3 * r)

        # set upper bound of limits in relation to init_vals
        factor = 100
        limits["x0"] = [[0, init_vals["x0"][i] * 3] for i in range(len(elm_idx_list))]
        limits["amp"] = [[1e-12, init_vals["amp"][i] * 3] for i in range(len(elm_idx_list))]
        limits["r"] = [[1e-12, init_vals["r"][i] * factor] for i in range(len(elm_idx_list))]

    elif fun == pynibs.sigmoid4 or fun == pynibs.sigmoid4_log:
        for _, elm in enumerate(elm_idx_list):
            e_elm = np.abs(e_matrix[mask_e_field[:, elm], elm])

            # x0 first guess: center between e_min, e_max
            e_min = np.min(e_elm)
            e_max = np.max(e_elm)

            x_0 = e_min + np.max(e_elm) / 2
            init_vals["x0"].append(x_0)

            amp = np.max(mep)
            init_vals["amp"].append(amp)  # largest MEP

            # r0 initial: slope from max_mep/min_mep over middle 50% of e-range
            # r = 8 / np.max(e_elm) * ((np.max(mep) - np.min(mep)) / (e_max - e_min))
            r = (np.max(mep) - np.min(mep)) / (e_max - e_min)
            init_vals["r"].append(r)

            # max_vals_refit["x0"].append(200)
            max_vals_refit["x0"].append(3 * x_0)
            max_vals_refit["amp"].append(3 * amp)
            max_vals_refit["r"].append(3 * r)

            init_vals["y0"].append(np.min(mep))

            # if init_vals["y0"][-1] <= 0:
            #     init_vals["y0"][-1] = 1e-3

            max_vals_refit["y0"].append(np.min(mep) * 3)

        # set upper bound of limits in relation to init_vals
        factor = 100
        limits["x0"] = [[0, init_vals["x0"][i] * 3] for i in range(len(elm_idx_list))]
        limits["amp"] = [[1e-12, init_vals["amp"][i] * 3] for i in range(len(elm_idx_list))]
        limits["r"] = [[1e-12, init_vals["r"][i] * factor] for i in range(len(elm_idx_list))]
        y0_init = init_vals["y0"][0]
        limits["y0"] = [[np.abs(y0_init) * -2, np.abs(y0_init) * 2] for _ in range(len(elm_idx_list))]

    elif fun == pynibs.dummy_fun:
        for _ in range(len(elm_idx_list)):
            limits["a"].append([0, 1])
            init_vals["a"].append(1)
            max_vals_refit["a"].append(1)
    else:
        raise NotImplementedError(fun)

    if fun == pynibs.sigmoid_log or fun == pynibs.sigmoid4_log:
        log_scale = True
    else:
        log_scale = False

    if rem_empty_hints:
        # remove params hints for params that are not taken care of here
        keys_2_remove = [k for k, v in limits.items() if not v]
        for k in keys_2_remove:
            del limits[k]
            del init_vals[k]
            del max_vals_refit[k]

    return log_scale, limits, init_vals, max_vals_refit


def nl_hdf5_single_core_write(i, elm_idx_list, fn_reg_hdf5=None, qoi_path_hdf5=None, e_matrix=None,
                              mep=None,
                              fun=pynibs.sigmoid4,
                              con=None, n_refit=50, return_fits=False, constants=None, verbose=False,
                              seed=None, stepdown=False, score_type='R2', return_progress=False, geo=None):
    # get string prefix for useful multiprocessing logging
    str_pref = "Main"
    try:
        str_pref = f"{multiprocessing.current_process()._identity[0]:0>2} "
    except Exception:
        pass

    # compute c
    if stepdown:
        res = stepdown_approach(zap_idx=z[i],
                                elm_idx_list=elm_idx_list,
                                fn_reg_hdf5=fn_reg_hdf5,
                                qoi_path_hdf5=qoi_path_hdf5,
                                e_matrix=e_matrix[z[i]],
                                mep=mep.iloc[z[i]],
                                fun=fun,
                                con=con,
                                n_refit=n_refit, return_fits=return_fits,
                                constants=constants,
                                verbose=verbose, seed=seed,
                                score_type=score_type,
                                return_progress=return_progress,
                                geo=geo)
    else:
        res = nl_hdf5_single_core(zap_idx=z[i],
                                  elm_idx_list=elm_idx_list,
                                  fn_reg_hdf5=fn_reg_hdf5,
                                  qoi_path_hdf5=qoi_path_hdf5,
                                  e_matrix=e_matrix,
                                  mep=mep,
                                  fun=fun,
                                  con=con,
                                  n_refit=n_refit, return_fits=return_fits, constants=constants,
                                  verbose=verbose, seed=seed)

    c = res['c']
    best_values = res['best_values'] if 'best_values' in res else None
    progress_data = res['progress'] if 'progress' in res else {}
    stats = res['stats'] if 'stats' in res else {}

    # write to hdf5, threadsafe
    if verbose:
        print(f"{str_pref}: > Writing results for {len(z[i])} zaps to {fn}.")
    with lock:
        with h5py.File(fn, 'a') as f:
            f.create_dataset(f'c/{len(z[i])}', data=c)
            for key in stats:
                stat = stats[key]
                if not isinstance(stat, np.ndarray):
                    stat = np.array([stat])
                f.create_dataset(f'{key}/{len(z[i])}', data=stat)

    if verbose:
        print(f"{str_pref}: > Writing results for {len(z[i])} zaps done.")

    return {'progress_data': progress_data,
            'best_values': best_values}


def get_bad_elms(x, y, method="lstsq", verbose=False):
    """
    This does an element-wise fast linear regression fit to identify bad elements.
    Bad is defined here as a negative slope.

    x : ndarray of float [n_zaps x n_ele]
        Electric field matrix
    y : ndarray of float [n_zaps]
        Motor evoked potentials for every stimulation
    method : str, default: "lstsq"
        Which method to use. (numpy.linalg.)lstsq, (scipy.stats.)linregress, or pinv
    verbose : bool, optional, default: False
        Print verbosity information

     Returns
    -------
    idx: ndarray
        Indices of bad elements
    """
    str_pref = "Main"
    try:
        str_pref = f"{multiprocessing.current_process()._identity[0]:0>2} "
    except:
        pass
    start = time.time()
    if method == "linregress":
        idx = [i for i in range(x.shape[1]) if
               linregress(x[:, i], y).slope < 0]
    elif method == "lstsq":
        idx = [i for i in range(x.shape[1]) if
               lstsq(np.vstack([x[:, i], np.ones(x.shape[0])]).T, y, rcond=None)[0][0] < 0]
    elif method == 'pinv':
        warnings.warn("pinv method is untested.")
        idx = [i for i in range(x.shape[1]) if
               pinv(x[:, i].reshape(x.shape[0], 1)).dot(y)[0] < 0]
    else:
        raise NotImplementedError(f'Method {method} unknown.')

    if verbose:
        print(
                f"Proc{str_pref}:  > {len(idx)}/{x.shape[1]} bad elms removed from fitting ({time.time() - start:2.4} s).")

    return idx


def nl_hdf5_single_core(zap_idx, elm_idx_list, fn_reg_hdf5=None, qoi_path_hdf5=None, e_matrix=None, mep=None,
                        fun=pynibs.sigmoid4,
                        con=None, n_refit=50, return_fits=False, constants=None, verbose=False, seed=None,
                        rem_bad_elms=True, return_e_field_stats=True):
    """
    Mass-univariate nonlinear regressions on raw MEP_{AMP} ~ E.
    That is, for each element in elm_idx_list, it's E (mag | norm | tan) for each zap regressed on the raw MEP
    amplitude. An element wise r2 score is returned.
    The function reads the precomputed array of E-MEP data from an .hdf5 file.

    Parameters
    ----------
    elm_idx_list : np.ndarray of int
        List containing the element indices the fit is performed for
    fn_reg_hdf5 : str
        Filename (incl. path) containing the precomputed E-MEP dataframes
    qoi_path_hdf5: str or list of str
        Path in .hdf5 file to dataset of electric field qoi e.g.: ["E", "E_norm", "E_tan"]
    e_matrix : ndarray of float [n_zaps x n_ele]
        Electric field matrix
    mep : ndarray of float [n_zaps]
        Motor evoked potentials for every stimulation
    zap_idx : np.array [n_zaps], optional, default: None
        Indices of zaps the congruence factor is calculated with (default: all)
    fun : function object
        A function of pynibs.exp.Mep (exp0, sigmoid)
    con : ndarray of float [n_roi, 3 or 4], optional, default: None
        Connectivity matrix of ROI (needed in case of refit because of discontinuity check)
    n_refit : int, optional, default: 50
        Maximum number of refits of zero elements. No refit is applied in case of n_refit = 0.
    return_fits : bool, optional, default: False
        Return fit objects containing the parameter estimates
    constants : dict of <string>:<num>, optional, default: None
        key:value pair of model parameters not to optimize.
    verbose : bool, optional, default: False
        Plot output messages
    seed: int, optional, default: None
        Seed to use.
    rem_bad_elms: bool, default: True
        Remove elements based on a fast linear regression slope estimation
    return_e_field_stats : bool, default: True
        Return some stats on the efield variance

    Returns
    -------
    r2 : ndarray of float [n_roi, n_qoi]
        R2 for each element in elm_idx_list
    """
    starttime = time.time()
    str_pref = "Main"
    try:
        str_pref = f"{multiprocessing.current_process()._identity[0]:0>2} "
    except:
        pass
    best_values = None

    if qoi_path_hdf5 is None:
        qoi_path_hdf5 = ["e_matrix"]

    if fn_reg_hdf5 is not None and qoi_path_hdf5 is not None:
        df_reg = pd.read_hdf(fn_reg_hdf5, qoi_path_hdf5)
        e_matrix = df_reg.values[:, :-1]
        mep = df_reg.loc[:, "qoi_amplitudes"].values

    elif e_matrix is None or mep is None:
        raise ValueError(f"Proc{str_pref}: Please provide e_matrix and mep or fn_reg_hdf5 and qoi_path_hdf5!")

    if n_refit > 0 and con is None:
        raise ValueError(f"Proc{str_pref}: Please provide connectivity matrix (con) in case of refit!")

    # shuffle elements because some of them need longer to compute
    # (in this way it is distributed more equally over all cores)
    if seed:
        np.random.seed(seed)
    np.random.shuffle(elm_idx_list)
    if not isinstance(elm_idx_list, np.ndarray):
        elm_idx_list = np.array(elm_idx_list)
    elm_idx_list_shuffle_idx = np.argsort(elm_idx_list)

    # setting up initial values and limits
    if verbose:
        print(
                f"Proc{str_pref}: > Setting up initial values and limits "
                f"for {fun.__name__} function (from {fun.__module__}).")

    log_scale, limits, init_vals, max_vals_refit = get_model_init_values(fun,
                                                                         elm_idx_list,
                                                                         e_matrix,
                                                                         mep)

    if verbose:
        print(f"Proc{str_pref}: > c-map for {len(zap_idx)}: starting.")

    n_elm = len(elm_idx_list)
    if type(qoi_path_hdf5) is not list:
        qoi_path_hdf5 = [qoi_path_hdf5]

    c_all = np.zeros((len(elm_idx_list), len(qoi_path_hdf5)))

    if rem_bad_elms:
        bad_elm_idx = get_bad_elms(e_matrix[zap_idx], mep.iloc[zap_idx].values, method='lstsq', verbose=True)
    else:
        bad_elm_idx = np.empty((0,))

    # get e field stats
    e_stats_dicts = None
    if return_e_field_stats:
        mc = pynibs.mutual_coherence(e_matrix.transpose())
        _, sv_rat, _ = svd(e_matrix)
        sv_rat = np.max(sv_rat) / np.min(sv_rat)
        e_stats_dicts = {'mc': mc,
                         'sv_rat': sv_rat}

    # fast return for testruns
    if fun == pynibs.dummy_fun:
        c_all = np.random.random(n_elm)
        ret = (c_all,)
        if return_fits:
            best_values = [{"a": 1} for _ in range(n_elm)]
            ret += (best_values,)
        if return_e_field_stats:
            ret += (e_stats_dicts,)
        return ret

    # loop over electric field QOIs
    for i_q, q in enumerate(qoi_path_hdf5):

        start = time.time()
        res = fit_elms(
                elm_idx_list=elm_idx_list,
                e_matrix=e_matrix,
                mep=mep,
                fun=fun,
                zap_idx=zap_idx,
                init_vals=init_vals,
                limits=limits,
                log_scale=log_scale,
                constants=constants,
                max_nfev=10,
                verbose=verbose,
                bad_elm_idx=bad_elm_idx)
        stop = time.time()

        if verbose:
            print(f"Proc{str_pref}:  > Determine c-factors done. ({stop - start:2.2f} s)")

        c = res[0]
        best_values = res[1]

        # resort c values
        c = c[elm_idx_list_shuffle_idx]
        best_values = np.array([best_values[i] for i in elm_idx_list_shuffle_idx])
        elm_idx_list = elm_idx_list[elm_idx_list_shuffle_idx]

        # refit elements
        ####################################################################
        if n_refit > 0:
            params = inspect.getfullargspec(fun).args[1:]

            # refit zero elements
            ####################################################################
            i_refit_zero = 0
            while i_refit_zero < n_refit:
                idx_zero = np.where(c < 1e-6)[0]
                idx_zero = np.setdiff1d(idx_zero, bad_elm_idx)

                # refit zero elements
                if len(idx_zero) > 0:
                    if verbose:
                        print(f"Proc{str_pref}:   > Zero refit {i_refit_zero}/{n_refit} "
                              f"({len(idx_zero)} elements): starting.")

                    # set random start values
                    for p in params:
                        for idx_ze in idx_zero:
                            init_vals[p][idx_ze] = max_vals_refit[p][idx_ze] * np.random.rand()

                    start = time.time()
                    c_refit, best_values_refit = fit_elms(
                            elm_idx_list=elm_idx_list[idx_zero],
                            e_matrix=e_matrix,
                            mep=mep,
                            fun=fun,
                            zap_idx=zap_idx,
                            init_vals=init_vals,
                            limits=limits,
                            log_scale=log_scale,
                            max_nfev=10,
                            verbose=verbose)
                    stop = time.time()

                    if verbose:
                        print(
                                f"Proc{str_pref}:   > Zero refit {i_refit_zero}/{n_refit} "
                                f"({len(idx_zero)} elements): done. "
                                f"({stop - start:.2f} s, "
                                f"{(stop - start) / len(idx_zero):.2f} / elm, "
                                f"{np.sum(c_refit > 1e-6)} > 0 )")

                    # overwrite old values with refitted ones if r2 score was higher, keep old value otherwise
                    for idx_c_ref, c_ref in enumerate(c_refit):
                        if c_ref > c[idx_zero[idx_c_ref]]:
                            # print(f"{idx_zero[idx_c_ref]}: {c[idx_zero[idx_c_ref]]} -> {c_ref}")
                            c[idx_zero[idx_c_ref]] = c_ref
                            best_values[idx_zero[idx_c_ref]] = best_values_refit[idx_c_ref]

                    i_refit_zero += 1

                # find discontinuities and refit

                idx_disc, idx_neighbor = pynibs.get_indices_discontinuous_data(data=c, con=con, neighbor=True,
                                                                               deviation_factor=2, min_val=1e-12,
                                                                               not_fitted_elms=bad_elm_idx)
                idx_disc = np.setdiff1d(idx_disc, bad_elm_idx)

                if len(idx_disc) > 0:

                    if verbose:
                        print(f"Proc{str_pref}:   > Discontinuous refit ({len(idx_disc)} elements): starting.")

                    # set start values from neighbors
                    for p in params:
                        for idx_re, idx_ne in zip(idx_disc, idx_neighbor):
                            init_vals[p][idx_re] = best_values[idx_ne][p]

                    start = time.time()
                    c_refit, best_values_refit = fit_elms(
                            elm_idx_list=elm_idx_list[idx_disc],
                            e_matrix=e_matrix,
                            mep=mep,
                            fun=fun,
                            zap_idx=zap_idx,
                            init_vals=init_vals,
                            limits=limits,
                            log_scale=log_scale,
                            max_nfev=10,
                            verbose=verbose)

                    stop = time.time()

                    if verbose:
                        print(
                                f"Proc{str_pref}:   > Discontinuous refit ({len(idx_disc)} elements): "
                                f"done ({stop - start:.2f} s)")

                    # overwrite old values with refitted ones
                    c[idx_disc] = c_refit
                    best_values[idx_disc] = best_values_refit

        c_all[:, i_q] = c.flatten()

    endtime = time.time()
    print(f"Proc{str_pref}:  > c-map for {len(zap_idx)} zaps done ({endtime - starttime:2.2f}s). ")

    ret = (c_all,)
    if return_fits:
        best_values = [{"a": 1} for _ in range(n_elm)]
        ret += (best_values,)
    if return_e_field_stats:
        ret += (e_stats_dicts,)
    return ret


def stepdown_approach(zap_idx, elm_idx_list, fn_reg_hdf5=None, qoi_path_hdf5=None, e_matrix=None,
                      mep=None,
                      fun=pynibs.sigmoid4,
                      con=None, n_refit=50, return_fits=False, constants=None, verbose=False,
                      seed=None,
                      rem_bad_elms=True, return_e_field_stats=True,
                      score_type='R2', return_progress=False, smooth_data=True, geo=None):
    """
    Mass-univariate nonlinear regressions on raw MEP_{AMP} ~ E in a stepdown manner to speed up computation.

    Initially, one set of fits is done for the complete dataset. Afterwards, the best 1% of the elements are used
        as initial fitting parameters for their neighboring elements. Then, neighboring elements are fitted accordingly
        and iterativley.
        Finally, discontinuous elements are refitted until a smooth map is found or n_refit is hit.

    Can be sped up with rem_bad_elms that computes a fast linear fit to identify elements with a negative slope.


    The function reads the precomputed array of E-MEP data from an .hdf5 file.

    Parameters
    ----------
    elm_idx_list : np.ndarray of int
        List containing the element indices the fit is performed for
    fn_reg_hdf5 : str
        Filename (incl. path) containing the precomputed E-MEP dataframes
    qoi_path_hdf5: str or list of str
        Path in .hdf5 file to dataset of electric field qoi e.g.: ["E", "E_norm", "E_tan"]
    e_matrix : ndarray of float [n_zaps x n_ele] | [n_zapidx x n_ele]
        Electric field matrix
    mep : ndarray of float [n_zaps]
        Motor evoked potentials for every stimulation
    zap_idx : np.array [n_zaps], optional, default: None
        Indices of zaps the congruence factor is calculated with (default: all)
    fun : function object
        A function of pynibs.exp.Mep (exp0, sigmoid)
    con : ndarray of float [n_elm_roi, 3 or 4], optional, default: None
        Connectivity matrix of ROI (needed in case of refit because of discontinuity check)
    n_refit : int, optional, default: 50
        Maximum number of refits of zero elements. No refit is applied in case of n_refit = 0.
    return_fits : bool, optional, default: False
        Return fit objects containing the parameter estimates
    constants : dict of <string>:<num>, optional, default: None
        key:value pair of model parameters not to optimize.
    verbose : bool, optional, default: False
        Plot output messages
    seed: int, optional, default: None
        Seed to use.
    rem_bad_elms: bool, default: True
        Remove elements based on a fast linear regression slope estimation
    return_e_field_stats : bool, default: True
        Return some stats on the efield variance

    Returns
    -------
    dict:
        r2 : ndarray of float [n_roi, n_qoi]
            R2 for each element in elm_idx_list
        best_values: list of dict, optional
            fit information
        stats : dict, optional
            'mc': float, optional
                Mutual coherence for e fields
            'sv_rat' : float, optional
                SVD singular value ratio
        progress : cmaps for each step
    """
    starttime = time.time()

    # get string prefix for useful multiprocessing logging
    str_pref = "Main"
    try:
        str_pref = f"{multiprocessing.current_process()._identity[0]:0>2} "
    except:
        pass

    if qoi_path_hdf5 is None:
        qoi_path_hdf5 = ["e_matrix"]

    if fn_reg_hdf5 is not None and qoi_path_hdf5 is not None:
        df_reg = pd.read_hdf(fn_reg_hdf5, qoi_path_hdf5)
        e_matrix = df_reg.values[:, :-1]
        mep = df_reg.loc[:, "qoi_amplitudes"].values

    elif e_matrix is None or mep is None:
        raise ValueError(f"Proc{str_pref}: Please provide e_matrix and mep or fn_reg_hdf5 and qoi_path_hdf5!")

    if n_refit > 0 and con is None:
        raise ValueError(f"Proc{str_pref}: Please provide connectivity matrix (con) in case of refit!")

    if not isinstance(elm_idx_list, np.ndarray):
        elm_idx_list = np.array(elm_idx_list)

    # setting up initial values and limits
    if verbose:
        print(
                f"Proc{str_pref}: > Setting up initial values and limits "
                f"for {fun.__name__} function (from {fun.__module__}).")

    log_scale, limits, init_vals, max_vals_refit = get_model_init_values(fun,
                                                                         elm_idx_list,
                                                                         e_matrix,
                                                                         mep)
    # convert dict-of-lists to dict-of-dicts

    init_vals = pd.DataFrame().from_dict(init_vals)
    limits = pd.DataFrame().from_dict(limits)

    n_elm = len(elm_idx_list)
    if type(qoi_path_hdf5) is not list:
        qoi_path_hdf5 = [qoi_path_hdf5]
    c_all = np.zeros((n_elm, len(qoi_path_hdf5)))

    if e_matrix.shape[0] != len(zap_idx):
        e_matrix = e_matrix[zap_idx]
        mep = mep[zap_idx]

    # get bad elms by checking their linear slope fit
    if rem_bad_elms:
        bad_elm_idx = set(get_bad_elms(e_matrix[:, elm_idx_list], mep.values, method='lstsq', verbose=verbose))
    else:
        bad_elm_idx = set()

    # get e field stats
    e_stats_dicts = None
    if return_e_field_stats:
        stats_start = time.time()
        mc = pynibs.mutual_coherence(e_matrix.transpose())

        sv_rat = svd(e_matrix, check_finite=False, compute_uv=False)
        sv_rat = np.max(sv_rat) / np.min(sv_rat)
        e_stats_dicts = {'mc': mc,
                         'sv_rat': sv_rat}
        stats_end = time.time()
        if verbose:
            print(f"Proc{str_pref} : > Efield stats computation took {stats_end - stats_start:2.2f} s.")

    # fast return for testruns
    if fun == pynibs.dummy_fun:
        c_all = np.random.random(n_elm)
        ret = (c_all,)
        if return_fits:
            best_values = [{"a": 1} for _ in range(n_elm)]
            ret += (best_values,)
        if return_e_field_stats:
            ret += (e_stats_dicts,)
        return ret

    if verbose:
        print(f"Proc{str_pref}: > c-map for {e_matrix.shape[0]}: starting.")
    if return_progress:
        return_progress_lst = []
    # loop over electric field QOIs
    for i_q, q in enumerate(qoi_path_hdf5):

        start = time.time()
        # get initial c-map
        start_sample = np.random.choice(elm_idx_list, int(.1 * len(elm_idx_list)), replace=False)
        # c, best_values = np.zeros(elm_idx_list.shape), np.zeros(elm_idx_list.shape).astype(object)

        c, best_values = np.zeros(elm_idx_list.shape), init_vals.copy()
        if return_progress:
            return_progress_lst.append(c.copy())
        c[start_sample], best_values.iloc[start_sample] = fit_elms(
                elm_idx_list=start_sample,
                e_matrix=e_matrix,
                mep=mep,
                fun=fun,
                init_vals=init_vals,
                limits=limits,
                log_scale=log_scale,
                constants=constants,
                max_nfev=10,
                verbose=verbose,
                bad_elm_idx=bad_elm_idx,
                score_type=score_type)
        if return_progress:
            return_progress_lst.append(c.copy())
        stop = time.time()

        if verbose:
            print(f"Proc{str_pref}:  > Initial c-factor map done. ({stop - start:2.2f} s)")

        # pick the best elements and compute their neibors' fits
        n_top = int(len(start_sample) * .2)

        elms_done = start_sample[np.argpartition(c[start_sample], -n_top)[-n_top:]]
        mask = np.ones(c.shape, np.bool)
        mask[elms_done] = 0
        c[mask] = 0
        if return_progress:
            return_progress_lst.append(c.copy())
        elms_done = elms_done[c[elms_done] > 0]
        elms_seed = elms_done.copy()
        elms_done = set(elms_done)

        params = inspect.getfullargspec(fun).args[1:]
        i_step = 0
        start = time.time()
        while True:
            # reorder to highest c first
            elms_seed = elms_seed[np.argsort(-c[elms_seed])]
            elm_to_compute = set()

            # compute last 5% in one batch
            if geo is not None and len(elms_done) > 0.95 * len(elm_idx_list):
                elm_to_compute = list(set(elm_idx_list).difference(elms_done))
                print(f"last 5% {len(elms_done)} -> {len(elm_to_compute)}")
                if not elm_to_compute:
                    break

                for elm in elm_to_compute:  # elm = list(elm_to_compute)[0]
                    # use nearest element's params to fit this element
                    nearest_idx = np.argmin(np.linalg.norm(np.mean(geo[con][c > 0], axis=1) -
                                                           np.mean(geo[con[elm]], axis=0), axis=1))
                    nearest_idx = np.argwhere(np.sum(con == con[c > 0][nearest_idx], axis=1) == 3)[0][0]
                    for p in params:
                        init_vals.iloc[elm][p] = best_values.iloc[nearest_idx][p]

            else:
                # increase spread with increasing steps
                for _ in range(i_step + 1):
                    for elm_done_i in elms_seed:
                        # find neighbors for the already computed element
                        mask = np.sum(np.isin(con, con[elm_done_i, :]), axis=1)
                        neighbors = set(np.where((0 < mask) & (mask < 3))[0])

                        # remove elms we already have computed or don't want to compute
                        neighbors.difference_update(elms_done, bad_elm_idx, elm_to_compute)
                        neighbors.intersection_update(elm_idx_list)
                        if not neighbors:
                            continue
                        elm_to_compute.update(neighbors)
                        for neigh in neighbors:
                            # use params of done neighbors as init vals for their neighbors
                            for p in params:
                                init_vals[p][neigh] = best_values.iloc[elm_done_i][p]
                            best_values.iloc[neigh] = best_values.iloc[elm_done_i]

                    print(f"{i_step:0>3}: Seed {len(elms_seed)} -> {len(elm_to_compute)}")

                    # refit already here some elements
                    not_fitted_elms = c[np.array(list(elms_done))] <= 0
                    # get random neighbor to refit
                    idx_disc, idx_neighbor = pynibs.get_indices_discontinuous_data(data=c[np.array(list(elms_done))],
                                                                                   con=con[np.array(list(elms_done))],
                                                                                   neighbor=True,
                                                                                   deviation_factor=3, min_val=1e-12,
                                                                                   not_fitted_elms=not_fitted_elms,
                                                                                   crit='randmax',
                                                                                   neigh_style='point')
                    idx_disc = np.setdiff1d(idx_disc, bad_elm_idx)
                    # set init values from neighbors best values
                    for p in params:
                        for idx_refit, idx_neighbor in zip(idx_disc, idx_neighbor):
                            init_vals[p][idx_refit] = best_values.iloc[idx_neighbor][p]
                    elm_to_compute.update(idx_disc)
                    # save the elms that will be computed now for the next iteration as seed elements
                    elms_seed = elm_to_compute.copy()
                elm_to_compute = list(elm_to_compute)
                elms_seed = np.array(list(elms_seed))

            if not elm_to_compute:
                # end loop
                break

            # start = time.time()
            c[elm_to_compute], best_values.iloc[elm_to_compute] = fit_elms(
                    elm_idx_list=elm_to_compute,
                    e_matrix=e_matrix,
                    mep=mep,
                    fun=fun,
                    init_vals=init_vals,
                    limits=limits,
                    log_scale=log_scale,
                    constants=constants,
                    max_nfev=1,
                    verbose=verbose,
                    score_type=score_type)
            if return_progress:
                return_progress_lst.append(c.copy())
            i_step += 1
            elms_done.update(elm_to_compute)
        stop = time.time()

        if verbose:
            print(
                    f"Proc{str_pref}:   > Stepdown iterations {i_step:0>2} "
                    f"({len(elms_done)}/{n_elm - len(bad_elm_idx)} ({len(bad_elm_idx)} excluded) elements): done. "
                    f"({stop - start:.2f} s "
                    f"{np.sum(c[elm_to_compute] > 1e-6)} > 0)")

        # refit the discontinues elemens
        not_fitted_elms = c == 0
        idx_disc, idx_neighbor = pynibs.get_indices_discontinuous_data(data=c, con=con[elm_idx_list], neighbor=True,
                                                                       deviation_factor=3, min_val=1e-12,
                                                                       not_fitted_elms=not_fitted_elms, crit='max',
                                                                       neigh_style='point')
        idx_disc = np.setdiff1d(idx_disc, bad_elm_idx)

        disc_fit_i, last_disc_idx = 1, idx_disc
        # only repeat until no improvement
        while 0 < len(idx_disc) and disc_fit_i <= n_refit:

            # set init values from neighbors best values
            for p in params:
                for idx_refit, idx_neighbor in zip(idx_disc, idx_neighbor):
                    init_vals[p][idx_refit] = best_values.iloc[idx_neighbor][p]

            start = time.time()
            c[idx_disc], best_values.iloc[idx_disc] = fit_elms(
                    elm_idx_list=elm_idx_list[idx_disc],
                    e_matrix=e_matrix,
                    mep=mep,
                    fun=fun,
                    init_vals=init_vals,
                    limits=limits,
                    log_scale=log_scale,
                    constants=constants,
                    max_nfev=int(np.log2(disc_fit_i)),  # inrease number of nfev each time
                    verbose=verbose,
                    score_type=score_type)
            if return_progress:
                return_progress_lst.append(c.copy())

            # prepare the next iteration
            last_disc_n = len(idx_disc)
            idx_disc, idx_neighbor = pynibs.get_indices_discontinuous_data(data=c, con=con[elm_idx_list], neighbor=True,
                                                                           deviation_factor=3, min_val=1e-12,
                                                                           not_fitted_elms=not_fitted_elms, crit='max',
                                                                           neigh_style='point')
            idx_disc = np.setdiff1d(idx_disc, bad_elm_idx)
            if np.all(last_disc_idx == idx_disc):
                break
            stop = time.time()

            if verbose:
                print(
                        f"Proc{str_pref}:   > Discontinuous refit {disc_fit_i:0>2} ({last_disc_n} elements): "
                        f"done ({stop - start:.2f} s)")
            disc_fit_i += 1

        # smooth data
        if smooth_data:
            smoothed_c = np.zeros_like(c)
            for i, c_dat in np.ndenumerate(c):
                mask = np.sum(np.isin(con, con[i, :]), axis=1)
                mask = np.logical_and(0 < mask, mask < 3)
                # if c_dat <= 0:
                if np.sum(c[mask] == 0) != 0:
                    # if all elements are < 0
                    smoothed_c[i] = 0.3 * np.mean(c[mask][c[mask] == 0]) + 0.7 * c_dat
                else:
                    # otherwise just use good elements
                    smoothed_c[i] = c_dat
                # else:
                # don't touch element if it's the only one with positive values
                # if len(c[mask][c[mask] > 0]) > 1:
                #     smoothed_c[i] = 0.3 * np.mean(c[mask][c[mask] > 0]) + 0.7 * c_dat
                # else:
                #     smoothed_c[i] = c_dat
            c = smoothed_c
        if return_progress:
            return_progress_lst.append(c.copy())
        c_all[:, i_q] = c.flatten()

    endtime = time.time()
    print(f"Proc{str_pref}:  > c-map for {len(zap_idx)} zaps done ({endtime - starttime:2.2f}s). ")
    if verbose:
        bad_elm_idx = list(bad_elm_idx)
        print(f"Proc{str_pref}:  >  min | med | max: "
              f"{np.min(np.delete(c, bad_elm_idx)):2.2f} | "
              f"{np.median(np.delete(c, bad_elm_idx)):2.2f} | "
              f"{np.max(np.delete(c, bad_elm_idx)):2.2f}. "
              f"{np.sum(c > 0)} elms > 0 | "
              f"{len(c)} n_elms")
    ret = {'c': c_all}
    if return_fits:
        ret['best_values'] = best_values
    if return_e_field_stats:
        ret['stats'] = e_stats_dicts
    if return_progress:
        ret['progress'] = return_progress_lst
    return ret


def sing_elm_fitted(elm_idx_list, mep_lst, mep_params, e, alpha=1000, n_samples=100):
    """
    Mass-univariate ridge regressions on fitted MEP_{AMP} ~ E.
    That is, for each element in elm_idx_list, it's E (mag | norm | tan) for each zap regressed on the raw MEP
    amplitude. An element wise sklearn.metrics.regression.r2_score is returned.


    elm_idx_list: nparray [chunksize]
        List of element indices, the congruence factor is computed for
    mep_lst: list of Mep object instances [n_cond]
        List of fitted Mep object instances for all conditions (see exp.py for more information of Mep class)
    mep_params: nparray of float [n_mep_params_total]
        List of all mep parameters of curve fits used to calculate the MEP (accumulated into one array)
        (e.g.: [mep_#1_para_#1, mep_#1_para_#2, mep_#1_para_#3, mep_#2_para_#1, mep_#2_para_#1, ...])
    e: nparray of float with e.shape == (n_elm, n_cond, n_qoi)
            array of the electric field to compute the r2 factor for, e.g. (e_mag, e_norm, e_tan)
    n_samples : int, default=100
        Number of data points to generate discrete mep and e curves

    Returns
    -------
    r2: nparray of float [n_roi, n_datasets]
        R^2 for each element in elm_idx_list
    """

    def cartesian_product(*arrays):
        """
        Fast implementation to get cartesian product of two arrays.

        cartesian_product([a,b,c],[2,3]) =
             [a, 2
              a, 3
              b, 2
              b, 3
              c, 2
              c, 3]
        """
        la = len(arrays)
        dtype = np.result_type(*arrays)
        arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
        for i, a in enumerate(np.ix_(*arrays)):
            arr[..., i] = a
        return arr.reshape(-1, la)

    n_eqoi = e.shape[2]
    n_cond = e.shape[1]
    n_elm = e.shape[0]
    assert n_cond == len(mep_lst)
    mep_params = np.array(mep_params).flatten()
    mep_params_cond = []
    start_idx = 0
    for i_cond in range(n_cond):
        mep_params_cond.append(mep_params[start_idx:(start_idx + mep_lst[i_cond].popt.size)])
        start_idx = start_idx + mep_lst[i_cond].popt.size

    del start_idx

    intensities = []
    amplitudes = []

    reg_r2 = np.empty((n_elm, n_eqoi))

    # get amplitudes from fitted meps
    for i_cond in range(n_cond):
        intensities.append(np.linspace(mep_lst[i_cond].x_limits[0], mep_lst[i_cond].x_limits[1], n_samples))
        amplitudes.append(mep_lst[i_cond].eval(intensities[-1], mep_params_cond[i_cond]))
        # intensities_min.append(mep_lst[i_cond].x_limits[0])
        # intensities_max.append(mep_lst[i_cond].x_limits[1])
    amplitudes = np.array(amplitudes).flatten()

    for qoi_idx in range(n_eqoi):
        # t_q = time.time()
        x = pd.DataFrame()
        index_shift = 0

        for mep_i, mep_lst in enumerate(mep_lst):
            # condition wise, as we stimulated with different intensities per conditions

            # for each element in roi, one datapoint for each zap.
            current = cartesian_product(e[:, mep_i, qoi_idx], intensities[mep_i])

            # index is iteration of zaps over all conditions
            index = cartesian_product(e[:, mep_i, qoi_idx], np.arange(n_samples))[:, 1]
            index += index_shift
            index_shift = index[-1] + 1

            # el is range(n_elements) * n_zaps_in_condition
            el_idx = np.repeat(np.arange(e.shape[0]), n_samples)

            # intensity * e
            e_zap = np.multiply(current[:, 0], current[:, 1])

            # put all together
            x_cond = pd.DataFrame(data={"index": index.astype(int),
                                        "el": el_idx,
                                        "e": e_zap})
            # amplitudes = np.append(amplitudes, mep_lst.mep)
            # "current": current[:, 1],
            # "mep": mep[:,1]})

            # x_cond['condition'] = mep_i
            x = x.append(x_cond)
        # x.shape is now (n_zaps*n_elms, 3)

        # reshape to (n_zaps, n_elms)
        x = x.pivot(index="index", columns="el", values="e")  # this is pretty slow

        do_reg_poly = False
        do_reg_linear = True

        # reg = Ridge(alpha=alpha)
        reg = LinearRegression(normalize=True)
        if do_reg_poly:
            raise NotImplementedError

        elif do_reg_linear:
            # Do one regression per element.
            r_t = time.time()

            def get_score(x_i):
                """Helper function do be used by pd.apply() to speed up things.

                Params:
                -------
                x_i: pd.Series
                 Column with e for a single elm.

                Returns:
                --------
                r2 for amplitudes ~ E
                """
                # x_i = x_i.reshape(-1, 1)
                reg.fit(x_i.reshape(-1, 1), amplitudes)
                return reg.score(x_i.reshape(-1, 1), amplitudes)

            scores = x.apply(get_score, axis=0, raw=True)
            # coefs = [get_score(x.iloc[:, el_idx]) for el_idx in range(n_elm)]
            print("all_reg: {}".format(time.time() - r_t))

        reg_r2[:, qoi_idx] = np.array(scores)
        # data.append(data_qoi_tmp)

        # print "qoi {}: {}".format(qoi_idx, time.time() - t_q)

    return reg_r2


def logistic_regression():
    """
    Some ideas on how to improve regression approach

    1. De-log data

    Data range has to be transformed to a reasonable range. For a full sigmoid, -10:10 looks ok

        sig <- function(z) {
          return( 1 / (1 + exp(-z)))
        }

        desig <- function(x) {
          return(- log((1/x) - 1))
        }

    This might be a reasonable fast approach, but the parameter range has to be estimated. Maybe remove some outliters?

    2. fit logistic regression to raw data
    scipy.optimize provides fit_curve(), which does OLS-ish fitting to a given function
    https://stackoverflow.com/questions/54376900/fit-sigmoid-curve-in-python

    I expect this to be rather slow.

    3. Use the sklearn logistic_regression classifyer and access raw fit data
    The logistic_regression is implemented as a classifyer, maybe it's possible to use it's regression fit results.
    Implementation should be pretty fast.

    """
    raise NotImplementedError


def init(l, zap_lists, res_fn):
    """
    Pool init function to use with regression_nl_hdf5_single_core_write

    Parameters
    ----------
    l : multiprocessing.Lock()
    zap_lists : list of list of int
        Which zaps to compute.
    res_fn : str
        .hdf5 fn
    """

    global lock, z, fn
    lock = l
    z = zap_lists
    fn = res_fn
