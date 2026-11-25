from ...config import Config
from ..button import Action
from ..window import WHITE, YELLOW, Key, Window
from ...path import ASSET_DIR

BACKGROUND_PATH = ASSET_DIR / "menu_bg.png"

TITLE = "INSTRUCTIONS"
TITLE_Y = 0.10
TITLE_FONT_SIZE = 100
LINE_FONT_SIZE = 45
FIRST_LINE_Y = 0.24
LINE_SPACING = 0.065
FOOTER = "PRESS ENTER OR ESC TO GO BACK"
FOOTER_Y = 0.90


class InstructionsScreen:

    def __init__(self, window: Window, config: Config) -> None:
        self._window = window
        self._background = window.load_image(BACKGROUND_PATH)

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