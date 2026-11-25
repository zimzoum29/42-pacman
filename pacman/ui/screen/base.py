from enum import Enum, auto
from typing import Optional, Protocol

from ..window import Key


class Action(Enum):

    PLAY = auto()
    LEADERBOARD = auto()
    HOME = auto()
    GAME_OVER = auto()
    QUIT = auto()
    INSTRUCTIONS = auto()


class Screen(Protocol):

    def update(self, keys: list[Key]) -> Optional[Action]:
        ...

    def draw(self) -> None:
        ...
