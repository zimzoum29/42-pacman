import pygame

from ...game.maze import Map
from ...game.game import Game
from ..button import Action
from ..window import BLACK, Color, Key, Window
from ...config import Config
from ...game.entities import Entities

MAP_WIDTH = 20
MAP_HEIGHT = 15

HUD_HEIGHT = 0.03
MARGIN = 0.03

WALL_COLOR: Color = (33, 33, 222)
BLOCK_COLOR: Color = (20, 20, 120)

GHOST_COORD = [(0, 0), (0, MAP_WIDTH - 1), (MAP_HEIGHT - 1, 0), (MAP_HEIGHT - 1, MAP_WIDTH - 1)]


class GameScreen:

    def __init__(self, window: Window, config: Config) -> None:
        self._window = window
        self._config = config
        self._map = Map(MAP_WIDTH, MAP_HEIGHT, self._config.seed)
        self._game = Game(self._map, self._config)
        self._compute_layout()
        self._walls = self._build_walls()
        self._ghosts = [Entities(x, y) for x, y in GHOST_COORD]

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

    def _build_walls(self) -> list[tuple[pygame.Surface, int, int]]:
        size, thick = self._cell, self._thick
        h_wall = self._window.new_image(size + thick, thick, WALL_COLOR)
        v_wall = self._window.new_image(thick, size + thick, WALL_COLOR)
        block = self._window.new_image(size, size, BLOCK_COLOR)

        walls: list[tuple[pygame.Surface, int, int]] = []
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                px, py = self.cell_to_pixel(x, y)
                if cell.north and cell.east and cell.south and cell.west:
                    walls.append((block, px, py))
                if cell.north:
                    walls.append((h_wall, px, py))
                if cell.west:
                    walls.append((v_wall, px, py))
                if cell.south and y == self._map.height - 1:
                    walls.append((h_wall, px, py + size))
                if cell.east and x == self._map.width - 1:
                    walls.append((v_wall, px + size, py))
        return walls

    def _draw_entities(self) -> list[Entities]:
        for ghost in self.ghosts: 
            ...


    def cell_to_pixel(self, x: int, y: int) -> tuple[int, int]:
        return (self._origin_x + x * self._cell,
                self._origin_y + y * self._cell)

    def update(self, keys: list[Key]) -> Action | None:
        for key in keys:
            if key is Key.QUIT:
                return Action.QUIT
            if key is Key.ESCAPE:
                return Action.HOME
        return None

    def draw(self) -> None:
        self._window.fill(BLACK)
        for image, x, y in self._walls:
            self._window.blit(image, x, y)