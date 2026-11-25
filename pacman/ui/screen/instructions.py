from ...config import Config
from ..button import Action
from ..window import Key, Window
from ...path import ASSET_DIR

BACKGROUND_PATH = ASSET_DIR / "menu_bg.png"
TITLE_PATH = ASSET_DIR / "instructions_title.png"
BUBBLE_PATHS = [ASSET_DIR / f"instructions_bubble_{i}.png" for i in range(1, 5)]

TITLE_Y = 0.04
GRID_TOP_GAP = 0.03
BUBBLE_GAP = 40


class InstructionsScreen:
    """Title on top, then 4 bubbles in a 2 x 2 grid. Everything is an image."""

    def __init__(self, window: Window, config: Config) -> None:
        self._window = window
        self._background = window.load_image(BACKGROUND_PATH)
        self._title = window.load_image(TITLE_PATH)
        self._bubbles = [window.load_image(path) for path in BUBBLE_PATHS]
        self._positions = self._layout()

    def _layout(self) -> list[tuple[int, int]]:
        """Top-left pixel of each bubble, as a 2 x 2 grid."""
        window = self._window
        first = next((b for b in self._bubbles if b is not None), None)
        w = first.get_width() if first else 0
        h = first.get_height() if first else 0
        title_h = self._title.get_height() if self._title else 0
        top = (window.ratio_y(TITLE_Y) + title_h
               + window.ratio_y(GRID_TOP_GAP))
        left = (window.width - (2 * w + BUBBLE_GAP)) // 2
        return [(left + col * (w + BUBBLE_GAP), top + row * (h + BUBBLE_GAP))
                for row in range(2) for col in range(2)]

    def update(self, keys: list[Key]) -> Action | None:
        for key in keys:
            if key is Key.QUIT:
                return Action.QUIT
            if key in (Key.ESCAPE, Key.ENTER):
                return Action.HOME
        return None

    def draw(self) -> None:
        window = self._window
        window.fill()
        if self._background is not None:
            window.blit_centered(self._background)
        if self._title is not None:
            window.blit_centered_x(self._title, window.ratio_y(TITLE_Y))
        for bubble, (x, y) in zip(self._bubbles, self._positions):
            if bubble is not None:
                window.blit(bubble, x, y)