import platform
import shutil
import numpy as np
import nibabel as nib
import meshio
import os
from .mesh import map_data_to_surface, data_nodes2elements, data_elements2nodes
from .util import *
from .hdf5_io import write_geo_hdf5_surf
from .hdf5_io import write_data_hdf5_surf
from .roi import make_GM_WM_surface
from .subject import *
import nibabel


def read_curv_data(fname_curv, fname_inf, raw=False):
    """
    Read curvature data provided by freesurfer and optionally process it.

    Parameters
    ----------
    fname_curv : str
        Filename of the freesurfer curvature file (e.g. ?h.curv), contains curvature data in nodes
        can be found in mri2mesh proband folder: /proband_ID/fs_ID/surf/?h.curv
    fname_inf : str
        Filename of inflated brain surface (e.g. ?h.inflated), contains points and connectivity data of surface
        can be found in mri2mesh proband folder: /proband_ID/fs_ID/surf/?h.inflated
    raw : boolean
        Decide if raw-data is returned or if the data is normalized to -1 for neg. and +1 for pos. curvature

    Returns
    -------
    curv : nparray of float or int
        Curvature data in element centers
    """

    # load curvature data
    curv_points = nibabel.freesurfer.io.read_morph_data(fname_curv)

    # load inflated brain surface data
    points_inf, con_inf = nibabel.freesurfer.read_geometry(fname_inf)

    # interpolate point data to element centers
    curv = data_nodes2elements(curv_points, con_inf)

    # normalize curvature data (optional)
    if not raw:
        curv[curv > 0] = 1
        curv[curv < 0] = -1

    return curv


