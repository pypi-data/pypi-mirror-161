""" """
import json
import math
import multiprocessing
import os
import time
import warnings
from functools import partial

import h5py
import nibabel
import numpy as np
import trimesh
from numpy import cross as cycross
from scipy.interpolate import griddata
from scipy.spatial import Delaunay
from tqdm import tqdm
import pynibs

__package__ = "pynibs"


def __path__():
    return os.path.dirname(__file__)


def calc_tet_volume(points, abs=True):
    """
    Calculate tetrahedra volumes.

    Parameter
    ---------
    points: np.ndarray
        shape: (n_tets,4,3)
        [[[Ax, Ay, Az],
          [Bx, By, Bz],
          [Cx, Cy, Cz],
          [Dx, Dy, Dy]],

         [[Ax, Ay, Az],
          [Bx, By, Bz],
          [Cx, Cy, Cz],
          [Dx, Dy, Dy]],

        ...

        ]

    Returns
    -------
    volume: np.ndarray
        shape: (n_tets)

    Other Parameters
    ----------------
    abs : bool
        Return magnitude. Default: True.
    """
    if points.ndim == 2:
        points = np.atleast_3d(points).reshape(1, 4, 3)
    if points.ndim != 3:
        raise ValueError(f"Wrong dimensions for points: ({points.shape}). Expected: (n_tets,4,3))")

    a = np.zeros((points.shape[0], 4, 4))
    a[:, :, 3] = 1
    a[:, :, :3] = points
    a = a.swapaxes(1, 2)

    if abs:
        return np.abs(1 / 6 * np.linalg.det(a))
    else:
        return 1 / 6 * np.linalg.det(a)


def calc_tri_surface(points):
    """
    Calculate triangle surface areas.

    Parameter
    ---------
    points : np.ndarray
        (n_triangles,3,3)

    Returns
    -------
    triange_area : np.ndarray
    """
    a = np.linalg.norm(points[:, 0] - points[:, 1], axis=1)
    b = np.linalg.norm(points[:, 1] - points[:, 2], axis=1)
    c = np.linalg.norm(points[:, 0] - points[:, 2], axis=1)
    s = np.sum((a, b, c), axis=0) / 2
    return (s * (s - a) * (s - b) * (s - c)) ** 0.5


def get_sphere(mesh=None, mesh_fn=None, target=None, radius=None, roi_idx=None, roi=None, elmtype='tris'):
    """
    Return element idx of elements within a certain distance to provided target.
    Element indices are 0-based (tris and tets start at 0, 'pynibs' style)
    Elements might be 'tris' (default) or 'tets'

    If roi object / idx and mesh fn is provided, the roi is expected to have midlayer information and the roi
    geometry is used.

    Parameters
    ----------
    mesh : pynibs.mesh.TetrahedraLinear, optional
    mesh_fn : str, optional
        Filename to SimNIBS .msh or pyNIBS .hdf5 mesh file
    target : np.ndarray of float, optional
        (3,) X, Y, Z coordinates of target
    radius : float, optional
        Sphere radius im mm
    roi_idx : str or int
        ROI name
    elmtype : str, optional
        Return triangles or tetrahedra in sphere around target. One of ('tris', 'tets')

    Returns
    -------
    elms_in_sphere : np.ndarray
        (n_elements): Indices of elements found in ROI
    """
    if mesh_fn is not None:
        if mesh is not None:
            raise ValueError("Either provide mesh or mesh_fn")
        if mesh_fn.endswith('.hdf5'):
            mesh = pynibs.load_mesh_hdf5(mesh_fn)
        elif mesh_fn.endswith('.msh'):
            mesh = pynibs.load_mesh_msh(mesh_fn)
    if roi is None and roi_idx is not None:
        if mesh_fn is None:
            raise ValueError("Provide mesh_fn to load roi from")
        roi = pynibs.load_roi_surface_obj_from_hdf5(mesh_fn)[roi_idx]
    if elmtype == 'tris':
        return tris_in_sphere(mesh=mesh, target=target, radius=radius, roi=roi)
    elif elmtype == 'tets':
        return tets_in_sphere(mesh=mesh, target=target, radius=radius, roi=roi)
    else:
        raise ValueError(f"Unknown elmtpye '{elmtype}'")


def tets_in_sphere(mesh, target, radius, roi):
    """
    Worker function for get_sphere()

    Returns element idx of elements within a certain distance to provided target.
    If roi object / idx and mesh fn is provided, the roi is expected to have midlayer information and the roi
    geometry is used.

    Parameters
    ----------
    mesh : pynibs.TetrahedraLinear, optional
    target : np.ndarray of float, optional
        (3,) X, Y, Z coordinates of target
    radius : float, optional
        Sphere radius im mm
    roi : pynibs.mesh.ROI, optional
        Region of interest

    Returns
    -------
    tets_in_sphere : np.ndarray
        (n_tets): Indices of elements found in ROI

    """
    if roi is None:
        if radius is None or radius == 0:
            return np.where(np.linalg.norm(mesh.tetrahedra_center - target, axis=1) ==
                            np.min(np.linalg.norm(mesh.tetrahedra_center - target, axis=1)))[0]

        else:
            return np.where(np.linalg.norm(mesh.tetrahedra_center - target, axis=1) <= radius)[0]

    else:
        warnings.warn("Sphere 'tets' extraction from ROI untested! Consider extracting 'tris' instead.")
        if radius is not None and radius > 0:
            tri_target_idx = np.where(np.linalg.norm(roi.tri_center_coord_mid - target, axis=1) <= radius)[0]
        else:
            tri_target_idx = np.where(np.linalg.norm(roi.tri_center_coord_mid - target, axis=1) == np.min(
                    np.linalg.norm(roi.tri_center_coord_mid - target, axis=1)))[0]
        tet_target_idx = roi.tet_idx_tri_center_mid[tri_target_idx]
        return tet_target_idx


def tris_in_sphere(mesh, target, radius, roi):
    """
    Worker function for get_sphere().

    Returns triangle idx of elements within a certain distance to provided target.
    If roi object / idx and mesh fn is provided, the roi is expected to have midlayer information and the roi
    geometry is used.

    Parameters
    ----------
    mesh : pynibs.mesh.TetrahedraLinear, optional
    target : np.ndarray of float, optional
        (3,) X, Y, Z coordinates of target
    radius : float, optional
        Sphere radius im mm
    roi : pynibs.mesh.ROI, optional
        ROI

    Returns
    -------
    tris_in_sphere : np.ndarray
        (n_triangles): Indices of elements found in sphere
    """
    if roi is None:
        if radius is None or radius == 0:
            tri_target_idx = np.where(np.linalg.norm(mesh.triangles_center - target, axis=1) ==
                                      np.min(np.linalg.norm(mesh.triangles_center - target, axis=1)))[0]
        else:
            tri_target_idx = np.where(np.linalg.norm(mesh.triangles_center - target, axis=1) <= radius)[0]
    else:
        if radius is not None and radius > 0:
            tri_target_idx = np.where(np.linalg.norm(roi.tri_center_coord_mid - target, axis=1) <= radius)[0]
        else:
            tri_target_idx = np.where(np.linalg.norm(roi.tri_center_coord_mid - target, axis=1) == np.min(
                    np.linalg.norm(roi.tri_center_coord_mid - target, axis=1)))[0]

    return tri_target_idx


def sample_sphere(n_points, r):
    """
    Creates n_points evenly spread in a sphere of radius r.

    Parameters
    ----------
    n_points: int
        Number of points to be spread, must be odd
    r: float
        Radius of sphere

    Returns
    -------
    points: np.ndarray of float [N x 3]
        Evenly spread points in a unit sphere
    """

    assert n_points % 2 == 1, "The number of points must be odd"
    points = []

    # The golden ratio
    phi = (1 + math.sqrt(5)) / 2.
    n = int((n_points - 1) / 2)

    for i in range(-n, n + 1):
        lat = math.asin(2 * i / n_points)
        lon = 2 * math.pi * i / phi
        x = r * math.cos(lat) * math.cos(lon)
        y = r * math.cos(lat) * math.sin(lon)
        z = r * math.sin(lat)
        points.append((x, y, z))

    points = np.array(points, dtype=float)

    return points


def cell_data_to_point_data(tris, data_tris, nodes, method='nearest'):
    """
    A wrapper for scipy.interpolate.griddata to interpolate cell data to node data.

    Parameters
    ----------

    tris : np.ndarray
        element number list, (n_tri, 3)
    data_tris : np.ndarray
        data in tris, (n_tri x 3)
    nodes : np.ndarray
        nodes coordinates, (n_nodes, 3
    method: str, default: 'nearest'
        Which method to use for interpolation. Default uses NearestNDInterpolator

    Returns
    -------
    data_nodes : np.ndarray
        Data in nodes
    """
    elms_center = np.mean(nodes[tris], axis=1)
    return griddata(elms_center, data_tris, nodes, method)


def get_indices_discontinuous_data(data, con, neighbor=False, deviation_factor=2,
                                   min_val=None, not_fitted_elms=None, crit='median', neigh_style='point'):
    """
    Get element indices (and the best neighbor index), where the data is discontinuous

    Parameters
    ----------
    data : np.ndarray of float [n_data]
        Data array to analyze given in the element center
    con : np.ndarray of float [n_data, 3 or 4]
        Connectivity matrix
    neighbor : boolean, optional, default=False
        Return also the element index of the "best" neighbor (w.r.t. median of data)
    deviation_factor : float
        Allows data deviation from 1/deviation_factor < data[i]/median < deviation_factor
    min_val : float, optional
        If given, only return elements which have a neighbor with data higher than min_val.
    not_fitted_elms : np.ndarray
        If given, these elements are not used as neighbors
    crit: str, default: median
        Criterium for best neighbor. Either median or max value
    neigh_style : str, default: 'point'
        Should neighbors share point or 'edge'

    Returns
    -------
    idx_disc : list of int [n_disc]
        Index list containing the indices of the discontinuous elements
    idx_neighbor : list of int [n_disc]
        Index list containing the indices of the "best" neighbors of the discontinuous elements
    """

    n_ele = con.shape[0]
    idx_disc, idx_neighbor = [], []

    data[data == 0] = 1e-12

    if neigh_style == 'point':
        def get_neigh(m):
            return np.logical_and(0 < mask, mask < 3)
    elif neigh_style == 'edge':
        def get_neigh(m):
            return mask == 2
    else:
        raise NotImplementedError(f"neigh_style {neigh_style} unknown.")

    if crit == 'median':
        def is_neigh():
            if not (1 / deviation_factor < data_i / median < deviation_factor):
                neighbor_indices = np.where(mask_neighbor)[0]
                best_neigh = neighbor_indices[(np.abs(data[neighbor_indices] - median)).argmin()]
                if min_val is None or data[best_neigh] > min_val:
                    idx_disc.append(elm_i)
                # if neighbor:
                idx_neighbor.append(best_neigh)
    elif crit == 'max':
        def is_neigh():
            if data_i / median < 1 / deviation_factor:
                neighbor_indices = np.where(mask_neighbor)[0]
                best_neigh = neighbor_indices[(data[neighbor_indices]).argmax()]
                if min_val is None or data[best_neigh] > min_val:
                    idx_disc.append(elm_i)

                # if neighbor:
                idx_neighbor.append(best_neigh)
    elif crit == 'randmax':
        def is_neigh():
            if data_i / median < 1 / deviation_factor:
                neighbor_indices = np.where(mask_neighbor)[0]
                best_neigh = np.random.choice(neighbor_indices[(data[neighbor_indices]) > 0], 1)
                if min_val is None or data[best_neigh] > min_val:
                    idx_disc.append(elm_i)

                # if neighbor:
                idx_neighbor.append(best_neigh)
    else:
        raise NotImplementedError(f"Criterium {crit} unknown. ")

    for elm_i, data_i in zip(range(n_ele), data):
        if elm_i in not_fitted_elms:
            continue

        # find neighbors
        mask = np.sum(np.isin(con, con[elm_i, :]), axis=1)
        mask_neighbor = get_neigh(mask)

        # best_values are set to 0 for bad elements and unfittable ones. do not use these as neighbors
        if not_fitted_elms is not None and len(not_fitted_elms) != 0:
            mask_neighbor[not_fitted_elms] = False

        # if the element is lonely floating and has no neighbors ... continue
        if not np.sum(mask_neighbor):
            continue

        # check if current value does not fit to neighbors
        median = np.median(data[mask_neighbor])

        if not median:
            median = 1e-12

        is_neigh()

        # if not (1 / deviation_factor < data_i / median < deviation_factor):
        #     # find best neighbor idx
        #     neighbor_indices = np.where(mask_neighbor)[0]
        #
        #     if crit == 'max':
        #         best_neigh = neighbor_indices[(data[neighbor_indices]).argmax()]
        #     elif crit == 'median':
        #         best_neigh = neighbor_indices[(np.abs(data[neighbor_indices] - median)).argmin()]
        #     else:
        #         raise  NotImplementedError(f"Criterium {crit} unknown. ")
        #     if min_val is None or data[best_neigh] > min_val:
        #         idx_disc.append(elm_i)
        #
        #     if neighbor:
        #         idx_neighbor.append(best_neigh)

        # stop = time.time()
        # print(stop-start)

    if neighbor:
        return idx_disc, idx_neighbor
    else:
        return idx_disc


def find_nearest(array, value):
    """
    Given an "array", and given a "value" , returns an index j such that "value" is between array[j]
    and array[j+1]. "array" must be monotonic increasing. j=-1 or j=len(array) is returned
    to indicate that "value" is out of range below and above respectively.

    Parameters
    ----------
    array : np.ndarray of float
        Monotonic increasing array
    value : float
        Target value the nearest neighbor index in "array" is computed for

    Returns
    -------
    idx : int
        Index j such that "value" is between array[j] and array[j+1]

    """
    n = len(array)
    if value < array[0]:
        return -1
    elif value > array[n - 1]:
        return n
    jl = 0  # Initialize lower
    ju = n - 1  # and upper limits.
    while ju - jl > 1:  # If we are not yet done,
        jm = (ju + jl) >> 1  # compute a midpoint with a bitshift
        if value >= array[jm]:
            jl = jm  # and replace either the lower limit
        else:
            ju = jm  # or the upper limit, as appropriate.
    # Repeat until the test condition is satisfied.
    if value == array[0]:  # edge cases at bottom
        return 0
    elif value == array[n - 1]:  # and top
        return n - 1
    else:
        return jl


