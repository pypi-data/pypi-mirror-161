"""The essential wrappers for the control-specific environments."""
from typing import Callable, Tuple, Optional, Union
import pathlib

import numpy as np
import gym
from gym.spaces import Box
import imageio


class TransformObservation(gym.ObservationWrapper):
    """Wrapper that can transform observation via `transform()` function.

    Warning:
        Observation space should be updated if necessary.
    """

    def __init__(self, env: gym.Env, transform: Callable) -> None:
        super().__init__(env)
        self.transform = transform

    def observation(self, observation: np.ndarray) -> np.ndarray:
        return self.transform(observation)


class TransformAction(gym.ActionWrapper):
    """Wrapper that can transform action via `transform()` function.

    Warning:
        Action space should be updated if necessary.
    """

    def __init__(self, env: gym.Env, transform: Callable) -> None:
        super().__init__(env)
        self.transform = transform

    def action(self, action: Union[int, np.ndarray]) -> Union[int, np.ndarray]:
        return self.transform(action)


class TransformReward(gym.RewardWrapper):
    """Wrapper that can transform reward via `transform()` function.

    Warning:
        Reward range should be updated if necessary.
    """

    def __init__(self, env: gym.Env, transform: Callable) -> None:
        super().__init__(env)
        self.transform = transform

    def reward(self, reward: float) -> float:
        return self.transform(reward)


class Wrappers(gym.Wrapper):

    def __init__(
        self,
        env: gym.Env,
        max_episode_steps: Optional[int] = None,
        full_observation: bool = False,
        time_aware: bool = False,
        timestep_aware: bool = False,
        reference_aware: bool = False,
        tolerance_aware: bool = False,
        action_aware: bool = False,
        rescale_action: bool = False,
        action_min: Union[float, np.ndarray] = 0.0,
        action_max: Union[float, np.ndarray] = 1.0,
        track_episode: bool = False,
        record_episode: bool = False,
        path: Union[str, pathlib.Path] = '.cybergenetics_cache',
    ):
        if max_episode_steps is not None:
            env = LimitedTimestep(env, max_episode_steps)
        if full_observation:
            env = FullObservation(env)
        if time_aware:
            env = TimeAwareObservation(env)
        if timestep_aware:
            env = TimestepAwareObservation(env)
        if reference_aware:
            env = ReferenceAwareObservation(env)
        if tolerance_aware:
            env = ToleranceAwareObservation(env)
        if action_aware:
            env = ActionAwareObservation(env)
        if rescale_action:
            env = RescaleAction(env, action_min, action_max)
        if track_episode:
            env = TrackEpisode(env)
        if record_episode:
            env = RecordEpisode(env, path)
        super().__init__(env)


class LimitedTimestep(gym.Wrapper):
    """Wrapper that limits timesteps per episode."""

    def __init__(self, env: gym.Env, max_episode_steps: int) -> None:
        super().__init__(env)
        self.max_episode_steps = max_episode_steps

    def step(self, action: Union[int, np.ndarray]) -> Tuple[np.ndarray, float, bool, dict]:
        observation, reward, terminated, info = super().step(action)
        if len(self.buffer) > self.max_episode_steps:
            info['truncated'] = not terminated
            terminated = True
        return observation, reward, terminated, info


class TrackEpisode(gym.Wrapper):
    """Wrapper that keeps track of cumulative reward and episode length."""

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self.episode_return = None
        self.episode_length = None

    def reset(self) -> np.ndarray:
        observation = super().reset()
        self.episode_return = 0.0
        self.episode_length = 0
        return observation

    def step(self, action: Union[int, np.ndarray]) -> Tuple[np.ndarray, float, bool, dict]:
        observation, reward, terminated, info = super().step(action)
        self.episode_return += reward
        self.episode_length += 1
        if terminated:
            info['episode_return'] = self.episode_return
            info['episode_length'] = self.episode_length
        return observation, reward, terminated, info


