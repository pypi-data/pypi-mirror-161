from typing import Optional, Tuple, Union

import gym
from gym.spaces import Discrete
import torch


class AsTensor(gym.Wrapper):
    """Wrapper that transforms data types to PyTorch tensors."""

    def __init__(
        self,
        env: gym.Env,
        dtype: torch.dtype = torch.float32,
        device: Optional[Union[str, torch.device]] = None,
    ) -> None:
        super().__init__(env)
        self.dtype = dtype
        self.device = device

    @property
    def state_dim(self) -> int:
        return self.observation_space.shape[0]

    @property
    def action_dim(self) -> int:
        if isinstance(self.action_space, Discrete):
            return self.action_space.n
        else:
            return self.action_space.shape[0]

    @property
    def action_sample(self) -> torch.Tensor:
        action = self.action_space.sample()
        return self.as_tensor(action, self.dtype, self.device)

    def reset(self) -> torch.Tensor:
        observation = self.env.reset()
        return self.as_tensor(observation, self.dtype, self.device)

    def step(self, action: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict]:
        if isinstance(self.action_space, Discrete):
            action = action.cpu().detach().item()
        else:
            action = action.view(-1).cpu().detach().numpy()
        observation, reward, done, info = self.env.step(action)
        observation = self.as_tensor(observation, self.dtype, self.device)
        reward = self.as_tensor(reward, self.dtype, self.device)
        done = self.as_tensor(done, self.dtype, self.device)
        return observation, reward, done, info

    @staticmethod
    def as_tensor(data, dtype, device):
        return torch.as_tensor(data, dtype=dtype, device=device).view(1, -1)
