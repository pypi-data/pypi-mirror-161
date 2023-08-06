import os
import re
import h5py
import nibabel
import warnings
import datetime
import numpy as np
import pandas as pd
import multiprocessing.pool
from subprocess import call
from _functools import partial

try:
    from simnibs import read_msh
except ImportError:
    Warning("SimNIBS not found ...")
import pynibs


def split_hdf5(hdf5_in_fn, hdf5_geo_out_fn='', hdf5_data_out_fn=None):
    """
    Splits one hdf5 into one with spatial data and one with statistical data.
    If coil data is present in hdf5_in, it is saved in hdf5Data_out.
    If new spatial data is added to file (curve, inflated, whatever), add this to the geogroups variable.

    Parameters
    ----------
    hdf5_in_fn : str
        Filename of .hdf5 input file
    hdf5_geo_out_fn : str
        Filename of .hdf5 .geo output file
    hdf5_data_out_fn : str
        Filename of .hdf5 .data output file (If none, remove data from hdf5_in)

    Returns
    -------
    <File> : .hdf5 file
        hdf5Geo_out_fn (spatial data)
    <File> : .hdf5 file
        hdf5Data_out_fn (data)
    """

    hdf5_in = None
    try:
        hdf5_in = h5py.File(hdf5_in_fn, 'r+')
    except OSError:
        print((hdf5_in_fn + " does not exist. Quitting."))
        quit()

    if hdf5_data_out_fn is not None:
        hdf5_geo_out = None
        hdf5_data_out = None
        try:
            hdf5_geo_out = h5py.File(hdf5_geo_out_fn, 'x')
            hdf5_data_out = h5py.File(hdf5_data_out_fn, 'x')
        except IOError:
            print((hdf5_geo_out_fn + " or " + hdf5_data_out_fn + " already exists. Quitting."))
            quit()

        print(("Writing " + hdf5_geo_out_fn))
        geogroups = ["/mesh/", "/nodes/"]
        for group in geogroups:
            if group in hdf5_in:
                hdf5_in.copy(group, hdf5_geo_out)
            else:
                print((group + "not found in " + hdf5_in_fn))

        print(("Writing " + hdf5_data_out_fn))
        datagroups = ["/data/", "/fields/", "/coil/"]
        for group in datagroups:
            if group in hdf5_in:
                hdf5_in.copy(group, hdf5_data_out)
            else:
                print((group + "not found in " + hdf5_in_fn))

        # sometimes there is /mesh/field. move to /field/
        if "/mesh/fields" in hdf5_geo_out:
            print(("Moving datarrays " +
                   os.path.basename(hdf5_geo_out_fn) + "/mesh/fields/* to " +
                   os.path.basename(hdf5_data_out_fn) + "/data/fields*"))
            if "/data/" not in hdf5_data_out:
                hdf5_data_out.create_group("/data/")
            hdf5_geo_out.copy("/mesh/fields/", hdf5_data_out)
            del (hdf5_geo_out['/mesh/fields/'])
            for field in hdf5_data_out['/fields/']:
                hdf5_data_out.move('/fields/' + field, '/data/' + field)
            del (hdf5_data_out['/fields'])

    else:  # remove spatial data from hdf5_in
        if "/mesh/fields" in hdf5_in:
            if "/data/" not in hdf5_in:
                hdf5_in.create_group("/data/")
            for dataset in hdf5_in["/mesh/fields"]:
                hdf5_in.move("/mesh/fields/" + dataset, "/data/" + dataset)
        for group in hdf5_in['/']:
            if group != "data" and group != "coil":
                del (hdf5_in['/' + group])
        hdf5_in.close()
        print("repacking .hdf5")
        os.rename(hdf5_in_fn, hdf5_in_fn + '_temp')
        # call("ptrepack -o --chunkshape=auto --propindexes " + hdf5_in_fn + '_temp ' + hdf5_in_fn)

        command = ["ptrepack", "-o", "--chunkshape=auto", "--propindexes",
                   hdf5_in_fn + '_temp',
                   hdf5_in_fn]
        call(command)
        os.remove(hdf5_in_fn + '_temp')


def read_data_hdf5(fname):
    """
    Reads phi and dA/dt data from .hdf5 file (phi and dAdt are given in the nodes!).

    Parameters
    ----------
    fname : str
        Filename of .hdf5 data file

    Returns
    -------
    phi : nparray of float [N_nodes]
        Electric potential in the nodes of the mesh
    da_dt : nparray of float [N_nodesx3]
        Magnetic vector potential in the nodes of the mesh
    """

    with h5py.File(fname, 'r') as f:
        phi = np.array(f['data/potential'])  # [N_nodes]
        # [3*N_nodes x 1]
        da_dt = np.array(f['data/dAdt'])
        da_dt = np.reshape(da_dt, (phi.shape[0], 3), order='c')  # [N_nodes x 3]
    return phi, da_dt


def load_mesh_msh(fname):
    """
    Loading mesh from .msh file and return object instance of TetrahedraLinear class.

    Parameters
    ----------
    fname : str
        Name of .msh file (incl. path)

    Returns
    -------
    obj : pynibs.mesh.TetrahedraLinear
    """

    msh_msh = read_msh(fname)

    points = msh_msh.nodes.node_coord
    triangles = msh_msh.elm.node_number_list[msh_msh.elm.elm_type == 2, 0:3]
    tetrahedra = msh_msh.elm.node_number_list[msh_msh.elm.elm_type == 4, 0:4]

    if tetrahedra.shape[0] == 0:
        offset_idx = np.min(triangles)
        tetrahedra_regions, tetrahedra = np.array(()), np.array(())
        triangles = triangles - offset_idx  # set start index to 0
    elif triangles.shape[0] == 0:
        triangles_regions, triangles = np.array(()), np.array(())
        tetrahedra_regions = msh_msh.elm.tag2[msh_msh.elm.elm_type == 4]
    else:
        offset_idx = np.min(np.array([np.min(triangles), np.min(tetrahedra)]))
        tetrahedra = tetrahedra - offset_idx  # set start index to 0
        tetrahedra_regions = msh_msh.elm.tag2[msh_msh.elm.elm_type == 4]
        triangles = triangles - offset_idx  # set start index to 0

    triangles_regions = msh_msh.elm.tag2[msh_msh.elm.elm_type == 2]

    obj = pynibs.mesh.TetrahedraLinear(points, triangles, triangles_regions, tetrahedra, tetrahedra_regions)

    return obj


def load_mesh_hdf5(fname):
    """
    Loading mesh from .hdf5 file and setting up TetrahedraLinear class.

    Parameters
    ----------
    fname : str
        Name of .hdf5 file (incl. path)

    Returns
    -------
    obj : pynibs.mesh.TetrahedraLinear
        Instance of TetrahedraLinear class

    Example
    -------
    hdf5 file format and contained groups. The content of .hdf5 files can be shown using the tool HDFView
    (https://support.hdfgroup.org/products/java/hdfview/)
    ::
        mesh
        I---/elm
        I    I--/elm_number          [1,2,3,...,N_ele]           Running index over all elements starting at 1,
                                                                    triangles and tetrahedra
        I    I--/elm_type            [2,2,2,...,4,4]             Element type: 2 triangles, 4 tetrahedra
        I    I--/node_number_list    [1,5,6,0;... ;1,4,8,9]      Connectivity of triangles [X, X, X, 0] and tetrahedra
                                                                            [X, X, X, X]
        I    I--/tag1                [1001,1001, ..., 4,4,4]     Surface (100X) and domain (X) indices with 1000 offset
                                                                             for surfaces
        I    I--/tag2                [   1,   1, ..., 4,4,4]     Surface (X) and domain (X) indices w/o offset
        I
        I---/nodes
        I    I--/node_coord          [1.254, 1.762, 1.875;...]   Node coordinates in (mm)
        I    I--/node_number         [1,2,3,...,N_nodes]         Running index over all points starting at 1
        I    I--/units               ["mm"]                      .value is unit of geometry
        I
        I---/fields
        I    I--/E/value             [E_x_1, E_y_1, E_z_1;...]   Electric field in all elms, triangles and tetrahedra
        I    I--/J/value             [J_x_1, J_y_1, J_z_1;...]   Current density in all elms, triangles and tetrahedra
        I    I--/normE/value         [normE_1,..., normE_N_ele]  Magnitude of electric field in all elements,
                                                                            triangles and tetrahedra
        I    I--/normJ/value         [normJ_1,..., normJ_N_ele]  Magnitude of current density in all elements,
                                                                            triangles and tetrahedra

        /data
        I---/potential               [phi_1, ..., phi_N_nodes]   Scalar electric potential in nodes (size N_nodes)
        I---/dAdt                    [A_x_1, A_y_1, A_z_1,...]   Magnetic vector potential (size 3xN_nodes)

    """
    with h5py.File(fname, 'r') as f:
        points = np.array(f['mesh/nodes/node_coord'])
        node_number_list = np.array(f['mesh/elm/node_number_list'])
        elm_type = np.array(f['mesh/elm/elm_type'])
        regions = np.array(f['mesh/elm/tag1'])
        triangles = np.array(f['mesh/elm/triangle_number_list'])  # node_number_list[elm_type == 2, 0:3]
        tetrahedra = np.array(f['mesh/elm/tetrahedra_number_list'])  # node_number_list[elm_type == 4, ]
        triangles_regions = np.array(f['mesh/elm/tri_tissue_type'])
        tetrahedra_regions = np.array(f['mesh/elm/tet_tissue_type'])

    obj = pynibs.mesh.TetrahedraLinear(points, triangles, triangles_regions, tetrahedra, tetrahedra_regions)
    return obj


