import numpy as np
from pynibs import load_muaps
from .exp.Mep import sigmoid
from scipy.special import logsumexp
from scipy.interpolate import LinearNDInterpolator


def calc_e_sensitivity(theta, gradient):
    """
    Determine sensitivity map of electric field

    Parameters
    ----------
    theta : np.ndarray
        Theta angle (matrix) [N_stim x N_ele] of electric field with respect to surface normal
    gradient : np.ndarray, optional, default: None
        Electric field gradient (matrix) [N_stim x N_ele] between layer 1 and layer 6. Optional, the neuron mean field
        model is more accurate when provided.

    Returns
    -------
    e_sens : np.ndarray
        Electric field sensitivity maps [N_stim x N_ele]
    """
    cell_simulation_data = []
    combined_thresholds = []
    thetas = []
    rel_gradients = []

    for cell_id in range(1, 6):
        cell_thetas = []
        cell_rel_grads = []
        cell_thresholds = []
        cell_simulation_data.append(np.genfromtxt(f'/data/pt_01756/studies/neuronibs/neuronibs_data/cells/Layer_5/L5_TTPC2_cADpyr232_{cell_id}/L5_TTPC2_cADpyr232_{cell_id}_41_9_6.csv', delimiter=','))

        thresholds = cell_simulation_data[-1][:, 3]
        theta_ = cell_simulation_data[-1][:, 0]
        phi = cell_simulation_data[-1][:, 1]
        rel_grad = cell_simulation_data[-1][:, 2]

        unique_theta = np.unique(theta_)
        unique_phi = np.unique(phi)
        unique_rel_grad = np.unique(rel_grad)

        theta_count = len(unique_theta)
        phi_count = len(unique_phi)
        rel_gradient_count = len(unique_rel_grad)

        slice_width = ((theta_count - 2) * phi_count + 2)
        for k in range(rel_gradient_count):
            slice_start = k * slice_width
            slice_end =  (k + 1) * slice_width - 1
            cell_thresholds += [thresholds[slice_start]] + [np.mean(thresholds[slice_start + phi_count * j + 1: slice_start + phi_count * j + phi_count + 1]) for j in range(theta_count-2)] + [thresholds[slice_end]]
            cell_thetas +=     [theta_[slice_start]] +      [np.mean(theta_[slice_start + phi_count * j + 1: slice_start + phi_count * j + phi_count + 1]) for j in range(theta_count-2)] + [theta_[slice_end]]
            cell_rel_grads +=  [rel_grad[slice_start]] +   [np.mean(rel_grad[slice_start + phi_count * j + 1: slice_start + phi_count * j + phi_count + 1]) for j in range(theta_count-2)] + [rel_grad[slice_end]]

        combined_thresholds.append(cell_thresholds)
        thetas.append(cell_thetas)
        rel_gradients.append(cell_rel_grads)

    # average thresholds over cells
    mean_threshold = np.mean(np.array(combined_thresholds), axis=0)

    # create ND Interpolator
    interp = LinearNDInterpolator(list(zip(thetas[0], rel_gradients[0])), mean_threshold)
    e_sens = interp(theta, gradient) / 3

    return e_sens


def calc_e_effective(e, theta, gradient=None):
    """
    Determines the effective electric field using a neuron mean field model.
    Transforms the electric field by subtracting the sensitivity map (in V/m) from the original electric field.
    The remaining field is the effective electric field (e_eff), which is responsible for the stimulation effect,
    i.e. behavioural effects start at e_eff > 0 because lower fields were not able to stimulate neurons.

    Parameters
    ----------
    e : np.ndarray
        Electric field (matrix) [N_stim x N_ele]
    theta : np.ndarray
        Theta angle (matrix) [N_stim x N_ele] of electric field with respect to surface normal
    gradient : np.ndarray, optional, default: None
        Electric field gradient (matrix) [N_stim x N_ele] between layer 1 and layer 6. Optional, the neuron mean field
        model is more accurate when provided.

    Returns
    -------
    e_eff : np.ndarray
        Effective electric field (matrix) [N_stim x N_ele] the regression analysis can be performed with.
    """
    # determine sensitivity map
    e_sens = calc_e_sensitivity(theta=theta, gradient=gradient)

    # determine effective electric field
    e_eff = e - e_sens

    return e_eff


