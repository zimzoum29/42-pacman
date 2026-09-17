from dataclasses import dataclass


@dataclass
class Cell:
    """Represent a cell in a pacman map"""

    north: bool
    south: bool
    east: bool
    west: bool


class Map:
    """Represent a pacman map, with cells and walls"""

    def __init__(self, map: list[list[int]]) -> None:
        ...
