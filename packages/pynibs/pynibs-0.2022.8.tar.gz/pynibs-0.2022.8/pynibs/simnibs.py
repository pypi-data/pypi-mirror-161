import gc
import re
import warnings
import copy
import numpy as np
import trimesh
import pynibs


def calc_e_in_midlayer_roi(phi_dadt, roi, subject, phi_scaling=1., mesh_idx=0, mesh=None, roi_hem='lh', depth=.5,
                           qoi=None):
    """
    This is to be called by Simnibs as postprocessing function per FEM solve.

    Parameters
    ----------
    phi_dadt : (array-like, elmdata)
    roi : pynibs.roi.RegionOfInterestSurface()
    subject: pynibs.Subject()
    phi_scaling : float
    mesh_idx : int
    mesh : simnibs.msh.Mesh()
    roi_hem : 'lh'
    depth : float
    qoi : list of str

    Returns
    -------
    (roi.n_tris,4) : np.vstack((e_mag, e_norm, e_tan, e_angle)).transpose()
    """
    if depth != .5:
        raise NotImplementedError(f"depth={depth} != 0.5 not implemented")
    import simnibs
    v_simnibs = int(simnibs.__version__[0])
    if v_simnibs == 3:
        # SimNIBS < 4 imports
        import simnibs.msh.mesh_io as mesh_io
        from simnibs.msh.mesh_io import Msh
        from simnibs.msh.mesh_io import Nodes
        from simnibs.msh.mesh_io import Elements
        from simnibs.msh.transformations import get_surface_names_from_folder_structure
    else:
        # SimNIBS >= 4 imports
        import simnibs.mesh_tools.mesh_io as mesh_io
        from simnibs.mesh_tools.mesh_io import Msh
        from simnibs.mesh_tools.mesh_io import Nodes
        from simnibs.mesh_tools.mesh_io import Elements

    import simnibs.simulation.fem as fem
    # mesh_folder = subject.mesh[mesh_idx]["mesh_folder"]

    # set default return quantities
    if qoi is None:
        qoi = ['E', 'mag', 'norm', 'tan', 'angle']
    qois_to_calc = copy.copy(qoi)
    ret_arr_shape = len(qoi)

    # some special care for E
    if 'E' in qoi:
        ret_arr_shape += 2  # E is 3D
        qois_to_calc.remove('E')  # we don't need this to be computed, it already is

    # simnibs calls this with empty data so find out about the results dimensions
    if isinstance(phi_dadt, tuple):
        # SimNIBS 4 includes 'phi/v' last in the tuple of the to-be computed fields
        phi = phi_dadt[-1] * phi_scaling
        # dadt = phi_dadt[1].elm_data2node_data().value
    else:
        return np.zeros((roi.n_tris, ret_arr_shape))

    def calc_quantities(nd, quants):
        quants = dict.fromkeys(quants)
        for quant in quants:
            if quant == 'mag':
                quants[quant] = nd.norm()
            elif quant == 'norm':
                quants[quant] = nd.normal()
                quants[quant].value *= -1
            elif quant == 'tan':
                quants[quant] = nd.tangent()
            elif quant == 'angle':
                quants[quant] = nd.angle()
            else:
                raise ValueError('Invalid quantity: {0}'.format(quant))
        return quants

    # prepare mesh_local
    mesh_local = copy.deepcopy(mesh)

    # write phi and dAdt in msh
    # dadt = mesh_io.NodeData(dadt, name='D', mesh=mesh_local)
    try:
        dadt = phi_dadt[0].value
    except AttributeError:
        dadt = phi_dadt[0]
    dadt = mesh_io.ElementData(dadt, name='D', mesh=mesh_local)
    phi = mesh_io.NodeData(phi.flatten(), name='v', mesh=mesh_local)

    mesh_local = fem.calc_fields(phi, "vDEe", cond=None, dadt=dadt)
    mesh_local = mesh_local.crop_mesh(2)

    # get folder names and such
    # m2m_folder = os.path.join(mesh_folder, "m2m_" + subject.id)
    # m2m_folder = os.path.abspath(os.path.normpath(m2m_folder))

    # if v_simnibs == 3:
    #     names, segtype = get_surface_names_from_folder_structure(m2m_folder)
    #     # middle_surf = {}
    #
    #     # get midlayer
    #     if segtype == 'mri2mesh':
    #         # for hemi in ['lh', 'rh']:
    #         wm_surface = mesh_io.read_freesurfer_surface(names[roi_hem + '_wm'])
    #         gm_surface = mesh_io.read_freesurfer_surface(names[roi_hem + '_gm'])
    #         # middle_surf = mesh_io._middle_surface(wm_surface, gm_surface, depth)
    #     elif segtype == 'headreco':
    #         pass
    #         # for hemi in ['lh', 'rh']:
    #         # middle_surf = mesh_io.read_gifti_surface(names[roi_hem + '_midgm'])
    #     else:
    #         raise NotImplementedError(f"segtype {segtype} unknown.")

    # initialize ROI surface
    surface = Msh(nodes=Nodes(node_coord=roi.node_coord_mid),
                  elements=Elements(triangles=roi.node_number_list + 1))

    # calc QOIs
    qois_dict = {}
    data = mesh_local.field['E']
    data = data.as_nodedata()
    interpolated = data.interpolate_to_surface(surface)

    q = calc_quantities(interpolated, qois_to_calc)
    for q_name, q_data in q.items():
        qois_dict[q_name] = q_data.value

    for q_name in qoi:
        if q_name == 'E':
            qois_dict[q_name] = interpolated.value

        # transform point data to element data
        qois_dict[q_name] = pynibs.data_nodes2elements(data=qois_dict[q_name], con=roi.node_number_list)
        # crop results data to ROI
        qois_dict[q_name] = qois_dict[q_name]
        if qois_dict[q_name].ndim == 1:
            qois_dict[q_name] = qois_dict[q_name][:, np.newaxis]

    res = tuple(qois_dict[q_name] for q_name in qoi)
    del qois_dict, surface, interpolated, mesh_local, phi, mesh, simnibs, data
    gc.collect()

    return np.hstack(res)


