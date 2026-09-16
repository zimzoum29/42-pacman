from enum import Enum, auto
from typing import Optional

import pygame

from .window import Key, Window


class Action(Enum):

    PLAY = auto()
    LEADERBOARD = auto()
    QUIT = auto()


BACKGROUND_PATH = "assets/menu_bg.png"
TITLE_PATH = "assets/logo.png"

TITLE_Y = 0.08
FIRST_BUTTON_Y = 0.40
BUTTON_SPACING = 0.04


class Button:

    def __init__(self, window: Window, idle_path: str, active_path: str, action: Action) -> None:
        self.action = action
        self._idle = window.load_image(idle_path)
        self._active = window.load_image(active_path)

    @property
    def height(self) -> int:
        plate = self._idle or self._active
        return plate.get_height() if plate is not None else 0

    def plate(self, active: bool) -> Optional[pygame.Surface]:
        return self._active if active else self._idle


BUTTONS: tuple[tuple[str, str, Action], ...] = (
    ("assets/play.png", "assets/play_active.png", Action.PLAY),
    ("assets/leaderboard.png","assets/leaderboard_active.png",Action.LEADERBOARD),
    ("assets/exit.png", "assets/exit_active.png", Action.QUIT),
    )


class HomeScreen:

    def __init__(self, window: Window):
        self._window = window
        self._selected = 0
        self._background = window.load_image(BACKGROUND_PATH)
        self._title = window.load_image(TITLE_PATH)
        self._buttons = [
            Button(window, idle, active, action)
            for idle, active, action in BUTTONS
        ]

    def update(self, keys: list[Key]):
        for key in keys:
            if key in (Key.QUIT, Key.ESCAPE):
                return Action.QUIT
            if key is Key.UP:
                self._move(-1)
            elif key is Key.DOWN:
                self._move(1)
            elif key is Key.ENTER:
                return self._buttons[self._selected].action
        return None

    def draw(self):
        self._draw_background()
        self._draw_title()
        self._draw_buttons()

    def _move(self, step: int):
        self._selected = (self._selected + step) % len(self._buttons)

    def _draw_background(self):
        self._window.fill()
        if self._background is not None:
            self._window.blit_centered(self._background)

    def _draw_title(self):
        if self._title is not None:
            self._window.blit_centered_x(
                self._title, self._window.ratio_y(TITLE_Y)
            )

    def _draw_buttons(self):
        y = self._window.ratio_y(FIRST_BUTTON_Y)
        spacing = self._window.ratio_y(BUTTON_SPACING)
        for index, button in enumerate(self._buttons):
            plate = button.plate(index == self._selected)
            if plate is not None:
                x = (self._window.width - plate.get_width()) // 2
                self._window.blit(plate, x, y)
            y += button.height + spacing