def DI_wave(t, intensity, t0=5, dt=1.4, width=0.25):
    """
    Determines cortical DI waves from TMS

    Parameters
    ----------
    t: ndarray of float [n_t]
        Time axis in ms
    intensity: float
        Stimulator intensity w.r.t resting motor threshold (typical range: [0 ... 2])
    t0: float
        offset time
    dt: float
        Spacing of waves in ms
    width: float
        Width of waves

    Returns
    -------
    y: ndarray of float [n_t]
        DI waves
    """

    waves = ["D", "I1", "I2", "I3", "I4"]

    x0 = dict()
    x0["D"] = 1.6952640144480995
    x0["I1"] = 1.314432218728424
    x0["I2"] = 1.4421623825084195
    x0["I3"] = 1.31643163560532
    x0["I4"] = 1.747079479469914

    amp = dict()
    amp["D"] = 12.83042571812661 / 35.46534715796085
    amp["I1"] = 35.46534715796085 / 35.46534715796085
    amp["I2"] = 26.15109003222628 / 35.46534715796085
    amp["I3"] = 15.491215097559184 / 35.46534715796085
    amp["I4"] = 10.461195366965226 / 35.46534715796085

    r = dict()
    r["D"] = 13.945868670402973
    r["I1"] = 8.707029476168504
    r["I2"] = 7.02266347578131
    r["I3"] = 16.74855628350182
    r["I4"] = 17.85806255278076

    y = np.zeros(len(t), dtype=np.float128)

    for i, w in enumerate(waves):
        y_ = np.exp(-(t - t0 - i * dt) ** 2 / (2 * width ** 2))
        y_ = y_ / np.max(y_)
        y_ = y_ * sigmoid(intensity, amp=amp[w], r=r[w], x0=x0[w])
        y = y + y_

    return y


class Workhorse(object):

    def __init__(self, t, aMN, renshaw):
        self.t = t
        self.dt = t[1] - t[0]
        self.aMN = aMN
        self.renshaw = renshaw

    def run(self, input):
        """
        Workhorse to run alpha motor neurons in parallel

        Parameters
        ----------
        input: ndarray of float [n_t]
            Input signal to alpha motor neurons

        Returns
        -------
        alpha_motor_neurons: list of AlphaMotorNeuron instances
            Alpha motor neurons with calculated membrane potential (Vm) and spike times (spike_times)
        """

        # iterate over each time step
        feedback = np.zeros(len(self.t))
        delay = round(self.renshaw.delay / self.dt)

        for i, t_ in enumerate(self.t):
            feedback[i] = self.aMN.step(input, feedback, t_, i)

            if i + delay < len(self.t) - 1:
                feedback[i + 1] = self.renshaw.step(feedback, t_, i)  # TODO consider delay and length of signal

        return self.aMN


