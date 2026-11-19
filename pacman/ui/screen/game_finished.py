import time
import pygame

from ...game.game import Game, Status
from ..window import Window, Key, WHITE, BLACK
from ..button import Action


class EndScreen:

    def __init__(self, window: Window, game: Game) -> None:
        self._window = window
        self._game_score = game.score
        self._game_status = game.status

        text_bar_w = 800
        text_bar_h = 200
        text_bar_x = self._window.height // 2
        text_bar_y = self._window.width // 4
        text_bar_max_len = 10#temp ??
        text_bar_authorized_characters = "QWERTYUIOPASDFGHJKLZXCVBNM0123456789 "
        self._input_name = TextBar(window,
                                   text_bar_w,
                                   text_bar_h,
                                   text_bar_x,
                                   text_bar_y,
                                   text_bar_max_len,
                                   text_bar_authorized_characters)

    def update(self, keys: list[Key]) -> Action | None:
        for key in keys:
            if key is Key.QUIT:
                return Action.QUIT
            if key is Key.ESCAPE:
                return Action.HOME
            self._input_name.update(key)

    def draw(self) -> None:
        self._input_name.draw()

    def _draw_victory(self) -> None:
        ...

    def _draw_defeat(self) -> None:
        ...

    def _draw_name_input(self) -> None:
        ...

    def _draw_stats(self) -> None:
        ...


class TextBar:

    def __init__(self,
                 window: Window,
                 w: int,
                 h: int,
                 x: int,
                 y: int,
                 max_characters: int,
                 authorized_characters: str) -> None:
        self._window = window
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self._max_characters = max_characters
        self._authorized_characters = authorized_characters

        self.actual_text = ""
        self.text_len = 0
        self._cursor_blink = 0.5
        self._last_blink = time.monotonic()
        self._cursor_printed = True
        self._cursor_index = 0

    def update(self, key: Key) -> None:
        print(type(pygame.key.name(key.value)))
        if key is Key.BACKSPACE and self._cursor_index > 0:
            self.actual_text = (self.actual_text[:self._cursor_index - 1]
                                + self.actual_text[self._cursor_index:])
            self._cursor_index -= 1
            self.text_len -= 1
        elif key is Key.LEFT and self._cursor_index > 0:
            self._cursor_index -= 1
        elif key is Key.RIGHT and self._cursor_index < self.text_len:
            self._cursor_index += 1
        elif (len(key.char) == 1
              and key.char.upper() in self._authorized_characters
              and self.text_len < self._max_characters):
            self.actual_text = (self.actual_text[:self._cursor_index]
                                + key.char
                                + self.actual_text[self._cursor_index:])
            print("?")
            self._cursor_index += 1
            self.text_len += 1

    def draw(self) -> None:
        self._draw_bar()
        self._draw_text()
        self._draw_cursor()

    def _draw_bar(self) -> None:
        self._window.draw_rounded_rect(self.x, self.y, self.w, self.h, 2, BLACK)
        self._window.draw_rounded_rect_outline(self.x, self.y, self.w, self.h, 2, WHITE)

    def _draw_text(self) -> None:
        self._window.text_centered_in_rect(self.actual_text, self.x, self.w, self.y, self.h // 2, WHITE)

    def _draw_cursor(self) -> None:
        now = time.monotonic()
        if now - self._last_blink > self._cursor_blink:
            self._cursor_printed = not self._cursor_printed
            self._last_blink = now

        if not self._cursor_printed:
            return

        ...#print le curseur dans le texte
