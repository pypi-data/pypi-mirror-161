__package__ = "pynibs"

import os
import copy
import math
import h5py
import shutil
import random
import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import pynibs

from scipy.spatial import Delaunay

from collections import OrderedDict


def get_coil_dipole_pos(coil_fn, matsimnibs):
    """
    Apply transformation to coil dipoles and return position.

    Parameters
    ----------
    coil_fn : str
        Filename of coil .ccd file
    matsimnibs : np.ndarray of float
        Transformation matrix

    Returns
    -------
    dipoles_pos : nparray [N x 3]
        Cartesian coordinates (x, y, z) of coil magnetic dipoles

    """

    if coil_fn[-3:] == "nii":
        coil_fn = coil_fn[:-3] + "ccd"
    coil_data = np.genfromtxt(coil_fn, delimiter=' ', skip_header=3)
    coil_dipoles = coil_data[:, 0:3]
    coil_dipoles *= 1e3
    coil_dipoles = np.hstack([coil_dipoles, np.ones((coil_dipoles.shape[0], 1))])

    return matsimnibs.dot(coil_dipoles.T).T[:, :3]


def check_coil_position(points, hull):
    """
    Check if magnetic dipoles are lying inside head region

    Parameters
    ----------
    points : np.ndarray of float [N_points x 3]
        Coordinates (x,y,z) of magnetic dipoles
    hull : Delaunay object or np.ndarray of float [N_surface_points x 3]
        Head surface data

    Returns
    -------
    valid : bool
        Validity of coil position
        TRUE: valid
        FALSE: unvalid
    """

    # make Delaunay grid if not already passed
    if not isinstance(hull, Delaunay):
        hull = Delaunay(hull)

    # filter out points which are outside bounding box to save some time
    bounds = [np.min(hull.points), np.max(hull.points)]
    points_inside = np.logical_and((points > bounds[0]).all(axis=1),
                                   (points < bounds[1]).all(axis=1))

    # test if points are inside (True)
    inside = hull.find_simplex(points[points_inside]) >= 0
    valid = not (inside.any())

    return valid


def calc_coil_transformation_matrix(LOC_mean, ORI_mean, LOC_var, ORI_var, V):
    """
    Calculate the modified coil transformation matrix needed for simnibs based on location and orientation
    variations observed in the framework of uncertainty analysis

    Parameters
    ----------
    LOC_mean : np.ndarray of float [3]
        Mean location of TMS coil
    ORI_mean : np.ndarray of float [3 x 3]
        Mean orientations of TMS coil

        .. math::
            \\begin{bmatrix}
            | & | & | \\\\
            x & y & z \\\\
            | & | & | \\\\
            \\end{bmatrix}

    LOC_var : nparray of float [3]
        Location variation in normalized space (dx', dy', dz'), i.e. zero mean and projected on principal axes
    ORI_var : nparray of float [3]
        Orientation variation expressed in Euler angles [alpha, beta, gamma] in deg
    V : nparray of float [3x3]
        V-matrix containing the eigenvectors from  _,_,V = numpy.linalg.svd

    Returns
    -------
    mat : nparray of float [4 x 4]
        Transformation matrix containing 3 axis and 1 location vector:

        .. math::
            \\begin{bmatrix}
            | & | & | &  |   \\\\
            x & y & z & pos  \\\\
            | & | & | &  |   \\\\
            0 & 0 & 0 &  1   \\\\
            \\end{bmatrix}
    """

    # calculate rotation matrix for angle variation (angle_var in deg)
    rotation_matrix = pynibs.euler_angles_to_rotation_matrix(ORI_var * np.pi / 180.)

    # determine new orientation
    ori = np.dot(ORI_mean, rotation_matrix)

    # determine new location by retransforming from normalized space to regular space
    locations = np.dot(LOC_var, V) + LOC_mean

    # concatenate results
    mat = np.hstack((ori, locations[:, np.newaxis]))
    mat = np.vstack((mat, [0, 0, 0, 1]))

    return mat


