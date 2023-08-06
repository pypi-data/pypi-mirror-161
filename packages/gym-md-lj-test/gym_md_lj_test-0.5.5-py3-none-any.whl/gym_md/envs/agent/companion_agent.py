from typing import List, Tuple
import random
from random import Random

from gym_md.envs.agent.agent import Agent
from gym_md.envs.point import Point
from gym_md.envs.agent.actioner import Actions
from gym_md.envs.grid import Grid
from gym_md.envs.setting import Setting


class CompanionAgent(Agent):
    def __init__(self, grid: Grid, setting: Setting, random: Random, action_type: str):
        super().__init__(grid, setting, random)
        self.action_type = action_type

    def _generate_free_spaces_list(self):
        self.grid_free_spaces: List[Point] = []
        for i in range(self.grid.H):
            for j in range(self.grid.W):
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["A"]:
                    self.grid_free_spaces.append((i,j))
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["S"]:
                    self.grid_free_spaces.append((i,j))
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["."]:
                    self.grid_free_spaces.append((i,j))
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["M"]:
                    self.grid_free_spaces.append((i,j))
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["T"]:
                    self.grid_free_spaces.append((i,j))
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["P"]:
                    self.grid_free_spaces.append((i,j))
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["E"]:
                    self.grid_free_spaces.append((i,j))

    def _init_player_pos(self) -> Point:
        """プレイヤーの座標を初期化して座標を返す.

        Notes
        -----
        初期座標を表すSを'.'にメソッド内で書き換えていることに注意する．

        Returns
        -------
        Point
            初期座標を返す

        """
        self._generate_free_spaces_list()

        for i in range(self.grid.H):
            for j in range(self.grid.W):
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["A"]:
                    self.grid[i, j] = self.setting.CHARACTER_TO_NUM["."]
                    self.grid_free_spaces.append((i,j))
                    return i, j

    def __return_position_based_on_action(self, pos: Point, action: str) -> Point:
        """Returns a new Point position based on the input directional action.

        Attributes
        ----------
        pos: Point
            Tuple[int, int]
            The reference point position to be used.
        action: str
            The directional action taken. Where action is a value
            within ['UP', 'DOWN', 'LEFT', 'RIGHT'].

        Notes
        -----
        A neighbouring position can fall within the following regions:
           NW                      NORTH                     NE
                           | -1  || -1  || +1  |
        WEST               | -1  || pos || +1  |                EAST
                           | -1  || +1  || +1  |
           SW                      SOUTH                     SE

        Direction calculations:
            up = (pos[0]-1, pos[1])
            right = (pos[0], pos[1]+1)
            down = (pos[0]+1, pos[1])
            left = (pos[0], pos[1]-1)

        Returns
        -------
        Point
        """
        new_pos = None
        if action == 'UP':
            new_pos = (pos[0]-1, pos[1])
        elif action == 'DOWN':
            new_pos = (pos[0]+1, pos[1])
        elif action == 'LEFT':
            new_pos = (pos[0], pos[1]-1)
        elif action == 'RIGHT':
            new_pos = (pos[0], pos[1]+1)

        if new_pos in self.grid_free_spaces:
            return new_pos
        else:
            return pos

    def select_action(self, actions: Actions) -> str:
        if self.action_type == 'directional':
            return self.select_directional_action(actions)
        else:
            return super().select_action(actions)

    def select_directional_action(self, actions: Actions) -> str:
        """行動を選択する.

        Notes
        -----
        行動を選択したときに，その行動が実行できない可能性がある．
        （マスがない可能性など）

        そのため，行動列すべてを受け取りできるだけ値の大きい実行できるものを選択する．
        **選択する**であり何も影響を及ぼさないことに注意．

        Parameters
        ----------
        actions: Actions
            行動列

        Returns
        -------
        str
            選択した行動IDを返す
        """
        actions_idx: List[Tuple[float, int]] = [(actions[i], i) for i in range(len(actions))]
        actions_idx.sort(key=lambda z: (-z[0], -z[1]))

        max_value = max(actions)
        max_actions = [i[1] for i in actions_idx if i[0]==max_value]
        random.shuffle(max_actions)

        # NUM_TO_DIRECTIONAL_ACTION =  {0: 'UP', 1: 'DOWN', 2: 'LEFT', 3: 'RIGHT'}
        action_out = self.setting.NUM_TO_DIRECTIONAL_ACTION[max_actions[0]]
        return action_out

    def take_action(self, action: str) -> None:
        if self.action_type == 'directional':
            return self.take_directional_action(action)
        else:
            return super().take_action(action)

    def take_directional_action(self, action: str) -> None:
        agent_pos = (self.y, self.x)
        new_pos = self.__return_position_based_on_action(agent_pos, action)
        self.y, self.x = new_pos
        self.be_influenced(y=self.y, x=self.x)


class DirectionalAgent(CompanionAgent):
    def _init_player_pos(self) -> Point:
        """プレイヤーの座標を初期化して座標を返す.

        Notes
        -----
        初期座標を表すSを'.'にメソッド内で書き換えていることに注意する．

        Returns
        -------
        Point
            初期座標を返す

        """
        self._generate_free_spaces_list()

        for i in range(self.grid.H):
            for j in range(self.grid.W):
                if self.grid[i, j] == self.setting.CHARACTER_TO_NUM["S"]:
                    self.grid[i, j] = self.setting.CHARACTER_TO_NUM["."]
                    self.grid_free_spaces.append((i,j))
                    return i, j