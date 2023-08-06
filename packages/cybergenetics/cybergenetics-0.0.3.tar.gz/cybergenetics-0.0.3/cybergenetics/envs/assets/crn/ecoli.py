# Configuration file for CRN Environment

# -- Import modules ------------------------------------------------------------------------------
import numpy as np

# -- Specify ODE for the physical simulation -----------------------------------------------------

# Parameters of the parametric ODE
d_r = 0.0956
d_p = 0.0214
k_m = 0.0116
b_r = 0.0965

# Initial state of the parametric ODE: x(0)
init = np.array([1.0, 1.0, 1.0])


# Define the RHS of the parametric ODE: dx/dt = f(x(t), u(t))
def ode(x: np.ndarray, u: float) -> np.ndarray:
    a = np.array([1, 5.134 / (1 + 5.411 * np.exp(-0.0698 * u)) + 0.1992 - 1])
    A_c = np.array([[-d_r, 0.0, 0.0], [d_p + k_m, -d_p - k_m, 0.0], [0.0, d_p, -d_p]])
    B_c = np.array([[d_r, b_r], [0.0, 0.0], [0.0, 0.0]])
    dxdt = A_c @ x + B_c @ a
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
            'ode': ode,
            'init_state': init,
            'n_sub_timesteps': 20,
            'state_info': {
                'color': ['tab:red', 'tab:purple', 'tab:green'],
                'label': ['R', 'P', 'G'],
                'ylim': [0.8, 2.2],
            },
            'control_max': 20.0,     # control signal u: intensity (%) ranging from 0.0% to 20.0%
            'control_info': {
                'color': 'tab:blue',
                'label': 'I (%)',
                'ylim': [-0.5, 20.5],
            },
        },
        'task': {
            'tracking': 'const',
            'scale': 1.8,
            'sampling_rate': 10,     # sampling rate: in min
            'dim_observed': -1,     # only signal G can be observed
            'tolerance': 0.05,
            'reward': 'gauss',
            'reward_info': {
                'color': 'tab:orange',
                'label': 'gauss',
                'ylim': [-0.05, 1.1],
            },
        },
    },
    'wrappers': {
        'max_episode_steps': 60,
        'record_episode': True,
    },
}
