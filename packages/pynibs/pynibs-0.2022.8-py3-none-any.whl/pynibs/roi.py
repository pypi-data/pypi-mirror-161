import numpy as np
import platform
import scipy
import os
import time
import h5py
import nibabel as nib
import trimesh
import tqdm
from itertools import product
import pynibs


def get_mask(areas, fn_annot, fn_inflated_fs, fn_out):
    """
    Determine freesurfer average mask .overlay file, which is needed to generate subject specific ROIs.

    Parameters
    ----------
    areas : list of str
        Brodmann areas (e.g. ['Brodmann.6', 'Brodmann.4', 'Brodmann.3', 'Brodmann.1'])
    fn_annot : str
        Annotation file of freesurfer (e.g. 'FREESURFER_DIR/fsaverage/label/lh.PALS_B12_Brodmann.annot')
    fn_inflated_fs : str
        Inflated surface of freesurfer average (e.g. 'FREESURFER_DIR/fsaverage/surf/lh.inflated')
    fn_out : str
        Filename of .overlay file of freesurfer mask

    Returns
    -------
    <File> : .overlay file
        fn_out.overlay file of freesurfer mask
    """
    # read annotation file
    vertices, colortable, label = nib.freesurfer.io.read_annot(fn_annot)

    # convert label from numpy bytes str to str
    label = [str(lab.astype(str)) for lab in label]

    idx_areas = [i_l for i_a, a in enumerate(areas) for i_l, l in enumerate(label) if a == l]
    ourvertices = np.zeros(len(vertices)).astype(bool)
    idx_label = colortable[idx_areas, 4]

    ourvertices[idx_label] = True

    # ourvertices = vertices(ourvertices) + 1; % matlab
    # indexing
    # 
    # overlay = zeros(size(vertices));
    # overlay(ourvertices) = 1;


def elem_workhorse(chunk, points_out, P1_all, P2_all, P3_all, P4_all, N_points_total, N_CPU):
    """
    Parameters
    ----------
    chunk: np.ndarray
        Indices of points the CPU thread is computing the element indices for
    points_out: np.ndarray of float [N_points x 3]
        Coordinates of points, the tetrahedra indices are computed for
    P1_all : np.ndarray of float [N_tet x 3]
        Coordinates of first point of tetrahedra
    P2_all : np.ndarray of float [N_tet x 3]
        Coordinates of second point of tetrahedra
    P3_all : np.ndarray of float [N_tet x 3]
        Coordinates of third point of tetrahedra
    P4_all : np.ndarray of float [N_tet x 3]
        Coordinates of fourth point of tetrahedra
    N_points_total : int
        Total number of points
    N_CPU : int
        Number of CPU cores to use

    Returns
    -------
    tet_idx_local: np.ndarray of int [N_points]
    """

    tet_idx_local = np.zeros([chunk.shape[0]])
    i_local = 0

    for i in chunk:
        start = time.time()

        vtest1 = pynibs.mesh.calc_tetrahedra_volume_cross(np.tile(points_out[i, :], (P1_all.shape[0], 1)),
                                                          P2_all,
                                                          P3_all,
                                                          P4_all)
        tet_idx_bool_1 = (vtest1 >= 0)
        tet_idx_1 = np.nonzero(tet_idx_bool_1)[0]

        vtest2 = pynibs.mesh.calc_tetrahedra_volume_cross(P1_all[tet_idx_1, :],
                                                          np.tile(points_out[i, :], (tet_idx_1.shape[0], 1)),
                                                          P3_all[tet_idx_1, :],
                                                          P4_all[tet_idx_1, :])
        tet_idx_bool_2 = (vtest2 >= 0)
        tet_idx_2 = tet_idx_1[np.nonzero(tet_idx_bool_2)[0]]

        vtest3 = pynibs.mesh.calc_tetrahedra_volume_cross(P1_all[tet_idx_2, :],
                                                          P2_all[tet_idx_2, :],
                                                          np.tile(points_out[i, :], (tet_idx_2.shape[0], 1)),
                                                          P4_all[tet_idx_2, :])
        tet_idx_bool_3 = (vtest3 >= 0)
        tet_idx_3 = tet_idx_2[np.nonzero(tet_idx_bool_3)[0]]

        vtest4 = pynibs.mesh.calc_tetrahedra_volume_cross(P1_all[tet_idx_3, :],
                                                          P2_all[tet_idx_3, :],
                                                          P3_all[tet_idx_3, :],
                                                          np.tile(points_out[i, :], (tet_idx_3.shape[0], 1)))
        tet_idx_bool_4 = (vtest4 >= 0)

        tet_idx_local[i_local] = tet_idx_3[
            np.nonzero(tet_idx_bool_4)[0]].astype(int)
        i_local = i_local + 1

        stop = time.time()
        print('Determining element index of point: {:s}/{:d} ({:d}/{:d}) \t [{:1.2f} sec] \t {:1.2f}%' \
              .format(str(i).zfill(int(np.floor(np.log10(N_points_total)) + 1)),
                      N_points_total,
                      i_local,
                      len(chunk),
                      stop - start,
                      float(i_local) / (N_points_total / N_CPU) * 100.0))
    return tet_idx_local


def load_roi_surface_obj_from_hdf5(fname):
    """
    Loading and initializing RegionOfInterestSurface object from .hdf5 mesh file.

    Parameters
    ----------
    fname : str
        Filename (incl. path) of .hdf5 mesh file, e.g. from subject.fn_mesh_hdf5

    Returns
    -------
    obj : object instance or list of object instances [n_roi]
        RegionOfInterestSurface object class instance
    """

    with h5py.File(fname, 'r') as f:
        if "roi_surface" not in f.keys():
            print(f"No rois found in {fname}.")
            return None
        roi_label = list(f["roi_surface"].keys())
        roi_label = [str(r) for r in roi_label]
        roi = dict()

        # loop over all available roi
        for roi_idx in roi_label:
            # initialize roi
            roi[roi_idx] = RegionOfInterestSurface()
            roi[roi_idx].mesh_folder = os.path.split(fname)[0]

            # read all labels
            data_label = list(f[f"roi_surface/{roi_idx}"].keys())
            data_label = [str(r) for r in data_label]

            # read data from .hdf5 file and pass it to object
            for j in range(len(data_label)):
                if type(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]) == np.ndarray and \
                        "S" in str(f[f'roi_surface/{roi_idx}/{data_label[j]}'].dtype) and \
                        len(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]) > 1:
                    expr = "roi[roi_idx]." + data_label[
                        j] + "= list(f[f'roi_surface/{roi_idx}/{data_label[j]}'][:].astype(str))"
                elif type(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]) == np.bytes_ and \
                        "S" in str(f[f'roi_surface/{roi_idx}/{data_label[j]}'].dtype):
                    expr = "roi[roi_idx]." + data_label[
                        j] + "= str(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()].astype(str))"

                # bytes string
                elif type(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]) == bytes:
                    expr = "roi[roi_idx]." + data_label[
                        j] + "= f[f'roi_surface/{roi_idx}/{data_label[j]}'][()].decode('utf-8')"

                # list of bytes string
                elif type(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]) == list and \
                        len(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]) > 1:
                    expr = "roi[roi_idx]." + data_label[
                        j] + "= list(f[f'roi_surface/{roi_idx}/{data_label[j]}'][:].astype(str))"

                elif type(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]) == np.float64 or \
                        type(f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]) == np.int64:
                    expr = "roi[roi_idx]." + data_label[j] + "= f[f'roi_surface/{roi_idx}/{data_label[j]}'][()]"
                else:
                    expr = "roi[roi_idx]." + data_label[j] + "= np.array(f[f'roi_surface/{roi_idx}/{data_label[j]}'])"
                exec(expr)

            for key in roi[roi_idx].__dict__:

                if type(getattr(roi[roi_idx], key)) == str:
                    if getattr(roi[roi_idx], key) == "None":
                        setattr(roi[roi_idx], key, None)

                if type(getattr(roi[roi_idx], key)) == list:
                    lst_tmp = []
                    for i_a, a in enumerate(getattr(roi[roi_idx], key)):
                        if a == "None":
                            lst_tmp.append(None)
                        else:
                            lst_tmp.append(a)
                        setattr(roi[roi_idx], key, lst_tmp)

            roi[roi_idx].n_tris = roi[roi_idx].node_number_list.shape[0]
            roi[roi_idx].n_nodes = roi[roi_idx].node_coord_low.shape[0]
            roi[roi_idx].n_tets = roi[roi_idx].tet_idx_node_coord_mid.shape[0]

    return roi


