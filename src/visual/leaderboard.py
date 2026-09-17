from .button import Action, Button
from .window import WHITE, YELLOW, Key, Window

BACKGROUND_PATH = "assets/menu_bg.png"

TITLE = "LEADERBOARD"
TITLE_Y = 0.10
TITLE_DIVISOR = 10

FIRST_ROW_Y = 0.26
ROW_SPACING = 0.06
ROW_DIVISOR = 22

MAX_ROWS = 10


class LeaderboardScreen:
    ...

    def __init__(self, window: Window, scores: dict[str, int]):
        self._window = window
        self._background = window.load_image(BACKGROUND_PATH)
        self._rows = sorted(scores.items(), key=lambda row: row[1], reverse=True)[:MAX_ROWS]

    def update(self, keys: list[Key]):
        for key in keys:
            if key is Key.QUIT:
                return Action.QUIT
            if key in (Key.ESCAPE, Key.ENTER):
                return Action.HOME
        return None

    def draw(self):
        self._draw_background()
        self._window.text_centered(TITLE, self._window.ratio_y(TITLE_Y), self._window.font_size(TITLE_DIVISOR), YELLOW)
        self._draw_rows()

    def _draw_background(self):
        self._window.fill()
        if self._background is not None:
            self._window.blit_centered(self._background)

    def _draw_rows(self):
        size = self._window.font_size(ROW_DIVISOR)
        y = self._window.ratio_y(FIRST_ROW_Y)
        if not self._rows:
            self._window.text_centered("NO SCORE YET", y, size, WHITE)
            return
        step = self._window.ratio_y(ROW_SPACING)
        for rank, (name, score) in enumerate(self._rows, start=1):
            line = f"{rank}. {name} - {score} pts"
            self._window.text_centered(line, y, size, WHITE)
            y += step