def calc_coil_position_pdf(fn_rescon=None, fn_simpos=None, fn_exp=None, orientation='quaternions',
                           folder_pdfplots=None):
    """
    Determines the probability density functions of the transformed coil position (x', y', z') and quaternions of
    the coil orientations (x'', y'', z'')

    Parameters
    ----------
    fn_rescon : str
        Filename of the results file from TMS experiments (results_conditions.csv)
    fn_simpos : str
        Filename of the positions and orientation from TMS experiments (simPos.csv)
    fn_exp : str
        Filename of experimental.csv file from experiments
    orientation: str
        Type of orientation estimation: 'quaternions' or 'euler'
    folder_pdfplots : str
        Folder, where the plots of the fitted pdfs are saved (omitted if not provided)

    Returns
    -------
    pdf_paras_location : list of list of np.ndarrays [n_conditions]
        Pdf parameters (limits and shape) of the coil position for x', y', and z' for each:

            - beta_paras ... [p, q, a, b] (2 shape parameters and limits)
            - moments    ... [data_mean, data_std, beta_mean, beta_std]
            - p_value    ... p-value of the Kolmogorov Smirnov test
            - uni_paras  ... [a, b] (limits)
    pdf_paras_orientation_euler : list of np.ndarray [n_conditions]
        Pdf parameters (limits and shape) of the coil orientation Psi, Theta, and Phi for each:

            - beta_paras ... [p, q, a, b] (2 shape parameters and limits)
            - moments    ... [data_mean, data_std, beta_mean, beta_std]
            - p_value    ... p-value of the Kolmogorov Smirnov test
            - uni_paras  ... [a, b] (limits)
    OP_mean : List of [3 x 4] np.ndarray [n_conditions]
        List of mean coil position and orientation for different conditions (global coordinate system)

        .. math::
            \\begin{bmatrix}
            |  &   |   &   |   &  |   \\\\
            ori_x & ori_y & ori_z & pos  \\\\
            |  &   |   &   |   &  |   \\\\
            \\end{bmatrix}

    OP_zeromean : list of [3 x 4 x n_con_each] np.ndarray [n_conditions]
        List over conditions containing zero-mean coil orientations and positions
    V : list of [3 x 3] np.ndarrays [n_conditions]
        Transformation matrix of coil positions from global coordinate system to transformed coordinate system
    P_transform : list of np.ndarray [n_conditions]
        List over conditions containing transformed coil positions [x', y', z'] of all stimulations
        (zero-mean, rotated by SVD)
    quaternions : list of np.ndarray [n_conditions]
        List over conditions containing imaginary part of quaternions [x'', y'', z''] of all stimulations
    """
    import pygpc

    if folder_pdfplots is not None:
        make_pdf_plot = True
    else:
        make_pdf_plot = False
        folder_pdfplots = ''

    if fn_rescon and fn_simpos:
        positions_all, conditions, position_list, _, _ = pynibs.read_exp_stimulations(fn_rescon, fn_simpos)

        # sort POSITIONS according to CONDITIONS, idx_con is alphabetically sorted, first index of condition[*]
        # appeareance
        conditions_unique, idx_con, n_con_each = np.unique(conditions,
                                                           return_index=True,
                                                           return_inverse=False,
                                                           return_counts=True)

        idx_con_sort = np.argsort(idx_con)
        conditions_unique = conditions_unique[idx_con_sort]  # conditions_unique is ordered like experimental data
        n_con_each = n_con_each[idx_con_sort]
        n_condition = len(conditions_unique)
        n_zaps = len(positions_all)

        pos_idx = 0
        k = 0

        # Orientation and position tensors (list over conditions containing arrays of [3 x 4 x n_con_each])
        op = [np.zeros((3, 4, n_con_each[i])) for i in range(n_condition)]

        # read data from global position_list
        for i in range(n_condition):
            while position_list[pos_idx][len(position_list[0]) - 3] == conditions_unique[i]:
                op[i][:, :, k] = np.array(positions_all[pos_idx])[0:3, 0:4]
                pos_idx = pos_idx + 1
                k = k + 1
                if pos_idx == n_zaps:
                    break
            k = 0

        # determine matrix of mean location and orientation (list over conditions containing arrays of [3 x 4])
        op_mean = [np.mean(op[i], axis=2) for i in range(n_condition)]

    elif fn_exp:
        exp = pynibs.read_csv(fn_exp)
        exp_cond = pynibs.sort_by_condition(exp)

        conditions_unique = [exp_cond[i_cond]['condition'][0] for i_cond in range(len(exp_cond))]

        n_con_each = [len(e['condition']) for e in exp_cond]
        n_condition = len(exp_cond)

        # Orientation and position tensors (list over conditions containing arrays of [3 x 4 x n_con_each])
        op = [np.zeros((3, 4, n_con_each[i])) for i in range(n_condition)]

        for i in range(n_condition):
            for k in range(n_con_each[i]):
                op[i][:, :, k] = exp_cond[i]['coil_mean_matrix'][k][0:3, :]

        # determine matrix of mean location and orientation (list over conditions containing arrays of [3 x 4])
        op_mean = [np.mean(op[i], axis=2) for i in range(n_condition)]

    else:
        raise AssertionError('Please provide experiment.csv or results_condition.csv and simpos.csv files!')

    # Initialize arrays
    # cond_0, zap_1                        zap_2
    # [   |      |      |     |  ]         [   |      |      |     |  ]
    # [ ori_x  ori_y  ori_z  pos ]  . . .  [ ori_x  ori_y  ori_z  pos ]  . . .
    # [   |      |      |     |  ]         [   |      |      |     |  ]

    # Orientation and position tensors with zeromean (list over conditions containing arrays of [3 x 4 x n_con_each])
    op_zeromean = [np.zeros((3, 4, n_con_each[i])) for i in range(n_condition)]

    # Transformed coil position in (x', y', z') space (list over conditions containing arrays of [n_con_each x 3])
    p_transform = [0] * n_condition

    # SVD matrices
    u = [0] * n_condition
    s = [0] * n_condition
    v = [0] * n_condition

    # pdf parameters
    pdf_paras_location = [[[] for _ in range(3)] for _ in range(n_condition)]
    pdf_paras_orientation_euler = [[[] for _ in range(3)] for _ in range(n_condition)]
    pos_names = ['xp', 'yp', 'zp']
    orientations = [0] * n_condition

    for i in range(n_condition):

        # shift data by mean
        op_zeromean[i][:, 3, :] = op[i][:, 3, :] - np.tile(op_mean[i][:, 3][:, np.newaxis], (1, n_con_each[i]))
        # OP[i][0:3,3,:] - np.tile(OP_mean[i][:, 3][:, np.newaxis], (1, n_con_each[i]))

        # perform SVD to determine principal axis
        u[i], s[i], v[i] = np.linalg.svd(op_zeromean[i][:, 3, :].T, full_matrices=True)

        # project locations on principal axis
        p_transform[i] = np.dot(op_zeromean[i][:, 3, :].T, v[i].T)

        # rotate coil orientations to mean orientation (zero-mean)
        op_zeromean[i][:, 0:3, :] = np.dot(op[i][:, 0:3, :].transpose(2, 1, 0), op_mean[i][:, 0:3]).transpose(2, 1, 0)

        # Determine quaternions or Euler angles
        orientations[i] = np.zeros((n_con_each[i], 3))
        xlabel, ylabel = '', ''

        for j in range(n_con_each[i]):
            if orientation == 'quaternions':
                orientations[i][j, :] = pynibs.rot_to_quat(op_zeromean[i][:, 0:3, j])[1:]
                ori_names = ['xq', 'yq', 'zq']
                xlabel = ['$x_q$', '$y_q$', '$z_q$']
                ylabel = ['$p(x_q)$', '$p(y_q)$', '$p(z_q)$']

            elif orientation == 'euler':
                orientations[i][j, :] = pynibs.rotation_matrix_to_euler_angles(op_zeromean[i][:, :, j]) * 180.0 / np.pi
                ori_names = ['Psi', 'Theta', 'Phi']
                xlabel = ['$\Psi$', '$\Theta$', '$\Phi$']
                ylabel = ['$p(\Psi)$', '$p(\Theta)$', '$p(\Phi)$']

            else:
                ValueError('Please set orientation parameter to either ''quaternions'' or ''euler''')

        # fit beta pdfs to x', y' and z' locations and orientations
        for j, name in enumerate(pos_names):
            pdf_paras_location[i][j] = pygpc.fit_betapdf(p_transform[i][:, j],
                                                         BETATOL=0.05,
                                                         PUNI=0.9,
                                                         PLOT=make_pdf_plot,
                                                         VISI=0,
                                                         xlabel=xlabel[j],
                                                         ylabel=ylabel[j],
                                                         filename=os.path.join(folder_pdfplots,
                                                                               'POS_' +
                                                                               conditions_unique[i] + '_' +
                                                                               name +
                                                                               '_betafit'))

        for j, name in enumerate(ori_names):
            pdf_paras_orientation_euler[i][j] = pygpc.fit_betapdf(orientations[i][:, j],
                                                                  BETATOL=0.05,
                                                                  PUNI=0.9,
                                                                  PLOT=make_pdf_plot,
                                                                  VISI=0,
                                                                  xlabel=xlabel[j],
                                                                  ylabel=ylabel[j],
                                                                  filename=os.path.join(folder_pdfplots,
                                                                                        'ORI_' +
                                                                                        conditions_unique[i] + '_' +
                                                                                        name +
                                                                                        '_betafit'))

    return pdf_paras_location, pdf_paras_orientation_euler, op_mean, op_zeromean, v, p_transform, orientations


def test_coil_position_gpc(parameters):
    """
    Testing valid coil positions for gPC analysis

    Parameters
    ----------

    Returns
    -------

    """
    from pygpc.RandomParameter import RandomParameter

    # load subject
    subject = pynibs.load_subject(parameters["fn_subject"])

    coil_uncertainty = False
    parameters_random = OrderedDict()

    # extract random parameters
    for p in parameters:
        if isinstance(parameters[p], RandomParameter):
            parameters_random[p] = parameters[p]
            if p in ["x", "y", "z", "psi", "theta", "phi"]:
                coil_uncertainty = True

    # dim = len(parameters_random)

    if coil_uncertainty:

        svd_v = parameters["coil_position_mean"][0:3, 0:3]

        # Loading geometry to create Delaunay object of outer skin surface
        with h5py.File(subject.mesh[parameters["mesh_idx"]]['fn_mesh_hdf5'], 'r') as f:
            points = np.array(f['mesh/nodes/node_coord'])
            node_number_list = np.array(f['mesh/elm/node_number_list'])
            elm_type = np.array(f['mesh/elm/elm_type'])
            regions = np.array(f['mesh/elm/tag1'])
            triangles_regions = regions[elm_type == 2, ] - 1000
            triangles = node_number_list[elm_type == 2, 0:3]

        triangles = triangles[triangles_regions == 5]
        surface_points = pynibs.unique_rows(np.reshape(points[triangles], (3 * triangles.shape[0], 3)))
        limits_scaling_factor = .1

        # Generate Delaunay triangulation object
        dobj = Delaunay(surface_points)

        del points, node_number_list, elm_type, regions, triangles_regions, triangles, surface_points

        # initialize parameter dictionary
        parameters_corr = dict()
        parameters_corr_idx = dict()
        coil_param = ['x', 'y', 'z', 'psi', 'theta', 'phi']

        for i, c in enumerate(coil_param):
            parameters_corr[c] = {'pdf_limits': [0, 0], 'pdf_shape': [0, 0]}
            parameters_corr_idx[i] = c

        # we need to map some indices
        dic_par_name = dict.fromkeys([0, 1, 2], "pdf_paras_location")
        dic_par_name.update(dict.fromkeys([3, 4, 5], "pdf_paras_orientation_euler"))
        dic_limit_id = {0: 0, 2: 1}  # translates from get_invalid_coil_parameters limits id to pdf_paras_* id
        dic_param_id = dict.fromkeys([0, 3], 0)
        dic_param_id.update(dict.fromkeys([1, 4], 1))
        dic_param_id.update(dict.fromkeys([2, 5], 2))

        # Determine bad parameters and correct them
        print(("Checking validity of coil position uncertainty for condition " + parameters["cond"]))
        random.seed(1)

        # gather random variables in parameter dict (constants = 0 = no variation)
        for i_rv, rv in enumerate(parameters_random):
            if rv in coil_param:
                parameters_corr[rv] = {'pdf_limits': parameters_random[rv].pdf_limits,
                                       'pdf_shape': parameters_random[rv].pdf_shape}

        bad_params = get_invalid_coil_parameters(parameters_corr,
                                                 coil_position_mean=parameters["coil_position_mean"],
                                                 svd_v=svd_v,
                                                 del_obj=dobj,
                                                 fn_coil=parameters["fn_coil"])

        # change param limits until no dipoles left inside head
        while bad_params:
            print(" > Invalid parameter found!")
            # several parameters may lead to a bad position
            # take a random parameter from these
            param_id = random.sample(list(range(len(bad_params))), 1)[0]

            # change last bad_params[-1]' limit
            param_to_change_idx = bad_params[param_id][0]
            limit_to_change_idx = dic_limit_id[bad_params[param_id][1]]  # change min or max limit from 3 to 2 limit

            # grab old limits of parameter to change
            limits_old = parameters_corr[parameters_corr_idx[param_to_change_idx]]['pdf_limits']

            # rescale limits (but change only important boundary, min or max)
            factor = (limits_old[1] - limits_old[0]) * limits_scaling_factor
            limits_temp = [limits_old[0] + factor, limits_old[1] - factor]
            limits_new = copy.deepcopy(limits_old)
            limits_new[limit_to_change_idx] = limits_temp[limit_to_change_idx]
            parameters_corr[parameters_corr_idx[param_to_change_idx]]['pdf_limits'] = limits_new

            print((' > Changing pdf_limits of {} from {} -> {}'.format(parameters_corr_idx[param_to_change_idx],
                                                                       limits_old,
                                                                       limits_new)))

            # overwrite old values
            parameters[parameters_corr_idx[param_to_change_idx]].pdf_limits = limits_new

            # repeat dipole check
            bad_params = get_invalid_coil_parameters(parameters_corr,
                                                     coil_position_mean=parameters["coil_position_mean"],
                                                     svd_v=svd_v,
                                                     del_obj=dobj,
                                                     fn_coil=parameters["fn_coil"])

    return parameters


