import pygame
import os
import math
from enum import Enum, auto
from pathlib import Path

Color = tuple[int, int, int]

BLACK: Color = (0, 0, 0)
WHITE: Color = (255, 255, 255)
YELLOW: Color = (255, 210, 0)
CYAN: Color = (0, 255, 255)
BLUE: Color = (0, 0, 255)
DARK_BLUE: Color = (10, 10, 90)
RED: Color = (255, 0, 0)
PINK: Color = (255, 128, 233)
ORANGE: Color = (255, 128, 0)

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
    N = auto()


_KEY_MAP: dict[int, Key] = {
    pygame.K_UP: Key.UP,
    pygame.K_DOWN: Key.DOWN,
    pygame.K_LEFT: Key.LEFT,
    pygame.K_RIGHT: Key.RIGHT,
    pygame.K_RETURN: Key.ENTER,
    pygame.K_ESCAPE: Key.ESCAPE,
    pygame.K_n: Key.N
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

    def load_image(self, path: str | Path):
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
        surface = self._font(size).render(text, False, color)
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

    def new_image(self, width: int, height: int, color: Color):
        image = pygame.Surface((width, height))
        image.fill(color)
        return image

    def pixel_put(self, x: int, y: int, color: Color, surface: pygame.Surface | None = None) -> None:
        target = self._surface if surface is None else surface
        if 0 <= x < target.get_width() and 0 <= y < target.get_height():
            target.set_at((x, y), color)

    def draw_rect(self, x: int, y: int, w: int, h: int, color: Color, surface: pygame.Surface | None = None) -> None:
        target = self._surface if surface is None else surface
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, target.get_width())
        y1 = min(y + h, target.get_height())
        for py in range(y0, y1):
            for px in range(x0, x1):
                target.set_at((px, py), color)

    def draw_rounded_rect(
        self, x: int, y: int, w: int, h: int, radius: int, color: Color, surface: pygame.Surface | None = None
    ) -> None:
        if w <= 0 or h <= 0:
            return

        r = max(0, min(radius, w // 2, h // 2))

        if r == 0:
            self.draw_rect(x, y, w, h, color, surface)
            return

        self.draw_rect(x + r, y, w - 2 * r, h, color, surface)

        self.draw_rect(x, y + r, r, h - 2 * r, color, surface)
        self.draw_rect(x + w - r, y + r, r, h - 2 * r, color, surface)

        tl_cx, tl_cy = x + r, y + r
        tr_cx, tr_cy = x + w - r - 1, y + r
        bl_cx, bl_cy = x + r, y + h - r - 1
        br_cx, br_cy = x + w - r - 1, y + h - r - 1

        for dy in range(r + 1):
            dx_max = int(math.sqrt(r * r - dy * dy))
            for dx in range(dx_max + 1):
                self.pixel_put(tl_cx - dx, tl_cy - dy, color, surface)
                self.pixel_put(tr_cx + dx, tr_cy - dy, color, surface)
                self.pixel_put(bl_cx - dx, bl_cy + dy, color, surface)
                self.pixel_put(br_cx + dx, br_cy + dy, color, surface)

    def draw_rounded_rect_outline(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        radius: int,
        color: Color,
        thickness: int = 1,
        surface: pygame.Surface | None = None,
    ) -> None:
        if w <= 0 or h <= 0 or thickness <= 0:
            return

        r = max(0, min(radius, w // 2, h // 2))

        self.draw_rect(x + r, y, w - 2 * r, thickness, color, surface)
        self.draw_rect(x + r, y + h - thickness, w - 2 * r, thickness, color, surface)
        self.draw_rect(x, y + r, thickness, h - 2 * r, color, surface)
        self.draw_rect(x + w - thickness, y + r, thickness, h - 2 * r, color, surface)

        if r == 0:
            return

        tl_cx, tl_cy = x + r, y + r
        tr_cx, tr_cy = x + w - r - 1, y + r
        bl_cx, bl_cy = x + r, y + h - r - 1
        br_cx, br_cy = x + w - r - 1, y + h - r - 1

        for curr_r in range(r, r - thickness, -1):
            if curr_r < 0:
                break
            cx_off = 0
            cy_off = curr_r
            d = 1 - curr_r
            while cx_off <= cy_off:
                self.pixel_put(tl_cx - cx_off, tl_cy - cy_off, color, surface)
                self.pixel_put(tl_cx - cy_off, tl_cy - cx_off, color, surface)
                self.pixel_put(tr_cx + cx_off, tr_cy - cy_off, color, surface)
                self.pixel_put(tr_cx + cy_off, tr_cy - cx_off, color, surface)
                self.pixel_put(bl_cx - cx_off, bl_cy + cy_off, color, surface)
                self.pixel_put(bl_cx - cy_off, bl_cy + cx_off, color, surface)
                self.pixel_put(br_cx + cx_off, br_cy + cy_off, color, surface)
                self.pixel_put(br_cx + cy_off, br_cy + cx_off, color, surface)

                cx_off += 1
                if d < 0:
                    d += 2 * cx_off + 1
                else:
                    cy_off -= 1
                    d += 2 * (cx_off - cy_off) + 1

    def text_at(self, text: str, x: int, y: int, size: int, color: Color):
        """Équivalent direct de Window.string_put dans core.py."""
        surface = self._font(size).render(text, False, color)
        self._surface.blit(surface, (x, y))

    def text_centered_in_rect(self, text: str, rect_x: int, rect_w: int, y: int, size: int, color: Color):
        """Centre un texte horizontalement à l'intérieur d'un segment [rect_x, rect_x + rect_w]."""
        surface = self._font(size).render(text, False, color)
        x = rect_x + (rect_w - surface.get_width()) // 2
        self._surface.blit(surface, (x, y))
