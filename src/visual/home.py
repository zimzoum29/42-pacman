import pygame

from .window import Key, Window
from .button import Action, Button

BACKGROUND_PATH = "assets/menu_bg.png"
TITLE_PATH = "assets/logo.png"

TITLE_Y = 0.05
FIRST_BUTTON_Y = 0.45
BUTTON_SPACING = 0.03

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