# def calc_e_in_midlayer_roi(phi_dadt, roi, subject, phi_scaling=1., mesh_idx=0, mesh=None, roi_hem='lh', depth=.5,
#                            qoi=None):
#     """
#     This is to be called by Simnibs as postprocessing function per FEM solve.
#
#     Parameters
#     ----------
#     phi_dadt : (array-like, elmdata)
#     roi : pynibs.roi.RegionOfInterestSurface()
#     subject: pynibs.Subject()
#     phi_scaling : float
#     mesh_idx : int
#     mesh : simnibs.msh.Mesh()
#     roi_hem : 'lh'
#     depth : float
#     qoi : list of str
#
#     Returns
#     -------
#     (roi.n_tris,4) : np.vstack((e_mag, e_norm, e_tan, e_angle)).transpose()
#     """
#     from .main import data_nodes2elements
#     import simnibs.msh.mesh_io as mesh_io
#     import simnibs.simulation.fem as fem
#     from simnibs.msh.transformations import get_surface_names_from_folder_structure
#
#     mesh_folder = subject.mesh[mesh_idx]["mesh_folder"]
#
#     # set default return quantities
#     if qoi is None:
#         qoi = ['E', 'mag', 'norm', 'tan', 'angle']
#     qois_to_calc = copy.copy(qoi)
#     ret_arr_shape = len(qoi)
#
#     # some special care for E
#     if 'E' in qoi:
#         ret_arr_shape += 2  # E is 3D
#         qois_to_calc.remove('E')  # we don't need this to be computed, it already is
#
#     # simnibs calls this with empty data so find out about the results dimensions
#     if isinstance(phi_dadt, tuple):
#         phi = phi_dadt[0] * phi_scaling
#         # dadt = phi_dadt[1].elm_data2node_data().value
#     else:
#         return np.zeros((roi.n_tris, ret_arr_shape))
#
#     def calc_quantities(nd, quants):
#         quants = dict.fromkeys(quants)
#         for quant in quants:
#             if quant == 'mag':
#                 quants[quant] = nd.norm()
#             elif quant == 'norm':
#                 quants[quant] = nd.normal()
#                 quants[quant].value *= -1
#             elif quant == 'tan':
#                 quants[quant] = nd.tangent()
#             elif quant == 'angle':
#                 quants[quant] = nd.angle()
#             else:
#                 raise ValueError('Invalid quantity: {0}'.format(quant))
#         return quants
#
#     # prepare mesh_local
#     mesh_local = copy.deepcopy(mesh)
#
#     # write phi and dAdt in msh
#     # dadt = mesh_io.NodeData(dadt, name='D', mesh=mesh_local)
#     try:
#         dadt = phi_dadt[1].value
#     except AttributeError:
#         dadt = phi_dadt[1]
#     dadt = mesh_io.ElementData(dadt, name='D', mesh=mesh_local)
#     phi = mesh_io.NodeData(phi.flatten(), name='v', mesh=mesh_local)
#
#     mesh_local = fem.calc_fields(phi, "vDEe", cond=None, dadt=dadt)
#     mesh_local = mesh_local.crop_mesh(2)
#
#     # get folder names and such
#     m2m_folder = os.path.join(mesh_folder, "m2m_" + subject.id)
#     m2m_folder = os.path.abspath(os.path.normpath(m2m_folder))
#     names, segtype = get_surface_names_from_folder_structure(m2m_folder)
#     # middle_surf = {}
#
#     # get midlayer
#     if segtype == 'mri2mesh':
#         # for hemi in ['lh', 'rh']:
#         wm_surface = mesh_io.read_freesurfer_surface(names[roi_hem + '_wm'])
#         gm_surface = mesh_io.read_freesurfer_surface(names[roi_hem + '_gm'])
#         middle_surf = mesh_io._middle_surface(wm_surface, gm_surface, depth)
#     elif segtype == 'headreco':
#         # for hemi in ['lh', 'rh']:
#         middle_surf = mesh_io.read_gifti_surface(names[roi_hem + '_midgm'])
#     else:
#         raise NotImplementedError(f"segtype {segtype} unknown.")
#
#     # calc QOIs
#     qois_dict = {}
#     data = mesh_local.field['E']
#     name = 'E'
#
#     data = data.as_nodedata()
#     interpolated = data.interpolate_to_surface(middle_surf)
#
#     q = calc_quantities(interpolated, qois_to_calc)
#     for q_name, q_data in q.items():
#         qois_dict[q_name] = q_data.value
#         middle_surf.add_node_field(q_data, name + '_' + q_name)
#
#     # load freesurfer surface
#     if type(roi.gm_surf_fname) is np.ndarray:
#         if roi.gm_surf_fname.ndim == 0:
#             roi.gm_surf_fname = [roi.gm_surf_fname.astype(str).tolist()]
#         else:
#             roi.gm_surf_fname = roi.gm_surf_fname.astype(str).tolist()
#
#     # if not isinstance(roi.gm_surf_fname, str):
#     #     raise NotImplementedError
#
#     if roi.gm_surf_fname in ('None', None, ''):
#         nodes_gm, tri_gm = nibabel.freesurfer.read_geometry(os.path.join(mesh_folder, roi.midlayer_surf_fname))
#     else:
#         nodes_gm, tri_gm = nibabel.freesurfer.read_geometry(os.path.join(mesh_folder, roi.gm_surf_fname))
#
#     if roi.fn_mask is None:
#         roi_mask_bool = (roi.node_coord_mid[:, 0] > min(roi.X_ROI)) & (
#                 roi.node_coord_mid[:, 0] < max(roi.X_ROI)) & \
#                         (roi.node_coord_mid[:, 1] > min(roi.Y_ROI)) & (
#                                 roi.node_coord_mid[:, 1] < max(roi.Y_ROI)) & \
#                         (roi.node_coord_mid[:, 2] > min(roi.Z_ROI)) & (
#                                 roi.node_coord_mid[:, 2] < max(roi.Z_ROI))
#         roi_mask_idx = np.where(roi_mask_bool)
#
#     else:
#         if type(roi.fn_mask) is np.ndarray:
#             if roi.fn_mask.ndim == 0:
#                 roi.fn_mask = roi.fn_mask.astype(str).tolist()
#
#         # read mask from freesurfer mask file (mask for freesurfer .pial)
#         mask = nibabel.freesurfer.mghformat.MGHImage.from_filename(os.path.join(mesh_folder, roi.fn_mask)).dataobj[:]
#         roi_mask_idx = np.where(mask > 0.5)
#
#     # get row index where all points are lying inside ROI
#     # find triangles idx which have all nodes in mask
#     # this is the old version:
#     # con_row_idx = [i for i in range(tri_gm.shape[0]) if len(np.intersect1d(tri_gm[i,], roi_mask_idx)) == 3]
#     # new, faster verion. might be more picky on dimensions
#     con_row_idx = np.where(np.isin(tri_gm[:, 0], roi_mask_idx) &
#                            np.isin(tri_gm[:, 1], roi_mask_idx) &
#                            np.isin(tri_gm[:, 2], roi_mask_idx))[0]
#     # assert np.all(con_row_idx_fast == con_row_idx) # yep
#
#     if roi_hem == 'rh':
#         warnings.warn("rh is untested")
#     # elif roi_hem == 'rh':
#     #     hem_idx = 1
#     #     warnings.warn("Right hemisphere roi is untested.")
#     # else:
#     #     raise NotImplementedError
#
#     for q_name in qoi:
#         if q_name == 'E':
#             qois_dict[q_name] = interpolated.value
#         # else:
#         #     qois_dict[q_name] = qois_dict[q_name]
#
#         # transform point data to element data
#         qois_dict[q_name] = data_nodes2elements(data=qois_dict[q_name], con=tri_gm)
#         # crop results data to ROI
#         qois_dict[q_name] = qois_dict[q_name][con_row_idx]
#         if qois_dict[q_name].ndim == 1:
#             qois_dict[q_name] = qois_dict[q_name][:, np.newaxis]
#
#     res = tuple(qois_dict[q_name] for q_name in qoi)
#     return np.hstack(res)