def in_hull(points, hull):
    """
    Test if points in `points` are in `hull`.
    `points` should be a [N x K] coordinates of N points in K dimensions.
    `hull` is either a scipy.spatial.Delaunay object or the [M x K] array of the
    coordinates of M points in Kdimensions for which Delaunay triangulation
    will be computed.

    Parameters
    ----------
    points : np.ndarray
        (N_points x 3) Set of floating point data to test whether they are lying inside the hull or not
    hull : scipy.spatial.Delaunay  or np.ndarray
         (M x K) Surface data

    Returns
    -------
    inside : np.ndarray of bool
        TRUE: point inside the hull
        FALSE: point outside the hull
    """


    if not isinstance(hull, Delaunay):
        hull = Delaunay(hull)
    return hull.find_simplex(points) >= 0


def calc_tetrahedra_volume_cross(P1, P2, P3, P4):
    """
    Calculates volume of tetrahedra specified by the 4 points P1...P4
    multiple tetrahedra can be defined by P1...P4 as 2-D np.arrays
    using the cross and vector dot product

    .. math::
        P1=\\begin{bmatrix}
        x_{{tet}_1} & y_{{tet}_1} & z_{{tet}_1}   \\\\
        x_{{tet}_2} & y_{{tet}_2} & z_{{tet}_2}   \\\\
        ... & ... & ...    \\\\
        x_{{tet}_N} & y_{{tet}_N} & z_{{tet}_N}    \\\\
        \\end{bmatrix}

    Parameters
    ----------
    P1 : np.ndarray of float [N_tet x 3]
        Coordinates of first point of tetrahedra
    P2 : np.ndarray of float [N_tet x 3]
        Coordinates of second point of tetrahedra
    P3 : np.ndarray of float [N_tet x 3]
        Coordinates of third point of tetrahedra
    P4 : np.ndarray of float [N_tet x 3]
        Coordinates of fourth point of tetrahedra

    Returns
    -------
    tetrahedra_volume: np.ndarray of float [N_tet x 1]
        Volumes of tetrahedra
    """

    tetrahedra_volume = 1.0 / 6 * \
                        np.sum(np.multiply(cycross(P2 - P1, P3 - P1), P4 - P1), 1)
    tetrahedra_volume = tetrahedra_volume[:, np.newaxis]
    return tetrahedra_volume


def calc_tetrahedra_volume_det(P1, P2, P3, P4):
    """
    Calculate volume of tetrahedron specified by 4 points P1...P4
    multiple tetrahedra can be defined by P1...P4 as 2-D np.arrays
    using the determinant.


    .. math::
        P1=\\begin{bmatrix}
        x_{{tet}_1} & y_{{tet}_1} & z_{{tet}_1}   \\\\
        x_{{tet}_2} & y_{{tet}_2} & z_{{tet}_2}   \\\\
        ... & ... & ...    \\\\
        x_{{tet}_N} & y_{{tet}_N} & z_{{tet}_N}    \\\\
        \\end{bmatrix}

    Parameters
    ----------
    P1 : np.ndarray of float [N_tet x 3]
        Coordinates of first point of tetrahedra
    P2 : np.ndarray of float [N_tet x 3]
        Coordinates of second point of tetrahedra
    P3 : np.ndarray of float [N_tet x 3]
        Coordinates of third point of tetrahedra
    P4 : np.ndarray of float [N_tet x 3]
        Coordinates of fourth point of tetrahedra

    Returns
    -------
    tetrahedra_volume : np.ndarray of float [N_tet x 1]
        Volumes of tetrahedra
    """

    N_tets = P1.shape[0] if P1.ndim > 1 else 1

    # add ones
    j1 = np.hstack((np.ones((N_tets, 1)), P1))
    j2 = np.hstack((np.ones((N_tets, 1)), P2))
    j3 = np.hstack((np.ones((N_tets, 1)), P3))
    j4 = np.hstack((np.ones((N_tets, 1)), P4))

    j = np.zeros((P1.shape[0] if P1.ndim > 1 else 1, 4, 4))

    j[:, :, 0] = j1
    j[:, :, 1] = j2
    j[:, :, 2] = j3
    j[:, :, 3] = j4

    tetrahedra_volume = 1.0 / 6.0 * np.linalg.det(j)
    tetrahedra_volume = tetrahedra_volume[:, np.newaxis]
    return tetrahedra_volume


def calc_gradient_surface(phi, points, triangles):
    """
    Calculate gradient of potential phi on surface (i.e. tangential component) given in vertices of a triangular
    mesh forming a 2D surface.

    Parameters
    ----------
    phi : np.ndarray of float [N_points x 1]
        Potential in nodes
    points : np.ndarray of float [N_points x 3]
        Coordinates of nodes (x,y,z)
    triangles : np.ndarray of int32 [N_tri x 3]
        Connectivity of triangular mesh

    Returns
    -------
    grad_phi : np.ndarray of float [N_tri x 3]
        Gradient of potential phi on surface
    """

    grad_phi = np.zeros((triangles.shape[0], 3))

    for i in range(triangles.shape[0]):
        a = np.array([[points[triangles[i, 0], 0] - points[triangles[i, 2], 0],
                       points[triangles[i, 0], 1] - points[triangles[i, 2], 1],
                       points[triangles[i, 0], 2] - points[triangles[i, 2], 2]],
                      [points[triangles[i, 1], 0] - points[triangles[i, 2], 0],
                       points[triangles[i, 1], 1] - points[triangles[i, 2], 1],
                       points[triangles[i, 1], 2] - points[triangles[i, 2], 2]]])

        b = np.array([phi[triangles[i, 0]] - phi[triangles[i, 2]],
                      phi[triangles[i, 1]] - phi[triangles[i, 2]]])

        grad_phi[i, :] = np.dot(np.linalg.pinv(a), b).T

    return grad_phi


def map_data_to_surface(datasets, points_datasets, con_datasets, fname_fsl_gm, fname_fsl_wm, fname_midlayer=None,
                        delta=0.5, input_data_in_center=True, return_data_in_center=True, data_substitute=-1):
    """
    Maps data from ROI of fsl surface (wm, gm, or midlayer) to given Freesurfer brain surface (wm, gm, inflated).

    Parameters
    ----------
    datasets : np.ndarray of float [N_points x N_data] or list of np.ndarray
        Data in nodes or center of triangles in ROI (specify this in "data_in_center")
    points_datasets : np.ndarray of float [N_points x 3] or list of np.ndarray
        Point coordinates (x,y,z) of ROI where data in datasets list is given, the points have to be a subset of the
        GM/WM surface (has to be provided for each dataset)
    con_datasets : np.ndarray of int [N_tri x 3] or list of np.ndarray
        Connectivity matrix of dataset points (has to be provided for each dataset)
    fname_fsl_gm : str or list of str or list of None
        Filename of pial surface fsl file(s) (one or two hemispheres)
        e.g. in mri2msh: .../fs_ID/surf/lh.pial
    fname_fsl_wm : str or list of str or list of None
        Filename of wm surface fsl file(s) (one or two hemispheres)
        e.g. in mri2msh: .../fs_ID/surf/lh.white
    fname_midlayer : str or list of str
        Filename of midlayer surface fsl file(s) (one or two hemispheres)
        e.g. in headreco: .../fs_ID/surf/lh.central
    delta : float
        Distance parameter where gm-wm surface was generated 0...1 (default: 0.5)
        0 -> WM surface
        1 -> GM surface
    input_data_in_center : bool
        Flag if data in datasets in given in triangle centers or in points (Default: True)
    return_data_in_center : bool
        Flag if data should be returned in nodes or in elements (Default: True)
    data_substitute : float
        Data substitute with this number for all points in the inflated brain, which do not belong to the given data set

    Returns
    -------
    data_mapped : np.ndarray of float [N_points_inf x N_data]
        Mapped data to target brain surface. In points or elements
    """

    if type(fname_fsl_gm) is not list:
        fname_fsl_gm = [fname_fsl_gm]

    if type(fname_fsl_wm) is not list:
        fname_fsl_wm = [fname_fsl_wm]

    if type(fname_midlayer) is not list:
        fname_midlayer = [fname_midlayer]

    if fname_midlayer[0] is None:
        # load all freesurfer surfaces of gm and wm (hemispheres) and create midlayer
        points_gm = []
        con_target = []
        points_wm = []
        con_idx = 0

        for f_gm, f_wm in zip(fname_fsl_gm, fname_fsl_wm):
            p_gm, c_tar = nibabel.freesurfer.read_geometry(f_gm)
            p_wm, _ = nibabel.freesurfer.read_geometry(f_wm)

            points_gm.append(p_gm)
            points_wm.append(p_wm)
            con_target.append(c_tar + con_idx)
            con_idx += np.max(c_tar) + 1  # c_tar.shape[0]

        points_gm = np.vstack(points_gm)
        points_wm = np.vstack(points_wm)
        con_target = np.vstack(con_target)

        # regenerate the gm-wm surface w/o cropping in order to find congruent points
        wm_gm_vector = points_gm - points_wm

        # determine wm-gm surface (midlayer)
        points = points_wm + wm_gm_vector * delta

    else:
        # load directly all freesurfer midlayer surfaces (hemispheres)
        points = []
        con_target = []
        con_idx = 0

        for f_mid in fname_midlayer:
            if f_mid.endswith('.gii'):
                img = nibabel.gifti.giftiio.read(f_mid)
                p_mid = img.agg_data('pointset')
                c_tar = img.agg_data('triangle')
            else:
                p_mid, c_tar = nibabel.freesurfer.read_geometry(f_mid)

            points.append(p_mid)
            con_target.append(c_tar + con_idx)
            con_idx += np.max(c_tar) + 1  # c_tar.shape[0]

        points = np.vstack(points)
        con_target = np.vstack(con_target)

    # check datasets
    if type(datasets) is not list:
        datasets = [datasets]

    for i in range(len(datasets)):
        if datasets[i].ndim == 1:
            datasets[i] = datasets[i][:, np.newaxis]
        elif datasets[i].shape[0] < datasets[i].shape[1]:
            raise Warning("Datasets #{} shape[0] dimension is smaller than shape[1] (less points than dataset"
                          "components). Input dimension should be [N_points x N_data] ")

    if type(points_datasets) is not list:
        points_datasets = [points_datasets]

    if type(con_datasets) is not list:
        con_datasets = [con_datasets]
    # check if all points and all con are the same (if so, just map once and reuse results)
    all_points_equal = all([(points_datasets[i] == points_datasets[i + 1]).all()
                            for i in range(len(points_datasets) - 1)])

    all_con_equal = all([(con_datasets[i] == con_datasets[i + 1]).all()
                         for i in range(len(con_datasets) - 1)])

    if all_points_equal and all_con_equal:
        n_main_iter = 1
        n_sub_iter = len(datasets)
    else:
        n_main_iter = len(datasets)
        n_sub_iter = 1

    # check if indexation starts with value greater zero
    if np.min(con_target) > 0:
        con_target = con_target - np.min(con_target)

    n_points = points.shape[0]

    data_mapped = []

    # for i, data in enumerate(datasets):
    for i in range(n_main_iter):
        n_data = datasets[i].shape[1] if datasets[i].ndim > 1 else 1

        n_points_cropped = points_datasets[i].shape[0]

        # check if indexation starts with value greater zero
        if np.min(con_datasets[i]) > 0:
            con_datasets[i] = con_datasets[i] - np.min(con_datasets[i])

        if datasets[i].ndim == 1:
            datasets[i] = datasets[i][:, np.newaxis]

        if input_data_in_center and return_data_in_center:
            # determine triangle center of dataset
            triangle_center_datasets = np.average(points_datasets[i][con_datasets[i]], axis=1)

            # determine triangle center of whole surface
            triangle_center_surface = np.average(points[con_target], axis=1)

            # loop over all points to get index list
            point_idx_target = []
            point_idx_data = []

            point_idx_target = np.zeros(datasets[i].shape[0])
            point_idx_data = np.arange(datasets[i].shape[0])
            for j in tqdm(range(datasets[i].shape[0]), desc="Mapping ROI to surface"):
                point_idx_target[j] = np.where(np.all(np.isclose(triangle_center_datasets[j,], triangle_center_surface),
                                                      axis=1))[0]
            point_idx_target = point_idx_target.astype(int).tolist()
            point_idx_data = point_idx_data.astype(int).tolist()

            # run subiterations (if all points and cons are equal, we save a lot of time here)
            for k in range(n_sub_iter):
                data_mapped.append(np.zeros([triangle_center_surface.shape[0], n_data]) + data_substitute * 1.0)
                data_mapped[k][point_idx_target, :] = datasets[k][point_idx_data, :]

        else:
            # loop over all points to get index list
            point_idx_target = []
            point_idx_data = list(range(datasets[i].shape[0]))

            for j in range(datasets[i].shape[0]):
                point_idx_target.append(np.where(np.all(np.isclose(points_datasets[i][j,], points), axis=1))[0])

            point_idx_target = [int(p) for p in point_idx_target]
            point_idx_data = [int(p) for p in point_idx_data]

            # run subiterations (if all points and cons are equal, we save a lot of time here)
            for k in range(n_sub_iter):
                # transform data from triangle center to triangle nodes if necessary
                if input_data_in_center:
                    data_nodes = data_elements2nodes(datasets[k], con_datasets[k])
                else:
                    data_nodes = datasets[k]

                # find and map data points
                data_mapped.append(np.zeros([n_points, n_data]) + data_substitute * 1.0)
                data_mapped[k][point_idx_target] = data_nodes[point_idx_data]

                # return data in elements instead of points
                if return_data_in_center:
                    data_mapped[k] = data_nodes2elements(data_mapped[k], con_target)

    return data_mapped


def data_nodes2elements(data, con):
    """
    Transforms data in nodes to elements (triangles or tetrahedra)

    Parameters
    ----------
    data : np.ndarray of float
        (N_nodes, N_data)
        Data given in the nodes
    con : np.ndarray of int
        triangles: (N_elements, 3)
        tetrahedra: (N_elements, 4)
        Connectivity index list forming the elements

    Returns
    -------
    out : np.ndarray of float
        (N_elements, N_data)
        Data given in the element scenters
    """

    return np.average(data[con], axis=1)


