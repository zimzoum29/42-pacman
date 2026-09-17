import sys
import time
from typing import Union

from .visual.button import Action
from .visual.home import HomeScreen
from .visual.leaderboard import LeaderboardScreen
from .visual.window import Window, WindowError
from .parsing import Parser

TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS

Screen = Union[HomeScreen, LeaderboardScreen]

def next_screen(action: Action, window: Window, highscores: dict[str, int]):
    if action is Action.LEADERBOARD:
        return LeaderboardScreen(window, highscores)
    if action is Action.PLAY:
        print("note: the game screen is not implemented yet")
    return HomeScreen(window)

def run(window: Window):
    screen = HomeScreen(window)
    running = True
    while running:
        start = time.monotonic()
        parser = Parser("test.json")
        config = parser.config
        highscores = parser.highscores
        action = screen.update(window.keys())
        if action is Action.QUIT:
            running = False
        elif action is not None:
            screen = next_screen(action, window, highscores)

        screen.draw()
        window.present()

        spare = FRAME_TIME - (time.monotonic() - start)
        if spare > 0:
            time.sleep(spare)

def main():
    window = None
    try:
        window = Window()
        run(window)
    except WindowError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted")
    finally:
        if window is not None:
            window.close()
    return 0