def write_geo_hdf5(out_fn, msh, roi_dict=None, hdf5_path='/mesh'):
    """
    Creates a .hdf5 file with geometry data from mesh including region of interest(s).

    Parameters
    ----------
    out_fn : str
        Filename of output .hdf5 file containing the geometry information
    msh: TetrahedraLinear object instance
        pynibs.mesh.TetrahedraLinear object
    roi_dict : dict of RegionOfInterestSurface and/or RegionOfInterestVolume object instance(s)
        Region of interest (surface and/or volume) class instance
    hdf5_path : str
        Folder in .hdf5 geometry file, where the mesh information are saved in (Default: /mesh)

    Returns
    -------
    <File> : .hdf5 file
        File containing the geometry information

    Example
    -------
    File structure of .hdf5 geometry file
    ::
        mesh
        I---/elm
        I    I--/elm_number             [1,2,3,...,N_ele]        Running index over all elements starting at 1
                                                                    (triangles and tetrahedra)
        I    I--/elm_type               [2,2,2,...,4,4]          Element type: 2 triangles, 4 tetrahedra
        I    I--/tag1                [1001,1001, ..., 4,4,4]     Surface (100X) and domain (X) indices with 1000
                                                                            offset for surfaces
        I    I--/tag2                [   1,   1, ..., 4,4,4]     Surface (X) and domain (X) indices w/o offset
        I    I--/triangle_number_list   [1,5,6;... ;1,4,8]       Connectivity of triangles [X, X, X]
        I    I--/tri_tissue_type        [1,1, ..., 3,3,3]        Surface indices to differentiate between surfaces
        I    I--/tetrahedra_number_list [1,5,6,7;... ;1,4,8,12]  Connectivity of tetrahedra [X, X, X, X]
        I    I--/tet_tissue_type        [1,1, ..., 3,3,3]        Volume indices to differentiate between volumes
        I    I--/node_number_list       [1,5,6,0;... ;1,4,8,9]   Connectivity of triangles [X, X, X, 0] and
                                                                    tetrahedra [X, X, X, X]
        I
        I---/nodes
        I    I--/node_coord          [1.254, 1.762, 1.875;...]   Node coordinates in (mm)
        I    I--/node_number         [1,2,3,...,N_nodes]         Running index over all points starting at 1
        I    I--/units               ['mm']                      .value is unit of geometry

        roi_surface
        I---/0                                                           Region of Interest number
        I    I--/node_coord_up              [1.254, 1.762, 1.875;...]    Coordinates of upper surface points
        I    I--/node_coord_mid             [1.254, 1.762, 1.875;...]    Coordinates of middle surface points
        I    I--/node_coord_low             [1.254, 1.762, 1.875;...]    Coordinates of lower surface points
        I    I--/tri_center_coord_up        [1.254, 1.762, 1.875;...]    Coordinates of upper triangle centers
        I    I--/tri_center_coord_mid       [1.254, 1.762, 1.875;...]    Coordinates of middle triangle centers
        I    I--/tri_center_coord_low       [1.254, 1.762, 1.875;...]    Coordinates of lower triangle centers
        I    I--/node_number_list           [1,5,6,0;... ;1,4,8,9]       Connectivity of triangles [X, X, X]
        I    I--/delta                      0.5                          Distance parameter between GM and WM surface
        I    I--/tet_idx_tri_center_up      [183, 913, 56, ...]          Tetrahedra indices where triangle center of
                                                                            upper surface are lying in
        I    I--/tet_idx_tri_center_mid     [185, 911, 58, ...]          Tetrahedra indices where triangle center of
                                                                            middle surface are lying in
        I    I--/tet_idx_tri_center_low     [191, 912, 59, ...]          Tetrahedra indices where triangle center of
                                                                            lower surface are lying in
        I    I--/tet_idx_node_coord_mid     [12, 15, 43, ...]            Tetrahedra indices where the node_coords_mid
                                                                            are lying in
        I    I--/gm_surf_fname              .../surf/lh.pial             Filename of GM surface from segmentation
        I    I--/wm_surf_fname              .../surf/lh.white            Filename of WM surface from segmentation
        I    I--/layer                      3                            Number of layers
        I    I--/fn_mask                    .../simnibs/mask.mgh         Filename of region of interest mask
        I    I--/X_ROI                      [-10, 15]                    X limits of region of interest box
        I    I--/Y_ROI                      [-10, 15]                    Y limits of region of interest box
        I    I--/Z_ROI                      [-10, 15]                    Z limits of region of interest box
        I
        I---/1
        I    I ...

        roi_volume
        I---/0                                                           Region of Interest number
        I    I--/node_coord                 [1.254, 1.762, 1.875;...]    Coordinates (x,y,z) of ROI nodes
        I    I--/tet_node_number_list       [1,5,6,7;... ;1,4,8,9]       Connectivity matrix of ROI tetrahedra
        I    I--/tri_node_number_list       [1,5,6;... ;1,4,8]           Connectivity matrix of ROI triangles
        I    I--/tet_idx_node_coord         [183, 913, 56, ...]          Tetrahedra indices where ROI nodes are
        I    I--/tet_idx_tetrahedra_center  [12, 15, 43, ...]            Tetrahedra indices where center points of
                                                                            ROI tetrahedra are
        I    I--/tet_idx_triangle_center    [12, 15, 43, ...]            Tetrahedra indices where center points of
                                                                            ROI triangles are

        I---/1
        I    I ...
    """
    if os.path.exists(out_fn):
        os.remove(out_fn)

    with h5py.File(out_fn, 'w') as f:
        f.create_dataset(hdf5_path + '/elm/elm_number', data=np.arange(msh.N_tet + msh.N_tri) + 1)
        f.create_dataset(hdf5_path + '/elm/elm_type', data=np.array([2] * msh.N_tri + [4] * msh.N_tet))
        f.create_dataset(hdf5_path + '/elm/tag1',
                         data=np.hstack((msh.triangles_regions + 1000, msh.tetrahedra_regions)).flatten())
        f.create_dataset(hdf5_path + '/elm/tag2',
                         data=np.hstack((msh.triangles_regions, msh.tetrahedra_regions)).flatten())
        f.create_dataset(hdf5_path + '/elm/triangle_number_list', data=msh.triangles)
        f.create_dataset(hdf5_path + '/elm/tri_tissue_type', data=msh.triangles_regions.flatten())
        f.create_dataset(hdf5_path + '/elm/tetrahedra_number_list', data=msh.tetrahedra)
        f.create_dataset(hdf5_path + '/elm/tet_tissue_type', data=msh.tetrahedra_regions.flatten())
        if msh.tetrahedra.size != 0:
            if msh.triangles.size != 0:
                f.create_dataset(hdf5_path + '/elm/node_number_list', data=np.vstack(
                        (np.hstack((msh.triangles, np.zeros((msh.N_tri, 1)))),
                         msh.tetrahedra)).astype(int))
            else:
                f.create_dataset(hdf5_path + '/elm/node_number_list', data=msh.tetrahedra).astype(int)
        else:
            f.create_dataset(hdf5_path + '/elm/node_number_list', data=np.vstack(
                    (np.hstack((msh.triangles, np.zeros((msh.N_tri, 1)))),
                     )).astype(int))
        f.create_dataset(hdf5_path + '/nodes/node_coord', data=msh.points)
        f.create_dataset(hdf5_path + '/nodes/node_number', data=np.arange(msh.N_points) + 1)
        # f.create_dataset(hdf5_path + '/nodes/units', data=['mm'])
        f.create_dataset(hdf5_path + '/elm/tet_elm_type', data=np.array([4] * msh.N_tet))
        f.create_dataset(hdf5_path + '/elm/tri_elm_type', data=np.array([2] * msh.N_tri))

        if roi_dict is not None:

            for roi_key in roi_dict.keys():
                # save roi surface information
                if roi_dict[roi_key].__class__.__name__ == 'RegionOfInterestSurface':

                    f.create_dataset(f'roi_surface/{roi_key}/node_coord_up',
                                     data=np.array(roi_dict[roi_key].node_coord_up))
                    f.create_dataset(f'roi_surface/{roi_key}/node_coord_mid',
                                     data=np.array(roi_dict[roi_key].node_coord_mid))
                    f.create_dataset(f'roi_surface/{roi_key}/node_coord_low',
                                     data=np.array(roi_dict[roi_key].node_coord_low))
                    f.create_dataset(f'roi_surface/{roi_key}/tri_center_coord_up',
                                     data=np.array(roi_dict[roi_key].tri_center_coord_up))
                    f.create_dataset(f'roi_surface/{roi_key}/tri_center_coord_mid',
                                     data=np.array(roi_dict[roi_key].tri_center_coord_mid))
                    f.create_dataset(f'roi_surface/{roi_key}/tri_center_coord_low',
                                     data=np.array(roi_dict[roi_key].tri_center_coord_low))
                    f.create_dataset(f'roi_surface/{roi_key}/node_number_list',
                                     data=np.array(roi_dict[roi_key].node_number_list))
                    f.create_dataset(f'roi_surface/{roi_key}/delta',
                                     data=np.array(roi_dict[roi_key].delta))

                    if roi_dict[roi_key].tet_idx_tri_center_up is not None:
                        f.create_dataset(f'roi_surface/{roi_key}/tet_idx_tri_center_up',
                                         data=np.array(roi_dict[roi_key].tet_idx_tri_center_up).astype(int))

                    f.create_dataset(f'roi_surface/{roi_key}/tet_idx_tri_center_mid',
                                     data=np.array(roi_dict[roi_key].tet_idx_tri_center_mid).astype(int))

                    if roi_dict[roi_key].tet_idx_tri_center_low is not None:
                        f.create_dataset(f'roi_surface/{roi_key}/tet_idx_tri_center_low',
                                         data=np.array(roi_dict[roi_key].tet_idx_tri_center_low).astype(int))

                    f.create_dataset(f'roi_surface/{roi_key}/tet_idx_node_coord_mid',
                                     data=np.array(roi_dict[roi_key].tet_idx_node_coord_mid).astype(int))
                    f.create_dataset(f'roi_surface/{roi_key}/gm_surf_fname',
                                     data=np.array(roi_dict[roi_key].gm_surf_fname).astype("S"))
                    f.create_dataset(f'roi_surface/{roi_key}/wm_surf_fname',
                                     data=np.array(roi_dict[roi_key].wm_surf_fname).astype("S"))
                    f.create_dataset(f'roi_surface/{roi_key}/midlayer_surf_fname',
                                     data=np.array(roi_dict[roi_key].midlayer_surf_fname).astype("S"))
                    f.create_dataset(f'roi_surface/{roi_key}/layer',
                                     data=roi_dict[roi_key].layer)
                    f.create_dataset(f'roi_surface/{roi_key}/refine',
                                     data=roi_dict[roi_key].refine)

                    if roi_dict[roi_key].fn_mask is not None:
                        f.create_dataset(f'roi_surface/{roi_key}/fn_mask',
                                         data=np.array(roi_dict[roi_key].fn_mask).astype("S"))

                    if roi_dict[roi_key].x_roi is not None:
                        f.create_dataset(f'roi_surface/{roi_key}/X_ROI',
                                         data=np.array(roi_dict[roi_key].x_roi))

                    if roi_dict[roi_key].y_roi is not None:
                        f.create_dataset(f'roi_surface/{roi_key}/Y_ROI',
                                         data=np.array(roi_dict[roi_key].y_roi))

                    if roi_dict[roi_key].z_roi is not None:
                        f.create_dataset(f'roi_surface/{roi_key}/Z_ROI',
                                         data=np.array(roi_dict[roi_key].z_roi))

                # save roi volume information
                if roi_dict[roi_key].__class__.__name__ == 'RegionOfInterestVolume':

                    f.create_dataset(f'roi_volume/{roi_key}/node_coord',
                                     data=np.array(roi_dict[roi_key].node_coord))
                    f.create_dataset(f'roi_volume/{roi_key}/tet_node_number_list',
                                     data=np.array(roi_dict[roi_key].tet_node_number_list))
                    f.create_dataset(f'roi_volume/{roi_key}/tri_node_number_list',
                                     data=np.array(roi_dict[roi_key].tri_node_number_list))

                    if roi_dict[roi_key].tet_idx_node_coord is not None:
                        f.create_dataset(f'roi_volume/{roi_key}/tet_idx_node_coord',
                                         data=np.array(roi_dict[roi_key].tet_idx_node_coord))

                    f.create_dataset(f'roi_volume/{roi_key}/tet_idx_tetrahedra_center',
                                     data=np.array(roi_dict[roi_key].tet_idx_tetrahedra_center))
                    f.create_dataset(f'roi_volume/{roi_key}/tet_idx_triangle_center',
                                     data=np.array(roi_dict[roi_key].tet_idx_triangle_center))


def write_geo_hdf5_surf(out_fn, points, con, replace=False, hdf5_path='/mesh'):
    """
    Creates a .hdf5 file with geometry data from midlayer.

    Parameters
    ----------
    out_fn : str
        Filename of output .hdf5 file containing the geometry information
    points : nparray [N_points x 3]
        Coordinates of nodes (x,y,z)
    con : nparray [N_tri x 3]
        Connectivity list of triangles
    replace : boolean
        Replace .hdf5 geometry file (True / False)
    hdf5_path : str
        Folder in .hdf5 geometry file, where the geometry information is saved in (Default: /mesh)

    Returns
    -------
    <File> : .hdf5 file
        File containing the geometry information.

    Example
    -------
    File structure of .hdf5 geometry file:
    ::
        mesh
        |---/elm
        |    |--/triangle_number_list   [1,5,6;... ;1,4,8]      Connectivity of triangles [X, X, X]
        |    |--/tri_tissue_type        [1,1, ..., 3,3,3]       Surface indices to differentiate between surfaces
        |
        |---/nodes
        |    |--/node_coord             [1.2, 1.7, 1.8; ...]    Node coordinates in (mm)
    """

    if os.path.exists(out_fn):
        os.remove(out_fn)

    with h5py.File(out_fn, 'w') as h5:
        h5.create_dataset(hdf5_path + '/nodes/' + 'node_coord',
                          data=points)
        h5.create_dataset(hdf5_path + '/elm/triangle_number_list',
                          data=con)
        h5.create_dataset(hdf5_path + '/elm/tri_tissue_type',
                          data=np.zeros((points.shape[0], 1)).astype(int))


def write_data_hdf5(out_fn, data, data_names, hdf5_path='/data', mode="a"):
    """
    Creates a .hdf5 file with data.

    Parameters
    ----------
    out_fn : str
        Filename of output .hdf5 file containing the geometry information
    data : nparray or list of nparrays of float
        Data to save in hdf5 data file
    data_names : str or list of str
        Labels of data
    hdf5_path : str
        Folder in .hdf5 geometry file, where the data is saved in (Default: /data)
    mode : str, optional, default: "a"
        Mode: "a" append, "w" write (overwrite)

    Returns
    -------
    <File> : .hdf5 file
        File containing the stored data

    Example
    -------
    File structure of .hdf5 data file
    ::
        data
        |---/data_names[0]          [data[0]]           First dataset
        |---/    ...                   ...                  ...
        |---/data_names[N-1]        [data[N-1]]         Last dataset
    """

    if type(data) is not list:
        data = [data]

    if type(data_names) is not list:
        data_names = [data_names]

    assert len(data_names) == len(data), f"Different number of data_names {len(data_names)} and data ({len(data)}."
    with h5py.File(out_fn, mode) as f:
        for i, data_name in enumerate(data_names):
            if isinstance(data[i], np.ndarray):
                f.create_dataset(hdf5_path + '/' + data_name, data=data[i], dtype="float64")
            else:
                f.create_dataset(hdf5_path + '/' + data_name, data=data[i])


def write_data_hdf5_surf(data, data_names, data_hdf_fn_out, geo_hdf_fn, replace=False, replace_array_in_file=True):
    """
    Saves surface data to .hdf5 data file and generates corresponding .xdmf file linking both.
    The directory of data_hdf_fn_out and geo_hdf_fn should be the same, as only basenames of files are stored
    in the .xdmf file.

    Parameters
    ----------
    data : ndarray or list [N_points_ROI x N_components]
        Data to map on surfaces
    data_names : str or list
        Names for datasets
    data_hdf_fn_out : str
        Filename of .hdf5 data file
    geo_hdf_fn : str
        Filename of .hdf5 geo file containing the geometry information (has to exist)
    replace : boolean, optional, default: False
        Replace existing .hdf5 and .xdmf file completely
    replace_array_in_file : boolean, optional, default: True
        Replace existing array in file

    Returns
    -------
    <File> : .hdf5 file
        data_hdf_fn_out.hdf5 containing data
    <File> : .xdmf file
        data_hdf_fn_out.xdmf containing information about .hdf5 file structure for Paraview

    Example
    -------
    File structure of .hdf5 data file
    ::
        /data
        |---/tris
        |      |---dataset_0    [dataset_0]    (size: N_dataset_0 x M_dataset_0)
        |      |---   ...
        |      |---dataset_K   [dataset_K]     (size: N_dataset_K x M_dataset_K)
    """

    # Check if files already exists
    try:
        if data_hdf_fn_out[-4:] != 'hdf5':
            data_hdf_fn_out += '.hdf5'
    except IndexError:
        data_hdf_fn_out += '.hdf5'

    data_xdmf_fn = data_hdf_fn_out[:-4] + 'xdmf'
    if os.path.exists(data_hdf_fn_out):
        if replace:
            os.remove(data_hdf_fn_out)
        elif not replace and replace_array_in_file:
            pass
        else:
            warnings.warn(data_hdf_fn_out + " already exists. Quitting")
            return
    if os.path.exists(data_xdmf_fn):
        if replace:
            os.remove(data_xdmf_fn)
        elif not replace and replace_array_in_file:
            pass
        else:
            warnings.warn(data_xdmf_fn + " already exists. Quitting")
            return

    # Check for correct data and data_names
    if type(data) == np.ndarray:
        data = [data]
    elif type(data) == list:
        for dat in data:
            if type(dat) is not np.ndarray:
                raise NotImplementedError
    else:
        raise NotImplementedError

    if type(data_names) is str:
        data_names = [data_names]
    elif type(data_names) is not list:
        raise NotImplementedError

    if len(data) != len(data_names):
        raise ValueError(f'Dimension mismatch, data (len: {len(data)}) <-> data_names (len: {len(data_names)})')

    with h5py.File(data_hdf_fn_out, 'a') as h5_data, \
            h5py.File(geo_hdf_fn, 'r') as h5_geo:

        # if geo file exists in same folder than data file only use relative path
        if os.path.split(data_hdf_fn_out) == os.path.split(geo_hdf_fn):
            geo_hdf_fn = os.path.basename(geo_hdf_fn)

        # write data
        only_data_replaced = True  # keep .xdmf if some data is only replaced in .hdf5 file and no new data is added

        for idx, dat in enumerate(data):
            if replace_array_in_file:
                try:
                    del h5_data['/data/tris/' + data_names[idx]]
                except KeyError:
                    only_data_replaced = False

            else:
                only_data_replaced = False

            h5_data.create_dataset('/data/tris/' + data_names[idx], data=data[idx])

        if not only_data_replaced:
            with open(data_xdmf_fn, 'w') as xdmf:
                # write xdmf file linking the data to the surfaces in geo_hdf_fn
                xdmf.write('<?xml version="1.0"?>\n')
                xdmf.write('<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>\n')
                xdmf.write('<Xdmf Version="2.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n')
                xdmf.write('<Domain>\n')

                # one collection grid
                xdmf.write('<Grid\nCollectionType="Spatial"\nGridType="Collection"\nName="Collection">\n')

                # read all available surfaces
                surface = []
                lookup_str = 'triangle_number_list_'
                lookup_str_node = 'node_coord_'
                lookup_str_tri = 'tri_tissue_type_'

                keys = list(h5_geo['mesh/elm/'].keys())
                for key in keys:
                    idx = key.find(lookup_str)
                    if idx >= 0:
                        surface.append(key[(idx + len(lookup_str)):])

                if not surface:
                    surface = []
                    lookup_str = 'triangle_number_list'
                    lookup_str_node = 'node_coord'
                    lookup_str_tri = 'tri_tissue_type'
                    keys = list(h5_geo['mesh/elm/'].keys())
                    for key in keys:
                        idx = key.find(lookup_str)
                        if idx >= 0:
                            surface.append(key[(idx + len(lookup_str)):])

                data_written = False

                for surf in surface:

                    n_tris = len(h5_geo['/mesh/elm/' + lookup_str + surf][:])
                    n_nodes = len(h5_geo['/mesh/nodes/' + lookup_str_node + surf][:])
                    assert n_tris, n_nodes

                    # one grid for triangles...
                    ###########################
                    xdmf.write('<Grid Name="tris" GridType="Uniform">\n')
                    xdmf.write('<Topology NumberOfElements="' + str(n_tris) +
                               '" TopologyType="Triangle" Name="' + surf + '_Tri">\n')
                    xdmf.write('<DataItem Format="HDF" Dimensions="' + str(n_tris) + ' 3">\n')
                    xdmf.write(geo_hdf_fn + ':' + '/mesh/elm/' + lookup_str + surf + '\n')
                    xdmf.write('</DataItem>\n')
                    xdmf.write('</Topology>\n')

                    # nodes
                    xdmf.write('<Geometry GeometryType="XYZ">\n')
                    xdmf.write('<DataItem Format="HDF" Dimensions="' + str(n_nodes) + ' 3">\n')
                    xdmf.write(geo_hdf_fn + ':' + '/mesh/nodes/' + lookup_str_node + surf + '\n')
                    xdmf.write('</DataItem>\n')
                    xdmf.write('</Geometry>\n')

                    # data
                    for idx, dat in enumerate(data):
                        data_dim = dat.shape[1] if dat.ndim > 1 else 1

                        xdmf.write('<Attribute Name="' + data_names[idx] + '" AttributeType="Scalar" Center="Cell">\n')
                        xdmf.write('<DataItem Format="HDF" Dimensions="' + str(n_tris) + ' ' + str(data_dim) + '">\n')
                        xdmf.write(os.path.basename(data_hdf_fn_out) + ':' + '/data/tris/' + data_names[idx] + '\n')
                        xdmf.write('</DataItem>\n')
                        xdmf.write('</Attribute>\n')

                    # tissue_type
                    xdmf.write('<Attribute Name="tissue_type" AttributeType="Scalar" Center="Node">\n')
                    xdmf.write('<DataItem Format="HDF" Dimensions="' + str(n_nodes) + ' 1">\n')
                    xdmf.write(geo_hdf_fn + ':' + '/mesh/elm/' + lookup_str_tri + surf + '\n')
                    xdmf.write('</DataItem>\n')
                    xdmf.write('</Attribute>\n')
                    xdmf.write('</Grid>\n')

                xdmf.write('</Grid>\n')
                xdmf.write('</Domain>\n')
                xdmf.write('</Xdmf>\n')