def data_elements2nodes(data, con):
    """
    Transforms data in elements (triangles or tetrahedra) to nodes.
    Data can be list of multiple data arrays.

    Parameters
    ----------
    data : np.ndarray of float or list of np.ndarray
        (N_elements, N_data)
        Data given in the elements (multiple datasets who fit to con may be passed in a list)
    con : np.ndarray of int
        triangles: (N_elements. 3)
        tetrahedra: (N_elements, 4)
        Connectivity index list forming the elements

    Returns
    -------
    out : np.ndarray of float or list of np.ndarray
        (N_nodes, N_data)
        Data in nodes
    """

    # check if single dataset or a list of multiple datasets is passed
    if type(data) is not list:
        single_array_input = True
        data = [data]
    else:
        single_array_input = False

    n_elements = data[0].shape[0]
    n_nodes = con.max() - con.min() + 1
    if con.min() != 0:
        warnings.warn("Node number list is not zero based")

    # built connectivity matrix
    try:
        c = np.zeros([n_elements, n_nodes])

        for i in range(n_elements):
            c[i, (con[i])] = 1.0 / con.shape[1]

        # filter out NaN from dataset
        for i in range(len(data)):
            data[i][np.isnan(data[i])] = 0

        # determine inverse of node matrix
        cinv = np.linalg.pinv(c)

        # transform data from element center to element nodes
        data_in_nodes = [np.dot(cinv, d) for d in data]

    except np.core._exceptions._ArrayMemoryError:
        warnings.warn("Cannot allocate enough RAM to do fast data->nodes conversion. "
                      "Falling back to (slow) iterative mapping.")
        data_in_nodes = []
        for d in data:
            data_nodes = np.zeros(n_nodes, )
            for i in tqdm(range(n_nodes), desc="Mapping elements to node data"):
                data_nodes[i] = d[np.argwhere(con == i)[:, 0]].mean()

    # if single array was provided, return array as well
    if single_array_input:
        data_in_nodes = np.array(data_in_nodes)

    return data_in_nodes