def determine_element_idx_in_mesh(fname, msh, points, compute_baricentric=False):
    """
    Finds the tetrahedron that contains each of the described points using a stochastic walk algorithm.

    Parameters
    ----------
    fname : str or None
        Filename of saved .txt file containing the element indices (no data is saved when fname=None or fname='')
    points : np.ndarray [N x 3] or list of ndarray
        List of points to be queried
    compute_baricentric : bool
        Wether or not to compute baricentric coordinates of the points

    Returns
    -------
    th_with_points : np.ndarray
        List with the tetrahedron that contains each point. If the point is outside
        the mesh, the value will be -1
    baricentric : np.ndarray [n x 4](if compute_baricentric == True)
        Baricentric coordinates of point. If the point is outside, a list of zeros

    Notes
    -----
    .. [1] Devillers, Olivier, Sylvain Pion, and Monique Teillaud. "Walking in a
       triangulation." International Journal of Foundations of Computer Science 13.02
       (2002): 181-199.
    """

    if platform.system() == 'Linux':
        import simnibs

        if int(simnibs.__version__[0]) < 4:
            import simnibs.cython_code.cython_msh as cython_msh
            # import pynibs.pckg.simnibs.cython_code.cython_msh as cython_msh
        else:
            from simnibs import cython_msh

    else:
        raise OSError('This function works currently only under Linux!')

    if type(points) is not list:
        points = [points]

    n_pointsets = len(points)

    # determine size of input data
    n_points = [points[i].shape[0] for i in range(len(points))]
    n_points_out_max = np.max(n_points)

    tet_idx = np.ones((n_points_out_max, n_pointsets))
    baricentric = [[] for _ in range(n_pointsets)]

    th_indices = np.arange(msh.tetrahedra.shape[0])
    th_nodes = msh.points[msh.tetrahedra]

    for i in range(n_pointsets):
        # Reduce the number of elements
        points_max = np.max(points[i], axis=0)
        points_min = np.min(points[i], axis=0)
        th_max = np.max(th_nodes, axis=1)
        th_min = np.min(th_nodes, axis=1)
        slack = (points_max - points_min) * .05
        th_in_box = np.where(np.all((th_min <= points_max + slack) * (th_max >= points_min - slack), axis=1))[0]
        th_indices = th_indices[th_in_box]
        th_nodes = th_nodes[th_in_box]

        # Calculate a few things we will use later
        faces, th_faces, adjacency_list = msh.get_faces(th_indices)

        # Find initial positions
        th_baricenters = np.average(th_nodes, axis=1)
        kdtree = scipy.spatial.cKDTree(th_baricenters)

        # Starting position for walking algorithm: the closest baricenter
        _, closest_th = kdtree.query(points[i])
        pts = np.array(points[i], dtype=np.float)
        th_nodes = np.array(th_nodes, dtype=np.float)
        closest_th = np.array(closest_th, dtype=np.int)
        th_faces = np.array(th_faces, dtype=np.int)
        adjacency_list = np.array(adjacency_list, dtype=np.int)
        th_with_points = cython_msh.find_tetrahedron_with_points(pts, th_nodes, closest_th, th_faces, adjacency_list)

        # calculate baricentric coordinates
        inside = th_with_points != -1
        if compute_baricentric:
            M = np.transpose(th_nodes[th_with_points[inside], :3, :3] -
                             th_nodes[th_with_points[inside], 3, None, :], (0, 2, 1))
            baricentric[i] = np.zeros((len(points[i]), 4), dtype=float)
            baricentric[i][inside, :3] = np.linalg.solve(M, points[i][inside] - th_nodes[th_with_points[inside], 3, :])
            baricentric[i][inside, 3] = 1 - np.sum(baricentric[i][inside], axis=1)

        # Return indices
        th_with_points[inside] = th_indices[th_with_points[inside]]
        tet_idx[:, i] = th_with_points.astype(int)

    if not (fname is None or fname == ''):
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
        np.savetxt(fname, tet_idx, '%d')
        print('Saved element indices of points_out in {}'.format(fname))

    if compute_baricentric:
        return tet_idx, baricentric
    else:
        return tet_idx