def write_xdmf(hdf5_fn, hdf5_geo_fn=None, overwrite_xdmf=False, overwrite_array=False, verbose=False, mode="r+"):
    """
    Creates .xdmf markup file for given hdf5 file, mainly for paraview visualization. Checks if triangles and
    tetrahedra already exists as distinct arrays in hdf5_fn . If not, these are added to the .hdf5 file and rebased to
    0 (from 1). If only hdf5_fn is provided, spatial information has to be present as arrays for tris and tets in this
    dataset.

    Parameters
    ----------
    hdf5_fn : str
        Filename of hdf5 file containing the data
    hdf5_geo_fn : str
        Filename of hdf5 file containing the geometry. Optional.
    overwrite_xdmf : bool
        Overwrite existing xdmf file if present. Default: False.
    overwrite_array : bool
        Overwrite existing arrays if present. Default: False.
    verbose : boolean
        Print output or not
    mode : str, optional, default: "r+"
        Mode to open hdf5_geo file. If hdf5_geo is already separated in tets and tris etc., nothing has to be written,
        use "r" to avoid IOErrors in case of parallel computing.

    Returns
    -------
    fn_xml : str
        Filename of the created .xml file
    <File> : .xdmf file
        hdf5_fn[-4].xdmf (only data if hdf5Geo_fn provided)
    <File> : .hdf5 file
        hdf5_fn changed if neccessary
    <File> : .hdf5 file
        hdf5geo_fn containing spatial data
    """

    if os.path.splitext(hdf5_fn)[1] not in ['.hdf5', '.h5', '.hdf']:
        print("Provide .hdf5 filename for existing file.")
        return

    xdmf_fn = os.path.splitext(hdf5_fn)[0] + '.xdmf'
    try:
        hdf5 = h5py.File(hdf5_fn, mode)
        hdf5_geo = h5py.File(hdf5_fn, mode)
    except IOError:
        print(f"Error opening file: {hdf5_fn} ... Quitting")
        return

    hdf5_fn = os.path.basename(hdf5_fn)

    if verbose:
        print("Creating " + xdmf_fn)

    if hdf5_geo_fn is not None:

        try:
            hdf5_geo = h5py.File(hdf5_geo_fn, mode)
        except IOError:
            print(f"Error opening file: {hdf5_geo_fn} ... Quitting")
            return
    else:
        hdf5_geo_fn = os.path.basename(hdf5_fn)

    if os.path.isfile(xdmf_fn) and not overwrite_xdmf:
        raise FileExistsError(f'{xdmf_fn} already exists. Remove or set overwriteXDMF. Quitting.')

    # check if triangle and tetra data is already in 2 dataframes in hdf5
    # /mesh/elm or /elm/?
    if "/elm/" in hdf5_geo:
        path = '/elm'
    else:
        path = '/mesh/elm'

    if "/nodes/" in hdf5_geo:
        node_path = '/nodes'
    else:
        node_path = '/mesh/nodes'

    if path + "/triangle_number_list" not in hdf5_geo:

        # if not, create
        if verbose:
            print(("triangle_number_list and tetrahedra_number_list do not exist. Adding to " + hdf5_geo_fn + "."))

        # get tris and tets from node_number list ... take the triangle ones
        triangles = (hdf5_geo[path + '/node_number_list'][:][hdf5_geo[path + '/elm_type'][:] == 2][:, 0:3])
        tetrahedra = (hdf5_geo[path + '/node_number_list'][:][hdf5_geo[path + '/elm_type'][:] == 4])

        # add to hdf5_fn and rebase to 0
        hdf5_geo.create_dataset(path + '/triangle_number_list', data=triangles - 1)
        hdf5_geo.create_dataset(path + '/tetrahedra_number_list', data=tetrahedra - 1)

    else:
        triangles = hdf5_geo[path + '/triangle_number_list']
        try:
            tetrahedra = hdf5_geo[path + '/tetrahedra_number_list']
        except KeyError:
            tetrahedra = None

    # check if data is divided into tets and tris

    # get information for .xdmf
    n_nodes = len(hdf5_geo[node_path + '/node_coord'])
    n_tris = len(triangles)
    try:
        n_tets = len(tetrahedra)
    except TypeError:
        n_tets = -1

    if not path + "/tri_tissue_type" in hdf5_geo:
        if verbose:
            print("elm data is not divided into tris and tets. Doing that now")
        if 'tag1' in hdf5_geo[path + '/']:
            hdf5_geo.create_dataset(path + '/tri_tissue_type',
                                    data=hdf5_geo[path + '/tag1'][:][hdf5_geo[path + '/elm_type'][:] == 2])
            hdf5_geo.create_dataset(path + '/tet_tissue_type',
                                    data=hdf5_geo[path + '/tag1'][:][hdf5_geo[path + '/elm_type'][:] == 4])

        hdf5_geo.create_dataset(path + '/tri_elm_type',
                                data=hdf5_geo[path + '/elm_type'][:][hdf5_geo[path + '/elm_type'][:] == 2])
        hdf5_geo.create_dataset(path + '/tet_elm_type',
                                data=hdf5_geo[path + '/elm_type'][:][hdf5_geo[path + '/elm_type'][:] == 4])

    if "data" in hdf5:
        for data in hdf5['/data/']:
            value = ""  # remove .value structure and save data directly in /data/dataname array
            try:
                if 'value' in list(hdf5['/data/' + data].keys()):
                    value = '/value'
            except (KeyError, AttributeError):
                pass
            if verbose:
                print(('Processing ' + data))
            if len(hdf5['/data/' + data + value]) == n_tris:
                if not "data/tris/" + data in hdf5:
                    if verbose:
                        print(('Writing /data/tris/' + data))
                    hdf5.create_dataset('/data/tris/' + data, data=hdf5['/data/' + data + value + value][:])

            elif len(hdf5['/data/' + data + value]) == n_tets:
                if not "data/tets/" + data in hdf5:
                    if verbose:
                        print(('Writing /data/tets/' + data))
                    hdf5.create_dataset('/data/tets/' + data, data=hdf5['/data/' + data + value + value][:])

            elif len(hdf5['/data/' + data + value]) == n_tris + n_tets and n_tets > 0:
                if not "data/tris" + data in hdf5:
                    if verbose:
                        print(('Writing /data/tris/' + data))
                    hdf5.create_dataset('/data/tris/' + data,
                                        data=hdf5['/data/' + data + value][:][hdf5_geo[path + '/elm_type'][:] == 2])

                if not "data/tets/" + data in hdf5:
                    if verbose:
                        print(('Writing /data/tets/' + data))
                    hdf5.create_dataset('/data/tets/' + data,
                                        data=hdf5['/data/' + data + value][:][hdf5_geo[path + '/elm_type'][:] == 4])

            elif len(hdf5['/data/' + data + value]) == n_nodes:
                if not "data/nodes" + data in hdf5:
                    if verbose:
                        print(("Writing /data/nodes/" + data))
                    if overwrite_array:
                        try:
                            del hdf5[f'/data/nodes/{data}']
                        except KeyError:
                            pass
                    try:
                        hdf5.create_dataset('/data/nodes/' + data, data=hdf5['/data/' + data + value][:])
                    except RuntimeError:
                        print(('/data/nodes/' + data + " already exists"))
            elif verbose:
                print((data + " not fitting to triangle or tetrahedra or total number. Ignoring."))

    if '/mesh/fields' in hdf5:
        for field in hdf5['/mesh/fields']:
            if verbose:
                print(('Processing ' + field))
            if '/data/tris/' + field not in hdf5:
                hdf5.create_dataset('/data/tris/' + field,
                                    data=hdf5['/mesh/fields/' + field + '/value'][:][
                                        hdf5_geo[path + '/elm_type'][:] == 2])
            if '/data/tets/' + field not in hdf5:
                hdf5.create_dataset('/data/tets/' + field,
                                    data=hdf5['/mesh/fields/' + field + '/value'][:][
                                        hdf5_geo[path + '/elm_type'][:] == 4])

    if '/elmdata/' in hdf5:
        for field in hdf5['/elmdata']:
            if verbose:
                print(('Processing ' + field))
            if '/data/tris/' + field not in hdf5:
                # sometimes data is stored in a 'value' subfolder
                try:
                    subfolder = '/value'
                    _ = hdf5['/elmdata/' + field + subfolder][0]
                # ... sometimes not
                except KeyError:
                    subfolder = ''
                hdf5.create_dataset('/data/tris/' + field,
                                    data=hdf5[f'/elmdata/{field}{subfolder}'][:][
                                        hdf5_geo[f'{path}/elm_type'][:] == 2])
            if '/data/tets/' + field not in hdf5:
                try:
                    subfolder = '/value'
                    _ = hdf5[f'/elmdata/{field}{subfolder}'][0]
                except KeyError:
                    subfolder = ''
                hdf5.create_dataset(f'/data/tets/{field}',
                                    data=hdf5[f'/elmdata/{field}{subfolder}'][:][
                                        hdf5_geo[f'{path}/elm_type'][:] == 4])

    # create .xdmf file
    f = open(xdmf_fn, 'w')
    space = '\t'

    # header
    f.write('<?xml version="1.0"?>\n')
    f.write('<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>\n')
    f.write('<Xdmf Version="2.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n')
    f.write('<Domain>\n')

    # one collection grid
    f.write('<Grid CollectionType="Spatial" GridType="Collection" Name="Collection">\n')

    # one grid for triangles...
    ###########################
    f.write(f'{space}<Grid Name="tris" GridType="Uniform">\n')
    space += '\t'
    f.write(f'{space}<Topology NumberOfElements="{n_tris}" TopologyType="Triangle" Name="Tri">\n')
    space += '\t'
    f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_tris} 3">\n')
    f.write(f'{space}{hdf5_geo_fn}:{path}/triangle_number_list\n')
    f.write(f'{space}</DataItem>\n')
    space = space[:-1]
    f.write(f'{space}</Topology>\n\n')

    # nodes
    f.write(f'{space}<Geometry GeometryType="XYZ">\n')
    space += '\t'
    f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_nodes} 3">\n')
    f.write(f'{space}{hdf5_geo_fn}:{node_path}/node_coord\n')
    f.write(f'{space}</DataItem>\n')
    space = space[:-1]
    f.write(f'{space}</Geometry>\n\n')

    # link tissue type to tris geometry for visualization
    if 'tri_tissue_type' in hdf5_geo[path + '/']:
        f.write(f'{space}<Attribute Name="tissue_type" AttributeType="Scalar" Center="Cell">\n')
        space += '\t'
        f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_tris} 1">\n')
        f.write(f'{space}{hdf5_geo_fn}:{path}/tri_tissue_type\n')
        f.write(f'{space}</DataItem>\n')
        space = space[:-1]
        f.write(f'{space}</Attribute>\n\n')
    # link data in tris to geometry
    if '/data/tris' in hdf5:

        # elm type
        if 'tri_elm_type' in hdf5_geo[path + '/']:
            f.write(f'{space}<Attribute Name="elm_type" AttributeType="Scalar" Center="Cell">\n')
            space += '\t'
            f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_tris} 1">\n')
            f.write(f'{space}{hdf5_geo_fn}:{path}/tri_elm_type\n')
            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Attribute>\n')

        for key, data in hdf5['/data/tris'].items():

            value = ""
            try:
                if 'value' in list(data.keys()):
                    data = data['value']
                    value = '/value'
            except (KeyError, AttributeError):
                pass
            if hasattr(data, 'shape') and len(data.shape) > 1:
                if data.shape[1] == 3:
                    attr_type = "Vector"
                    dim = 3
                elif data.shape[1] == 1:
                    attr_type = "Scalar"
                    dim = 1
                else:
                    print(("Data shape unknown: " + str(data.shape[1])))
                    attr_type, dim = None, None  # just to make compiler happy
                    quit()
            else:
                attr_type = "Scalar"
                dim = 1

            f.write(f'{space}<Attribute Name="{key}" AttributeType="{attr_type}" Center="Cell">\n')
            space += '\t'
            f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_tris} {dim} ">\n')
            f.write(f'{space}{hdf5_fn}:/data/tris/{key}{value}\n')
            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Attribute>\n\n')

    # node data
    if '/data/nodes' in hdf5:
        # data sets (mostly statistics)
        space += '\t'
        for key, data in hdf5['/data/nodes'].items():
            value = ""
            try:
                if 'value' in list(data.keys()):
                    data = data['value']
                    value = '/value'
            except (KeyError, AttributeError):
                pass
            if hasattr(data, 'shape') and len(data.shape) > 1:
                if data.shape[1] == 3:
                    attr_type = "Vector"
                    dim = 3
                elif data.shape[1] == 1:
                    attr_type = "Scalar"
                    dim = 1
                else:
                    print(("Data shape unknown: " + str(data.shape[1])))
                    attr_type, dim = None, None  # just to make compiler happy
                    quit()

            else:
                attr_type = "Scalar"
                dim = 1

            f.write(f'{space}<Attribute Name="{key}" AttributeType="{attr_type}" Center="Node">\n')
            f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_nodes}  {dim}">\n')
            f.write(f'{hdf5_fn}:/data/nodes/{key}{value}\n')

            f.write('</DataItem>\n')
            f.write('</Attribute>\n')
    space = space[:-1]
    f.write(f'{space}</Grid>\n\n')

    # ...one grid for tetrahedra...
    ##################################
    if n_tets > 0:
        f.write(f'{space}<Grid Name="tets" GridType="Uniform">\n')
        space += '\t'
        f.write(f'{space}<Topology NumberOfElements="{n_tets}" TopologyType="Tetrahedron" Name="Tet">\n')
        space += '\t'
        f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_tets} 4">\n')
        f.write(f'{space}{hdf5_geo_fn}:{path}/tetrahedra_number_list\n')
        f.write(f'{space}</DataItem>\n')
        space = space[:-1]
        f.write(f'{space}</Topology>\n\n')

        # nodes
        f.write(f'{space}<Geometry GeometryType="XYZ">\n')
        space += '\t'
        f.write(f'{space}<DataItem Format=\"HDF\" Dimensions=\"{n_nodes} 3">\n')
        f.write(f'{space}{hdf5_geo_fn}:{node_path}/node_coord\n')
        f.write(f'{space}</DataItem>\n')
        space = space[:-1]
        f.write(f'{space}</Geometry>\n')

        # link tissue type to tets geometry for visualization
        if 'tet_tissue_type' in hdf5_geo[path + '/']:
            f.write(f'{space}<Attribute Name="tissue_type" AttributeType="Scalar" Center="Cell">\n')
            space += '\t'
            f.write(f'{space}<DataItem Format=\"HDF\" Dimensions=\"{n_tets} 1\">\n')
            f.write(f'{space}{hdf5_geo_fn}:{path}/tet_tissue_type\n')

            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Attribute>\n')

        # data in tets
        if '/data/tets' in hdf5 or '/data/nodes' in hdf5 or '/mesh/fields' in hdf5:

            # elm type
            if 'tet_elm_type' in hdf5_geo[path + '/']:
                f.write('<Attribute Name="elm_type" AttributeType="Scalar" Center="Cell">\n')
                f.write(f'<DataItem Format=\"HDF\" Dimensions=\"{n_tets} 1\">\n')
                f.write(f'{hdf5_geo_fn}:{path}/tet_elm_type\n')
                f.write(f'</DataItem>\n')
                f.write(f'</Attribute>\n')

            # link tet data to geometry
            if '/data/tets' in hdf5:
                # data sets (mostly statistics)
                for key, data in hdf5['/data/tets'].items():
                    value = ""
                    try:
                        if 'value' in list(data.keys()):
                            data = data['value']
                            value = '/value'
                    except (KeyError, AttributeError):
                        pass
                    if hasattr(data, 'shape') and len(data.shape) > 1:
                        if data.shape[1] == 3:
                            attr_type = "Vector"
                            dim = 3
                        elif data.shape[1] == 1:
                            attr_type = "Scalar"
                            dim = 1
                        else:
                            print(("Data shape unknown: " + str(data.shape[1])))
                            attr_type, dim = None, None  # just to make compiler happy
                            quit()
                    else:
                        attr_type = "Scalar"
                        dim = 1

                    f.write('<Attribute Name="' + key + '" AttributeType="' + attr_type + '" Center="Cell">\n')
                    f.write('<DataItem Format="HDF" Dimensions="' + str(n_tets) + ' ' + str(dim) + '">\n')
                    f.write(hdf5_fn + ':/data/tets/' + key + value + '\n')

                    f.write('</DataItem>\n')
                    f.write('</Attribute>\n')
        space = space[:-1]
        f.write(f'{space}</Grid>\n')
    # end tetrahedra data

    # one grid for coil dipole nodes...store data hdf5.
    #######################################################
    if '/coil' in hdf5:
        f.write('<Grid Name="coil" GridType="Uniform">\n')
        f.write('<Topology NumberOfElements="' + str(len(hdf5['/coil/dipole_position'][:])) +
                '" TopologyType="Polyvertex" Name="Tri">\n')
        f.write('<DataItem Format="XML" Dimensions="' + str(len(hdf5['/coil/dipole_position'][:])) + ' 1">\n')
        # f.write(hdf5_fn + ':' + path + '/triangle_number_list\n')
        np.savetxt(f, list(range(len(hdf5['/coil/dipole_position'][:]))), fmt='%d',
                   delimiter=' ')  # 1 2 3 4 ... N_Points
        f.write('</DataItem>\n')
        f.write('</Topology>\n')

        # nodes
        f.write('<Geometry GeometryType="XYZ">\n')
        f.write('<DataItem Format="HDF" Dimensions="' + str(len(hdf5['/coil/dipole_position'][:])) + ' 3">\n')
        f.write(hdf5_fn + ':' + '/coil/dipole_position\n')
        f.write('</DataItem>\n')
        f.write('</Geometry>\n')

        # data
        if '/coil/dipole_moment_mag' in hdf5:
            # dipole magnitude
            f.write('<Attribute Name="dipole_mag" AttributeType="Scalar" Center="Cell">\n')
            f.write('<DataItem Format="HDF" Dimensions="' + str(len(hdf5['/coil/dipole_moment_mag'][:])) + ' 1">\n')
            f.write(hdf5_fn + ':' + '/coil/dipole_moment_mag\n')

            f.write('</DataItem>\n')
            f.write('</Attribute>\n')

        f.write('</Grid>\n')
        # end coil dipole data

    # footer
    f.write('</Grid>\n')
    f.write('</Domain>\n')
    f.write('</Xdmf>\n')
    f.close()

    return xdmf_fn