class TetrahedraLinear:
    """
    Mesh, consisting of linear tetrahedra.

    Parameters
    ----------
    points : array of float [N_points x 3]
        Vertices of FE mesh
    triangles : np.ndarray of int [N_tri x 3]
        Connectivity of points forming triangles
    triangles_regions : np.ndarray of int [N_tri x 1]
        Region identifiers of triangles
    tetrahedra : np.ndarray of int [N_tet x 4]
        Connectivity of points forming tetrahedra
    tetrahedra_regions : np.ndarray of int [N_tet x 1]
        Region identifiers of tetrahedra

    Attributes
    ----------
    N_points : int
        Number of vertices
    N_tet : int
        Number of tetrahedra
    N_tri : int
        Number of triangles
    N_region : int
        Number of regions
    region : np.ndarray of int
        Region labels
    tetrahedra_volume : np.ndarray of float [N_tet x 1]
        Volumes of tetrahedra
    tetrahedra_center : np.ndarray of float [N_tet x 1]
        Center of tetrahedra
    triangles_center : np.ndarray of float [N_tri x 1]
        Center of triangles
    triangles_normal : np.ndarray of float [N_tri x 3]
        Normal components of triangles pointing outwards
    """

    def __init__(self, points, triangles, triangles_regions, tetrahedra, tetrahedra_regions):
        """ Initialize TetrahedraLinear class """
        self.points = points
        self.triangles = triangles
        self.triangles_regions = triangles_regions
        self.tetrahedra = tetrahedra
        self.tetrahedra_regions = tetrahedra_regions
        # index of points in "tetrahedra" start with 0 or 1

        self.tetrahedra_triangle_surface_idx = - np.ones((self.triangles.shape[0], 2))

        # shift index to start always from 0 (python)
        if self.tetrahedra.size != 0:
            self.idx_start = np.min(self.tetrahedra)
            self.tetrahedra = self.tetrahedra - self.idx_start
            self.N_tet = self.tetrahedra.shape[0]
            p1_tet = self.points[self.tetrahedra[:, 0], :]  # [P1x P1y P1z]
            p2_tet = self.points[self.tetrahedra[:, 1], :]
            p3_tet = self.points[self.tetrahedra[:, 2], :]
            p4_tet = self.points[self.tetrahedra[:, 3], :]
            self.tetrahedra_volume = calc_tetrahedra_volume_cross(p1_tet, p2_tet, p3_tet, p4_tet)
            self.tetrahedra_center = 1.0 / 4 * (p1_tet + p2_tet + p3_tet + p4_tet)

        else:
            self.N_tet = 0
            self.idx_start = 0
        self.triangles = self.triangles - self.idx_start

        self.region = np.unique(self.tetrahedra_regions)

        # number of elements and points etc
        self.N_points = self.points.shape[0]
        self.N_tri = self.triangles.shape[0]
        self.N_region = len(self.region)

        # count index lists of elements [0,1,2,....]
        self.tetrahedra_index = np.arange(self.N_tet)
        self.triangles_index = np.arange(self.N_tri)

        if self.N_tri > 0:
            p1_tri = self.points[self.triangles[:, 0], :]
            p2_tri = self.points[self.triangles[:, 1], :]
            p3_tri = self.points[self.triangles[:, 2], :]

            self.triangles_center = 1.0 / 3 * (p1_tri + p2_tri + p3_tri)
            self.triangles_normal = cycross(p2_tri - p1_tri, p3_tri - p1_tri)
            normal_norm = np.linalg.norm(self.triangles_normal, axis=1)
            normal_norm = normal_norm[:, np.newaxis]
            self.triangles_normal = self.triangles_normal / np.tile(normal_norm, (1, 3))
            self.triangles_area = 0.5 * np.linalg.norm(np.cross(p2_tri - p1_tri, p3_tri - p1_tri), axis=1)

    def calc_E_on_GM_WM_surface_simnibs(self, phi, dAdt, roi, subject, verbose=False, mesh_idx=0):
        """
        Determines the normal and tangential component of the induced electric field on a GM-WM surface by recalculating
        phi and dA/dt in an epsilon environment around the GM/WM surface (upper and lower GM-WM surface) or by using
        the Simnibs interpolation function.

        Parameters
        ----------
        phi : np.ndarray of float [N_nodes x 1]
            Scalar electric potential given in the nodes of the mesh
        dAdt : np.ndarray of float [N_nodes x 3]
            Magnetic vector potential given in the nodes of the mesh
        roi : object instance
            RegionOfInterestSurface object class instance
        subject : Subject object
            Subject object loaded from .hdf5 file
        verbose : boolean
            Print information to stdout
        mesh_idx : int
            Mesh index

        Returns
        -------
        E_normal : np.ndarray of float [N_points x 3]
            Normal vector of electric field on GM-WM surface
        E_tangential : np.ndarray of float [N_points x 3]
            Tangential vector of electric field on GM-WM surface
        """
        import tempfile
        import simnibs.msh.mesh_io as mesh_io
        import simnibs.simulation.fem as fem
        import simnibs.msh.transformations as transformations

        mesh_folder = subject.mesh[mesh_idx]["mesh_folder"]

        # load mesh
        mesh = mesh_io.read_msh(subject.mesh[mesh_idx]["fn_mesh_msh"])

        # write phi and dAdt in msh
        dAdt_SimNIBS = mesh_io.NodeData(dAdt, name='D', mesh=mesh)
        phi_SimNIBS = mesh_io.NodeData(phi.flatten(), name='v', mesh=mesh)

        if verbose:
            print("Calculating e-field")
        out = fem.calc_fields(phi_SimNIBS, "vDEe", cond=None, dadt=dAdt_SimNIBS)

        with tempfile.TemporaryDirectory() as f:
            fn_res_tmp = os.path.join(f, "res.msh")
            # mesh_io.write_msh(out, fn_res_tmp)

            if verbose:
                print("Interpolating values to midlayer of GM")
            # determine e in midlayer
            transformations.middle_gm_interpolation(mesh_fn=out,
                                                    m2m_folder=os.path.join(mesh_folder, "m2m_" + subject.id),
                                                    out_folder=f,
                                                    out_fsaverage=None,
                                                    depth=0.5,
                                                    quantities=['norm', 'normal', 'tangent', 'angle'],
                                                    fields=None,
                                                    open_in_gmsh=False,
                                                    write_msh=False)  #

            # load freesurfer surface
            if type(roi.gm_surf_fname) is not list:
                roi.gm_surf_fname = [roi.gm_surf_fname]

            points_gm = [None for _ in range(len(roi.gm_surf_fname))]
            con_gm = [None for _ in range(len(roi.gm_surf_fname))]

            max_idx_gm = 0

            if (roi.gm_surf_fname is list and len(roi.gm_surf_fname) > 0) or (roi.gm_surf_fname is str):
                fn_surface = list(roi.gm_surf_fname)
            elif (roi.midlayer_surf_fname is list and len(roi.gm_surf_fname) > 0) or (roi.midlayer_surf_fname is str):
                fn_surface = list(roi.midlayer_surf_fname)

            for i in range(len(fn_surface)):
                points_gm[i], con_gm[i] = nibabel.freesurfer.read_geometry(os.path.join(mesh_folder, fn_surface[i]))

                con_gm[i] = con_gm[i] + max_idx_gm

                max_idx_gm = max_idx_gm + points_gm[i].shape[0]  # np.max(con_gm[i]) + 2

            points_gm = np.vstack(points_gm)
            con_gm = np.vstack(con_gm)

            if verbose:
                print("Processing data to ROI")
            if roi.fn_mask is None or roi.fn_mask == []:

                if roi.X_ROI is None or roi.X_ROI == []:
                    roi.X_ROI = [-np.inf, np.inf]
                if roi.Y_ROI is None or roi.Y_ROI == []:
                    roi.Y_ROI = [-np.inf, np.inf]
                if roi.Z_ROI is None or roi.Z_ROI == []:
                    roi.Z_ROI = [-np.inf, np.inf]

                roi_mask_bool = (roi.node_coord_mid[:, 0] > min(roi.X_ROI)) & (
                        roi.node_coord_mid[:, 0] < max(roi.X_ROI)) & \
                                (roi.node_coord_mid[:, 1] > min(roi.Y_ROI)) & (
                                        roi.node_coord_mid[:, 1] < max(roi.Y_ROI)) & \
                                (roi.node_coord_mid[:, 2] > min(roi.Z_ROI)) & (
                                        roi.node_coord_mid[:, 2] < max(roi.Z_ROI))
                roi_mask_idx = np.where(roi_mask_bool)

            else:
                if type(roi.fn_mask) is np.ndarray:
                    if roi.fn_mask.ndim == 0:
                        roi.fn_mask = roi.fn_mask.astype(str).tolist()

                # read mask from freesurfer mask file
                mask = nibabel.freesurfer.mghformat.MGHImage.from_filename(
                        os.path.join(mesh_folder, roi.fn_mask)).dataobj[:]
                roi_mask_idx = np.where(mask > 0.5)

            # read results data
            if verbose:
                print("Reading SimNIBS midlayer data")
            e_normal = []
            e_tan = []

            for fn_surf in fn_surface:
                if "lh" in os.path.split(fn_surf)[1]:
                    e_normal.append(nibabel.freesurfer.read_morph_data(
                            os.path.join(f, "lh.res.central.E." + "normal")).flatten()[:, np.newaxis])
                    e_tan.append(nibabel.freesurfer.read_morph_data(
                            os.path.join(f, "lh.res.central.E." + "tangent")).flatten()[:, np.newaxis])

                if "rh" in os.path.split(fn_surf)[1]:
                    e_normal.append(nibabel.freesurfer.read_morph_data(
                            os.path.join(f, "rh.res.central.E." + "normal")).flatten()[:, np.newaxis])
                    e_tan.append(nibabel.freesurfer.read_morph_data(
                            os.path.join(f, "rh.res.central.E." + "tangent")).flatten()[:, np.newaxis])

            e_normal = np.vstack(e_normal)
            e_tan = np.vstack(e_tan)

            # transform point data to element data
            if verbose:
                print("Transforming point data to element data")
            e_normal = data_nodes2elements(data=e_normal, con=con_gm)
            e_tan = data_nodes2elements(data=e_tan, con=con_gm)

            # crop results data to ROI
            # if not roi_mask_bool.all():
            if roi_mask_idx:
                if verbose:
                    print("Cropping results data to ROI")

                # get row index where all points are lying inside ROI
                con_row_idx = [i for i in range(con_gm.shape[0]) if len(np.intersect1d(con_gm[i,], roi_mask_idx)) == 3]

                e_normal = e_normal[con_row_idx, :]
                e_tan = e_tan[con_row_idx, :]

        return e_normal, e_tan

    def calc_E_on_GM_WM_surface_simnibs_KW(self, phi, dAdt, roi, subject, verbose=False, mesh_idx=0):
        """
        Determines the normal and tangential component of the induced electric field on a GM-WM surface by recalculating
        phi and dA/dt in an epsilon environment around the GM/WM surface (upper and lower GM-WM surface) or by using
        the Simnibs interpolation function.

        Parameters
        ----------
        phi : np.ndarray of float [N_nodes x 1]
            Scalar electric potential given in the nodes of the mesh
        dAdt : np.ndarray of float [N_nodes x 3]
            Magnetic vector potential given in the nodes of the mesh
        roi : object instance
            RegionOfInterestSurface object class instance
        subject : Subject object
            Subject object loaded from .hdf5 file
        verbose : boolean
            Print information to stdout
        mesh_idx : int
            Mesh index

        Returns
        -------
        E_normal : np.ndarray of float [N_points x 3]
            Normal vector of electric field on GM-WM surface
        E_tangential : np.ndarray of float [N_points x 3]
            Tangential vector of electric field on GM-WM surface
        """
        import tempfile
        import simnibs.msh.mesh_io as mesh_io
        import simnibs.simulation.fem as fem
        import simnibs.msh.transformations as transformations

        mesh_folder = subject.mesh[mesh_idx]["mesh_folder"]

        # load mesh
        mesh = mesh_io.read_msh(subject.mesh[mesh_idx]["fn_mesh_msh"])

        # write phi and dAdt in msh
        dAdt_SimNIBS = mesh_io.NodeData(dAdt, name='D', mesh=mesh)
        phi_SimNIBS = mesh_io.NodeData(phi.flatten(), name='v', mesh=mesh)

        if verbose:
            print("Calculating e-field")
        out = fem.calc_fields(phi_SimNIBS, "vDEe", cond=None, dadt=dAdt_SimNIBS)

        with tempfile.TemporaryDirectory() as f:
            fn_res_tmp = os.path.join(f, "res.msh")
            mesh_io.write_msh(out, fn_res_tmp)

            if verbose:
                print("Interpolating values to midlayer of GM")
            # determine e in midlayer
            transformations.middle_gm_interpolation(mesh_fn=fn_res_tmp,
                                                    m2m_folder=os.path.join(mesh_folder, "m2m_" + subject.id),
                                                    out_folder=f,
                                                    out_fsaverage=None,
                                                    depth=0.5,
                                                    quantities=['norm', 'normal', 'tangent', 'angle'],
                                                    fields=None,
                                                    open_in_gmsh=False)  # write_msh=False

            # load freesurfer surface
            if type(roi.gm_surf_fname) is not list:
                roi.gm_surf_fname = [roi.gm_surf_fname]

            points_gm = [None for _ in range(len(roi.gm_surf_fname))]
            con_gm = [None for _ in range(len(roi.gm_surf_fname))]

            max_idx_gm = 0

            if (type(roi.gm_surf_fname) is list and roi.gm_surf_fname[0] is not None) or \
                    (type(roi.gm_surf_fname) is str):
                if type(roi.gm_surf_fname) is str:
                    fn_surface = [roi.gm_surf_fname]
                else:
                    fn_surface = roi.gm_surf_fname

            elif (type(roi.midlayer_surf_fname) is list and roi.gm_surf_fname is not None) or \
                    (type(roi.midlayer_surf_fname) is str):
                if type(roi.midlayer_surf_fname) is str:
                    fn_surface = [roi.midlayer_surf_fname]
                else:
                    fn_surface = roi.midlayer_surf_fname

            for i in range(len(fn_surface)):
                points_gm[i], con_gm[i] = nibabel.freesurfer.read_geometry(os.path.join(mesh_folder, fn_surface[i]))

                con_gm[i] = con_gm[i] + max_idx_gm

                max_idx_gm = max_idx_gm + points_gm[i].shape[0]  # np.max(con_gm[i]) + 2

            points_gm = np.vstack(points_gm)
            con_gm = np.vstack(con_gm)

            if verbose:
                print("Processing data to ROI")
            if roi.fn_mask is None or roi.fn_mask == []:

                if roi.X_ROI is None or roi.X_ROI == []:
                    roi.X_ROI = [-np.inf, np.inf]
                if roi.Y_ROI is None or roi.Y_ROI == []:
                    roi.Y_ROI = [-np.inf, np.inf]
                if roi.Z_ROI is None or roi.Z_ROI == []:
                    roi.Z_ROI = [-np.inf, np.inf]

                roi_mask_bool = (roi.node_coord_mid[:, 0] > min(roi.X_ROI)) & (
                        roi.node_coord_mid[:, 0] < max(roi.X_ROI)) & \
                                (roi.node_coord_mid[:, 1] > min(roi.Y_ROI)) & (
                                        roi.node_coord_mid[:, 1] < max(roi.Y_ROI)) & \
                                (roi.node_coord_mid[:, 2] > min(roi.Z_ROI)) & (
                                        roi.node_coord_mid[:, 2] < max(roi.Z_ROI))
                roi_mask_idx = np.where(roi_mask_bool)

            else:
                if type(roi.fn_mask) is np.ndarray:
                    if roi.fn_mask.ndim == 0:
                        roi.fn_mask = roi.fn_mask.astype(str).tolist()

                # read mask from freesurfer mask file
                mask = nibabel.freesurfer.mghformat.MGHImage.from_filename(
                        os.path.join(mesh_folder, roi.fn_mask)).dataobj[:]
                roi_mask_idx = np.where(mask > 0.5)

            # read results data
            if verbose:
                print("Reading SimNIBS midlayer data")
            e_normal = []
            e_tan = []

            for fn_surf in fn_surface:
                if "lh" in os.path.split(fn_surf)[1]:
                    e_normal.append(nibabel.freesurfer.read_morph_data(
                            os.path.join(f, "lh.res.central.E." + "normal")).flatten()[:, np.newaxis])
                    e_tan.append(nibabel.freesurfer.read_morph_data(
                            os.path.join(f, "lh.res.central.E." + "tangent")).flatten()[:, np.newaxis])

                if "rh" in os.path.split(fn_surf)[1]:
                    e_normal.append(nibabel.freesurfer.read_morph_data(
                            os.path.join(f, "rh.res.central.E." + "normal")).flatten()[:, np.newaxis])
                    e_tan.append(nibabel.freesurfer.read_morph_data(
                            os.path.join(f, "rh.res.central.E." + "tangent")).flatten()[:, np.newaxis])

            e_normal = np.vstack(e_normal)
            e_tan = np.vstack(e_tan)

            # transform point data to element data
            if verbose:
                print("Transforming point data to element data")
            e_normal = data_nodes2elements(data=e_normal, con=con_gm)
            e_tan = data_nodes2elements(data=e_tan, con=con_gm)

            # crop results data to ROI
            # if not roi_mask_bool.all():
            if roi_mask_idx:
                if verbose:
                    print("Cropping results data to ROI")

                # get row index where all points are lying inside ROI
                con_row_idx = [i for i in range(con_gm.shape[0]) if len(np.intersect1d(con_gm[i,], roi_mask_idx)) == 3]

                e_normal = e_normal[con_row_idx, :]
                e_tan = e_tan[con_row_idx, :]

        return e_normal, e_tan

    def calc_E_on_GM_WM_surface3(self, phi, dAdt, roi, verbose=True, mode="components"):
        """
        Determines the normal and tangential component of the induced electric field on a GM-WM surface by recalculating
        phi and dA/dt in an epsilon environment around the GM/WM surface (upper and lower GM-WM surface).

        Parameters
        ----------
        phi : np.ndarray of float [N_nodes x 1]
            Scalar electric potential given in the nodes of the mesh
        dAdt : np.ndarray of float [N_nodes x 3]
            Magnetic vector potential given in the nodes of the mesh
        roi : object instance
            RegionOfInterestSurface object class instance
        verbose : boolean
            Print information to stdout
        mode : str
            Select mode of output:
            - "components" : return x, y, and z component of tangential and normal components
            - "magnitude" : return magnitude of tangential and normal component (normal with sign for direction)

        Returns
        -------
        E_normal : np.ndarray of float [N_points x 3]
            Normal vector of electric field on GM-WM surface
        E_tangential : np.ndarray of float [N_points x 3]
            Tangential vector of electric field on GM-WM surface
        """
        # check if dimension are fitting
        assert phi.shape[0] == dAdt.shape[0]
        assert dAdt.shape[1] == 3

        # interpolate electric scalar potential to central points of upper and lower surface triangles
        if verbose:
            print("Interpolating electric scalar potential to central points of upper and lower surface triangles")
        phi_gm_wm_surface_up = self.calc_QOI_in_points_tet_idx(qoi=phi,
                                                               points_out=roi.tri_center_coord_up,
                                                               tet_idx=roi.tet_idx_tri_center_up.flatten())

        phi_gm_wm_surface_low = self.calc_QOI_in_points_tet_idx(qoi=phi,
                                                                points_out=roi.tri_center_coord_low,
                                                                tet_idx=roi.tet_idx_tri_center_low.flatten())

        # determine distance between upper and lower surface (in m!)
        d = np.linalg.norm(roi.tri_center_coord_up - roi.tri_center_coord_low, axis=1)[:, np.newaxis] * 1E-3
        d[np.argwhere(d == 0)[:, 0]] = 1e-6  # delete zero distances

        # determine surface normal vector (normalized)
        # n = ((points_up - points_low) / np.tile(d, (1, 3)))*1E-3
        # n = (points_up - points_low) * 1E-3

        p1_tri = roi.node_coord_mid[roi.node_number_list[:, 0], :]
        p2_tri = roi.node_coord_mid[roi.node_number_list[:, 1], :]
        p3_tri = roi.node_coord_mid[roi.node_number_list[:, 2], :]

        n = cycross(p2_tri - p1_tri, p3_tri - p1_tri)
        normal_norm = np.linalg.norm(n, axis=1)
        normal_norm = normal_norm[:, np.newaxis]
        n = n / np.tile(normal_norm, (1, 3))

        # interpolate magnetic vector potential to central surface points (primary electric field)
        # E_pri = griddata(self.points, dAdt, surf_mid, method='linear', fill_value=np.NaN, rescale=False)
        if verbose:
            print("Interpolating magnetic vector potential to central surface points (primary electric field)")
        e_pri = self.calc_QOI_in_points_tet_idx(qoi=dAdt,
                                                points_out=roi.tri_center_coord_mid,
                                                tet_idx=roi.tet_idx_tri_center_mid.flatten())

        # determine its normal component
        e_pri_normal = np.multiply(np.sum(np.multiply(e_pri, n), axis=1)[:, np.newaxis], n)

        # determine gradient of phi and multiply with surface normal (secondary electric field)
        e_sec_normal = np.multiply((phi_gm_wm_surface_up - phi_gm_wm_surface_low) * 1E-3 / d, n)

        # combine (normal) primary and secondary electric field
        e_normal = self.calc_E(e_sec_normal, e_pri_normal)

        # compute tangential component of secondary electric field on surface
        if verbose:
            print("Interpolating scalar electric potential to nodes of midlayer (primary electric field)")
        phi_surf_mid_nodes = self.calc_QOI_in_points_tet_idx(qoi=phi,
                                                             points_out=roi.node_coord_mid,
                                                             tet_idx=roi.tet_idx_node_coord_mid.flatten())

        if verbose:
            print("Determine gradient of scalar electric potential on midlayer surface (E_sec_tangential)")
        e_sec_tan = calc_gradient_surface(phi=phi_surf_mid_nodes,
                                          points=roi.node_coord_mid,
                                          triangles=roi.node_number_list)

        # compute tangential component of primary electric field on surface
        e_pri_tan = e_pri - e_pri_normal

        # compute tangential component of total electric field
        e_tan = self.calc_E(e_sec_tan, e_pri_tan)

        # determine total E on surface (sanity check)
        # E = self.calc_QOI_in_points(E, surf_mid)

        if mode == "magnitude":
            # get sign info of normal component
            e_normal_dir = (np.sum(e_normal * n, axis=1) > 0)[:, np.newaxis].astype(int)

            e_normal_dir[e_normal_dir == 1] = 1
            e_normal_dir[e_normal_dir == 0] = -1

            # determine magnitude of vectors and assign sign info
            e_tan = np.linalg.norm(e_tan, axis=1)[:, np.newaxis]
            e_normal = np.linalg.norm(e_normal, axis=1)[:, np.newaxis] * e_normal_dir

        return e_normal, e_tan

    def calc_E_on_GM_WM_surface(self, E, roi):
        """
        Determines the normal and tangential component of the induced electric field on a GM-WM surface using
        nearest neighbour principle.

        Parameters
        ----------
        E : np.ndarray of float [N_tri x 3]
            Induced electric field given in the tetrahedra centre of the mesh instance
        roi : pynibs.roi.RegionOfInterestSurface
            RegionOfInterestSurface object class instance

        Returns
        -------
        E_normal : np.ndarray of float [N_points x 3]
            Normal vector of electric field on GM-WM surface
        E_tangential : np.ndarray of float [N_points x 3]
            Tangential vector of electric field on GM-WM surface
        """

        e_gm_wm_surface = E[roi.tet_idx_nodes_mid, :]

        # determine surface normal vector (normalized)
        n = cycross(roi.node_coord_mid[roi.node_number_list[:, 1]] - roi.node_coord_mid[roi.node_number_list[:, 0]],
                    roi.node_coord_mid[roi.node_number_list[:, 2]] - roi.node_coord_mid[roi.node_number_list[:, 0]])
        n = n / np.linalg.norm(n, axis=1)[:, np.newaxis]

        # determine its normal component
        e_normal = np.multiply(np.sum(np.multiply(e_gm_wm_surface, n), axis=1)[:, np.newaxis], n)

        # compute tangential component of total electric field
        e_tan = e_gm_wm_surface - e_normal

        # determine total E on surface (sanity check)
        # E = self.calc_QOI_in_points(E, surf_mid)

        return e_normal, e_tan

    def calc_QOI_in_points(self, qoi, points_out):
        """
        Calculate QOI_out in points_out using the mesh instance and the quantity of interest (QOI).

        Parameters
        ----------
        qoi : np.ndarray of float
            Quantity of interest in nodes of tetrahedra mesh instance
        points_out : np.ndarray of float
            Point coordinates (x, y, z) where the qoi is going to be interpolated by linear basis functions

        Returns
        -------
        qoi_out : np.ndarray of float
            Quantity of interest in points_out

        """

        N_phi_points_out = points_out.shape[0]
        qoi_out = np.zeros(
                [N_phi_points_out, qoi.shape[1] if qoi.ndim > 1 else 1])

        P1_all = self.points[self.tetrahedra[:, 0], :]
        P2_all = self.points[self.tetrahedra[:, 1], :]
        P3_all = self.points[self.tetrahedra[:, 2], :]
        P4_all = self.points[self.tetrahedra[:, 3], :]

        # identify  in which tetrahedron the point lies
        # (all other volumes have at least one negative sub-volume)

        # determine all volumes (replacing points with points_out)
        # find the element where all volumes are > 0 (not inverted element)
        # get index of this tetrahedron
        # do it successively to decrease amount of volume calculations for all
        # 4 points in tetrahedra
        for i in range(N_phi_points_out):
            start = time.time()
            Vtest1 = calc_tetrahedra_volume_cross(np.tile(points_out[i, :], (P1_all.shape[0], 1)),
                                                  P2_all,
                                                  P3_all,
                                                  P4_all)
            tet_idx_bool_1 = (Vtest1 >= 0)
            tet_idx_1 = np.nonzero(tet_idx_bool_1)[0]

            Vtest2 = calc_tetrahedra_volume_cross(P1_all[tet_idx_1, :],
                                                  np.tile(
                                                          points_out[i, :], (tet_idx_1.shape[0], 1)),
                                                  P3_all[tet_idx_1, :],
                                                  P4_all[tet_idx_1, :])
            tet_idx_bool_2 = (Vtest2 >= 0)
            tet_idx_2 = tet_idx_1[np.nonzero(tet_idx_bool_2)[0]]

            Vtest3 = calc_tetrahedra_volume_cross(P1_all[tet_idx_2, :],
                                                  P2_all[tet_idx_2, :],
                                                  np.tile(
                                                          points_out[i, :], (tet_idx_2.shape[0], 1)),
                                                  P4_all[tet_idx_2, :])
            tet_idx_bool_3 = (Vtest3 >= 0)
            tet_idx_3 = tet_idx_2[np.nonzero(tet_idx_bool_3)[0]]

            Vtest4 = calc_tetrahedra_volume_cross(P1_all[tet_idx_3, :],
                                                  P2_all[tet_idx_3, :],
                                                  P3_all[tet_idx_3, :],
                                                  np.tile(points_out[i, :], (tet_idx_3.shape[0], 1)))
            tet_idx_bool_4 = (Vtest4 >= 0)
            tet_idx = tet_idx_3[np.nonzero(tet_idx_bool_4)[0]]

            # calculate subvolumes of final tetrahedron and its total volume
            Vsub1 = calc_tetrahedra_volume_cross(points_out[i, :][np.newaxis],
                                                 P2_all[tet_idx, :],
                                                 P3_all[tet_idx, :],
                                                 P4_all[tet_idx, :])
            Vsub2 = calc_tetrahedra_volume_cross(P1_all[tet_idx, :],
                                                 points_out[i, :][np.newaxis],
                                                 P3_all[tet_idx, :],
                                                 P4_all[tet_idx, :])
            Vsub3 = calc_tetrahedra_volume_cross(P1_all[tet_idx, :],
                                                 P2_all[tet_idx, :],
                                                 points_out[i, :][np.newaxis],
                                                 P4_all[tet_idx, :])
            Vsub4 = calc_tetrahedra_volume_cross(P1_all[tet_idx, :],
                                                 P2_all[tet_idx, :],
                                                 P3_all[tet_idx, :],
                                                 points_out[i, :][np.newaxis], )

            vsub = np.array([Vsub1, Vsub2, Vsub3, Vsub4])
            vtot = np.sum(vsub)

            # calculate phi_out
            qoi_out[i,] = 1.0 * np.dot(vsub.T, qoi[self.tetrahedra[tet_idx[0], :],]) / vtot

            stop = time.time()
            print(('Total: Point: {:d}/{:d} [{} sec]\n'.format(i + 1, N_phi_points_out, stop - start)))

        return qoi_out

    def calc_QOI_in_points_tet_idx(self, qoi, points_out, tet_idx):
        """
        Calculate QOI_out in points_out sitting in tet_idx using the mesh instance and the quantity of interest (QOI).

        Parameters
        ----------
        qoi : np.ndarray of float
            Quantity of interest in nodes of tetrahedra mesh instance
        points_out : np.ndarray of float
            Point coordinates (x, y, z) where the qoi is going to be interpolated by linear basis functions
        tet_idx : np.ndarray of int
            Element indices where the points_out are sitting

        Returns
        -------
        qoi_out : np.ndarray of float
            Quantity of interest in points_out

        """

        N_phi_points_out = points_out.shape[0]
        qoi_out = np.zeros([N_phi_points_out, qoi.shape[1] if qoi.ndim > 1 else 1])

        P1_all = self.points[self.tetrahedra[:, 0], :]
        P2_all = self.points[self.tetrahedra[:, 1], :]
        P3_all = self.points[self.tetrahedra[:, 2], :]
        P4_all = self.points[self.tetrahedra[:, 3], :]

        # determine sub-volumes
        Vsub1 = calc_tetrahedra_volume_cross(points_out,
                                             P2_all[tet_idx, :],
                                             P3_all[tet_idx, :],
                                             P4_all[tet_idx, :])
        Vsub2 = calc_tetrahedra_volume_cross(P1_all[tet_idx, :],
                                             points_out,
                                             P3_all[tet_idx, :],
                                             P4_all[tet_idx, :])
        Vsub3 = calc_tetrahedra_volume_cross(P1_all[tet_idx, :],
                                             P2_all[tet_idx, :],
                                             points_out,
                                             P4_all[tet_idx, :])
        Vsub4 = calc_tetrahedra_volume_cross(P1_all[tet_idx, :],
                                             P2_all[tet_idx, :],
                                             P3_all[tet_idx, :],
                                             points_out)
        Vsub = np.hstack([Vsub1, Vsub2, Vsub3, Vsub4])
        Vtot = np.sum(Vsub, axis=1)

        # calculate the QOIs in the tetrahedron of interest
        for i in range(qoi.shape[1]):
            qoi_out[:, i] = 1.0 * np.sum(np.multiply(Vsub, qoi[self.tetrahedra[tet_idx, :], i]), axis=1) / Vtot

        # for i in range(N_phi_points_out):
        #     # calculate subvolumes of final tetrahedron and its total volume
        #     Vsub1 = calc_tetrahedra_volume_cross(points_out[i, :][np.newaxis],
        #                                               P2_all[tet_idx[i], :][np.newaxis],
        #                                               P3_all[tet_idx[i], :][np.newaxis],
        #                                               P4_all[tet_idx[i], :][np.newaxis])
        #     Vsub2 = calc_tetrahedra_volume_cross(P1_all[tet_idx[i], :][np.newaxis],
        #                                               points_out[i, :][np.newaxis],
        #                                               P3_all[tet_idx[i], :][np.newaxis],
        #                                               P4_all[tet_idx[i], :][np.newaxis])
        #     Vsub3 = calc_tetrahedra_volume_cross(P1_all[tet_idx[i], :][np.newaxis],
        #                                               P2_all[tet_idx[i], :][np.newaxis],
        #                                               points_out[i, :][np.newaxis],
        #                                               P4_all[tet_idx[i], :][np.newaxis])
        #     Vsub4 = calc_tetrahedra_volume_cross(P1_all[tet_idx[i], :][np.newaxis],
        #                                               P2_all[tet_idx[i], :][np.newaxis],
        #                                               P3_all[tet_idx[i], :][np.newaxis],
        #                                               points_out[i, :][np.newaxis])
        #
        #     Vtot = np.sum([Vsub1, Vsub2, Vsub3, Vsub4])
        #
        #     # calculate the QOIs in the tetrahedron of interest
        #     qoi_out[i,] = 1.0 * np.dot(Vsub.T, qoi[self.tetrahedra[tet_idx[i], :],]) / Vtot

        return qoi_out

    def data_nodes2elements(self, data):
        """
        Interpolate data given in the nodes to the tetrahedra center.

        Parameters
        ----------
        data : np.ndarray [N_nodes x N_data]
            Data in nodes

        Returns
        -------
        data_elements : np.ndarray [N_elements x N_data]
            Data in elements
        """
        data_elements = np.sum(data[self.tetrahedra[:, i]] for i in range(4)) / 4.0

        return data_elements

    def data_elements2nodes(self, data):
        """
        Transforms an data in tetrahedra into the nodes after Zienkiewicz et al. (1992) [1].
        Can only transform volume data, i.e. needs the data in the surrounding tetrahedra to average it to the nodes.
        Will not work well for discontinuous fields (like E, if several tissues are used).

        Parameters
        ----------
        data : np.ndarray [N_elements x N_data]
            Data in tetrahedra

        Returns
        -------
        data_nodes : np.ndarray [N_nodes x N_data]
            Data in nodes

        Notes
        -----
        .. [1] Zienkiewicz, Olgierd Cecil, and Jian Zhong Zhu. "The superconvergent patch recovery and a
           posteriori error estimates. Part 1: The recovery technique." International Journal for
           Numerical Methods in Engineering 33.7 (1992): 1331-1364.
        """

        # check dimension of input data
        if data.ndim == 1:
            data = data[:, np.newaxis]

        N_data = data.shape[1]
        data_nodes = np.zeros((self.N_points, N_data))

        if self.N_tet != data.shape[0]:
            raise ValueError("The number of data points in the data has to be equal to the number"
                             "of elements in the mesh")

        value = np.atleast_2d(data)
        if value.shape[0] < value.shape[1]:
            value = value.T

        # nd = np.zeros((self.N_points, N_data))

        # get all nodes used in tetrahedra, creates the NodeData structure
        # uq = np.unique(msh.elm[msh.elm.tetrahedra])
        # nd = NodeData(np.zeros((len(uq), self.nr_comp)), self.field_name, mesh=msh)
        # nd.node_number = uq

        # Get the point in the outside surface
        points_outside = np.unique(self.get_outside_faces())
        outside_points_mask = np.in1d(self.tetrahedra, points_outside).reshape(-1, 4)
        masked_th_nodes = np.copy(self.tetrahedra)
        masked_th_nodes[outside_points_mask] = -1

        # Calculates the quantities needed for the superconvergent patch recovery
        uq_in, th_nodes = np.unique(masked_th_nodes, return_inverse=True)

        baricenters = self.tetrahedra_center
        volumes = self.tetrahedra_volume
        baricenters = np.hstack([np.ones((baricenters.shape[0], 1)), baricenters])

        A = np.empty((len(uq_in), 4, 4))
        b = np.empty((len(uq_in), 4, N_data), 'float64')
        for i in range(4):
            for j in range(i, 4):
                A[:, i, j] = np.bincount(th_nodes.reshape(-1),
                                         np.repeat(baricenters[:, i], 4) *
                                         np.repeat(baricenters[:, j], 4))
        A[:, 1, 0] = A[:, 0, 1]
        A[:, 2, 0] = A[:, 0, 2]
        A[:, 3, 0] = A[:, 0, 3]
        A[:, 2, 1] = A[:, 1, 2]
        A[:, 3, 1] = A[:, 1, 3]
        A[:, 3, 2] = A[:, 2, 3]

        for j in range(N_data):
            for i in range(4):
                b[:, i, j] = np.bincount(th_nodes.reshape(-1),
                                         np.repeat(baricenters[:, i], 4) *
                                         np.repeat(value[:, j], 4))

        a = np.linalg.solve(A[1:], b[1:])
        p = np.hstack([np.ones((len(uq_in) - 1, 1)), self.points[uq_in[1:]]])
        f = np.einsum('ij, ijk -> ik', p, a)
        data_nodes[uq_in[1:]] = f

        # Assigns the average value to the points in the outside surface
        masked_th_nodes = np.copy(self.tetrahedra)
        masked_th_nodes[~outside_points_mask] = -1
        uq_out, th_nodes_out = np.unique(masked_th_nodes, return_inverse=True)

        sum_vals = np.empty((len(uq_out), N_data), 'float64')

        for j in range(N_data):
            sum_vals[:, j] = np.bincount(th_nodes_out.reshape(-1),
                                         np.repeat(value[:, j], 4) *
                                         np.repeat(volumes, 4))

        sum_vols = np.bincount(th_nodes_out.reshape(-1), np.repeat(volumes, 4))

        data_nodes[uq_out[1:]] = (sum_vals / sum_vols[:, None])[1:]

        return data_nodes

    def get_outside_faces(self, tetrahedra_indexes=None):
        """
        Creates a list of nodes in each face that are in the outer volume.

        Parameters
        ----------
        tetrahedra_indices : np.ndarray
            Indices of the tetrehedra where the outer volume is to be determined (default: all tetrahedra)

        Returns
        -------
        faces : np.ndarray
            List of nodes in faces in arbitrary order
        """

        if tetrahedra_indexes is None:
            tetrahedra_indexes = self.tetrahedra_index

        th = self.tetrahedra[tetrahedra_indexes]
        faces = th[:, [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]]
        faces = faces.reshape(-1, 3)
        hash_array = np.array([hash(f.tobytes()) for f in np.sort(faces, axis=1)])
        unique, idx, inv, count = np.unique(hash_array, return_index=True,
                                            return_inverse=True, return_counts=True)

        # if np.any(count > 2):
        #     raise ValueError('Invalid Mesh: Found a face with more than 2 adjacent'
        #                      ' tetrahedra!')

        outside_faces = faces[idx[count == 1]]

        return outside_faces

    def calc_gradient(self, phi):
        """
        Calculate gradient of scalar DOF in tetrahedra center.

        Parameters
        ----------
        phi : np.ndarray of float [N_nodes]
            Scalar DOF the gradient is calculated for

        Returns
        -------
        grad_phi : np.ndarray of float [N_tet x 3]
            Gradient of Scalar DOF in tetrahedra center
        """

        a1 = np.vstack((self.points[self.tetrahedra[:, 3], :] - self.points[self.tetrahedra[:, 1], :],
                        self.points[self.tetrahedra[:, 2], :] -
                        self.points[self.tetrahedra[:, 0], :],
                        self.points[self.tetrahedra[:, 3], :] -
                        self.points[self.tetrahedra[:, 0], :],
                        self.points[self.tetrahedra[:, 1], :] - self.points[self.tetrahedra[:, 0], :]))

        a2 = np.vstack((self.points[self.tetrahedra[:, 2], :] - self.points[self.tetrahedra[:, 1], :],
                        self.points[self.tetrahedra[:, 3], :] -
                        self.points[self.tetrahedra[:, 0], :],
                        self.points[self.tetrahedra[:, 1], :] -
                        self.points[self.tetrahedra[:, 0], :],
                        self.points[self.tetrahedra[:, 2], :] - self.points[self.tetrahedra[:, 0], :]))

        a3 = np.vstack((self.points[self.tetrahedra[:, 0], :] - self.points[self.tetrahedra[:, 1], :],
                        self.points[self.tetrahedra[:, 1], :] -
                        self.points[self.tetrahedra[:, 0], :],
                        self.points[self.tetrahedra[:, 2], :] -
                        self.points[self.tetrahedra[:, 0], :],
                        self.points[self.tetrahedra[:, 3], :] - self.points[self.tetrahedra[:, 0], :]))

        volumes = np.sum(np.multiply(cycross(a1, a2), a3), 1)
        volumes = volumes[:, np.newaxis]
        Dlambda = np.transpose(np.reshape(cycross(
                a1, a2) / np.tile(volumes, (1, 3)), (self.N_tet, 4, 3), order='F'), (0, 2, 1))

        grad_phi = np.zeros((self.N_tet, 3))
        # calculate gradient at barycenters of tetrahedra
        for j in range(4):
            grad_phi = grad_phi + Dlambda[:, :, j] * np.tile(phi[self.tetrahedra[:, j]], (1, 3))

        return grad_phi

    def calc_E(self, grad_phi, omegaA):
        """
        Calculate electric field with gradient of electric potential and omega-scaled magnetic vector potential A.

        .. math:: \mathbf{E}=-\\nabla\\varphi-\omega\mathbf{A}

        Parameters
        ----------
        grad_phi : np.ndarray of float [N_tet x 3]
            Gradient of Scalar DOF in tetrahedra center
        omegaA : np.ndarray of float [N_tet x 3]
            Magnetic vector potential in tetrahedra center (scaled with angular frequency omega)

        Returns
        -------
        E : np.ndarray of float [N_tet x 3]
            Electric field in tetrahedra center
        """

        E = -grad_phi - omegaA

        return E

    def calc_J(self, E, sigma):
        """ Calculate current density J. The conductivity sigma is a list of np.arrays containing conductivities of
        regions (scalar and/or tensor).

        .. math::
            \mathbf{J} = [\sigma]\mathbf{E}

        Parameters
        ----------
        E : np.ndarray of float [N_tet x 3]
            Electric field in tetrahedra center
        sigma : list of np.ndarray of float [N_regions][3 x 3]
            Conductivities of regions (scalar and/or tensor).

        Returns
        -------
        E : np.ndarray of float [N_tet x 3]
            Electric field in tetrahedra center
        """

        J = np.zeros((E.shape[0], 3))

        for i in range(self.N_region):
            tet_bool_idx = self.tetrahedra_regions == self.region[i]
            J[tet_bool_idx[:, 0], :] = np.dot(
                    sigma[i], E[tet_bool_idx[:, 0], :].T).T
        return J

    def calc_surface_adjacent_tetrahedra_idx_list(self, fname):
        """
        Determine the indices of the tetrahedra touching the surfaces and save the indices into a .txt file specified
        with fname.

        Parameters
        ----------
        fname : str
            Filename of output .txt file

        Returns
        -------
        <File> : .txt file
            Element indices of the tetrahedra touching the surfaces (outer-most elements)
        """

        # determine indices of the 2 adjacent tetrahedra with common face on
        # surface
        P1_idx = np.zeros((self.N_tet, 1), dtype=bool)
        P2_idx = np.zeros((self.N_tet, 1), dtype=bool)
        P3_idx = np.zeros((self.N_tet, 1), dtype=bool)
        tet_idx_pos = np.zeros((self.N_tri, 1)).astype(int)
        tet_idx_neg = np.zeros((self.N_tri, 1)).astype(int)

        start = time.time()

        tetrahedra0 = self.tetrahedra[:, 0]
        tetrahedra1 = self.tetrahedra[:, 1]
        tetrahedra2 = self.tetrahedra[:, 2]
        tetrahedra3 = self.tetrahedra[:, 3]

        for i in range(self.N_tri):

            if (not (i % 100) and i > 0):
                stop = time.time()
                print(('Tri: {:d}/{:d} [{} sec]\n'.format(i, self.N_tri, stop - start)))
                start = time.time()

            triangle = set(self.triangles[i, :])

            triangle0 = self.triangles[i, 0]
            triangle1 = self.triangles[i, 1]
            triangle2 = self.triangles[i, 2]

            P1_idx = (tetrahedra0 == triangle0) | (tetrahedra1 == triangle0) | (
                    tetrahedra2 == triangle0) | (tetrahedra3 == triangle0)
            P2_idx = (tetrahedra0 == triangle1) | (tetrahedra1 == triangle1) | (
                    tetrahedra2 == triangle1) | (tetrahedra3 == triangle1)
            P3_idx = (tetrahedra0 == triangle2) | (tetrahedra1 == triangle2) | (
                    tetrahedra2 == triangle2) | (tetrahedra3 == triangle2)

            tet_bool_idx = P1_idx & P2_idx & P3_idx
            tet_idx = np.where(tet_bool_idx)[0][:]

            # get 4th (test) point of e.g. first tetrahedron which is not in
            # plane
            P4_idx = list(set(self.tetrahedra[tet_idx[0], :]) - triangle)

            # calculate projection of the line between:
            # center of triangle -> 4th point
            # and
            # normal of the triangle
            c = np.dot(
                    self.points[P4_idx, :] - self.triangles_center[i, :], self.triangles_normal[i, :])

            # positive projection: normal points to the 4th (test) point of first tetrahedron
            # and first tetrahedron is on "positive" side

            # outermost surface (has only one adjacent tetrahedron)
            if len(tet_idx) == 1:
                if c > 0:
                    tet_idx_pos[i] = tet_idx[0]
                    tet_idx_neg[i] = -1

                else:
                    tet_idx_pos[i] = -1
                    tet_idx_neg[i] = tet_idx[0]

            # inner surfaces have 2 adjacent tetrahedra
            else:
                if c > 0:
                    tet_idx_pos[i] = tet_idx[0]
                    tet_idx_neg[i] = tet_idx[1]
                else:
                    tet_idx_pos[i] = tet_idx[1]
                    tet_idx_neg[i] = tet_idx[0]

        # save the indices of the tetrahedra sharing the surfaces (negative,
        # i.e. bottom side first)
        self.tetrahedra_triangle_surface_idx = np.hstack(
                [tet_idx_neg, tet_idx_pos])
        f = open(fname, 'w')
        np.savetxt(f, self.tetrahedra_triangle_surface_idx, '%d')
        f.close()

    def calc_E_normal_tangential_surface(self, E, fname):
        """
        Calculate normal and tangential component of electric field on given surfaces of mesh instance.

        Parameters
        ----------
        E : np.ndarray of float [N_tri x 3]
            Electric field data on surfaces
        fname : str
            Filename of the .txt file containing the tetrahedra indices, which are adjacent to the surface triangles
            generated by the method "calc_surface_adjacent_tetrahedra_idx_list(self, fname)"

        Returns
        -------
        En_pos : np.ndarray of float [N_tri x 3]
            Normal component of electric field of top side (outside) of surface
        En_neg : np.ndarray of float [N_tri x 3]
            Normal component of electric field of bottom side (inside) of surface
        n : np.ndarray of float [N_tri x 3]
            Normal vector
        Et : np.ndarray of float [N_tri x 3]
            Tangential component of electric field lying in surface
        t : np.ndarray of float [N_tri x 3]
            Tangential vector
        """

        n = self.triangles_normal
        En_pos = np.zeros((self.N_tri, 1))
        En_neg = np.zeros((self.N_tri, 1))
        Et = np.zeros((self.N_tri, 1))
        t = np.zeros((self.N_tri, 3))
        self.tetrahedra_triangle_surface_idx = np.loadtxt(fname).astype(int)

        for i in range(self.N_tri):
            En_neg[i, 0] = np.dot(
                    E[self.tetrahedra_triangle_surface_idx[i, 0], :], n[i, :])

            if self.tetrahedra_triangle_surface_idx[i, 1] > -1:
                En_pos[i, 0] = np.dot(
                        E[self.tetrahedra_triangle_surface_idx[i, 1], :], n[i, :])
            else:
                En_pos[i, 0] = np.nan

            t[i, :] = E[self.tetrahedra_triangle_surface_idx[i, 0], :] - \
                      1.0 * En_neg[i, 0] * n[i, :]
            Et[i, 0] = np.linalg.norm(t[i, :])
            t[i, :] = t[i, :] / Et[i, 0] if Et[i, 0] > 0 else np.zeros(3)

        return En_pos, En_neg, n, Et, t

    def get_faces(self, tetrahedra_indexes=None):
        """
        Creates a list of nodes in each face and a list of faces in each tetrahedra.

        Parameters
        ----------
        tetrahedra_indexes : np.ndarray
            Indices of the tetrehedra where the faces are to be determined (default: all tetrahedra)

        Returns
        -------
        faces : np.ndarray
            List of nodes in faces, in arbitrary order
        th_faces : np.ndarray
            List of faces in each tetrahedra, starts at 0, order=((0, 2, 1), (0, 1, 3), (0, 3, 2), (1, 2, 3))
        face_adjacency_list : np.ndarray
            List of tetrahedron adjacent to each face, filled with -1 if a face is in a
            single tetrahedron. Not in the normal element ordering, but only in the order
            the tetrahedra are presented
        """

        if tetrahedra_indexes is None:
            tetrahedra_indexes = np.arange(self.tetrahedra.shape[0])
        # th = self[tetrahedra_indexes]
        th = self.tetrahedra[tetrahedra_indexes, :]
        faces = th[:, [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]]
        faces = faces.reshape(-1, 3)
        hash_array = np.array([hash(f.tobytes()) for f in np.sort(faces, axis=1)])
        unique, idx, inv, count = np.unique(hash_array, return_index=True,
                                            return_inverse=True, return_counts=True)
        faces = faces[idx]
        face_adjacency_list = -np.ones((len(unique), 2), dtype=int)
        face_adjacency_list[:, 0] = idx // 4

        # if np.any(count > 2):
        #     raise ValueError('Invalid Mesh: Found a face with more than 2 adjacent'
        #                      ' tetrahedra!')

        # Remove the faces already seen from consideration
        # Second round in order to make adjacency list
        # create a new array with a mask in the elements already seen
        mask = unique[-1] + 1
        hash_array_masked = np.copy(hash_array)
        hash_array_masked[idx] = mask
        # make another array, where we delete the elements we have already seen
        hash_array_reduced = np.delete(hash_array, idx)
        # Finds where each element of the second array is in the first array
        # (https://stackoverflow.com/a/8251668)
        hash_array_masked_sort = hash_array_masked.argsort()
        hash_array_repeated_pos = hash_array_masked_sort[
            np.searchsorted(hash_array_masked[hash_array_masked_sort], hash_array_reduced)]
        # Now find the index of the face corresponding to each element in the
        # hash_array_reduced
        faces_repeated = np.searchsorted(unique, hash_array_reduced)
        # Finally, fill out the second column in the adjacency list
        face_adjacency_list[faces_repeated, 1] = hash_array_repeated_pos // 4

        return faces, inv.reshape(-1, 4), face_adjacency_list