def make_GM_WM_surface(gm_surf_fname, wm_surf_fname, mesh_folder, midlayer_surf_fname=None, delta=0.5,
                       x_roi=None, y_roi=None, z_roi=None,
                       layer=1,
                       fn_mask=None,
                       refine=False):
    """
    Generating a surface between WM and GM in a distance of delta 0...1 for ROI,
    given by freesurfer mask or coordinates.

    Parameters
    ----------
    gm_surf_fname : str or list of str
        Filename(s) of GM surface generated by freesurfer (lh and/or rh)
        (e.g. in mri2msh: fs_ID/surf/lh.pial)
    wm_surf_fname : str or list of str
        Filename(s) of WM surface generated by freesurfer (lh and/or rh)
        (e.g. in mri2msh: fs_ID/surf/lh.white)
    mesh_folder : str
        Path of mesh (parent directory)
    midlayer_surf_fname : str or list of str
        filename(s) of midlayer surface generated by headreco (lh and/or rh)
        (e.g. in headreco: fs_ID/surf/lh.central) (after conversion)
    [defunct] m2m_mat_fname : str
        Filename of mri2msh transformation matrix
        (e.g. in mri2msh: m2m_ProbandID/MNI2conform_6DOF.mat)
    delta : float
        Distance parameter where surface is generated 0...1 (default: 0.5)
        - 0 -> WM surface
        - 1 -> GM surface
    x_roi : list of float or None
        Region of interest [Xmin, Xmax], whole X range if empty [0,0] or None
        (left - right)
    y_roi : list of float or None
        Region of interest [Ymin, Ymax], whole Y range if empty [0,0] or None
        (anterior - posterior)
    z_roi : list of float or None
        Region of interest [Zmin, Zmax], whole Z range if empty [0,0] or None
        (inferior - superior)
    layer : int
        Define the number of layers:

        - 1: one layer
        - 3: additionally upper and lower layers are generated around the central midlayer
    fn_mask: string or None
        Filename for freesurfer mask. If given, this is used instead of *_ROIs
    refine : bool, optional, default: False
        Refine ROI by splitting elements

    Returns
    -------
    if layer == 3:
        surface_points_upper : np.ndarray of float
            (N_points, 3) Coordinates (x, y, z) of surface + epsilon (in GM surface direction)
        surface_points_middle : np.ndarray of float
            (N_points, 3) Coordinates (x, y, z) of surface
        surface_points_lower : np.ndarray of float
            (N_points, 3) Coordinates (x, y, z) of surface - epsilon (in WM surface direction)
        connectivity : np.ndarray of int
             (N_tri x 3) Connectivity of triangles (indexation starts at 0!)
    else:
        surface_points_middle : np.ndarray of float
            (N_points, 3) Coordinates (x, y, z) of surface
        connectivity : np.ndarray of int
             (N_tri x 3) Connectivity of triangles (indexation starts at 0!)

    Example
    -------
    make_GM_WM_surface(self, gm_surf_fname, wm_surf_fname, delta, X_ROI, Y_ROI, Z_ROI)
    make_GM_WM_surface(self, gm_surf_fname, wm_surf_fname, delta, mask_fn, layer=3)
    """

    if type(gm_surf_fname) is not list:
        gm_surf_fname = [gm_surf_fname]

    if type(wm_surf_fname) is not list:
        wm_surf_fname = [wm_surf_fname]

    if type(midlayer_surf_fname) is not list:
        midlayer_surf_fname = [midlayer_surf_fname]

    if len(gm_surf_fname) != len(wm_surf_fname):
        raise Exception('provide equal number of GM and WM surfaces!')

    # load surface data
    points_gm = [None for _ in range(len(gm_surf_fname))]
    points_wm = [None for _ in range(len(wm_surf_fname))]
    points_mid = [None for _ in range(len(midlayer_surf_fname))]
    con_gm = [None for _ in range(len(gm_surf_fname))]
    con_wm = [None for _ in range(len(wm_surf_fname))]
    con_mid = [None for _ in range(len(midlayer_surf_fname))]

    max_idx_gm = 0
    max_idx_wm = 0
    max_idx_mid = 0

    for i in range(len(gm_surf_fname)):
        if gm_surf_fname[i] is not None:
            points_gm[i], con_gm[i] = nib.freesurfer.read_geometry(os.path.join(mesh_folder, gm_surf_fname[i]))
            con_gm[i] = con_gm[i] + max_idx_gm
            max_idx_gm = max_idx_gm + points_gm[i].shape[0]  # np.max(con_gm[i]) + 2

        if wm_surf_fname[i] is not None:
            points_wm[i], con_wm[i] = nib.freesurfer.read_geometry(os.path.join(mesh_folder, wm_surf_fname[i]))
            con_wm[i] = con_wm[i] + max_idx_wm
            max_idx_wm = max_idx_wm + points_wm[i].shape[0]  # np.max(con_wm[i]) + 2

        if midlayer_surf_fname[i] is not None:
            points_mid[i], con_mid[i] = nib.freesurfer.read_geometry(
                    os.path.join(mesh_folder, midlayer_surf_fname[i]))
            con_mid[i] = con_mid[i] + max_idx_mid
            max_idx_mid = max_idx_mid + points_mid[i].shape[0]  # np.max(con_wm[i]) + 2

    points_gm = np.vstack(points_gm)
    points_wm = np.vstack(points_wm)
    points_mid = np.vstack(points_mid)
    con_gm = np.vstack(con_gm)
    con_wm = np.vstack(con_wm)
    con_mid = np.vstack(con_mid)

    # Determine 3 layer midlayer if GM and WM surfaces are present otherwise use provided midlayer data
    if gm_surf_fname[0] is not None and wm_surf_fname[0] is not None:
        # determine vector pointing from wm surface to gm surface
        wm_gm_vector = points_gm - points_wm

        eps_0 = 0.025
        eps, surface_points_upper, surface_points_lower = (False,) * 3
        surface_points_upper = False
        if layer == 3:
            # set epsilon range for upper and lower surface
            if delta < eps_0:
                eps = delta / 2
            elif delta > (1 - eps_0):
                eps = (1 - delta) / 2
            else:
                eps = eps_0

        # determine wm-gm surfaces
        surface_points_middle = points_wm + wm_gm_vector * delta  # type: np.ndarray
        if layer == 3:
            surface_points_upper = surface_points_middle + wm_gm_vector * eps
            surface_points_lower = surface_points_middle - wm_gm_vector * eps

        con = con_gm

    elif midlayer_surf_fname[0] is not None:
        layer = 1

        surface_points_upper = None
        surface_points_lower = None
        surface_points_middle = points_mid

        con = con_mid

    else:
        raise IOError("Please provide GM and WM surfaces or midlayer "
                      "surface directly for midlayer calculation...")

    # crop region if desired
    x_roi_wb, y_roi_wb, z_roi_wb = (False,) * 3
    if fn_mask is None:
        # crop to region of interest
        if x_roi is None or x_roi == [0, 0]:
            x_roi = [-np.inf, np.inf]
            x_roi_wb = True
        if y_roi is None or y_roi == [0, 0]:
            y_roi = [-np.inf, np.inf]
            y_roi_wb = True
        if z_roi is None or z_roi == [0, 0]:
            z_roi = [-np.inf, np.inf]
            z_roi_wb = True

        roi_mask_bool = (surface_points_middle[:, 0] > min(x_roi)) & (surface_points_middle[:, 0] < max(x_roi)) & \
                        (surface_points_middle[:, 1] > min(y_roi)) & (surface_points_middle[:, 1] < max(y_roi)) & \
                        (surface_points_middle[:, 2] > min(z_roi)) & (surface_points_middle[:, 2] < max(z_roi))
        roi_mask_idx = np.where(roi_mask_bool)

    else:
        # read mask from freesurfer mask file
        mask = nib.freesurfer.mghformat.MGHImage.from_filename(os.path.join(mesh_folder, fn_mask)).dataobj[:]
        roi_mask_idx = np.where(mask > 0.5)

    # redefine connectivity matrix for cropped points (reindexing)
    # get row index where all points are lying inside ROI
    if not (x_roi_wb and y_roi_wb and z_roi_wb):
        con_row_idx = [i for i in range(con.shape[0]) if len(np.intersect1d(con[i,], roi_mask_idx)) == 3]
        # crop connectivity matrix to ROI
        con_cropped = con[con_row_idx,]
    else:
        con_cropped = con

    # evaluate new indices of cropped connectivity matrix
    point_idx_before, point_idx_after = np.unique(con_cropped, return_inverse=True)
    con_cropped_reform = np.reshape(point_idx_after, (con_cropped.shape[0], con_cropped.shape[1]))

    # crop points to ROI
    surface_points_middle = surface_points_middle[point_idx_before,]
    if layer == 3:
        surface_points_upper = surface_points_upper[point_idx_before,]
        surface_points_lower = surface_points_lower[point_idx_before,]

    # refine
    if refine:
        if not os.path.exists(os.path.join(mesh_folder, "roi", "tmp")):
            os.makedirs(os.path.join(mesh_folder, "roi", "tmp"))

        mesh = trimesh.Trimesh(vertices=surface_points_middle,
                               faces=con_cropped_reform)
        mesh.export(os.path.join(mesh_folder, "roi", "tmp", "roi.stl"))

        pynibs.mesh.refine_surface(fn_surf=os.path.join(mesh_folder, "roi", "tmp", "roi.stl"),
                                   fn_surf_refined=os.path.join(mesh_folder, "roi", "tmp", "roi_refined.stl"),
                                   center=[0, 0, 0],
                                   radius=np.inf,
                                   verbose=True,
                                   repair=False,
                                   remesh=False)

        roi = trimesh.load(os.path.join(mesh_folder, "roi", "tmp", "roi_refined.stl"))
        con_cropped_reform = roi.faces
        surface_points_middle = roi.vertices

        if layer == 3:
            roi = []

            for p in [surface_points_upper, surface_points_lower]:
                mesh = trimesh.Trimesh(vertices=p,
                                       faces=con_cropped_reform)
                mesh.export(os.path.join(mesh_folder, "roi", "tmp", "roi.stl"))

                pynibs.mesh.refine_surface(fn_surf=os.path.join(mesh_folder, "roi", "tmp", "roi.stl"),
                                           fn_surf_refined=os.path.join(mesh_folder, "roi", "tmp", "roi_refined.stl"),
                                           center=[0, 0, 0],
                                           radius=np.inf,
                                           verbose=True,
                                           repair=False)

                roi.append(trimesh.load(os.path.join(mesh_folder, "roi", "tmp", "roi_refined.stl")))

            surface_points_upper = roi[0].vertices
            surface_points_lower = roi[1].vertices

    if layer == 3:
        return surface_points_upper, surface_points_middle, surface_points_lower, con_cropped_reform
    else:
        return surface_points_middle, con_cropped_reform


