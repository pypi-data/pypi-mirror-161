"""renderer module."""
from typing import Final, Optional

import matplotlib.pyplot as plt
from PIL import Image

from gym_md.envs.agent.agent import Agent
from gym_md.envs.agent.companion_agent import CompanionAgent
from gym_md.envs.grid import Grid
from gym_md.envs.renderer.collab_generator import CollabGenerator
from gym_md.envs.renderer.renderer import Renderer
from gym_md.envs.setting import Setting


class CollabRenderer(Renderer):
    """Renderer class."""

    def __init__(self, grid: Grid, agent: Agent, setting: Setting, c_agent: CompanionAgent):
        super().__init__(grid, agent, setting)
        self.c_agent: Final[CompanionAgent] = c_agent
        self.c_generator: Final[CollabGenerator] = CollabGenerator(grid=grid, agent=agent, agent_2=c_agent)

    def generate(self, mode="human") -> Image:
        """画像を生成して返す.

        Parameters
        ----------
        mode:str

        Returns
        -------
        Image or None
        """
        if mode == "human":
            return self.c_generator.generate()

