"""Entry point of the Pac-Man game."""
from __future__ import annotations

import sys
import time

from .visual.home import Action, HomeScreen
from .visual.window import Window, WindowError

TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS



def run(window: Window):
    screen = HomeScreen(window)
    running = True
    while running:
        start = time.monotonic()

        action = screen.update(window.keys())
        if action is Action.QUIT:
            running = False
        elif action is not None:
            print(f"selected: {action.name}")

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