def get_invalid_coil_parameters(param_dict, coil_position_mean, svd_v, del_obj, fn_coil,
                                fn_hdf5_coilpos=None):
    """
    Finds gpc parameter combinations, which place coil dipoles inside subjects head.
    Only endpoints (and midpoints) of the parameter ranges are examined.

    get_invalid_coil_parameters(param_dict, pos_mean, v, del_obj, fn_coil, fn_hdf5_coilpos=None)

    Parameters:
    -----------
    param_dict: dict
        Dictionary containing dictionary with 'limits' and 'pdfshape'
        keys: 'x', 'y', 'z', 'psi', 'theta', 'phi'
    coil_position_mean: nparray [3 x 4]
        Mean coil positions and orientations
    svd_v: nparray [3 x 3]
        SVD matrix V
    del_obj: Delaunay object
        Skin surface (created with scipy.spatial.Delaunay)
    fn_coil: str
        Filename of coil .ccd file
    fn_hdf5_coilpos: str
        Filename of .hdf5 file to save coil_pos in (incl. path and .hdf5 extension)

    Returns:
    --------
    fail_params: list of int
        Index and combination of failed parameter
    """

    # for every condition:
    results = []

    # for i in range(6):
    limits_pos_x = param_dict['x']['limits']
    limits_pos_y = param_dict['y']['limits']
    limits_pos_z = param_dict['z']['limits']
    limits_psi = param_dict['psi']['limits']
    limits_theta = param_dict['theta']['limits']
    limits_phi = param_dict['phi']['limits']

    limits_pos_x = pynibs.add_center(limits_pos_x)
    limits_pos_y = pynibs.add_center(limits_pos_y)
    limits_pos_z = pynibs.add_center(limits_pos_z)
    limits_psi = pynibs.add_center(limits_psi)
    limits_theta = pynibs.add_center(limits_theta)
    limits_phi = pynibs.add_center(limits_phi)

    temp_list = [[0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2]]
    combinations = list(itertools.product(*temp_list))
    del temp_list

    for combination in combinations:

        # create matsimnibs
        loc_var = np.array([limits_pos_x[combination[0]],
                            limits_pos_y[combination[1]],
                            limits_pos_z[combination[2]]])
        ori_var = np.array([limits_psi[combination[3]],
                            limits_theta[combination[4]],
                            limits_phi[combination[5]]])

        mat = calc_coil_transformation_matrix(LOC_mean=coil_position_mean[0:3, 3],
                                              ORI_mean=coil_position_mean[0:3, 0:3],
                                              LOC_var=loc_var,
                                              ORI_var=ori_var,
                                              V=svd_v)

        # get dipole points for coil for actual matsimnibs
        coil_dipoles = get_coil_dipole_pos(fn_coil, mat)

        if fn_hdf5_coilpos:
            with h5py.File(fn_hdf5_coilpos, 'w') as f:
                f.create_dataset("/dipoles/", data=coil_dipoles)

            with open(os.path.splitext(fn_hdf5_coilpos)[0] + ".xdmf", 'w') as f:
                f.write('<?xml version="1.0"?>\n')
                f.write('<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>\n')
                f.write('<Xdmf Version="2.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n')
                f.write('<Domain>\n')

                # one collection grid
                f.write('<Grid\nCollectionType="Spatial"\nGridType="Collection"\nName="Collection">\n')

                f.write('<Grid Name="coil" GridType="Uniform">\n')
                f.write('<Topology NumberOfElements="' + str(len(coil_dipoles)) +
                        '" TopologyType="Polyvertex" Name="Tri">\n')
                f.write('<DataItem Format="XML" Dimensions="' + str(len(coil_dipoles)) + ' 1">\n')
                np.savetxt(f, list(range(len(coil_dipoles))), fmt='%d',
                           delimiter=' ')  # 1 2 3 4 ... N_Points
                f.write('</DataItem>\n')
                f.write('</Topology>\n')

                # nodes
                f.write('<Geometry GeometryType="XYZ">\n')
                f.write('<DataItem Format="HDF" Dimensions="' + str(len(coil_dipoles)) + ' 3">\n')
                f.write(fn_hdf5_coilpos + ':' + '/dipoles\n')
                f.write('</DataItem>\n')
                f.write('</Geometry>\n')

                f.write('</Grid>\n')
                f.write('</Grid>\n')
                f.write('</Domain>\n')
                f.write('</Xdmf>\n')

        # check hull and add to results
        results.append(pynibs.in_hull(coil_dipoles, del_obj))

    # find parameter which drives dipoles into head
    combinations = np.array(combinations)
    fail_params = []
    if np.sum(results) > 0:
        comb_idx = np.where(np.sum(results, axis=1) > 0)[0]
        params_idx = np.where(np.var(combinations[comb_idx], axis=0) ==
                              min(np.var(combinations[comb_idx], axis=0)))[0]
        for param_idx in params_idx:
            comb_idx = comb_idx[combinations[comb_idx, params_idx[0]] != 1]
            fail_params.append((param_idx, combinations[comb_idx, params_idx[0]][0]))

    return fail_params