def write_temporal_xdmf(hdf5_fn, data_folder='c', coil_center_folder=None, coil_ori_0_folder=None,
                        coil_ori_1_folder=None, coil_ori_2_folder=None, coil_current_folder=None, hdf5_geo_fn=None,
                        overwrite_xdmf=False, verbose=False):
    """
    Creates .xdmf markup file for given ROI hdf5 data file with 4D data. This was written to be able to visualize data
    from the permutation analysis of the regression approach
    It expects an .hdf5 with a data group with (many) subarrays. The N subarrays name should be named from 0 to N-1
    Each subarray has shape = (N_elemns,1)

    Not tested for whole brain.

    hdf5:/data_folder/0
                     /1
                     /2
                     /3
                     /4
                     ...

    Parameters
    ----------
    hdf5_fn : str
        Filename of hdf5 file containing the data
    data_folder : str
        Path within hdf5 to group of dataframes
    hdf5_geo_fn : str (optional)
        Filename of hdf5 file containing the geometry
    overwrite_xdmf : boolean
        Overwrite existing xdmf file if present
    coil_center_folder :  str
    coil_ori_0_folder : str
    coil_ori_1_folder : str
    coil_ori_2_folder : str
    coil_current_folder : str
    verbose : boolean
        Print output or not

    Returns
    -------
    <File> : .xdmf file
        hdf5_fn[-4].xdmf
    """
    hdf5_fn_full = hdf5_fn

    if os.path.splitext(hdf5_fn)[1] not in ['.hdf5', '.h5', '.hdf']:
        print("Provide .hdf5 filename for existing file.")
        return

    xdmf_fn = os.path.splitext(hdf5_fn)[0] + '.xdmf'
    try:
        hdf5 = h5py.File(hdf5_fn, 'r+')
        hdf5_geo = h5py.File(hdf5_fn, 'r+')
    except IOError:
        print((hdf5_fn + " does not exists. Quitting."))
        return

    if verbose:
        print("Creating " + xdmf_fn)
    # splitted = False
    if hdf5_geo_fn is not None:
        # splitted = True
        try:
            hdf5_geo = h5py.File(hdf5_geo_fn, 'r+')
        except IOError:
            print((hdf5_geo_fn + " does not exists. Quitting."))
            return
    else:
        hdf5_geo_fn = os.path.basename(hdf5_fn)
    if os.path.split(hdf5_fn)[0] == os.path.split(hdf5_geo_fn)[0]:
        hdf5_geo_fn = os.path.basename(hdf5_geo_fn)

    hdf5_fn = os.path.basename(hdf5_fn)
    if os.path.isfile(xdmf_fn) and not overwrite_xdmf:
        print((xdmf_fn + ' already exists. Remove or set overwriteXDMF. Quitting.'))
        return

    # check if triangle and tetra data is already in 2 dataframes in hdf5
    # /mesh/elm or /elm/?
    if "/elm/" in hdf5_geo:
        path = '/elm'
    else:
        path = '/mesh/elm'

    if "/nodes/" in hdf5_geo:
        node_path = '/nodes'
    else:
        node_path = '/mesh/nodes'

    if path + "/triangle_number_list" not in hdf5_geo:

        # if not, create
        if verbose:
            print(("triangle_number_list and tetrahedra_number_list do not exist. Adding to " + hdf5_geo_fn + "."))

        # get tris and tets
        triangles = (hdf5_geo[path + '/node_number_list'][:]  # from node_number list...
                     [hdf5_geo[path + '/elm_type'][:] == 2]  # ... take the triangle ones...
        [:, 0:3])
        tetrahedra = (hdf5_geo[path + '/node_number_list'][:]  # same with tetrahedra nodelist
        [hdf5_geo[path + '/elm_type'][:] == 4])

        # add to hdf5_fn and rebase to 0
        hdf5_geo.create_dataset(f'{path}/triangle_number_list', data=triangles - 1)
        hdf5_geo.create_dataset(f'{path}/tetrahedra_number_list', data=tetrahedra - 1)
        n_tets = len(tetrahedra)

    else:
        triangles = hdf5_geo[f'{path}/triangle_number_list']
        try:
            tetrahedra = hdf5_geo[path + '/tetrahedra_number_list']
            n_tets = len(tetrahedra)
        except KeyError:
            tetrahedra = None
            n_tets = 0

    # check if data is divided into tets and tris

    # get information for .xdmf
    n_nodes = len(hdf5_geo[f'{node_path}/node_coord'])
    n_tris = len(triangles)
    # n_tets = len(tetrahedra)

    # get shape of temporal information
    dimensions = dict()
    if data_folder is not None:
        if isinstance(data_folder, list):
            allkeys = [set(hdf5[dat_folder].keys()) for dat_folder in data_folder]
            data_keys = set.intersection(*allkeys)
            allkeys = set.union(*allkeys)
            dif = allkeys.difference(data_keys)
            if len(dif) != 0:
                warnings.warn(f"Unequal sets of keys found. Missing keys: {dif}")

            # get first value from dict to get shape of data array
            for dat_folder in data_folder:
                dimensions[dat_folder] = next(iter(hdf5[dat_folder].values())).shape[0]

        else:
            data_keys = hdf5[data_folder].keys()
            dimensions[data_folder] = next(iter(hdf5[data_folder].values())).shape[0]
    else:
        data_keys = hdf5[coil_center_folder].keys()
        dimensions[data_folder] = next(iter(hdf5[coil_center_folder].values())).shape[0]

    # create .xdmf file
    f = open(xdmf_fn, 'w')
    space = '\t'
    # header
    f.write('<?xml version="1.0"?>\n')
    f.write('<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>\n')
    f.write('<Xdmf Version="2.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n')
    f.write('<Domain>\n')

    # one collection grid
    # f.write('<Grid\nCollectionType="Spatial"\nGridType="Collection"\nName="Collection">\n')
    f.write(f'{space}<Grid Name="GridTime" GridType="Collection" CollectionType="Temporal">\n')
    space += '\t'
    for i in data_keys:
        f.write("\n<!-- " + '#' * 20 + f" Timestep {i:0>3}/{len(data_keys): >3} " + '#' * 20 + ' -->\n')
        if data_folder is not None:
            # one grid for triangles...
            ###########################
            f.write(f'{space}<Grid Name="tris" GridType="Uniform">\n')
            space += '\t'
            f.write(f'{space}<Time Value="{i}" />	\n')
            f.write(f'{space}<Topology NumberOfElements="{n_tris}" TopologyType="Triangle" Name="Tri">\n')
            space += '\t'
            f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_tris} 3">\n')
            space += '\t'
            f.write(f'{space}{hdf5_geo_fn}:{path}/triangle_number_list\n')
            space = space[:-1]
            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Topology>\n\n')

            # nodes
            f.write(f'{space}<Geometry GeometryType="XYZ">\n')
            space += '\t'
            f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_nodes} 3">\n')
            f.write(f'{space}{hdf5_geo_fn}:{node_path}/node_coord\n')
            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Geometry>\n\n')

            # data
            if isinstance(data_folder, list):
                for dat_folder in data_folder:
                    # scalar or vector
                    if len(next(iter(hdf5[data_folder].values())).shape) > 1:
                        attrtype = 'Vector'
                        data_dims = 3
                    else:
                        attrtype = 'Scalar'
                        data_dims = 1

                    f.write(f'{space}<Attribute Name="{dat_folder}" AttributeType="{attrtype}" Center="Cell">\n')
                    space += '\t'
                    f.write(f'{space}<DataItem Format="HDF" Dimensions="{dimensions[dat_folder]} {data_dims}">\n')
                    f.write(f'{space}{hdf5_fn}:{dat_folder}/{i}\n')
                    f.write(f'{space}</DataItem>\n')
                    space = space[:-1]
                    f.write(f'{space}</Attribute>\n\n')
            else:
                # scalar or vector
                if len(np.squeeze(next(iter(hdf5[data_folder].values()))).shape) > 1:
                    attrtype = 'Vector'
                    data_dims = 3
                else:
                    attrtype = 'Scalar'
                    data_dims = 1
                f.write(f'{space}<Attribute Name="{data_folder}" AttributeType="{attrtype}" Center="Cell">\n')
                space += '\t'
                f.write(f'{space}<DataItem Format="HDF" Dimensions="{dimensions[data_folder]} {data_dims}">\n')
                f.write(f'{space}{hdf5_fn}:{data_folder}/{i}\n')
                f.write(f'{space}</DataItem>\n')

                space = space[:-1]
                f.write(f'{space}</Attribute>\n\n')

            #     for key, data in hdf5['/data/tris'].items():
            #
            #         value = ""
            #         try:
            #             if 'value' in list(data.keys()):
            #                 data = data['value']
            #                 value = '/value'
            #         except (KeyError, AttributeError):
            #             pass
            #         if hasattr(data, 'shape') and len(data.shape) > 1:
            #             if data.shape[1] == 3:
            #                 attr_type = "Vector"
            #                 dim = 3
            #             elif data.shape[1] == 1:
            #                 attr_type = "Scalar"
            #                 dim = 1
            #             else:
            #                 print(("Data shape unknown: " + str(data.shape[1])))
            #                 quit()
            #         else:
            #             attr_type = "Scalar"
            #             dim = 1
            #         assert attr_type
            #         assert dim
            #         # except IndexError or AttributeError:
            #         #                 AttrType = "Scalar"
            #         #                 dim = 1
            #
            #         f.write('<Attribute Name="' + key + '" AttributeType="' + attr_type + '" Center="Cell">\n')
            #         f.write('<DataItem Format="HDF" Dimensions="' + str(n_tris) + ' ' + str(dim) + '">\n')
            #         f.write(hdf5_fn + ':/data/tris/' + key + value + '\n')
            #         f.write('</DataItem>\n')
            #         f.write('</Attribute>\n')
            #         # node data
            # if '/data/nodes' in hdf5:
            #     # data sets (mostly statistics)
            #     for key, data in hdf5['/data/nodes'].items():
            #         value = ""
            #         try:
            #             if 'value' in list(data.keys()):
            #                 data = data['value']
            #                 value = '/value'
            #         except (KeyError, AttributeError):
            #             pass
            #         if hasattr(data, 'shape') and len(data.shape) > 1:
            #             if data.shape[1] == 3:
            #                 attr_type = "Vector"
            #                 dim = 3
            #             elif data.shape[1] == 1:
            #                 attr_type = "Scalar"
            #                 dim = 1
            #             else:
            #                 print(("Data shape unknown: " + str(data.shape[1])))
            #                 quit()
            #
            #                 #                 except IndexError or AttributeError:
            #         else:
            #             attr_type = "Scalar"
            #             dim = 1
            #
            #         f.write('<Attribute Name="' + key + '" AttributeType="' + attr_type + '" Center="Node">\n')
            #         f.write('<DataItem Format="HDF" Dimensions="' + str(n_nodes) + ' ' + str(dim) + '">\n')
            #         f.write(hdf5_fn + ':/data/nodes/' + key + value + '\n')
            #
            #         f.write('</DataItem>\n')
            #         f.write('</Attribute>\n')
            # f.write('</Grid>\n')

            # # ...one grid for tetrahedra...
            # ##################################
            # f.write('<Grid Name="tets" GridType="Uniform">\n')
            # f.write('<Topology NumberOfElements="' + str(n_tris) + '" TopologyType="Tetrahedron" Name="Tet">\n')
            # f.write('<DataItem Format="HDF" Dimensions="' + str(n_tets) + ' 4">\n')
            # f.write(hdf5_geo_fn + ':' + path + '/tetrahedra_number_list\n')
            # f.write('</DataItem>\n')
            # f.write('</Topology>\n')

            # nodes
            f.write(f'{space}<Geometry GeometryType="XYZ">\n')
            space += '\t'
            f.write(f'{space}<DataItem Format="HDF" Dimensions="{n_nodes} 3">\n')
            f.write(f'{space}{hdf5_geo_fn}:{node_path}/node_coord\n')
            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Geometry>\n')

            # link tissue type to tets geometry for visualization
            # if 'tet_tissue_type' in hdf5_geo[path + '/']:
            #     f.write(f'{space}<Attribute Name="tissue_type" AttributeType="Scalar" Center="Cell">\n')
            #     space += '\t'
            #     f.write(f'{space}<DataItem Format=\"HDF\" Dimensions=\"{n_tets} 1\">\n')
            #     f.write(f'{space}{hdf5_geo_fn}:{path}/tet_tissue_type\n')
            #     f.write(f'{space}</DataItem>\n')
            #     space = space[:-1]
            #     f.write(f'{space}</Attribute>\n')
            #     space = space[:-1]
            # if 'tet_tissue_type' in hdf5_geo[path + '/']:
            if 'tri_tissue_type' in hdf5_geo[path].keys():
                f.write(f'{space}<Attribute Name="tissue_type" AttributeType="Scalar" Center="Cell">\n')
                space += '\t'
                f.write(f'{space}<DataItem Format=\"HDF\" Dimensions=\"{n_tris} 1\">\n')
                f.write(f'{space}{hdf5_geo_fn}:{path}/tri_tissue_type\n')
                f.write(f'{space}</DataItem>\n')
                space = space[:-1]
                f.write(f'{space}</Attribute>\n')
            space = space[:-1]

            # data in tets
            if '/data/tets' in hdf5 or '/data/nodes' in hdf5 or '/mesh/fields' in hdf5:

                # elm type
                if 'tet_elm_type' in hdf5_geo[path + '/']:
                    f.write('<Attribute Name="elm_type" AttributeType="Scalar" Center="Cell">\n')
                    f.write(f'<DataItem Format=\"HDF\" Dimensions=\"{str(n_tets)} 1\">\n')
                    f.write(hdf5_geo_fn + ':' + path + '/tet_elm_type\n')
                    f.write('</DataItem>\n')
                    f.write('</Attribute>\n\n')

                # link tet data to geometry
                if '/data/tets' in hdf5:
                    # data sets (mostly statistics)
                    for key, data in hdf5['/data/tets'].items():
                        value = ""
                        try:
                            if 'value' in list(data.keys()):
                                data = data['value']
                                value = '/value'
                        except (KeyError, AttributeError):
                            pass
                        if hasattr(data, 'shape') and len(data.shape) > 1:
                            if data.shape[1] == 3:
                                attr_type = "Vector"
                                dim = 3
                            elif data.shape[1] == 1:
                                attr_type = "Scalar"
                                dim = 1
                            else:
                                print(("Data shape unknown: " + str(data.shape[1])))
                                attr_type, dim = 0, 0
                                quit()
                        else:
                            attr_type = "Scalar"
                            dim = 1

                        f.write('<Attribute Name="' + key + '" AttributeType="' + attr_type + '" Center="Cell">\n')
                        f.write(f'<DataItem Format=\"HDF\" Dimensions=\"{n_tets} {dim}\">\n')
                        f.write(hdf5_fn + ':/data/tets/' + key + value + '\n')

                        f.write('</DataItem>\n')
                        f.write('</Attribute>\n')

            f.write(f'{space}</Grid>\n\n')
            # end tetrahedra data

    # footer
    space = space[:-1]
    f.write(f'{space}</Grid>\n\n')

    # one grid for coil dipole nodes...store data hdf5.
    #######################################################
    if '/coil' in hdf5:
        for i in data_keys:
            f.write(f'{space}<Grid Name="GridTime" GridType="Collection" CollectionType="Temporal">\n')

            f.write(f'{space}<Grid Name="coil" GridType="Uniform">\n')
            space += '\t'
            f.write(f'{space}<Time Value="{i}" />	\n')
            f.write(f'{space}<Topology NumberOfElements="' + str(len(hdf5[f'/coil/dipole_position/{i}'][:])) +
                    '" TopologyType="Polyvertex" Name="Tri">\n')
            space += '\t'
            f.write(
                    f'{space}<DataItem Format="XML" Dimensions="' + str(
                            len(hdf5[f'/coil/dipole_position/{i}'][:])) + ' 1">\n')
            # f.write(hdf5_fn + ':' + path + '/triangle_number_list\n')
            np.savetxt(f, list(range(len(hdf5[f'/coil/dipole_position/{i}'][:]))), fmt='%d',
                       delimiter=' ')  # 1 2 3 4 ... N_Points
            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Topology>\n\n')

            # nodes
            f.write(f'{space}<Geometry GeometryType="XYZ">\n')
            space += '\t'
            f.write(
                    f'{space}<DataItem Format="HDF" Dimensions="' + str(
                            len(hdf5[f'/coil/dipole_position/{i}'][:])) + ' 3">\n')

            f.write(space + hdf5_fn + ':' + f'/coil/dipole_position/{i}\n')

            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Geometry>\n\n')
            space = space[:-1]
            # data
            if '/coil/dipole_moment_mag' in hdf5:
                # dipole magnitude
                f.write('<Attribute Name="dipole_mag" AttributeType="Scalar" Center="Cell">\n')
                f.write('<DataItem Format="HDF" Dimensions="' + str(
                        len(hdf5[f'/coil/dipole_moment_mag/{i}'][:])) + ' 1">\n')
                f.write(hdf5_fn + ':' + f'/coil/dipole_moment_mag/{i}\n')

                f.write('</DataItem>\n')
                f.write('</Attribute>\n')

            f.write(f'{space}</Grid>\n')
            # end coil dipole data
            f.write(f'{space}</Grid>\n\n')

    # one grid for coil dipole nodes...store data hdf5.
    #######################################################
    if coil_center_folder is not None:
        f.write(f'{space}<Grid Name="GridTime" GridType="Collection" CollectionType="Temporal">\n')
        for i in data_keys:
            space += '\t'
            with h5py.File(hdf5_fn_full, "r") as g:
                n_coil_pos = g[f"{coil_center_folder}/{i}"][:].shape[0]
            f.write(f'{space}<Grid Name="stimsites" GridType="Uniform">\n')
            space += '\t'
            f.write(f'{space}<Time Value="{i}" />	\n')

            f.write(
                    f'{space}<Topology NumberOfElements="' + str(
                        n_coil_pos) + '" TopologyType="Polyvertex" Name="Tri">\n')
            space += '\t'
            f.write(f'{space}<DataItem Format="XML" Dimensions="' + str(n_coil_pos) + ' 1">\n')
            space += '\t'
            np.savetxt(f, list(range(n_coil_pos)), fmt='%d', delimiter=' ')  # 1 2 3 4 ... N_Points
            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Topology>\n\n')

            # nodes
            f.write(f'{space}<Geometry GeometryType="XYZ">\n')
            space += '\t'
            f.write(f'{space}<DataItem Format="HDF" Dimensions="' + str(n_coil_pos) + ' 3">\n')
            space += '\t'
            f.write(f'{space}{hdf5_fn}:{coil_center_folder}/{i}\n')
            space = space[:-1]
            f.write(f'{space}</DataItem>\n')
            space = space[:-1]
            f.write(f'{space}</Geometry>\n\n')

            coil_ori_folder = [coil_ori_0_folder, coil_ori_1_folder, coil_ori_2_folder]

            for j in range(3):
                f.write(f'{space}<Attribute Name="dir_' + str(j) + '" AttributeType="Vector" Center="Cell">\n')
                space += '\t'
                f.write(f'{space}<DataItem Format="HDF" Dimensions="' + str(n_coil_pos) + ' 3">\n')
                space += '\t'
                f.write(f'{space}{hdf5_fn}:{coil_ori_folder[j]}/{i}\n')
                space = space[:-1]
                f.write(f'{space}</DataItem>\n')
                space = space[:-1]
                f.write(f'{space}</Attribute>\n\n')

            if coil_current_folder is not None:
                f.write(f'{space}<Attribute Name="current" AttributeType="Scalar" Center="Cell">\n')
                space += '\t'
                f.write(f'{space}<DataItem Format="HDF" Dimensions="' + str(n_coil_pos) + ' 1">\n')
                space += '\t'
                f.write(f'{space}{hdf5_fn}:{coil_current_folder}/{i}\n')
                space = space[:-1]
                f.write(f'{space}</DataItem>\n')
                space = space[:-1]
                f.write(f'{space}</Attribute>\n\n')

            space = space[:-1]
            f.write(f'{space}</Grid>\n\n')
        space = space[:-1]
        f.write(f'{space}</Grid>\n\n')

    f.write('</Domain>\n')
    f.write('</Xdmf>\n')
    f.close()


