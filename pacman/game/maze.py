from dataclasses import dataclass
from enum import Enum

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


@dataclass
class Cell:

    north: bool
    east: bool
    south: bool
    west: bool

    @classmethod
    def from_value(cls, value: int) -> "Cell":
        return cls(
            north=bool(value & NORTH_BIT),
            east=bool(value & EAST_BIT),
            south=bool(value & SOUTH_BIT),
            west=bool(value & WEST_BIT),
        )

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