def create_stimsite_hdf5(fn_exp, fn_hdf, conditions_selected=None, sep="_", merge_sites=False, fix_angles=False,
                         data_dict=None, conditions_ignored=None):
    """
    Reads results_conditions and creates an hdf5/xdmf pair with condition-wise centers of stimulation sites and
    coil directions as data.

    Parameters
    ----------
    fn_exp : str
        Path to results.csv
    fn_hdf : str
        Path where to write file. Gets overridden if already existing
    conditions_selected : str or list of str, Default=None
        List of conditions returned by the function, the others are omitted,
        If None, all conditions are returned
    sep: str, Default: "_"
        Separator between condition label and angle (e.g. M1_0, or M1-0)
    merge_sites : boolean
        If true, only one coil center per site is generated.
    fix_angles : boolean
        rename 22.5 -> 0, 0 -> -45, 67.5 -> 90, 90 -> 135
    data_dict : dict ofnp.ndarray of float [n_stimsites] (optional), default: None
        Dictionary containing data corresponding to the stimulation sites (keys)
    conditions_ignored : str or list of str, Default=None
        Conditions, which are not going to be included in the plot

    Returns
    -------
    <Files> : hdf5/xdmf file pair
        Contains information about condition-wise stimulation sites and coil directions (fn_hdf)

    Example
    -------
    Example::
        pynibs.create_stimsite_hdf5('/data/pt_01756/probands/15484.08/exp/1/experiment_corrected.csv',
                                     '/data/pt_01756/tmp/test', True, True)
    """
    assert not fn_hdf.endswith('/')

    exp = pynibs.read_csv(fn_exp)

    exp_cond = pynibs.sort_by_condition(exp, conditions_selected=conditions_selected)  # []

    # get the unique conditions in the correct order
    conds = [c['condition'][0] for c in exp_cond]

    # remove conds
    conds_temp = []
    exp_cond_temp = []

    if type(conditions_ignored) is not list:
        conditions_ignored = [conditions_ignored]

    for i_c, c in enumerate(conds):
        ignore = False
        for ci in list(conditions_ignored):
            if c == ci:
                ignore = True

        if not ignore:
            conds_temp.append(conds[i_c])
            exp_cond_temp.append(exp_cond[i_c])

    exp_cond = exp_cond_temp
    conds = conds_temp

    # hardcoded row #3 is condition
    cond_idx = np.linspace(0, len(exp_cond), 1)[:, np.newaxis]

    centers = []
    m0 = []
    m1 = []
    m2 = []

    for i_cond in range(len(exp_cond)):
        centers.append(exp_cond[i_cond]['coil_mean_matrix'][0][0:3, 3])
        m0.append(exp_cond[i_cond]['coil_mean_matrix'][0][0:3, 0])
        m1.append(exp_cond[i_cond]['coil_mean_matrix'][0][0:3, 1])
        m2.append(exp_cond[i_cond]['coil_mean_matrix'][0][0:3, 2])

    # split conds to angles and sites: M1_90 -> M1, 90
    angles = np.array([sp.split(sep)[-1] for sp in conds]).astype(np.float)
    sites = np.array([sp.split(sep)[0] for sp in conds])
    sites_unique = np.unique(sites)

    # average the center positions of a stimulation site over all orientations
    if merge_sites:

        # generate sites dict
        centers_sites = dict()

        for site in sites_unique:
            centers_sites[site] = []

        # gather all orientations and put them to the corresponding sites
        for i_cond, site in enumerate(sites):
            centers_sites[site].append(exp_cond[i_cond]['coil_mean_matrix'][0][0:3, 3])

        # determine average position over all orientations for each site
        for site in sites_unique:
            centers_sites[site] = np.mean(np.vstack(centers_sites[site]), axis=0)

        # write it back to centers
        for i_cond, site in enumerate(sites):
            centers[i_cond] = centers_sites[site]

    centers = np.vstack(centers)
    m0 = np.vstack(m0)
    m1 = np.vstack(m1)
    m2 = np.vstack(m2)

    # enumerate sites, as paraview does not plot string array data
    sites_idx = np.array(list(range(len(sites))))[:, np.newaxis]

    angles[angles[:] == 675.] = 67.5
    angles[angles[:] == 225.] = 22.5

    if fix_angles:
        # rename wrong angle names
        angles_cor = np.copy(angles)
        angles_cor[angles == 0] = -45.
        angles_cor[angles == 22.5] = 0.
        angles_cor[angles == 67.5] = 90.
        angles_cor[angles == 90] = 135.
        angles = angles_cor

    # write hdf5 file
    if not fn_hdf.endswith('.hdf5'):
        fn_hdf += '.hdf5'
    f = h5py.File(fn_hdf, 'w')
    f.create_dataset('centers', data=centers.astype(np.float))
    f.create_dataset('m0', data=m0.astype(np.float))
    f.create_dataset('m1', data=m1.astype(np.float))
    f.create_dataset('m2', data=m2.astype(np.float))
    f.create_dataset('cond', data=np.string_(conds))  # this is a string array, not xdmf compatible
    f.create_dataset('cond_idx', data=cond_idx)
    f.create_dataset('angles', data=angles)
    f.create_dataset('sites', data=np.string_(sites))  # this is a string array, not xdmf compatible
    f.create_dataset('sites_idx', data=sites_idx)

    data = None
    if data_dict is not None:
        data = np.zeros((len(list(data_dict.keys())), 1))
        for i_data, cond in enumerate(conds):
            data[i_data, 0] = data_dict[cond]
        f.create_dataset('data', data=data)
    f.close()

    # write .xdmf file
    f = open(fn_hdf[:-4] + 'xdmf', 'w')
    fn_hdf = os.path.basename(fn_hdf)  # relative links

    # header
    f.write('<?xml version="1.0"?>\n')
    f.write('<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>\n')
    f.write('<Xdmf Version="2.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n')
    f.write('<Domain>\n')
    f.write('<Grid\nCollectionType="Spatial"\nGridType="Collection"\nName="Collection">\n')

    # one grid for coil dipole nodes...store data hdf5.
    #######################################################
    f.write('<Grid Name="stimsites" GridType="Uniform">\n')
    f.write('<Topology NumberOfElements="' + str(centers.shape[0]) +
            '" TopologyType="Polyvertex" Name="Tri">\n')
    f.write('<DataItem Format="XML" Dimensions="' + str(centers.shape[0]) + ' 1">\n')
    # f.write(hdf5_fn + ':' + path + '/triangle_number_list\n')
    np.savetxt(f, list(range(centers.shape[0])), fmt='%d', delimiter=' ')  # 1 2 3 4 ... N_Points
    f.write('</DataItem>\n')
    f.write('</Topology>\n')

    # nodes
    f.write('<Geometry GeometryType="XYZ">\n')
    f.write('<DataItem Format="HDF" Dimensions="' + str(centers.shape[0]) + ' 3">\n')
    f.write(fn_hdf + ':' + '/centers\n')
    f.write('</DataItem>\n')
    f.write('</Geometry>\n')

    # data
    # dipole magnitude
    # the 4 vectors
    for i in range(3):
        f.write('<Attribute Name="dir_' + str(i) + '" AttributeType="Vector" Center="Cell">\n')
        f.write('<DataItem Format="HDF" Dimensions="' + str(centers.shape[0]) + ' 3">\n')
        f.write(fn_hdf + ':' + '/m' + str(i) + '\n')
        f.write('</DataItem>\n')
        f.write('</Attribute>\n\n')

    #  angles
    f.write('<Attribute Name="angles" AttributeType="Scalar" Center="Cell">\n')
    f.write('<DataItem Format="HDF" Dimensions="' + str(centers.shape[0]) + ' 1">\n')
    f.write(fn_hdf + ':' + '/angles\n')
    f.write('</DataItem>\n')
    f.write('</Attribute>\n\n')

    #  data
    if data_dict is not None:
        f.write('<Attribute Name="data" AttributeType="Scalar" Center="Cell">\n')
        f.write('<DataItem Format="HDF" Dimensions="' + str(data.shape[0]) + ' 1">\n')
        f.write(fn_hdf + ':' + '/data\n')
        f.write('</DataItem>\n')
        f.write('</Attribute>\n\n')

    # site idx
    f.write('<Attribute Name="sites_idx" AttributeType="Scalar" Center="Cell">\n')
    f.write('<DataItem Format="HDF" Dimensions="' + str(centers.shape[0]) + ' 1">\n')
    f.write(fn_hdf + ':' + '/sites_idx\n')
    f.write('</DataItem>\n')
    f.write('</Attribute>\n\n')

    f.write('</Grid>\n')
    # end coil dipole data

    # footer
    f.write('</Grid>\n')
    f.write('</Domain>\n')
    f.write('</Xdmf>\n')
    f.close()