def read_coil_geo(fn_coil_geo):
    """
    Parameters
    ----------
    fn_coil_geo : str
        Filename of *.geo file created from SimNIBS containing the dipole information

    Returns
    -------
    dipole_pos : ndarray of float [n_dip x 3]
        Dipole positions (x, y, z)
    dipole_mag : ndarray of float [n_dip x 1]
        Dipole magnitude
    """
    regex = r"SP\((.*?)\)\{(.*?)\}"
    with open(fn_coil_geo, 'r') as file:
        dipole_pos = []
        dipole_mag = []
        while file:
            te = file.readline()

            if te == "":
                break

            try:
                pos, mag = re.findall(regex, te)[0]
                pos = [float(x) for x in pos.split(',')]
                mag = float(mag)
                dipole_pos.append(pos)
                dipole_mag.append(mag)
            except IndexError:
                pass

        dipole_pos = np.vstack(dipole_pos)
        dipole_mag = np.array(dipole_mag)[:, np.newaxis]

    return dipole_pos, dipole_mag


def check_mesh(mesh, verbose=False):
    from simnibs import read_msh
    """
    Check a simmibs.Mesh for degenerated elements:
        - zero surface triangles
        - zerso volume tetrahedra
        - negative volume tetrahedra

    Parameters
    ----------
    mesh : str of simnibs.Mesh

    Other parameters
    -----------------
    verbose : book, default: False
        Print some verbosity messages

    Returns
    -------
    zero_tris : np.ndarray
        Element indices for zero surface tris (0-indexed)
    zero_tets : np.ndarray
        Element indices for zero volume tets (0-indexed)
    neg_tets : np.ndarray
        Element indicies for negative volume tets (0-indexed)

    """
    if isinstance(mesh, str):
        mesh = read_msh(mesh)
    tris = mesh.elm.node_number_list[mesh.elm.triangles - 1][:, :3]
    points_tri = mesh.nodes[tris]
    tri_area = pynibs.calc_tri_surface(points_tri)
    zero_tris = np.argwhere(np.isclose(tri_area, 0, atol=1e-13))
    if verbose:
        print(f"{len(zero_tris)} zero surface triangles found.")

    tets = mesh.elm.node_number_list[mesh.elm.tetrahedra - 1]
    points_tets = mesh.nodes[tets]
    tets_volume = pynibs.calc_tet_volume(points_tets)
    zero_tets = np.argwhere(np.isclose(tets_volume, 0, atol=1e-13))
    if verbose:
        print(f"{len(zero_tets)} zero volume tetrahedra found.")

    tet_idx = mesh.elm.node_number_list[mesh.elm.tetrahedra - 1]
    vol = pynibs.calc_tet_volume(mesh.nodes.node_coord[tet_idx - 1], abs=False)
    neg_idx = np.argwhere(vol > 0)
    if verbose:
        print(f"{len(neg_idx)} negative tets found.")
    neg_idx_in_full_arr = mesh.elm.tetrahedra[neg_idx] - 1

    return zero_tris, zero_tets + len(mesh.elm.triangles), neg_idx_in_full_arr


