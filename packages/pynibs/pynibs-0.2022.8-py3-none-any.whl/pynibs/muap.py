import numpy as np
from scipy import interpolate


def sfap_dip(z):
    dist = 1

    i = np.zeros(len(z))
    i[np.isclose(z, 0, atol=0.01)] = 1
    i[np.isclose(z, dist, atol=0.01)] = -1
    return i


def sfap(z, sigma_i=1.01, d=55*1e-6, alpha=0.5):
    """
    Single fibre propagating transmembrane current (second spatial derivative of transmembrane potential).

    S. D. Nandedkar and E. V. Stalberg,“Simulation of single musclefiber action potentials”
    Med. Biol. Eng. Comput., vol. 21, pp. 158–165, Mar.1983.

    J.  Duchene  and  J.-Y.  Hogrel,“A  model  of  EMG  generation,”
    IEEETrans. Biomed. Eng., vol. 47, no. 2, pp. 192–200, Feb. 2000

    Hamilton-Wright, A., & Stashuk, D. W. (2005).
    Physiologically based simulation of clinical EMG signals.
    IEEE Transactions on biomedical engineering, 52(2), 171-183.

    Parameters
    ----------
    t : ndarray of float [n_t]
        Time in (ms)
    sigma_i : float, optional, default: 1.01
        Intracellular conductivity in (S/m)
    d : float, optional, default: 55*1e-6
        Diameter of muscle fibre in (m)
    v : float, optional, default: 1
        Conduction velocity in (m/s)
    alpha : float, optional, default: 0.5
        Scaling factor to adjust length of AP

    Returns
    -------
    i : ndarray of float [n_t]
        Transmembrane current of muscle fibre
    """
    # z = v * t
    z[z<0] = 0
    i = (sigma_i * np.pi * d**2) * 96 * alpha**3 * z * np.exp(-alpha*z) * (alpha**2*z**2 - 6*alpha*z + 6)
    # i = (sigma_i * np.pi * d**2) * 96 * (z) * (6-6*(z) + (z)**2)*np.exp(-z)
    # i = (sigma_i * np.pi * d**2)/4 * 3072 * z * (z**2 - 3*z + 1.5) * np.exp(-2*z)

    return i


def dipole_potential(z, loc, response):
    """
    Returns dipole potential at given coordinates z (interpolates given dipole potential)
    """
    res = np.zeros(len(z))
    mask = np.logical_and(z > loc[0], z < loc[-1])
    f = interpolate.interp1d(loc, response)
    res[mask] = f(z[mask])

    return res


def create_electrode(l_x, l_z, n_x, n_z):
    """
    Creates electrode coordinates

    Parameters
    ----------
    l_x : float
        X-extension of electrode in mm
    l_z : float
        Z-extension of electrode in mm
    n_x : int
        Number of point electrode in x-direction
    n_z : int
        Number of point electrodes in z-direction

    Returns
    -------
    electrode_coords : ndarray of float [n_ele x 3]
        Coordinates of point electrodes (x, y, z)
    """

    electrode_coords = np.zeros((n_x*n_z, 3))

    i = 0
    dx = l_x/(n_x-1)
    dz = l_z/(n_z-1)

    for i_x in range(n_x):
        for i_z in range(n_z):
            electrode_coords[i, :] = np.array([-l_x/2 + i_x*dx, 0, -l_z/2 + i_z*dz])
            i += 1

    return electrode_coords


def create_muscle_coords(l_x, l_y, n_x, n_y, h):
    """
    Create x and y coordinates of muscle fibres in muscle

    Parameters
    ----------
    l_x : float
        X-extension of muscle in mm
    l_y : float
        Y-extension of muscle in mm
    n_x : int
        Number of muscle fibres in x-direction
    n_y : int
        Number of muscle fibres in y-direction
    h : float
        Offset of muscle from electrode plane in mm

    Returns
    -------
    muscle_coords : ndarray of float [n_muscle x 3]
        Coordinates of muscle fibres in x-y plane (x, y, z)
    """

    muscle_coords = np.zeros((n_x*n_y, 3))

    i = 0

    if n_x == 1:
        dx = 0
    else:
        dx = l_x/(n_x-1)

    if n_y == 1:
        dy = 0
    else:
        dy = l_y/(n_y-1)

    for i_x in range(n_x):
        for i_y in range(n_y):
            muscle_coords[i, :] = np.array([-l_x/2 + i_x*dx, h + i_y*dy, 0])
            i += 1

    return muscle_coords


