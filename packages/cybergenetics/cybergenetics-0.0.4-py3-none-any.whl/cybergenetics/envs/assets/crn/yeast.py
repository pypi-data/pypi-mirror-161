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
init_state = np.array([0.0, k_basal / k_degR, (k_trans * k_basal) / (k_degP * k_degR)])


# Define the RHS of the parametric ODE: dx/dt = f(x(t), u(t))
def ode(x: np.ndarray, u: float) -> np.ndarray:
    TF_on, mRNA, Protein = x
    dTF_ondt = u * k_on * (TF_tot - TF_on) - k_off * TF_on
    dmRNAdt = k_basal + k_max * (TF_on**n) / (K_d**n + TF_on**n) - k_degR * mRNA
    dProteindt = k_trans * mRNA - k_degP * Protein
    dxdt = np.array([dTF_ondt, dmRNAdt, dProteindt])
    return dxdt


# -- Specify the target and reward in the task ---------------------------------------------------

# Define the target, i.e. the reference computation functioon
# def reference_func(t: np.ndarray) -> np.ndarray:
#     return

# Define the reward computation function
# def reward_func(
#     achieved: Union[float, np.ndarray],
#     desired: Union[float, np.ndarray],
#     tolerance: float,
# ) -> float:
#     return

# -- Environment configuration -------------------------------------------------------------------
configs = {
    'environment': {
        'discrete': False,
        'render_mode': 'dashboard',
        'physics': {
            'ode': ode,
            'init_state': init_state,
            'integrator': 'RK45',
            'n_sub_timesteps': 20,
            'system_noise': 0.0,
            'actuation_noise': 0.0,
            'state_min': 0.0,
            'state_max': float(np.finfo(np.float32).max),
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
            'tracking': 'const',
            'scale': 3200,
            'sampling_rate': 10,     # per min
            'observability': -1,     # only signal 'Protein' can be observed
            'reward': 'in_tolerance',
            'reward_kwargs': {},
            'reward_info': {
                'color': 'tab:orange',
                'label': 'in_tolerance',
                'ylim': [-0.05, 1.1],
            },
            'tolerance': 0.05,
            'observation_error': 0.05,
        },
    },
    'wrappers': {
        'max_episode_steps': 6 * 10,     # 10 hours
        'full_observation': False,
        'time_aware': False,
        'timestep_aware': False,
        'reference_aware': False,
        'tolerance_aware': False,
        'action_aware': False,
        'rescale_action': False,
        'action_min': 0.0,
        'action_max': 1.0,
        'track_episode': True,
        'record_episode': False,
    },
}