def create_stimsite_from_list(fn_hdf, poslist, datanames=None, data=None, overwrite=False):
    """This takes a TMSLIST from simnibs and creates a .hdf5 + .xdmf tuple for all positions.

    Centers and coil orientations are written so disk.

    Parameters
    -----------
    fn_hdf: basestring
        Filename for the .hdf5 file. The .xdmf is saved with the same basename.
        Folder should already exist.

    datanames: basestring or list of basestring
        Dataset names for _data_. Default: None.

    data: np.ndarray
        Dataset array with (len(poslist.pos), len(datanames()). Default: None.

    poslist: TMSLIST object (simnibs.simulation.simstruct.TMSLIST)
        poslist.pos[*].matsimnibs have to be set.

    overwrite : boolean
        Overwrite existing files. Default:  False.
    """

    centers = []
    m0 = []
    m1 = []
    m2 = []

    for lst in poslist:
        # assert pos.matsimnibs is not None
        centers.append(lst[0:3, 3])
        m0.append(lst[0:3, 0])
        m1.append(lst[0:3, 1])
        m2.append(lst[0:3, 2])

    centers = np.vstack(centers)
    m0 = np.vstack(m0)
    m1 = np.vstack(m1)
    m2 = np.vstack(m2)

    write_coil_pos_hdf5(fn_hdf, centers, m0, m1, m2, datanames=datanames, data=data, overwrite=overwrite)


def create_stimsite_from_tmslist(fn_hdf, poslist, datanames=None, data=None, overwrite=False):
    """This takes a TMSLIST from simnibs and creates a .hdf5 + .xdmf tuple for all positions.

    Centers and coil orientations are written so disk.

    Parameters
    -----------
    fn_hdf: basestring
        Filename for the .hdf5 file. The .xdmf is saved with the same basename.
        Folder should already exist.

    datanames: basestring or list of basestring
        Dataset names for _data_. Default: None.

    data: np.ndarray
        Dataset array with (len(poslist.pos), len(datanames()). Default: None.

    poslist: TMSLIST object (simnibs.simulation.simstruct.TMSLIST)
        poslist.pos[*].matsimnibs have to be set.

    overwrite : boolean
        Overwrite existing files. Default:  False.
    """

    centers = []
    m0 = []
    m1 = []
    m2 = []
    assert poslist.pos
    for pos in poslist.pos:
        assert pos.matsimnibs is not None
        pos.matsimnibs = np.array(pos.matsimnibs)
        centers.append(pos.matsimnibs[0:3, 3])
        m0.append(pos.matsimnibs[0:3, 0])
        m1.append(pos.matsimnibs[0:3, 1])
        m2.append(pos.matsimnibs[0:3, 2])

    centers = np.vstack(centers)
    m0 = np.vstack(m0)
    m1 = np.vstack(m1)
    m2 = np.vstack(m2)

    write_coil_pos_hdf5(fn_hdf, centers, m0, m1, m2, datanames=datanames, data=data, overwrite=overwrite)


def create_stimsite_from_exp_hdf5(fn_exp, fn_hdf, datanames=None, data=None, overwrite=False):
    """
    This takes an experiment.hdf5 file and creates an .hdf5 + .xdmf tuple for all coil positions for visualization.

    Parameters
    -----------
    fn_exp : str
        Path to experiment.hdf5
    fn_hdf : basestring
        Filename for the resulting .hdf5 file. The .xdmf is saved with the same basename.
        Folder should already exist.
    datanames : basestring or list of basestring
        Dataset names for _data_. Default: None.
    data : np.ndarray
        Dataset array with (len(poslist.pos), len(datanames()). Default: None.
    overwrite : boolean
        Overwrite existing files. Default:  False.
    """

    df_stim = pd.read_hdf(fn_exp, "stim_data")

    matsimnibs = np.zeros((4, 4, df_stim.shape[0]))

    for i in range(df_stim.shape[0]):
        matsimnibs[:, :, i] = df_stim["coil_mean"].iloc[i]

    create_stimsite_from_matsimnibs(fn_hdf=fn_hdf,
                                    matsimnibs=matsimnibs,
                                    datanames=datanames,
                                    data=data,
                                    overwrite=overwrite)


def create_stimsite_from_matsimnibs(fn_hdf, matsimnibs, datanames=None, data=None, overwrite=False):
    """
    This takes a matsimnibs array and creates an .hdf5 + .xdmf tuple for all coil positions for visualization.

    Centers and coil orientations are written disk.

    Parameters
    -----------
    fn_hdf: string
        Filename for the .hdf5 file. The .xdmf is saved with the same basename.
        Folder should already exist.
    matsimnibs: np.ndarray
        (4, 4, n_pos)
        Matsimnibs matrices containing the coil orientation (x,y,z) and position (p)
            [ |  |  |  | ]
            [ x  y  z  p ]
            [ |  |  |  | ]
            [ 0  0  0  1 ]
    datanames: string or list of string
        Dataset names for _data_. Default: None.
    data: np.ndarray, optional
        (len(poslist.pos), len(datanames).
    overwrite : boolean, default: False
        Overwrite existing files.
    """
    n_pos = matsimnibs.shape[2]
    centers = np.zeros((n_pos, 3))
    m0 = np.zeros((n_pos, 3))
    m1 = np.zeros((n_pos, 3))
    m2 = np.zeros((n_pos, 3))

    for i in range(matsimnibs.shape[2]):
        centers[i, :] = matsimnibs[0:3, 3, i]
        m0[i, :] = matsimnibs[0:3, 0, i]
        m1[i, :] = matsimnibs[0:3, 1, i]
        m2[i, :] = matsimnibs[0:3, 2, i]

    write_coil_pos_hdf5(fn_hdf, centers, m0, m1, m2, datanames=datanames, data=data, overwrite=overwrite)


def write_coil_pos_hdf5(fn_hdf, centers, m0, m1, m2, datanames=None, data=None, overwrite=False):
    """
    Creates a .hdf5 + .xdmf file for all coil positions.

    Centers and coil orientations are written to disk.

    Parameters
    -----------
    fn_hdf : basestring
        Filename for the .hdf5 file. The .xdmf is saved with the same basename.
        Folder should already exist.
    centers : np.ndarray of float [n_pos x 3]
        Coil positions
    m0 : np.ndarray of float [n_pos x 3]
        Coil orientation x-axis (looking at the active (patient) side of the coil pointing to the right)
    m1 : np.ndarray of float [n_pos x 3]
        Coil orientation y-axis (looking at the active (patient) side of the coil pointing up away from the handle)
    m2 : np.ndarray of float [n_pos x 3]
        Coil orientation z-axis (looking at the active (patient) side of the coil pointing to the patient)
    datanames : basestring or list of basestring [n_data]
        Dataset names for _data_. Default: None.
    data : np.ndarray [n_pos, n_data]
        Dataset array with (len(poslist.pos), len(datanames()). Default: None.
    overwrite : boolean
        Overwrite existing files. Default: False.
    """
    n_pos = centers.shape[0]

    if data is not None:
        if datanames is None:
            raise ValueError("Provide datanames= with data= argument.")

        if data.ndim == 1:
            data = data[:, np.newaxis]

        assert data.shape == (n_pos, len(datanames))

    if type(datanames) == str:
        datanames = [datanames]

    m0_reshaped = np.hstack((m0, np.zeros((n_pos, 1)))).T[:, np.newaxis, :]
    m1_reshaped = np.hstack((m1, np.zeros((n_pos, 1)))).T[:, np.newaxis, :]
    m2_reshaped = np.hstack((m2, np.zeros((n_pos, 1)))).T[:, np.newaxis, :]
    centers_reshaped = np.hstack((centers, np.ones((n_pos, 1)))).T[:, np.newaxis, :]

    matsimnibs = np.concatenate((m0_reshaped, m1_reshaped, m2_reshaped, centers_reshaped), axis=1)

    # write hdf5 file
    if not fn_hdf.endswith('.hdf5'):
        fn_hdf += '.hdf5'
    if os.path.exists(fn_hdf) and not overwrite:
        raise OSError(fn_hdf + " already exists. Set overwrite flag for create_stimsite_from_poslist.")

    f = h5py.File(fn_hdf, 'w')
    f.create_dataset('centers', data=centers.astype(np.float))
    f.create_dataset('m0', data=m0.astype(np.float))
    f.create_dataset('m1', data=m1.astype(np.float))
    f.create_dataset('m2', data=m2.astype(np.float))
    f.create_dataset("matsimnibs", data=matsimnibs)

    if data is not None:
        for i, col in enumerate(data.T):
            f.create_dataset('/data/' + datanames[i], data=col)
    f.close()

    # write .xdmf file
    f = open(fn_hdf[:-4] + 'xdmf', 'w')
    fn_hdf = os.path.basename(fn_hdf)  # relative links

    # header
    f.write('<?xml version="1.0"?>\n')
    f.write('<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>\n')
    f.write('<Xdmf Version="2.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n')
    f.write('<Domain>\n')
    f.write('<Grid\nCollectionType="Spatial"\nGridType="Collection"\nName="Collection">\n')

    # one grid for coil dipole nodes...store data hdf5.
    #######################################################
    f.write('<Grid Name="stimsites" GridType="Uniform">\n')
    f.write('<Topology NumberOfElements="' + str(centers.shape[0]) +
            '" TopologyType="Polyvertex" Name="Tri">\n')
    f.write('<DataItem Format="XML" Dimensions="' + str(centers.shape[0]) + ' 1">\n')
    np.savetxt(f, list(range(centers.shape[0])), fmt='%d', delimiter=' ')  # 1 2 3 4 ... N_Points
    f.write('</DataItem>\n')
    f.write('</Topology>\n')

    # nodes
    f.write('<Geometry GeometryType="XYZ">\n')
    f.write('<DataItem Format="HDF" Dimensions="' + str(centers.shape[0]) + ' 3">\n')
    f.write(fn_hdf + ':' + '/centers\n')
    f.write('</DataItem>\n')
    f.write('</Geometry>\n')

    # data
    # dipole magnitude
    # the 4 vectors
    for i in range(3):
        f.write('<Attribute Name="dir_' + str(i) + '" AttributeType="Vector" Center="Cell">\n')
        f.write('<DataItem Format="HDF" Dimensions="' + str(centers.shape[0]) + ' 3">\n')
        f.write(fn_hdf + ':' + '/m' + str(i) + '\n')
        f.write('</DataItem>\n')
        f.write('</Attribute>\n\n')

    if data is not None:
        for i, col in enumerate(data.T):
            f.write(f'<Attribute Name="{datanames[i]}" AttributeType="Scalar" Center="Cell">\n')
            f.write('<DataItem Format="HDF" Dimensions="' + str(centers.shape[0]) + ' 1">\n')
            f.write(fn_hdf + f':/data/{datanames[i]}\n')
            f.write('</DataItem>\n')
            f.write('</Attribute>\n\n')

    f.write('</Grid>\n')
    # end coil dipole data

    # footer
    f.write('</Grid>\n')
    f.write('</Domain>\n')
    f.write('</Xdmf>\n')
    f.close()


