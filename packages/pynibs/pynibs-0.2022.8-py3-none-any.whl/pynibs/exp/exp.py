import os
import csv
import copy
import h5py
import nibabel
import warnings
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from collections import OrderedDict
import xml.etree.ElementTree as ET
from fsl.transform.flirt import fromFlirt
from fsl.data.image import Image
import pynibs

try:
    from pynibs.pckg import libeep
except (ImportError, SyntaxError):
    pass


def read_exp_stimulations(fname_results_conditions, fname_simpos, filter_bad_trials=False, drop_idx=None):
    """
    Reads results_conditions.csv and simPos.csv and returns data.

    Parameters
    ----------
    fname_results_conditions : str
        Filename of results_conditions.csv file
    fname_simpos : str
        Filename of simPos.csv file
    filter_bad_trials : bool, False
        If true, some filtering will be done to exclude erroneous data
    drop_idx : list, empty
        Indices of trials to drop

    Returns
    -------
    positions_all : list of np.ndarrays of float [N_zaps x [4 x 4]]
        List of position matrices of TMS coil, formatted in simnibs style

        .. math::
           \\begin{bmatrix}
            | & | & | &  |   \\\\
            x & y & z & pos  \\\\
            | & | & | &  |   \\\\
            0 & 0 & 0 &  1   \\\\
           \\end{bmatrix}

    conditions : list of str [N_zaps]
        Str labels of the condition corresponding to each zap
    position_list : list of float and str [N_zaps x 55]
        List of data stored in results_conditions.csv (condition, MEP amplitude, locations of neuronavigation trackers)
    mep_amp : np.array of float [N_zaps]
        MEP amplitude in [V] corresponding to each zap
    intensities : np.array of float [N_zaps]
        Stimulator intensities corresponding to each zap
    fails_idx : np.array(N_fails_idx x 1) (only if filter_bad_trials)
        Which trials were dropped through filtering?
    """
    if drop_idx is None:
        drop_idx = []
    if not type(drop_idx) == list:
        drop_idx = [drop_idx]

    # store rows from file in list. each row is one list ins positionList
    position_list = []
    positionfile = fname_results_conditions
    with open(positionfile, 'rb') as positions:
        posreader = csv.reader(positions, delimiter=',', quotechar='|')
        next(posreader, None)  # skip header
        for row in posreader:
            position_list.append(row)

    # read simPos.csv file
    sim_pos_fn = fname_simpos
    sim_pos_list = []
    with open(sim_pos_fn, 'rb') as simPosFile:
        posreader = csv.reader(simPosFile, delimiter=',', quotechar='|')
        for row in posreader:
            sim_pos_list.append(row)

    conditions = [position_list[i][len(position_list[0]) - 3] for i in range(len(position_list))]
    positions_all = []
    mep_amp = [float(position_list[i][48]) for i in range(len(position_list))]

    frametime = [float(cell[54]) for cell in position_list]
    intensities = [float(position_list[i][3]) for i in range(len(position_list))]
    time_diff = [float(cell[49]) for cell in position_list]

    fails_idx = None
    if filter_bad_trials:
        # convert to masked array
        mep_amp = np.ma.array(mep_amp, mask=False)
        frametime = np.ma.array(frametime, mask=False)
        time_diff = np.ma.array(time_diff, mask=False)
        intensities = np.ma.array(intensities, mask=False)
        conditions = np.ma.array(conditions, mask=False)

        # get idx to drop
        fails_idx = np.where((mep_amp < 0) |
                             (mep_amp > 30) |
                             (frametime > 0.235) |
                             (frametime < 0.218) |
                             (intensities < 20) |
                             (time_diff > 100))[0]
        for idx in drop_idx:
            fails_idx = np.append(fails_idx, idx)

        # set drop idx to true
        intensities.mask[fails_idx] = True
        conditions.mask[fails_idx] = True
        mep_amp.mask[fails_idx] = True

        # remove drop idx from lists
        intensities = intensities.compressed()
        mep_amp = mep_amp.compressed()
        conditions = conditions.compressed()

        position_list_filtered = []
        sim_pos_list_filtered = []
        for idx in range(len(position_list)):
            if idx not in fails_idx and idx not in drop_idx:
                position_list_filtered.append(position_list[idx])
                sim_pos_list_filtered.append(sim_pos_list[idx])

        position_list = position_list_filtered
        sim_pos_list = sim_pos_list_filtered

    elif len(drop_idx) > 0 and not filter_bad_trials:
        raise NotImplementedError

    for idx, row in enumerate(position_list):
        # x to z, z to x, y to -y
        # simnibs:    02    -01    00    03    12    -11    10    13    22
        # -21    20    23    32    -31    30    33

        # results.csv 38    -37    36    39    42    -41    40    43    46
        # -45    44    47     0      0     0     1

        # intermangle results_conditions and simpos.csv...
        positions_all.append([[float(row[38]), - float(row[37]), float(row[36]), float(sim_pos_list[idx][0])],
                              [float(row[42]), - float(row[41]), float(row[40]), float(sim_pos_list[idx][1])],
                              [float(row[46]), - float(row[45]), float(row[44]), float(sim_pos_list[idx][2])],
                              [0, 0, 0, 1]])

    if filter_bad_trials:
        return positions_all, conditions, position_list, \
               np.array(mep_amp).astype(float), np.array(intensities).astype(float), fails_idx

    else:
        return positions_all, conditions, position_list, \
               np.array(mep_amp).astype(float), np.array(intensities).astype(float)


def sort_data_by_condition(conditions, return_alph_sorted=True, conditions_selected=None, *data):
    """
    Sorts data by condition and returns tuples of data with corresponding labels.

    Parameters
    ----------
    conditions : list of str [N_zaps]
        Str labels of the condition corresponding to each data
    return_alph_sorted : Boolean, Default True
        Shall returns be in alphabetically or original order
    conditions_selected: list of str or None
        List of conditions returned by the function (in this order), the others are omitted
    data : tuple of data indexed by condition [N_data x N_zaps x m]
        Data to sort

    Returns
    -------
    cond_labels : list of str [N_cond]
        Labels of conditions
    data_sorted : tuple of sorted data [N_cond x N_data x N_zaps x m]
        Sorted data by condition
    """

    # sorts condition labels alphabetically (return idx to redo it optionally)
    cond_labels, idx = np.unique(conditions, return_index=True)

    n_data = len(data)

    data_sorted = []
    temp = []

    # loop over cond_labels (sorted alphabetically) or conditions[idx] (sorted in original order)
    if not return_alph_sorted:
        cond_labels = np.array(conditions)[np.sort(idx)]

    for i in range(n_data):
        for cond in cond_labels:
            mask = [idx for idx in range(len(conditions)) if conditions[idx] == cond]
            temp.append(data[i][mask,])
        data_sorted.append(temp)
        temp = []

    if conditions_selected:
        data_sorted_selected = [[0 for _ in range(len(conditions_selected))] for __ in range(n_data)]

        for i_data in range(n_data):
            for i_cond, c in enumerate(conditions_selected):
                for i_cond_all in range(len(cond_labels)):
                    if cond_labels[i_cond_all] == c:
                        data_sorted_selected[i_data][i_cond] = data_sorted[i_data][i_cond_all]

        return conditions_selected, data_sorted_selected
    else:
        return cond_labels, data_sorted


