from enum import Enum, auto
from .window import Window

class Action(Enum):

    PLAY = auto()
    LEADERBOARD = auto()
    HOME = auto()
    QUIT = auto()

class Button:

    def __init__(self, window: Window, idle_path: str, active_path: str, action: Action):
        self.action = action
        self._idle = window.load_image(idle_path)
        self._active = window.load_image(active_path)

    @property
    def height(self):
        plate = self._idle or self._active
        return plate.get_height() if plate is not None else 0

    def plate(self, active: bool):
        return self._active if active else self._idle