def sort_opt_coil_positions(fn_coil_pos_opt, fn_coil_pos, fn_out_hdf5=None, root_path="/0/0/", verbose=False,
                            print_output=False):
    """
    Sorts coil positions according to Traveling Salesman problem

    Parameters
    ----------
    fn_coil_pos_opt : str
        Name of .hdf5 file containing the optimal coil position indices
    fn_coil_pos : str
        Name of .hdf5 file containing the matsimnibs matrices of all coil positions
    fn_out_hdf5 : str
        Name of output .hdf5 file (will be saved in the same format as fn_coil_pos_opt)
    verbose : bool, optional, default: False
        Print output messages
    print_output : bool or str, optional, default: False
        Print output image as .png file showing optimal path

    Returns
    -------
    <file> .hdf5 file containing the sorted optimal coil position indices
    """

    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp

    if verbose:
        print(f"Loading optimal coil indices from file: {fn_coil_pos_opt}")

    with h5py.File(fn_coil_pos_opt, "r") as f:
        coil_pos_idx = f[root_path + "coil_seq"][:, 0].astype(int)
        goal_fun_val = f[root_path + "coil_seq"][:, 1]
        intensities_opt = f[root_path + "coil_seq"][:, 2]

    if verbose:
        print(f"Loading all coil positions from file: {fn_coil_pos}")

    with h5py.File(fn_coil_pos, "r") as f:
        matsimnibs = f["matsimnibs"][:]

    matsimnibs_opt = np.zeros((4, 4, len(coil_pos_idx)))

    for i, idx in enumerate(coil_pos_idx):
        matsimnibs_opt[:, :, i] = matsimnibs[:, :, idx]

    opt_idx_sort = np.argsort(matsimnibs_opt[0, 3, :])
    matsimnibs_opt = matsimnibs_opt[:, :, opt_idx_sort]

    unique_idx = np.zeros(len(opt_idx_sort))

    pos_unique = np.unique(matsimnibs_opt[0, 3, :])

    for i, pos in enumerate(pos_unique):
        unique_idx[matsimnibs_opt[0, 3, :] == pos] = i

    if verbose:
        print(f"Sorting same positions according to angles ...")

    matsimnibs_opt_sorted_pert = np.zeros(matsimnibs_opt.shape)
    matsimnibs_opt_sorted = np.zeros(matsimnibs_opt.shape)

    for i in unique_idx:
        pos = matsimnibs_opt[:, :, unique_idx == i]
        angles = np.zeros(pos.shape[2])

        if pos.shape[2] > 1:
            for i_p in range(pos.shape[2]):
                dot_prod = np.dot(pos[:3, 0, 0], pos[:3, 0, i_p])
                if dot_prod > 1:
                    dot_prod = 1
                elif dot_prod < -1:
                    dot_prod = -1
                angles[i_p] = np.arccos(dot_prod) / np.pi * 180

            angles_sort_idx = np.argsort(angles)
            pos_sorted = pos[:, :, angles_sort_idx]
        else:
            pos_sorted = pos

        matsimnibs_opt_sorted[:, :, unique_idx == i] = pos_sorted
        matsimnibs_opt_sorted_pert[:, :, unique_idx == i] = pos_sorted
        matsimnibs_opt_sorted_pert[0, 3, unique_idx == i] += np.arange(len(angles)) * 1e-2

    coords = matsimnibs_opt_sorted_pert[:3, 3, :].transpose()
    coords_list = [tuple(c) for c in coords]

    def compute_euclidean_distance_matrix(locations):
        """Creates callback to return distance between points."""
        distances = {}
        for from_counter, from_node in enumerate(locations):
            distances[from_counter] = {}
            for to_counter, to_node in enumerate(locations):
                if from_counter == to_counter:
                    distances[from_counter][to_counter] = 0
                else:
                    # Euclidean distance
                    distances[from_counter][to_counter] = (int(
                            math.hypot((from_node[0] - to_node[0]),
                                       (from_node[1] - to_node[1]))))
        return distances

    def get_routes(s, r, m):
        """Get vehicle routes from a solution and store them in an array."""
        # Get vehicle routes and store them in a two-dimensional array whose
        # i,j entry is the jth location visited by vehicle i along its route.
        routes_l = []
        for route_nbr in range(r.vehicles()):
            index = r.Start(route_nbr)
            route = [m.IndexToNode(index)]
            while not r.IsEnd(index):
                index = s.Value(r.NextVar(index))
                route.append(m.IndexToNode(index))
            routes_l.append(route)

        return routes_l

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    # Instantiate the data problem.
    data = {}
    # Locations in block units
    data['locations'] = coords_list
    data['num_vehicles'] = 1
    data['depot'] = 0

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    distance_matrix = compute_euclidean_distance_matrix(data['locations'])
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    # Solve the problem.
    if verbose:
        print(f"Determine optimal order of sequence ...")
    solution = routing.SolveWithParameters(search_parameters)

    routes = np.array(get_routes(solution, routing, manager)[0])[:-1]

    matsimnibs_opt_sorted = matsimnibs_opt_sorted[:, :, routes]

    idx_global_sorted = np.zeros(len(goal_fun_val))
    goal_fun_val_sorted = np.zeros(len(goal_fun_val))
    intensities_opt_sorted = np.zeros(len(intensities_opt))

    for i in range(len(idx_global_sorted)):
        for j in range(matsimnibs.shape[2]):
            if (matsimnibs[:, :, j] == matsimnibs_opt_sorted[:, :, i]).all():
                idx_global_sorted[i] = int(j)
        goal_fun_val_sorted[i] = goal_fun_val[np.where(int(idx_global_sorted[i]) == coil_pos_idx)[0][0]]
        intensities_opt_sorted[i] = intensities_opt[np.where(int(idx_global_sorted[i]) == coil_pos_idx)[0][0]]

    # overwrite input file if no output file given
    outpath = fn_coil_pos_opt
    if fn_out_hdf5 is not None:
        outpath = fn_out_hdf5
        shutil.copy(fn_coil_pos_opt, fn_out_hdf5)

    if verbose:
        print(f"Saving output to: {outpath}")

    with h5py.File(outpath, "a") as f:
        f[root_path + "coil_seq"][:] = np.vstack((idx_global_sorted, goal_fun_val_sorted,
                                                  intensities_opt_sorted)).transpose()

    if print_output:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(coords[routes, 0], coords[routes, 1], coords[routes, 2], s=intensities_opt_sorted * 11, c="k")
        ax.plot3D(coords[routes, 0], coords[routes, 1], coords[routes, 2])
        ax.set_xlabel("x in mm")
        ax.set_ylabel("y in mm")
        ax.set_zlabel("z in mm")
        ax.view_init(elev=40., azim=230)
        plt.savefig(print_output, dpi=600, transparent=True)