def determine_e_midlayer_workhorse(fn_e_results, subject, mesh_idx, midlayer_fun, fn_mesh_hdf5, roi_idx, phi_scaling=1.,
                                   verbose=False):
    """
    phi_scaling: float
        simnibs < 3.0  : 1000.
        simnibs >= 3.0 :    1. (Default)
    """

    if verbose:
        print(f"Loading Mesh and ROI {roi_idx} from {fn_mesh_hdf5}")

    msh = pynibs.load_mesh_hdf5(fn_mesh_hdf5)
    roi = pynibs.load_roi_surface_obj_from_hdf5(fn_mesh_hdf5)

    for fn_e in fn_e_results:

        with h5py.File(fn_e + ".hdf5", 'r') as f:
            phi = f['data/nodes/v'][:][:, np.newaxis]
            # phi = f['data/potential'][:][:, np.newaxis]
            dadt = f['data/nodes/D'][:]
            # dadt = np.reshape(f['data/dAdt'][:], (phi.shape[0], 3), order="c")

        # determine e_norm and e_tan for every simulation
        if verbose:
            print(f"Determine midlayer E-field for {fn_e}.hdf5")

        # choose which function to use for midlayer computation
        if midlayer_fun == "pynibs":
            e_norm_temp, e_tan_temp = msh.calc_E_on_GM_WM_surface3(phi=phi * phi_scaling,
                                                                   dAdt=dadt,
                                                                   roi=roi[roi_idx],
                                                                   verbose=False,
                                                                   mode='magnitude')

            e_norm_temp = e_norm_temp.flatten() * -1
            e_tan_temp = e_tan_temp.flatten()
            e_mag_temp = np.linalg.norm(np.vstack([e_norm_temp, e_tan_temp]).transpose(), axis=1).flatten()

        elif midlayer_fun == "simnibs":
            e_norm_temp_simnibs, e_tan_temp_simnibs = msh.calc_E_on_GM_WM_surface_simnibs_KW(phi=phi * phi_scaling,
                                                                                             dAdt=dadt,
                                                                                             roi=roi[roi_idx],
                                                                                             verbose=False,
                                                                                             subject=subject,
                                                                                             mesh_idx=mesh_idx)

            e_norm_temp_simnibs = e_norm_temp_simnibs.flatten()
            e_tan_temp_simnibs = e_tan_temp_simnibs.flatten()
            e_mag_temp_simnibs = np.linalg.norm(np.vstack([e_norm_temp_simnibs, e_tan_temp_simnibs]).transpose(),
                                                axis=1).flatten()
        else:
            raise ValueError(f"midlayer_fun {midlayer_fun} not implemented.")

        del phi, dadt

        with h5py.File(fn_e + ".hdf5", 'a') as f:
            try:
                del f['data/midlayer/roi_surface/{}/E_mag'.format(roi_idx)]
                del f['data/midlayer/roi_surface/{}/E_tan'.format(roi_idx)]
                del f['data/midlayer/roi_surface/{}/E_norm'.format(roi_idx)]
            except KeyError:
                pass

            f.create_dataset('data/midlayer/roi_surface/{}/E_mag'.format(roi_idx), data=e_mag_temp_simnibs)
            f.create_dataset('data/midlayer/roi_surface/{}/E_tan'.format(roi_idx), data=e_tan_temp_simnibs)
            f.create_dataset('data/midlayer/roi_surface/{}/E_norm'.format(roi_idx), data=e_norm_temp_simnibs)

        if verbose:
            print("\tAdding results to {}".format(fn_e + ".hdf5"))