def create_muscle_fibre(x0, y0, L, n_fibre):
    """
    Creates muscle fibre coordinates (in z-direction)

    Parameters
    ----------
    x0 : float
        X-location of muscle fibre
    y0 : float
        Y-location of muscle fibre
    L : float
        Length of muscle fibre
    n_fibre : float
        Number of discrete fibre elements

    Returns
    -------
    fibre_coords : ndarray of float [n_fibre x 3]
        Coordinates of muscle fibre in z-direction (x, y, z)
    """
    dz_fibre = L/(n_fibre-1)
    fibre_coords = np.hstack((np.ones((n_fibre, 1))*x0,
                              np.ones((n_fibre, 1))*y0,
                              (-L/2 + np.arange(n_fibre) * dz_fibre)[:, np.newaxis]))

    return fibre_coords


def create_signal_matrix(T, dt, fibre_coords, z_e, v):
    """
    Create signal matrix containing the travelling action potential on the fibre

    Parameters
    ----------
    T : float
        Total time
    dt : float
        Time step
    fibre_coords : ndarray of float [n_fibre x 3]
        Coordinates of muscle fibre in z-direction (x, y, z)
    z_e : float
        Location of action potential generation
    v : float
        Velocity of action potential

    Returns
    -------
    signal_matrix : ndarray of float [n_time x n_fibre]
        Signal matrix containing the action potential values for each time step in the rows
    """
    N_t = int(T/dt + 1)  # number of time-steps
    t = np.linspace(0, T, N_t)
    n_fibre = fibre_coords.shape[0]
    dz_fibre = np.abs(fibre_coords[0, 2] - fibre_coords[1, 2])
    signal_matrix = np.zeros((N_t, n_fibre))
    z_e_idx = np.argmin(np.abs(fibre_coords[:, 2] - z_e))
    z_r = fibre_coords[z_e_idx:, 2] - fibre_coords[-1, 2]
    z_l = fibre_coords[:z_e_idx, 2] - fibre_coords[z_e_idx, 2]  # np.arange(-(L/2 + z_e), 0, dz_fibre)

    for i in range(N_t):
        z_l += v*dt
        z_r += v*dt

#         ap_r = sfap_dip(z=z_r)
#         ap_l = sfap_dip(z=z_l)

        ap_r = sfap(t=z_r, v=1)
        ap_l = sfap(t=z_l, v=1)

        signal_matrix[i, :z_e_idx] = ap_l
        signal_matrix[i, z_e_idx:] = np.flip(ap_r)

    return signal_matrix, t, fibre_coords[:, 2]


def hermite_rodriguez_1st(t, tau0=0, tau=0, lam=0.002):
    """
    First order Hermite Rodriguez function to model surface MUAPs

    Parameters
    ----------
    t : ndarray of float [n_t]
        Time axis in s
    tau0 : float, optional, default: 0
        initial shift to ensure causality in s
    tau : float, optional, default: 0
        shift (firing time) in s
    lam : float, optional, default: 2
        Timescale in s

    Returns
    -------
    y : ndarray of float [n_t]
        Surface MUAP
    """

    return -(t-tau0-tau) * np.exp(-((t-tau0-tau)/lam)**2)


def weight_signal_matrix(signal_matrix, fn_imp, t, z):
    """
    Weight signal matrix with impulse response from single dipole at every location
    """
    imp = np.loadtxt(fn_imp)
    imp[:, 0:3] = imp[:, 0:3]*1000
    imp[:, 3] = imp[:, 3]/np.max(imp[:, 3])
    signal_matrix_weighted = np.zeros((signal_matrix.shape[0], signal_matrix.shape[1], signal_matrix.shape[1]))

    for i_t in range(signal_matrix.shape[0]):
        print(f"{i_t}/{signal_matrix.shape[0]}")
        for i_z, z_w in enumerate(z):
            ir_interp = dipole_potential(z=z-z_w, loc=imp[:, 2], response=imp[:, 3])
            signal_matrix_weighted[i_t, i_z, :] = signal_matrix[i_t, i_z] * ir_interp

    signal_matrix_weighted = np.sum(signal_matrix_weighted, axis=1)

    return signal_matrix_weighted


