"""Image Generate module."""
from os import path
from typing import Final, List

from PIL import Image

from gym_md.envs.agent.agent import Agent
from gym_md.envs.agent.companion_agent import CompanionAgent
from gym_md.envs.grid import Grid
from gym_md.envs.renderer.generator import Generator, tiles_dir, LENGTH



class CollabGenerator(Generator):
    """Generator class."""

    def __init__(self, grid: Grid, agent: Agent, agent_2: CompanionAgent):
        super().__init__(grid, agent)
        self.companion_agent: Final[CompanionAgent] = agent_2

        self.tiles_dir = path.join(path.dirname(__file__), path.pardir, "tiles/collab_dungeon")
        self.tiles_names: Final[List[str]] = [
            "free.png",
            "walls.png",
            "treasure.png",
            "potion.png",
            "enemy.png",
            "exit.png",
            "player.png",
            "dungeon_bones.png",
        ]
        self.tiles_paths: Final[List[str]] = [path.join(self.tiles_dir, t) for t in self.tiles_names]
        self.tiles_images = [Image.open(t).convert("RGBA") for t in self.tiles_paths]
        self.split_images = [[x for x in img.split()] for img in self.tiles_images]

        self.LENGTH: Final[int] = 20

    def generate(self) -> Image:
        """画像を生成する.

        Returns
        -------
        Image

        """
        img = super().generate()

        side_kick_sprite = Image.open(f"{path.join(tiles_dir, 'side_kick.png')}").convert("RGBA")
        side_kick_death_sprite = Image.open(f"{path.join(tiles_dir, 'deadhero.png')}").convert("RGBA")
        split_images = [[x for x in img.split()] for img in [side_kick_sprite, side_kick_death_sprite]]

        sprite = side_kick_sprite if self.companion_agent.hp > 0 else side_kick_death_sprite
        sprite_split_image = split_images[0] if self.companion_agent.hp > 0 else split_images[1]
        
        img.paste(sprite, (LENGTH * self.companion_agent.x, self.companion_agent.y * LENGTH), sprite_split_image[3])
        return img

    def generate_alternative_sprites(self) -> Image:
        """画像を生成する.

        Returns
        -------
        Image

        """
        img = Image.new("RGB", (self.W * LENGTH, self.H * LENGTH))
        for i in range(self.H):
            for j in range(self.W):
                img.paste(self.tiles_images[0], (LENGTH * j, i * LENGTH))
                e: int = self.grid[i, j]
                if i == self.agent.y and j == self.agent.x:
                    e = 6 if self.agent.hp > 0 else 7
                img.paste(self.tiles_images[e], (LENGTH * j, i * LENGTH), self.split_images[e][3])

        side_kick_sprite = Image.open(f"{path.join(self.tiles_dir, 'player_2.png')}").convert("RGBA")
        side_kick_death_sprite = Image.open(f"{path.join(self.tiles_dir, 'dungeon_bones.png')}").convert("RGBA")
        split_images = [[x for x in img.split()] for img in [side_kick_sprite, side_kick_death_sprite]]

        sprite = side_kick_sprite if self.companion_agent.hp > 0 else side_kick_death_sprite
        sprite_split_image = split_images[0] if self.companion_agent.hp > 0 else split_images[1]

        img.paste(sprite, (self.LENGTH * self.companion_agent.x, self.companion_agent.y * self.LENGTH), sprite_split_image[3])
        return img