def determine_e_midlayer(fn_e_results, fn_mesh_hdf5, subject, mesh_idx, roi_idx, n_cpu=4, midlayer_fun="simnibs",
                         phi_scaling=1., verbose=False):
    """
    Parallel version to determine the midlayer e-fields from a list of .hdf5 results files

    Parameters
    ----------
    fn_e_results : list of str
        List of results filenames (.hdf5 format)
    fn_mesh_hdf5 : str
        Filename of corresponding mesh file
    subject : pynibs.Subject
        Subject object
    mesh_idx : int
        Mesh index
    roi_idx : int
        ROI index
    n_cpu : int, optional, default: 4
        Number of parallel computations
    midlayer_fun : str, optional, default: "simnibs"
        Method to determine the midlayer e-fields ("pynibs" or "simnibs")
    phi_scaling : float, optional, default: 1.0
        Scaling factor of scalar potential to change between "m" and "mm"

    Returns
    -------
    <File> .hdf5 file
        Adds midlayer e-field results to ROI
    """

    # msh = pynibs.load_mesh_msh(subject.mesh[mesh_idx]['fn_mesh_msh'])

    n_cpu_available = multiprocessing.cpu_count()
    n_cpu = min(n_cpu, n_cpu_available)

    workhorse_partial = partial(determine_e_midlayer_workhorse,
                                subject=subject,
                                mesh_idx=mesh_idx,
                                midlayer_fun=midlayer_fun,
                                fn_mesh_hdf5=fn_mesh_hdf5,
                                roi_idx=roi_idx,
                                phi_scaling=phi_scaling,
                                verbose=verbose)

    fn_e_results_chunks = pynibs.compute_chunks(fn_e_results, n_cpu)
    pool = multiprocessing.Pool(n_cpu)
    pool.map(workhorse_partial, fn_e_results_chunks)
    pool.close()
    pool.join()