class Model(object):
    """
    Spinal cord and Muscle model containing alpha motor neurons and Renshaw cells.
    """

    def __init__(self, T, dt, N_MU=100, fn_muaps="/data/pt_01756/studies/MEP_modeling/results/muscle_model"
                                                 "/Dist1_Monopolar_Abduct_NormalCV_New.hdf5", **kwargs):
        """
        Initialize spinal cord and Muscle model

        Parameters
        ----------
        T : Total Time of obesrvation
        dt : time step
        N_MU: Number of Motor units
        fn_muaps : Path to muap shapes
        **kwars: constants of neurons
        """

        # setup parameters and state variables
        self.N_MU = N_MU
        self.T = T
        self.dt = dt
        self.t = np.arange(0, T + dt, dt)

        # Neuron
        self.Vm_thr_array = kwargs['n_thr'] + kwargs['m_thr'] * np.arange(self.N_MU)  # thresholds of alpha MNs
        self.t_refrac = kwargs['t_refrac']
        self.tau_mem = kwargs['tau_mem']
        self.Vm_rest = kwargs['Vm_rest']
        self.Rm = kwargs['Rm']

        # Renshaw cell (inhibitory)
        self.slope_renshaw = kwargs.get('slope_renshaw')
        self.Vm_thr_renshaw = kwargs.get('Vm_thr_renshaw')
        self.Vm_rest_renshaw = kwargs.get('Vm_rest_renshaw')

        # Acetyl synapse (excitatory)
        self.tau_syn_decay_ac = kwargs.get('tau_syn_decay_ac')
        self.tau_syn_rise_ac = kwargs.get('tau_syn_rise_ac')
        self.tau_syn_decay_fast_ac = kwargs.get('tau_syn_decay_fast_ac')
        self.tau_syn_decay_slow_ac = kwargs.get('tau_syn_decay_slow_ac')
        self.a_syn_decay_fast_ac = kwargs.get('a_syn_decay_fast_ac')
        self.a_syn_decay_slow_ac = kwargs.get('a_syn_decay_slow_ac')

        # Glycin Synapse (inhibitory)
        self.tau_syn_decay_gl = kwargs.get('tau_syn_decay_gl')
        self.tau_syn_rise_gl = kwargs.get('tau_syn_rise_gl')
        self.tau_syn_decay_fast_gl = kwargs.get('tau_syn_decay_fast_gl')
        self.tau_syn_decay_slow_gl = kwargs.get('tau_syn_decay_slow_gl')
        self.a_syn_decay_fast_gl = kwargs.get('a_syn_decay_fast_gl')
        self.a_syn_decay_slow_gl = kwargs.get('a_syn_decay_slow_gl')

        # Connectivity
        self.connectivity_cortex_alpha = kwargs.get('connectivity_cortex_alpha')
        self.connectivity_renshaw_alpha = kwargs.get('connectivity_renshaw_alpha')
        self.connectivity_alpha_renshaw = kwargs.get('connectivity_alpha_renshaw')

        # Load MUAPS
        self.fn_muaps = fn_muaps
        self.muaps = []
        self.t_muap = []
        self.muaps, t_muap = load_muaps(self.fn_muaps)

        # Workhorse Arrays
        self.alpha_motor_neurons = []
        self.renshaw_cells = []
        self.motor_units = []

        # Output Values
        self.mep = None
        self.mep_p2p = None

        # Synapse (Cortex -> Alpha Motor Neurons)
        acetyl_synapse_1 = Synapse(dt=self.dt, T=self.T,
                                   tau_syn_decay_fast=self.tau_syn_decay_fast_ac,
                                   tau_syn_decay_slow=self.tau_syn_decay_slow_ac,
                                   tau_syn_rise=self.tau_syn_rise_ac,
                                   a_syn_decay_slow=self.a_syn_decay_slow_ac,
                                   a_syn_decay_fast=self.a_syn_decay_fast_ac,
                                   connectivity=kwargs.get('connectivity_cortex_alpha'),
                                   N=self.N_MU)

        # Synapse (Alpha Motor Neurons -> Renshaw Cells)
        acetyl_synapse_2 = Synapse(dt=self.dt, T=self.T,
                                   tau_syn_decay_fast=self.tau_syn_decay_fast_ac,
                                   tau_syn_decay_slow=self.tau_syn_decay_slow_ac,
                                   tau_syn_rise=self.tau_syn_rise_ac,
                                   a_syn_decay_slow=self.a_syn_decay_slow_ac,
                                   a_syn_decay_fast=self.a_syn_decay_fast_ac,
                                   connectivity=self.connectivity_alpha_renshaw,
                                   N=self.N_MU)

        # Synapse (Renshaw Cells -> Alpha Motor Neurons)
        glycine_synapse = Synapse(dt=self.dt, T=self.T,
                                  tau_syn_decay_fast=self.tau_syn_decay_fast_gl,
                                  tau_syn_decay_slow=self.tau_syn_decay_slow_gl,
                                  tau_syn_rise=self.tau_syn_rise_gl,
                                  a_syn_decay_slow=self.a_syn_decay_slow_gl,
                                  a_syn_decay_fast=self.a_syn_decay_fast_gl,
                                  connectivity=self.connectivity_renshaw_alpha,
                                  N=self.N_MU)

        self.aMNs = AlphaMotorNeuron(tau_mem=self.tau_mem, Vm_thr=self.Vm_thr_array, Vm_rest=self.Vm_rest, Rm=self.Rm,
                                     t_refrac=self.t_refrac, T=self.T, dt=self.dt,
                                     synapses=[acetyl_synapse_1, glycine_synapse], N=self.N_MU)

        self.renshaw = RenshawCell(tau_mem=self.tau_mem, Vm_thr=self.Vm_thr_renshaw, Vm_rest=self.Vm_rest, Rm=self.Rm,
                                   T=self.T, dt=self.dt, delay=0,
                                   synapses=[acetyl_synapse_2],
                                   slope=self.slope_renshaw)  # TODO own Vm_thr for optimisation

        for i in range(self.N_MU):
            self.motor_units.append(MotorUnit(muap=self.muaps[:, i], t=self.t))

    def run(self, inp):
        """
        Starts the parallel processing.
        Creates Model can all workhorse process

        Parameters
        ----------
        inp: ndarray of float [n_t]
            Input signal to alpha motor neurons
        """

        workhorse = Workhorse(self.t, self.aMNs, self.renshaw)
        self.alpha_motor_neurons = workhorse.run(inp)

        muscle = Muscle(self.alpha_motor_neurons, self.motor_units)
        self.mep = muscle.get_mep()
        self.mep_p2p = np.max(self.mep) - np.min(self.mep)