def print_attrs(name, obj):
    """
    Helper function for hdf_2_ascii. To be called from h5py.Group.visititems()

    Parameters
    ----------
    name : str
        Name of structural element
    obj : object
        Structural element

    Returns
    -------
    <Print> : Structure of .hdf5 file
    """

    import h5py

    if isinstance(obj, h5py.Dataset):
        print(('/' + name + '\t\t ' + str(obj.shape)))
    else:
        print(('\n/' + name))

    for key, val in obj.attrs.items():
        print("    %s: %s" % (key, val))


def hdf_2_ascii(hdf5_fn):
    """
    Prints out structure of given .hdf5 file.

    Parameters
    ----------
    hdf5_fn : str
        Filename of .hdf5 file.

    Returns
    -------
    h5 : items
        Structure of .hdf5 file
    """

    import h5py

    print('/')

    h5 = h5py.File(hdf5_fn, 'r')
    h5.visititems(print_attrs)


def simnibs_results_msh2hdf5_workhorse(fn_msh, fn_hdf5, S, pos_tms_idx, pos_local_idx, subject, mesh_idx,
                                       mode_xdmf="r+",
                                       verbose=False, overwrite=False, mid2roi=False):
    """
    Converts simnibs .msh results file to .hdf5 (including midlayer data if desired)

    Parameters
    ----------
    fn_msh : list of str
        Filenames (incl. path) of .msh results files from simnibs
    fn_hdf5 : str or list of str
        Filenames (incl. path) of .hdf5 results files
    S : Simnibs Session object
        Simnibs Session object the simulations are conducted with
    pos_tms_idx : list of int
        Index of the simulation w.r.t. to the simnibs TMSList (inside Session object S)
        For every coil a separate TMSList exists, which contains multiple coil positions.
    pos_local_idx : list of int
        Index of the simulation w.r.t. to the simnibs POSlist in the TMSList (inside Session object S)
        For every coil a separate TMSList exists, which contains multiple coil positions.
    subject : Subject object
        Subject object loaded from .pkl file
    mesh_idx : int
        Mesh index
    mode_xdmf : str, optional, default: "r+"
        Mode to open hdf5_geo file to write xdmf. If hdf5_geo is already separated in tets and tris etc,
        the file is not changed, use "r" to avoid IOErrors in case of parallel computing.
    verbose : bool, optional, default: False
        Print output messages
    overwrite: bool, optional, default: False
        Overwrite .hdf5 file if existing
    mid2roi : bool, list of string, or string, optional, default:False
        If the mesh contains ROIs and the e-field was calculated in the midlayer using simnibs (S.map_to_surf = True),
        the midlayer results will be mapped from the simnibs midlayer to the ROIs (takes some time for large ROIs)

    Returns
    -------
    <File> : .hdf5 file
        .hdf5 file containing the results. An .xdmf file is also created to link the results with the mesh .hdf5 file
        of the subject
    """

    if type(fn_msh) is not list:
        fn_msh = [fn_msh]

    if type(fn_hdf5) is not list:
        fn_hdf5 = [fn_hdf5]

    if type(mid2roi) is str:
        mid2roi = [mid2roi]

    # Save results in .hdf5 format
    regex = r"[\d]-[\d]{4}"

    idx = np.hstack((np.array(pos_tms_idx)[:, None], np.array(pos_local_idx)[:, None]))

    for f_msh in fn_msh:
        indices = np.array(re.findall(regex, f_msh)[0].split("-")).astype(int) - 1
        f_tms_idx = indices[0]
        f_local_idx = indices[1]
        f_global_idx = np.where((idx == indices).all(axis=1))[0][0]

        if os.path.exists(fn_hdf5[f_global_idx] + ".hdf5") and not overwrite:
            if verbose:
                print(f"Skipping {f_msh} --> {fn_hdf5[f_global_idx]}.hdf5")
            continue

        if verbose:
            print(f"Transforming {f_msh} --> {fn_hdf5[f_global_idx]}.hdf5")

        # read dipole position and magnitude
        fn_coil_geo = os.path.join(S.pathfem,
                                   os.path.splitext(os.path.split(S.fnamehead)[1])[0] +
                                   "_TMS_" +
                                   str(f_tms_idx + 1) + "-" + str(f_local_idx + 1).zfill(4) + "_" +
                                   os.path.splitext(
                                           os.path.splitext(os.path.split(S.poslists[f_tms_idx].fnamecoil)[1])[0])[0] +
                                   "_nii_coil_pos.geo")

        # for some reason, the .geo file of the simulation was not saved ...
        try:
            dipole_position, dipole_moment_mag = pynibs.read_coil_geo(fn_coil_geo)
        except FileNotFoundError:
            dipole_position = np.array([[0, 0, 0]])
            dipole_moment_mag = np.array([[0]])
            Warning(f"Coil .geo file not found... Skipping coil positions ({fn_coil_geo})")

        # read .msh results file from SimNIBS
        msh = read_msh(f_msh)

        # collect data
        data = [dipole_position, dipole_moment_mag]
        data_names = ["coil/dipole_position", "coil/dipole_moment_mag"]

        for i in range(len(msh.nodedata)):
            data_names.append("data/nodes/" + msh.nodedata[i].field_name)
            data.append(msh.nodedata[i].value)

        for i in range(len(msh.elmdata)):
            data_names.append("data/tris/" + msh.elmdata[i].field_name)
            data.append(msh.elmdata[i].value[msh.elm.elm_type == 2, ])

            data_names.append("data/tets/" + msh.elmdata[i].field_name)
            data.append(msh.elmdata[i].value[msh.elm.elm_type == 4, ])

            # save dadt also in nodes (does require TBs of RAM because of inversion,
            # there is maybe a more elegant way using SimNIBS directly)
            # if msh.elmdata[i].field_name == "D":
            #    data_names.append("data/nodes/D")
            #    con_tets = msh.elm.node_number_list[msh.elm.elm_type == 4, ]
            #    data.append(pynibs.mesh.data_elements2nodes(msh.elmdata[i].value[msh.elm.elm_type == 4, ], con_tets))

        # write .hdf5 file data
        write_data_hdf5(out_fn=os.path.splitext(fn_hdf5[f_global_idx])[0] + ".hdf5",
                        data=data,
                        data_names=data_names,
                        hdf5_path='',
                        mode="w")

        # write .xdmf markup file for paraview
        write_xdmf(hdf5_fn=os.path.splitext(fn_hdf5[f_global_idx])[0] + ".hdf5",
                   hdf5_geo_fn=os.path.join(subject.subject_folder, 'mesh', str(mesh_idx),
                                            subject.mesh[mesh_idx]["fn_mesh_hdf5"]),
                   overwrite_xdmf=True,
                   verbose=False,
                   mode=mode_xdmf)

        # if calculated from Simnibs copy and crop midlayer results to ROIs
        if S.map_to_surf and mid2roi is not False:
            try:

                # load rois
                if verbose:
                    print(f"Loading ROIs")

                roi = pynibs.load_roi_surface_obj_from_hdf5(fname=os.path.join(subject.subject_folder,
                                                                               'mesh',
                                                                               str(mesh_idx),
                                                                               subject.mesh[mesh_idx]["fn_mesh_hdf5"]))
                mesh_folder = os.path.join(subject.subject_folder,
                                           'mesh', str(mesh_idx),
                                           subject.mesh[mesh_idx]["mesh_folder"])

                for roi_idx in roi.keys():
                    # skip rois that are not wanted
                    if isinstance(mid2roi, list) and roi_idx not in mid2roi:
                        continue
                    # load freesurfer surface
                    if type(roi[roi_idx].gm_surf_fname) is not list:
                        roi[roi_idx].gm_surf_fname = [roi[roi_idx].gm_surf_fname]

                    points_gm = [None for _ in range(len(roi[roi_idx].gm_surf_fname))]
                    con_gm = [None for _ in range(len(roi[roi_idx].gm_surf_fname))]

                    max_idx_gm = 0

                    if (type(roi[roi_idx].gm_surf_fname) is list and roi[roi_idx].gm_surf_fname[0] is not None) or \
                            (type(roi[roi_idx].gm_surf_fname) is str):
                        if type(roi[roi_idx].gm_surf_fname) is str:
                            fn_surface = [roi[roi_idx].gm_surf_fname]
                        else:
                            fn_surface = roi[roi_idx].gm_surf_fname

                    elif (type(roi[roi_idx].midlayer_surf_fname) is list and
                          roi[roi_idx].gm_surf_fname is not None) or \
                            (type(roi[roi_idx].midlayer_surf_fname) is str):
                        if type(roi[roi_idx].midlayer_surf_fname) is str:
                            fn_surface = [roi[roi_idx].midlayer_surf_fname]
                        else:
                            fn_surface = roi[roi_idx].midlayer_surf_fname

                    for i in range(len(fn_surface)):
                        gii_obj = nibabel.load(os.path.join(mesh_folder, fn_surface[i]))
                        points_gm[i] = gii_obj.darrays[0].data
                        con_gm[i] = gii_obj.darrays[1].data

                        # points_gm[i], con_gm[i] = nibabel.freesurfer.read_geometry(
                        #     os.path.join(mesh_folder, fn_surface[i]))

                        con_gm[i] = con_gm[i] + max_idx_gm

                        max_idx_gm = max_idx_gm + points_gm[i].shape[0]  # np.max(con_gm[i]) + 2

                    # points_gm = np.vstack(points_gm)
                    con_gm = np.vstack(con_gm)

                    if verbose:
                        print(f"Processing data to ROI #{roi_idx}")

                    if roi[roi_idx].fn_mask is None or roi[roi_idx].fn_mask == []:
                        if roi[roi_idx].x_roi is None or roi[roi_idx].x_roi == []:
                            roi[roi_idx].x_roi = [-np.inf, np.inf]
                        if roi[roi_idx].y_roi is None or roi[roi_idx].y_roi == []:
                            roi[roi_idx].y_roi = [-np.inf, np.inf]
                        if roi[roi_idx].z_roi is None or roi[roi_idx].z_roi == []:
                            roi[roi_idx].z_roi = [-np.inf, np.inf]

                        roi_mask_bool = (roi[roi_idx].node_coord_mid[:, 0] > min(roi[roi_idx].X_ROI)) & (
                                roi[roi_idx].node_coord_mid[:, 0] < max(roi[roi_idx].X_ROI)) & \
                                        (roi[roi_idx].node_coord_mid[:, 1] > min(roi[roi_idx].Y_ROI)) & (
                                                roi[roi_idx].node_coord_mid[:, 1] < max(roi[roi_idx].Y_ROI)) & \
                                        (roi[roi_idx].node_coord_mid[:, 2] > min(roi[roi_idx].Z_ROI)) & (
                                                roi[roi_idx].node_coord_mid[:, 2] < max(roi[roi_idx].Z_ROI))
                        roi_mask_idx = np.where(roi_mask_bool)

                    else:
                        if type(roi[roi_idx].fn_mask) is np.ndarray:
                            if roi[roi_idx].fn_mask.ndim == 0:
                                roi[roi_idx].fn_mask = roi[roi_idx].fn_mask.astype(str).tolist()

                        # read mask from freesurfer mask file
                        mask = nibabel.freesurfer.mghformat.MGHImage.from_filename(
                                os.path.join(mesh_folder, roi[roi_idx].fn_mask)).dataobj[:]
                        roi_mask_idx = np.where(mask > 0.5)

                    # read results data
                    if verbose:
                        print("Reading SimNIBS midlayer data")
                    e_normal = []
                    e_tan = []

                    for fn_surf in fn_surface:
                        fn_msh_base = os.path.splitext(os.path.split(f_msh)[1])[0]

                        if "lh" in os.path.split(fn_surf)[1]:
                            fname_base = os.path.join(os.path.split(f_msh)[0], "subject_overlays", "lh." + fn_msh_base)

                        if "rh" in os.path.split(fn_surf)[1]:
                            fname_base = os.path.join(os.path.split(f_msh)[0], "subject_overlays", "rh." + fn_msh_base)

                        e_normal.append(
                                nibabel.freesurfer.read_morph_data(fname_base + ".central.E.normal").flatten()[:,
                                np.newaxis])
                        e_tan.append(
                                nibabel.freesurfer.read_morph_data(fname_base + ".central.E.tangent").flatten()[:,
                                np.newaxis])

                    e_normal = np.vstack(e_normal)
                    e_tan = np.vstack(e_tan)

                    # transform point data to element data
                    if verbose:
                        print("Transforming point data to element data")
                    e_normal = pynibs.data_nodes2elements(data=e_normal, con=con_gm)
                    e_tan = pynibs.data_nodes2elements(data=e_tan, con=con_gm)

                    # crop results data to ROI
                    # if not roi_mask_bool.all():
                    if roi_mask_idx:
                        if verbose:
                            print("Cropping data to ROI")

                        # get row index where all points are lying inside ROI
                        con_row_idx = [i for i in range(con_gm.shape[0]) if
                                       len(np.intersect1d(con_gm[i,], roi_mask_idx)) == 3]

                        e_normal = e_normal[con_row_idx, :].flatten()
                        e_tan = e_tan[con_row_idx, :].flatten()

                    e_mag = np.linalg.norm(np.vstack([e_normal, e_tan]).transpose(), axis=1).flatten()

                    if verbose:
                        print("Writing data to .hdf5")

                    with h5py.File(os.path.splitext(fn_hdf5[f_global_idx])[0] + ".hdf5", 'a') as f:
                        try:
                            del f['data/midlayer/roi_surface/{}/E_mag'.format(roi_idx)]
                            del f['data/midlayer/roi_surface/{}/E_tan'.format(roi_idx)]
                            del f['data/midlayer/roi_surface/{}/E_norm'.format(roi_idx)]
                        except KeyError:
                            pass

                        f.create_dataset('data/midlayer/roi_surface/{}/E_mag'.format(roi_idx), data=e_mag)
                        f.create_dataset('data/midlayer/roi_surface/{}/E_tan'.format(roi_idx), data=e_tan)
                        f.create_dataset('data/midlayer/roi_surface/{}/E_norm'.format(roi_idx), data=e_normal)

                    del e_mag, e_normal, e_tan
            except KeyError as e:
                warnings.warn(f"Could not map2surf: {e}")

        # Write info in .hdf5 file
        #######################################################################
        with h5py.File(os.path.splitext(fn_hdf5[f_global_idx])[0] + ".hdf5", 'a') as f:
            try:
                del f["info"]
            except KeyError:
                pass

            f.create_dataset("info/date", data=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            f.create_dataset("info/sigma_WM", data=S.poslists[f_tms_idx].cond[0].value)
            f.create_dataset("info/sigma_GM", data=S.poslists[f_tms_idx].cond[1].value)
            f.create_dataset("info/sigma_CSF", data=S.poslists[f_tms_idx].cond[2].value)
            f.create_dataset("info/sigma_Skull", data=S.poslists[f_tms_idx].cond[3].value)
            f.create_dataset("info/sigma_Scalp", data=S.poslists[f_tms_idx].cond[4].value)
            if len(S.poslists[f_tms_idx].cond) > 5:
                f.create_dataset("info/sigma_EyeBalls", data=S.poslists[f_tms_idx].cond[5].value)
            f.create_dataset("info/fn_coil", data=S.poslists[f_tms_idx].fnamecoil)
            f.create_dataset("info/matsimnibs", data=S.poslists[f_tms_idx].pos[f_local_idx].matsimnibs)
            f.create_dataset("info/dIdt", data=S.poslists[f_tms_idx].pos[f_local_idx].didt)
            f.create_dataset("info/anisotropy_type", data=S.poslists[f_tms_idx].anisotropy_type)
            f.create_dataset("info/fn_mesh_msh", data=S.fnamehead)

        # # Write .nfo file
        # #######################################################################
        # info = dict()
        # info['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # info['sigma_WM'] = S.poslists[f_tms_idx].cond[0].value  # WM
        # info['sigma_GM'] = S.poslists[f_tms_idx].cond[1].value  # GM
        # info['sigma_CSF'] = S.poslists[f_tms_idx].cond[2].value  # CSF
        # info['sigma_Skull'] = S.poslists[f_tms_idx].cond[3].value  # Skull
        # info['sigma_Scalp'] = S.poslists[f_tms_idx].cond[4].value  # Scalp
        # info['fn_coil'] = S.poslists[f_tms_idx].fnamecoil  # filename of TMS coil
        # info['matsimnibs'] = S.poslists[f_tms_idx].pos[f_local_idx].matsimnibs.tolist()  # coil loc and ori
        # info['dIdt'] = S.poslists[f_tms_idx].pos[f_local_idx].didt  # rate of change of coil current
        # info['anisotropy_type'] = S.poslists[f_tms_idx].anisotropy_type  # type of anisotropy model
        # info['fn_mesh_msh'] = S.fnamehead  # mesh
        #
        # import json
        #
        # with open(os.path.splitext(fn_hdf5[f_global_idx])[0] + ".nfo", 'w') as file:
        #     file.write(json.dumps(info, indent=0))  # use `json.loads` to do the reverse

        del f_global_idx


def simnibs_results_msh2hdf5(fn_msh, fn_hdf5, S, pos_tms_idx, pos_local_idx, subject, mesh_idx, mode_xdmf="r+",
                             n_cpu=4, verbose=False, overwrite=False, mid2roi=False):
    """
    Converts simnibs .msh results file(s) to .hdf5 / .xdmf tuple.

    Parameters
    ----------
    fn_msh : str list of str
        Filenames (incl. path) of .msh results files from simnibs
    fn_hdf5 : str or list of str
        Filenames (incl. path) of .hdf5 results files
    S : Simnibs Session object
        Simnibs Session object the simulations are conducted with
    pos_tms_idx : list of int
        Index of the simulation w.r.t. to the simnibs TMSList (inside Session object S)
        For every coil a separate TMSList exists, which contains multiple coil positions.
    pos_local_idx : list of int
        Index of the simulation w.r.t. to the simnibs POSlist in the TMSList (inside Session object S)
        For every coil a separate TMSList exists, which contains multiple coil positions.
    subject : Subject object
        Subject object loaded from .pkl file
    mesh_idx : int
        Mesh index
    mode_xdmf : str, optional, default: "r+"
        Mode to open hdf5_geo file to write xdmf. If hdf5_geo is already separated in tets and tris etc.,
        the file is not changed, use "r" to avoid IOErrors in case of parallel computing.
    n_cpu : int
        Number of processes
    verbose : bool, optional, default: False
        Print output messages
    overwrite: bool, optional, default: False
        Overwrite .hdf5 file if existing
    mid2roi : bool or string, optional, default: False
        If the mesh contains ROIs and the e-field was calculated in the midlayer using simnibs (S.map_to_surf = True),
        the midlayer results will be mapped from the simnibs midlayer to the ROIs (takes some time for large ROIs)

    Returns
    -------
    <File> : .hdf5 file
        .hdf5 file containing the results. An .xdmf file is also created to link the results with the mesh .hdf5 file
        of the subject
    """
    n_cpu_available = multiprocessing.cpu_count()
    n_cpu = min(n_cpu, n_cpu_available, len(fn_msh))
    pool = multiprocessing.Pool(n_cpu)
    save_hdf5_partial = partial(simnibs_results_msh2hdf5_workhorse,
                                fn_hdf5=fn_hdf5,
                                S=S,
                                pos_tms_idx=pos_tms_idx,
                                pos_local_idx=pos_local_idx,
                                subject=subject,
                                mesh_idx=mesh_idx,
                                mode_xdmf="r",
                                verbose=verbose,
                                overwrite=overwrite,
                                mid2roi=mid2roi)

    filenames_chunks = pynibs.compute_chunks(fn_msh, n_cpu)
    pool.map(save_hdf5_partial, filenames_chunks)
    pool.close()
    pool.join()


def msh2hdf5(fn_msh=None, skip_roi=False, include_data=False,
             approach="mri2mesh", subject=None, mesh_idx=None):
    """
    Transforms mesh from .msh to .hdf5 format. Mesh is read from subject object or from fn_msh.

    Parameters
    ----------
    fn_msh : str, optional, default: None
        Filename of .msh file
    skip_roi : bool, optional, default: False
        Skip generating ROI in .hdf5
    include_data : bool, optional, default: False
        Also convert data in .msh file to .hdf5 file
    subject : Subject object, optional, default: None
        Subject object
    mesh_idx : int or list of int, optional, default: None
        Mesh index, the conversion from .msh to .hdf5 is conducted for

    Depreciated parameters
    ----------------------
    approach : str
        Approach the headmodel was created with ("mri2mesh" or "headreco")


    Returns
    -------
    <File> : .hdf5 file
        .hdf5 file with mesh information
    """
    import simnibs

    if approach is not None:
        warnings.warn("'approach' parameter is depreciated.", category=DeprecationWarning)

    if subject is not None:
        mesh_folder = subject.mesh[mesh_idx]["mesh_folder"]

    # load mesh from .msh file and generate mesh object
    if fn_msh is not None:
        msh = load_mesh_msh(fn_msh)
        print("Loading mesh from file: {}".format(fn_msh))
        out_fn = os.path.splitext(fn_msh)[0] + ".hdf5"

    else:
        print("Loading mesh #{} from .msh file: {}".format(mesh_idx, subject.mesh[mesh_idx]['fn_mesh_msh']))
        msh = load_mesh_msh(subject.mesh[mesh_idx]['fn_mesh_msh'])
        out_fn = subject.mesh[mesh_idx]['fn_mesh_hdf5']

    roi_passed = None
    if not skip_roi:
        if subject is None:
            raise ValueError(f"'msh2hdf5(skip_roi=True)': Must provide subject object to write out ROIs."
                             f"Or set 'skip_roi=True'")
        roi = dict()

        if mesh_idx in subject.roi.keys():

            roi[mesh_idx] = dict()

            for roi_idx in subject.roi[mesh_idx].keys():

                print(("\t Initializing ROI #{} {} (type: {})".format(roi_idx,
                                                                      subject.roi[mesh_idx][roi_idx]['info'],
                                                                      subject.roi[mesh_idx][roi_idx]['type'])))
                # surface ROIs
                if subject.roi[mesh_idx][roi_idx]['type'] == 'surface':
                    print("\t\t Generating ROI")
                    # generate RegionOfInterestSurface object instance
                    roi[mesh_idx][roi_idx] = pynibs.RegionOfInterestSurface()
                    # generate the region
                    refine = False
                    try:
                        refine = subject.roi[mesh_idx][roi_idx]['refine']
                    except KeyError:
                        pass
                    roi[mesh_idx][roi_idx].make_GM_WM_surface(
                            gm_surf_fname=subject.roi[mesh_idx][roi_idx]['gm_surf_fname'],
                            wm_surf_fname=subject.roi[mesh_idx][roi_idx]['wm_surf_fname'],
                            midlayer_surf_fname=subject.roi[mesh_idx][roi_idx]['midlayer_surf_fname'],
                            mesh_folder=mesh_folder,
                            delta=subject.roi[mesh_idx][roi_idx]['delta'],
                            x_roi=subject.roi[mesh_idx][roi_idx]['X_ROI'],
                            y_roi=subject.roi[mesh_idx][roi_idx]['Y_ROI'],
                            z_roi=subject.roi[mesh_idx][roi_idx]['Z_ROI'],
                            layer=subject.roi[mesh_idx][roi_idx]['layer'],
                            fn_mask=subject.roi[mesh_idx][roi_idx]['fn_mask'],
                            refine=refine)
                    # find tet_idx for roi in triangle_center of all 3 layers
                    print("\t\t Determining tetrahedra indices of triangle centers of midlayer")
                    roi[mesh_idx][roi_idx].determine_element_idx_in_mesh(msh=msh)

                # volume ROIs
                if subject.roi[mesh_idx][roi_idx]['type'] == 'volume':
                    print("\t\t Generating ROI")
                    # TODO generate ROI here
                    roi[mesh_idx].append(pynibs.RegionOfInterestVolume())
                    # TODO: include make_roi_volume_from_points
                    # generate the region
                    roi[mesh_idx][roi_idx].make_roi_volume_from_msh(msh=msh,
                                                                    volume_type=subject.roi[mesh_idx][roi_idx][
                                                                        'volume_type'],
                                                                    x_roi=subject.roi[mesh_idx][roi_idx]['X_ROI'],
                                                                    y_roi=subject.roi[mesh_idx][roi_idx]['Y_ROI'],
                                                                    z_roi=subject.roi[mesh_idx][roi_idx]['Z_ROI'])

                roi_passed = roi[mesh_idx]

    # save mesh with roi information in .hdf5 format
    write_geo_hdf5(out_fn=out_fn,
                   msh=msh,
                   roi_dict=roi_passed,
                   hdf5_path='/mesh')

    hdf5_geo_fn = None
    if include_data:
        # load mesh in .msh format
        msh_simnibs = read_msh(fn_msh)

        for field in msh_simnibs.field:

            # write node data
            if isinstance(msh_simnibs.field[field], simnibs.mesh_io.NodeData):

                data = msh_simnibs.field[field].value

                with h5py.File(out_fn, "a") as f:
                    f.create_dataset("data/nodes/" + field, data=data, dtype="float64")

            # write tet and tri data
            elif isinstance(msh_simnibs.field[field], simnibs.mesh_io.ElementData):
                data_tris = msh_simnibs.field[field].value[msh_simnibs.elm.elm_type == 2,]
                data_tets = msh_simnibs.field[field].value[msh_simnibs.elm.elm_type == 4,]

                with h5py.File(out_fn, "a") as f:
                    f.create_dataset("data/tets/" + field, data=data_tets)
                    f.create_dataset("data/tris/" + field, data=data_tris)
        hdf5_geo_fn = out_fn

    write_xdmf(hdf5_fn=out_fn,
               hdf5_geo_fn=hdf5_geo_fn,
               overwrite_xdmf=True,
               verbose=False)


def write_arr_to_hdf5(fn_hdf5, arr_name, data, overwrite_arr=True, verbose=False, check_file_exist=False):
    """
    Takes an array and adds it to an hdf5 file

    If data is list of dict, write_dict_to_hdf5() is called for each dict with adapted hdf5-folder name
    Otherwise, data is casted to np.ndarray and dtype of unicode data casted to '|S'.


    Parameters:
    -----------
    fn_hdf5 : str
        Filename of .hdf5 file
    arr_name : str
        Complete path in .hdf5 file with array name
    data : ndarray, list or dict
        Data to write
    overwrite_arr : bool, optional, default: True
        Overwrite existing array
    verbose : bool, optional, default: False
        Print information
    """
    # dictionary
    if isinstance(data, dict):
        write_dict_to_hdf5(fn_hdf5=fn_hdf5,
                           data=data,
                           folder=f"{arr_name}",
                           verbose=verbose,
                           check_file_exist=check_file_exist)
        return

    # list of dictionaries:
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        for idx, lst in enumerate(data):
            write_dict_to_hdf5(fn_hdf5=fn_hdf5,
                               data=lst,
                               folder=f"{arr_name}/{idx}",
                               verbose=verbose,
                               check_file_exist=check_file_exist)
            return
    elif not isinstance(data, np.ndarray):
        data = np.array(data)

    # do some type casting from numpy/pd -> h5py
    # date column from experiment.csv is O
    # plotsetting["view"] is O list of list of different length
    # coil1 and coil2 columns names from experiment.csv is <U8
    # coil_mean column name from experiment.csv is <U12
    if data.dtype == 'O' or data.dtype.kind == 'U':
        data = data.astype('|S')
        if verbose:
            warnings.warn(f"Converting array '{arr_name}'' to string")

    try:
        key = os.path.split(arr_name)[1]
        if key.endswith('fname') or key.startswith('fn'):
            if data.dtype.type == np.bytes_:
                data_l = np.char.decode(data, 'UTF-8').tolist()
                if not isinstance(data_l, list):
                    data_l = [data_l]
                for d in data_l:
                    if d and d != 'None':
                        if isinstance(d, list):
                            for d_sublist in d:
                                if not os.path.exists(d_sublist) and check_file_exist:
                                    warnings.warn(f'Key: {arr_name}: file {d_sublist} does not exist.')
                        else:
                            if not os.path.exists(d) and check_file_exist:
                                warnings.warn(f'Key: {arr_name}: file {d} does not exist.')
    except OSError:
        pass

    with h5py.File(fn_hdf5, 'a') as f:
        # create data_set
        if overwrite_arr:
            try:
                del f[arr_name]
            except KeyError:
                pass
        f.create_dataset(arr_name, data=data)


def write_dict_to_hdf5(fn_hdf5, data, folder, check_file_exist=False, verbose=False):
    """
    Takes dict (from subject.py) and passes its keys to write_arr_to_hdf5()

    fn_hdf5:folder/
                  |--key1
                  |--key2
                  |...

    Parameters
    ----------
    fn_hdf5: str
    data: dict | pynibs.Mesh
    folder: str
    verbose: bool
    check_file_exist : bool

    """
    for key in data.keys():
        write_arr_to_hdf5(fn_hdf5=fn_hdf5,
                          arr_name=f"{folder}/{key}",
                          data=data[key],
                          verbose=verbose,
                          check_file_exist=check_file_exist)


def read_dict_from_hdf5(fn_hdf5, folder):
    """
    Read all arrays from from hdf5 file and return them as dict

    Parameters
    ----------
    fn_hdf5: str
        Filename of .hdf5 file
    folder: str
        Folder inside .hdf5 file to read

    Returns
    --------
    d : dict
        Dictionary from .hdf5 file folder

    """
    d = dict()
    with h5py.File(fn_hdf5, 'r') as f:
        for key in f[folder].keys():

            # read datasets contained hdf5 folder
            if isinstance(f[folder][key], h5py.Dataset):

                # converting strings saved as np.bytes_ in hdf5 to str and converting 'None' to None
                if type(f[folder][key][()]) == np.bytes_:

                    d[key] = str(f[folder][key][()].astype(str))

                    # setting None values correctly
                    if d[key] == 'None':
                        d[key] = None

                # reading ndarray and looking for strings and None
                elif type(f[folder][key][()]) == np.ndarray:
                    d[key] = read_arr_from_hdf5(fn_hdf5, folder + '/' + key)

                else:
                    d[key] = f[folder][key][()]

            # read datasets contained in (multiple) hdf5 sub-folder
            else:
                # d[key] = list()
                # d[key].append(read_dict_from_hdf5(fn_hdf5, f"{folder}/{key}"))
                d[key] = read_dict_from_hdf5(fn_hdf5, f"{folder}/{key}")

    return d


def read_arr_from_hdf5(fn_hdf5, folder):
    """
    Read array and transform to list: strings saved as np.bytes_ to str and 'None' to None

    fn_hdf5: str
        Filename of .hdf5 file
    folder: str
        Folder inside .hdf5 file to read

    Returns
    -------
    l : list
        List containing data from .hdf5 file
    """
    arr_1d = False

    with h5py.File(fn_hdf5, 'r') as f:
        a = f[folder][:]

    if a.size == 0:
        return []

    else:
        if a.ndim == 1:
            arr_1d = True
            a = a[np.newaxis, :]

        df = pd.DataFrame(a.tolist())

        with np.nditer(a, op_flags=['readwrite'], flags=["multi_index"]) as it:
            for x in it:
                if type(x[np.newaxis][0]) == np.bytes_:
                    df.iat[it.multi_index] = str(x.astype(str))

                    try:
                        df.iat[it.multi_index] = float(df.iat[it.multi_index])
                    except ValueError:
                        pass

                    if df.iat[it.multi_index] == 'None':
                        df.iat[it.multi_index] = None

        l = df.values.tolist()

        if arr_1d:
            l = l[0]

        return l


def create_position_path_xdmf(sorted_fn, coil_pos_fn, output_xdmf, stim_intens=None,
                              coil_sorted='/0/0/coil_seq'):
    """
    Creates one .xdmf file that allows paraview plottings of coil position paths.

    Parameters
    ----------
    sorted_fn : str
        .hdf5 filename with position indices, values, intensities from pynibs.sort_opt_coil_positions()
    coil_pos_fn : str
        .hdf5 filename with original set of coil positions. Indices from sorted_fn are mapped to this.
        Either '/matsimnibs' or 'm1' and 'm2' datasets.
    output_xdmf : str
    stim_intens : int, optional
        Intensities are multiplied by this factor

    Returns
    -------
    output_xdmf : <file>

    Other Parameters
    ----------------
    coil_sorted : str
        Path to coil positions in sorted_fn
    """
    # get datasets for nodes used in path, goal value, intensity
    sorted_data = h5py.File(sorted_fn, 'r')[coil_sorted][:]
    nodes_idx, goal_val, intens = sorted_data[:, 0].astype(int), sorted_data[:, 1], sorted_data[:, 2]

    # get direction vectors (for all positions)
    with h5py.File(coil_pos_fn, 'r') as f:
        m1 = f['/m1'][:]
        m2 = f['/m2'][:]

    # get path from node to node
    nodes_path = []
    for i in range(nodes_idx.shape[0] - 1):
        nodes_path.append([nodes_idx[i], nodes_idx[i + 1]])
    nodes_path = np.array(nodes_path).astype(int)

    # write .xdmf file
    with open(output_xdmf, 'w') as f:
        # header
        f.writelines('<?xml version="1.0"?>\n'
                     '<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>\n'
                     '<Xdmf Version="2.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n'
                     '<Domain>\n')

        # one collection grid for everything
        f.writelines('  <Grid CollectionType="Spatial" GridType="Collection" Name="Collection">\n')

        # one grid for the lines
        f.writelines('      <Grid Name="path" GridType="Uniform">\n')
        f.writelines('          <Topology NumberOfElements="1764860" TopologyType="Polyline" Name="Tri" '
                     'NodesPerElement="2">\n')
        f.writelines(f'             <DataItem Format="XML" Dimensions="{nodes_path.shape[0]} 2">\n')

        for node_path in nodes_path:
            f.writelines(f"                 {node_path[0]} {node_path[1]}\n")

        f.writelines('             </DataItem>\n')
        f.writelines('          </Topology>\n')
        f.writelines('			<Geometry GeometryType="XYZ">\n')
        f.writelines(f'				<DataItem Format="HDF" Dimensions="{m1.shape[0]} 3">\n')
        f.writelines(f'				{coil_pos_fn}:/centers\n')
        f.writelines('				</DataItem>\n')
        f.writelines('			</Geometry>\n')

        f.writelines('			<Attribute Name="Stimulation #" AttributeType="Scalar" Center="Cell">\n')
        f.writelines(f'				<DataItem Format="XML" Dimensions="{nodes_path.shape[0]}">\n')
        for i in range(goal_val.shape[0])[:-1]:
            f.writelines(f"                 {i + 1}\n")
        f.writelines('				</DataItem>\n')
        f.writelines('			</Attribute>\n')

        f.writelines('		</Grid>\n')

        # one grid for the spheres
        f.writelines('      <Grid Name="nodes" GridType="Uniform">\n')
        f.writelines('          <Topology NumberOfElements="1764860" TopologyType="Polyvertex" Name="nodes" '
                     'NodesPerElement="2">\n')
        f.writelines(f'             <DataItem Format="XML" Dimensions="{nodes_path.shape[0]} 1">\n')
        for i in nodes_idx:
            f.writelines(f"                 {int(i)}\n")
        f.writelines('             </DataItem>\n\n')
        f.writelines('          </Topology>\n\n')
        f.writelines('			<Geometry GeometryType="XYZ">\n')
        f.writelines(f'				<DataItem Format="HDF" Dimensions="{m1.shape[0]} 3">\n')
        f.writelines(f'				{coil_pos_fn}:/centers\n')
        f.writelines('				</DataItem>\n')
        f.writelines('			</Geometry>\n')

        # intensity dataset for the spheres
        f.writelines('			<Attribute Name="intensity" AttributeType="Scalar" Center="Cell">\n')
        f.writelines(f'				<DataItem Format="XML" Dimensions="{nodes_idx.shape[0]}">\n')
        for i in intens:
            intensity_i = i if stim_intens is None else int(i * stim_intens)
            if intensity_i == 0:
                intensity_i = stim_intens
            f.writelines(f"                 {intensity_i}\n")
        f.writelines('				</DataItem>\n')
        f.writelines('			</Attribute>\n')

        # direction dataset for spheres
        f.writelines('          <Attribute Name="dir_1" AttributeType="Vector" Center="Cell">\n')
        f.writelines(f'              <DataItem Format="XML" Dimensions="{nodes_idx.shape[0]} 3">\n')
        for idx in nodes_idx:
            f.writelines(f"                 {m1[idx][0]} {m1[idx][1]} {m1[idx][2]} \n")
        f.writelines('              </DataItem>\n')
        f.writelines('          </Attribute>\n')
        f.writelines('          \n')
        f.writelines('          <Attribute Name="dir_2" AttributeType="Vector" Center="Cell">\n')
        f.writelines(f'              <DataItem Format="XML" Dimensions="{nodes_idx.shape[0]} 3">\n')
        for idx in nodes_idx:
            f.writelines(f"                 {m2[idx][0]} {m2[idx][1]} {m2[idx][2]} \n")
        f.writelines('              </DataItem>\n')
        f.writelines('          </Attribute>\n')
        f.writelines('\n')
        f.writelines('\n')
        f.writelines('		</Grid>\n')

        # collection grid close
        f.writelines('	</Grid>\n')
        f.writelines('</Domain>\n</Xdmf>')


def create_fibre_geo_hdf5(fn_fibres_hdf5, overwrite=True):
    """
    Reformats geometrical fibre data and adds a /plot subfolder containing geometrical fibre data including connectivity

    Parameters
    ----------
    fn_fibres_hdf5 : str
        Path to fibre.hdf5 file containing the original fibre data
    overwrite : bool
        Overwrites existing /plot subfolder in .hdf5 file
    """

    fibres = []
    # read fibre data from parent folder
    with h5py.File(fn_fibres_hdf5, "a") as f:
        for key in f.keys():
            if key == "plot" and overwrite:
                print("/plot subfolder exists but will be overwritten (overwrite=True)")
                del f[key]
            elif key == "plot" and not overwrite:
                print("/plot subfolder already exists and will not be overwritten (overwrite=False)")
                return None
            else:
                tmp = f[key][:]
                if type(tmp) is np.ndarray and tmp.shape[1] == 3:
                    fibres.append(tmp)

    # concatenate all points
    fibre_points = np.vstack(fibres)

    # create connectivity list
    fibre_con = np.hstack(
            (np.arange(fibre_points.shape[0])[:, np.newaxis], np.arange(fibre_points.shape[0])[:, np.newaxis] + 1))

    # delete connectivities between fibres
    fibre_con = np.delete(fibre_con, np.cumsum([len(fib) for fib in fibres]) - 1, 0)

    # append data to .hdf5
    with h5py.File(fn_fibres_hdf5, "a") as f:
        f.create_dataset(name="plot/fibre_points", data=fibre_points, dtype=float)
        f.create_dataset(name="plot/fibre_con", data=fibre_con, dtype=int)

    # create .xdmf file for plotting
    create_fibre_xdmf(fn_fibre_geo_hdf5=fn_fibres_hdf5, overwrite=overwrite)


def create_fibre_xdmf(fn_fibre_geo_hdf5, fn_fibre_data_hdf5=None, overwrite=True, fibre_points_path="fibre_points",
                      fibre_con_path="fibre_con", fibre_data_path=""):
    """
    Creates .xdmf file to plot fibres in Paraview

    Parameters
    ----------
    fn_fibre_geo_hdf5 : str
        Path to fibre_geo.hdf5 file containing the geometry (in /plot subfolder created with create_fibre_geo_hdf5())
    fn_fibre_data_hdf5 : str (optional) default: None
        Path to fibre_data.hdf5 file containing the data to plot (in parent folder)
    fibre_points_path : str (optional) default: fibre_points
        Path to fibre point array in .hdf5 file
    fibre_con_path : str (optional) default: fibre_con
        Path to fibre connectivity array in .hdf5 file
    fibre_data_path : str (optional) default: ""
        Path to parent data folder in data.hdf5 file (Default: no parent folder)

    Returns
    -------
    <File> : .xdmf file for Paraview
    """
    if fn_fibre_data_hdf5 is None:
        fn_xdmf = os.path.splitext(fn_fibre_geo_hdf5)[0] + ".xdmf"

    else:
        fn_xdmf = os.path.splitext(fn_fibre_data_hdf5)[0] + ".xdmf"

        data_dict = dict()
        with h5py.File(fn_fibre_data_hdf5, "r") as f:
            for key in f.keys():
                data_dict[key] = f[key][:]

    with h5py.File(fn_fibre_geo_hdf5, "r") as f:
        n_con = f[fibre_con_path][:].shape[0]
        n_points = f[fibre_points_path][:].shape[0]

    if os.path.exists(fn_xdmf) and not overwrite:
        print("Aborting .xdmf file already exists (overwrite=False)")
        return

    with open(fn_xdmf, 'w') as xdmf:
        # Header
        xdmf.write(f'<?xml version="1.0"?>\n')
        xdmf.write(f'<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>\n')
        xdmf.write(f'<Xdmf Version="2.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n')

        # Domain and Grid
        xdmf.write(f'<Domain>\n')
        xdmf.write(f'<Grid\n')
        xdmf.write(f'CollectionType="Spatial"\n')
        xdmf.write(f'GridType="Collection"\n')
        xdmf.write(f'Name="Collection">\n')
        xdmf.write(f'<Grid Name="fibres" GridType="Uniform">\n')

        # Topology (connectivity)
        xdmf.write(f'<Topology NumberOfElements="{n_con}" TopologyType="Polyline" NodesPerElement="2" Name="fibres">\n')
        xdmf.write(f'<DataItem Format="HDF" Dimensions="{n_con} 2">\n')
        xdmf.write(f'{fn_fibre_geo_hdf5}:{fibre_con_path}\n')
        xdmf.write(f'</DataItem>\n')
        xdmf.write(f'</Topology>\n')

        # Geometry (points)
        xdmf.write(f'<Geometry GeometryType="XYZ">\n')
        xdmf.write(f'<DataItem Format="HDF" Dimensions="{n_points} 3">\n')
        xdmf.write(f'{fn_fibre_geo_hdf5}:{fibre_points_path}\n')
        xdmf.write(f'</DataItem>\n')
        xdmf.write(f'</Geometry>\n')

        # Data
        if fn_fibre_data_hdf5 is not None:
            for data_name in data_dict.keys():
                data_shape_0 = data_dict[data_name].shape[0]

                if data_dict[data_name].ndim < 2:
                    data_shape_1 = 1
                else:
                    data_shape_1 = data_dict[data_name].shape[1]

                xdmf.write(f'<Attribute Name="{data_name}" AttributeType="Scalar" Center="Cell">\n')
                xdmf.write(f'<DataItem Format="HDF" Dimensions="{data_shape_0} {data_shape_1}">\n')
                xdmf.write(f'{fn_fibre_data_hdf5}:{fibre_data_path}/{data_name}\n')
                xdmf.write(f'</DataItem>\n')
                xdmf.write(f'</Attribute>\n')

        xdmf.write(f'</Grid>\n')
        xdmf.write(f'</Grid>\n')
        xdmf.write(f'</Domain>\n')
        xdmf.write(f'</Xdmf>\n')


def data_superimpose(fn_in_hdf5_data, fn_in_geo_hdf5, fn_out_hdf5_data, data_hdf5_path='/data/tris/',
                     data_substitute=-1, normalize=False):
    """
    Overlaying data stored in .hdf5 files except in regions where data_substitute is found. These points
    are omitted in the analysis and will be replaced by data_substitute instead.

    Parameters
    ----------
    fn_in_hdf5_data: list of str
        Filenames of .hdf5 data files with common geometry
        (e.g. generated by pynibs.data_sub2avg(...))
    fn_in_geo_hdf5: str
        Geometry .hdf5 file, which corresponds to the .hdf5 data files
    fn_out_hdf5_data: str
        Filename of .hdf5 data output file containing the superimposed data
    data_hdf5_path: str
        Path in .hdf5 data file where data is stored (e.g. '/data/tris/')
    data_substitute: float or NaN
        Data substitute with this number for all points in the inflated brain, which do not belong to the given data set
        (Default: -1)
    normalize: boolean or str
        Decide if individual datasets are normalized w.r.t. their maximum values before they are superimposed
        (Default: False)
        - 'global': global normalization w.r.t. maximum value over all datasets and subjects
        - 'dataset': dataset wise normalization w.r.t. maximum of each dataset individually (over subjects)
        - 'subject': subject wise normalization (over datasets)

    Returns
    -------
    <File>: .hdf5 file
        Overlayed data
    """

    n_subjects = len(fn_in_hdf5_data)
    data_dic = [dict() for _ in range(n_subjects)]
    labels = [''] * n_subjects
    percentile = [99]

    # load .hdf5 data files and save them in dictionaries
    for i, filename in enumerate(fn_in_hdf5_data):
        with h5py.File(filename, 'r') as f:
            labels[i] = list(f[data_hdf5_path].keys())
            for j, label in enumerate(labels[i]):
                data_dic[i][label] = f[data_hdf5_path + label][:]
                # normalize data if desired

    # find matching labels in all datasets
    cmd = " ".join(['set(labels[' + str(int(i)) + ']) &' for i in range(n_subjects)])[0:-2]
    data_labels = list(eval(cmd))

    # reform data
    data = [np.zeros((data_dic[0][data_labels[i]].shape[0], n_subjects)) for i in range(len(data_labels))]
    for i, label in enumerate(data_labels):
        for j in range(n_subjects):
            data[i][:, j] = data_dic[j][label].flatten()

    del data_dic

    # Normalize each dataset over subjects to 1
    if normalize == 'dataset':
        for i in range(len(data_labels)):
            mask = np.all(data[i] != data_substitute, axis=1)
            data[i][mask, :] = data[i][mask, :] / np.tile(np.percentile(data[i][mask, :],
                                                                        percentile)[0],
                                                          (np.sum(mask), 1))

            # trim values > 1 from percentile to 1
            mask_idx = np.where(mask)[0]
            data[i][mask_idx[data[i][mask, :] > 1], :] = 1
            # np.max(data[i][mask, :], axis=0)

    elif normalize == 'subject':
        # subject - wise
        for i_subj in range(n_subjects):
            sub_data = np.array(())
            mask = np.array(())
            max_val = []

            # dataset - wise
            for i_data in range(len(data_labels)):
                mask = np.append(mask, np.all(data[i_data] != data_substitute, axis=1))
                sub_data = np.append(sub_data, data[i_data][:, i_subj])
                max_val.append(np.percentile(sub_data[mask == 1.], percentile)[0])

            # max(max) over all datasets
            max_val = np.max(max_val)
            for i_data in range(len(data_labels)):
                mask = np.all(data[i_data] != data_substitute, axis=1)
                data[i_data][mask, i_subj] /= max_val

                # trim values > 1 from percentile to 1
                mask_idx = np.where(mask)[0]
                data[i_data][mask_idx[data[i_data][mask, i_subj] > 1], i_subj] = 1

    # Find max of all datasets of all subject and normalize w.r.t. this value
    elif normalize == 'global':
        data_max = []
        # mag, norm, tan
        for i in range(len(data_labels)):
            mask = np.all(data[i] != data_substitute, axis=1)
            # take max(subject-wise 99.9percentile)
            data_max.append(np.max(np.percentile(data[i][mask, :], percentile, axis=0)[0]))

        # find maximum of mag, norm, tan
        data_max = np.max(data_max)

        # normalize
        for i in range(len(data_labels)):
            mask = np.all(data[i] != data_substitute, axis=1)
            # data[i][mask, :] = data[i][mask, :]/np.tile(data_max, (np.sum(mask), 1))
            data[i][mask, :] = data[i][mask, :] / data_max

            # trim values > 1 from percentile to 1
            mask_idx = np.where(mask)[0]
            data[i][mask_idx[data[i][mask, :] > 1], :] = 1

    # average data in regions where values are defined in every dataset
    data_mean = [np.ones(data[i].shape[0]) * data_substitute for i in range(len(data_labels))]

    for i in range(len(data_labels)):
        mask = np.all(data[i] != data_substitute, axis=1)
        data_mean[i][mask] = np.mean(data[i][mask, :], axis=1)

    # create results directory
    if not os.path.exists(os.path.split(fn_out_hdf5_data)[0]):
        os.makedirs(os.path.split(fn_out_hdf5_data)[0])

    # copy .hdf5 geometry file to results folder of .hdf5 data file
    os.system('cp ' + fn_in_geo_hdf5 + ' ' + os.path.split(fn_out_hdf5_data)[0])

    # rename .hdf5 geo file to match with .hdf5 data file
    fn_in_geo_hdf5_new = os.path.splitext(fn_out_hdf5_data)[0] + '_geo.hdf5'
    os.system('mv ' + os.path.join(os.path.split(fn_out_hdf5_data)[0], os.path.split(fn_in_geo_hdf5)[1]) + ' ' +
              fn_in_geo_hdf5_new)

    # write data to .hdf5 data file
    write_data_hdf5_surf(data=data_mean,
                         data_names=data_labels,
                         data_hdf_fn_out=fn_out_hdf5_data,
                         geo_hdf_fn=fn_in_geo_hdf5_new,
                         replace=True)
