import pygame
import time

from ..window import Key, Window
from ..button import Action, Button
from ...path import ASSET_DIR

BACKGROUND_PATH = ASSET_DIR / "menu_bg.png"
TITLE_PATH = ASSET_DIR / "logo.png"

TITLE_Y = 0.04
FIRST_BUTTON_Y = 0.37
BUTTON_SPACING = 0.0

GHOST_Y = 0.92
PACMAN_Y = 0.914
SPRITE_SPEED = 660.0
GHOST_GAP = 0.065
FRAME_TIME_SPRITE = 0.15
GHOST_FRAME_TIME = 0.15
GHOST_FRAMES = 2
MAX_DT = 0.1

BUTTONS: tuple[tuple[str, str, Action], ...] = (
    (ASSET_DIR / "play.png", ASSET_DIR / "play_active.png", Action.PLAY),
    (ASSET_DIR / "instructions.png", ASSET_DIR / "instructions_active.png",
     Action.INSTRUCTIONS),
    (ASSET_DIR / "leaderboard.png", ASSET_DIR / "leaderboard_active.png",
     Action.LEADERBOARD),
    (ASSET_DIR / "exit.png", ASSET_DIR / "exit_active.png", Action.QUIT),
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
        self._ghost_frames = [
            window.load_image(ASSET_DIR / f"ghost_anim_{i}.png")
            for i in range(GHOST_FRAMES)
        ]
        self._ghost_phase = 0
        self._ghost_timer = 0.0
        self._pacman_x =  -window.width * GHOST_GAP
        self._ghost_x = 0.0
        self._pacman_y = window.ratio_y(PACMAN_Y)
        self._ghost_y = window.ratio_y(GHOST_Y)
        self._pacman_frames = [
            window.load_image(f"pacman/assets/pacman_{i}.png")
            for i in range(3)
        ]
        self._pacman_order = (0, 1, 2, 1)
        self._pacman_phase = 0
        self._pacman_timer = 0.0
        self._last_time = time.monotonic()

    def update(self, keys: list[Key]):
        now = time.monotonic()
        dt = min(now - self._last_time, MAX_DT)
        self._last_time = now
        self._move_sprites(dt)
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
        self._draw_sprites()
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

    def _move_sprites(self, delta: float):
        step = SPRITE_SPEED * delta
        self._pacman_x += step
        self._ghost_x += step
        if self._pacman_x > self._window.width:
            self._pacman_x = -self._window.width * GHOST_GAP * 2
        if self._ghost_x > self._window.width:
            self._ghost_x = -self._window.width * GHOST_GAP * 2
        self._pacman_timer += delta
        while self._pacman_timer >= FRAME_TIME_SPRITE:
            self._pacman_timer -= FRAME_TIME_SPRITE
            self._pacman_phase = (self._pacman_phase + 1) % len(
                self._pacman_order
            )
        self._ghost_timer += delta
        while self._ghost_timer >= GHOST_FRAME_TIME:
            self._ghost_timer -= GHOST_FRAME_TIME
            self._ghost_phase = (self._ghost_phase + 1) % GHOST_FRAMES

    def _draw_sprites(self):
        frame = self._pacman_frames[
            self._pacman_order[self._pacman_phase]
        ]
        if frame is not None:
            self._window.blit(
                frame, int(self._pacman_x), self._pacman_y
            )
        ghost = self._ghost_frames[self._ghost_phase]
        if ghost is not None:
            self._window.blit(ghost, int(self._ghost_x), self._ghost_y)