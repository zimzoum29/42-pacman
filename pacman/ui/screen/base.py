"""What every screen must provide, and how it asks to change screen."""
from enum import Enum, auto
from typing import Optional, Protocol

from ..window import Key


class Action(Enum):
    """Request sent by a screen to the main loop."""

    PLAY = auto()
    LEADERBOARD = auto()
    HOME = auto()
    QUIT = auto()


class Screen(Protocol):
    """Any object with these two methods can be used as a screen."""

    def update(self, keys: list[Key]) -> Optional[Action]:
        """Handle the pressed keys, return an Action to change screen."""
        ...

    def draw(self) -> None:
        """Draw the screen in the window."""
        ...