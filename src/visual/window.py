import pygame
import os
from enum import Enum, auto

Color = tuple[int, int, int]

BLACK: Color = (0, 0, 0)
WHITE: Color = (255, 255, 255)
YELLOW: Color = (255, 221, 0)

SCREEN_MARGIN = 80
MIN_HEIGHT = 480
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 1000

class WindowError(Exception):
    ...

class Key(Enum):

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    ENTER = auto()
    ESCAPE = auto()
    QUIT = auto()


_KEY_MAP: dict[int, Key] = {
    pygame.K_UP: Key.UP,
    pygame.K_DOWN: Key.DOWN,
    pygame.K_LEFT: Key.LEFT,
    pygame.K_RIGHT: Key.RIGHT,
    pygame.K_RETURN: Key.ENTER,
    pygame.K_ESCAPE: Key.ESCAPE,
}

class Window:

    def __init__(self, title: str = "Pac-Man"):
        try:
            pygame.init()
            pygame.font.init()
            self.width = WINDOW_WIDTH
            self.height = WINDOW_HEIGHT
            self._center_on_screen()
            self._surface = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(title)
        except pygame.error as exc:
            raise WindowError(f"cannot open window: {exc}") from exc
        self._fonts: dict[int, pygame.font.Font] = {}

    def _center_on_screen(self):
        info = pygame.display.Info()
        x = max((info.current_w - self.width) // 2, 0)
        y = max((info.current_h - self.height) // 2, 0)
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"

    def load_image(self, path: str):
        try:
            return pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError) as exc:
            print(f"warning: cannot load '{path}' ({exc})")
            return None

    def keys(self):
        pressed: list[Key] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pressed.append(Key.QUIT)
            elif event.type == pygame.KEYDOWN:
                key = _KEY_MAP.get(event.key)
                if key is not None:
                    pressed.append(key)
        return pressed

    def ratio_y(self, ratio: float):
        return int(self.height * ratio)

    def font_size(self, divisor: int):
        return max(self.height // divisor, 12)

    def fill(self, color: Color = BLACK):
        self._surface.fill(color)

    def blit_centered(self, image: pygame.Surface):
        x = (self.width - image.get_width()) // 2
        y = (self.height - image.get_height()) // 2
        self._surface.blit(image, (x, y))

    def text_centered(self, text: str, y: int, size: int, color: Color):
        surface = self._font(size).render(text, True, color)
        x = (self.width - surface.get_width()) // 2
        self._surface.blit(surface, (x, y))

    def present(self):
        pygame.display.flip()

    def close(self):
        pygame.quit()

    def _font(self, size: int):
        if size not in self._fonts:
            self._fonts[size] = pygame.font.Font(None, size)
        return self._fonts[size]

    def blit(self, image: pygame.Surface, x: int, y: int):
        self._surface.blit(image, (x, y))

    def blit_centered_x(self, image: pygame.Surface, y: int):
        x = (self.width - image.get_width()) // 2
        self.blit(image, x, y)