def fix_mesh(mesh, verbose=False):
    from simnibs import read_msh
    """
    Fixes simnibs.Mesh by removing any zero surface tris and zero volume tets and by fixing negative volume tets.



    Parameters
    ----------
    mesh : str of simnibs.Mesh

    Other parameters
    -----------------
    verbose : book, default: False
        Print some verbosity messages

    Returns
    -------
    fixed_mesh : simnibs.Mesh
    """
    if isinstance(mesh, str):
        mesh = read_msh(mesh)

    zero_tris, zero_tets, neg_tets = check_mesh(mesh, verbose=verbose)

    if neg_tets.size:
        mesh.elm.node_number_list[neg_tets, [0, 1, 2, 3]] = mesh.elm.node_number_list[neg_tets, [0, 1, 3, 2]]

    if zero_tris.size:
        mesh = mesh.remove_from_mesh(elements=zero_tris + 1)

    if zero_tets.size:
        mesh = mesh.remove_from_mesh(elements=zero_tets + 1 - zero_tris.size)

    # check again
    zero_tris, zero_tets, neg_tets = check_mesh(mesh)

    if zero_tris.size or zero_tets.size or neg_tets.size:
        warnings.warn(f"Couldn't fix mesh: zero_tris: "
                      f"{zero_tris.size} zero tris, {zero_tets.size} zero_tets, {neg_tets.size} neg_tets left over.")

    return mesh