def project_on_scalp_hdf5(coords, mesh, scalp_tag=1005):
    """
    Find the node in the scalp closest to each coordinate

    Parameters
    -------
    coords: nx3 np.ndarray
        Vectors to be transformed
    mesh: str or pynibs.TetrahedraLinear
        Filename of mesh in .hdf5 format or Mesh structure
    scalp_tag: int (optional)
        Tag in the mesh where the scalp is to be set. Default: 1005

    Returns
    ------
    points_closest: nx3 np.ndarray
        coordinates projected scalp (closest skin points)
    """

    # read head mesh and extract skin surface
    if isinstance(mesh, str):
        mesh = pynibs.load_mesh_hdf5(mesh)

    if coords.ndim == 1:
        coords = coords[np.newaxis,]

    # crop to skin surface
    triangles_skin = mesh.triangles[mesh.triangles_regions == scalp_tag]
    point_idx_skin = np.unique(triangles_skin)
    points_skin = mesh.points[point_idx_skin]

    # find points with smalled euclidean distance
    points_closest = np.zeros(coords.shape)
    for i, c in enumerate(coords):
        points_closest[i,] = points_skin[np.argmin(np.linalg.norm(points_skin - c, axis=1)),]

    return points_closest


def project_on_scalp(coords, mesh, scalp_tag=1005):
    """
    Find the node in the scalp closest to each coordinate

    Parameters
    ----------
    coords: nx3 np.ndarray
        Vectors to be transformed
    mesh: pynibs.TetrahedraLinear or simnibs.msh.mesh_io.Msh
        Mesh structure in simnibs or pynibs format
    scalp_tag: int, optional, default: 1005
        Tag in the mesh where the scalp is to be set. Default: 1005

    Returns
    -------
    points_closest: np.ndarry
        (n, 3) coordinates projected scalp (closest skin points)
    """
    from simnibs.msh.transformations import project_on_scalp as project_on_scalp_msh
    from simnibs.msh.mesh_io import Msh

    if isinstance(mesh, TetrahedraLinear):
        points_closest = project_on_scalp_hdf5(coords=coords, mesh=mesh, scalp_tag=scalp_tag)
    elif isinstance(mesh, Msh):
        points_closest = project_on_scalp_msh(coords=coords, mesh=mesh, scalp_tag=scalp_tag, distance=0.)
    else:
        raise ValueError(f"Unknown mesh type: {type(mesh)}.")

    return points_closest


def refine_surface(fn_surf, fn_surf_refined, center, radius, repair=True, remesh=True, verbose=True):
    """
    Refines surface (.stl) in spherical ROI an saves as .stl file.

    Parameters
    ----------
    fn_surf : str
        Input filename (.stl)
    fn_surf_refined : str
        Output filename (.stl)
    center : np.ndarray of float (3)
        Center of spherical ROI (x,y,z)
    radius : float
        Radius of ROI
    repair : bool, optional, default: True
        Repair surface mesh to ensure that it is watertight and forms a volume
    remesh : bool, optional, default:False
        Perform remeshing with meshfix (also removes possibly overlapping facets and intersections)
    verbose : bool, optional, default: True
        Print output messages
    Returns
    -------
    <file>: .stl file
    """
    radius_ = radius + 2
    refine = True

    while refine:
        if verbose:
            print(f"Loading {fn_surf} ...")
        # reading original .stl file
        wm = trimesh.load(fn_surf)

        tris = wm.faces
        tris_center = wm.triangles_center
        points = wm.vertices

        # Splitting elements by adding tris_center to points in ROI
        mask_roi = np.linalg.norm(tris_center - center, axis=1) < radius
        ele_idx_roi = np.where(np.linalg.norm(tris_center - center, axis=1) < radius)[0]
        points_refine = points
        tris_refine = tris

        if verbose:
            print(f"Splitting elements ...")

        for ele_idx in tqdm(ele_idx_roi):
            points_idx_ele = tris[ele_idx, :]
            p_0 = points[points_idx_ele[0], :]
            p_1 = points[points_idx_ele[1], :]
            p_2 = points[points_idx_ele[2], :]
            p_01 = p_0 + 0.5 * (p_1 - p_0)
            p_02 = p_0 + 0.5 * (p_2 - p_0)
            p_12 = p_1 + 0.5 * (p_2 - p_1)

            points_refine = np.vstack((points_refine, p_01, p_02, p_12))

            mask_roi = np.hstack((mask_roi, False, False, False, False))

            # add 6 new triangles
            p_0_idx = points_idx_ele[0]
            p_1_idx = points_idx_ele[1]
            p_2_idx = points_idx_ele[2]
            p_01_idx = points_refine.shape[0] - 3
            p_02_idx = points_refine.shape[0] - 2
            p_12_idx = points_refine.shape[0] - 1

            # adding 4 elements
            tris_refine = np.vstack((tris_refine, np.array([[p_0_idx, p_01_idx, p_02_idx],
                                                            [p_01_idx, p_1_idx, p_12_idx],
                                                            [p_02_idx, p_12_idx, p_2_idx],
                                                            [p_01_idx, p_12_idx, p_02_idx]])))

        ele_idx_del = []

        if radius != np.inf:
            if verbose:
                print(f"Adding triangles in surrounding elements ...")
            # add triangles in surrounding elements
            ele_sur_idx = np.where(np.logical_and(np.linalg.norm(tris_center - center, axis=1) < radius_,
                                                  np.linalg.norm(tris_center - center, axis=1) >= radius))[0]

            for ele_sur in tqdm(ele_sur_idx):
                points_idx_ele = tris[ele_sur, :]
                p_0 = points[points_idx_ele[0], :]
                p_1 = points[points_idx_ele[1], :]
                p_2 = points[points_idx_ele[2], :]
                p_01 = p_0 + 0.5 * (p_1 - p_0)
                p_02 = p_0 + 0.5 * (p_2 - p_0)
                p_12 = p_1 + 0.5 * (p_2 - p_1)

                p_0_idx = points_idx_ele[0]
                p_1_idx = points_idx_ele[1]
                p_2_idx = points_idx_ele[2]

                p_on_02 = False
                p_on_12 = False
                p_on_01 = False

                if (np.sum(p_01 == points_refine, axis=1) == 3).any():
                    p_on_01 = True

                if (np.sum(p_02 == points_refine, axis=1) == 3).any():
                    p_on_02 = True

                if (np.sum(p_12 == points_refine, axis=1) == 3).any():
                    p_on_12 = True

                # no edge with point
                if not p_on_01 and not p_on_02 and not p_on_12:
                    pass

                # one edge with point
                elif p_on_01 and not p_on_02 and not p_on_12:
                    ele_idx_del.append(ele_sur)
                    p_01_idx = np.where(np.sum(points_refine == p_01, axis=1) == 3)[0][0]
                    tris_refine = np.vstack((tris_refine, np.array([[p_0_idx, p_01_idx, p_2_idx],
                                                                    [p_01_idx, p_1_idx, p_2_idx]])))

                elif p_on_02 and not p_on_01 and not p_on_12:
                    ele_idx_del.append(ele_sur)
                    p_02_idx = np.where(np.sum(points_refine == p_02, axis=1) == 3)[0][0]
                    tris_refine = np.vstack((tris_refine, np.array([[p_0_idx, p_1_idx, p_02_idx],
                                                                    [p_02_idx, p_1_idx, p_2_idx]])))

                elif p_on_12 and not p_on_02 and not p_on_01:
                    ele_idx_del.append(ele_sur)
                    p_12_idx = np.where(np.sum(points_refine == p_12, axis=1) == 3)[0][0]
                    tris_refine = np.vstack((tris_refine, np.array([[p_0_idx, p_1_idx, p_12_idx],
                                                                    [p_0_idx, p_12_idx, p_2_idx]])))

                # 2 edges with points
                elif p_on_02 and p_on_12 and not p_on_01:
                    ele_idx_del.append(ele_sur)
                    p_12_idx = np.where(np.sum(points_refine == p_12, axis=1) == 3)[0][0]
                    p_02_idx = np.where(np.sum(points_refine == p_02, axis=1) == 3)[0][0]
                    tris_refine = np.vstack((tris_refine, np.array([[p_0_idx, p_1_idx, p_02_idx],
                                                                    [p_1_idx, p_12_idx, p_02_idx],
                                                                    [p_02_idx, p_12_idx, p_2_idx]])))

                elif p_on_02 and p_on_01 and not p_on_12:
                    ele_idx_del.append(ele_sur)
                    p_01_idx = np.where(np.sum(points_refine == p_01, axis=1) == 3)[0][0]
                    p_02_idx = np.where(np.sum(points_refine == p_02, axis=1) == 3)[0][0]
                    tris_refine = np.vstack((tris_refine, np.array([[p_0_idx, p_01_idx, p_02_idx],
                                                                    [p_01_idx, p_2_idx, p_02_idx],
                                                                    [p_01_idx, p_1_idx, p_2_idx]])))

                elif p_on_01 and p_on_12 and not p_on_02:
                    ele_idx_del.append(ele_sur)
                    p_01_idx = np.where(np.sum(points_refine == p_01, axis=1) == 3)[0][0]
                    p_12_idx = np.where(np.sum(points_refine == p_12, axis=1) == 3)[0][0]
                    tris_refine = np.vstack((tris_refine, np.array([[p_0_idx, p_01_idx, p_2_idx],
                                                                    [p_01_idx, p_12_idx, p_2_idx],
                                                                    [p_01_idx, p_1_idx, p_12_idx]])))

        if verbose:
            print("Deleting old triangles ...")

        # delete old triangles
        ele_idx_roi = np.where(mask_roi)[0]
        ele_idx_lst_del = ele_idx_del + list(ele_idx_roi)
        tris_refine = np.delete(tris_refine, ele_idx_lst_del, 0)

        points_refine = np.round_(points_refine, 5)

        # # delete duplicate points
        # p_added = points_refine[points.shape[0]:, :]
        #
        # point_idx_del = np.array([])
        # for i_p, p in tqdm(enumerate(p_added)):
        #
        #     p_idx = np.where(np.sum(p == points_refine, axis=1) == 3)[0]
        #
        #     if len(p_idx) > 1:
        #         if p_idx[1] not in point_idx_del:
        #             point_idx_del = np.hstack((point_idx_del, p_idx[1:]))
        #
        #             # loop over point_idx_del and replace with first point idx
        #             for p_d_idx in p_idx[1:]:
        #                 tris_refine[tris_refine == p_d_idx] = p_idx[0]
        #
        # point_idx_keep = [i for i in range(points_refine.shape[0]) if i not in point_idx_del]
        # point_idx_new = [i for i in range(len(point_idx_keep))]
        # points_refine = points_refine[point_idx_keep, :]
        #
        # # renumber
        # for p_idx_keep, p_idx_new in zip(point_idx_keep[points.shape[0]:], point_idx_new[points.shape[0]:]):
        #     tris_refine[tris_refine == p_idx_keep] = p_idx_new

        # create new trimesh
        mesh = trimesh.Trimesh(vertices=points_refine,
                               faces=tris_refine)

        if repair:
            if mesh.is_watertight:
                if verbose:
                    print(f"Surface is watertight ...")
                mesh_ok = True
            else:
                if verbose:
                    print(f"Surface is NOT watertight ... trying to repair mesh ... ")
                # repair mesh
                trimesh.repair.fill_holes(mesh)

                if mesh.is_watertight:
                    if verbose:
                        print(f"Surface repaired ...")
                    mesh_ok = True

                else:
                    mesh_ok = False
                    radius -= 1
                    radius_ = radius + 2

                    if verbose:
                        print(f"WARNING: Could not repair refined surface ... "
                              f"shrinking radius by 1 mm to {radius} mm")
        else:
            mesh_ok = True

        if mesh_ok:
            if verbose:
                print(f"Saving {fn_surf_refined} ...")
            mesh.export(fn_surf_refined, file_type='stl_ascii')

            if remesh:
                # remesh surface
                print(f"Remeshing {fn_surf_refined} ...")
                command = f"meshfix {fn_surf_refined} -a 2.0 -u 1 -q --shells 9 " \
                          f"--stl -o {fn_surf_refined}"
                os.popen(command).read()

            refine = False


def find_element_idx_by_points(nodes, con, points):
    """
    Finds the tetrahedral element index of an arbitrary point in the FEM mesh.

    Parameters
    ----------
    nodes : np.ndarray [N_nodes x 3]
        Coordinates (x, y, z) of the nodes
    con : np.ndarray [N_tet x 4]
        Connectivity matrix
    points : np.ndarray [N_points x 3]
        Points for which the element indices are found.

    Returns
    -------
    ele_idx : np.ndarray [N_points]
        Element indices of tetrahedra where corresponding 'points' are lying in
    """

    node_idx = []
    for i in range(points.shape[0]):
        node_idx.append(np.where(np.linalg.norm(nodes - points[i, :], axis=1) < 1e-2)[0])

    # ele_idx = np.where((con == np.array(node_idx)).all(axis=1))[0]
    ele_idx = np.where(np.all(np.sort(con, axis=1) == np.sort(np.array(node_idx).flatten()), axis=1))[0]
    return ele_idx


