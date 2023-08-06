import os
import glob
import copy
import shutil
import pynibs
import simnibs
import datetime
import numpy as np
from pygpc.AbstractModel import AbstractModel


class _TMS(AbstractModel):
    """
    TMS field calculation using Simnibs
    """

    def __init__(self):
        """
        Parameters
        ----------
        p : dict
            parameters dictionary
        p["fn_subject"] : str
            Filename of subject object
            (e.g. /data/pt_01756/probands/15484.08/15484.08.pkl)
        p["mesh_idx"] : int
            MESH index the simulations are conducted with
        p["fn_coil"] : str
            Filename of coil .ccd file
        p["coil_position_mean"]: ndarray of float [3 x 4]
            Mean coil position and orientation [x_ori, y_ori, z_ori, loc]
        p["anisotropy_type"]: str or None
            Type of anisotropy ("vn" (volume normalized) or None)
        p["sigma_WM"] : float
            Electrical conductivity of white matter (default: 0.126 S/m)
        p["sigma_GM"] : float
            Electrical conductivity of gray matter (default: 0.275 S/m)
        p["sigma_CSF"] : float
            Electrical conductivity of CSF (default: 1.654 S/m)
        p["sigma_Skull"] : float
            Electrical conductivity of skull (default: 0.010 S/m)
        p["sigma_Scalp"] : float
            Electrical conductivity of scalp (default: 0.465 S/m)
        p["aniso"] : float
            Anisotropy scaling factor (default: 0.5)
        p["x"] : float
            Displacement of TMS coil along first principal axis
        p["y"] : float
            Displacement of TMS coil along second principal axis
        p["z"] : float
            Displacement of TMS coil along third principal axis
        p["psi"] : float
            Rotation of TMS coil around first principal axis in deg
        p["theta"] : float
            Rotation of TMS coil around second principal axis in deg
        p["phi"] : float
            Rotation of TMS coil around third principal axis in deg
        p["fn_results"] : str
            Results folder
            (e.g. /home/raid1/kweise/data/probands/15484.08/results/gpc/20_cond_coil_corrected/electric_field/I_0)
        """
        pass

    def validate(self):
        pass

    def simulate(self, process_id=None, matlab_engine=None):
        """
        Calculates the scalar electric potential

        Returns
        -------
        potential : ndarray of float [n_points]
            Scalar electric potential in nodes of FEM mesh
        additional_data : dict of ndarray
            Additional output data
            - dA/dt [3*n_points] ... magnetic vector potential in nodes of mesh
            - coil_dipoles [3*n_dipoles] ... coil dipole positions
            - coil_mag [n_dipoles] ... coil dipole magnitude
        """

        # load subject
        subject = pynibs.load_subject(self.p["fn_subject"])

        # Setting up SimNIBS SESSION
        #######################################################################
        S = simnibs.sim_struct.SESSION()
        S.fnamehead = subject.mesh[self.p["mesh_idx"]]["fn_mesh_msh"]
        S.pathfem = os.path.join(os.path.split(self.p["fn_results"])[0], "tmp", str(process_id))
        S.fields = "veED"
        S.open_in_gmsh = False

        if os.path.isdir(S.pathfem):
            shutil.rmtree(S.pathfem)
        os.makedirs(S.pathfem)

        # Setting up coil position
        #######################################################################
        matsimnibs = pynibs.calc_coil_transformation_matrix(
            LOC_mean=self.p["coil_position_mean"][0:3, 3],
            ORI_mean=self.p["coil_position_mean"][0:3, 0:3],
            LOC_var=np.array([self.p["x"], self.p["y"], self.p["z"]]),
            ORI_var=np.array([self.p["psi"], self.p["theta"], self.p["phi"]]),
            V=self.p["coil_position_mean"][0:3, 0:3])

        # Define the TMS simulation and setting up conductivities
        #######################################################################
        tms = S.add_tmslist()
        tms.fnamecoil = self.p["fn_coil"]
        tms.cond[0].value = self.p["sigma_WM"]      # WM
        tms.cond[1].value = self.p["sigma_GM"]      # GM
        tms.cond[2].value = self.p["sigma_CSF"]     # CSF
        tms.cond[3].value = self.p["sigma_Skull"]   # Skull
        tms.cond[4].value = self.p["sigma_Scalp"]   # Scalp

        if not (self.p['anisotropy_type'] in ['iso', 'vn']):
            raise NotImplementedError

        if self.p['anisotropy_type'] == 'vn':
            S.fname_tensor = subject.mesh[self.p['mesh_idx']]['fn_tensor_vn']
            tms.fn_tensor_nifti = subject.mesh[self.p['mesh_idx']]['fn_tensor_vn']
            tms.anisotropy_type = self.p['anisotropy_type']

        tms.excentricity_scale = self.p["aniso"]

        # Define the coil positions
        #######################################################################
        pos = tms.add_position()
        pos.matsimnibs = copy.deepcopy(matsimnibs)
        pos.distance = 0.1  # distance from coil surface to head surface
        pos.didt = 1e6      # in A/s (1e6 A/s = 1 A/us)
        pos.postprocess = S.fields

        # Running simulation
        #######################################################################
        print("Running computation of TMS induced electric fields.")
        filenames = simnibs.run_simnibs(S, cpus=1)

        # Reading results from .msh file
        #######################################################################
        print("Reading results from: {}".format(filenames[0]))

        msh = simnibs.msh.mesh_io.read_msh(filenames[0])
        msh_pyfempp = pynibs.load_mesh_msh(filenames[0])

        # potential
        for i in range(len(msh.nodedata)):
            if msh.nodedata[i].field_name == "v":
                print("Reading potential")
                v = msh.nodedata[i].value.flatten()

        # fields
        for i in range(len(msh.elmdata)):
            # save dadt also in nodes
            if msh.elmdata[i].field_name == "D":
                print("Reading dAdt and transforming from elements2nodes")
                D = pynibs.mesh.data_elements2nodes(msh.elmdata[i].value[msh.elm.elm_type == 4,])
                D = D.flatten()[:, np.newaxis]

            # if msh.elmdata[i].field_name == "E":
            #     E_tets = msh.elmdata[i].value[msh.elm.elm_type == 4, ]
            #     E_tets = E_tets.flatten()[:, np.newaxis]
            #
            # if msh.elmdata[i].field_name == "normE":
            #     normE_tets = msh.elmdata[i].value[msh.elm.elm_type == 4, ]
            #     normE_tets = normE_tets.flatten()[:, np.newaxis]
            #
            # if msh.elmdata[i].field_name == "E":
            #     E_tris = msh.elmdata[i].value[msh.elm.elm_type == 2, ]
            #     E_tris = E_tris.flatten()[:, np.newaxis]
            #
            # if msh.elmdata[i].field_name == "normE":
            #     normE_tris = msh.elmdata[i].value[msh.elm.elm_type == 2, ]
            #     normE_tris = normE_tris.flatten()[:, np.newaxis]

        # dipole position and magnitude
        fn_coil_geo = glob.glob(os.path.join(S.pathfem, "*.geo"))[0]
        print("Reading coil dipole information from {}".format(fn_coil_geo))
        dipole_position, dipole_moment_mag = pynibs.simnibs.read_coil_geo(fn_coil_geo)

        # Additional information
        #######################################################################
        print("Collecting simulation information")
        additional_data = dict()
        additional_data['info/date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        additional_data['info/sigma_WM'] = S.poslists[0].cond[0].value      # WM
        additional_data['info/sigma_GM'] = S.poslists[0].cond[1].value      # GM
        additional_data['info/sigma_CSF'] = S.poslists[0].cond[2].value     # CSF
        additional_data['info/sigma_Skull'] = S.poslists[0].cond[3].value   # Skull
        additional_data['info/sigma_Scalp'] = S.poslists[0].cond[4].value   # Scalp
        additional_data['info/fn_coil'] = S.poslists[0].fnamecoil           # TMS coil
        additional_data['info/matsimnibs'] = matsimnibs.flatten()  # coil location and orientation
        additional_data['info/dIdt'] = S.poslists[0].pos[0].didt  # rate of change of coil current
        additional_data['info/anisotropy_type'] = S.poslists[0].anisotropy_type  # type of anisotropy model
        additional_data['info/fn_mesh_msh'] = S.fnamehead  # mesh
        additional_data["coil/dipole_position"] = dipole_position.flatten()
        additional_data["coil/dipole_moment_mag"] = dipole_moment_mag.flatten()
        additional_data["data/nodes/D"] = D.flatten()
        # additional_data["data/tets/E"] = E_tets.flatten()
        # additional_data["data/tets/normE"] = normE_tets.flatten()
        # additional_data["data/tris/E"] = E_tris.flatten()
        # additional_data["data/tris/normE"] = normE_tris.flatten()

        # Deleting temporary files
        print("Removing temporary files: {}".format(S.pathfem))
        shutil.rmtree(S.pathfem)

        return v, additional_data