def smooth_mesh(mesh, output_fn, smooth=.8, approach='taubin', skin_only_output=False):
    from simnibs import mesh_io
    """
    Smoothes the skin compartment of a simnibs mesh. Uses one of three trimesh.smoothing approaches.

    Parameter
    ---------
    mesh : str or simnibs.Mesh
    output_fn : str
    smooth : float, default: 0.8
        Smoothing aggressiveness. [0, ..., 1]
    approach: str, default: 'taubin'
        Which smoothing approach to use. One of ('taubin', laplacian', 'humphrey)

    Other parameters
    ----------------
    skin_only_output : bool, default: True
        If true, a skin only mesh is written out instead of the full mesh.

    Returns
    -------
    <file> : The smoothed mesh.
    """
    if isinstance(mesh, str):
        mesh = mesh_io.read_msh(mesh)
    mesh_skin = mesh.crop_mesh(elm_type=2)
    mesh_skin = mesh_skin.crop_mesh([5, 1005])
    tri_node_nr = mesh_skin.elm.node_number_list[mesh_skin.elm.triangles - 1] - 1
    tri_node_nr = tri_node_nr[:, :3]

    assert output_fn.endswith('.msh'), f"Wrong file suffix: {output_fn}. Use .msh"
    assert 0 <= smooth <= 1, f"'smooth={smooth}' parameter must be within  [0,1]. "

    # create a Trimesh object based on the skin tris
    mesh_trimesh = trimesh.Trimesh(vertices=mesh_skin.nodes.node_coord,
                                   faces=tri_node_nr,
                                   process=False)  # process=False keeps original ordering
    if approach == 'taubin':
        smoothed_mesh = trimesh.smoothing.filter_taubin(mesh_trimesh.copy(), lamb=smooth)  # do smoothing
    elif approach == 'laplacian':
        smoothed_mesh = trimesh.smoothing.filter_laplacian(mesh_trimesh.copy(), lamb=smooth)  # do smoothing
    elif approach == 'humphrey':
        smoothed_mesh = trimesh.smoothing.filter_humphrey(mesh_trimesh.copy(), alpha=smooth)  # do smoothing
    else:
        raise NotImplementedError(f"Approach {approach} not implemented. Use 'taubin', laplacian', or 'humphrey'.")

    # find indices of nodes in original mesh
    ind_nodes = np.in1d(mesh.nodes.node_coord[:, 0], mesh_skin.nodes.node_coord[:, 0]) + \
                np.in1d(mesh.nodes.node_coord[:, 1], mesh_skin.nodes.node_coord[:, 1]) + \
                np.in1d(mesh.nodes.node_coord[:, 2], mesh_skin.nodes.node_coord[:, 2])
    ind_nodes = np.where(ind_nodes)[0]

    if skin_only_output:
        # replace smoothed nodes in skin only mesh and write to disk
        mesh_skin.nodes.node_coord = smoothed_mesh.vertices  # overwrite simnibs Mesh object's nodes
        mesh_skin.write(output_fn)
    else:
        # replace surface node_number list in full mesh and write to disk
        mesh.nodes.node_coord[ind_nodes, :] = smoothed_mesh.vertices
        mesh.write(output_fn)