class Synapse(object):
    """
    Synapse (conductance-based)
    """

    def __init__(self, T, dt, N, tau_syn_decay=None, tau_syn_rise=None,
                 tau_syn_decay_fast=None, tau_syn_decay_slow=None, a_syn_decay_fast=None, a_syn_decay_slow=None,
                 connectivity=1):
        """
        Initializes Synapse instance

        Parameters
        ----------
        T : float
            Total simulation time in ms
        dt : float
            Time-step to solve DEQ
        tau_syn_decay : float
            Decay time constant of synapse in ms (set this parameter, if only one decay time constant is present and set
            tau_syn_decay_fast=None, tau_syn_decay_slow=None)
        tau_syn_rise : float
            Rise time of synapse in ms
        tau_syn_decay_fast : float
            Decay time constant of synapse of fast component in ms
        tau_syn_decay_slow : float
            Decay time constant of synapse of slow component in ms
        a_syn_decay_fast : float
            Proportion of fast decay time constant
        a_syn_decay_slow : float
            Proportion of slow decay time constant
        connectivity : float
            Scaling factor for synaptic strength
        """

        self.tau_syn_decay = tau_syn_decay
        self.T = T
        self.dt = dt
        self.connectivity = connectivity
        self.tau_syn_rise = tau_syn_rise
        self.tau_syn_decay_fast = tau_syn_decay_fast
        self.tau_syn_decay_slow = tau_syn_decay_slow
        self.a_syn_decay_fast = a_syn_decay_fast
        self.a_syn_decay_slow = a_syn_decay_slow
        self.synapse_single_decay = False
        self.synapse_double_decay = False
        self.synapse_single_decay_rise = False
        self.synapse_double_decay_rise = False

        if tau_syn_decay is not None and (
                tau_syn_decay_slow is None and tau_syn_decay_fast is None and tau_syn_rise is None):
            self.synapse_single_decay = True

        if (tau_syn_decay_slow is not None and tau_syn_decay_fast is not None) and (
                tau_syn_rise is None and tau_syn_decay is None):
            self.synapse_double_decay = True

        if (tau_syn_decay_slow is not None and tau_syn_decay_fast is not None and tau_syn_rise is not None) and (
                tau_syn_decay is None):
            self.synapse_double_decay_rise = True

        if (tau_syn_rise is not None and tau_syn_decay is not None) and (
                tau_syn_decay_slow is None and tau_syn_decay_fast is None):
            self.synapse_single_decay_rise = True

        if self.synapse_single_decay + self.synapse_double_decay + self.synapse_single_decay_rise + \
                self.synapse_double_decay_rise != 1:
            raise AssertionError("Please check assignment of time constants...")

        # initialize arrays
        self.t = np.linspace(0, self.T, int(self.T / self.dt + 1))
        self.g_f = np.zeros((N, len(self.t)))
        self.x_f = np.zeros((N, len(self.t)))
        self.g_s = np.zeros((N, len(self.t)))
        self.x_s = np.zeros((N, len(self.t)))
        self.x = np.zeros((N, len(self.t)))
        self.g_tot = np.zeros((N, len(self.t)))

    def step(self, inp, i):
        """
        Solves the DEQ and computes synapse conductivity

        Parameters
        ----------
        inp: ndarray of float [n_t]
            Input signal
        i: int
            Current index
        """

        # double exponential kernel with rise time and slow + fast decay times
        if self.synapse_double_decay_rise:
            self.g_f[:, i] = self.g_f[:, i - 1] + self.x_f[:, i - 1] * self.dt
            self.x_f[:, i] = self.x_f[:, i - 1] + (
                    (inp[i] - self.x_f[:, i - 1]) * (self.tau_syn_rise + self.tau_syn_decay_fast) -
                    self.g_f[:, i - 1]) / (self.tau_syn_rise * self.tau_syn_decay_fast) * self.dt
            self.g_s[:, i] = self.g_s[:, i - 1] + self.x_s[:, i - 1] * self.dt
            self.x_s[:, i] = self.x_s[:, i - 1] + (
                    (inp[i] - self.x_s[:, i - 1]) * (self.tau_syn_rise + self.tau_syn_decay_slow) -
                    self.g_s[:, i - 1]) / (self.tau_syn_rise * self.tau_syn_decay_slow) * self.dt
            self.g_tot[:, i] = self.a_syn_decay_fast * self.g_f[:, i] + self.a_syn_decay_slow * self.g_s[:, i]

        # single exponential kernel with slow + fast decay times
        if self.synapse_double_decay:
            self.g_s[:, i] = self.g_s[:, i - 1] + ((0 - self.g_s[:, i - 1]) / self.tau_syn_decay_slow) * self.dt + inp[
                i]
            self.g_f[:, i] = self.g_f[:, i - 1] + ((0 - self.g_f[:, i - 1]) / self.tau_syn_decay_fast) * self.dt + inp[
                i]
            self.g_tot[:, i] = self.a_syn_decay_fast * self.g_f[:, i] + self.a_syn_decay_slow * self.g_s[:, i]

        # single exponential kernel with one decay time
        if self.synapse_single_decay:
            self.g_tot[:, i] = self.g_tot[:, i - 1] + ((0 - self.g_tot[:, i - 1]) / self.tau_syn_decay) * self.dt + inp[
                i]

        # double exponential kernel with rise time and one decay time
        if self.synapse_single_decay_rise:
            self.g_tot[:, i] = self.g_tot[:, i - 1] + self.x[:, i - 1] * self.dt
            self.x[:, i] = self.x[:, i - 1] + ((inp[i] - self.x[:, i - 1]) * (self.tau_syn_rise + self.tau_syn_decay) -
                                               self.g_tot[:, i - 1]) / (
                                   self.tau_syn_rise * self.tau_syn_decay) * self.dt

        return self.g_tot[:, i] * self.connectivity  # Apply weight to output