# def check_valid_coil_position_uncertainty(self, problem, coil_position_mean, svd_v):
#     """ Tests extreme cases of possible coil positions if dipoles are located inside the head.
#     If an invalid position is found, the parameter space is reduced by shrinking the limits.
#
#     Parameters:
#     -----------
#     problem : Problem class instance
#         GPC problem under investigation
#     coil_position_mean : np.ndarray of float [3 x 4]
#         Mean coil position matrix containing the 3 orientation vectors and the location [ori_x, ori_y, ori_z, loc]
#     svd_v: np.ndarray of float [3 x 3]
#         List containing the SVD matrices V for each condition (principal axes of orientation)
#
#     Returns:
#     --------
#     param_dict: list of dict [n_conditions]
#         List of dictionaries containing dictionary with corrected 'limits' and 'pdfshape'
#         keys: 'x', 'y', 'z', 'psi', 'theta', 'phi'
#    """
#
#     # Loading geometry to create Delaunay object of outer skin surface
#     with h5py.File(self.subject.mesh[self.mesh_idx]['fn_mesh_hdf5'], 'r') as f:
#         points = np.array(f['mesh/nodes/node_coord'])
#         node_number_list = np.array(f['mesh/elm/node_number_list'])
#         elm_type = np.array(f['mesh/elm/elm_type'])
#         regions = np.array(f['mesh/elm/tag1'])
#         triangles_regions = regions[elm_type == 2, ] - 1000
#         triangles = node_number_list[elm_type == 2, 0:3]
#
#     triangles = triangles[triangles_regions == 5]
#     surface_points = pynibs.pynibs.unique_rows(np.reshape(points[triangles], (3 * triangles.shape[0], 3)))
#     limits_scaling_factor = .1
#
#     # Generate Delaunay triangulation object
#     dobj = Delaunay(surface_points)
#
#     del points, node_number_list, elm_type, regions, triangles_regions, triangles, surface_points
#
#     # initialize parameter dictionary
#     param_dict = dict()
#     param_dict_idx = dict()
#     coil_param = ['x', 'y', 'z', 'psi', 'theta', 'phi']
#
#     for i, c in enumerate(coil_param):
#         param_dict[c] = {'pdf_limits': [0, 0], 'pdf_shape': [0, 0]}
#         param_dict_idx[i] = c
#
#     # we need to map some indices
#     dic_par_name = dict.fromkeys([0, 1, 2], "pdf_paras_location")
#     dic_par_name.update(dict.fromkeys([3, 4, 5], "pdf_paras_orientation_euler"))
#     dic_limit_id = {0: 0, 2: 1}  # translates from get_invalid_coil_parameters limits id to pdf_paras_* id
#     dic_param_id = dict.fromkeys([0, 3], 0)
#     dic_param_id.update(dict.fromkeys([1, 4], 1))
#     dic_param_id.update(dict.fromkeys([2, 5], 2))
#
#     # Determine bad parameters and correct them
#     print("Checking validity of coil position uncertainty for condition " + self.cond)
#     random.seed(1)
#
#     # gather random variables in parameter dict (constants = 0 = no variation)
#     for i_rv, rv in enumerate(problem.random_vars):
#         if rv in coil_param:
#             param_dict[rv] = {'pdf_limits': problem.parameters[rv].pdf_limits,
#                               'pdf_shape': problem.parameters[rv].pdf_shape}
#
#     bad_params = self.get_invalid_coil_parameters(param_dict,
#                                                   coil_position_mean=coil_position_mean,
#                                                   svd_v=svd_v,
#                                                   del_obj=dobj,
#                                                   fn_coil=self.fn_coil)
#
#     # change param limits until no dipoles left inside head
#     while bad_params:
#         print(" > Invalid parameter found!")
#         # several parameters may lead to a bad position
#         # take a random parameter from these
#         param_id = random.sample(range(len(bad_params)), 1)[0]
#
#         # change last bad_params[-1]' limit
#         param_to_change_idx = bad_params[param_id][0]
#         limit_to_change_idx = dic_limit_id[bad_params[param_id][1]]  # change min or max limit from 3 to 2 limit
#
#         # grab old limits of parameter to change
#         limits_old = param_dict[param_dict_idx[param_to_change_idx]]['pdf_limits']
#
#         # rescale limits (but change only important boundary, min or max)
#         factor = (limits_old[1] - limits_old[0]) * limits_scaling_factor
#         limits_temp = [limits_old[0] + factor, limits_old[1] - factor]
#         limits_new = copy.deepcopy(limits_old)
#         limits_new[limit_to_change_idx] = limits_temp[limit_to_change_idx]
#         param_dict[param_dict_idx[param_to_change_idx]]['pdf_limits'] = limits_new
#
#         print(' > Changing pdf_limits of {} from {} -> {}'.format(param_dict_idx[param_to_change_idx],
#                                                              limits_old,
#                                                              limits_new))
#
#         # repeat dipole check
#         bad_params = self.get_invalid_coil_parameters(param_dict,
#                                                       coil_position_mean=self.coil_position_mean,
#                                                       svd_v=svd_v,
#                                                       del_obj=dobj,
#                                                       fn_coil=self.fn_coil)
#
#     return param_dict

