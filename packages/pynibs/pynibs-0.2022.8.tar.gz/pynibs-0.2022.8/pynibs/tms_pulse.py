import numpy as np


def biphasic_pulse(t, R=0.0338, L=15.5*1e-6, C=193.6*1e-6, alpha=1089.8, f=2900):
    """
    Returns normalized single biphasic pulse waveform of electric field (first derivative of coil current)

    Parameters
    ----------
    t: ndarray of float [n_t]
        Time array in seconds
    R: float, optional, default: 0.0338 Ohm
        Resistance of coil in (Ohm)
    L: float, optional, default: 15.5*1e-6 H
        Inductance of coil in (H)
    C: float, optional, default: 193.6*1e-6
        Capacitance of coil in (F)
    alpha: float, optional, default: 1089.8 1/s
        Damping coefficient in (1/s)
    f: float, optional, default: 2900 Hz
        Frequency in (Hz)

    Returns
    -------
    e: ndarray of float [n_t]
        Normalized electric field time course (can be scaled with electric field)
    """
    omega = 2 * np.pi * f
    i = 1/(omega*L) * np.exp(-alpha*t) * np.sin(omega*t)
    e = np.gradient(i)
    e = e/np.max(e)

    return e