class RenshawCell(object):
    """
    Renshaw Cell (Leaky integrate and fire)
    """

    def __init__(self, tau_mem, Vm_thr, Vm_rest, Rm, T, dt, delay, synapses, slope):
        """
        Initializes Renshaw Cell instance

        Parameters
        ----------
        tau_mem : float
            Time constant of cell membrane in ms
        Vm_thr : float
            Firing threshold in mV
        Vm_rest : float
            Resting potential
        Rm : float
            Cell membrane resistance
        T : float
            Total simulation time in ms
        dt : float
            Time-step to solve DEQ
        delay: float
            Delay of feedback in ms
        synapses: list of Synapses
            List of all synapses
        slope : float
            Slope of Threshold
        """
        self.tau_mem = tau_mem
        self.Vm_thr = Vm_thr  # TODO proper Threshold
        self.Vm_rest = Vm_rest
        self.Rm = Rm

        self.T = T
        self.dt = dt
        self.t_rest = 0

        self.max_firerate = 23.12  # TODO Proper value
        self.slope = slope
        self.delay = delay

        # Synapses
        self.acetyl_synapse = synapses[0]  # excitatory (Alpha Motor Neuron)

        # initialize arrays
        self.t = np.linspace(0, self.T, int(self.T / self.dt + 1))
        self.g_tot = np.zeros(len(self.t))
        self.Vm = Vm_rest * np.ones(len(self.t), dtype=np.float128)
        self.spike_times = np.zeros(len(self.t))
        self.output = np.zeros(len(self.t), dtype=np.float128)

    def step(self, inp, t_, i):
        """
        Solves the DEQ and computes membrane potential.
        Saves membrane potential in self.Vm and spike times in self.spike_times

        Parameters
        ----------
        inp: ndarray of float [n_t]
            Input signal
        t_ : floatf
            Current time step
        i : int
            Current index
        """

        self.g_tot[i] = np.sum(self.acetyl_synapse.step(inp, i))

        self.Vm[i] = self.Vm[i - 1] + (-(self.Vm[i - 1] - self.Vm_rest) - self.Vm[i - 1] * self.g_tot[
            i] * self.Rm) / self.tau_mem * self.dt

        # A. Spiegler potential to Rate
        # np.seterr('raise')
        self.output[i] = 2 * self.max_firerate / (1 + (logsumexp(self.slope * (self.Vm_thr - self.Vm[i]))))

        return self.output[i]

        # if(self.Vm[i] >= self.Vm_thr):
        #     self.spike_times[i] = t_
        #     self.Vm[i] = self.Vm_rest
        #     self.t_rest = t_ + self.t_refrac
        #     return 1 / self.dt #TODO in Feuerate umwandeln
        #
        # return 0  # return no spike


