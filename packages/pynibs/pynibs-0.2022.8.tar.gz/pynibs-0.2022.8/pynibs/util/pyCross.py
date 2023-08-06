import pyximport;

pyximport.install()
from cross import pointNormal, vectorCross
from numpy import *
from numpy.random import randn
from timeit import timeit

# specify problem size per call and in total
# also, specify the data type the input data shall have
N = 2000000
total = 10000000
dtype = float64

# generate random groups of three points and determine the base vectors
arrPoints = randn(N, 9).astype(dtype)
arrAB = arrPoints[:, 3:6] - arrPoints[:, 0:3]
arrAC = arrPoints[:, 6:9] - arrPoints[:, 0:3]


# define wrapper functions to allow easy timing evaluation
def runNumpyCross():
    return cross(arrAB, arrAC)


def runPointNormal():
    return pointNormal(arrPoints)


def runVectorCross():
    return vectorCross(arrAB, arrAC)


# compute normals (cython vs. numpy) and print difference norm (validation)
arrNref = runNumpyCross()
arrNpnt = runPointNormal()
arrNvec = runVectorCross()
print(("||arrNpnt - arrNref|| = %f" % (linalg.norm(arrNpnt - arrNref))))
print(("||arrNvec - arrNref|| = %f" % (linalg.norm(arrNvec - arrNref))))

# evaluate speed of implementation per timing (N per call / total)
rep = total / N
print(("Runtime for a set of %d problems (averaged over %d sets)" % (N, rep)))
print(("numpy.cross() = %f us" % (timeit(runNumpyCross, number=rep) * 1e6 / rep)))
print(("vectorCross() = %f us" % (timeit(runVectorCross, number=rep) * 1e6 / rep)))
print(("pointNormal() = %f us" % (timeit(runPointNormal, number=rep) * 1e6 / rep)))
