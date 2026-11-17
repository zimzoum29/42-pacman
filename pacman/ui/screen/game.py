import time

import pygame

from ...config import Config
from ...game.game import Game, Status
from ...game.maze import Direction
from ..button import Action
from ..window import BLACK, WHITE, Color, Key, Window
from ...path import ASSET_DIR

HUD_HEIGHT = 0.05
HUD_FONT_SIZE = 36
MARGIN = 0.03
MAX_DT = 0.1

YELLOW: Color = (255, 255, 0)
WALL_COLOR: Color = (33, 33, 222)
BLOCK_COLOR: Color = (20, 20, 120)
GHOST_COLOR: Color = (255, 0, 0)
FRIGHTENED_COLOR: Color = (60, 60, 255)

KEY_DIRECTIONS: dict[Key, Direction] = {
    Key.UP: Direction.UP,
    Key.DOWN: Direction.DOWN,
    Key.LEFT: Direction.LEFT,
    Key.RIGHT: Direction.RIGHT,
}

CELL_SIZE = 76
WALL_THICKNESS = 10
FLOOR_PATH = ASSET_DIR / "floor.png"
WALL_H_PATH = ASSET_DIR / "wall_h.png"
WALL_V_PATH = ASSET_DIR / "wall_v.png"
BLOCK_PATH = ASSET_DIR / "block.png"
BLINKY_PATH = ASSET_DIR / "blinky.png"
CLYDE_PATH = ASSET_DIR / "clyde.png"
PINKY_PATH = ASSET_DIR / "pinky.png"
INKY_PATH = ASSET_DIR / "inky.png"
FRIGHTENED_GHOST_PATH = ASSET_DIR / "frightened_ghost.png"
FRIGHTENED_WHITE_PATH = ASSET_DIR / "frightened_ghost_white.png"
BLINK_START = 3.0
BLINK_PERIOD = 0.25

DIRECTION_NAMES: dict[Direction, str] = {
    Direction.UP: "up",
    Direction.DOWN: "down",
    Direction.LEFT: "left",
    Direction.RIGHT: "right",
}

ARROW_GAP = 2