class AlphaMotorNeuron(object):
    """
    Alpha Motor Neuron (Leaky integrate and fire)
    """

    def __init__(self, tau_mem, Vm_thr, Vm_rest, Rm, t_refrac, T, dt, synapses, N):
        """
        Initializes AlphaMotorNeuron instance

        Parameters
        ----------
        tau_mem : float
            Time constant of cell membrane in ms
        Vm_thr : float
            Firing threshold in mV
        Vm_rest : float
            Resting potential
        Rm : float
            Cell membrane resistance
        t_refrac : float
            Refractory time
        T : float
            Total simulation time in ms
        dt : float
            Time-step to solve DEQ
        synapses: list of Synapses
            List of all synapses
        N: int
            Number of alpha motor neurons
        """
        self.tau_mem = tau_mem
        self.Vm_thr = Vm_thr
        self.Vm_rest = Vm_rest
        self.Rm = Rm
        self.t_refrac = t_refrac
        self.T = T
        self.N = N
        self.dt = dt
        self.t_rest = np.zeros(N)
        self.is_in_refrac = np.ones(N)

        # Synapses
        self.acetyl_synapse = synapses[0]  # excitatory (from motor cortex)
        self.glycin_synapse = synapses[1]  # inhibitory (from Renshaw cell)

        # initialize arrays
        self.t = np.linspace(0, self.T, int(self.T / self.dt + 1))
        self.g_tot = np.zeros((N, len(self.t)))
        self.Vm = Vm_rest * np.ones((N, len(self.t)), dtype=np.float128)
        self.spike_times = np.zeros((N, len(self.t)))

        self.anySpike = 0

    def step(self, inp, renshaw_feedback, t_, i):
        """
        Solves the DEQ and computes membrane potential.
        Saves membrane potential in self.Vm and spike times in self.spike_times

        Parameters
        ----------
        inp: ndarray of float [n_t]
            Input signal
        renshaw_feedback: ndarray of float
            Feedback from Renshaw Cell
        t_ : float
            Current time
        i : int
            Current index
        """
        x = 0  # self.glycin_synapse.step(renshaw_feedback, i)
        y = self.acetyl_synapse.step(inp, i)

        self.g_tot[:, i] = np.where(x + y < 0, 0, x + y)

        # if t_ > self.t_rest:
        self.Vm[:, i] = self.Vm[:, i - 1] + self.is_in_refrac * \
                        ((-(self.Vm[:, i - 1] - self.Vm_rest) - self.Vm[:, i - 1] * self.g_tot[:, i] * self.Rm) /
                         self.tau_mem * self.dt)
        firing_neurons = zip(*np.where(self.Vm[:, i] >= self.Vm_thr))

        for f in firing_neurons:
            if self.is_in_refrac[f] == 1:
                self.spike_times[f, i] = t_
                self.Vm[f, i] = self.Vm_rest
                self.t_rest[f] = t_ + self.t_refrac
                self.is_in_refrac[f] = 0
                self.anySpike = 1

        for k, t in enumerate(self.t_rest):
            if t_ > self.t_rest[k]:
                self.is_in_refrac[k] = 1

        # spike event (reset to Vm_rest and pause integrating during refractory period)
        if self.anySpike == 1:
            self.anySpike = 0
            return 1 / self.dt

        # if np.any(self.Vm[:, i] >= self.Vm_thr):
        #     # check if still in refract
        #     np.where(t_ > self.t_rest and self.Vm[:, i] >= self.Vm_thr, self.is_in_refrac, self.is_in_refrac + 1)
        #     print((self.is_in_refrac))
        #     self.spike_times.append(t_ * self.is_in_refrac)  # if in refrac append 0
        #     self.Vm[:, i] = self.Vm_rest * (1 - self.is_in_refrac) + self.Vm[:, i]  # TODO
        #     self.t_rest = (t_ + self.t_refrac) * (1 - self.is_in_refrac) + self.t_rest * self.is_in_refrac
        #
        #     np.where(self.Vm[:, i] >= self.Vm_thr, self.is_in_refrac,
        #              self.is_in_refrac * 0)  # Sets all Amn 0 when in refrac
        #
        #     return 1 / self.dt  # return spike

        return 0  # return no spike


