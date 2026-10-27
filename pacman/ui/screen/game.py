import time

import pygame

from ...config import Config
from ...game.game import Game, Status
from ...game.maze import Direction
from ..button import Action
from ..window import BLACK, WHITE, YELLOW, Color, Key, Window
from ...path import ASSET_DIR

HUD_HEIGHT = 0.05
HUD_FONT_SIZE = 36
MARGIN = 0.03
MAX_DT = 0.1

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

CELL_SIZE = 60
WALL_THICKNESS = 8
FLOOR_PATH = ASSET_DIR / "floor.png"
WALL_H_PATH = ASSET_DIR / "wall_h.png"
WALL_V_PATH = ASSET_DIR / "wall_v.png"
BLOCK_PATH = ASSET_DIR / "block.png"


class GameScreen:

    def __init__(self, window: Window, config: Config) -> None:
        self._window = window
        self._game = Game(config)
        self._last_time = time.monotonic()
        self._floor_img = window.load_image(FLOOR_PATH)
        self._wall_h_img = window.load_image(WALL_H_PATH)
        self._wall_v_img = window.load_image(WALL_V_PATH)
        self._block_img = window.load_image(BLOCK_PATH)
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
        last_x, last_y = self._map.width - 1, self._map.height - 1

        walls: list[tuple[pygame.Surface, int, int]] = []
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                px, py = self.cell_to_pixel(x, y)
                if cell.is_closed and self._block_img is not None:
                    walls.append((self._block_img, px, py))
                else:
                    if h_wall is not None:
                        if cell.north or self._map.cells[y - 1][x].is_closed:
                            walls.append((h_wall, px - half, py - half))
                        if (cell.south and y == last_y) or (y + 1 < last_y and self._map.cells[y + 1][x].is_closed):
                            walls.append((h_wall, px - half, py + size - half))
                    if v_wall is not None:
                        if cell.west or self._map.cells[y][x - 1].is_closed:
                            walls.append((v_wall, px - half, py - half))
                        if (cell.east and x == last_x) or (x + 1 < last_x and self._map.cells[y][x + 1].is_closed):
                            walls.append((v_wall, px + size - half, py - half))

        return walls

    def _build_images(self) -> None:
        cell = self._cell
        self._pacgum_size = max(cell // 6, 2)
        self._super_size = max(cell // 3, 4)
        self._entity_size = cell // 2
        new = self._window.new_image
        self._pacgum_img = new(self._pacgum_size, self._pacgum_size, WHITE)
        self._super_img = new(self._super_size, self._super_size, WHITE)
        size = self._entity_size
        self._pacman_img = new(size, size, YELLOW)
        self._ghost_img = new(size, size, GHOST_COLOR)
        self._frightened_img = new(size, size, FRIGHTENED_COLOR)

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

        now = time.monotonic()
        dt = min(now - self._last_time, MAX_DT)
        self._last_time = now
        self._game.update(dt)

        if self._game.status is not Status.PLAYING:
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
        px, py = self._game.pacman.position
        self._draw_centered(self._pacman_img, self._entity_size, px, py)

    def _draw_pacgums(self) -> None:
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                if cell.pacgum:
                    self._draw_centered(self._pacgum_img, self._pacgum_size, x, y)
                elif cell.super_pacgum:
                    self._draw_centered(self._super_img, self._super_size, x, y)

    def _draw_ghosts(self) -> None:
        frightened = self._game.frightened_time > 0
        image = self._frightened_img if frightened else self._ghost_img
        for ghost in self._game.ghosts:
            if ghost.is_active:
                gx, gy = ghost.position
                self._draw_centered(image, self._entity_size, gx, gy)

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