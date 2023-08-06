import numpy as np
import gdist


def geodesic_dist(nodes, tris, source, source_is_node=True):
    """
    Returns geodesic distance of all nodes to source node (or tri).

    This is just a wrapper for the gdist package.

    Example:
    with h5py.File(fn,'r') as f:
        tris = f['/mesh/elm/triangle_number_list'][:]
        nodes = f['/mesh/nodes/node_coord'][:]
    nodes_dist_ged, tris_dist_ged = geodesic_dist(nodes, tris, 3017)

    pynibs.write_data_hdf5(data_fn,
                        data=[tris_dist_ged, nodes_dist_ged],
                        data_names=["tris_dist_ged", "nodes_dist_ged"])
    pynibs.write_xdmf(data_fn,hdf5_geo_fn=fn)


    Parameters
    ----------
    nodes : np.ndarray(n_nodes,3)
    tris : np.ndarray(n_tris,3)
    source: np.ndarray(int) or int
        Geodesic distances of all nodes (or tri) to this will be computed
    source_is_node : bool
        Is source a node idx or a tr idx

    Returns
    -------
    nodes_dist : np.ndarray(n_nodes,)
    tris_dist : np.ndarray(n_tris,)
    """
    if source_is_node:
        if type(source) is not np.ndarray:
            source = np.array([source])
        nodes_dist = gdist.compute_gdist(nodes.astype(np.float64),
                                         tris.astype(np.int32),
                                         source_indices=source.astype(np.int32))

    else:
        nodes = nodes.astype(np.float64)
        tris = tris.astype(np.int32)
        source = tris[source].astype(np.int32)
        nodes_dist = gdist.compute_gdist(nodes,
                                         tris,
                                         source_indices=source)
        # l = []
        # for n in source:
        #     l.append(np.mean(gdist.compute_gdist(nodes,
        #                                  tris,
        #                                  source_indices=np.array([n]).astype(np.int32))[tris],axis=1))
        # # a = np.array(l)
        # nodes_dist = np.mean(l,axis=0)
        # a.shape
    tris_dist = np.mean(nodes_dist[tris], axis=1)

    return nodes_dist, tris_dist


def euclidean_dist(nodes, tris, source, source_is_node=True):
    """
    Returns euclidean_dist distance of all nodes to source node (tria).

    This is just a wrapper for the gdist package.

    Example:
    with h5py.File(fn,'r') as f:
        tris = f['/mesh/elm/triangle_number_list'][:]
        nodes = f['/mesh/nodes/node_coord'][:]
    nodes_dist_euc, tris_dist_euc = euclidean_dist(nodes, tris, 3017)

    pynibs.write_data_hdf5(data_fn,
                        data=[tris_dist_euc, nodes_dist_euc],
                        data_names=["tris_dist_euc", "nodes_dist_euc", "])
    pynibs.write_xdmf(data_fn,hdf5_geo_fn=fn)

    Parameters
    ----------
    nodes : np.ndarray(n_nodes,3)
    tris : np.ndarray(n_tris,3)
    source: np.ndarray(int) or int
        geodesic distances of all nodes to this will be computed
    source_is_node : bool
        Is source a node idx or a tr idx

    Returns
    -------
    nodes_dist : np.ndarray(n_nodes,)
    tres_dist : np.ndarray(n_tris,)
    """
    if source_is_node:
        nodes_dist = np.linalg.norm(nodes - nodes[source], axis=1)
    else:
        nodes_dist = np.zeros(nodes.shape[0], )
        for node in nodes[tris[source]]:
            nodes_dist += np.linalg.norm(nodes - node, axis=1)
        nodes_dist /= 3
    tris_dist = np.mean(nodes_dist[tris], axis=1)

    return nodes_dist, tris_dist