def make_group_average(subjects=None, subject_dir=None, average=None, hemi="lh", template="mytemplate", steps=3,
                       n_cpu=2, average_dir=None):
    """
    Creates a group average from scratch, based on one subject. This prevents for example the fsaverage problems of
    large elements at M1, etc.

    Parameters
    ----------
    subjects : list of str
        List of freesurfer subjects names
    subject_dir : str
            temporary subject directory of freesurfer (symlinks of subjects will be generated in there and average
            template will be temporarily stored before it is copied to average_dir)
    average: string (Optional)
        Which subject to base new average template on? Default: subjects[0]
    hemi : string (Optional)
        lh or rh
    template : string <Default: mytemplate>
        Basename of new template
    steps : int <Default: 2>
        Number of iterations
    n_cpu : int <Default: 4>
        How many cores for multithreading?
    average_dir : str
        Path to directory where average template will be stored
        (e.g.: probands/avg_template_15/mesh/0/fs_avg_template_15)

    Returns
    -------
    <File> : .tif file
        SUBJECT_DIR/TEMPLATE*.tif, TEMPLATE0.tif based on AVERAGE, rest on all subjects
    <File> : .myreg file
        SUBJECT_DIR/SUBJECT*/surf/HEMI.sphere.myreg*
    <File> : .tif file
        Subject wise sphere registration based on TEMPLATE*.tif
    """
    subject_names = [os.path.split(subjects[i])[1] for i in range(len(subjects))]

    # define $SUBJECT_DIR of FREESURFER
    if not os.path.exists(subject_dir):
        print(('Creating $SUBJECTS_DIR in {}'.format(subject_dir)))
        os.makedirs(subject_dir)
    print(('Set environment variable of freesurfer SUBJECTS_DIR={}'.format(subject_dir)))
    os.putenv('SUBJECTS_DIR', subject_dir)

    # make symlinks of subjects in $SUBJECT_DIR
    for i, subject in enumerate(subjects):
        if not os.path.exists(os.path.join(subject_dir, subject_names[i])):
            print(('Generating symlink of subject {} in {}'.format(subject_names[i], subject_dir)))
            bash('ln -s ' + subject + ' ' + subject_dir)

    # if not subject_dir:
    #     subject_dir = "/data/pt_01756/tmp/fs_ownav/"
    # if not subject_dir.endswith('/'):
    #     subject_dir += '/'
    # if template.endswith(".tif"):
    #     template = template[:-4]

    os.chdir(subject_dir)

    # if not subjects:
    #     subjects = ["fs_15484.08",
    #                 "fs_08950.3f"]  # , "fs_09440.22", "fs_14102.d1", "fs_15891.1c", "fs_19925.e6", "fs_22793.3b",
    #                    "fs_24417.b5", "fs_26824.0f", "fs_28027.87", "fs_28093.e5", "fs_29721.12", "fs_29965.48",
    #                    "fs_30252.51", "fs_31715.c2", "fs_18080.2d"]

    if not average:
        average = subjects[0]

    print("Creating initial template")
    "mris_make_template lh sphere fs_15484.08 ./templates.tif"

    command = "FREESURFER mris_make_template {} sphere {} lh{}0.tif".format("lh", os.path.split(average)[1], template)
    os.system(command)
    command = "FREESURFER mris_make_template {} sphere {} rh{}0.tif".format("rh", os.path.split(average)[1], template)
    os.system(command)
    # print command

    processes = set()
    for i in range(steps):
        command = "FREESURFER mris_register"
        print("\n\nStep {}".format(i))
        print("############################################################################################")
        # start all subjects registrations to .tif* in parallel
        for subject in subjects:
            # print "{}/surf/{}.sphere {}{}.tif {}.sphere.myreg{}".format(subject, hemi, template, i, hemi, i)
            # print [command, "{}/surf/{}.sphere {}{}.tif {}.sphere.myreg{}".format(subject,
            # hemi, template, i, hemi, i)]
            processes.add(subprocess.Popen(
                    [f'{command} '
                     f'{os.path.split(subject)[1]}{os.sep}surf{os.sep}lh.sphere lh{template}{i}.tif '
                     f'{"lh"}.sphere.{template}{i}'],
                    shell=True))
            processes.add(subprocess.Popen(
                    [f"{command} "
                     f"{os.path.split(subject)[1]}{os.sep}surf{os.sep}rh.sphere rh{template}{i}.tif "
                     f"{'rh'}.sphere.{template}{i}"],
                    shell=True))

            # check if n_cpu processes are reached
            if len(processes) >= n_cpu:
                os.wait()
                processes.difference_update([p for p in processes if p.poll() is not None])

            #        for subject in subjects:
            #           print "        mris_register step {}{}".format(i, subject)
            #         command = "FREESURFER mris_register {}/surf/{}.sphere {}{}.tif
            #         {}.sphere.myreg{}".format(subject,hemi,template,i,hemi,i)
            #       print command
            #     os.system(command)
        # needed? wait for all processes to finish
        while len(processes) > 0:
            os.wait()
            processes.difference_update([p for p in processes if p.poll() is not None])

        short_subjects = [os.path.split(subject)[1] for subject in subjects]
        print("        making template for step {}".format(i))
        # command = "FREESURFER mris_make_template {} sphere {} rh{}0.tif".format("rh", os.path.split(average)[1],
        #                                                                         template)
        command = f"FREESURFER mris_make_template {'rh'} sphere.{template}{i} {' '.join(short_subjects)} " \
                  f"rh{template}{i + 1}.tif"
        print(command)
        os.system(command)

        command = f"FREESURFER mris_make_template {'lh'} sphere.{template}{i} {' '.join(short_subjects)} " \
                  f"lh{template}{i + 1}.tif"
        print(command)
        os.system(command)

        print("##################### Iteration {} done. #####################\n".format(i))

    print('Creating average surfaces and volumes of average subject')
    make_average_subject(subjects=subjects,
                         subject_dir=subject_dir,
                         average_dir=average_dir,
                         fn_reg='sphere.{}{}'.format(template, steps - 1))


def make_average_subject(subjects, subject_dir, average_dir, fn_reg='sphere.reg'):
    """
    Generates the average template from a list of subjects using the freesurfer average.

    Parameters
    ----------
    subjects : list of str
        paths of subjects directories, where the freesurfer files are located
        (e.g.: for simnibs mri2mesh .../fs_SUBJECT_ID)
    subject_dir : str
        temporary subject directory of freesurfer (symlinks of subjects will be generated in there and average
        template will be temporarily stored before it is copied to average_dir)
    average_dir : str
        path to directory where average template will be stored
        (e.g.: probands/avg_template_15/mesh/0/fs_avg_template_15
    fn_reg : str <Default: sphere.reg --> ?h.sphere.reg>
        Filename suffix of freesurfer registration file containing registration information to template

    Returns
    -------
    <Files> : .tif and .reg files
        Average template in average_dir and registered curvature files, ?h.sphere.reg in subjects/surf folders
    """

    subject_names = [os.path.split(subjects[i])[1] for i in range(len(subjects))]

    # check for right operating system
    if platform.system() != 'Linux':
        raise OSError('Average template can only be generated with linux because of FREESURFER requirements!')

    # check if FREESURFER is installed
    output = bash('which FREESURFER')
    if not output:
        raise Exception('FREESURFER not installed! Please visit https://freesurfer.net/ for more information')

    # define $SUBJECT_DIR of FREESURFER
    if not os.path.exists(subject_dir):
        print(('Creating $SUBJECTS_DIR in {}'.format(subject_dir)))
        os.makedirs(subject_dir)
    print(('Set environment variable of freesurfer SUBJECTS_DIR={}'.format(subject_dir)))
    os.putenv('SUBJECTS_DIR', subject_dir)

    # make symlinks of subjects in $SUBJECT_DIR
    for i, subject in enumerate(subjects):
        if not os.path.exists(os.path.join(subject_dir, subject_names[i])):
            print(('Generating symlink of subject {} in {}'.format(subject_names[i], subject_dir)))
            bash('ln -s ' + subject + ' ' + subject_dir)

    # make average template
    if os.path.exists(f'{subject_dir}{os.sep}avg_template'):
        shutil.rmtree(f'{subject_dir}{os.sep}avg_template')
    print(('Generating average subject in {}/avg_template'.format(subject_dir)))
    print('==============================================')
    command = 'FREESURFER make_average_subject ' \
              '--out avg_template ' \
              ' --subjects ' + " ".join(subject_names) + \
              ' --surf-reg ' + fn_reg

    os.system(command)

    # copy average template to average_dir
    print(('Moving average template to {}'.format(average_dir)))
    os.system('mv $SUBJECTS_DIR/avg_template ' + average_dir)