class GameScreen:

    def __init__(self, window: Window, config: Config) -> None:
        self._window = window
        self._game = Game(config)
        self._last_time = time.monotonic()
        self._floor_img = window.load_image(FLOOR_PATH)
        self._wall_h_img = window.load_image(WALL_H_PATH)
        self._wall_v_img = window.load_image(WALL_V_PATH)
        self._block_img = window.load_image(BLOCK_PATH)
        self._ghost_imgs: dict[str, str] = {
            "pinky": window.load_image(PINKY_PATH),
            "inky": window.load_image(INKY_PATH),
            "blinky": window.load_image(BLINKY_PATH),
            "clyde": window.load_image(CLYDE_PATH),
        }
        self._frightened_img = window.load_image(FRIGHTENED_GHOST_PATH)
        self._frightened_white_img = window.load_image(FRIGHTENED_WHITE_PATH)
        self._pacman_imgs = {
            d: window.load_image(ASSET_DIR / f"pacman_{name}.png")
            for d, name in DIRECTION_NAMES.items()
        }
        self._arrow_imgs = {
            d: window.load_image(ASSET_DIR / f"arrow_{name}.png")
            for d, name in DIRECTION_NAMES.items()
        }
        self._pause_overlay = window.create_dither_overlay()
        self._load_level()

    def _load_level(self) -> None:
        self._level = self._game.level
        self._map = self._game.map
        self._compute_layout()
        self._floors = self._build_floors()
        self._walls = self._build_walls()
        self._build_images()

    def _compute_layout(self) -> None:
        window = self._window
        margin = window.ratio_y(MARGIN)
        top = window.ratio_y(HUD_HEIGHT)
        free_w = window.width - 2 * margin
        free_h = window.height - top - margin
        self._cell = min(free_w // self._map.width, free_h // self._map.height)
        self._thick = max(self._cell // 8, 2)
        map_w = self._cell * self._map.width
        map_h = self._cell * self._map.height
        self._origin_x = (window.width - map_w) // 2
        self._origin_y = top + (free_h - map_h) // 2
        self._cell = CELL_SIZE
        self._thick = WALL_THICKNESS

    def _build_walls(self) -> list[tuple[pygame.Surface, int, int]]:
        size = self._cell
        half = self._thick // 2
        h_wall, v_wall = self._wall_h_img, self._wall_v_img

        walls: list[tuple[pygame.Surface, int, int]] = []
        blocks: list[tuple[pygame.Surface, int, int]] = []
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                px, py = self.cell_to_pixel(x, y)
                if cell.is_closed:
                    if self._block_img is not None:
                        blocks.append((self._block_img, px, py))
                    continue
                if h_wall is not None:
                    if cell.north:
                        walls.append((h_wall, px - half, py - half))
                    if cell.south:
                        walls.append((h_wall, px - half, py + size - half))
                if v_wall is not None:
                    if cell.west:
                        walls.append((v_wall, px - half, py - half))
                    if cell.east:
                        walls.append((v_wall, px + size - half, py - half))
        return walls + blocks

    def _build_images(self) -> None:
        cell = self._cell
        self._pacgum_size = max(cell // 6, 2)
        self._super_size = max(cell // 3, 4)
        self._entity_size = cell // 2
        new = self._window.new_image
        self._pacgum_img = new(self._pacgum_size, self._pacgum_size, YELLOW)
        self._super_img = new(self._super_size, self._super_size, YELLOW)
        size = self._entity_size

    def cell_to_pixel(self, x: int, y: int) -> tuple[int, int]:
        return (self._origin_x + x * self._cell,
                self._origin_y + y * self._cell)

    def update(self, keys: list[Key]) -> Action | None:
        for key in keys:
            if key is Key.QUIT:
                return Action.QUIT
            if key is Key.ESCAPE:
                return Action.HOME
            if key in KEY_DIRECTIONS:
                self._game.set_direction(KEY_DIRECTIONS[key])
            elif key is Key.PAUSE:
                self._game.switch_pause()

        now = time.monotonic()
        dt = min(now - self._last_time, MAX_DT)
        self._last_time = now
        self._game.update(dt)

        if self._game.status in [Status.GAME_OVER, Status.VICTORY]:
            return Action.HOME
        if self._game.level != self._level:
            self._load_level()
        return None

    def draw(self) -> None:
        self._window.fill(BLACK)
        if self._floor_img is not None:
            for x, y in self._floors:
                self._window.blit(self._floor_img, x, y)
        for image, x, y in self._walls:
            self._window.blit(image, x, y)
        self._draw_pacgums()
        self._draw_ghosts()
        self._draw_pacman()

        if self._game.status is Status.PAUSE:
            self._window.blit(self._pause_overlay, 0, 0)
            self._window.text_centered("PAUSE", self._window.height // 2, 72, WHITE)

    def _draw_pacgums(self) -> None:
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                if cell.pacgum:
                    self._draw_centered(self._pacgum_img, self._pacgum_size, x, y)
                elif cell.super_pacgum:
                    self._draw_centered(self._super_img, self._super_size, x, y)

    def _draw_ghosts(self) -> None:
        frightened_img = self._frightened_image()
        for ghost in self._game.ghosts:
            if not ghost.is_active:
                continue
            image = (frightened_img if ghost.frightened
                     else self._ghost_imgs[ghost.name])
            if image is not None:
                gx, gy = ghost.position
                self._blit_center(image, *self._cell_center(gx, gy))

    def _draw_centered(self, image: pygame.Surface, size: int,x: float, y: float) -> None:
        offset = (self._cell - size) // 2
        px = self._origin_x + x * self._cell + offset
        py = self._origin_y + y * self._cell + offset
        self._window.blit(image, int(px), int(py))

    def _build_floors(self) -> list[tuple[int, int]]:
        floors: list[tuple[int, int]] = []
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                if not cell.is_closed:
                    floors.append(self.cell_to_pixel(x, y))
        return floors

    def _draw_pacman(self) -> None:
        pacman = self._game.pacman
        facing = pacman.direction or pacman.last_direction
        cx, cy = self._cell_center(*pacman.position)

        sprite = self._pacman_imgs[facing]
        if sprite is not None:
            self._blit_center(sprite, cx, cy)

        wanted = pacman.wanted or facing
        arrow = self._arrow_imgs[wanted]
        if arrow is None:
            return
        reach_x = (sprite.get_width() if sprite else 0) // 2
        reach_y = (sprite.get_height() if sprite else 0) // 2
        dist_x = reach_x + arrow.get_width() // 2 + ARROW_GAP
        dist_y = reach_y + arrow.get_height() // 2 + ARROW_GAP
        self._blit_center(arrow, cx + wanted.dx * dist_x, cy + wanted.dy * dist_y)

    def _cell_center(self, x: float, y: float) -> tuple[float, float]:
        return (self._origin_x + (x + 0.5) * self._cell,
                self._origin_y + (y + 0.5) * self._cell)

    def _blit_center(self, image: pygame.Surface, cx: float, cy: float) -> None:
        self._window.blit(image, int(cx - image.get_width() / 2), int(cy - image.get_height() / 2))

    def _frightened_image(self) -> pygame.Surface:
        time_left = self._game.frightened_time
        if time_left > BLINK_START:
            return self._frightened_img
        blink_step = int(time_left / BLINK_PERIOD)
        if blink_step % 2 == 0:
            return self._frightened_white_img
        return self._frightened_img