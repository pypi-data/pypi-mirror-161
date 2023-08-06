import os
import warnings

import h5py
import pickle
import numpy as np
import pynibs


class Subject:
    """
    Subject containing subject specific information, like mesh, roi, uncertainties, plot settings.

    Attributes
    ----------
    self.id : str
        Subject id from MPI database

    Notes
    -----
    **Initialization**

    sub = subject(subject_ID, mesh)

    **Parameters**

    id : str
        Subject id
    fn_mesh : str
         .msh or .hdf5 file containing the mesh information


    **Subject.seg, segmentation information dictionary**

    fn_lh_wm : str
        Filename of left hemisphere white matter surface
    fn_rh_wm : str
        Filename of right hemisphere white matter surface
    fn_lh_gm : str
        Filename of left hemisphere grey matter surface
    fn_rh_gm : str
        Filename of right hemisphere grey matter surface
    fn_lh_curv : str
        Filename of left hemisphere curvature data on grey matter surface
    fn_rh_curv : str
        Filename of right hemisphere curvature data on grey matter surface

    **Subject.mri, mri information dictionary**

    fn_mri_T1 : str
        Filename of T1 image
    fn_mri_T2 : str
        Filename of T2 image
    fn_mri_DTI : str
        Filename of DTI dataset
    fn_mri_DTI_bvec : str
        Filename of DTI bvec file
    fn_mri_DTI_bval : str
        Filename of DTI bval file
    fn_mri_conform : str
        Filename of conform T1 image resulting from SimNIBS mri2mesh function

    **Subject.ps, plot settings dictionary**

    see plot functions in para.py for more details

    **Subject.exp, experiment dictionary**

    info : str
        General information about the experiment
    date : str
        Date of experiment (e.g. 01/01/2018)
    fn_tms_nav : str
        Path to TMS navigator folder
    fn_data : str
        Path to data folder or files
    fn_exp_csv : str
        Filename of experimental data .csv file containing the merged experimental data information
    fn_coil : str
        Filename of .ccd or .nii file of coil used in the experiment (contains ID)
    fn_mri_nii : str
        Filename of MRI .nii file used during the experiment
    cond : str or list of str
        Conditions in the experiment in the recorded order (e.g. ['PA-45', 'PP-00'])
    experimenter : str
        Name of experimenter who conducted the experiment
    incidents : str
        Description of special events occured during the experiment

    **Subject.mesh, mesh dictionary**

    info : str
        Information about the mesh (e.g. dicretization etc)
    fn_mesh_msh : str
        Filename of the .msh file containing the FEM mesh
    fn_mesh_hdf5 : str
        Filename of the .hdf5 file containing the FEM mesh
    seg_idx : int
        Index indicating to which segmentation dictionary the mesh belongs

    **Subject.roi region of interest dictionary**

    type : str
        Specify type of ROI ('surface', 'volume')
    info : str
        Info about the region of interest, e.g. "M1 midlayer from freesurfer mask xyz"
    region : list of str or float
        Filename for freesurfer mask or [[X_min, X_max], [Y_min, Y_max], [Z_min, Z_max]]
    delta : float
        Distance parameter between WM and GM (0 -> WM, 1 -> GM) (for surfaces only)

    """

    def __init__(self, subject_id, subject_folder):
        self.id = subject_id  # subject id
        self.subject_folder = subject_folder  # folder containing subject information
        self.mri = []  # list containing mri information
        self.mesh = {}  # dict containing mesh information
        self.exp = {}  # dict containing information about conducted experiments
        self.ps = []  # list containing plot settings
        self.roi = {}  # dict containing the roi information

    def add_mesh_info(self, mesh_dict):
        """
        Adding filename information of the mesh to the subject object (multiple filenames possible).

        Parameters
        ----------
        mesh_dict : dictionary or list of dictionaries
            Dictionary containing the mesh information

        Notes
        -----
        **Adds Attributes**

        Subject.mesh : list of dict
            Dictionaries containing the mesh information
        """
        if type(mesh_dict) is list:
            for mesh in mesh_dict:
                self.mesh.append(mesh)

        else:
            self.mesh = mesh_dict

    def add_roi_info(self, roi_dict):
        """
        Adding ROI (surface) information of the mesh with mesh_index to the subject object (multiple ROIs possible).

        Parameters
        ----------
        roi_dict : dict of dict or list of dictionaries
            Dictionary containing the ROI information of the mesh with mesh_index [mesh_idx][roi_idx]

        Notes
        -----
        **Adds Attributes**

        Subject.mesh[mesh_index].roi : list of dict
            Dictionaries containing ROI information
        """

        for mesh_idx in roi_dict.keys():
            self.roi[mesh_idx] = dict()

            for roi_idx in roi_dict[mesh_idx].keys():
                self.roi[mesh_idx][roi_idx] = roi_dict[mesh_idx][roi_idx]

    def add_plotsettings(self, ps_dict):
        """
        Adding ROI information to the subject object (multiple ROIs possible).

        Parameters
        ----------
        ps_dict : dictionary or list of dictionaries
            Dictionary containing plot settings of the subject

        Notes
        -----
        **Adds Attributes**

        Subject.ps : list of dict
            Dictionary containing plot settings of the subject
        """

        if type(ps_dict) is not list:
            ps_dict = [ps_dict]

        for ps in ps_dict:
            self.ps.append(ps)

    def add_mri_info(self, mri_dict):
        """
        Adding MRI information to the subject object (multiple MRIs possible).

        Parameters
        ----------
        mri_dict : dictionary or list of dictionaries
            Dictionary containing the MRI information of the subject

        Notes
        -----
        **Adds Attributes**

        Subject.mri : list of dict
            Dictionary containing the MRI information of the subject
        """

        if type(mri_dict) is not list:
            mri_dict = [mri_dict]

        for mri in mri_dict:
            self.mri.append(mri)

    @staticmethod
    def _prep_fn(val):
        if type(val) is dict:
            pass
        elif type(val) is not list:
            val = [val]
            for j in range(len(val)):
                _ = check_file_and_format(val[j])
        return val

    def add_experiment_info(self, exp_dict):
        """
        Adding information about a particular experiment.

        Parameters
        ----------
        exp_dict : dict of dict or list of dict
            Dictionary containing information about the experiment

        Notes
        -----
        **Adds Attributes**

        exp : list of dict
            Dictionary containing information about the experiment
        """
        fns = ['fn_data', 'fn_coil', 'fn_mri_nii']
        if exp_dict is None:
            return

        # if type(exp_dict) is not list:
        #     exp_dict = [exp_dict
        # check if files and folder exist and convert to list
        for i in exp_dict.keys():

            # # fn_tms_nav
            # if type(exp_dict[i]['fn_tms_nav']) is not list:
            #     exp_dict[i]['fn_tms_nav'] = [exp_dict[i]['fn_tms_nav']]
            # for j in range(len(exp_dict[i]['fn_tms_nav'])):
            #     _ = check_file_and_format(exp_dict[i]['fn_tms_nav'][j])

            # fn_data
            for fn in fns:
                try:
                    exp_dict[i][fn] = self._prep_fn(exp_dict[i][fn])
                except KeyError:
                    pass

            # new subject files have 'cond' as dictionary
            if 'cond' in exp_dict[i].keys():
                if isinstance(exp_dict[i]['cond'], dict):
                    for cond_name in exp_dict[i]['cond'].keys():
                        for fn in fns:
                            try:
                                exp_dict[i]['cond'][cond_name][fn] = self._prep_fn(exp_dict[i]['cond'][cond_name][fn])
                            except KeyError:
                                pass
            else:
                exp_dict[i]['cond'] = [[""]]

        for exp in exp_dict:
            self.exp[exp] = exp_dict[exp]


