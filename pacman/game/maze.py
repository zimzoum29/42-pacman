from dataclasses import dataclass
from enum import Enum

from mazegenerator import MazeGenerator

NORTH_BIT = 1
EAST_BIT = 2
SOUTH_BIT = 4
WEST_BIT = 8
ALL_WALLS = NORTH_BIT | EAST_BIT | SOUTH_BIT | WEST_BIT
SUPER_PACGUM_COORD = [(0,1),(1,0),(0,0),(1,1)]


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

    @property
    def is_closed(self) -> bool:
        return self.north and self.east and self.south and self.west


class Map:

    def __init__(self, width: int, height: int, seed: int) -> None:
        maze = MazeGenerator(size=(width, height), perfect=False, seed=seed).maze
        self.width: int = len(maze[0])
        self.height: int = len(maze)
        self.cells: list[list[Cell]] = [[Cell.from_value(value) for value in row] for row in maze]
        self._place_pacgum()

    def _place_pacgum(self):
        for line in self.cells:
            for cell in line:
                cell.pacgum = False if cell.is_closed else True
        for x, y in SUPER_PACGUM_COORD:
            self.cells[x][y].pacgum = False
            self.cells[x][y].super_pacgum = True


