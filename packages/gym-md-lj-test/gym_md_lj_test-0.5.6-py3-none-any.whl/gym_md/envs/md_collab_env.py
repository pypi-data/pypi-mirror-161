from collections import defaultdict
from typing import DefaultDict, Dict, Final, List, Tuple
from PIL import Image
import numpy
import gym
from random import Random

from gym_md.envs.md_env import MdEnvBase
from gym_md.envs.agent.agent import Agent
from gym_md.envs.agent.companion_agent import CompanionAgent, DirectionalAgent
from gym_md.envs.renderer.collab_renderer import CollabRenderer
from gym_md.envs.agent.actioner import Actions
from gym_md.envs.point import Point
from gym_md.envs.setting import Setting
from gym_md.envs.definition import DIRECTIONAL_ACTIONS
from gym_md.envs.grid import Grid

JointActions = [List[float], List[float]]

class MdCollabEnv(MdEnvBase):
    def __init__(self, stage_name: str, action_type='path'):

        self.random = Random()
        self.stage_name: Final[str] = stage_name

        self.setting: Final[Setting] = Setting(self.stage_name)
        self.setting.DIRECTIONAL_ACTIONS: Final[List[str]] = DIRECTIONAL_ACTIONS
        self.setting.DIRECTIONAL_ACTION_TO_NUM: Final[Dict[str, int]] = Setting.list_to_dict(self.setting.DIRECTIONAL_ACTIONS)
        self.setting.NUM_TO_DIRECTIONAL_ACTION: Final[Dict[int, str]] = Setting.swap_dict(self.setting.DIRECTIONAL_ACTION_TO_NUM)

        self.grid: Grid = Grid(self.stage_name, self.setting)
        self.info: DefaultDict[str, int] = defaultdict(int)
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(7,))
        self.observation_space = gym.spaces.Box(
            low=0, high=self.setting.DISTANCE_INF, shape=(16,), dtype=numpy.int32
        )

        self.action_type = action_type
        if self.action_type=='directional':
            self.agent: DirectionalAgent = DirectionalAgent(self.grid, self.setting, self.random, self.action_type)
        else:
            self.agent: Agent = Agent(self.grid, self.setting, self.random)

        self.c_agent: CompanionAgent = CompanionAgent(self.grid, self.setting, self.random, self.action_type)
        self.c_renderer: Final[CollabRenderer] = CollabRenderer(self.grid, self.agent, self.setting, self.c_agent)
        self.directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']

    def reset(self) -> List[int]:
        """環境をリセットする."""
        super().reset()
        self.c_agent.reset()
        return self._get_observation()

    def _get_observation_c_agent(self) -> List[int]:
        """環境の観測を取得する.

        Returns
        -------
        list of int
            エージェントにわたす距離の配列 (len: 8)
        """
        sd, _ = self.c_agent.path.get_distance_and_prev(
            y=self.c_agent.y, x=self.c_agent.x, safe=True
        )
        ud, _ = self.c_agent.path.get_distance_and_prev(
            y=self.c_agent.y, x=self.c_agent.x, safe=False
        )
        sd = self.c_agent.path.get_nearest_distance(sd)
        ud = self.c_agent.path.get_nearest_distance(ud)
        ret = [
            ud["M"],
            ud["T"],
            sd["T"],
            ud["P"],
            sd["P"],
            ud["E"],
            sd["E"],
            self.c_agent.hp,
        ]
        return numpy.array(ret, dtype=numpy.int32)

    def _get_observation(self) -> List[int]:
        """環境の観測を取得する.

        Returns
        -------
        list of int
            エージェントにわたす距離の配列 (len: 9)
        """
        ret = super()._get_observation()
        c_ret = self._get_observation_c_agent()
        return numpy.append(ret, c_ret).astype(numpy.int32)

    def _is_done(self) -> bool:
        """ゲームが終了しているか.

        Returns
        -------
        bool
        """
        agent_1_end = super()._is_done()
        return agent_1_end or self.c_agent.is_exited() or self.c_agent.is_dead()

    def __return_position_based_on_action(self, pos: Point, direction: str) -> Point:
        """Returns a Point based on the input direction.

        Attributes
        ----------
        pos: Point
            Tuple[int, int]
            The reference point position to be used.
        direction: str
            The point direction to return, where direction
            is a value within ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'].


        Notes
        -----
        A neighbouring position can fall within the following regions:
           NW                      NORTH                     NE
                           | -1  || -1  || +1  |
        WEST               | -1  || pos || +1  |                EAST
                           | -1  || +1  || +1  |
           SW                      SOUTH                     SE

        Direction calculations:
            northwards = (pos[0]-1, pos[1])
            northeast = (pos[0]-1, pos[1]+1)
            eastwards = (pos[0], pos[1]+1)
            southeast = (pos[0]+1, pos[1]+1)
            southwards = (pos[0]+1, pos[1])
            southwest = (pos[0]+1, pos[1]-1)
            westwards = (pos[0], pos[1]-1)
            northwest = (pos[0]-1, pos[1]-1)

        Returns
        -------
        Point
        """
        if direction == 'n':
            return (pos[0]-1, pos[1])
        elif direction == 'ne':
            return (pos[0]-1, pos[1]+1)
        elif direction == 'e':
            return (pos[0], pos[1]+1)
        elif direction == 'se':
            return (pos[0]+1, pos[1]+1)
        elif direction == 's':
            return (pos[0]+1, pos[1])
        elif direction == 'sw':
            return (pos[0]+1, pos[1]-1)
        elif direction == 'w':
            return (pos[0], pos[1]-1)
        elif direction == 'nw':
            return (pos[0]-1, pos[1]-1)

    def _companion_in_range(self) -> bool:
        """Return true is companion agent is near main agent.

        Returns
        -------
        bool
        """
        pos = (self.agent.y, self.agent.x)
        neighbours = [self.__return_position_based_on_action(pos, d) for d in self.directions]
        return True if (self.c_agent.y, self.c_agent.x) in neighbours else False

    def _update_grid(self) -> None:
        """グリッドの状態を更新する.

        Notes
        -----
        メソッド内でグリッドの状態を**直接更新している**ことに注意．

        Returns
        -------
        None
        """
        agent_y, agent_x = self.agent.y, self.agent.x
        C = self.setting.CHARACTER_TO_NUM
        if self.agent.hp <= 0:
            return
        if (self.grid[agent_y, agent_x] in [C["P"], C["M"], C["T"]]) and (self._companion_in_range()):
            self.grid[agent_y, agent_x] = C["."]

    def _get_reward(self) -> float:
        """報酬を計算する.

        Returns
        -------
        int
            報酬

        """
        R = self.setting.REWARDS
        C = self.setting.CHARACTER_TO_NUM
        ret: float = -R.TURN
        y, x = self.agent.y, self.agent.x
        if self.agent.hp <= 0:
            return ret + R.DEAD
        if (self.grid[y, x] == C["T"]) and (self._companion_in_range()):
            ret += R.TREASURE
        if (self.grid[y, x] == C["E"]):
            ret += R.EXIT
        if (self.grid[y, x] == C["M"]) and (self._companion_in_range()):
            ret += R.KILL
        if (self.grid[y, x] == C["P"]) and (self._companion_in_range()):
            ret += R.POTION
        return ret

    def step(self, actions: JointActions) -> Tuple[List[int], int, bool, DefaultDict[str, int]]:
        """エージェントが1ステップ行動する.

        Attributes
        ----------
        actions: Actions
            list of int
            各行動の値を入力する

        Notes
        -----
        行動列をすべて入力としている
        これはある行動をしようとしてもそのマスがない場合があるため
        その場合は次に大きい値の行動を代わりに行う．

        Returns
        -------
        Tuple of (list of int, int, bool, dict)
        """
        observation, reward, done, self.info = super().step(actions[0])

        c_action: Final[str] = self.c_agent.select_action(actions[1])
        self.c_agent.take_action(c_action)
        reward: int = self._get_reward()
        done: bool = self._is_done()
        self._update_grid()

        return observation, reward, done, self.info

    def render(self, mode="human") -> Image:
        """画像の描画を行う.

        Notes
        -----
        画像自体も取得できるため，保存も可能.

        Returns
        -------
        Image
        """
        return self.c_renderer.render(mode=mode)

    def generate(self, mode="human") -> Image:
        """画像を生成する.

        Notes
        -----
        画像の保存などの処理はgym外で行う.

        Returns
        -------
        Image
        """
        return self.c_renderer.generate(mode=mode)