# def calc_coil_position_pdf(fn_rescon, fn_simpos, folder_pdfplots):
#     """ Determines the probability density functions of the transformed coil position (x', y', z') and Euler angles of
#     the coil orientations (Psi, Theta, Phi)
#
#     calc_coil_position_pdf(fn_rescon, fn_simpos)
#
#     Parameters
#     ----------
#     fn_rescon: str
#         Filename of the results file from TMS experiments (results_conditions.csv)
#     fn_simpos: str
#         Filename of the positions and orientation from TMS experiments (simPos.csv)
#     folder_pdfplots: str
#         Folder, where the plots of the fitted pdfs are saved
#
#     Returns
#     -------
#     pdf_paras_location: list of np.array [n_conditions]
#         Pdf parameters (limits and shape) of the coil position
#     pdf_paras_orientation_euler: list of np.array [n_conditions]
#         Pdf parameters (limits and shape) of the coil orientation
#     positions_mean: List of [3x3] np.array [n_conditions]
#         List of mean coil position and orientation for different conditions (global coordinate system)
#     locations_zeromean: list of np.array [n_conditions]
#         List of shifted coil positions (zero-mean) for different conditions
#     V: list of [3x3] np.arrays [n_conditions]
#         Transformation matrix of coil positions from global coordinate system to transformed coordinate system
#     locations_transform: np.array [N_zaps_total x 3]
#         Transformed coil positions [x', y', z'] of all stimulations (zero-mean, rotated by SVD)
#     euler_angles: np.array [N_zaps_total x 3]
#         Euler angles [Psi, Theta, Phi] of all stimulations
#     """
#     import pygpc
#
#     if folder_pdfplots is not None:
#         make_pdf_plot = True
#     else:
#         make_pdf_plot = False
#         folder_pdfplots = ''
#
#     # load recorded positions and orientations
#     positions_all, conditions, position_list, _, _ = pynibs.read_exp_stimulations(fn_rescon, fn_simpos)
#
#     # sort POSITIONS according to CONDITIONS, idx_con is alphabetically sorted, first index of condition[*]
#     appeareance
#     conditions_unique, idx_con, n_con_each = np.unique(conditions,
#                                                        return_index=True,
#                                                        return_inverse=False,
#                                                        return_counts=True)
#     n_condition = len(conditions_unique)
#     n_zaps = len(positions_all)
#
#     idx_CON_sort = np.argsort(idx_con)
#     # idx_con = idx_con[idx_CON_sort]
#     conditions_unique = conditions_unique[idx_CON_sort]  # conditions_unique is ordered like exp. data
#     n_con_each = n_con_each[idx_CON_sort]
#
#     positions = [[] for i in range(n_condition)]
#     ori_x = [0] * n_condition
#     ori_y = [0] * n_condition
#     ori_z = [0] * n_condition
#     loc = [0] * n_condition
#     i = 0
#     k = 0
#     for j in range(n_condition):
#         ori_x[j] = np.zeros((n_con_each[j], 3))
#         ori_y[j] = np.zeros((n_con_each[j], 3))
#         ori_z[j] = np.zeros((n_con_each[j], 3))
#         loc[j] = np.zeros((n_con_each[j], 3))
#
#         while position_list[i][len(position_list[0])-3] == conditions_unique[j]:
#             positions[j].append(np.array(positions_all[i])[0:3, 0:4])
#             ori_x[j][k, ] = np.array(positions_all[i])[0:3, 0]
#             ori_y[j][k, ] = np.array(positions_all[i])[0:3, 1]
#             ori_z[j][k, ] = np.array(positions_all[i])[0:3, 2]
#             loc[j][k, ] = np.array(positions_all[i])[0:3, 3]
#             i = i + 1
#             k = k + 1
#             if i == n_zaps:
#                 break
#         k = 0
#     del i, j
#
#     # determine "mean" location and orientation
#     positions_mean = [0]*n_condition
#     pos = np.zeros((3, 4))
#
#     for i in range(n_condition):
#         for j in range(n_con_each[i]):
#             pos = pos + positions[i][j]
#         pos = pos / n_con_each[i]
#         positions_mean[i] = pos  # POSITIONS_mean[0] is mean coil center in condition '0'
#         pos = np.zeros((3, 4))
#
#         # test orthogonality of mean orientation axis
#         xy_orth = np.inner(positions_mean[i][:, 0], positions_mean[i][:, 1])
#         xz_orth = np.inner(positions_mean[i][:, 0], positions_mean[i][:, 2])
#         yz_orth = np.inner(positions_mean[i][:, 1], positions_mean[i][:, 2])
#
#     del i, j
#
#     # determine location inaccuracy
#
#     # concatenate all locations into one array
#     locations = [np.zeros((3,1))]*n_condition
#     for i in range(n_condition):
#         for j in range(n_con_each[i]):
#             locations[i] = np.hstack((locations[i], positions[i][j][0:3, 3][:, np.newaxis]))
#         locations[i] = np.delete(locations[i], 0, axis=1)
#
#     # shift points for SVD
#     locations_zeromean = [0]*n_condition
#     locations_transform = [0]*n_condition
#     U = [0]*n_condition
#     s = [0]*n_condition
#     V = [0]*n_condition
#
#     for i in range(n_condition):
#         locations_zeromean[i] = locations[i] - np.tile(positions_mean[i][:, 3][:, np.newaxis],
#                                                        (1, n_con_each[i]))
#         # LOCATIONS_zeromean[0] are 'normalized' positions
#
#         # perform SVD to determine principal axis
#         U[i], s[i], V[i] = np.linalg.svd(locations_zeromean[i].T, full_matrices=True)
#
#         # project locations on principal axis
#         locations_transform[i] = np.dot(locations_zeromean[i].T, V[i].T)
#         # LOCATIONS_transform[0] are svd'ed, normalized positions of condition 0
#
#     # fit beta pdfs to x', y' and z' locations and
#     pdf_paras_location = [[[] for i in range(3)] for j in range(n_condition)]
#     np.random.seed(5)
#     loc_labels = ['xp', 'yp', 'zp']
#     for i in range(n_condition):
#         for j in range(3):
#             pdf_paras_location[i][j] = pygpc.fit_betapdf(locations_transform[i][:, j],
#                                                          BETATOL=0.05,
#                                                          PUNI=0.9,
#                                                          PLOT=make_pdf_plot,
#                                                          VISI=0,
#                                                          filename=os.path.join(folder_pdfplots, 'POS_' +
#                                                                                conditions_unique[i] + '_' +
#                                                                                loc_labels[j] +
#                                                                                '_betafit'))
#         # pdf_paras_location[0][0] are beta parameter for condition 0, X axis
#
#     # project coil orientations to mean orientation
#
#     ori_x_transform = [0]*n_condition
#     ori_y_transform = [0]*n_condition
#     ori_z_transform = [0]*n_condition
#
#     for i in range(n_condition):
#         # for j in range(N_CON_each[i]):
#         ori_x_transform[i] = np.dot(ori_x[i], positions_mean[i][0:3, 0:3])
#         ori_y_transform[i] = np.dot(ori_y[i], positions_mean[i][0:3, 0:3])
#         ori_z_transform[i] = np.dot(ori_z[i], positions_mean[i][0:3, 0:3])
#
#     # # plot original orientations (endpoints) of first axis of first condition
#     # fig = plt.figure()
#     # ax = fig.add_subplot(111, projection='3d')
#     # ax.scatter(ORI_X[0][:,0], ORI_X[0][:,1], ORI_X[0][:,2] , zdir='z', s=20, c=[1,1,0], depthshade=True)
#     # fig.savefig(folder + 'ORI_X_0.png')
#     #
#     # fig = plt.figure()
#     # ax = fig.add_subplot(111, projection='3d')
#     # ax.scatter(ORI_X_transform[0][:,0], ORI_X_transform[0][:,1], ORI_X_transform[0][:,2] , zdir='z',
#     s=20, c=[1,1,0],
#     #  depthshade=True)
#     # fig.savefig(folder + 'ORI_X_transform_0.png')
#
#     # estimate angle variation between axes
#     pdf_paras_orientation = [[[] for i in range(3)] for j in range(n_condition)]
#     pdf_paras_orientation_euler = [[[] for i in range(3)] for j in range(n_condition)]
#     deviation_angle_all = [0]*n_condition
#     angle_names = ['Psi', 'Theta', 'Phi']
#     euler_angles = [0]*n_condition
#
#     r_all = []  # store all R here
#     for i in range(n_condition):
#         deviation_angle_all[i] = np.zeros((n_con_each[i], 3))
#
#         # Determine Euler angles
#         euler_angles[i] = np.zeros((n_con_each[i], 3))
#
#         for j in range(n_con_each[i]):
#             R = np.hstack((ori_x_transform[i][j, :][:, np.newaxis],
#                            ori_y_transform[i][j, :][:, np.newaxis],
#                            ori_z_transform[i][j, :][:, np.newaxis]))
#             euler_angles[i][j, :] = pynibs.rotation_matrix_to_euler_angles(R) * 180.0 / np.pi
#             r_all.append(R)
#         for j, name in enumerate(angle_names):
#             np.random.seed(5)
#             pdf_paras_orientation_euler[i][j] = pygpc.fit_betapdf(euler_angles[i][:, j],
#                                                                   BETATOL=0.05,
#                                                                   PUNI=0.9,
#                                                                   PLOT=make_pdf_plot,
#                                                                   VISI=0,
#                                                                   filename=os.path.join(folder_pdfplots, 'ORI_' +
#                                                                                         conditions_unique[i] + '_' +
#                                                                                         angle_names[j] +
#                                                                                         '_betafit'))
#             # pdf_paras_orientation_euler[0][0] are beta parameter for condition 0, alpha (pitch)
#     return pdf_paras_location, pdf_paras_orientation_euler, positions_mean, \
#            locations_zeromean, V, np.concatenate(locations_transform), np.concatenate(euler_angles)