def fill_from_dict(self, d):
    """
    Set all attributes from d in object self.

    Parameters:
    -----------
    d : dict
    """

    for key, value in d.items():
        if not hasattr(self, f"{key}"):
            warnings.warn(f"{key} not existing.")
        setattr(self, key, value)

    return self


def save_subject(subject_id, subject_folder, fname, mri_dict=None, mesh_dict=None, roi_dict=None,
                 exp_dict=None, ps_dict=None, **kwargs):
    """
    Saving subject information in .pkl or .hdf5 format (preferred)

    Parameters
    ----------
    subject_id : str
        ID of subject
    subject_folder : str
        Subject folder
    fname : str
        Filename with .hdf5 or .pkl extension (incl. path)
    mri_dict : list of dict, optional, default: None
        MRI info
    mesh_dict : list of dict, optional, default: None
        Mesh info
    roi_dict : list of list of dict, optional, default: None
        Mesh info
    exp_dict : list of dict, optional, default: None
        Experiment info
    ps_dict : list of dict, optional, default:None
        Plot-settings info
    kwargs : str or np.array
        Additional information saved in the parent folder of the .hdf5 file

    Returns
    -------
    <File> : .hdf5 file
        Subject information
    """
    filetype = os.path.splitext(fname)[1]

    if filetype == ".hdf5":
        if os.path.exists(fname):
            os.remove(fname)

        save_subject_hdf5(subject_id=subject_id,
                          subject_folder=subject_folder,
                          fname=fname,
                          mri_dict=mri_dict,
                          mesh_dict=mesh_dict,
                          roi_dict=roi_dict,
                          exp_dict=exp_dict,
                          ps_dict=ps_dict,
                          **kwargs)

    elif filetype == ".pkl":
        raise NotImplementedError
        #
        # # create and initialize subject
        # subject = Subject(subject_id=subject_id)
        #
        # # add mri information
        # subject.add_mri_info(mri_dict=mri_dict)
        #
        # # add mesh information
        # subject.add_mesh_info(mesh_dict=mesh_dict)
        #
        # # add roi info to mesh
        # subject.add_roi_info(roi_dict=roi_dict)
        #
        # # add experiment info
        # subject.add_experiment_info(exp_dict=exp_dict)
        #
        # # add plotsettings
        # subject.add_plotsettings(ps_dict=ps_dict)
        #
        # save_subject_pkl(sobj=subject, fname=fname)


