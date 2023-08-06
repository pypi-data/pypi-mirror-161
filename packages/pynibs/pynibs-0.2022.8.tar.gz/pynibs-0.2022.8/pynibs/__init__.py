from .para import *
from .tensor_scaling import rescale_lambda_centerized_workhorse
from .tensor_scaling import rescale_lambda_centerized

from .hdf5_io import *
from .coil import *
from .exp import *
from .util import *
from .freesurfer import *
from .roi import *
from .subject import *
from .postproc import *
from .simnibs import *
import pynibs.models
from .exp import *
from .opt import *
from .neuron import *
from .mesh import *

try:
    from .pckg import libeep
except (ImportError, SyntaxError):
    pass
try:
    from paraview.simple import *
except ImportError:
    pass

__version__ = "0.2022.8"
__datadir__ = os.path.join(os.path.os.path.dirname(__file__), '..', 'tests','data')