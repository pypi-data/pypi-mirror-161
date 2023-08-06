# Configuration file for CRN Environment

# -- Import modules ------------------------------------------------------------------------------
import numpy as np

# -- Specify ODE for the physical simulation -----------------------------------------------------

# Parameters of the parametric ODE
TF_tot = 2000
k_on = 0.0016399
k_off = 0.34393
k_max = 13.588
K_d = 956.75
n = 4.203
k_basal = 0.02612
k_degR = 0.042116
k_trans = 1.4514
k_degP = 0.007

# Initial state of the parametric ODE: x(0)
yeast_init = np.array([0.0, k_basal / k_degR, (k_trans * k_basal) / (k_degP * k_degR)])


# Define the RHS of the parametric ODE: dx/dt = f(x(t), u(t))
def yeast_ode(x: np.ndarray, u: float) -> np.ndarray:
    TF_on, mRNA, Protein = x
    dTF_ondt = u * k_on * (TF_tot - TF_on) - k_off * TF_on
    dmRNAdt = k_basal + k_max * (TF_on**n) / (K_d**n + TF_on**n) - k_degR * mRNA
    dProteindt = k_trans * mRNA - k_degP * Protein
    dxdt = np.array([dTF_ondt, dmRNAdt, dProteindt])
    return dxdt


# -- Specify the target and reward in the task ---------------------------------------------------


# target
def multistage(t: np.ndarray, stages: np.ndarray) -> np.ndarray:
    stages = np.concatenate((np.zeros((1, 2)), stages), axis=0)
    y = np.zeros_like(t)
    y[0] = stages[1, 1]
    for i in range(stages.shape[0] - 1):
        mask = (t > stages[i, 0]) & (t <= stages[i + 1, 0])
        np.place(y, mask, stages[i + 1, 1])
    return y


# reward

# -- Environment configuration -------------------------------------------------------------------
configs = {
    'environment': {
        'discrete': False,
        'render_mode': 'dashboard',
        'physics': {
            'ode': yeast_ode,
            'init_state': yeast_init,
            'system_noise': 0.0,
            'actuation_noise': 0.0,
            'state_min': 0.0,
            'state_max': np.inf,
            'state_dtype': np.float32,
            'state_info': {
                'color': ['tab:red', 'tab:purple', 'tab:green'],
                'label': ['TF_on', 'mRNA', 'Protein'],
                'ylim': [-0.5, 4000],
            },
            'control_min': 0.0,
            'control_max': 80.0,     # control signal u: intensity ranging from 0.0 to 80.0
            'control_dtype': float,
            'control_info': {
                'color': 'tab:blue',
                'label': 'I',
                'ylim': [-0.5, 100],
            },
        },
        'task': {
            'tracking': multistage,
            'stages': np.array([[200, 2400], [400, 3200], [600, 2800]]),
            'sampling_rate': 10,     # sampling rate: in min
            'dim_observed': -1,     # only signal Protein can be observed
            'tolerance': 0.05,
            'reward': 'gauss',
            'reward_kwargs': {},
            'reward_info': {
                'color': 'tab:orange',
                'label': 'gauss',
                'ylim': [-0.05, 1.1],
            },
            'observation_noise': 0.0,
            'action_min': -1.0,
            'action_max': 1.0,
            'action_dtype': np.float32,
            'action_info': {},
        },
    },
    'wrappers': {
        'max_episode_steps': 60,
        'full_observation': False,
        'time_aware': False,
        'timestep_aware': False,
        'reference_aware': False,
        'tolerance_aware': False,
        'action_aware': False,
        'rescale_action': False,
        'action_min': 0.0,
        'action_max': 1.0,
        'track_episode': False,
        'record_episode': True,
    },
}
