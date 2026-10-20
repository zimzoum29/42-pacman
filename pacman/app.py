import sys
import time
from typing import Optional

from .config import Config, ConfigError, load_config
from .highscores import Highscores
from .path import HIGHSCORES_DIR
from .ui.screen.base import Action, Screen
from .ui.screen.game import GameScreen
from .ui.screen.home import HomeScreen
from .ui.screen.leaderboard import LeaderboardScreen
from .ui.window import Window, WindowError

TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS
USAGE = "usage: python3 pac-man.py <config.json>"


class App:

    def __init__(self, window: Window, config: Config, highscores: Highscores) -> None:
        self._window = window
        self._config = config
        self._highscores = highscores
        self._screen = HomeScreen(window)

    def run(self) -> None:
        while True:
            start = time.monotonic()

            action = self._screen.update(self._window.keys())
            if action is Action.QUIT:
                return
            if action is not None:
                self._screen = self._next_screen(action)

            self._screen.draw()
            self._window.present()

            spare = FRAME_TIME - (time.monotonic() - start)
            if spare > 0:
                time.sleep(spare)

    def _next_screen(self, action: Action) -> Screen:
        if action is Action.PLAY:
            return GameScreen(self._window, self._config.seed)
        if action is Action.LEADERBOARD:
            return LeaderboardScreen(self._window, self._highscores.scores)
        return HomeScreen(self._window)


def load_files(config_path: str) -> tuple[Config, Highscores]:
    config = load_config(config_path)
    highscores = Highscores(HIGHSCORES_DIR / config.highscore_filename)
    return config, highscores


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 1

    try:
        config, highscores = load_files(argv[1])
    except ConfigError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    window: Optional[Window] = None
    try:
        window = Window()
        App(window, config, highscores).run()
    except WindowError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted")
    except Exception as e:
        print(f"[ERROR] unexpected error: {e!r}", file=sys.stderr)
        return 1
    finally:
        if window is not None:
            window.close()
    return 0