def create_sensor_matrix(electrode_coords, fibre_coords, sigma_r=1, sigma_z=1):
    """
    Create sensor matrix containing the inverse distances from the point electrodes to the fibre elements
    weighted by the anisotropy factor of the muscle tissue.

    Parameters
    ----------
    electrode_coords : ndarray of float [n_ele x 3]
        Coordinates of point electrodes (x, y, z)
    fibre_coords : ndarray of float [n_fibre x 3]
        Coordinates of muscle fibre in z-direction (x, y, z)
    sigma_r : float, optional, default: 1
        Radial conductivity of muscle
    sigma_z : float, optional, default: 1
        Axial conductivity of muscle along fibre

    Returns
    -------
    sensor_matrix : ndarray of float [n_fibre x n_ele]
        Sensor matrix containing the inverse distances weighted with the anisotropy of muscle tissue
    """
    sigma_factor = sigma_z/sigma_r

    sensor_matrix = np.zeros((fibre_coords.shape[0], electrode_coords.shape[0]))

    for i in range(electrode_coords.shape[0]):
        r_f = np.linalg.norm(electrode_coords[i, :2] - fibre_coords[:, :2], axis=1)

        # sensor_matrix[:, i] = 1/np.linalg.norm(fibre_coords-electrode_coords[i, :], axis=1)
        sensor_matrix[:, i] = 1/np.sqrt(sigma_factor*r_f**2 + (fibre_coords[:, 2]-electrode_coords[i, 2])**2)

    return sensor_matrix


def compute_signal(signal_matrix, sensor_matrix):
    """
    Determine average signal from one single muscle fibre on all point electrodes

    Parameters
    ----------
    signal_matrix : ndarray of float [n_time x n_fibre]
        Signal matrix containing the action potential values for each time step in the rows
    sensor_matrix : ndarray of float [n_fibre x n_ele]
        Sensor matrix containing the inverse distances weighted with the anisotropy of muscle tissue

    Returns
    -------
    signal : ndarray of float [n_time]
        Average signal detected all point electrodes
    """
    signal = np.mean(np.matmul(signal_matrix, sensor_matrix), axis=1)

    return signal


def calc_mep_wilson(firing_rate_in, t, Qvmax=900, Qmmax=300, q=8, Tmin=14, N=100, M0=42, lam=0.002, tau0=0.006):
    """
    Determine motor evoked potential from incoming firing rate

    Parameters
    ----------
    firing_rate_in : ndarray of float [n_t]
        Input firing rate from alpha motor neurons
    t : ndarray of float [n_t]
        Time axis in s
    Qvmax : float, optional, default: 900
        Max of incoming firing rate [1/s]
    Qmmax : float, optional, default: 300
        Max of MU firing rate [1/s]
    q : float, optional, default: 8
        Min firing rate of MU [1/s]
    Tmin : float, optional, default: 14
        Min MU threshold [1/s]
    N : float, optional, default: 100
        Number of MU
    M0 : float, optional, default: 42
        Scaling constant of MU amplitude [mV/s]
    lam : float, optional, default: 0.002
        MUAP timescale of first order Hermite Rodriguez function [s]
    tau0 : float, optional, default: 0.006
        Standard shift of MUAP to ensure causality [s]

    Returns
    -------
    mep : ndarray of float [n_t]
        Motor evoked potential at surface electrode
    """
    dt = t[1] - t[0]            # time step
    k = np.arange(N)+1          # MU index
    firing_rate_in_mat = np.repeat(firing_rate_in[np.newaxis, :], N, axis=0)

    # determine MU thresholds
    alpha = 1/N*np.log(Qvmax/Tmin)
    Tk = Tmin * np.exp(alpha*k)

    # determine MU amplitude
    Mk = M0 * np.exp(alpha*k)

    # determine spike rate of MUs from incoming spike rate
    kappak = (Qmmax - q) / (Qvmax - Tk)
    Qk = q + kappak[:, np.newaxis] * (firing_rate_in_mat - Tk[:, np.newaxis])
    Qk[firing_rate_in_mat < Tk[:, np.newaxis]] = 0

    # determine spike times of MUs by integrating the spike rates
    Qk_int = np.cumsum(Qk, axis=1) * dt

    spike_times = []
    for k in range(N):
        Qk_int_max = int(np.floor(Qk_int[k, -1]))

        if Qk_int_max > 0:
            spike_times.append(np.zeros(Qk_int_max))

            for j in range(Qk_int_max):
                spike_times[k][j] = t[np.where(Qk_int[k, :] > (j+1))[0][0]]
        else:
            spike_times.append([])

    # determine EMG signal by summing up all MUAPS at determined firing times
    mep = np.zeros(len(t))

    for k in range(N):
        if len(spike_times[k]) > 0:
            for tau in spike_times[k]:
                mep += Mk[k] * hermite_rodriguez_1st(t=t, tau0=tau0, tau=tau, lam=lam)

    return mep