def save_subject_pkl(sobj, fname):
    """
    Saving subject object as pickle file.

    Parameters
    ----------
    sobj: object
        Subject object to save
    fname: str
        Filename with .pkl extension

    Returns
    -------
    <File> : .pkl file
        Subject object instance
    """

    if type(fname) is list:
        fname = fname[0]

    with open(fname, 'wb') as output:
        pickle.dump(sobj, output, -1)


def save_subject_hdf5(subject_id, subject_folder, fname, mri_dict=None, mesh_dict=None, roi_dict=None,
                      exp_dict=None, ps_dict=None, overwrite=True, check_file_exist=False, verbose=False, **kwargs):
    """
    Saving subject information in hdf5 file.

    Parameters
    ----------
    subject_id : str
        ID of subject
    subject_folder : str
        Subject folder
    fname : str
        Filename with .hdf5 extension (incl. path)
    mri_dict : list of dict, optional, default: None
        MRI info
    mesh_dict : list of dict, optional, default: None
        Mesh info
    roi_dict : list of list of dict, optional, default: None
        Mesh info
    exp_dict : list of dict or dict of dict, optional, default: None
        Experiment info
    ps_dict : list of dict, optional, default:None
        Plot-settings info
    overwrite : bool
        Overwrites existing .hdf5 file
    check_file_exist : bool
        Hide warnings.
    verbose : bool
        Print information about meshes and ROIs.
    kwargs : str or np.ndarray
        Additional information saved in the parent folder of the .hdf5 file

    Returns
    -------
    <File> : .hdf5 file
        Subject information
    """

    assert fname.endswith('.hdf5')

    if overwrite and os.path.exists(fname):
        os.remove(fname)

    with h5py.File(fname, 'a') as f:
        f["subject_id"] = np.array(subject_id).astype("|S")
        f["subject_folder"] = np.array(subject_folder).astype("|S")

    if mri_dict is not None:
        if isinstance(mri_dict, list):
            mri_dict = {i: mri_dict[i] for i in range(len(mri_dict))}

        for i in mri_dict.keys():
            pynibs.write_dict_to_hdf5(fn_hdf5=fname, data=mri_dict[i], folder=f"mri/{i}", check_file_exist=True)

    if mesh_dict is not None:
        if isinstance(mesh_dict, list):
            mesh_dict = {i: mesh_dict[i] for i in range(len(mesh_dict))}

        for mesh_name, mesh_dict in mesh_dict.items():
            mesh = pynibs.Mesh(mesh_name=mesh_name, subject_id=subject_id, subject_folder=subject_folder)
            mesh.fill_defaults(mesh_dict['approach'])
            mesh = fill_from_dict(mesh, mesh_dict)
            mesh.write_to_hdf5(fn_hdf5=fname, check_file_exist=check_file_exist, verbose=verbose)

    if roi_dict is not None:
        for mesh_name in roi_dict.keys():
            for roi_name, roi_dict_i in roi_dict[mesh_name].items():
                roi = pynibs.ROI(subject_id=subject_id, roi_name=roi_name, mesh_name=mesh_name)
                roi = fill_from_dict(roi, roi_dict_i)
                roi.write_to_hdf5(fn_hdf5=fname, check_file_exist=check_file_exist, verbose=verbose)

    if exp_dict is not None:
        if isinstance(exp_dict, list):
            exp_dict = {i: exp_dict[i] for i in range(len(exp_dict))}
        for i in exp_dict.keys():
            pynibs.write_dict_to_hdf5(fn_hdf5=fname, data=exp_dict[i], folder=f"exp/{i}",
                                      check_file_exist=check_file_exist)

    if ps_dict is not None:
        for i in range(len(ps_dict)):
            pynibs.write_dict_to_hdf5(fn_hdf5=fname, data=ps_dict[i], folder=f"ps/{i}",
                                      check_file_exist=check_file_exist)

    with h5py.File(fname, 'a') as f:
        for key, value in kwargs.items():
            try:
                del f[key]
            except KeyError:
                pass
            f.create_dataset(name=key, data=value)