class RecordEpisode(gym.Wrapper):
    """Wrapper that records video of an episode."""

    def __init__(self, env: gym.Env, path: Union[str, pathlib.Path]) -> None:
        super().__init__(env)
        self.path = pathlib.Path(path).joinpath('episode_cache')
        try:
            self.path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            pass
        self._frames = []

    def step(self, action: Union[int, np.ndarray]) -> Tuple[np.ndarray, float, bool, dict]:
        observation, reward, terminated, info = super().step(action)
        fig = super().render()
        frame = self.path.joinpath(f'fig{self.buffer.timestep.timestep}.png')
        fig.savefig(frame)
        self._frames.append(frame)
        if terminated:
            gif = self.path.parent.joinpath('episode.gif')
            with imageio.get_writer(gif, mode='I') as writer:
                for frame in self._frames:
                    writer.append_data(imageio.imread(frame))
        return observation, reward, terminated, info


class FullObservation(gym.ObservationWrapper):
    """Wrapper that observes physical internal state."""

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self.observation_space = Box(
            low=self.physics.state_min,
            high=self.physics.state_max,
            dtype=self.physics.dtype,
        )

    def observation(self, observation: np.ndarray) -> np.ndarray:
        return self.buffer.timestep.state


class TimeAwareObservation(gym.ObservationWrapper):
    """Wrapper that augments the observation with current time."""

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self.observation_space = Box(
            low=np.append(self.observation_space.low, 0.0),
            high=np.append(self.observation_space.high, np.inf),
            dtype=self.observation_space.dtype,
        )

    def observation(self, observation: np.ndarray) -> np.ndarray:
        return np.append(observation,
                         self.buffer.timestep.time).astype(self.observation_space.dtype)


class TimestepAwareObservation(gym.ObservationWrapper):
    """Wrapper that augments the observation with current timestep."""

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self.observation_space = Box(
            low=np.append(self.observation_space.low, 0.0),
            high=np.append(self.observation_space.high, np.inf),
            dtype=self.observation_space.dtype,
        )

    def observation(self, observation: np.ndarray) -> np.ndarray:
        return np.append(observation,
                         self.buffer.timestep.timestep).astype(self.observation_space.dtype)


class ReferenceAwareObservation(gym.ObservationWrapper):
    """Wrapper that augments the observation with current reference."""

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self.observation_space = Box(
            low=np.append(self.observation_space.low, 0.0),
            high=np.append(self.observation_space.high, np.inf),
            dtype=self.observation_space.dtype,
        )

    def observation(self, observation: np.ndarray) -> np.ndarray:
        return np.append(observation,
                         self.buffer.timestep.reference).astype(self.observation_space.dtype)


class ToleranceAwareObservation(gym.ObservationWrapper):
    """Wrapper that augments the observation with current tolerance."""

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self.observation_space = Box(
            low=np.append(self.observation_space.low, 0.0),
            high=np.append(self.observation_space.high, np.inf),
            dtype=self.observation_space.dtype,
        )

    def observation(self, observation: np.ndarray) -> np.ndarray:
        reference = self.buffer.timestep.reference
        tolerance = self.task.tolerance
        _in_tolerance = self.in_tolerance(observation, reference, tolerance)
        return np.append(observation, _in_tolerance).astype(self.observation_space.dtype)

    @staticmethod
    def in_tolerance(achieved, desired, tolerance):
        return float(np.abs(achieved - desired) / desired < tolerance)


class ActionAwareObservation(gym.ObservationWrapper):
    """Wrapper that augments the observation with current action."""

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self.observation_space = Box(
            low=np.append(self.observation_space.low, 0.0),
            high=np.append(self.observation_space.high, np.inf),
            dtype=self.observation_space.dtype,
        )

    def observation(self, observation: np.ndarray) -> np.ndarray:
        return np.append(observation,
                         self.buffer.timestep.action).astype(self.observation_space.dtype)


class RescaleAction(gym.ActionWrapper):
    """Wrapper that affinely rescales continuous action space."""

    def __init__(
        self,
        env: gym.Env,
        action_min: Union[float, np.ndarray] = 0.0,
        action_max: Union[float, np.ndarray] = 1.0,
    ) -> None:
        super().__init__(env)
        self._from_range = (self.action_space.low, self.action_space.high)
        self.action_space = Box(
            low=action_min,
            high=action_max,
            shape=(1,),
            dtype=self.action_space.dtype,
        )
        self._to_range = (self.action_space.low, self.action_space.high)

    def action(self, action: Union[int, np.ndarray]) -> Union[int, np.ndarray]:
        raise self.rescale(action, self._from_range, self._to_range)

    @staticmethod
    def rescale(data, from_range, to_range):
        _low, _high = from_range
        low, high = to_range
        return low + (data - _low) * (high - low) / (_high - _low)