def data_sub2avg(fn_subject_obj, fn_average_obj, hemisphere, fn_in_hdf5_data, data_hdf5_path, data_label,
                 fn_out_hdf5_geo, fn_out_hdf5_data, mesh_idx=0, roi_idx=0, subject_data_in_center=True,
                 data_substitute=-1, verbose=True, replace=True, reg_fn="sphere.reg"):
    """
    Maps the data from the subject space to the average template. If the data is given only in an ROI, the data is
    mapped to the whole brain surface.

    Parameters
    ----------
    fn_subject_obj : str
        Filename of subject object .pkl file (incl. path)
        (e.g.: .../probands/subjectID/subjectID.pkl)
    fn_average_obj : str
        Filename of average template object .pkl file (incl. path)
        (e.g.: .../probands/avg_template/avg_template.pkl)
    hemisphere : str
        Define hemisphere to work on ('lh' or 'rh' for left or right hemisphere, respectively)
    fn_in_hdf5_data : str
        Filename of .hdf5 data input file containing the subject data
    data_hdf5_path : str
        Path in .hdf5 data file where data is stored (e.g. '/data/tris/')
    data_label : str or list of str
        Label of datasets contained in hdf5 input file to map
    fn_out_hdf5_geo : str
        Filename of .hdf5 geo output file containing the geometry information
    fn_out_hdf5_data : str
        Filename of .hdf5 data output file containing the mapped data
    mesh_idx : int
        Index of mesh used in the simulations
    roi_idx : int
        Index of region of interest used in the simulations
    subject_data_in_center : boolean
        Specify if the data is given in the center of the triangles or in the nodes (Default = True)
    data_substitute : float
        Data substitute with this number for all points outside the ROI mask
    verbose : boolean
        Verbose output (Default: True)
    replace : boolean
        Replace output files (Default: True)
    reg_fn : string
        Sphere.reg fn

    Returns
    -------
    <Files> : .hdf5 files
        Geometry and corresponding data files to plot with Paraview:

        - fn_out_hdf5_geo.hdf5: geometry file containing the geometry information of the average template
        - fn_out_hdf5_data.hdf5: geometry file containing the data
    """

    subject = load_subject(fname=fn_subject_obj)
    average = load_subject(fname=fn_average_obj)

    mesh_folder_avg = average.mesh["0"]["mesh_folder"]
    mesh_folder_sub = subject.mesh[mesh_idx]["mesh_folder"]

    fn_sub_gm = subject.mesh[mesh_idx]['fn_' + hemisphere + '_gm']
    fn_sub_wm = subject.mesh[mesh_idx]['fn_' + hemisphere + '_wm']
    fn_avg_gm = average.mesh[mesh_idx]['fn_' + hemisphere + '_gm']
    fn_avg_wm = average.mesh[mesh_idx]['fn_' + hemisphere + '_wm']

    # freesurfer folder, e.g.: /data/pt_01756/probands/subject[i].id + '/mesh/0/fs_' + subject[i].id
    subject_dir = os.path.split(os.path.split(fn_sub_gm)[0])[0]
    average_dir = os.path.split(os.path.split(fn_avg_gm)[0])[0]

    # filename of mapped subject data in nodes in .curv format for freesurfer (will be generated)
    fn_data_sub_nodes_mapped_curv = [os.path.join(
            os.path.split(fn_out_hdf5_geo)[0],
            hemisphere + '.' +
            os.path.split(subject_dir)[1] +
            '_' +
            data_label[i] +
            '.curv')
        for i in range(len(data_label))]

    # filename of mapped subject data in nodes on average template in .curv format for freesurfer (will be generated)
    fn_data_sub_nodes_mapped_avg_curv = [os.path.join(
            os.path.split(fn_data_sub_nodes_mapped_curv[i])[0],
            os.path.splitext(os.path.split(fn_data_sub_nodes_mapped_curv[i])[1])[0] +
            '_avg.curv')
        for i in range(len(data_label))]

    if verbose:
        print('> Generating GM/WM surface on average template')
    points_avg, con_avg = make_GM_WM_surface(gm_surf_fname=fn_avg_gm,
                                             wm_surf_fname=fn_avg_wm,
                                             mesh_folder=mesh_folder_avg,
                                             delta=subject.roi[mesh_idx][roi_idx]['delta'],
                                             layer=1)
    files_not_exist = not np.array([os.path.exists(fn_data_sub_nodes_mapped_avg_curv[i]) for
                                    i in range(len(data_label))]).all()

    if files_not_exist or replace:

        # Generate WM/GM surfaces of subject and average template
        if verbose:
            print(("> Reading ROI #{} of subject ...".format(roi_idx)))

        with h5py.File(subject.mesh[mesh_idx]['fn_mesh_hdf5'], 'r') as f:
            points_roi = np.array(f['roi_surface/' + str(roi_idx) + '/node_coord_mid'])
            con_roi = np.array(f['roi_surface/' + str(roi_idx) + '/node_number_list'])

        # Read subject data
        if verbose:
            print(('> Reading subject data: {}'.format(data_label)))
        data_sub = [h5py.File(fn_in_hdf5_data, 'r')[data_hdf5_path + data_label[i]][:] for i in range(len(data_label))]

        # Transform data when given in element centers to nodes
        if subject_data_in_center:
            if verbose:
                print('> Transforming subject data from element centers to nodes')
            # data_sub_nodes = [data_elements2nodes(data_sub[i], con_ROI) for i in range(len(data_label))]
            data_sub_nodes = data_elements2nodes(data_sub, con_roi)

        else:
            data_sub_nodes = data_sub

        del data_sub

        # map data given in nodes to brain surface since this is needed for mapping the subject data to the avg template
        # (subject space)
        if subject.roi[mesh_idx][roi_idx]['fn_mask']:
            if verbose:
                print('> Mapping point data of ROI to whole brain surface')
            data_sub_nodes_mapped = map_data_to_surface(datasets=data_sub_nodes,
                                                        points_datasets=[points_roi] * len(data_sub_nodes),
                                                        con_datasets=[con_roi] * len(data_sub_nodes),
                                                        fname_fsl_gm=os.path.join(mesh_folder_sub, fn_sub_gm),
                                                        fname_fsl_wm=os.path.join(mesh_folder_sub, fn_sub_wm),
                                                        delta=subject.roi[mesh_idx][roi_idx]['delta'],
                                                        input_data_in_center=False,
                                                        return_data_in_center=False,
                                                        data_substitute=data_substitute)
        else:
            data_sub_nodes_mapped = data_sub_nodes

        del data_sub_nodes

        # # remove NaNs from data because freesurfer can not handle it
        # if verbose:
        #     print("> Removing NaN from datasets and replacing it with data_substitute")
        # for i in range(len(data_sub_nodes_mapped)):
        #     data_sub_nodes_mapped[i][np.isnan(data_sub_nodes_mapped[i])] = data_substitute

        # Saving mapped subject data in nodes to .curv format for freesurfer (subject space)
        if verbose:
            print('> Saving mapped subject data in nodes in .curv format for freesurfer')
        for i in range(len(data_label)):
            nibabel.freesurfer.io.write_morph_data(fn_data_sub_nodes_mapped_curv[i], data_sub_nodes_mapped[i])

        # Set $SUBJECT_DIR of freesurfer
        if verbose:
            print(('> Set environment variable of freesurfer SUBJECTS_DIR={}'.format(subject_dir)))
        os.putenv('SUBJECTS_DIR', os.path.split(subject_dir)[0])

        # Make temporary symlink of average_dir in subject_dir
        if verbose:
            print("> Generating temporary symlink from average template to $SUBJECTS_DIR")
            fn_avg_template_symlink_dest = os.path.join(os.path.split(subject_dir)[0], os.path.split(average_dir)[1])
            if os.path.exists(fn_avg_template_symlink_dest):
                os.system('rm -f ' + fn_avg_template_symlink_dest)
            os.system('ln -s ' + average_dir + ' ' + fn_avg_template_symlink_dest)

        # map data on it using freesurfer
        if verbose:
            print('> Mapping subject data to average template using freesurfer mri_surf2surf')
        for i in range(len(data_label)):
            fs_cmd = "FREESURFER mri_surf2surf --srcsubject " + os.path.split(subject_dir)[1] + \
                     " --trgsubject " + os.path.split(average_dir)[1] + \
                     " --srcsurfval " + fn_data_sub_nodes_mapped_curv[i] + \
                     " --trgsurfval " + fn_data_sub_nodes_mapped_avg_curv[i] + \
                     " --hemi " + hemisphere + \
                     " --src_type curv " + \
                     " --trg_type curv " + \
                     " --surfreg " + reg_fn

            os.system(fs_cmd)

    else:
        print(('> Mapped *_avg.curv files found in {}'.format(os.path.split(fn_data_sub_nodes_mapped_avg_curv[0])[0])))

    # read mapped data
    data_avg_nodes_mapped = [0] * len(data_label)
    if verbose:
        print('> Reading mapped data from .curv files')
    for i in range(len(data_label)):
        data_avg_nodes_mapped[i] = nibabel.freesurfer.read_morph_data(fn_data_sub_nodes_mapped_avg_curv[i])

    # transform data from nodes to centers
    data_avg_centers_mapped = [0] * len(data_label)
    if verbose:
        print('> Transforming mapped nodal data to element centers')
    for i in range(len(data_label)):
        data_avg_centers_mapped[i] = data_nodes2elements(data_avg_nodes_mapped[i], con_avg)[:, np.newaxis]

    # create .hdf5 geometry file
    if verbose:
        print('> Creating .hdf5 geometry file of mapped data')
    write_geo_hdf5_surf(out_fn=fn_out_hdf5_geo, points=points_avg, con=con_avg, replace=True, hdf5_path='/mesh')

    # create .hdf5 data file
    if verbose:
        print('> Creating .hdf5 data files')
    write_data_hdf5_surf(data=data_avg_centers_mapped,
                         data_names=data_label,
                         data_hdf_fn_out=fn_out_hdf5_data,
                         geo_hdf_fn=fn_out_hdf5_geo,
                         replace=True)

    if verbose:
        print('> Done!\n')