# TODO: @Lucas: Bitte dokumentieren
def outliers_mask(data, m=2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    return s < m


def square(x, a, b, c):
    """
    Parametrized quadratic function

    .. math::
        y = ax^2+bx+c

    Parameters
    ----------
    x : nparray of float [N_x]
        X-values the function is evaluated in
    a : float
        Slope parameter of x^2
    b : float
        Slope parameter of x
    c : float
        Offset parameter

    Returns
    -------
    y : nparray of float [N_x]
        Function value at argument x
    """
    y = a * x ** 2 + b * x + c
    return y


def splitext_niigz(fn):
    """
    Splitting extension(s) from .nii or .nii.gz file

    Parameters
    ----------
    fn : str
        Filename of input image .nii or .nii.gz file

    Returns
    -------
    path : str
        Path and filename without extension(s)
    ext : str
        Extension, either .nii or .nii.gz
    """

    path, filename = os.path.split(fn)

    file0, ext0 = os.path.splitext(filename)

    if ext0 == '.gz':
        file1, ext1 = os.path.splitext(file0)
        return os.path.join(path, file1), ext1 + ext0
    elif ext0 == '.nii':
        return os.path.join(path, file0), ext0
    else:
        raise Exception('File extension is neither .nii or .nii.gz!')


def toRAS(fn_in, fn_out):
    """
    Transforming MRI .nii image to RAS space.

    Parameters
    ----------
    fn_in : str
        Filename of input image .nii file
    fn_out : str
        Filename of output image .nii file in RAS space

    Returns
    -------
    <File> : .nii file
        .nii image in RAS space (fn_out)
    """

    # read image data
    img_in = nibabel.load(fn_in)
    img_in_hdr = img_in.header
    img_out = copy.deepcopy(img_in)

    # read and invert q-form of original image
    m_qform_in = img_in.get_qform()
    m_qform_inv_in = np.linalg.inv(m_qform_in)

    # identify axes to flip
    mathlp = np.sign(m_qform_inv_in)

    ras_dim = np.zeros(3)
    ras_sign = np.zeros(3)

    for i in range(3):
        ras_dim[i] = np.where(np.abs(m_qform_inv_in[:, i]) == np.max(np.abs(m_qform_inv_in[:, i])))[0]
        ras_sign[i] = mathlp[int(ras_dim[i]), i]

    ras_dim = ras_dim.astype(int)

    # apply sorting to qform: first permute, then flip
    m_perm = np.zeros((4, 4))
    m_perm[3, 3] = 1

    for i in range(3):
        m_perm[ras_dim[i], i] = 1

    imgsize = img_in_hdr['dim'][1:4]
    imgsize = imgsize[ras_dim]

    m_flip = np.eye(4)

    for i in range(3):
        if ras_sign[i] < 0:
            m_flip[i, i] = -1
            m_flip[i, 3] = imgsize[i] - 1

    m_qform_out = np.dot(np.dot(m_qform_in, m_perm), m_flip)
    img_out.set_qform(m_qform_out)
    img_out.set_sform(m_qform_out)
    # m_toORG = np.dot(m_perm, m_flip)

    # apply sorting to image: first permute, then flip
    img_out_data = np.transpose(img_in.get_data(), ras_dim)

    for i in range(3):
        if ras_sign[i] < 0:
            img_out_data = np.flip(img_out_data, i)

    # save transformed image in .nii file
    img_out = nibabel.Nifti1Image(img_out_data, img_out.affine, img_out.header)
    nibabel.save(img_out, fn_out)


def get_coil_flip_m(source_system='simnibs', target_system=None):
    """
    Returns a flimp matrix 4x4 to flip coil axis from one system to another.

    Parameters
    ----------
    source_system : str
        Atm only possible source: 'simnibs'
    target_system :
        tmsnavigator, visor, brainsight

    Returns
    -------
    flip_m : np.ndarray
        shape: 4x4
    """
    if source_system.lower() == 'simnibs':
        if target_system.lower() in ["localite", "tmsnavigator"]:
            return np.array([[0, 0, 1, 0],
                             [0, -1, 0, 0],
                             [1, 0, 0, 0],
                             [0, 0, 0, 1]])

        elif target_system.lower() == "visor":
            return np.array([[-1, 0, 0, 0],
                             [0, 1, 0, 0],
                             [0, 0, -1, 0],
                             [0, 0, 0, 1]])

        elif target_system.lower() == "brainsight":
            return np.array([[-1, 0, 0, 0],
                             [0, 1, 0, 0],
                             [0, 0, -1, 0],
                             [0, 0, 0, 1]])

        else:
            raise NotImplementedError(
                    "Neuronavigation system: {} not implemented! ('tmsnavigator', 'Visor' or 'brainsight')".format(
                            target_system))

    raise NotImplementedError(
            "Source system: {} not implemented! ('simnibs')".format(source_system))


def nnav2simnibs(fn_exp_nii, fn_conform_nii, m_nnav, nnav_system, mesh_approach="headreco",
                 fiducials=None, orientation='RAS', fsl_cmd=None, target='simnibs', temp_dir=None, rem_tmp=False,
                 verbose=False):
    """
    Transforming TMS coil positions from neuronavigation to simnibs space

    Parameters
    ----------
    fn_exp_nii : str
        Filename of .nii file the experiments were conducted with
    fn_conform_nii: str
        Filename of .nii file from SimNIBS mri2msh function
        (e.g.: .../fs_subjectID/subjectID_T1fs_conform.nii.gz)
    m_nnav : nparray [4 x 4 x N]
        Position matrices from neuronavigation
    nnav_system : str
        Neuronavigation system:
        - "Localite" ... Localite neuronavigation system
        - "Visor" ... Visor neuronavigation system from ANT
        - "Brainsight" ... Brainsight neuronavigation system from Rougue Research
    mesh_approach : str, optional, default: "headreco"
        Approach the mesh is generated with ("headreco" or "mri2mesh")
    fiducials : np.array of float [3 x 3]
        Fiducial points in ANT nifti space from file
        (e.g.: /data/pt_01756/probands/33791.b8/exp/1/33791.b8_recording/MRI/33791.b8_recording.mri)
        (x frontal-occipital, y right-left, z inferior-superior)
        VoxelOnPositiveXAxis (Nasion, first row)
        221	131	127
        VoxelOnPositiveYAxis (left ear, second row)
        121	203	105
        VoxelOnNegativeYAxis (right ear, third row)
        121	57	105
    orientation : str
        Orientation convention ('RAS' or 'LPS')
        (can be read from neuronavigation .xml file under coordinateSpace="RAS")
    fsl_cmd : str
        bash command to start FSL environment (Default: FSL)
    target : str, optional, default: 'simnibs'
        Either transform to 'simnibs' or to 'nnav' space
    temp_dir : str, optional, default: None (fn_exp_mri_nii folder)
        Directory to save temporary files (transformation .nii and .mat files)
    rem_tmp : bool, optional, default: False
        Remove temporary files from registration
    verbose : boolean
        Print output (True / False)

    Returns
    -------
    m_simnibs : nparray of float [4 x 4 x N]
    """
    # assumes that the script is called within FSL environment, otherwise this function starts FSL
    # with 'fsl_cmd' and executes some FSL functions for coregistration
    if fsl_cmd is None:
        fsl_cmd = 'FSL'

    if temp_dir is None:
        temp_dir = os.path.split(fn_exp_nii)[0]

    assert target in ['nnav', 'simnibs']
    # get original qform without RAS
    exp_nii_original = nibabel.load(fn_exp_nii)
    conform_nii_original = nibabel.load(fn_conform_nii)
    m_qform_exp_original = exp_nii_original.get_qform()
    m_qform_conform_original = conform_nii_original.get_qform()

    # check if conform_nii and exp_nii are the same and have the same q-form
    skip_flirt = np.all((np.isclose(m_qform_conform_original, m_qform_exp_original)))

    fn_exp_nii_ras = os.path.join(temp_dir,
                                  os.path.split(splitext_niigz(fn_exp_nii)[0] +
                                                '_RAS' +
                                                splitext_niigz(fn_exp_nii)[1])[1])

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # transform exp to RAS
    toRAS(fn_exp_nii, fn_exp_nii_ras)

    # load .nii files
    if verbose:
        print('Loading .nii files:')
        print((' > {}'.format(fn_exp_nii_ras)))
        # print((' > {}'.format(fn_conform_nii)))
    exp_nii = nibabel.load(fn_exp_nii_ras)
    # conform_nii = nibabel.load(fn_conform_nii)

    if verbose:
        print('Gathering header information...')
    # extract header information
    # conform_hdr = conform_nii.header
    # exp_hdr = exp_nii.header

    # read q-form matrix from exp
    # if verbose:
    #     print('Constructing transformation matrices:')
    #     print(' > q-form matrix of exp')
    # m_qform_exp = exp_nii.get_qform()

    # read q-form matrix from conform
    # m_qform_conform = conform_nii.get_qform()

    # # invert q-form matrix
    # if verbose:
    #     print(' > inverse q-form matrix of exp')
    # if mesh_approach != "headreco":
    # m_qform_exp_inv = np.linalg.inv(m_qform_exp)
    # else:
    #     m_qform_exp_inv = np.eye(4)

    # construct m_vox2mm matrix from exp
    # if verbose:
    #     print(' > vox2mm matrix of exp')
    # pixdim_exp = exp_hdr['pixdim'][1:4]
    # m_vox2mm = np.eye(4)
    #
    # for i in range(3):
    #     m_vox2mm[i, i] = pixdim_exp[i]

    # construct flirt2fs matrix
    # if verbose:
    #     print(' > flirt2fs matrix of conform')
    # pixdim_conform = conform_hdr['pixdim'][1:4]
    # dim_conform = conform_hdr['dim'][1:4]
    # m_flirt2fs = np.eye(4)

    # if mesh_approach != "headreco":
    # m_flirt2fs[0, 3] = -pixdim_conform[0] * (dim_conform[0] / 2.0 - 1)
    # m_flirt2fs[1, 3] = -pixdim_conform[1] * (dim_conform[1] / 2.0)
    # m_flirt2fs[2, 3] = -pixdim_conform[2] * (dim_conform[2] / 2.0 - 1)

    # construct flip matrix
    if verbose:
        print(' > flip matrix')

    m_flip = get_coil_flip_m(target_system=nnav_system)

    # construct flip matrix
    if verbose:
        print(' > RAS matrix')
    if orientation != 'RAS':
        raise NotImplementedError(f"Orientation {orientation} not implemented.")

    # construct flirt transformation matrix if necessary
    if verbose:
        print(' > flirt transformation matrix')
    if skip_flirt:
        if verbose:
            print('    - experimental and simnibs .nii files are equal... Accelerating process')
        m_exp2conf = np.eye(4)

    else:
        if verbose:
            print('    - starting coregistration of exp and conform .nii images')
        fn_flip = os.path.join(temp_dir, os.path.split(splitext_niigz(fn_exp_nii_ras)[0] + '_flipped_temp.nii')[1])
        fn_out_fslmaths = os.path.join(temp_dir, os.path.split(splitext_niigz(fn_conform_nii)[0] +
                                                               '_binarized_temp')[1])
        fn_mat_m_2conform = os.path.join(temp_dir,
                                         os.path.split(splitext_niigz(fn_exp_nii_ras)[0] + '_m_2conform_temp')[1])
        dof = 6

        # define binarization threshold on the image. .80 seems to work.
        # thresh = np.quantile(conform_nii.get_data(), 0.80)

        # flip image of exp along first dimension and save it (to LAS, radiologic)
        data_exp_flipped = np.flip(exp_nii.get_data(), axis=0)
        exp_flipped_nii = nibabel.Nifti1Image(data_exp_flipped, exp_nii.affine, exp_nii.header)
        nibabel.save(exp_flipped_nii, fn_flip)

        # call FSL to align exp to conform
        if not os.path.exists(fn_mat_m_2conform + '.mat'):
            cmdstr = ['' for _ in range(3)]
            cmdstr[0] = fsl_cmd + ' fslorient -setqformcode 1 ' + fn_flip
            cmdstr[1] = fsl_cmd + ' fslorient -forceradiological ' + fn_flip
            # this doesn't work stable for all images
            # cmdstr[2] = f'{fsl_cmd} fslmaths {fn_conform_nii} -thr {thresh} -bin -s 1 {fn_out_fslmaths}.nii.gz'
            cmdstr[2] = f'{fsl_cmd} flirt -in {fn_flip} -ref {fn_conform_nii} ' \
                        f' -searchrx -30 30 ' \
                        f'-searchry -30 30 -searchrz -30 30  -interp sinc ' \
                        f'-cost mutualinfo -searchcost mutualinfo -dof {str(dof)} ' \
                        f'-omat {fn_mat_m_2conform}.mat -out {fn_mat_m_2conform}.nii.gz'

            # execute FSL commands
            if verbose:
                print('    - Executing:')
            for i in range(len(cmdstr)):
                if verbose:
                    print(('     > {}'.format(cmdstr[i])))
                os.system(cmdstr[i])

        m_2conform = np.loadtxt(f'{fn_mat_m_2conform}.mat')

        exp_ras_img = Image(fn_exp_nii_ras)
        conform_img = Image(fn_conform_nii)

        m_exp2conf = fromFlirt(m_2conform, exp_ras_img, conform_img, from_='world', to='world')

        if rem_tmp:
            for f in [fn_exp_nii_ras,
                      f'{fn_mat_m_2conform}.mat',
                      f'{fn_mat_m_2conform}.nii.gz',
                      f"{fn_out_fslmaths}.nii.gz",
                      fn_flip]:
                try:
                    os.unlink(f)
                except FileNotFoundError:
                    print(f"Cannot remove {f}: File not found.")

    # if nnav_system.lower() == "brainsight":
    #     m_brainsight2simnibs = np.array([[-1, 0, 0, 0],
    #                                      [0, -1, 0, 0],
    #                                      [0, 0, 1, 0],
    #                                      [0, 0, 0, 1]])
    #     m_brainsight2simnibs = np.dot(m_brainsight2simnibs, exp_nii.affine)
    #     # m_brainsight2simnibs = np.dot(np.linalg.inv(exp_nii.affine), m_brainsight2simnibs)
    #     m_exp2conf = np.dot(m_exp2conf, m_brainsight2simnibs)

    # apply the exp2conf matrix to the data...
    if target == 'nnav':
        m_exp2conf = np.linalg.inv(m_exp2conf)
    m_simnibs = np.dot(np.dot(m_exp2conf, m_nnav.transpose([2, 0, 1])).transpose([1, 0, 2]),
                       m_flip).transpose([1, 2, 0])  # ...and the coil axis flip
    # TODO: check transformation for conform == exp
    #       check headreco and mri2mesh meshes

    return m_simnibs


def add_sigmoidal_bestfit(mep, p0, constraints=None):
    """
    Add best fitting sigmoidal function to instance (determined by multistart approach)

    Parameters
    ----------
    mep : pynibs.Mep
        Mep object class instance
    p0 : float
    constraints : dict
        Dictionary with parameter names as keys and [min, max] values as constraints

    Returns
    -------
    mep : object
        Updated Mep object class instance with the following attributes

    Notes
    -----
    Adds Attributes

    Mep.fun_sig : function
        Sigmoid function
    Mep.popt_sig : nparray of float [3]
        Parameters of sigmoid function
    """

    # p0 = [70, 0.6, 1]

    # if mep.fun == sigmoid:
    #     mep.fun_sig = sigmoid
    #     mep.popt_sig = copy.deepcopy(mep.popt)
    #
    # else:
    mep.fun_sig = pynibs.sigmoid

    x = np.linspace(mep.x_limits[0], mep.x_limits[1], 100)
    y = mep.eval(x, mep.popt)

    mep.fit_sig = mep.run_fit_multistart(pynibs.sigmoid, x=x, y=y, p0=p0, constraints=constraints)

    # get names of arguments of function
    argnames = pynibs.sigmoid.__code__.co_varnames[1:pynibs.sigmoid.__code__.co_argcount]

    # read out optimal function parameters from best fit
    mep.popt_sig = []

    for i in range(len(argnames)):
        mep.popt_sig.append(mep.fit_sig.best_values[argnames[i]])

    mep.popt_sig = np.asarray(mep.popt_sig)
    mep.cvar_sig = mep.fit_sig.covar
    mep.pstd_sig = np.sqrt(np.diag(mep.cvar_sig))

    return mep


def get_cnt_infos(fn_cnt):
    """
    Read some meta information from .cnt file

    Returns
    -------
    dict d

    """
    f = libeep.read_cnt(fn_cnt)
    d = dict()
    d['sampling_rate'] = f.get_sample_frequency()
    d['trigger_count'] = f.get_trigger_count()
    d['sample_count'] = f.get_sample_count()
    d['channel_count'] = f.get_channel_count()
    d['channel_names'] = [f.get_channel(i)[0].lower() for i in range(d['channel_count'])]

    return d


def get_coil_sn_lst(fn_coil):
    coil_sn_lst = []
    for coil_path_str_lst in fn_coil:
        coil_sn_lst.append(coil_path_str_lst[0][-8:-4])
    return coil_sn_lst


# def calc_p2p(sweep):
#     """
#     Calc peak-to-peak values of an mep sweep.
#
#     Parameters
#     ----------
#     sweep : np.array of float [Nx1]
#         Input curve
#
#     Returns
#     -------
#     p2p : float
#         Peak-to-peak value of input curve
#     """
#
#     # Filter requirements.
#     order = 6
#     fs = 16000  # sample rate, Hz
#     cutoff = 2000  # desired cutoff frequency of the filter, Hz
#
#     # Get the filter coefficients so we can check its frequency response.
#     # import matplotlib.pyplot as plt
#     # b, a = butter_lowpass(cutoff, fs, order)
#     #
#     # # Plot the frequency response.
#     # w, h = freqz(b, a, worN=8000)
#     # plt.subplot(2, 1, 1)
#     # plt.plot(0.5 * fs * w / np.pi, np.abs(h), 'b')
#     # plt.plot(cutoff, 0.5 * np.sqrt(2), 'ko')
#     # plt.axvline(cutoff, color='k')
#     # plt.xlim(0, 0.5 * fs)
#     # plt.title("Lowpass Filter Frequency Response")
#     # plt.xlabel('Frequency [Hz]')
#     # plt.grid()
#
#     sweep_filt = butter_lowpass_filter(sweep, cutoff, fs, order)
#
#     # get indices for max
#     index_max_begin = np.argmin(sweep) + 40  # get TMS impulse # int(0.221 / 0.4 * sweep.size)
#     index_max_end = sweep_filt.size  # int(0.234 / 0.4 * sweep.size) + 1
#     if index_max_begin >= index_max_end:
#         index_max_begin = index_max_end-1
#     # index_max_end = index_max_begin + end_mep
#
#     # get maximum and max index
#     sweep_max = np.amax(sweep_filt[index_max_begin:index_max_end])
#     sweep_max_index = index_max_begin + np.argmax(sweep_filt[index_max_begin:index_max_end])
#
#     # if list of indices then get last value
#     if sweep_max_index.size > 1:
#         sweep_max_index = sweep_max_index[0]
#
#     # get minimum and mix index
#     index_min_begin = sweep_max_index  # int(sweep_max_index + 0.002 / 0.4 * sweep_filt.size)
#     index_min_end = sweep_max_index + 40  # int(sweep_max_index + 0.009 / 0.4 * sweep_filt.size) + 1
#
#     # Using the same window as the max should make this more robust
#     # index_min_begin = index_max_begi
#     sweep_min = np.amin(sweep_filt[index_min_begin:index_min_end])
#
#     return sweep_max - sweep_min


def match_behave_and_triggermarker(mep_time_lst, xml_paths, bnd_factor=0.99 / 2, isi=None):
    """
    Sort out timestamps of mep and tms files that do not match.

    Parameters
    ----------
    mep_time_lst : list of datetime.timedelta
        timedeltas of MEP recordings.
    xml_paths : list of str
        Paths to coil0-file and optionally coil1-file if there is no coil1-file, use empty string
    bnd_factor : float, optional, default: 0.99/2
        Bound factor relative to interstimulus interval in which +- interval to match neuronavigation and mep data
        from their timestamps. (0 means perfect matching, 0.5 means +- half interstimulus interval)
    isi : float, optional.
        Interstimulus intevals. Of not provided it's estimated from the first trial.

    Returns
    -------
    tms_index_lst : list of int
        Indices of tms-timestamps that match
    mep_index_lst : list of int
        Indices of mep-timestamps that match
    tms_time_lst : list of datetime
        TMS timstamps
    """
    # mep_time_lst = []
    # for cfs_path in cfs_paths:
    #     _, mep_time_lst_tmp = get_mep_elements(cfs_path, tms_pulse_time)
    #     mep_time_lst.extend(mep_time_lst_tmp)

    _, tms_ts_lst, _, tms_idx_invalid = pynibs.get_tms_elements(xml_paths, verbose=True)

    # get timestamp difference of mep measurements
    if isi is None:
        isi = (mep_time_lst[1] - mep_time_lst[0]).total_seconds()

    # get offset to match first timestamps of mep and tms
    coil_offset = datetime.timedelta(seconds=float(tms_ts_lst[0]) / 1000)

    # match start time with the timestamp of the xml file
    # tms_time_lst = [mep_time_lst[0] - time_offset + datetime.timedelta(seconds=float(ts) / 1000) for ts in tms_ts_lst]
    coil_time_delta_lst = [-coil_offset + datetime.timedelta(seconds=float(ts) / 1000) for ts in tms_ts_lst]
    coil_time_delta_lst_orig = [-coil_offset + datetime.timedelta(seconds=float(ts) / 1000) for ts in tms_ts_lst]

    # get index for cfs and xml files
    # mep_time_index, mep_index_lst = 0, []
    # tms_time_index, tms_index_lst = 0, []

    # get maximal list length of time lists
    # min_lst_length = min([len(lst) for lst in [mep_time_lst, tms_time_delta_lst]])

    # mep_last_working_idx = 0
    # tms_last_working_idx = 0

    if (len(coil_time_delta_lst) + len(tms_idx_invalid)) == len(mep_time_lst):
        print("Equal amount of TMS and MEP data...")
        print(f"Removing invalid coil positions {tms_idx_invalid} from MEP data...")

        # invalid coil positions were already removed in previous call of get_tms_elements(xml_paths)
        coil_to_mep_match_lst = [i for i in range(len(tms_ts_lst))]

        # MEP indices without invalid coil positions
        mep_index_lst = [i for i in range(len(mep_time_lst)) if i not in tms_idx_invalid]

    else:
        mep_index_lst = []
        coil_to_mep_match_lst = []
        mep_time_lst = np.array(mep_time_lst)
        coil_time_delta_lst = np.array(coil_time_delta_lst)

        # iterate over all MEPs
        for mep_index in range(len(mep_time_lst)):
            # set bounds
            time_bnd_l = mep_time_lst[mep_index] + datetime.timedelta(
                    seconds=-isi * bnd_factor)  # time bound low
            time_bnd_h = mep_time_lst[mep_index] + datetime.timedelta(
                    seconds=+isi * bnd_factor)  # time bound high

            # search for corresponding TMS coil positions
            coil_mep_in_bound = (time_bnd_l <= coil_time_delta_lst) & (coil_time_delta_lst <= time_bnd_h)

            # no TMS coil position in bound (untracked coil position already removed)
            if np.sum(coil_mep_in_bound) == 0:
                print(f"Untracked coil position, excluding MEP_idx: {mep_index}")

            # one correct TMS coil position in bound
            elif np.sum(coil_mep_in_bound) == 1:
                mep_index_lst.append(mep_index)
                coil_match_index = np.where(coil_mep_in_bound)[0][0]
                coil_to_mep_match_lst.append(coil_match_index)

                # zero times on last match to avoid time shift
                mep_time_lst -= mep_time_lst[mep_index]
                coil_time_delta_lst -= coil_time_delta_lst[coil_match_index]

            # one correct and one accidental TMS coil position in bound -> take closest
            elif np.sum(coil_mep_in_bound) > 1:
                mep_index_lst.append(mep_index)
                delta_t = np.abs(np.array([mep_time_lst[mep_index] for _ in range(np.sum(coil_mep_in_bound))]) -
                                 np.array(coil_time_delta_lst)[coil_mep_in_bound])
                coil_match_index = np.where(coil_mep_in_bound)[0][np.argmin(delta_t)]
                coil_to_mep_match_lst.append(coil_match_index)

                print(f"Two tracked TMS coil positions found within search window -> choosing closest index by time.")
                print(
                        f"MEP_idx: {mep_index} ({mep_time_lst[mep_index]}) -> "
                        f"TMS_idx: {coil_match_index} ({coil_time_delta_lst[coil_match_index]})")

                # zero times on last match
                mep_time_lst -= mep_time_lst[mep_index]
                coil_time_delta_lst -= coil_time_delta_lst[coil_match_index]

    return [coil_to_mep_match_lst, mep_index_lst, coil_time_delta_lst_orig]


def print_time(relation, tms_time, tms_time_index, mep_time, mep_time_index, time_bnd_l, time_bnd_h):
    """
    Print timestamps that do not match.

    Parameters
    ----------
    relation : str
        'bigger' or 'smaller'
    tms_time : datetime.timedelta
        TMS timestamps
    tms_time_index : int
        Index of tms timestamp
    mep_time : datetime.timedelta
        Mep timestamps
    mep_time_index : int
        Index of mep timestamps
    time_bnd_l : datetime.timedelta
        Lowest datetime timestamp for matching
    time_bnd_h : datetime.timdelta
        Highest datetime timestamp for matching
    """

    if relation == 'bigger':
        print('tms_time is bigger. Difference: {}s. TMS Nav idx: {}. MEP idx: {}'.format(
                (tms_time - mep_time).total_seconds(),
                tms_time_index,
                mep_time_index))
        print("  ({} > {} [{} - {})".format(tms_time,
                                            mep_time,
                                            time_bnd_l,
                                            time_bnd_h))
    if relation == 'smaller':
        print('tms_time is smaller. Difference: {}s. TMS Nav idx: {}. MEP idx: {}'.format(
                (tms_time - mep_time).total_seconds(),
                tms_time_index,
                mep_time_index))
        print("  ({} < {} [{} - {})".format(tms_time,
                                            mep_time,
                                            time_bnd_l,
                                            time_bnd_h))
    return 0


def combine_nnav_mep(xml_paths, cfs_paths, im, coil_sn,
                     nii_exp_path, nii_conform_path,
                     patient_id, tms_pulse_time, drop_mep_idx, mep_onsets, nnav_system, mesh_approach="headreco",
                     temp_dir=None, cfs_data_column=0, channels=None, plot=False):
    """
    Creates dictionary containing all experimental data.

    Parameters
    ----------
    xml_paths : list of str
        Paths to coil0-file and optionally coil1-file if there is no coil1-file, use empty string
    cfs_paths : list of str
        Paths to .cfs mep file
    im : list of str
        List of path to the instrument-marker-file or list of strings containing the instrument marker
    coil_sn : str
        Coil-serial-number
    nii_exp_path : str
        Path to the .nii file that was used in the experiment
    nii_conform_path : str
        Path to the conform*.nii file used to calculate the E-fields with SimNIBS
    patient_id : str
        Patient id
    tms_pulse_time : float
        Time in [s] of TMS pulse as specified in signal
    drop_mep_idx : List of int or None
        Which MEPs to remove before matching.
    mep_onsets : List of int or None (Default: None)
        If there are multiple .cfs per TMS Navigator sessions, onsets in [ms] of .cfs. E.g.: [0, 71186].
    temp_dir : str, optional, default: None (fn_exp_mri_nii folder)
        Directory to save temporary files (transformation .nii and .mat files)
    cfs_data_column : int or list of int
        Column(s) of dataset in .cfs file.
    channels : list of str, optional, default: None
        Channel names
    nnav_system : str
        Type of neuronavigation system ("Localite", "Visor")
    mesh_approach : str, optional, default: "headreco"
        Approach the mesh is generated with ("headreco" or "mri2mesh")
    plot : bool, optional, default: False
        Plot MEPs and p2p evaluation

    Returns
    -------
    dict_lst : list of dicts, one dict for each zap
          'number'
          'condition'
          'current'
          'mep_raw_data'
          'mep'
          'mep_latency'
          'mep_filt_data'
          'mep_raw_data_time'
          'time_tms'
          'ts_tms'
          'time_mep'
          'date'
          'coil_sn'
          'patient_id'
    """

    # get arrays and lists
    coil_array, ts_tms_lst, current_lst, tms_idx_invalid = pynibs.get_tms_elements(xml_paths, verbose=False)

    # get MEP amplitudes from .cfs files
    time_mep_lst, mep_latencies = [], []
    last_mep_onset = datetime.timedelta(seconds=0)
    mep_raw_data, mep_filt_data, p2p_arr = None, None, None

    if not isinstance(cfs_paths, list):
        cfs_paths = [cfs_paths]

    for idx, cfs_path in enumerate(cfs_paths):
        # calc MEP amplitudes and MEP onset times from .cfs file
        p2p_array_tmp, time_mep_lst_tmp, \
        mep_raw_data_tmp, mep_filt_data_tmp, \
        mep_raw_data_time, mep_latency = pynibs.get_mep_elements(mep_fn=cfs_path,
                                                                 tms_pulse_time=tms_pulse_time,
                                                                 drop_mep_idx=drop_mep_idx,
                                                                 cfs_data_column=cfs_data_column,
                                                                 channels=channels,
                                                                 plot=plot)

        # add .cfs onsets from subject object and add onset of last mep from last .cfs file
        if mep_onsets is not None:
            time_mep_lst_tmp = [time_mep_lst_tmp[i] + datetime.timedelta(milliseconds=mep_onsets[idx]) +
                                last_mep_onset for
                                i in range(len(time_mep_lst_tmp))]
        time_mep_lst.extend(time_mep_lst_tmp)

        if idx == 0:
            p2p_arr = p2p_array_tmp
            mep_raw_data = mep_raw_data_tmp
            mep_filt_data = mep_filt_data_tmp
            mep_latencies = mep_latency
        else:
            mep_raw_data = np.vstack((mep_raw_data, mep_raw_data_tmp))
            mep_filt_data = np.vstack((mep_filt_data, mep_filt_data_tmp))
            p2p_arr = np.concatenate((p2p_arr, p2p_array_tmp), axis=1)
            mep_latencies.append(mep_latency)

        last_mep_onset = time_mep_lst[-1]
    mep_latencies = np.array(mep_latencies)

    # match TMS Navigator zaps and MEPs
    tms_index_lst, mep_index_lst, time_tms_lst = match_behave_and_triggermarker(mep_time_lst=time_mep_lst,
                                                                                xml_paths=xml_paths,
                                                                                bnd_factor=0.99 / 2)  # 0.99/2

    if cfs_paths[0].endswith("cfs"):
        experiment_date_time = pynibs.get_time_date(cfs_paths)
    else:
        experiment_date_time = "N/A"

    # get indices of not recognizable coils
    unit_matrix_index_list = []
    for unit_matrix_index1 in range(coil_array.shape[0]):
        for unit_matrix_index2 in range(coil_array.shape[1]):
            if np.allclose(coil_array[unit_matrix_index1, unit_matrix_index2, :, :], np.identity(4)):
                unit_matrix_index_list.append([unit_matrix_index1, unit_matrix_index2])

    # set condition names in case of random sampling
    if im is None or im == [""] or im == "":
        coil_cond_lst = [str(i) for i in range(len(ts_tms_lst))]
        drop_idx = []
    else:
        # get conditions from instrument markers
        if os.path.isfile(im[0]):
            coil_cond_lst, drop_idx = pynibs.match_instrument_marker_file(xml_paths, im[0])
        else:
            coil_cond_lst, drop_idx = pynibs.match_instrument_marker_string(xml_paths, im)

    # coordinate transform (for coil_0, coil_1, coil_mean)
    for idx in range(coil_array.shape[0]):
        # move axis, calculate and move back
        m_simnibs = np.moveaxis(coil_array[idx, :, :, :], 0, 2)
        m_simnibs = nnav2simnibs(fn_exp_nii=nii_exp_path[0],
                                 fn_conform_nii=nii_conform_path,
                                 m_nnav=m_simnibs,
                                 nnav_system=nnav_system,
                                 mesh_approach=mesh_approach,
                                 temp_dir=temp_dir)

        coil_array[idx, :, :, :] = np.moveaxis(m_simnibs, 2, 0)

    # replace transformed identity matrices
    for unit_matrix_indices in unit_matrix_index_list:
        coil_array[unit_matrix_indices[0], unit_matrix_indices[1], :, :] = np.identity(4)

    # list for dictionaries
    dict_lst = []
    idx = 0

    assert len(tms_index_lst) == len(mep_index_lst)

    delta_t = []
    ts_mep = [time_mep_lst[i] for i in mep_index_lst]
    ts_tms = [time_tms_lst[i] for i in tms_index_lst]

    for t1, t2 in zip(ts_mep, ts_tms):
        # print(f"MEP: {t1}     TMS: {t2}")
        delta_t.append(np.abs(t1 - t2))

    plt.plot(np.array([delta_t[i].microseconds for i in range(len(delta_t))]) / 1000)
    plt.xlabel("TMS pulse #", fontsize=11)
    plt.ylabel("$\Delta t$ in ms", fontsize=11)
    fn_plot = os.path.join(os.path.split(cfs_paths[0])[0], "delta_t_mep_vs_tms.png")
    plt.savefig(fn_plot, dpi=600)
    plt.close()

    # iterate over mep and tms indices to get valid matches of MEPs and TMS Navigator information
    for tms_index, mep_index in zip(tms_index_lst, mep_index_lst):
        if tms_index not in drop_idx:
            dictionary = {'number': idx,
                          'condition': coil_cond_lst[tms_index],
                          'current': current_lst[tms_index],
                          'mep_raw_data': mep_raw_data[:, mep_index, :],
                          'mep': p2p_arr[:, mep_index],
                          'mep_latency': mep_latencies[:, mep_index],
                          'mep_filt_data': mep_filt_data[:, mep_index, :],
                          'mep_raw_data_time': mep_raw_data_time,
                          'time_tms': time_tms_lst[tms_index].total_seconds(),
                          'ts_tms': ts_tms_lst[tms_index],
                          'time_mep': time_mep_lst[mep_index].total_seconds(),
                          'date': experiment_date_time,
                          'coil_sn': coil_sn,
                          'patient_id': patient_id}

            # write coils
            for index1 in range(4):
                for index2 in range(4):
                    dictionary.update({'coil0_' + str(index1) + str(index2): coil_array[0, tms_index, index1, index2]})
                    dictionary.update({'coil1_' + str(index1) + str(index2): coil_array[1, tms_index, index1, index2]})
                    dictionary.update(
                            {'coil_mean_' + str(index1) + str(index2): coil_array[2, tms_index, index1, index2]})

            # get time difference
            time_diff = time_tms_lst[tms_index] - time_mep_lst[mep_index]
            time_diff = time_diff.total_seconds() * 1000
            dictionary.update({'time_diff': time_diff})

            # append to list
            dict_lst.append(dictionary)

            idx += 1

    return dict_lst


def get_trial_data_from_csv(behavior_fn, cond, drop_trial_idx=None, only_corr=True, startatzero=True):
    """
    Reads trial data from csv file.
    Reaction time is in [0.1ms]

    Parameters
    ----------
     behavior_fn : str
        Filename with columns: 'trialtype', 'onset_time', 'rt'
    cond : str
        Which condition to choose from .csv file
    drop_trial_idx : list of int, optional
        'trialnum' to remove
    only_corr : bool, default: True
        Only return trials with correct responses
    startatzero : bool, default: True
        Shift onset_time axis to zero

    Returns
    -------
    rt : list of float
    onsets : list of float
    mean_isi : tuple of int
        in [s]
    """

    if drop_trial_idx is None:
        drop_trial_idx = []

    data = pd.read_csv(behavior_fn)

    if startatzero:
        data['onset_time'] = data['onset_time'] - data['onset_time'].values[0]

    # remove some predefined trials
    for drop in drop_trial_idx:
        data = data[data['trialnum'] != drop]

    # remove incorrect trials
    if only_corr:
        data = data[data['wrong'] == 0]

    # subset to condition of interest
    data = data[data['trialtype'] == cond]

    mean_isi = data['isi'].mean()
    rt = data['rt'].to_list()
    onsets = data['onset_time'].to_list()

    return rt, onsets, mean_isi / 1000


def combine_nnav_rt(xml_paths, behavior_paths, im, coil_sn,
                    nii_exp_path, nii_conform_path,
                    patient_id, drop_trial_idx, nnav_system, cond,
                    mesh_approach="headreco", temp_dir=None, plot=False):
    """
    Creates dictionary containing all experimental data.

    Parameters
    ----------
    xml_paths : list of str
        Paths to coil0-file and optionally coil1-file if there is no coil1-file, use empty string
    behavior_paths : list of str
        Paths to .cfs mep file
    im : list of str
        List of path to the instrument-marker-file or list of strings containing the instrument marker
    coil_sn : str
        Coil-serial-number
    nii_exp_path : str
        Path to the .nii file that was used in the experiment
    nii_conform_path : str
        Path to the conform*.nii file used to calculate the E-fields with SimNIBS
    patient_id : str
        Patient id
    drop_trial_idx : List of int or None
        Which MEPs to remove before matching.
    temp_dir : str, optional, default: None (fn_exp_mri_nii folder)
        Directory to save temporary files (transformation .nii and .mat files)
    nnav_system : str
        Type of neuronavigation system ("Localite", "Visor")
    cond : str
        Condition name in data_path
    mesh_approach : str, optional, default: "headreco"
        Approach the mesh is generated with ("headreco" or "mri2mesh")
    plot : bool, optional, default: False
        Plot MEPs and p2p evaluation

    Returns
    -------
    dict_lst : list of dicts, one dict for each zap
          'number'
          'condition'
          'current'
          'mep_raw_data'
          'mep'
          'mep_latency'
          'mep_filt_data'
          'mep_raw_data_time'
          'time_tms'
          'ts_tms'
          'time_mep'
          'date'
          'coil_sn'
          'patient_id'
    """

    # get arrays and lists
    coil_array, ts_tms_lst, current_lst, tms_idx_invalid = pynibs.get_tms_elements(xml_paths, verbose=False)

    # get RT from .csv files
    time_mep_lst = []
    # last_mep_onset = datetime.timedelta(seconds=0)
    rt_arr = None

    if not isinstance(behavior_paths, list):
        behavior_paths = [behavior_paths]

    for idx, behavior_path in enumerate(behavior_paths):
        # get RT and trial onsets from .csv file
        rt_array_tmp, trial_onset_lst_tmp, mean_isi = get_trial_data_from_csv(behavior_fn=behavior_path,
                                                                              drop_trial_idx=drop_trial_idx,
                                                                              cond=cond,
                                                                              only_corr=True)

        time_mep_lst.extend(trial_onset_lst_tmp)

        if idx == 0:
            rt_arr = rt_array_tmp
        else:
            rt_arr = np.concatenate((rt_arr, rt_array_tmp), axis=1)

        # last_mep_onset = time_mep_lst[-1]

    # match TMS Navigator zaps and MEPs
    time_mep_lst = [datetime.timedelta(seconds=onset / 1000) for onset in time_mep_lst]

    tms_index_lst, mep_index_lst, time_tms_lst = match_behave_and_triggermarker(mep_time_lst=time_mep_lst,
                                                                                xml_paths=xml_paths,
                                                                                isi=mean_isi)  # 0.99/2

    experiment_date_time = "N/A"

    # get indices of not recognizable coils
    unit_matrix_index_list = []
    for unit_matrix_index1 in range(coil_array.shape[0]):
        for unit_matrix_index2 in range(coil_array.shape[1]):
            if np.allclose(coil_array[unit_matrix_index1, unit_matrix_index2, :, :], np.identity(4)):
                unit_matrix_index_list.append([unit_matrix_index1, unit_matrix_index2])

    # set condition names in case of random sampling
    if im is None or im == [""] or im == "":
        coil_cond_lst = [str(i) for i in range(len(ts_tms_lst))]
        drop_idx = []
    else:
        # get conditions from instrument markers
        if os.path.isfile(im[0]):
            coil_cond_lst, drop_idx = pynibs.match_instrument_marker_file(xml_paths, im[0])
        else:
            coil_cond_lst, drop_idx = pynibs.match_instrument_marker_string(xml_paths, im)

    # coordinate transform (for coil_0, coil_1, coil_mean)
    for idx in range(coil_array.shape[0]):
        # move axis, calculate and move back
        m_simnibs = np.moveaxis(coil_array[idx, :, :, :], 0, 2)
        m_simnibs = nnav2simnibs(fn_exp_nii=nii_exp_path[0],
                                 fn_conform_nii=nii_conform_path,
                                 m_nnav=m_simnibs,
                                 nnav_system=nnav_system,
                                 mesh_approach=mesh_approach,
                                 temp_dir=temp_dir)

        coil_array[idx, :, :, :] = np.moveaxis(m_simnibs, 2, 0)

    # replace transformed identity matrices
    for unit_matrix_indices in unit_matrix_index_list:
        coil_array[unit_matrix_indices[0], unit_matrix_indices[1], :, :] = np.identity(4)

    # list for dictionaries
    dict_lst = []
    idx = 0

    assert len(tms_index_lst) == len(mep_index_lst)

    delta_t = []
    ts_mep = [time_mep_lst[i] for i in mep_index_lst]
    ts_tms = [time_tms_lst[i] for i in tms_index_lst]

    for t1, t2 in zip(ts_mep, ts_tms):
        # print(f"MEP: {t1}     TMS: {t2}")
        delta_t.append(np.abs(t1 - t2))

    plt.plot(np.array([delta_t[i].microseconds for i in range(len(delta_t))]) / 1000)
    plt.xlabel("TMS pulse #", fontsize=11)
    plt.ylabel("$\Delta t$ in ms", fontsize=11)
    fn_plot = os.path.join(os.path.split(behavior_paths[0])[0], "delta_t_mep_vs_tms.png")
    plt.savefig(fn_plot, dpi=600)
    plt.close()

    # iterate over trial and tms indices to get valid matches of trials and TMS Navigator information
    for tms_index, mep_index in zip(tms_index_lst, mep_index_lst):
        if tms_index not in drop_idx:
            dictionary = {'number': idx,
                          'condition': coil_cond_lst[tms_index],
                          'current': current_lst[tms_index],
                          'rt': rt_arr[mep_index],
                          'time_tms': time_tms_lst[tms_index].total_seconds(),
                          'ts_tms': ts_tms_lst[tms_index],
                          'time_trial': time_mep_lst[mep_index].total_seconds(),
                          'date': experiment_date_time,
                          'coil_sn': coil_sn,
                          'patient_id': patient_id}

            # write coils
            for index1 in range(4):
                for index2 in range(4):
                    dictionary.update({'coil0_' + str(index1) + str(index2): coil_array[0, tms_index, index1, index2]})
                    dictionary.update({'coil1_' + str(index1) + str(index2): coil_array[1, tms_index, index1, index2]})
                    dictionary.update(
                            {'coil_mean_' + str(index1) + str(index2): coil_array[2, tms_index, index1, index2]})

            # get time difference
            time_diff = time_tms_lst[tms_index] - time_mep_lst[mep_index]
            time_diff = time_diff.total_seconds() * 1000
            dictionary.update({'time_diff': time_diff})

            # append to list
            dict_lst.append(dictionary)

            idx += 1

    return dict_lst


def get_patient_id(xml_path):
    """
    Read patiend-ID.

    Parameters
    ----------
    xml_path : str
        Path to coil0-file

    Returns
    -------
    xml_pd.find('patientID').text : str
        ID of patient
    """

    patient_data_path = os.path.dirname(xml_path) + '/PatientData.xml'
    # parse XML document
    xml_tree = ET.parse(patient_data_path)
    xml_root = xml_tree.getroot()
    xml_pd = xml_root.find('patientData')
    return xml_pd.find('patientID').text


def write_csv(csv_output_path, dict_lst):
    """
    Write dictionary into .csv-file.

    Parameters
    ----------
    csv_output_path : str
        Path to output-file
    dict_lst : list of dict
        Fields of the .csv-file
    """

    with open(csv_output_path, 'w') as csv_file:
        fieldnames = ['number', 'patient_id', 'condition', 'current', 'mep', 'coil_sn', 'coil0_00', 'coil0_01',
                      'coil0_02', 'coil0_03', 'coil0_10',
                      'coil0_11', 'coil0_12', 'coil0_13', 'coil0_20', 'coil0_21', 'coil0_22', 'coil0_23', 'coil0_30',
                      'coil0_31', 'coil0_32', 'coil0_33', 'coil1_00', 'coil1_01', 'coil1_02', 'coil1_03', 'coil1_10',
                      'coil1_11', 'coil1_12', 'coil1_13', 'coil1_20', 'coil1_21', 'coil1_22', 'coil1_23', 'coil1_30',
                      'coil1_31', 'coil1_32', 'coil1_33', 'coil_mean_00', 'coil_mean_01', 'coil_mean_02',
                      'coil_mean_03',
                      'coil_mean_10', 'coil_mean_11', 'coil_mean_12', 'coil_mean_13', 'coil_mean_20', 'coil_mean_21',
                      'coil_mean_22', 'coil_mean_23', 'coil_mean_30', 'coil_mean_31', 'coil_mean_32', 'coil_mean_33',
                      'ts_tms', 'time_tms', 'time_mep', 'time_diff', 'date']

        fieldnames_all = list(dict_lst[0].keys())

        for field in fieldnames_all:
            if field not in fieldnames:
                fieldnames.append(field)

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for index, dictionary in enumerate(dict_lst):
            dictionary.update({'number': index})
            writer.writerow(dictionary)
        return 0


def read_csv(csv_path):
    """
    Read dictionary from .csv-file.

    Parameters
    ----------
    csv_path : str
        Path to .csv-file

    Returns
    -------
    dict_lst : dict of list
        Field name of the .csv-file as the key
    """

    dictionary = {}
    with open(csv_path) as csv_handle:
        # read csv file
        csv_file = csv.reader(csv_handle)
        # get fieldnames
        csv_fieldnames = next(csv_handle)
        csv_fieldnames = csv_fieldnames.split(',')
        # remove unnecessary characters
        for index in range(len(csv_fieldnames)):
            csv_fieldnames[index] = csv_fieldnames[index].replace('"', '')
            csv_fieldnames[index] = csv_fieldnames[index].replace('\n', '')
            csv_fieldnames[index] = csv_fieldnames[index].replace('\r', '')
        # iterate over rows
        for index, field in enumerate(csv_fieldnames):
            row_array = []
            # rewind file
            csv_handle.seek(0)
            for row_index, row in enumerate(csv_file):
                # do not get fieldname
                if row_index == 0:
                    continue
                value = row[index]
                # do not convert patient_id
                if field != 'patient_id':
                    # try to convert into integer
                    try:
                        value = int(value)
                    except ValueError:
                        # try to convert into float
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                row_array.append(value)
            dictionary.update({field: row_array})
    dictionary = get_csv_matrix(dictionary)
    return dictionary


def get_csv_matrix(dictionary):
    coil_name_lst = ['coil0_', 'coil1_', 'coil_mean_']
    for coil_name in coil_name_lst:
        array_lst = []
        for lst_index in range(len(dictionary[coil_name + '00'])):
            array = np.empty([4, 4])
            for coil_index1 in range(4):
                for coil_index2 in range(4):
                    coil_name_index = coil_name + str(coil_index1) + str(coil_index2)
                    array[coil_index1, coil_index2] = float(dictionary[coil_name_index][lst_index])
            array_lst.append(array)
        dictionary.update({coil_name + 'matrix': array_lst})
    # remove redundant entries
    for coil_name in coil_name_lst:
        for coil_index1 in range(4):
            for coil_index2 in range(4):
                coil_name_index = coil_name + str(coil_index1) + str(coil_index2)
                del dictionary[coil_name_index]
    return dictionary


def sort_by_condition(exp, conditions_selected=None):
    """
    Sort experimental dictionary from experimental.csv into list by conditions.

    Parameters
    ----------
    exp : dict or list of dict
        Dictionary containing the experimental data information
    conditions_selected : str or list of str, Default=None
        List of conditions returned by the function (in this order), the others are omitted,
        If None, all conditions are returned

    Returns
    -------
    exp_cond : list of dict
        List of dictionaries containing the experimental data information sorted by condition
    """

    _, idx = np.unique(exp['condition'], return_index=True)
    conds = list(np.array(exp['condition'])[np.sort(idx)])

    cond_idx = []
    exp_cond = []
    keys = list(exp.keys())

    for k in range(len(conds)):
        cond_idx.append([i for i, j in enumerate(exp['condition']) if j == conds[k]])
        exp_cond.append(dict())

        for l_k in range(len(keys)):
            exp_cond[-1][keys[l_k]] = []

            for y in cond_idx[-1]:
                exp_cond[-1][keys[l_k]].append(exp[keys[l_k]][y])

    if conditions_selected is not None:
        if type(conditions_selected) is not list:
            conditions_selected = [conditions_selected]
        exp_cond_selected = []
        for c in conditions_selected:
            exp_cond_selected.append([exp_cond[i] for i in range(len(exp_cond)) if exp_cond[i]['condition'][0] == c][0])

        return exp_cond_selected

    else:
        return exp_cond


def coil_outlier_correction_cond(exp=None, fn_exp=None, fn_exp_out=None, outlier_angle=5., outlier_loc=3.):
    """
    Searches and removes outliers of coil orientation and location w.r.t. the average orientation and location from
    all zaps. It generates plots of the individual conditions showing the outliers in the folder of fn_exp_out.
    Depending on if exp (dict containing lists) or fn_exp (csv file) is provided it returns the outlier corrected dict
    or writes a new <fn_exp_out>.csv file.
    If _exp_ is provided, all keys are kept.

    Parameters
    ----------
    exp : list of dict, optional, default: None
        List of dictionaries containing the experimental data
    fn_exp : str, optional, default: None
        Filename (incl. path) of experimental .csv file
    fn_exp_out : str, optional, default: None
        Filename (incl. path) of corrected experimental .csv file
    outlier_angle : float, optional, default: 5.
        Coil orientation outlier "cone" around axes in +- deg.
        All zaps with coil orientations outside of this cone are removed.
    outlier_loc : float, optional, default: 3.
        Coil position outlier "sphere" in +- mm.
        All zaps with coil locations outside of this sphere are removed.

    Returns
    -------
    <File>: .csv file
        experimental_oc.csv file with outlier corrected coil positions
    <Files>: .png files
        Plot showing the coil orientations and locations (folder_of_fn_exp_out/COND_X_coil_position.png)
    or
    exp : dict
         Dictionary containing the outlier corrected experimental data
    """

    if exp is not None:
        if type(exp) is list:
            exp = pynibs.list2dict(exp)
    elif fn_exp is not None:
        exp = read_csv(fn_exp)
    else:
        raise IOError("Please provide either dictionary containing the experimental data or the filename "
                      "of the experimental.csv file")

    # read and sort by condition
    exp_by_cond = sort_by_condition(exp)
    exp_cond_corr = []

    bound_radius = np.sin(outlier_angle / 180 * np.pi)

    for cond in exp_by_cond:
        # concatenate all matrices in one tensor
        n_coords = len(cond["coil_mean"])

        coil_coords = np.zeros((4, 4, n_coords))

        for i in range(n_coords):
            coil_coords[:, :, i] = cond["coil_mean"][i]

        # call plot function
        # idx_keep, _, _ = calc_outlier(coords=coil_coords, dev_location=outlier_loc, dev_radius=bound_radius,
        #                              fn_out=os.path.join(os.path.split(fn_exp_out)[0],
        #                                                  str(cond["condition"][0]) + "_coil_position.png"))

        idx_keep, _, _ = calc_outlier(coords=coil_coords, dev_location=outlier_loc, dev_radius=bound_radius)

        # remove outlier and rebuilt dictionary with lists
        exp_cond_corr.append(OrderedDict())

        for key in list(cond.keys()):
            exp_cond_corr[-1][key] = []
            for i in idx_keep:
                exp_cond_corr[-1][key].append(cond[key][i])

    # corrected exp dictionary
    exp_corr = OrderedDict()
    keys = list(exp.keys())
    for i_cond in range(len(exp_cond_corr)):
        for k in keys:
            if i_cond == 0:
                exp_corr[k] = exp_cond_corr[i_cond][k]
            else:
                exp_corr[k] = exp_corr[k] + exp_cond_corr[i_cond][k]

    if fn_exp is not None:
        # reformat results to save new .csv file
        coil0_keys = ['coil0_' + str(int(m)) + str(int(n)) for m in range(4) for n in range(4)]
        coil1_keys = ['coil1_' + str(int(m)) + str(int(n)) for m in range(4) for n in range(4)]
        coil_mean_keys = ['coil_mean_' + str(int(m)) + str(int(n)) for m in range(4) for n in range(4)]

        exp_corr_formatted = copy.deepcopy(exp_corr)
        del exp_corr_formatted['coil0_matrix']
        del exp_corr_formatted['coil1_matrix']
        del exp_corr_formatted['coil_mean_matrix']

        for i_key in range(len(coil0_keys)):
            m = int(coil0_keys[i_key][-2])
            n = int(coil0_keys[i_key][-1])

            exp_corr_formatted[coil0_keys[i_key]] = [exp_corr['coil0_matrix'][i_zap][m, n]
                                                     for i_zap in range(len(exp_corr['coil0_matrix']))]

            exp_corr_formatted[coil1_keys[i_key]] = [exp_corr['coil1_matrix'][i_zap][m, n]
                                                     for i_zap in range(len(exp_corr['coil1_matrix']))]

            exp_corr_formatted[coil_mean_keys[i_key]] = [exp_corr['coil_mean_matrix'][i_zap][m, n]
                                                         for i_zap in range(len(exp_corr['coil_mean_matrix']))]

        # reformat from dict containing lists to list containing dicts to write csv file
        exp_corr_list = []
        for i in range(len(exp_corr_formatted['coil_mean_00'])):
            exp_corr_list.append(OrderedDict())
            for key in list(exp_corr_formatted.keys()):
                exp_corr_list[-1][key] = exp_corr_formatted[key][i]

        # save experimental csv
        write_csv(fn_exp_out, exp_corr_list)
    else:
        return exp_corr


def calc_outlier(coords, dev_location, dev_radius, target=None, fn_out=None, print_msg=True):
    """
    Computes median coil position and angle, identifies outliers, plots neat figure.
    Returns a list of idx that are not outliers

    Parameters:
    -----------
    coords : 4 x 4 x n_zaps np.ndArray
    dev_location : float
    dev_radis : flat
    target : np.ndarray
        4*4 matrix with target coordinates. Optional.
    fn_out : string, optional

    Returns:
    --------
    list of int, list of int, list of int : idx_keep, idx_zero, idx_outlier
    """
    if coords.shape[:2] != (4, 4):
        print(f"plot_coords is expecting a 4x4xn_zaps array. Found {coords.shape}. Trying to resize")
        if len(coords.shape) != 3:
            raise NotImplementedError
        elif coords.shape[1:] != (4, 4):
            raise NotImplementedError
        coords = np.rollaxis(coords, 0, coords.ndim)

    # remove idx with no tracking information
    idx_zero = []
    np.where(coords[0, 3, :] == 0)
    for i in range(coords.shape[2]):
        if np.all(np.diag(coords[:, :, i]) == np.array([1, 1, 1, 1])):
            idx_zero.append(i)
    # coords = np.delete(coords, idx_zero, axis=2)
    # determine mean coil orientation and location
    idx_nonzero = np.setdiff1d(range(coords.shape[2]), idx_zero)
    n_coords = coords.shape[2]
    coil_coords_median = np.median(coords[:, :, idx_nonzero], axis=2)
    coil_coords_0 = np.zeros((4, 4, n_coords))
    coil_coords_0[3, 3, :] = 1.0
    if target is not None:
        for i in range(n_coords):
            coil_coords_0[:3, 3, i] = coords[:3, 3, i] - target[:3, 3]
    else:
        # shift all coil_coords (zero-mean)
        for i in range(n_coords):
            coil_coords_0[:3, 3, i] = coords[:3, 3, i] - coil_coords_median[:3, 3]

    if print_msg:
        print(f"{n_coords} coil positions found, {len(idx_nonzero)} tracked. Detecting outliers...")
        print(f"Max allowed location/angle deviation: {dev_location}, {dev_radius}")
        print(f"Median location original data:        {np.round(coil_coords_median[0:3, 3], 2)}")
        print(
                f"Median orientation original data:     {np.round(coil_coords_median[0:3, 0], 2)}, "
                f"{np.round(coil_coords_median[0:3, 1], 2)}")

    # rotate all coil_coords to median orientation
    idx_keep = []
    idx_outlier = []
    for i in range(n_coords):
        if target is not None:
            coil_coords_0[:3, :3, i] = np.dot(coords[:3, :3, i], np.transpose(target[:3, :3]))
        else:
            coil_coords_0[:3, :3, i] = np.dot(coords[:3, :3, i], np.transpose(coil_coords_median[:3, :3]))

        dev_ori_x = np.sqrt(coil_coords_0[1, 0, i] ** 2 + coil_coords_0[2, 0, i] ** 2)
        dev_ori_y = np.sqrt(coil_coords_0[0, 1, i] ** 2 + coil_coords_0[2, 1, i] ** 2)
        dev_ori_z = np.sqrt(coil_coords_0[0, 2, i] ** 2 + coil_coords_0[1, 2, i] ** 2)
        dev_pos = np.linalg.norm(coil_coords_0[:3, 3, i])

        if (i in idx_nonzero) and not (
                dev_ori_x > dev_radius or dev_ori_y > dev_radius or dev_ori_z > dev_radius or dev_pos > dev_location):
            idx_keep.append(i)
        elif i in idx_nonzero:
            idx_outlier.append(i)
            if print_msg > 1:
                print(f"Outlier in coil position or orientation detected, removing data point. cond:  zap #{i}")
    if target is not None:
        coil_coords_0 = coords
    coil_coords_median = np.median(coil_coords_0[:, :, idx_keep], axis=2)
    if fn_out is not None:
        coil_coords_0_keep = coil_coords_0[:, :, idx_keep]
        coil_coords_0_outlier = coil_coords_0[:, :, idx_outlier]

        fig = plt.figure(figsize=[10, 5.5])  # fig.add_subplot(121, projection='3d')
        ax = fig.add_subplot(121, projection='3d')
        try:
            ax.set_aspect("equal")
        except NotImplementedError:
            pass

        # draw sphere
        if target is not None:
            ax.scatter(target[0, 3], target[1, 3], target[2, 3], color='y', s=400)
        if dev_location != np.inf:
            u, v = np.mgrid[0:2 * np.pi:20j, 0:np.pi:10j]
            x = dev_location * np.cos(u) * np.sin(v)
            y = dev_location * np.sin(u) * np.sin(v)
            z = dev_location * np.cos(v)
            ax.plot_wireframe(x, y, z, color="k")
            ax.set_xlim([-dev_location * 1.1, dev_location * 1.1])
            ax.set_ylim([-dev_location * 1.1, dev_location * 1.1])
            ax.set_zlim([-dev_location * 1.1, dev_location * 1.1])
        else:
            ax.set_xlim([np.min(coil_coords_0_keep[0, 3, :]) - 2, np.max(coil_coords_0_keep[0, 3, :]) + 2])
            ax.set_ylim([np.min(coil_coords_0_keep[1, 3, :]) - 2, np.max(coil_coords_0_keep[1, 3, :]) + 2])
            ax.set_zlim([np.min(coil_coords_0_keep[2, 3, :]) - 2, np.max(coil_coords_0_keep[2, 3, :]) + 2])

        # color bar + scaling for quiver
        cm = plt.cm.get_cmap('cool')
        norm = Normalize()
        norm.autoscale(range(coil_coords_0_keep.shape[2]))

        # draw coil center locations
        # pl = ax.scatter(coil_coords_0_keep[0, 3, :], coil_coords_0_keep[1, 3, :], coil_coords_0_keep[2, 3, :],
        #                 c=range(coil_coords_0_keep.shape[2]), cmap=cm)
        ax.scatter(coil_coords_0_outlier[0, 3, :], coil_coords_0_outlier[1, 3, :], coil_coords_0_outlier[2, 3, :],
                   color='r')

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_title("Coil location")
        # ax.annotate(f'median: {np.round(coil_coords_median[0:3,3],2)}\n'
        #             f'std:     {np.round(np.std(coords[0:3,3,idx_keep],axis=1),4)}',xy=(10,-150),
        #             annotation_clip=False,xycoords='axes pixels',
        #             bbox=OrderedDict(boxstyle='square', facecolor='wheat', alpha=1),fontfamily='monospace' )
        med_pos = np.round(coil_coords_median[0:3, 3], 2)
        std_pos = np.round(np.std(coords[0:3, 3, idx_keep], axis=1), 4)
        anot = f'median(pos): [{med_pos[0]: 3.3f}, {med_pos[1]: 3.3f}, {med_pos[2]: 3.3f}]\n' \
               f'   std(pos): [{std_pos[0]: 7.3f}, {std_pos[1]: 7.3f}, {std_pos[2]: 7.3f}]'

        if target is not None:
            pos_dif = np.linalg.norm(((coords[0:3, 3, idx_keep].transpose() - target[0:3, 3]).transpose()), axis=0)
            anot += f'\nmin/med/max (std) dif: ' \
                    f'{np.min(pos_dif):2.2f}, {np.median(pos_dif):2.2f}, ' \
                    f'{np.max(pos_dif):2.2f} ({np.std(pos_dif):2.2f})'

        ax.annotate(anot,
                    xy=(30, -250),
                    annotation_clip=False, xycoords='axes pixels',
                    bbox=OrderedDict(boxstyle='square', facecolor='wheat', alpha=1), font='monospace')

        # draw coil orientations
        ax = fig.add_subplot(122, projection='3d')
        try:
            ax.set_aspect("equal")
        except NotImplementedError:
            pass

        if target is not None:
            ax.quiver(0, 0, 0, target[0, 0], target[1, 0], target[2, 0], color='y')
            ax.quiver(0, 0, 0, target[0, 1], target[1, 1], target[2, 1], color='y')
            ax.quiver(0, 0, 0, target[0, 2], target[1, 2], target[2, 2], color='y')

        for i in range(coil_coords_0_keep.shape[2]):
            ax.quiver(0, 0, 0, coil_coords_0_keep[0, 0, i], coil_coords_0_keep[1, 0, i], coil_coords_0_keep[2, 0, i],
                      color=cm(norm(range(coil_coords_0_keep.shape[2])))),
            ax.quiver(0, 0, 0, coil_coords_0_keep[0, 1, i], coil_coords_0_keep[1, 1, i], coil_coords_0_keep[2, 1, i],
                      color=cm(norm(range(coil_coords_0_keep.shape[2])))),
            ax.quiver(0, 0, 0, coil_coords_0_keep[0, 2, i], coil_coords_0_keep[1, 2, i], coil_coords_0_keep[2, 2, i],
                      color=cm(norm(range(coil_coords_0_keep.shape[2])))),
        for i in range(coil_coords_0_outlier.shape[2]):
            ax.quiver(0, 0, 0, coil_coords_0_outlier[0, 0, i], coil_coords_0_outlier[1, 0, i],
                      coil_coords_0_outlier[2, 0, i], color='r')
            ax.quiver(0, 0, 0, coil_coords_0_outlier[0, 1, i], coil_coords_0_outlier[1, 1, i],
                      coil_coords_0_outlier[2, 1, i], color='r')
            ax.quiver(0, 0, 0, coil_coords_0_outlier[0, 2, i], coil_coords_0_outlier[1, 2, i],
                      coil_coords_0_outlier[2, 2, i], color='r')

        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_zlim([-1.2, 1.2])
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_title("Coil orientation")
        med_pos = np.round(np.median(coil_coords_0_keep[0:3, 0], axis=1), 2)
        med_rot = np.round(np.median(coil_coords_0_keep[0:3, 1], axis=1), 2)
        std_pos = np.round(np.std(coords[0:3, 0, idx_keep], axis=1), 4)
        std_rot = np.round(np.std(coords[0:3, 1, idx_keep], axis=1), 4)
        ax.annotate(f'median(x): [{med_pos[0]: 2.3f}, {med_pos[1]: 2.3f}, {med_pos[2]: 2.3f}]\n'
                    f'   std(x): [{std_pos[0]: 2.3f}, {std_pos[1]: 2.3f}, {std_pos[2]: 2.3f}]\n'
                    f'median(y): [{med_rot[0]: 2.3f}, {med_rot[1]: 2.3f}, {med_rot[2]: 2.3f}]\n'
                    f'   std(y): [{std_rot[0]: 2.3f}, {std_rot[1]: 2.3f}, {std_rot[2]: 2.3f}]',
                    xy=(30, -250),
                    annotation_clip=False, xycoords='axes pixels',
                    bbox=OrderedDict(boxstyle='square', facecolor='wheat', alpha=1), font='monospace')

        # these are matplotlib.patch.Patch properties
        props = OrderedDict(boxstyle='round', facecolor='wheat', alpha=0.5)

        # place a text box in upper left in axes coords
        plt.figtext(0.5, .7,
                    f"n_pos:     {n_coords}\n"
                    f"n_zero:    {len(idx_zero)}\n"
                    f"n_outlier: {len(idx_outlier)}\n"
                    f"n_keep:    {len(idx_keep)}", bbox=props, family='monospace')
        # plt.tight_layout(rect=[0.1, 0.03, 1, 0.95])
        if not os.path.exists(os.path.split(fn_out)[0]):
            os.makedirs(os.path.split(fn_out)[0])
        plt.savefig(fn_out, dpi=300)

    if print_msg:
        print(f"{len(idx_outlier)} outliers/zero zaps detected and removed.")
        print(f"Median location w/o outliers:    {np.round(coil_coords_median[0:3, 3], 2)}")
        print(f"Median orientation w/o outliers: {np.round(coil_coords_median[0:3, 0], 2)}, "
              f"{np.round(coil_coords_median[0:3, 1], 2)}")

    return idx_keep, idx_zero, idx_outlier


def write_triggermarker_stats(tm_array, idx_keep, idx_outlier, idx_zero, fn, **kwargs):
    """
    Write some stats about the triggermarker analyses to a .csv .
    Use kwargs to add some more information, like subject id, experiment, conditions, etc

    Call example:
    pynibs.write_triggermarker_stats(tm_array, idx_keep, idx_outlier, idx_zero,
                                          fn=f"{output_folder}/coil_stats.csv",subject=subject_id,
                                          experiment=exp, cond=cond)
    Parameters:
    -----------
    tm_array : np.ndarray
        (N zaps * 4 * 4)
    """

    idx_nonzero = np.setdiff1d(range(tm_array.shape[0]), idx_zero)
    # 'subject': [subject_id],
    # 'experiment': [exp],
    # 'cond': [cond],
    res = {
        'n_zaps': [tm_array.shape[0]],
        'n_zero': [len(idx_zero)],
        'n_outlier': [len(idx_outlier)],
        'median_pos_nonzero_x': [np.median(tm_array[idx_nonzero, 0, 3])],
        'median_pos_nonzero_y': [np.median(tm_array[idx_nonzero, 1, 3])],
        'median_pos_nonzero_z': [np.median(tm_array[idx_nonzero, 2, 3])],
        'median_pos_keep_x': [np.median(tm_array[idx_keep, 0, 3])],
        'median_pos_keep_y': [np.median(tm_array[idx_keep, 1, 3])],
        'median_pos_keep_z': [np.median(tm_array[idx_keep, 2, 3])],
        'std_pos_nonzero_x': [np.std(tm_array[idx_nonzero, 0, 3])],
        'std_pos_nonzero_y': [np.std(tm_array[idx_nonzero, 1, 3])],
        'std_pos_nonzero_z': [np.std(tm_array[idx_nonzero, 2, 3])],
        'std_pos_keep_x': [np.std(tm_array[idx_keep, 0, 3])],
        'std_pos_keep_y': [np.std(tm_array[idx_keep, 1, 3])],
        'std_pos_keep_z': [np.std(tm_array[idx_keep, 2, 3])],
        'median_angle_x_nonzero_x': [np.median(tm_array[idx_nonzero, 0, 3])],
        'median_angle_x_nonzero_y': [np.median(tm_array[idx_nonzero, 0, 3])],
        'median_angle_x_nonzero_z': [np.median(tm_array[idx_nonzero, 0, 3])],
        'median_angle_x_keep_x': [np.median(tm_array[idx_keep, 0, 0])],
        'median_angle_x_keep_y': [np.median(tm_array[idx_keep, 1, 0])],
        'median_angle_x_keep_z': [np.median(tm_array[idx_keep, 2, 0])],
        'std_angle_x_nonzero_x': [np.std(tm_array[idx_nonzero, 0, 0])],
        'std_angle_x_nonzero_y': [np.std(tm_array[idx_nonzero, 1, 0])],
        'std_angle_x_nonzero_z': [np.std(tm_array[idx_nonzero, 2, 0])],
        'std_angle_x_keep_x': [np.std(tm_array[idx_keep, 0, 0])],
        'std_angle_x_keep_y': [np.std(tm_array[idx_keep, 1, 0])],
        'std_angle_x_keep_z': [np.std(tm_array[idx_keep, 2, 0])],
    }

    # add kwargs
    for key, val in kwargs.items():
        res[key] = [val]

    # save csv
    pd.DataFrame().from_dict(res).to_csv(fn, index=False)


def coil_distance_correction(exp=None, fn_exp=None, fn_exp_out=None, fn_geo_hdf5=None,
                             remove_coil_skin_distance_outlier=False, fn_plot=None, min_dist=-5, max_dist=2):
    """
    Corrects the distance between the coil and the head assuming that the coil is touching the head surface during
    the experiments. This is done since the different coil tracker result in different coil head distances due to
    tracking inaccuracies. Also averages positions and orientations over the respective condition and writes both
    mean position and orientation for every condition in fn_exp_out.

    Depending on if exp (dict containing lists) or fn_exp (csv file) is provided it returns the outlier corrected dict
    or writes a new <fn_exp_out>.csv file.


    Parameters
    ----------
    exp : list of dict or dict of list, optional, default: None
        List of dictionaries containing the experimental data
    fn_exp : str
        Filename (incl. path) of experimental .csv file
    fn_exp_out : str
        Filename (incl. path) of distance corrected experimental .csv file
    fn_geo_hdf5 : str
        Filename (incl. path) of geometry mesh file (.hdf5)
    remove_coil_skin_distance_outlier : bool
        Remove coil positions, which are more than +- 2 mm located from the zero mean skin surface.
    fn_plot : str, default: None (fn_geo_hdf5 folder)
        Folder where plots will be saved in.
    min_dist : int
        Ignored.
    max_dist : int
        Ignored.

    Returns
    -------
    <File>: .csv file
        experimental_dc.csv file with distance corrected coil positions
    or
    exp : dict
         Dictionary containing the outlier corrected experimental data
    """

    if exp is not None:
        if type(exp) is list:
            exp = pynibs.list2dict(exp)
    elif fn_exp is not None:
        exp = read_csv(fn_exp)
    else:
        raise IOError("Please provide either dictionary containing the experimental data or the filename "
                      "of the experimental.csv file")

    if fn_plot is None:
        fn_plot = os.path.split(fn_geo_hdf5)[0]

    # read and sort by condition
    exp_cond = sort_by_condition(exp)
    # exp_cond_corr = []
    n_conditions = len(exp_cond)

    # read head mesh and extract skin surface
    msh = pynibs.load_mesh_hdf5(fn_geo_hdf5)
    triangles = msh.triangles[msh.triangles_regions == 1005]
    point_idx_unique = np.unique(triangles)
    points = msh.points[point_idx_unique, :]

    # get mean coil orientantion and position
    ori_mean = [np.mean(np.array(exp_cond[i]['coil_mean'])[:, 0:3, 0:3], axis=0) for i in range(n_conditions)]
    pos_mean = [np.mean(np.array(exp_cond[i]['coil_mean'])[:, 0:3, 3], axis=0) for i in range(n_conditions)]

    # determine distance between coil plane and skin surface and set coil to it
    coil_normal = [np.zeros(3) for _ in range(n_conditions)]
    distance = np.zeros(n_conditions)
    # distance_check = np.zeros(n_conditions)

    pos_mean_corrected = [np.zeros(3) for _ in range(n_conditions)]
    # coil_pos_selected = [0 for _ in range(n_conditions)]

    for i_cond in range(n_conditions):
        # determine coil normal pointing to subject
        coil_normal[i_cond] = ori_mean[i_cond][:, 2] / np.linalg.norm(ori_mean[i_cond][:, 2])

        # determine minimal distance between coil and skin surface
        distance[i_cond] = np.min(np.dot((points - pos_mean[i_cond]), coil_normal[i_cond]))

        # move coil in normal direction by this distance
        pos_mean_corrected[i_cond] = pos_mean[i_cond] + distance[i_cond] * coil_normal[i_cond]

        # # check if distance is reduced
        # distance_check[i_cond] = np.min(np.dot((points - POS_mean_corrected[i_cond]), coil_normal[i_cond]))

    # outlier detection
    if remove_coil_skin_distance_outlier:
        distance_mean = np.median(distance)
        distance_zm = distance - distance_mean
        coil_pos_selected = np.logical_and(-5 < distance_zm, distance_zm < 2)  # TODO: remove hardcoded dists

        # distance distribution (original)
        plt.hist(distance, bins=50, density=True)
        plt.hist(distance[coil_pos_selected], bins=50, density=True, alpha=0.6)
        plt.xlabel("distance in (mm)")
        plt.ylabel("number of stimulations")
        plt.title(f"Distance histogram (original, mean: {distance_mean:.2f}mm)")
        plt.legend(["original", "outlier corrected"])
        plt.savefig(os.path.join(fn_plot, "distance_histogram_orig.png"), dpi=300)
        plt.close()

        # distance distribution (zero mean)
        plt.hist(distance_zm, bins=50, density=True)
        plt.hist(distance_zm[coil_pos_selected], bins=50, density=True, alpha=0.6)
        plt.xlabel("distance in (mm)")
        plt.ylabel("number of stimulations")
        plt.title("Distance histogram (zero mean)")
        plt.legend(["zero mean", "outlier corrected"])
        plt.savefig(os.path.join(fn_plot, "distance_histogram_zm.png"), dpi=300)
        plt.close()

    else:
        coil_pos_selected = [True] * n_conditions

    # write results in exp_corr
    exp_cond_corr = copy.deepcopy(exp_cond)

    for i_cond in range(n_conditions):
        exp_cond_corr[i_cond]['coil_mean'] = [np.vstack((np.hstack((ori_mean[i_cond],
                                                                    pos_mean_corrected[i_cond][:, np.newaxis])),
                                                         [0, 0, 0, 1]))] * len(
                exp_cond_corr[i_cond]['coil_mean'])
        exp_cond_corr[i_cond]['coil_0'] = exp_cond_corr[i_cond]['coil_mean']
        exp_cond_corr[i_cond]['coil_1'] = exp_cond_corr[i_cond]['coil_mean']

    # filter out valid coil positions
    exp_cond_corr_selected = []
    i_zap_total = 0
    for i_cond in range(n_conditions):
        if coil_pos_selected[i_cond]:
            exp_cond_corr_selected.append(exp_cond_corr[i_cond])
        else:
            print(f"Removing coil position #{i_zap_total} (-5mm < distance < 3mm from zero mean "
                  f"coil <-> skin distance distribution")
        i_zap_total += 1

    exp_corr = dict()
    keys = list(exp.keys())
    for i_cond in range(len(exp_cond_corr_selected)):
        for k in keys:
            if i_cond == 0:
                exp_corr[k] = exp_cond_corr_selected[i_cond][k]
            else:
                exp_corr[k] = exp_corr[k] + exp_cond_corr_selected[i_cond][k]

    if fn_exp_out is not None:
        # reformat results to save new .csv file
        coil0_keys = ['coil0_' + str(int(m)) + str(int(n)) for m in range(4) for n in range(4)]
        coil1_keys = ['coil1_' + str(int(m)) + str(int(n)) for m in range(4) for n in range(4)]
        coil_mean_keys = ['coil_mean_' + str(int(m)) + str(int(n)) for m in range(4) for n in range(4)]

        exp_corr_formatted = copy.deepcopy(exp_corr)  # type: dict
        del exp_corr_formatted['coil_0']
        del exp_corr_formatted['coil_1']
        del exp_corr_formatted['coil_mean']

        for i_key in range(len(coil0_keys)):
            m = int(coil0_keys[i_key][-2])
            n = int(coil0_keys[i_key][-1])

            exp_corr_formatted[coil0_keys[i_key]] = [exp_corr['coil_0'][i_zap][m, n]
                                                     for i_zap in range(len(exp_corr['coil_0']))]

            exp_corr_formatted[coil1_keys[i_key]] = [exp_corr['coil_1'][i_zap][m, n]
                                                     for i_zap in range(len(exp_corr['coil_1']))]

            exp_corr_formatted[coil_mean_keys[i_key]] = [exp_corr['coil_mean'][i_zap][m, n]
                                                         for i_zap in range(len(exp_corr['coil_mean']))]

        exp_corr_list = []
        for i in range(len(exp_corr_formatted['coil_mean_00'])):
            exp_corr_list.append(dict())
            for key in list(exp_corr_formatted.keys()):
                exp_corr_list[-1][key] = exp_corr_formatted[key][i]

        # save experimental csv
        write_csv(fn_exp_out, exp_corr_list)
    else:
        return exp_corr


def coil_distance_correction_matsimnibs(matsimnibs, fn_mesh_hdf5, distance=0, remove_coil_skin_distance_outlier=False):
    """
    Corrects the distance between the coil and the head assuming that the coil is located at a distance "d"
    with respect to the head surface during the experiments. This is done since the different coil tracker result in
    different coil head distances due to tracking inaccuracies.

    Parameters
    ----------
    matsimnibs : ndarray of float [4 x 4] or [4 x 4 x n_mat]
        Tensor containing matsimnibs matrices
    fn_mesh_hdf5 : str
        .hdf5 file containing the head mesh
    distance : float
        Target distance in (mm) between coil and head due to hair layer. All coil positions are moved to this distance.
    remove_coil_skin_distance_outlier : bool
        Remove coil positions, which are more than +- 6 mm located from the skin surface.

    Returns
    -------
    matsimnibs : ndarray of float [4 x 4 x n_mat]
        Tensor containing matsimnibs matrices with distance corrected coil positions
    """
    if matsimnibs.ndim == 2:
        matsimnibs = matsimnibs[:, :, np.newaxis]

    n_matsimnibs = matsimnibs.shape[2]
    matsimnibs_corrected = copy.deepcopy(matsimnibs)

    # read head mesh and extract skin surface
    msh = pynibs.load_mesh_hdf5(fn_mesh_hdf5)
    triangles = msh.triangles[msh.triangles_regions == 1005]  # this is skin
    point_idx_unique = np.unique(triangles)
    points = msh.points[point_idx_unique, :]
    coil_normal = [np.zeros(3) for _ in range(n_matsimnibs)]
    distance_coil_skin = np.zeros(n_matsimnibs)
    coil_pos_selected = [0 for _ in range(n_matsimnibs)]
    # distance_check = np.zeros(n_matsimnibs)

    # determine distance between coil plane and skin surface and set coil to it
    for i_mat in range(n_matsimnibs):
        # determine coil normal pointing to subject
        coil_normal[i_mat] = matsimnibs[0:3, 2, i_mat] / np.linalg.norm(matsimnibs[0:3, 2, i_mat])

        # determine minimal distance between coil and skin surface
        distance_coil_skin[i_mat] = np.min(np.dot((points - matsimnibs[0:3, 3, i_mat]), coil_normal[i_mat])) - distance

        # move coil in normal direction by this distance
        matsimnibs_corrected[0:3, 3, i_mat] = matsimnibs[0:3, 3, i_mat] + distance_coil_skin[i_mat] * coil_normal[i_mat]

        # # check if distance is reduced
        # distance_check[i_cond] = np.min(np.dot((points - POS_mean_corrected[i_cond]), coil_normal[i_cond]))

        # check if distance is too big -> outlier
        if remove_coil_skin_distance_outlier:
            coil_pos_selected[i_mat] = np.logical_and(-5 < distance_coil_skin[i_mat], distance_coil_skin[i_mat] < 2)
            if not coil_pos_selected[i_mat]:
                print(f"Removing coil position #{i_mat} "
                      f"(distance is larger than -5mm < distance < 2mm from skin surface)")
        else:
            coil_pos_selected[i_mat] = True

    # select valid coil positions
    matsimnibs_corrected = matsimnibs_corrected[:, :, coil_pos_selected]

    return matsimnibs_corrected


def save_matsimnibs_txt(fn_matsimnibs, matsimnibs):
    """
    Saving matsimnibs matrices in .txt file.

    Parameters
    ----------
    fn_matsimnibs : str
        Filename of .txt file the matsimnibs matrices are stored in
    matsimnibs : ndarray of float [4 x 4] or [4 x 4 x n_mat]
        Tensor containing matsimnibs matrices

    Returns
    -------
    <File>: .txt file
        Textfile containing the matsimnibs matrices
    """
    if matsimnibs.ndim == 2:
        matsimnibs = matsimnibs[:, :, np.newaxis]

    for i_mat in range(matsimnibs.shape[2]):
        if i_mat == 0:
            mode = "w"
        else:
            mode = "a"

        with open(fn_matsimnibs, mode) as f:
            for line in np.matrix(matsimnibs[:, :, i_mat]):
                np.savetxt(f, line, fmt='%.8f')
            f.write("\n")


def load_matsimnibs_txt(fn_matsimnibs):
    """
    Loading matsimnibs matrices from .txt file.

    Parameters
    ----------
    fn_matsimnibs : str
        Filename of .txt file the matsimnibs matrices are stored in

    Returns
    -------
    matsimnibs : ndarray of float [4 x 4] or [4 x 4 x n_mat]
        Tensor containing matsimnibs matrices
    """

    matsimnibs_list = []

    with open(fn_matsimnibs, "r") as f:
        # read first line
        line = np.array([float(i) for i in f.readline().strip().split()])

        while line.any():
            mat = []
            i = 0

            # read remaining lines
            while line != "\n":
                mat.append(line)
                i += 1
                line = np.array([float(j) for j in f.readline().strip().split()])

                if line.size == 0:
                    break

            matsimnibs_list.append(np.vstack(mat))
            line = np.array([float(j) for j in f.readline().strip().split()])

    matsimnibs = np.zeros((matsimnibs_list[0].shape[0], matsimnibs_list[0].shape[1], len(matsimnibs_list)))

    for i, m in enumerate(matsimnibs_list):
        matsimnibs[:, :, i] = m

    return matsimnibs


# TODO: Hier fehlen noch die MEP Amplituden in den phys_data/postproc/zap_idx/EMG_p2p folder im hdf5
def convert_csv_to_hdf5(fn_csv, fn_hdf5, overwrite_arr=True, verbose=False):
    """Wrapper from experiment.csv to experiment.hdf5

    Saves all relevant columns from the (old) experiment.csv file to an .hdf5 file.
    fn_hdf5:/stim_data/
                       |--coil_sn
                       |--current
                       |--date
                       |--time_diff
                       |--time_mep
                       |--time_tms
                       |--ts_tms
                       |--coil0      # <- all coil0_** columns
                       |--coil1      # <- all coil1_** columns
                       |--coil_mean  # <- all coil_mean_** columns

    All columns not found in experiment.csv are ignored (and a warning is thrown).

    Parameters:
    -----------
    fn_csv: str
        experiment.csv filename
    fn_hdf5: str
        experiment.hdf5 filename. File is created if not existing.
    overwrite_arr: bool
        Overwrite existing arrays. Otherwise: fail. Default: True.
    verbose: bool
        Print some information (default: false).

    """
    # fn_csv = "/data/pt_01756/tmp/write_exp_hdf/experiment_oc_dc.csv"
    # fn_hdf5 = "/data/pt_01756/tmp/write_exp_hdf/experiment.hdf5"
    # verbose = True
    csv_data = pd.read_csv(fn_csv)

    # save the following columns to hdf5
    cols2save = ["coil_sn", "current", "date", "time_diff", "time_mep", "time_tms", "ts_tms"]
    for missing_col in set(cols2save) - set(csv_data.columns):
        warnings.warn(f"{missing_col} not found in {fn_csv}")
    cols2save = list(set(cols2save) & set(csv_data.columns))

    for col_name, data in csv_data[cols2save].iteritems():
        if verbose:
            print(f"Adding {col_name} to {fn_hdf5}:/stim_data/{col_name}")

        data = data.values
        pynibs.write_arr_to_hdf5(fn_hdf5, f"/stim_data/{col_name}", data, overwrite_arr=overwrite_arr, verbose=verbose)

    # save coil coordinate information hdf5
    cols2save = ["coil0", "coil1", "coil_mean"]

    # the coil coordinates are stored as one column per cell, so get all columns that belong to coilX
    for col_name in cols2save:
        cols = [col for col in csv_data if col.startswith(col_name)]
        if not cols:
            warnings.warn(f"{col_name} not found in {fn_csv}")
            continue
        if verbose:
            print(f"Adding {col_name} to {fn_hdf5}:/stim_data/{col_name}")
        data = csv_data[cols].values

        if col_name == "coil0":
            col_name = "coil_0"
        if col_name == "coil1":
            col_name = "coil_1"

        pynibs.write_arr_to_hdf5(fn_hdf5, f"/stim_data/{col_name}", data, overwrite_arr=True, verbose=True)
        pynibs.write_arr_to_hdf5(fn_hdf5, f"/stim_data/{col_name}_columns", np.array(cols), overwrite_arr=True,
                                 verbose=True)


def cfs2hdf5(fn_cfs, fn_hdf5=None):
    """
    Converts EMG data included in .cfs file to .hdf5 format.

    Parameters
    ----------
    fn_cfs : str
        Filename of .cfs file
    fn_hdf5 : str, optional, default: None
        Filename of .hdf5 file (if not provided, a file with same name as fn_cfs will be created with .hdf5 extension)

    Returns
    -------
    <file> : .hdf5 File
        File containing:
        - EMG data in f["emg"][:]
        - Time axis in f["time"][:]
    """

    try:
        import biosig
    except ImportError:
        ImportError("Please install biosig from pynibs/pkg/biosig folder!")

    if fn_hdf5 is None:
        fn_hdf5 = os.path.splitext(fn_cfs)[0] + ".hdf5"

    # load header and data
    cfs_header = biosig.header(fn_cfs)
    emg = biosig.data(fn_cfs)[:, 0]

    sweep_index = cfs_header.find('NumberOfSweeps')
    comma_index = cfs_header.find(',', sweep_index)
    sweeps = int(cfs_header[sweep_index + 18:comma_index])
    records = emg.shape[0]
    samples = int(records / sweeps)
    sampling_rate = pynibs.get_mep_sampling_rate(fn_cfs)
    emg = np.reshape(emg, (sweeps, samples))
    time = np.linspace(0, samples, samples) / sampling_rate

    with h5py.File(fn_hdf5, "w") as f:
        f.create_dataset("emg", data=emg)
        f.create_dataset("time", data=time)
        f.create_dataset("sampling_rate", data=np.array([sampling_rate]))


def get_intensity_e(e1, e2, target1, target2, radius1, radius2, headmesh,
                    rmt=1, roi='midlayer_lh_rh', verbose=False):
    """
    Computes the stimulator intensity adjustment factor based on the electric field

    Parameters
    ----------
    e1 : str
        .hdf5 e field with midlayer
    e2 : str
        .hdf5 e field with midlayer
    target1 : np.ndarray (3,)
        Coordinates of cortical site of MT
    target2 : np.ndarray (3,)
        Coordinates of cortical target site
    radius1 : float
        Electric field of field1 is averaged over elements inside this radius around target1
    radius2 : float
        Electric field of field2 is averaged over elements inside this radius around target2
    headmesh : str
        .hdf5 headmesh
    rmt : float, optional, default=0
        Resting motor threshold to be corrected
    roi : str, optional, default='midlayer_lh_rh'
        Name of roi. Expected to sit in mesh['/data/midlayer/roi_surface/']
    verbose : bool, optional, Default: false
        Print verbosity information.

    Returns
    -------
    rmt_e_corr : float
        Adjusted stimulation intensity for target2
    """

    with h5py.File(headmesh, 'r') as f:
        tris = f[f'/roi_surface/{roi}/tri_center_coord_mid'][:]

    idx, e_avg_target, e_target, t_idx_sphere = [], [], [], []
    for field, target, radius in zip([e1, e2], [target1, target2], [radius1, radius2]):
        idx.append(np.argmin(np.linalg.norm(tris - target, axis=1)))
        t_idx_sphere.append(np.where(np.linalg.norm(tris - tris[idx[-1]], axis=1) < radius)[0])
        with h5py.File(field, 'r') as e:
            e_avg_target.append(np.mean(e[f'/data/midlayer/roi_surface/{roi}/E_mag'][t_idx_sphere[-1]]))
            e_target.append(e[f'/data/midlayer/roi_surface/{roi}/E_mag'][idx[-1]])

    # determine scaling factor
    e_fac_avg = e_avg_target[0] / e_avg_target[1]
    e_fac = e_target[0] / e_target[1]
    rmt_e_corr = rmt * e_fac_avg

    if verbose:
        print(f"Target1: {target1}->{tris[idx[0]]}. E: {e_target[0]:2.4f}, {len(t_idx_sphere[0])} elms")
        print(f"Target2: {target2}->{tris[idx[1]]}. E: {e_target[1]:2.4f}, {len(t_idx_sphere[0])} elms")
        print(f"Efield normalization factor: {e_fac_avg:2.4f} ({e_fac:2.4f} for single elm).")
        # print(f"Center: {target} { tris_center[t_idx, ]}.")
        print(f"Given intensity {rmt}% is normalized to {rmt * e_fac_avg:2.4f}%.")

    return rmt_e_corr


def get_intensity_e_old(mesh1, mesh2, target1, target2, radius1, radius2, rmt=1, verbose=False):
    """
    Computes the stimulator intensity adjustment factor based on the electric field

    Something weird is going on here - check simnibs coordinates of midlayer before usage.

    Parameters
    ----------
    mesh1 : str or simnibs.msh.mesh_io.Msh
        Midlayer mesh containing results of the optimal coil position of MT in the midlayer
        (e.g.: .../subject_overlays/00001.hd_fixed_TMS_1-0001_MagVenture_MCF_B65_REF_highres.ccd_scalar_central.msh)
    mesh2 : str or simnibs.msh.mesh_io.Msh
        Midlayer mesh containing results of the optimal coil position of the target in the midlayer
        (e.g.: .../subject_overlays/00001.hd_fixed_TMS_1-0001_MagVenture_MCF_B65_REF_highres.ccd_scalar_central.msh)
    target1 : np.ndarray (3,)
        Coordinates of cortical site of MT
    target2 : np.ndarray (3,)
        Coordinates of cortical target site
    radius1 : float
        Electric field in target 1 is averaged over elements inside this radius
    radius2 : float
        Electric field in target 2 is averaged over elements inside this radius
    rmt : float, optional, default=0
        Resting motor threshold, which will be corrected
    verbose : bool, optional, Default: false
        Print verbosity information.

    Returns
    -------
    rmt_e_corr : float
        Adjusted stimulation intensity for target2
    """
    from simnibs.msh.mesh_io import read_msh

    # load mesh1 (MT) if filename is provided
    if isinstance(mesh1, str):
        if os.path.splitext(mesh1)[1] == ".msh":
            mesh1 = read_msh(mesh1)
        elif os.path.splitext(mesh1)[1] == ".hdf5":
            mesh1 = pynibs.load_mesh_hdf5(mesh1)

    # load mesh2 (target) if filename is provided
    if isinstance(mesh2, str):
        if os.path.splitext(mesh2)[1] == ".msh":
            mesh2 = read_msh(mesh2)
        elif os.path.splitext(mesh2)[1] == ".hdf5":
            mesh2 = pynibs.load_mesh_hdf5(mesh2)

    # load electric fields in midlayer and average electric field around sphere in targets
    e_avg_target = []
    for mesh, target, radius in zip([mesh1, mesh2], [target1, target2], [radius1, radius2]):
        nodes = mesh.nodes.node_coord
        tris = mesh.elm.node_number_list[:, :-1] - 1
        tris_center = np.mean(nodes[tris,], axis=1)

        e_norm_nodes = None
        for nodedata in mesh.nodedata:
            if nodedata.field_name == "E_norm":
                e_norm_nodes = nodedata.value

        e_norm_tris = np.mean(e_norm_nodes[tris], axis=1)

        # project targets to midlayer
        t_idx = np.argmin(np.linalg.norm(tris_center - target, axis=1))

        # get indices of surrounding elements in some radius
        t_idx_sphere = np.where(np.linalg.norm(tris_center - tris_center[t_idx,], axis=1) < radius)[0]

        # average e-field in this area
        e_avg_target.append(np.mean(e_norm_tris[t_idx_sphere]))

        print(f"Center: {target} {tris_center[t_idx,]}.")

    # determine scaling factor
    e_fac = e_avg_target[0] / e_avg_target[1]
    rmt_e_corr = rmt * e_fac

    if verbose:
        print(f"Efield normalized factor is: {e_fac:2.4f}.")
        # print(f"Center: {target} { tris_center[t_idx, ]}.")
        print(f"Given stimulatior intensity {rmt}% is normalized to new intensity {rmt * e_fac:2.4f}%.")

    return rmt_e_corr


# def get_intensity_e(mesh1, mesh2, target1, target2, e1, e2, radius1, radius2, roi_idx=None,rmt=1, verbose=False):
#     # find node with minimum distance to target coordinate
#     sphere_t1 = tets_in_sphere(mesh1, target1, radius1)
#     sphere_t2 = tets_in_sphere(mesh2, target2, radius2,roi_idx)
#     # sphere_t2 = np.where(np.linalg.norm(mesh2.tetrahedra_center - target2, axis=1) <= radius)[0]
#
#     assert mesh1.tetrahedra_center.shape[0] == e1.shape[0]
#     assert mesh2.tetrahedra_center.shape[0] == e2.shape[0]
#     assert len(sphere_t1)
#     assert len(sphere_t2)
#     avg_e_t1 = np.mean(e1[sphere_t1])
#     avg_e_t2 = np.mean(e2[sphere_t2])
#     e_fac = avg_e_t1 / avg_e_t2
#
#     if verbose:
#         print(f"{len(sphere_t1)} tets found in field 1. Mean normE: {avg_e_t1:2.4f}")
#         print(f"{len(sphere_t2)} tets found in field 2. Mean normE: {avg_e_t2:2.4f}")
#
#         print(f"Efield normalized factor is: {e_fac:2.4f}.")
#         print(f"Given stimulatior intensity {rmt} is normalized to new intensity {rmt * e_fac:2.4f}.")
#
#     return e_fac*rmt


def get_intensity_stokes(mesh, target1, target2, spat_grad=3, rmt=0, verbose=False, scalp_tag=1005, roi=None):
    """
    Computes the stimulator intensity adjustment factor according to Stokes et al. 2005
    (doi:10.1152/jn.00067.2005).
    Adjustment is based on target-scalp distance differences:
    adj = (Dist2-Dist1)*spat_grad

    Parameters
    ----------
    mesh : str or simnibs.msh.mesh_io.Msh
        Mesh of the head model
    target1 : np.ndarray (3,)
        Coordinates of cortical site of MT
    target2 : np.ndarray (3,)
        Coordinates of cortical target site
    spat_grad : float
        Spatial gradient. Default: 3
    rmt : float, optional, default=0
        Resting motor threshold, which will be corrected
    scalp_tag: int, optional, default: 1005
        Tag in the mesh where the scalp is to be set. Default: 1005
    verbose : bool, optional, Default: false
        Print verbosity information.
    roi: np.ndarray (3,N)
        Array of nodes to project targets onto

    Returns
    -------
    rmt_stokes : float
        Adjusted stimulation intensity for target2
    """
    from simnibs.msh.mesh_io import read_msh
    from pynibs.mesh import project_on_scalp

    # load mesh if filename is provided
    if isinstance(mesh, str):
        if os.path.splitext(mesh)[1] == ".msh":
            mesh = read_msh(mesh)
        elif os.path.splitext(mesh)[1] == ".hdf5":
            mesh = pynibs.load_mesh_hdf5(mesh)

    t1_proj = project_on_scalp(target1, mesh, scalp_tag=scalp_tag)
    t2_proj = project_on_scalp(target2, mesh, scalp_tag=scalp_tag)

    if roi is not None:
        t1_idx = np.argmin(np.linalg.norm(roi - target1, axis=1))
        t2_idx = np.argmin(np.linalg.norm(roi - target2, axis=1))
        t1_on_roi = roi[t1_idx]
        t2_on_roi = roi[t2_idx]

        if verbose:
            print("Projecting targets on ROI:\n"
                  "T1: [{0:+06.2f}, {1:+06.2f}, {2:+06.2f}] -> [{3:+06.2f}, {4:+06.2f}, {5:+06.2f}] Dist: {6:05.2f}mm"
                  "\n".format(*target1, *t1_on_roi, np.linalg.norm(target1 - t1_on_roi)) + \
                  "T2: [{0:+06.2f}, {1:+06.2f}, {2:+06.2f}] -> [{3:+06.2f}, {4:+06.2f}, {5:+06.2f}] Dist: {6:05.2f}mm"
                  "".format(*target2, *t2_on_roi, np.linalg.norm(target2 - t2_on_roi)))
        target1 = t1_on_roi
        target2 = t2_on_roi

    t1_dist = np.linalg.norm(target1 - t1_proj)
    t2_dist = np.linalg.norm(target2 - t2_proj)

    stokes_factor = (t2_dist - t1_dist) * spat_grad
    rmt_stokes = rmt + stokes_factor

    if verbose:
        print("Target 1: [{0:+06.2f}, {1:+06.2f}, {2:+06.2f}] ->"
              " [{3:+06.2f}, {4:+06.2f}, {5:+06.2f}] Dist: {6:05.2f}mm ".format(*target1, *t1_proj.flatten(), t1_dist))
        print("Target 2: [{0:+06.2f}, {1:+06.2f}, {2:+06.2f}] ->"
              " [{3:+06.2f}, {4:+06.2f}, {5:+06.2f}] Dist: {6:05.2f}mm ".format(*target2, *t2_proj.flatten(), t2_dist))
        print(f"Dist1 - Dist2: {t1_dist - t2_dist:05.2f} mm")
        print(f"rMT Stokes corrected: {rmt_stokes:05.2f} %MSO")

    return rmt_stokes