class MotorUnit(object):
    """
    Motor unit
    """

    def __init__(self, muap, t):
        """
        Initializes motor unit instance

        Parameters
        ----------
        muap: ndarray of float [n_t]
            Motor unit action potential
        t: ndarray of float [n_t]
            Time axis corresponding to motor unit action potential
        t_total: ndarray of float [n_t]
            Total time axis of observation (has to fit to t)
        """

        self.muap = muap
        self.t = t

    def get_muap(self, spike_times, k):
        """
        Adds MUAPs of the motorunit at given spiketimes

        Parameters
        ----------
        spike_times: ndarray of float [n_spikes]
            Spike times

        Returns
        -------
        muap_total: ndarray of float [n_t]
            Total MUAP signal (MUAPs are summed at spiketimes)
        """
        muap_total = np.zeros(len(self.t))

        for tau in spike_times[k, :]:
            if not tau == 0:
                try:
                    idx_tau = np.argmin(np.abs(self.t - tau))
                    if len(muap_total) - idx_tau < len(self.muap):
                        muap_total[idx_tau:idx_tau + len(self.muap)] += self.muap[:len(muap_total) - idx_tau]
                    else:
                        muap_total[idx_tau:idx_tau + len(self.muap)] += self.muap

                except Exception as error:
                    print(error)
        return muap_total


class Muscle(object):
    """
    Muscle containing multiple motor unit instances
    """

    def __init__(self, alpha_motor_neurons, motor_units):
        """
        Initializes muscle instance

        Parameters
        ----------
        alpha_motor_neurons: list of AlphaMotorNeuron instances
            AlphaMotorNeuron instances of the muscle
        motor_units: list of MotorUnit instances
            MotorUnit instances corresponding to the AlphaMotorNeuron instances
        """

        self.alpha_motor_neurons = alpha_motor_neurons
        self.motor_units = motor_units
        self.t = self.alpha_motor_neurons.t
        self.N = self.alpha_motor_neurons.N
        self.mep = np.zeros(len(self.t))

        # import matplotlib.pyplot as plt
        # plt.plot(self.t, alpha_motor_neurons.Vm[80, :])
        # plt.title("80-Alpha-Motorneuron")
        # plt.xlabel("t[ms]")
        # plt.ylabel("PSP [mV]")
        # plt.show()

    def get_mep(self):
        for k in range(self.N):
            self.mep += self.motor_units[k].get_muap(self.alpha_motor_neurons.spike_times, k)

        return self.mep
