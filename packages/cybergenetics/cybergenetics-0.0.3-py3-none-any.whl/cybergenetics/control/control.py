"""A gym.Env subclass for buffered control-specific environments based on physics and task."""
from typing import Callable, Optional, Tuple, Union, NamedTuple
import abc
import contextlib

import numpy as np
import gym
from gym.utils import seeding


class Timestep(NamedTuple):

    timestep: int
    time: float
    control: Union[float, np.ndarray]
    physical_control: Union[float, np.ndarray]
    state: np.ndarray
    action: Union[int, np.ndarray]
    observation: np.ndarray
    reference: np.ndarray
    reward: float


class Trajectory(Timestep):
    pass


class Buffer(abc.ABC):
    """Buffer for environments."""

    _data = []

    def __len__(self) -> int:
        return len(self._data)

    def __copy__(self):
        # TODO: handle copy in the future
        raise NotImplementedError("Call the method 'copy()' instead")

    @property
    def timestep(self) -> Optional[Timestep]:
        """Returns the current timestep if the buffer is not empty."""
        if len(self._data) == 0:
            return None
        return self._data[-1]

    @property
    def trajectory(self) -> Optional[Trajectory]:
        """Returns the current trajector if the buffer is not empty."""
        if len(self._data) == 0:
            return None
        return Trajectory(*zip(*self._data))

    def copy(self):
        "Returns a copy of the buffer."
        import copy
        instance = self.__class__.__new__(self.__class__)
        instance.__dict__['_data'] = copy.deepcopy(self.__dict__['_data'])
        return instance

    def empty(self) -> bool:
        "Whether the buffer is empty."
        return len(self._data) == 0

    def push(self, *timestep) -> None:
        "Push a timestep into the buffer."
        self._data.append(Timestep(*timestep))

    def flush(self) -> None:
        "Flushes the buffer."
        self._data.clear()


class Physics(abc.ABC):
    """Simulates a controlled physical dynamical system."""

    _timestep = None
    _time = None
    _control = None
    _physical_control = None
    _state = None

    _np_random = None

    @property
    def np_random(self) -> seeding.RandomNumberGenerator:
        """Lazily seeds for the random number generator(s) since it is expensive and only needed
        if sampling.
        """
        if self._np_random is None:
            self.seed()
        return self._np_random

    @abc.abstractmethod
    def dynamics(
        self,
        time: float,
        state: np.ndarray,
        control: Union[float, np.ndarray],
    ) -> np.ndarray:
        """Defines the ODEs for the dynamical system at every call.

        Should be overridden by all subclasses.

        Args:
            time (float): The simulation time (implicit in the ODEs).
            state (np.ndarray): The simulation state.
            control (Union[float, np.ndarray]): The control signal for the actuators.
        """
        raise NotImplementedError

    def set_control(self, control: Union[float, np.ndarray]) -> None:
        """Sets the control signal for the actuators.

        ```python
        self._control = control
        self._physical_control = control
        ```

        Args:
            control (Union[float, np.ndarray]): A valid control signal.
        """
        raise NotImplementedError

    @contextlib.contextmanager
    def reset_context(self):
        """Context manager for resetting the simulation state.

        Sets the internal simulation to a default state when entering the block.

        ```python
        with physics.reset_context():
            task.reset(physics)
        task.step()
        ```

        Yields:
            The `Physics` instance.
        """
        try:
            self.reset()
        except PhysicsError:
            pass
        finally:
            yield self

    @abc.abstractmethod
    def reset(self) -> None:
        """Resets the simulation state."""
        raise NotImplementedError

    @abc.abstractmethod
    def step(self, sampling_rate: float = 1.) -> None:
        """Updates the simulation state.

        Args:
            sampling_rate (float): How often to repeatedly update the simulation state (optional).
        """
        raise NotImplementedError

    def seed(self, seed: Optional[int] = None) -> None:
        """Seeds for the random number generator(s)."""
        self._np_random, _ = seeding.np_random(seed)

    def timestep(self) -> int:
        """Returns the simulation timestep."""
        return self._timestep

    def time(self) -> float:
        """Returns the elapsed simulation time."""
        return self._time

    def control(self) -> Union[float, np.ndarray]:
        """Returns the simulating control signal for the actuators."""
        return self._control

    def physical_control(self) -> Union[float, np.ndarray]:
        """Returns the physical control signal for the actuators."""
        return self._physical_control

    def state(self) -> np.ndarray:
        """Returns the simulation state."""
        return self._state


class PhysicsError(RuntimeError):
    """Raised if the state of the physical simulation becomes divergent."""
    pass