class RegionOfInterestSurface:
    """
    Region of interest (surface)

    Attributes
    ----------
    node_coord_up : np.ndarray [N_points x 3]
        Coordinates (x,y,z) of upper surface nodes
    node_coord_mid : np.ndarray [N_points x 3]
        Coordinates (x,y,z) of middle surface nodes
    node_coord_low : np.ndarray [N_points x 3]
        Coordinates (x,y,z) of lower surface nodes
    node_number_list : np.ndarray [N_points x 3]
        Connectivity matrix of triangles
    delta : float
        Distance parameter between WM and GM (0 -> WM, 1 -> GM)
    tet_idx_tri_center_up : np.ndarray [N_points]
        Tetrahedra indices of TetrahedraLinear object instance where the center points of the triangles of the
        upper surface are lying in
    tet_idx_tri_center_mid : np.ndarray [N_points]
        Tetrahedra indices of TetrahedraLinear object instance where the center points of the triangles of the
        middle surface are lying in
    tet_idx_tri_center_low : np.ndarray [N_points]
        Tetrahedra indices of TetrahedraLinear object instance where the center points of the triangles of the
        lower surface are lying in
    tet_idx_node_coord_mid : np.ndarray [N_tri]
        Tetrahedra indices of TetrahedraLinear object instance where the nodes of the middle surface are lying in
    tri_center_coord_up : np.ndarray [N_tri x 3]
        Coordinates of roi triangle center of upper surface
    tri_center_coord_mid : np.ndarray [N_tri x 3]
        Coordinates of roi triangle center of middle surface
    tri_center_coord_low : np.ndarray [N_tri x 3]
        Coordinates of roi triangle center of lower surface
    fn_mask : string
        Filename for surface mask in subject space. .mgh file or freesurfer surface file.
    fn_mask_avg : string
        Filename for .mgh mask in fsaverage space. Absolute path or relative to mesh folder.
    fn_mask_nii : string
        Filename for .nii or .nii.gz mask. Absolute path or relative to mesh folder.
    X_ROI : list of float
        Region of interest [Xmin, Xmax], whole X range if empty [0,0] or None
        (left - right)
    Y_ROI : list of float
        Region of interest [Ymin, Ymax], whole Y range if empty [0,0] or None
        (anterior - posterior)
    Z_ROI : list of float
        Region of interest [Zmin, Zmax], whole Z range if empty [0,0] or None
        (inferior - superior)
    template : str
        'MNI', 'fsaverage', 'subject'
    center : list of float
        Center coordinates for spherical ROI in self.template space
    radius : float
        Radius in [mm] for spherical ROI
    gm_surf_fname : str or list of str
        Filename(s) of GM surface generated by freesurfer (lh and/or rh)
        (e.g. in mri2msh: .../fs_ID/surf/lh.pial)
    wm_surf_fname : str or list of str
        Filename(s) of WM surface generated by freesurfer (lh and/or rh)
        (e.g. in mri2msh: .../fs_ID/surf/lh.white)
    layer : int
        Define the number of layers:
        - 1: one layer
        - 3: additionally upper and lower layers are generated around the central midlayer

    Notes
    -----
    Initialization:
    ::
        roi = RegionOfInterestSurface()
    """

    def __init__(self):
        """ Initialize RegionOfInterestSurface class instance """

        self.node_coord_up = []
        self.node_coord_mid = []
        self.node_coord_low = []

        self.node_number_list = []
        self.delta = []

        self.tet_idx_tri_center_up = []
        self.tet_idx_tri_center_mid = []
        self.tet_idx_tri_center_low = []

        self.tet_idx_node_coord_mid = []

        self.tri_center_coord_up = []
        self.tri_center_coord_mid = []
        self.tri_center_coord_low = []

        self.template = None
        self.fn_mask = []
        self.fn_mask_avg = None
        self.fn_mask_nii = None

        self.X_ROI = []
        self.Y_ROI = []
        self.Z_ROI = []

        self.center = None
        self.radius = None

        self.gm_surf_fname = []
        self.wm_surf_fname = []
        self.midlayer_surf_fname = []
        self.layer = []
        self.mesh_folder = []
        self.refine = []

        self.n_tris = -1
        self.n_nodes = -1
        self.n_tets = -1

    def project_on_midlayer(self, target, verbose=False):
        """
        Project a coordinate on the nearest midlayer node

        Parameters
        ----------
        target : np.ndarray
            Coordinate to project as  (3,) array
        verbose : bool
            Print some verbosity information. Default: False

        Returns
        -------
        target_proj : np.ndarray
            Node coordinate of nearest midlayer node.
        """
        # find midlayer node that is nearest to the target
        target_node_coord_mid = np.where(np.linalg.norm(self.node_coord_mid - target, axis=1) == np.min(
                np.linalg.norm(self.node_coord_mid - target, axis=1)))[0][0]

        # get coordinates of that node
        target_proj = self.node_coord_mid[target_node_coord_mid]

        if verbose:
            print(f"Projected {target} to {target_proj} (Dist: {np.linalg.norm(target - target_proj):2.2f}mm)")

        return target_proj

    def make_GM_WM_surface(self, gm_surf_fname=None, wm_surf_fname=None, midlayer_surf_fname=None, mesh_folder=None,
                           delta=0.5,
                           x_roi=None, y_roi=None, z_roi=None,
                           layer=1,
                           fn_mask=None, refine=False):
        """
        Generating a surface between WM and GM in a distance of delta 0...1 for ROI,
        given by Freesurfer mask or coordinates.

        Parameters
        ----------
        gm_surf_fname : str or list of str
            Filename(s) of GM FreeSurfer surface(s)  (lh and/or rh).
            Either relative to mesh_folder (fs_ID/surf/lh.pial) or absolute (/full/path/to/lh.pial)
        wm_surf_fname : str or list of str
            Filename(s) of WM FreeSurfer surface(s) (lh and/or rh)
            Either relative to mesh_folder (fs_ID/surf/lh.white) or absolute (/full/path/to/lh.white)
        midlayer_surf_fname : str or list of str
            Filename(s) of midlayer surface (lh and/or rh)
            Either relative to mesh_folder (fs_ID/surf/lh.central) or absolute (/full/path/to/lh.central)
        mesh_folder : str
            Root folder of mesh, Needed if paths above are given relative, or refine=True
        [defunct] m2m_mat_fname : str
            Filename of mri2msh transformation matrix
            (e.g. in mri2msh: .../m2m_ProbandID/MNI2conform_6DOF.mat)
        delta : float
            Distance parameter where surface is generated 0...1 (default: 0.5)
            - 0 -> WM surface
            - 1 -> GM surface
        x_roi : list of float
            Region of interest [Xmin, Xmax], whole X range if empty [0,0] or None
            (left - right)
        y_roi : list of float
            Region of interest [Ymin, Ymax], whole Y range if empty [0,0] or None
            (anterior - posterior)
        z_roi : list of float
            Region of interest [Zmin, Zmax], whole Z range if empty [0,0] or None
            (inferior - superior)
        layer : int
            Define the number of layers:
            - 1: one layer
            - 3: additionally upper and lower layers are generated around the central midlayer
        fn_mask : str
            Filename for FreeSurfer .mgh mask.
        refine : bool, optional, default: False
            Refine ROI by splitting elements

        Returns
        -------
        node_coord_up : np.ndarray of float [N_roi_points x 3]
            Node coordinates (x, y, z) of upper epsilon layer of ROI surface
        node_coord_mid : np.ndarray of float [N_roi_points x 3]
            Node coordinates (x, y, z) of ROI surface
        node_coord_low : np.ndarray of float [N_roi_points x 3]
            Node coordinates (x, y, z) of lower epsilon layer of ROI surface
        node_number_list : np.ndarray of int [N_roi_tri x 3]
            Connectivity matrix of intermediate surface layer triangles
        delta : float
            Distance parameter where surface is generated 0...1 (default: 0.5)
            - 0 -> WM surface
            - 1 -> GM surface
        tri_center_coord_up : np.ndarray of float [N_roi_tri x 3]
            Coordinates (x, y, z) of triangle center of upper epsilon layer of ROI surface
        tri_center_coord_mid : np.ndarray of float [N_roi_tri x 3]
            Coordinates (x, y, z) of triangle center of ROI surface
        tri_center_coord_low : np.ndarray of float [N_roi_tri x 3]
            Coordinates (x, y, z) of triangle center of lower epsilon layer of ROI surface
        fn_mask : str
            Filename for freesurfer mask. If given, this is used instead of *_ROIs
        X_ROI : list of float
            Region of interest [Xmin, Xmax], whole X range if empty [0,0] or None
            (left - right)
        Y_ROI : list of float
            Region of interest [Ymin, Ymax], whole Y range if empty [0,0] or None
            (anterior - posterior)
        Z_ROI : list of float
            Region of interest [Zmin, Zmax], whole Z range if empty [0,0] or None
            (inferior - superior)

        Example
        -------
        make_GM_WM_surface(self, gm_surf_fname, wm_surf_fname, delta, X_ROI, Y_ROI, Z_ROI)
        make_GM_WM_surface(self, gm_surf_fname, wm_surf_fname, delta, mask_fn, layer=3)
        """

        self.gm_surf_fname = gm_surf_fname
        self.wm_surf_fname = wm_surf_fname
        self.midlayer_surf_fname = midlayer_surf_fname
        self.layer = layer
        self.mesh_folder = mesh_folder
        self.fn_mask = fn_mask
        self.delta = delta
        self.X_ROI = x_roi
        self.Y_ROI = y_roi
        self.Z_ROI = z_roi
        self.refine = refine

        if type(gm_surf_fname) is not list:
            gm_surf_fname = [gm_surf_fname]

        if type(wm_surf_fname) is not list:
            wm_surf_fname = [wm_surf_fname]

        if type(midlayer_surf_fname) is not list:
            midlayer_surf_fname = [midlayer_surf_fname]

        if len(gm_surf_fname) != len(wm_surf_fname):
            raise Exception('provide equal number of GM and WM surfaces!')

        # load surface data
        points_gm = [None for _ in range(len(gm_surf_fname))]
        points_wm = [None for _ in range(len(wm_surf_fname))]
        points_mid = [None for _ in range(len(midlayer_surf_fname))]
        con_gm = [None for _ in range(len(gm_surf_fname))]
        # con_wm = [None for _ in range(len(wm_surf_fname))]
        con_mid = [None for _ in range(len(midlayer_surf_fname))]

        max_idx_gm = 0
        # max_idx_wm = 0
        max_idx_mid = 0

        def read_geom(fn, max_idx):
            """
            Read freesurfer geometries, either in .central format or as .gii
            """
            if not fn.startswith(os.sep):
                fn = os.path.join(mesh_folder, fn)

            # charm uses .gii files
            if fn.endswith('.gii'):
                points, con = nib.load(fn).agg_data()

            # headreco uses .central files
            else:
                points, con = nib.freesurfer.read_geometry(fn)

            con += max_idx
            max_idx += points.shape[0]  # np.max(con_gm[i]) + 2
            return points, con, max_idx

        for i in range(len(gm_surf_fname)):
            if gm_surf_fname[i] is not None:
                points_gm[i], con_gm[i], max_idx_gm = read_geom(gm_surf_fname[i], max_idx_gm)

            if wm_surf_fname[i] is not None:
                points_wm[i], _, max_idx_wm = read_geom(wm_surf_fname[i], max_idx_gm)

            if midlayer_surf_fname[i] is not None:
                points_mid[i], con_mid[i], max_idx_mid = read_geom(midlayer_surf_fname[i], max_idx_mid)

        points_gm = np.vstack(points_gm)
        points_wm = np.vstack(points_wm)
        points_mid = np.vstack(points_mid)
        con_gm = np.vstack(con_gm)
        # con_wm = np.vstack(con_wm) # we don't use this
        con_mid = np.vstack(con_mid)

        # Determine 3 layer midlayer if GM and WM surfaces are present otherwise use provided midlayer data
        if gm_surf_fname[0] is not None and wm_surf_fname[0] is not None:
            # determine vector pointing from wm surface to gm surface
            wm_gm_vector = points_gm - points_wm

            eps_0 = 0.025
            eps, surface_points_upper, surface_points_lower = (False,) * 3
            surface_points_upper = False
            if layer == 3:
                # set epsilon range for upper and lower surface
                if delta < eps_0:
                    eps = delta / 2
                elif delta > (1 - eps_0):
                    eps = (1 - delta) / 2
                else:
                    eps = eps_0

            # determine wm-gm surfaces
            surface_points_middle = points_wm + wm_gm_vector * delta  # type: np.ndarray
            if layer == 3:
                surface_points_upper = surface_points_middle + wm_gm_vector * eps
                surface_points_lower = surface_points_middle - wm_gm_vector * eps

            con = con_gm

        elif midlayer_surf_fname[0] is not None:
            self.layer = 1

            surface_points_upper = None
            surface_points_lower = None
            surface_points_middle = points_mid

            con = con_mid

        else:
            raise IOError("Please provide GM and WM surfaces or midlayer "
                          "surface directly for midlayer calculation...")

        # crop region if desired
        x_roi_wb, y_roi_wb, z_roi_wb = (False,) * 3
        if fn_mask is None:
            # crop to region of interest
            if x_roi is None or x_roi == [0, 0]:
                x_roi = [-np.inf, np.inf]
                x_roi_wb = True
            if y_roi is None or y_roi == [0, 0]:
                y_roi = [-np.inf, np.inf]
                y_roi_wb = True
            if z_roi is None or z_roi == [0, 0]:
                z_roi = [-np.inf, np.inf]
                z_roi_wb = True

            roi_mask_bool = (surface_points_middle[:, 0] > min(x_roi)) & (surface_points_middle[:, 0] < max(x_roi)) & \
                            (surface_points_middle[:, 1] > min(y_roi)) & (surface_points_middle[:, 1] < max(y_roi)) & \
                            (surface_points_middle[:, 2] > min(z_roi)) & (surface_points_middle[:, 2] < max(z_roi))
            roi_mask_idx = np.where(roi_mask_bool)

        else:
            if x_roi is not None or y_roi is not None or z_roi is not None:
                raise ValueError(f"Either provide X_ROI, Y_ROI, Z_ROI or fn_mask, not both.")

            # read mask from freesurfer mask file
            if not fn_mask.startswith(os.sep):
                fn_mask = os.path.join(mesh_folder, fn_mask)
            if fn_mask.endswith('.mgh') or fn_mask.endswith('.mgz'):
                mask = nib.freesurfer.mghformat.MGHImage.from_filename(fn_mask).dataobj[:]
            else:
                mask = nib.freesurfer.read_morph_data(fn_mask)[:, np.newaxis, np.newaxis]
            roi_mask_idx = np.where(mask > 0.5)

        # redefine connectivity matrix for cropped points (reindexing)
        # get row index where all points are lying inside ROI
        if not (x_roi_wb and y_roi_wb and z_roi_wb):
            con_row_idx = [i for i in range(con.shape[0]) if len(np.intersect1d(con[i,], roi_mask_idx)) == 3]
            # crop connectivity matrix to ROI
            con_cropped = con[con_row_idx,]
        else:
            con_cropped = con

        # evaluate new indices of cropped connectivity matrix
        point_idx_before, point_idx_after = np.unique(con_cropped, return_inverse=True)
        con_cropped_reform = np.reshape(point_idx_after, (con_cropped.shape[0], con_cropped.shape[1]))

        # crop points to ROI
        surface_points_middle = surface_points_middle[point_idx_before,]
        if self.layer == 3:
            surface_points_upper = surface_points_upper[point_idx_before,]
            surface_points_lower = surface_points_lower[point_idx_before,]

        # refine
        if refine:
            if not os.path.exists(os.path.join(self.mesh_folder, "roi", "tmp")):
                os.makedirs(os.path.join(self.mesh_folder, "roi", "tmp"))

            mesh = trimesh.Trimesh(vertices=surface_points_middle,
                                   faces=con_cropped_reform)
            mesh.export(os.path.join(self.mesh_folder, "roi", "tmp", "roi.stl"))

            pynibs.mesh.refine_surface(fn_surf=os.path.join(self.mesh_folder, "roi", "tmp", "roi.stl"),
                                       fn_surf_refined=os.path.join(self.mesh_folder, "roi", "tmp", "roi_refined.stl"),
                                       center=[0, 0, 0],
                                       radius=np.inf,
                                       verbose=True,
                                       repair=False)

            roi = trimesh.load(os.path.join(self.mesh_folder, "roi", "tmp", "roi_refined.stl"))
            con_cropped_reform = roi.faces
            surface_points_middle = roi.vertices

            if self.layer == 3:
                roi = []

                for p in [surface_points_upper, surface_points_lower]:
                    mesh = trimesh.Trimesh(vertices=p,
                                           faces=con_cropped_reform)
                    mesh.export(os.path.join(self.mesh_folder, "roi", "tmp", "roi.stl"))

                    pynibs.mesh.refine_surface(fn_surf=os.path.join(self.mesh_folder, "roi", "tmp", "roi.stl"),
                                               fn_surf_refined=os.path.join(self.mesh_folder, "roi", "tmp",
                                                                            "roi_refined.stl"),
                                               center=[0, 0, 0],
                                               radius=np.inf,
                                               verbose=True,
                                               repair=False)

                    roi.append(trimesh.load(os.path.join(self.mesh_folder, "roi", "tmp", "roi_refined.stl")))

                surface_points_upper = roi[0].vertices
                surface_points_lower = roi[1].vertices

        self.node_coord_mid = surface_points_middle
        self.node_number_list = con_cropped_reform

        if self.layer == 3:
            self.node_coord_up = surface_points_upper
            self.node_coord_low = surface_points_lower
            self.tri_center_coord_up = np.average(self.node_coord_up[self.node_number_list], axis=1)
            self.tri_center_coord_low = np.average(self.node_coord_low[self.node_number_list], axis=1)

        self.tri_center_coord_mid = np.average(self.node_coord_mid[self.node_number_list], axis=1)

        if self.layer == 3:
            return surface_points_upper, surface_points_middle, surface_points_lower, con_cropped_reform
        else:
            return surface_points_middle, con_cropped_reform

    def determine_element_idx_in_mesh(self, msh):
        """
        Determines tetrahedra indices of msh where the triangle center points of upper, middle and lower surface
        and the nodes of middle surface are lying in.

        Parameters
        ----------
        msh : pynibs.TetrahedraLinear
            Object instance of TetrahedraLinear class

        Returns
        -------
        RegionOfInterestSurface.tet_idx_tri_center_up : np.ndarray [N_points]
            Tetrahedra indices of TetrahedraLinear object instance where the center points of the triangles of the
            upper surface are lying in
        RegionOfInterestSurface.tet_idx_tri_center_mid : np.ndarray [N_points]
            Tetrahedra indices of TetrahedraLinear object instance where the center points of the triangles of the
            middle surface are lying in
        RegionOfInterestSurface.tet_idx_tri_center_low : np.ndarray [N_points]
            Tetrahedra indices of TetrahedraLinear object instance where the center points of the triangles of the
            lower surface are lying in
        RegionOfInterestSurface.tet_idx_node_coord_mid : np.ndarray [N_tri]
            Tetrahedra indices of TetrahedraLinear object instance where the nodes of the middle surface are lying in
     """
        # determine tetrahedra indices of triangle center points of upper, middle and lower surface
        if self.tri_center_coord_low != [] and self.tri_center_coord_up != []:
            points = [self.tri_center_coord_low,
                      self.tri_center_coord_mid,
                      self.tri_center_coord_up]
        else:
            points = [self.tri_center_coord_mid]

        tet_idx = determine_element_idx_in_mesh(fname=None,
                                                msh=msh,
                                                points=points,
                                                compute_baricentric=False)

        if self.tri_center_coord_low != [] and self.tri_center_coord_up != []:
            self.tet_idx_tri_center_low = tet_idx[:, 0]
            self.tet_idx_tri_center_mid = tet_idx[:, 1]
            self.tet_idx_tri_center_up = tet_idx[:, 2]
        else:
            self.tet_idx_tri_center_low = None
            self.tet_idx_tri_center_mid = tet_idx[:, 0]
            self.tet_idx_tri_center_up = None

        # determine tetrahedra indices of nodes of middle surface
        self.tet_idx_node_coord_mid = determine_element_idx_in_mesh(fname=None,
                                                                    msh=msh,
                                                                    points=self.node_coord_mid,
                                                                    compute_baricentric=False)

    def subsample(self, dist=10, fn_sphere=""):
        """
        Subsample ROI surface and return element indices

        Parameters
        ----------
        dist : float
            Distance in mm the subsampled points lie apart
        fn_sphere : str
            Name of ?.sphere file (freesurfer)

        Returns
        -------
        ele_idx : ndarray of float [n_ele]
            Element indices of the subsampled surface
        """

        # load sphere surface
        sphere_coords, sphere_faces = nib.freesurfer.io.read_geometry(fn_sphere)

        # sample sphere equally
        r = np.linalg.norm(sphere_coords[0, :])
        a0 = 4 * np.pi * r ** 2

        sphere_points_sampled = pynibs.sample_sphere(n_points=int(np.ceil(a0 / dist ** 2) // 2 * 2 + 1),
                                                     r=np.linalg.norm(sphere_coords[0, :]))

        # read mask from freesurfer mask file
        mask = nib.freesurfer.mghformat.MGHImage.from_filename(
                os.path.join(self.mesh_folder, self.fn_mask)).dataobj[:].flatten()
        roi_mask_idx = np.where(mask > 0.5)

        con_row_idx = [i for i in range(sphere_faces.shape[0]) if
                       len(np.intersect1d(sphere_faces[i,], roi_mask_idx)) == 3]

        # crop connectivity matrix to ROI
        con_cropped = sphere_faces[con_row_idx,]

        p1_tri = sphere_coords[con_cropped[:, 0], :]
        p2_tri = sphere_coords[con_cropped[:, 1], :]
        p3_tri = sphere_coords[con_cropped[:, 2], :]
        tri_center = 1.0 / 3 * (p1_tri + p2_tri + p3_tri)
        ele_idx = []

        for i_p_ss in range(sphere_points_sampled.shape[0]):
            dist = np.linalg.norm(tri_center - sphere_points_sampled[i_p_ss], axis=1)

            if np.min(dist) < 1:
                ele_idx.append(np.argmin(dist))

        return ele_idx


class RegionOfInterestVolume:
    """
    Region of interest (volume) class

    Attributes
    ----------
    node_coord : np.ndarray [N_points x 3]
        Coordinates (x,y,z) of ROI tetrahedra nodes
    tet_node_number_list : np.ndarray [N_tet_roi x 3]
        Connectivity matrix of ROI tetrahedra
    tri_node_number_list : np.ndarray [N_tri_roi x 3]
        Connectivity matrix of ROI tetrahedra
    tet_idx_node_coord : np.ndarray [N_points]
        Tetrahedra indices of TetrahedraLinear object instance where the ROI nodes are lying in
    tet_idx_tetrahedra_center : np.ndarray [N_tet_roi]
        Tetrahedra indices of TetrahedraLinear object instance where the center points of the ROI tetrahedra are
        lying in
    tet_idx_triangle_center : np.ndarray [N_tri_roi]
        Tetrahedra indices of TetrahedraLinear object instance where the center points of the ROI triangle are
        lying in. If the ROI is directly generated from the msh instance using "make_roi_volume_from_msh", these
        indices are the triangle indices of the head mesh since the ROI mesh and the head mesh are overlapping. If
        the ROI mesh is not the same as the head mesh, the triangle center of the ROI mesh are always lying in a
        tetrahedra of the head mesh (these indices are given in this case)
    """

    def __init__(self):
        """ Initialize RegionOfInterestVolume class instance """

        self.node_coord = []
        self.tet_node_number_list = []
        self.tri_node_number_list = []
        self.tet_idx_node_coord = []
        self.tet_idx_tetrahedra_center = []
        self.tet_idx_triangle_center = []

    def make_roi_volume_from_msh(self, msh, volume_type='box', x_roi=None, y_roi=None, z_roi=None):
        """
        Generate region of interest (volume) and extract nodes, triangles and tetrahedra from msh instance.

        Parameters
        ----------
        msh: pynibs.TetrahedraLinear
            Mesh object instance of type TetrahedraLinear (see main.py)
        volume_type: str
            Type of ROI ('box' or 'sphere')
        x_roi: list of float
            - type = 'box': [Xmin, Xmax] (in mm), whole X range if empty [0,0] or None (left - right)
            - type = 'sphere': origin [x,y,z]
        y_roi: list of float
            - type = 'box': [Ymin, Ymax] (in mm), whole Y range if empty [0,0] or None (anterior - posterior)
            - type = 'sphere': radius (in mm)
        z_roi: list of float
            - type = 'box': [Zmin, Zmax] (in mm), whole Z range if empty [0,0] or None (inferior - superior)
            - type = 'sphere': None

        Returns
        -------
        RegionOfInterestVolume.node_coord : np.ndarray [N_points x 3]
            Coordinates (x,y,z) of ROI tetrahedra nodes
        RegionOfInterestVolume.tet_node_number_list : np.ndarray [N_tet_roi x 3]
            Connectivity matrix of ROI tetrahedra
        RegionOfInterestVolume.tri_node_number_list : np.ndarray [N_tri_roi x 3]
            Connectivity matrix of ROI tetrahedra
        RegionOfInterestVolume.tet_idx_node_coord : np.ndarray [N_points]
            Tetrahedra indices of TetrahedraLinear object instance where the ROI nodes are lying in
        RegionOfInterestVolume.tet_idx_tetrahedra_center : np.ndarray [N_tet_roi]
            Tetrahedra indices of TetrahedraLinear object instance where the center points of the ROI tetrahedra are
            lying in
        RegionOfInterestVolume.tet_idx_triangle_center : np.ndarray [N_tri_roi]
            Tetrahedra indices of TetrahedraLinear object instance where the center points of the ROI triangle are
            lying in. If the ROI is directly generated from the msh instance using "make_roi_volume_from_msh", these
            indices are the triangle indices of the head mesh since the ROI mesh and the head mesh are overlapping. If
            the ROI mesh is not the same as the head mesh, the triangle center of the ROI mesh are always lying in a
            tetrahedra of the head mesh (these indices are given in this case)
        """

        if volume_type == 'box':
            roi_mask_bool = (msh.points[:, 0] > min(x_roi)) & (msh.points[:, 0] < max(x_roi)) & \
                            (msh.points[:, 1] > min(y_roi)) & (msh.points[:, 1] < max(y_roi)) & \
                            (msh.points[:, 2] > min(z_roi)) & (msh.points[:, 2] < max(z_roi))
            roi_mask_idx = np.where(roi_mask_bool)[0]

        elif volume_type == 'sphere':
            roi_mask_bool = np.linalg.norm(msh.points - np.array(x_roi), axis=1) <= y_roi
            roi_mask_idx = np.where(roi_mask_bool)[0]

        else:
            raise Exception('region of interest type not specified correctly (either box or sphere)')

        self.node_coord = msh.points[roi_mask_idx, :]

        # crop connectivity matrices of tetrahedra and triangles to ROI
        tet_con_row_idx = [i for i in range(msh.tetrahedra.shape[0]) if
                           len(np.intersect1d(msh.tetrahedra[i,], roi_mask_idx)) == 3]
        tet_con_cropped = msh.tetrahedra[tet_con_row_idx,]

        tri_con_row_idx = [i for i in range(msh.triangles.shape[0]) if
                           len(np.intersect1d(msh.triangles[i,], roi_mask_idx)) == 3]
        tri_con_cropped = msh.triangles[tri_con_row_idx,]

        # evaluate new indices of cropped connectivity matrices of tetrahedra and triangles (starts from 0)
        tet_point_idx_before, tet_point_idx_after = np.unique(tet_con_cropped, return_inverse=True)
        self.tet_node_number_list = np.reshape(tet_point_idx_after,
                                               (tet_con_cropped.shape[0], tet_con_cropped.shape[1]))

        tri_point_idx_before, tri_point_idx_after = np.unique(tri_con_cropped, return_inverse=True)
        self.tri_node_number_list = np.reshape(tri_point_idx_after,
                                               (tri_con_cropped.shape[0], tri_con_cropped.shape[1]))

        self.tet_idx_node_coord = None
        self.tet_idx_tetrahedra_center = np.array(tet_con_row_idx)
        self.tet_idx_triangle_center = np.array(tri_con_row_idx)

    # def make_roi_volume_from_points(self, msh, points):
    #     """
    #     Generate region of interest (volume) and extract nodes, triangles and tetrahedra from msh instance
    #
    #     Parameters
    #     ----------
    #     msh: object instance
    #         Mesh object instance of type TetrahedraLinear (see main.py)
    #     points: np.ndarray [N_points_roi x 3]
    #         Coordinates of points in ROI x, y, z)
    #     """
    #     a=1
    #
    # def determine_element_idx_in_mesh(self):
    #     """ In development """
    #     a=1


# def determine_element_idx_in_mesh_old(self, fname, points, N_MAX_CPU=20):
#     """
#     Determine the element indices where the points_out are lying and safe the results to a .txt file.
#
#     Parameters
#     ----------
#     fname: str
#         Filename of saved .txt file containing the element indices
#     points_out: array(s) of float (list possible)
#         Point coordinates (x,y,z) whose corresponding elements are found
#     N_MAX_CPU: int
#         Number of CPU cores to determine the element indices
#
#     Returns
#     -------
#     <File>: .txt file
#         Element indices of the mesh, where the points are lying in
#     tet_idx: ndarray [N_points x N_point_tupels]
#         Element indices of the mesh, where the points are lying in
#     """
#
#     if type(points) is not list:
#         points = [points]
#
#     # determine size of input data
#     N_points = [points[i].shape[0] for i in range(len(points))]
#     N_points_out_max = np.max(N_points)
#
#     # initialize tet_idx array
#     tet_idx = np.ones([N_points_out_max, len(points)]) * -1
#
#     P1_all = self.points[self.tetrahedra[:, 0], :]
#     P2_all = self.points[self.tetrahedra[:, 1], :]
#     P3_all = self.points[self.tetrahedra[:, 2], :]
#     P4_all = self.points[self.tetrahedra[:, 3], :]
#
#     # determine all volumes (replacing points with points_out)
#     # find the element where all volumes are > 0 (not inverted element)
#     # get index of this tetrahedron
#     # do it successively to decrease amount of volume calculations for all
#     # 4 points in tetrahedra
#
#     N_CPU_total = multiprocessing.cpu_count()
#     if N_CPU_total > N_MAX_CPU:
#         N_CPU = N_MAX_CPU
#     else:
#         N_CPU = N_CPU_total
#
#     if platform.system() == 'Windows':
#         print("Starting single core version with {:d}/{:d} processors ...").format(1, N_CPU_total)
#
#         for j in range(len(points)):
#             chunks = np.arange(len(points[j]))
#             tet_idx[:, j] = elem_workhorse(chunk=chunks,
#                                            points_out=points[j],
#                                            P1_all=P1_all,
#                                            P2_all=P2_all,
#                                            P3_all=P3_all,
#                                            P4_all=P4_all,
#                                            N_points_total=N_points[j],
#                                            N_CPU=N_CPU)
#
#     else:
#         print("Starting multiprocessed index version with {:d}/{:d} processors ...").format(N_CPU, N_CPU_total)
#
#         for j in range(len(points)):
#             print("Starting run " + str(j + 1) + " of " + str(range(len(points))))
#             # n_points[j] are all points in roi
#
#             # range(N_points_out_max) aufteilen nach cpu count
#             avg = N_points[j] / float(N_CPU)
#             chunks = []
#             last = 0.0
#             points_idx = range(N_points[j])
#             while last < N_points[j]:
#                 chunks.append(np.array(points_idx[int(last):int(last + avg)]))
#                 last += avg
#
#             # call pool
#             pool = multiprocessing.Pool(N_CPU)
#             partialized = partial(elem_workhorse,
#                                   points_out=points[j],
#                                   P1_all=P1_all,
#                                   P2_all=P2_all,
#                                   P3_all=P3_all,
#                                   P4_all=P4_all,
#                                   N_points_total=N_points[j],
#                                   N_CPU=N_CPU)
#
#             results = pool.map(partialized, chunks)
#             pool.close()
#             pool.join()
#
#             # concatenate results
#             tet_idx[:, j] = np.concatenate(results, axis=0)
#
#     # save results
#     if not os.path.exists(os.path.dirname(fname)):
#         os.makedirs(os.path.dirname(fname))
#     np.savetxt(fname, tet_idx, '%d')
#     print 'Saved element indices of points_out in {}'.format(fname)
#
#     return tet_idx


def get_sphere_in_nii(center, radius, nii=None, out_fn=None,
                      thresh_by_nii=True, val_in=1, val_out=0,
                      outside_val=0, outside_radius=np.inf):
    """
    Computes a spherical ROI for a given Nifti image (defaults to simnibs MNI T1 tissue). The ROI area is defined
    in nifti coordinates.
    By default, everything inside the ROI is set to 1, areas outside = 0.
    The ROI is further thresholded by the nifti.
    A nib.Nifti image is returned and optionally saved.

    Parameters
    ----------
    center : array-like
        X, Y, Z coordinates in nifti space
    radius : float
        radius of sphere
    nii : string or nib.nifti1.Nifti1Image, optional
        The nifti image to work with.
    out_fn : string, optional
        If provided, sphere ROI image is saved here
    outside_val : float, default = None
        Value outside of outside_radius.
    outside_radius : float, default = None
        Distance factor to define the 'outside' area: oudsidefactor * radius -> outside

    Returns
    -------
    sphere_img :  nib.nifti1.Nifti1Image
    sphere_img : <file>, optional

    Other Parameters
    ----------------
    thresh_by_nii : bool, optional
        Mask sphere by nii != 0
    val_in : float, optional
        Value within ROI
    val_out : float, optional
        Value outside ROI

    Raises
    ------
    ValueError
        If the final ROI is empty.
    """
    from simnibs import SIMNIBSDIR
    if outside_radius is None:
        outside_radius = np.inf
    # load image for affine and tissue borders
    if nii is None:
        mni_fn = f"{SIMNIBSDIR}/resources/templates/spmprior_tissue.nii"
        nii = nib.load(mni_fn)
    elif isinstance(nii, str):
        nii = nib.load(nii)

    center = np.atleast_1d(center).astype(int)
    assert center.shape == (3,)

    roi_data = np.zeros_like(nii.get_fdata())
    roi_data[:] = val_out

    center = np.atleast_1d(center)

    # speed up the long loop below
    affine_inv = np.linalg.inv(nii.affine)
    norm = np.linalg.norm

    center_vox = nib.affines.apply_affine(affine_inv, center)

    if outside_radius != np.inf:
        # search space is whole nifti space
        x_min, y_min, z_min = 0, 0, 0
        x_max, y_max, z_max = nii.shape[:3]

    else:
        # if outside_val should not be set we only need to search within center-radius
        x_min, y_min, z_min = center_vox - radius
        x_max, y_max, z_max = center_vox + radius

    # compute spherical roi around nifti coordinates
    # do this in original coordinates to have correct mm radius

    pixdim = nii.get_header()['pixdim'][1:4]
    for xyz in tqdm.tqdm(product(range(x_min, x_max), range(y_min, y_max), range(z_min, z_max)),
                         total=x_max * y_max * z_max,
                         desc="Finding ROI elements."):
        # set to val_in if within radius
        dist = norm(np.multiply(pixdim, center_vox - xyz))
        if dist < radius:
            roi_data[xyz] = val_in
        elif dist > outside_radius:
            # Set values outside of outside_radius to outside_val
            roi_data[xyz] = outside_val

    # check if there's something left in the ROI
    if np.sum(roi_data) == 0:
        raise ValueError(f"No tissue found in {radius} mm sphere around {center}.")

    # threshold roi by tissue
    if thresh_by_nii:
        roi_data[nii.get_fdata() == 0] = 0
        roi_data[np.isnan(nii.get_fdata())] = 0

    roi_mni_img = nib.Nifti1Image(roi_data, nii.affine)

    if out_fn is not None:
        # make new roi image and save file
        nib.save(roi_mni_img, out_fn)

    return roi_mni_img


def create_refine_spherical_roi(center, radius, final_tissues_nii, out_fn, target_size=.5,
                                outside_size=None, outside_factor=3,
                                out_spher_fn=None, tissue_types=None, verbose=False):
    """
    Create a spherical roi nifti for simnibs 4 refinement.
    Only tissue types accoring to _tissue_types will be refined.

    Use the resulting output file as input for --sizing_field in SimNIBS-4/simnibs/cli/meshmesh.py

    Paraneters
    ----------
    center : list of float
        Center of spherical ROI in mm
    radius : float
        Radius of spherical ROI in mm
    final_tissues_nii : string or nib.nifti1.Nifti1Image
        final_tissues.nii.gz to create roi for.
    out_fn : str
        Final output filename
    target_size : float, default = 0.5
        Target element size of refined areas in mm (?)
    outside_size : float, default = None
        Element size outside of target size.
    outside_factor : float, default = None
        Distance factor to define the 'outside' area: oudsidefactor * radius -> outside

    Other parameters
    ----------------
    out_spher_fn : str, optional
        Output filename of orignal, raw spherical ROI
    tissue_types : list of float, default = [1,2,3]
        Which tissue types to refine. Defaults to WM, GM, CSF
    verbose : bool, optional, default=False
        Print additional information
    """
    # get spherical ROI, masked to all tissues
    roi_img = get_sphere_in_nii(
            center=center,
            radius=radius,
            nii=final_tissues_nii,
            val_in=target_size,
            out_fn=out_spher_fn,
            outside_val=outside_size, outside_radius=radius * outside_factor)

    # get tissue_types data
    if isinstance(final_tissues_nii, str):
        final_tissues_nii = nib.load(final_tissues_nii)
    org_img_data = final_tissues_nii.get_fdata()

    if tissue_types is None:
        tissue_types = [1, 2, 3]

    data = roi_img.get_fdata()
    if verbose:
        print(f"{np.sum(data == target_size): >6} elements found in spherical roi.")
        if outside_size is not None:
            print(f"{np.sum(data == outside_size): >6} elements outside area in spherical roi.")
    # apply tissue_types list mask
    data[~np.isin(org_img_data, tissue_types) & (data == target_size)] = 0

    # apply refined element size
    # data[data == 1] = target_size

    if verbose:
        print(f"{np.sum(data != 0): >6} elements found in spherical roi for tissues {tissue_types}.")

    # write final image
    roi_refine_img = nib.Nifti2Image(affine=roi_img.affine, dataobj=data)
    roi_refine_img.to_filename(out_fn)


def clean_roi(img, vox_thres=.5, fn_out=None):
    """
    Remove values < vox thres from image.

    Parameters
    ----------
    img : str or nibabel.nifti1.Nifti1Image
    vox_thres : float, optional
    fn_out : str

    Returns
    -------
    img_thres : nibabel.nifti1.Nifti1Image
    img_thres : <file>
        If fn_out is specified, thresholded image is saved here
    """
    # threshold subject space image to remove speckles
    if isinstance(img, str):
        nii = nib.load(img)
    else:
        nii = img
    data = nii.get_fdata()
    data[(data < vox_thres)] = 0
    nii = nib.Nifti1Image(data, nii.affine)
    if fn_out is not None:
        nib.save(nii, fn_out)
    return nii


def nii2msh(mesh, m2m_dir, nii, out_folder, hem, out_fsaverage=False, roi_name='ROI'):
    """
    Transform a nifti ROI image to subject space .mgh file.

    Parameters
    ----------
    mesh : simnibs.Mesh or str
    m2m_dir : str
    nii : nibabel.nifti1.Nifti1Image or str
    out_folder : str
    hem : str
        'lh' or 'rh'
    out_fsaverage : bool

    Returns
    -------
    roi : file
        f"{out_folder}/{hem}.mesh.central.{roi_name}"

    Other Parameters
    ----------------
    roi_name : str
        How to name the ROI
    """
    from simnibs import mesh_io, transformations
    if isinstance(mesh, str):
        mesh = mesh_io.read_msh(mesh)
    if isinstance(nii, str):
        nii = nib.load(nii)
    assert hem in ['lh', 'rh'], f"hem argument must be one of ('lh','rh). You specified hem={hem}."

    fn_mesh_out = os.path.join(out_folder, 'mesh.msh')
    vol = nii.dataobj
    affine = nii.affine

    # Interpolating data in NifTI file to mesh
    # nd = mesh_io.NodeData.from_data_grid(mesh, vol, affine, 'from_volume')

    # meshify
    ed = mesh_io.ElementData.from_data_grid(mesh, vol, affine, roi_name)
    mesh.nodedata = []
    mesh.elmdata = [ed]
    mesh_io.write_msh(mesh, fn_mesh_out)

    # trasform to midlayer
    if out_fsaverage:
        out_fsaverage = out_folder
    else:
        out_fsaverage = None
    transformations.middle_gm_interpolation(fn_mesh_out, m2m_folder=m2m_dir,
                                            out_folder=out_folder, out_fsaverage=out_folder)

    return nib.freesurfer.read_morph_data(os.path.join(out_folder, f"{hem}.mesh.central.{roi_name}"))
