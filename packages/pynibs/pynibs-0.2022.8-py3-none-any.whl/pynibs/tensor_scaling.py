import numpy as np
import warnings


def ellipse_eccentricity( a , b ):
    """Calculates the eccentricity of an 2D ellipse with the
    semi axis a and b. An eccentricity of 0 corresponds to a sphere and an
    eccentricity of 1 means complete eccentric (line) with full restriction to
    the other axis

    Parameters
    ----------
    a : float
        First semi axis parameter
    b : float
        Second semi axis parameter

    Returns
    -------
    e : float
        Eccentricity (0...1)
    """
    return np.sqrt(1-(b/a)**2)


def rescale_lambda_centerized(D, s, tsc=False):
    """Rescales the eigenvalues of the matrix D
    according to their eccentricity. The scale factor is between 0...1 a
    scale factor of 0.5 would not alter the eigenvalues of the matrix D. A
    scale factor of 0 would unify all eigenvalues to one value such that it
    corresponds to a isotropic sphere. A scale factor of 1 alters the
    eigenvalues in such a way that the resulting ellipsoid is fully
    eccentric and anisotropic.

    Parameters
    ----------
    D : nparray of float [3 x 3]
        Diffusion tensor
    s : float
        Scale parameter [0 (iso) ... 0.5 (unaltered)... 1 (aniso)]
    tsc : boolean
        Tensor singularity correction

    Returns
    -------
    Ds : nparray of float [3 x 3]
        Scaled diffusion tensor
    """

    # print("Tensor scaling factor: " + str(s))
    # check if tensor matrix contains any element > 0
    if D.any():

        # reformat data if necessary
        reformat = 0

        if D.ndim == 1 and D.size == 9:
            D = np.reshape(D, (3, 3))
            reformat = 1

        # determine eigenvalues of original diffusion tensor matrix
        l, v = np.linalg.eig(D)
        l_idx = np.fliplr(np.argsort(l)[np.newaxis, :])[0]
        l_idx_reverse = np.argsort(l_idx)
        l = l[l_idx]
        v = v[:, l_idx]

        # calculate eccentricity e = [e12, e13, e23]
        e = ellipse_eccentricity(np.array([l[0], l[0], l[1]]), np.array([l[1], l[2], l[2]]))

        # calculate volume
        # Vol_old = 4.0/3 * np.pi * L[0]*L[1]*L[2]

        # scale eccentricity
        if s < 0.5:
            es = 2.0*e*s
        elif s > 0.5:
            es = 2.0*(1-e)*s+2*e-1
        elif s < 0:
            raise ValueError('ERROR: scale parameter s must not be smaller than 0!')
        elif s > 1:
            raise ValueError('ERROR: scale parameter s must not exceed 1!')
        elif s == 0.5:
            es = e
            warnings.warn('Scale parameter s = 0.5 ... diffusion tensor matrix is unaltered!')

        ls1 = 1
        ls2 = np.sqrt(1 - es[0]**2)
        ls3 = np.sqrt(1 - es[1]**2)

        Ls = np.array([ls1, ls2, ls3])

        # calculate scale factor for volume constraint
        scale = (l[0]*l[1]*l[2])/(Ls[0]*Ls[1]*Ls[2])

        # scale eigenvalues in order to fulfill volume constraint
        Ls = scale**(1.0/3)*Ls

        # compute scaled diffusion tensor matrix and reorder them
        Ds = np.dot(np.dot(v[:, l_idx_reverse], np.diag(Ls[l_idx_reverse])), v[:, l_idx_reverse].T)

        # reformat data back again to original format if input was like this
        if reformat:
            Ds = np.reshape(Ds, (9), order='F')

    elif tsc:
        Ds = np.array([1, 0, 0, 0, 1, 0, 0, 0, 1])

    else:
        Ds = D

    return Ds


def rescale_lambda_centerized_workhorse(D, s, tsc=False):
    """Rescales the eigenvalues of the matrix D
    according to their eccentricity. The scale factor is between 0...1 a
    scale factor of 0.5 would not alter the eigenvalues of the matrix D. A
    scale factor of 0 would unify all eigenvalues to one value such that it
    corresponds to a isotropic sphere. A scale factor of 1 alters the
    eigenvalues in such a way that the resulting ellipsoid is fully
    eccentric and anisotropic

    Parameters
    ----------
    D : ndarray of float [n x 9]
        Diffusion tensor
    s : float
        Scale parameter [0 (iso) ... 0.5 (unaltered)... 1 (aniso)]
    tsc : boolean
        Tensor singularity correction

    Returns
    -------
    Ds : list of nparray of float [3 x 3]
        Scaled diffusion tensor
    """

    Ds = np.empty(D.shape)

    for i in range(D.shape[0]):
        Ds[i, :] = rescale_lambda_centerized(D[i, :], s, tsc)

    return Ds