def freesurfer2vtk(in_fns, out_folder, hem='lh', surf='pial', prefix=None, fs_subject='fsaverage', fs_subjects_dir=None):
    f"""
    Transform multiple freesurfer .mgh files into one .vtk file.
    This can be read with Paraview and others.

    Parameters
    ----------
    in_fns : list of str or list
    out_folder : str
        Output folder.
    hem : str, default: 'lh'
        Which hemisphere: 'lh' or 'rh'
    surf : str, default:  'pial'
        Which freesurfer surface: 'pial', 'inflated', ...
    prefix : str, optional
        Prefix to add to each filename
    fs_subject : string, default: 'fsaverage'
        FreeSurfer subject 
    fs_subjects_dir : string, optional
        FreeSurfer subjects directory. If not provided, read from environment

    Returns
    -------
    out_folder/{prefix}_{hem}_{surf}.vtk : File
        One .vtk file with data as overlays from all .mgh files provided
    """
    if not isinstance(in_fns, list):
        in_fns = [in_fns]

    if prefix is not None and not prefix.endswith('_'):
        prefix += '_'

    if fs_subjects_dir is None:
        try:
            fs_subjects_dir = os.environ['SUBJECTS_DIR']
        except KeyError:
            print(f"Freesurfer not loaded and 'fs_subjects_dir' not provided.")

    output_fn = f"{out_folder}/{prefix}{hem}_{surf}.vtk"

    # create a dict with fn as key, data as value. keys will be vtk data array names
    point_data = {}
    for fn in in_fns:
        point_data[os.path.split(fn)[1].replace('.mgh', '')] = nib.load(fn).get_fdata()

    # read freesurfer surface mesh
    coords, faces = nib.freesurfer.read_geometry(f"{fs_subjects_dir}/{fs_subject}/surf/{hem}.{surf}")

    # write all dataarrays + mesh geometry into one .vtk
    meshio.Mesh(np.squeeze(coords), [('triangle', faces)], point_data=point_data).write(output_fn)