class Mesh:
    """"
    Mesh class to initialize default attributes.
    """

    def __init__(self, mesh_name, subject_id, subject_folder):
        self.subject_id = subject_id
        self.subject_folder = subject_folder
        self.name = mesh_name
        self.info = None
        self.approach = None  # 'mri2mesh', 'headreco', 'charm'
        self.mri_idx = None

        # default parameters
        self.mesh_folder = os.path.join(subject_folder, 'mesh', mesh_name)
        self.fn_mesh_msh = os.path.join(self.mesh_folder, f"{subject_id}.msh")
        self.fn_mesh_hdf5 = os.path.join(self.mesh_folder, f"{subject_id}.hdf5")
        self.fn_tensor_vn = f"d2c_{subject_id}{os.sep}dti_results_T1space{os.sep}DTI_conf_tensor.nii.gz"
        self.fn_mri_conform = f"{subject_id}_T1fs_conform.nii.gz"
        self.fn_lh_midlayer = f"fs_{subject_id}{os.sep}surf{os.sep}lh.central"
        self.fn_rh_midlayer = f"fs_{subject_id}{os.sep}surf{os.sep}rh.central"
        self.vertex_density = 1.0  # headreco
        self.numvertices = 100000  # mri2mesh

        # refinement parameters
        self.center = None
        self.radius = None
        self.element_size = None
        self.refine_domains = None
        self.smooth_domains = None

        self.fn_lh_wm = None
        self.fn_rh_wm = None
        self.fn_lh_gm = None
        self.fn_rh_gm = None
        self.fn_lh_gm_curv = None
        self.fn_rh_gm_curv = None

        # charm meshes
        self.smooth_skin = None
        self.refinement_roi = None
        self.refinemement_element_size = None

    def fill_defaults(self, approach):
        """
        Initializes attributes for a headreco mesh.

        Parameters:
        -----------
        approach: str
            'headreco'
            'mri2mesh'
            'charm'
        """
        self.approach = approach
        if approach == 'headreco':
            self.fn_mesh_msh = os.path.join(self.mesh_folder, f"{self.subject_id}.msh")
            self.fn_mesh_hdf5 = os.path.join(self.mesh_folder, f"{self.subject_id}.hdf5")
            self.fn_tensor_vn = f"d2c_{self.subject_id}{os.sep}dti_results_T1space{os.sep}DTI_conf_tensor.nii.gz"
            self.fn_mri_conform = f"{self.subject_id}_T1fs_conform.nii.gz"
            self.fn_lh_midlayer = f"fs_{self.subject_id}{os.sep}surf{os.sep}lh.central"
            self.fn_rh_midlayer = f"fs_{self.subject_id}{os.sep}surf{os.sep}rh.central"

        elif approach == 'mri2mesh':
            self.fn_mesh_msh = os.path.join(self.mesh_folder, f"{self.subject_id}.msh")
            self.fn_mesh_hdf5 = os.path.join(self.mesh_folder, f"{self.subject_id}.hdf5")
            self.fn_tensor_vn = f"d2c_{self.subject_id}{os.sep}dti_results_T1space{os.sep}DTI_conf_tensor.nii.gz"
            self.fn_mri_conform = f"{self.subject_id}_T1fs_conform.nii.gz"
            self.fn_lh_gm_curv = f"fs_{self.subject_id}{os.sep}surf{os.sep}lh.curv.pial"
            self.fn_rh_gm_curv = f"fs_{self.subject_id}{os.sep}surf{os.sep}rh.curv.pial"

        elif approach == 'charm':
            self.fn_mesh_msh = os.path.join(self.mesh_folder, f"{self.subject_id}.msh")
            self.fn_mesh_hdf5 = os.path.join(self.mesh_folder, f"{self.subject_id}.hdf5")
            self.fn_tensor_vn = f"d2c_{self.subject_id}{os.sep}dti_results_T1space{os.sep}DTI_conf_tensor.nii.gz"
            self.fn_mri_conform = f"{self.subject_id}_T1.nii.gz"
            self.fn_lh_midlayer = f"m2m_{self.subject_id}{os.sep}surfaces{os.sep}lh.central.gii"
            self.fn_rh_midlayer = f"m2m_{self.subject_id}{os.sep}surfaces{os.sep}rh.central.gii"

        else:
            raise NotImplementedError(f"Approach {approach} not implemented.")

    def write_to_hdf5(self, fn_hdf5, check_file_exist=False, verbose=False):
        """
        Write this mesh' attributes to .hdf5 file.

        Parameters:
        -----------
        fn_hdf5 : str
        check_file_exist : bool
            Check if provided filenames exist, warn if not.
        verbose : bool
            Print self information
        """

        pynibs.write_dict_to_hdf5(fn_hdf5=fn_hdf5, data=self.__dict__, folder=f"mesh/{self.name}",
                                  check_file_exist=check_file_exist)
        if verbose:
            self.print()

    def print(self):
        """
        Print self information.
        """
        n_left, n_right = int(32 - np.floor((len(self.name) + 10) / 2)), int(32 - np.ceil((len(self.name) + 10) / 2))
        n_left, n_right = np.max(n_left, 0), np.max(n_right, 0)
        print("    " + "=" * n_left + f"  Mesh {self.name}:  " + "=" * n_right)
        print("\t" + json.dumps(self.__dict__, sort_keys=False, indent="\t", ))
        print("    " + "=" * 64 + "\n")


class ROI:
    """"
    Region of interest class to initialize default attributes.

    """

    def __init__(self, subject_id, roi_name, mesh_name):
        self.subject_id = subject_id
        self.name = roi_name
        self.mesh_name = mesh_name
        self.type = None  # 'surface' or 'volume'
        self.info = None
        self.template = None  # None, 'MNI', 'fsaverage', 'subject'
        self.gm_surf_fname = None
        self.wm_surf_fname = None
        self.midlayer_surf_fname = None
        self.delta = 0.5
        self.refine = False
        self.X_ROI = None
        self.Y_ROI = None
        self.Z_ROI = None
        self.center = None
        self.radius = None
        self.layer = 3
        self.fn_mask = None
        self.fn_mask_avg = None
        self.hemisphere = None
        self.midlayer_surf_fname = None
        self.tri_center_coord_mid = None

    def write_to_hdf5(self, fn_hdf5, check_file_exist=False, verbose=False):
        """
        Write this mesh' attributes to .hdf5 file.

        Parameters:
        -----------
        fn_hdf5 : str
        check_file_exist : bool
            Check if provided filenames exist, warn if not.
        verbose : bool
            Print self information
        """

        pynibs.write_dict_to_hdf5(fn_hdf5=fn_hdf5, data=self.__dict__, folder=f"roi/{self.mesh_name}/{self.name}",
                                  check_file_exist=check_file_exist)
        if verbose:
            self.print()

    def print(self):
        """
        Print self information.
        """
        n_left, n_right = int(32 - np.floor((len(self.name) + 10) / 2)), int(32 - np.ceil((len(self.name) + 10) / 2))
        n_left, n_right = np.max(n_left, 0), np.max(n_right, 0)
        print("    " + "=" * n_left + f"  ROI {self.name}:  " + "=" * n_right)
        print("\t" + json.dumps(self.__dict__, sort_keys=False, indent="\t", ))
        print("    " + "=" * 64 + "\n")


def check_islands_for_single_elm(source_elm, connectivity=None, adjacency=None, island_crit=1):
    """
    This identifies islands in a mesh for a given element. An island is a set of elements, that is only connect
    via a single node to another set of elements.
    These islands usually crash the FEM solver and should be removed.

    1. Find all elements connect to source_elm via one node (1-node-neighbor)
    2. Start with source_elm and visit all 2-node-neighbors ('shared-edge)
    3. Continue recursively with all 2-node-neighbors and visit their 2-node-neighbors
    4. See if any 1-node-neighbors have not been visited with this strategy. If so, an island has been found

    Parameters
    ----------
    source_elm : int
        The source element to check
    connectivity : np.ndarray, optional
        Connectivity ('node_number_list') starting with 0. Can be triangles or tetrahedra
        (n_elms, 3) or (n_elms_4).
    adjacency : np.ndparray, optional
        Adjenceny matrix (n_elm, n_elm). Weights are supposed to be number of shared nodes.
        Computed from neighbors if not provided.
    island_crit : int, optional, default: 'any'
        How many nodes to define islands?
        'any' -> Elements connected via a single node or single edge are defined as an island.
        'node' -> Elements connected via a single _node_ are defined as an island.
        'edge' -> Elements connected via a single _edge_ are defined as an island.

    Returns
    -------
    n_visited : int
    n_not_visited : int
    neighbors_visited : dict, which neighbors have been visited and which have not
    """
    if adjacency is not None and connectivity is not None:
        raise ValueError(f"Provide either neighbors or connectivity, not both.")

    if adjacency is None:
        assert connectivity is not None
        adjacency = np.array([np.sum(np.isin(connectivity, elm), axis=1) for elm in connectivity])

    if island_crit == 'any':
        # find elements with only one node in common
        neighbors_visited = {i: False for i in np.where(adjacency[source_elm] == 1)[0]}
        island_crit = 2
    elif island_crit == 'node':
        # find elements with only one node in common
        neighbors_visited = {i: False for i in np.where(adjacency[source_elm] == 1)[0]}
        island_crit = 1
    elif island_crit == 'edge':
        # find elements with only one node in common
        neighbors_visited = {i: False for i in np.where(adjacency[source_elm] == 2)[0]}
        island_crit = 2
    else:
        raise ValueError

    # now visit all elements with 2 or more neighboring elements recursivly.
    # everything that's left over between 1 and 2 neighbors is an island
    neighs_to_check = set(np.where(adjacency[source_elm] > island_crit)[0].tolist())

    # add the starting element to the list
    neighs_to_check.add(source_elm)
    # go through all elements in list
    # print(neighs_to_check)
    while neighs_to_check:
        elm = neighs_to_check.pop()
        neighbors_visited[elm] = True

        # now add all 2-node neighbors for this element
        # for neigh in np.where(adjacency[elm] > 1)[0]:
        sort = (-adjacency[elm]).argsort()
        for idx in np.arange((np.bincount(adjacency[elm])[(island_crit + 1):]).sum()):
            i = sort[idx]
            if i not in neighbors_visited or not neighbors_visited[i]:
                # print(i)
                neighs_to_check.add(i)

    return np.sum([v for v in neighbors_visited.values()]), \
           np.sum([not v for v in neighbors_visited.values()]), \
           neighbors_visited


def find_islands(connectivity=None, adjacency=None, island_crit='any', verbose=False):
    """
    This identifies islands in a mesh. An island is a set of elements, that is only connect
    via a single node to another set of elements.
    These islands usually crash the FEM solver and should be removed.

    For each element:
        1. Find all elements connect to source_elm via one node (1-node-neighbor)
        2. Start with source_elm and visit all 2-node-neighbors ('shared-edge)
        3. Continue recursively with all 2-node-neighbors and visit their 2-node-neighbors
        4. See if any 1-node-neighbors have not been visited with this strategy. If so, an island has been found

    Parameters
    ----------
    connectivity : np.ndarray, optional
        Connectivity ('node_number_list') starting with 0. Can be triangles or tetrahedra
        (n_elms, 3) or (n_elms_4).
    adjacency : np.ndparray, optional
        Adjenceny matrix (n_elm, n_elm). Weights are supposed to be number of shared nodes.
        Computed from neighbors if not provided.
    island_crit : int, optional, default: 'any'
        How many nodes to define islands?
        'any' -> Elements connected via a single node or single edge are defined as an island.
        'node' -> Elements connected via a single _node_ are defined as an island.
        'edge' -> Elements connected via a single _edge_ are defined as an island.
    verbose : bool, optional
        Print some verbosity information. Default: False
    Returns
    -------
        elms_with_island : list
            Elements with neighboring islands
        counter_visited : np.ndarray
            shape = (n_elms). How often as each element been visited.
        counter_not_visited : np.ndarray
            shape = (n_elms). How often as each element not been visited.
    """
    elms_with_island = []
    if adjacency is not None and connectivity is not None:
        raise ValueError(f"Provide either neighbors or connectivity, not both.")
    if adjacency is None and connectivity is None:
        raise ValueError(f"Provide either neighbors or connectivity")
    if adjacency is None:
        assert connectivity is not None
        adjacency = np.array([np.sum(np.isin(connectivity, elm), axis=1) for elm in connectivity])

    counter_not_visited = np.zeros(adjacency.shape[0])
    counter_visited = np.zeros(adjacency.shape[0])

    # go through elements and check for islands
    for elm_source in tqdm(range(adjacency.shape[0]), desc="Checking for islands."):
        _, n_not_visited, visited = check_islands_for_single_elm(elm_source,
                                                                 adjacency=adjacency,
                                                                 island_crit=island_crit)

        # add stats for each element how often it has been visited
        elms_visited = [i for i, v in visited.items() if v]
        elms_not_visited = [i for i, v in visited.items() if not v]
        counter_visited[elms_visited] += 1
        counter_not_visited[elms_not_visited] += 1

        # if an island is found add it to results list
        if n_not_visited:
            if verbose:
                print(f"\nElement {elm_source: >4}: {n_not_visited} 1-node-neighbors not visited. ")
            elms_with_island.append(elm_source)

    return elms_with_island, counter_visited, counter_not_visited


def find_island_elms(connectivity=None, adjacency=None, verbose=False, island_crit='edge', decision='cumulative'):
    """
    Searches for islands in a mesh and returns element indices of the smallest island.
    Island is defines as a set of elements, which share a single node and/or single edge with the rest of the mesh.

    Parameters
    ----------
    connectivity : np.ndarray, optional
        Connectivity ('node_number_list') starting with 0. Can be triangles or tetrahedra
        (n_elms, 3) or (n_elms_4).
    adjacency : np.ndparray, optional
        Adjenceny matrix (n_elm, n_elm). Weights are supposed to be number of shared nodes.
        Computed from neighbors if not provided.
    island_crit : int, optional, default: 'edge'
        How many nodes to define islands?
        'node' -> Elements connected via a single _node_ are defined as an island.
        'edge' -> Elements connected via a single _edge_ are defined as an island.
    decision : string, optional, default: cumulative
        'cumulative' -> Return all element indices that are not visited any times
        'smallest'   -> Return smallest island.
    verbose : bool, optional
        Print some verbosity information. Default: False

    Returns
    -------
        island : list of island-elms
    """
    if adjacency is not None and connectivity is not None:
        raise ValueError(f"Provide either neighbors or connectivity, not both.")
    if adjacency is None:
        assert connectivity is not None
        adjacency = np.array([np.sum(np.isin(connectivity, elm), axis=1) for elm in connectivity])

    all_islands, counter_visited, counter_not_visited = find_islands(connectivity, verbose=verbose,
                                                                     island_crit=island_crit)

    if decision == 'smallest':
        # find the size of the islands
        one_node_neighs = {k: np.where(adjacency[k] == island_crit)[0] for k in all_islands}

        visited, not_visited = {}, {}
        for island, one_node_neigh in one_node_neighs.items():

            # two counters
            n_visited_i, n_not_visited_i = 0, 0

            for island_i in one_node_neigh:
                n_visited, n_not_visited, _ = check_islands_for_single_elm(island_i, adjacency=adjacency,
                                                                           island_crit=island_crit + 1)
                n_visited_i += n_visited
                n_not_visited_i += n_not_visited
            visited[island] = n_visited_i
            not_visited[island] = n_not_visited_i

        # choose the smallest island and get all 2-neighbors
        smallest_island_idx = np.argmin(list(visited.values()))
        smallest_island = list(visited.keys())[smallest_island_idx]

        _, _, elm_idx_from_smalles_island = check_islands_for_single_elm(smallest_island, island_crit=island_crit + 1,
                                                                         adjacency=adjacency)

        if verbose:
            print(f"Island with {len(list(elm_idx_from_smalles_island.keys()))} elements found.")
        return list(elm_idx_from_smalles_island.keys())

    elif decision == 'cumulative':
        return np.argwhere(counter_not_visited > 0)