def load_subject_hdf5(fname):
    """
    Loading subject information from .hdf5 file and returning subject object.

    Parameters
    ----------
    fname : str
        Filename with .hdf5 extension (incl. path)

    Returns
    -------
    subject : Subject object
        Loaded Subject object
    """

    with h5py.File(fname, 'r') as f:
        subject_id = str(f["subject_id"][()].astype(str))
        subject_folder = str(f["subject_folder"][()].astype(str))

        # create and initialize subject
        subject = Subject(subject_id=subject_id, subject_folder=subject_folder)

        # add mri information
        try:
            mri_keys = f["mri"].keys()
            mri = []

            for key in mri_keys:
                mri.append(pynibs.read_dict_from_hdf5(fn_hdf5=fname, folder=f"mri/{key}"))

        except KeyError:
            mri = None

        subject.add_mri_info(mri_dict=mri)

        # add mesh information
        try:
            mesh_keys = f["mesh"].keys()
            mesh = {}

            for key in mesh_keys:
                mesh[key] = pynibs.read_dict_from_hdf5(fn_hdf5=fname, folder=f"mesh/{key}")

        except KeyError:
            mesh = None

        subject.add_mesh_info(mesh_dict=mesh)

        # add roi info
        try:
            mesh_idx_keys = f["roi"].keys()
            roi = dict()

            for mesh_idx in mesh_idx_keys:
                try:
                    roi_idx_keys = f[f"roi/{mesh_idx}"].keys()
                    roi[mesh_idx] = dict()

                    for roi_idx in roi_idx_keys:
                        roi[mesh_idx][roi_idx] = pynibs.read_dict_from_hdf5(fn_hdf5=fname,
                                                                            folder=f"roi/{mesh_idx}/{roi_idx}")

                except KeyError:
                    roi[mesh_idx] = None

            subject.add_roi_info(roi_dict=roi)

        except KeyError:
            pass

        # add experiment information
        try:
            exp_keys = f["exp"].keys()
            exp = {}

            for key in exp_keys:
                exp[key] = pynibs.read_dict_from_hdf5(fn_hdf5=fname, folder=f"exp/{key}")

        except KeyError:
            exp = None

        subject.add_experiment_info(exp_dict=exp)

        # add plotsettings information
        try:
            ps_keys = f["ps"].keys()
            ps = []

            for key in ps_keys:
                ps.append(pynibs.read_dict_from_hdf5(fn_hdf5=fname, folder=f"ps/{key}"))

        except KeyError:
            ps = None

        subject.add_plotsettings(ps_dict=ps)

    return subject


def load_subject(fname, filetype=None):
    """
    Wrapper for pkl and hdf5 subject loader

    Parameters
    ----------
    fname: str
        endwith('.pkl') | endswith('.hdf5')
    filetype: str
        Explicitely set file version.
    """

    # explicit set fname type
    if filetype:
        if filetype.lower().endswith("hdf5"):
            filetype = "hdf5"
        elif filetype.lower().endswith("pkl"):
            filetype = "pkl"
        else:
            raise NotImplementedError(f"{filetype} unknown.")

    # determine fname type from file-ending
    else:
        if fname.lower().endswith("hdf5"):
            filetype = "hdf5"
        elif fname.lower().endswith("pkl"):
            filetype = "pkl"
        else:
            raise NotImplementedError(f"{fname} type unknown.")

    # load file using correct load function
    if filetype == "hdf5":
        return load_subject_hdf5(fname)
    elif filetype == "pkl":
        return load_subject_pkl(fname)


def load_subject_pkl(fname):
    """
    Loading subject object from .pkl file.

    Parameters
    ----------
    fname : str
        Filename with .pkl extension

    Returns
    -------
    subject : Subject object
        Loaded Subject object
    """

    try:
        with open(fname, 'rb') as f:
            return pickle.load(f)

    except UnicodeDecodeError:
        print(".pkl file version does not match python version... recreating subject object")
        fn_scipt = os.path.join(os.path.split(fname)[0],
                                "create_subject_" +
                                os.path.splitext(os.path.split(fname)[1])[0] + ".py")
        pynibs.bash_call("python {}".format(fn_scipt))

        with open(fname, 'rb') as f:
            return pickle.load(f)


def check_file_and_format(fname):
    """
    Checking existence of file and transforming to list if necessary.

    Parameters
    ----------
    fname: str or list of str
        Filename(s) to check

    Returns
    -------
    fname: list of str
        Checked filename(s) as list
    """

    if type(fname) is not list:
        fname = [fname]

    for fn in fname:
        if not (os.path.exists(fn)):
            Exception('File/Folder {} does not exist!'.format(fn))

    return fname