def nrmsd(array, array_ref, error_norm="relative", x_axis=False):
    """
    Determine the normalized root-mean-square deviation between input data and reference data.

    normalized_rms = get_normalized_rms(array, array_ref)

    Parameters
    ----------
    array: np.ndarray
        input data [ (x), y0, y1, y2 ... ]
    array_ref: np.ndarray
        reference data [ (x_ref), y0_ref, y1_ref, y2_ref ... ]
        if array_ref is 1D, all sizes have to match
    error_norm: str, optional, default="relative"
        Decide if error is determined "relative" or "absolute"
    x_axis: boolean, optional, default=False
        If True, the first column of array and array_ref is interpreted as the x-axis, where the data points are
        evaluated. If False, the data points are assumed to be at the same location.

    Returns
    -------
    normalized_rms: ndarray of float [array.shape[1]]
        Normalized root-mean-square deviation between the columns of array and array_ref
    """

    n_points = array.shape[0]

    if x_axis:
        # handle different array lengths
        if len(array_ref.shape) == 1:
            array_ref = array_ref[:, None]
        if len(array.shape) == 1:
            array = array[:, None]

        # determine number of input arrays
        if array_ref.shape[1] == 2:
            n_data = array.shape[1] - 1
        else:
            n_data = array.shape[1]

        # interpolate array on array_ref data if necessary
        if array_ref.shape[1] == 1:
            data = array
            data_ref = array_ref
        else:
            # crop reference if it is longer than the axis of the data
            data_ref = array_ref[(array_ref[:, 0] >= min(array[:, 0])) & (array_ref[:, 0] <= max(array[:, 0])), 1]
            array_ref = array_ref[(array_ref[:, 0] >= min(array[:, 0])) & (array_ref[:, 0] <= max(array[:, 0])), 0]

            data = np.zeros([len(array_ref), n_data])
            for i_data in range(n_data):
                data[:, i_data] = np.interp(array_ref, array[:, 0], array[:, i_data + 1])
    else:
        data_ref = array_ref
        data = array

    # determine "absolute" or "relative" error
    if error_norm == "relative":
        # max_min_idx = np.isclose(np.max(data_ref, axis=0), np.min(data_ref, axis=0))
        delta = np.max(data_ref, axis=0) - np.min(data_ref, axis=0)

        # if max_min_idx.any():
        #     delta[max_min_idx] = max(data_ref[max_min_idx])
    elif error_norm == 'absolute':
        delta = 1
    else:
        raise NotImplementedError

    # determine normalized rms deviation and return
    normalized_rms = np.sqrt(1.0 / n_points * np.sum((data - data_ref) ** 2, axis=0)) / delta

    return normalized_rms


def c_map_comparison(c1, c2, t1, t2, nodes, tris):
    """
    Compares two c-maps in terms of NRMSD and calculates the geodesic distance between the hotspots

    Parameters
    ----------
    c1 : ndarray of float [n_ele]
        First c-map
    c2 : ndarray of float [n_ele]
        Second c-map (reference)
    t1 : ndarray of float [3]
        Coordinates of the hotspot in the first c-map
    t2 : ndarray of float [3]
        Coordinates of the hotspot in the second c-map
    nodes : ndarray of float [n_nodes x 3]
        Node coordinates
    tris : ndarray of float [n_tris x 3]
        Connectivity of ROI elements

    Returns
    -------
    nrmsd : float
        Normalized root-mean-square deviation between the two c-maps in (%)
    gdist : float
        Geodesic distance between the two hotspots in (mm)
    """

    # determine NRMSD between two c-maps
    nrmsd_ = nrmsd(array=c1, array_ref=c2, error_norm="relative", x_axis=False) * 100

    # determine geodesic distance between hotspots
    tris_center = np.mean(nodes[tris, ], axis=1)

    t1_idx = np.argmin(np.linalg.norm(tris_center - t1, axis=1))
    t2_idx = np.argmin(np.linalg.norm(tris_center - t2, axis=1))
    gdists = geodesic_dist(nodes=nodes, tris=tris, source=t2_idx, source_is_node=False)[1]
    gdist_ = gdists[t1_idx]

    return nrmsd_, gdist_
