from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from mazegenerator import MazeGenerator

NORTH_BIT = 1
EAST_BIT = 2
SOUTH_BIT = 4
WEST_BIT = 8
ALL_WALLS = NORTH_BIT | EAST_BIT | SOUTH_BIT | WEST_BIT


class Direction(Enum):

    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    @property
    def opposite(self) -> Direction:
        return Direction((-self.dx, -self.dy))


@dataclass
class Cell:

    north: bool
    east: bool
    south: bool
    west: bool
    pacgum: bool = False
    super_pacgum: bool = False

    @classmethod
    def from_value(cls, value: int) -> Cell:
        return cls(
            north=bool(value & NORTH_BIT),
            east=bool(value & EAST_BIT),
            south=bool(value & SOUTH_BIT),
            west=bool(value & WEST_BIT),
        )

    @cached_property
    def is_closed(self) -> bool:
        return self.north and self.east and self.south and self.west

    @cached_property
    def is_intersection(self) -> bool:
        return (not self.north or not self.south) and (not self.east or not self.west)

    @cached_property
    def is_dead_end(self) -> bool:
        return True if sum([self.north, self.east, self.south, self.west]) == 3 else False

    def has_wall(self, direction: Direction) -> bool:
        walls = {
            Direction.UP: self.north,
            Direction.RIGHT: self.east,
            Direction.DOWN: self.south,
            Direction.LEFT: self.west,
        }
        return walls[direction]


class Map:

    def __init__(self, width: int, height: int, seed: int) -> None:
        maze = MazeGenerator(size=(width, height), perfect=False, seed=seed).maze
        self.width: int = len(maze[0])
        self.height: int = len(maze)
        self.cells: list[list[Cell]] = [[Cell.from_value(value) for value in row] for row in maze]
        self._place_pacgums()

    def corners(self) -> list[tuple[int, int]]:
        right, bottom = self.width - 1, self.height - 1
        return [(0, 0), (right, 0), (0, bottom), (right, bottom)]

    def spawn_cell(self) -> tuple[int, int]:
        cx, cy = self.width // 2, self.height // 2
        open_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.cells[y][x].is_closed:
                    open_cells.append((x, y))
        return min(open_cells, key=lambda pos: (abs(pos[0] - cx) + abs(pos[1] - cy), pos[1], pos[0]))

    def _place_pacgums(self) -> None:
        for row in self.cells:
            for cell in row:
                cell.pacgum = not cell.is_closed
        for x, y in self.corners():
            self.cells[y][x].pacgum = False
            self.cells[y][x].super_pacgum = True
        sx, sy = self.spawn_cell()
        self.cells[sy][sx].pacgum = False

    def count_pacgums(self) -> int:
        return sum(cell.pacgum or cell.super_pacgum
                   for row in self.cells for cell in row)

    def can_move(self, x: int, y: int, direction: Direction) -> bool:
        if self.cells[y][x].has_wall(direction):
            return False
        nx, ny = x + direction.dx, y + direction.dy
        return 0 <= nx < self.width and 0 <= ny < self.height# Pourquoi faire ? Remplacer par un return True