class Task(abc.ABC):
    """Defines a task based on the physical simulation."""

    reference_registry = {}
    reward_registry = {}

    _observation = None
    _reference = None
    _reward = None

    _np_random = None

    @property
    def np_random(self) -> seeding.RandomNumberGenerator:
        """Lazily seeds since it is expensive and only needed if sampling."""
        if self._np_random is None:
            self.seed()
        return self._np_random

    @abc.abstractmethod
    def target(self, time: float) -> np.ndarray:
        """Defines the target for the task at every call.

        Should be overridden by all subclasses.

        Args:
            time (float): The simulation time.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def action_space(self, physics: Physics) -> gym.Space:
        """Returns a valid action space for the task."""
        raise NotImplementedError

    @abc.abstractmethod
    def observation_space(self, physics: Physics) -> gym.Space:
        """Returns a valid observation space for the task."""
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self, physics: Physics) -> None:
        """Sets the initial state of the environment at the start of an episode.

        Args:
            physics (Physics): Instance of `Physics`.
        """
        raise NotImplementedError

    def after_reset(self, physics: Physics) -> None:
        """Optional method to update the task before stepping forward."""
        pass

    def before_step(self, action: Union[int, np.ndarray], physics: Physics) -> None:
        """Updates the task from the provided action.

        Should be called before stepping the physical simulation.

        ```python
        control = action
        physics.set_control(control)
        ```

        Args:
            action (Union[int, np.ndarray]): A valid action drawing from the action space.
            physics (Physics): Instance of `Physics`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def step(self, physics: Physics) -> None:
        """Updates the task by stepping the physical simulation.

        Args:
            physics (Physics): Instance of `Physics`.
        """
        raise NotImplementedError

    def after_step(self, physics: Physics) -> None:
        """Optional method to update the task after stepping the physical simulation."""
        pass

    def seed(self, seed: Optional[int] = None) -> None:
        """Seeds for the random number generator(s)."""
        self._np_random, _ = seeding.np_random(seed)

    @classmethod
    def register_reference(cls, reference: Callable) -> Callable:
        """Decorator to register a reference computation function.

        ```python
        @Task.register_reference
        def const(t: np.ndarray) -> np.ndarray:
            return CONST + np.zeros_like(t)
        ```

        Args:
            reference (Callable): The reference computation function.
        """
        cls.reference_registry[reference.__name__] = reference
        return reference

    @classmethod
    def register_reward(cls, reward: Callable) -> Callable:
        """Decorator to register a reward computation function.

        ```python
        @Task.register_reward
        def in_tolerance(
            achieved: Union[float, np.ndarray],
            desired: Union[float, np.ndarray],
            tolerance: float,
        ) -> float:
            return float(abs(achieved - desired) / desired < tolerance)
        ```

        Args:
            reward (Callable): The reward computation function.
        """
        cls.reward_registry[reward.__name__] = reward
        return reward

    def observation(self, physics: Physics) -> np.ndarray:
        """Returns an observation from the environment."""
        raise NotImplementedError

    def reference(self, physcis: Physics) -> np.ndarray:
        """Returns the reference corresponding to the task target."""
        raise NotImplementedError

    def reward(self, physics: Physics) -> float:
        """Returns a reward from the environment."""
        raise NotImplementedError

    def terminated(self, physics: Physics) -> bool:
        """Whether the episode should be terminated."""
        return False

    def info(self, physics: Physics) -> dict:
        """Returns the extras."""
        return {}


class Environment(gym.Env):
    """Buffered environment based on physics and task."""

    _buffer = None

    def __init__(self, physics: Physics, task: Task) -> None:
        """Initializes an environment.

        Args:
            physics: Instance of `Physics`.
            task: Instance of `Task`.
        """
        self._buffer = Buffer()
        self._physics = physics
        self._task = task
        self.action_space = self._task.action_space(self._physics)
        self.observation_space = self._task.observation_space(self._physics)

    @property
    def buffer(self) -> Buffer:
        """Returns the buffer of the environment."""
        return self._buffer

    @property
    def physics(self) -> Physics:
        """Returns the physics of the environment."""
        return self._physics

    @property
    def task(self) -> Task:
        """Returns the task of the environment."""
        return self._task

    def reset(self) -> np.ndarray:
        """Resets the environment starting a new episode.

        Returns:
            observation (np.ndarray): An observation from the environment.
        """
        self._buffer.flush()
        with self._physics.reset_context():
            self._task.reset(self._physics)
        self._task.after_reset(self._physics)
        timestep = self._physics.timestep()
        time = self._physics.time()
        control = None
        physical_control = None
        state = self._physics.state()
        action = None
        observation = self._task.observation(self._physics)
        reference = self._task.reference(self._physics)
        reward = None
        self._buffer.push(
            timestep,
            time,
            control,
            physical_control,
            state,
            action,
            observation,
            reference,
            reward,
        )
        return observation

    def step(self, action: Union[int, np.ndarray]) -> Tuple[np.ndarray, float, bool, dict]:
        """Updates the environment.

        Args:
            action (Union[int, np.ndarray]):

        Returns:
            observation (np.ndarray): An observation from the environment.
            reward (float): An observation from the environment.
            terminated (bool): Whether the episode should be terminated.
            info (dict): The extras.
        """
        if self._buffer.empty():
            raise RuntimeError
        self._task.before_step(action, self._physics)
        self._task.step(self._physics)
        self._task.after_step(self._physics)
        timestep = self._physics.timestep()
        time = self._physics.time()
        control = self._physics.control()
        physical_control = self._physics.physical_control()
        state = self._physics.state()
        observation = self._task.observation(self._physics)
        reference = self._task.reference(self._physics)
        reward = self._task.reward(self._physics)
        terminated = self._task.terminated(self._physics)
        info = self._task.info(self._physics)
        self._buffer.push(
            timestep,
            time,
            control,
            physical_control,
            state,
            action,
            observation,
            reference,
            reward,
        )
        return observation, reward, terminated, info

    def replay(self, buffer: Optional[Buffer] = None) -> None:
        """Replays the buffer of the environment."""
        if self._buffer.empty() and (buffer is None):
            raise RuntimeError
        buffer = self._buffer if buffer is None else buffer
        raise NotImplementedError

    def close(self) -> None:
        """Cleans up the buffer of the environment."""
        self._buffer = None

    def seed(self, seed: Optional[int] = None) -> None:
        """Seeds for the random number generator(s)."""
        self._np_random, _ = seeding.np_random(seed)
        self._physics.seed(seed)
        self._task.seed(seed)
