import random
import math
from typing import Optional, Callable
from enum import Enum, auto
from abc import ABC, abstractmethod

from .maze import Direction, Map


class Entity(ABC):

    def __init__(self, x: int, y: int, speed: float) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.direction: Optional[Direction] = None
        self.progress = 0.0

    @property
    def position(self) -> tuple[float, float]:
        if self.direction is None:
            return float(self.x), float(self.y)
        return (self.x + self.direction.dx * self.progress,
                self.y + self.direction.dy * self.progress)

    def place(self, x: int, y: int) -> None:
        self.x, self.y = x, y
        self.direction = None
        self.progress = 0.0

    def update(self, dt: float, maze: Map) -> list[tuple[int, int]]:
        reached: list[tuple[int, int]] = []
        if self.direction is None:
            self._choose_direction(maze)
        while self.direction is not None:
            self.progress += self.speed * dt
            if self.progress < 1.0:
                break
            dt = (self.progress - 1.0) / self.speed
            self.x += self.direction.dx
            self.y += self.direction.dy
            self.progress = 0.0
            reached.append((self.x, self.y))
            self._choose_direction(maze)
        return reached

    @abstractmethod
    def _choose_direction(self, maze: Map) -> None:
        pass


class Pacman(Entity):

    def __init__(self, x: int, y: int, speed: float) -> None:
        super().__init__(x, y, speed)
        self.last_direction = Direction.UP
        self.wanted: Optional[Direction] = None

    def place(self, x: int, y: int) -> None:
        super().place(x, y)
        self.wanted = None

    def update(self, dt: float, maze: Map) -> list[tuple[int, int]]:
        if self.direction and self.direction != self.last_direction:
            self.last_direction = self.direction
        if (self.direction is not None and self.wanted is not None and self.wanted is self.direction.opposite and self.progress > 0.0):
            self.x += self.direction.dx
            self.y += self.direction.dy
            self.progress = 1.0 - self.progress
            self.direction = self.wanted
        return super().update(dt, maze)

    def _choose_direction(self, maze: Map) -> None:
        if self.wanted is not None and maze.can_move(self.x, self.y, self.wanted):
            self.direction = self.wanted
        elif self.direction is not None and not maze.can_move(self.x, self.y, self.direction):
            self.direction = None


class GhostMode(Enum):
    CHASE = auto()
    SCATTER = auto()
    FRIGHTENED = auto()


class Ghost(Entity, ABC):

    def __init__(self,
                 x: int,
                 y: int,
                 speed: float,
                 rng: random.Random,
                 pacman: Pacman,
                 ) -> None:
        super().__init__(x, y, speed)
        self.home = (x, y)
        self.mode = GhostMode.CHASE
        self.direction_function: Callable = self._chase
        self.respawn_time = 0.0
        self._rng = rng
        self.pacman = pacman

    @property
    def is_active(self) -> bool:
        return self.respawn_time <= 0.0

    def go_home(self) -> None:
        self.place(*self.home)

    def set_mode(self, mode: GhostMode) -> None:
        if mode is self.mode:
            return
        if mode is GhostMode.FRIGHTENED:
            self._turn_back()
        self.mode = mode
        self.direction_function = {
            GhostMode.CHASE: self._chase,
            GhostMode.SCATTER: self._scatter,
            GhostMode.FRIGHTENED: self._frightened,
        }[mode]

    def _turn_back(self) -> None:
        if self.direction is None or self.progress == 0.0:
            return
        self.x += self.direction.dx
        self.y += self.direction.dy
        self.progress = 1.0 - self.progress
        self.direction = self.direction.opposite

    def _choose_direction(self, maze: Map) -> None:
        if self.direction is None:
            options = [d for d in Direction if maze.can_move(self.x, self.y, d)]
            self.direction = self._rng.choice(options) if options else None

        elif maze.cells[self.y][self.x].is_dead_end:
            self.direction = self.direction.opposite

        elif maze.cells[self.y][self.x].is_intersection:
            self.direction_function(maze)

    @abstractmethod
    def _chase(self, maze: Map) -> None:
        pass

    def _scatter(self, maze: Map) -> None:
        self._head_towards_position(maze, self.home)

    def _frightened(self, maze: Map) -> None:
        if self.direction:
            options = [d for d in Direction if maze.can_move(self.x, self.y, d)
                       and d is not self.direction.opposite]

            self.direction = self._rng.choice(options)

    def _head_towards_position(self, maze: Map, position: tuple[int | float, int | float]) -> None:
        if self.direction:
            options = [d for d in Direction if maze.can_move(self.x, self.y, d)
                       and d is not self.direction.opposite]

            distances = [self._distance((self.position[0] + option.dx, self.position[1] + option.dy), position) for option in options]

            self.direction = options[distances.index(min(distances))]

    @staticmethod
    def _distance(a: tuple[int | float, int | float],
                  b: tuple[int | float, int | float]) -> int | float:
        x_a, y_a = a
        x_b, y_b = b
        return math.sqrt((x_b - x_a)**2 + (y_b - y_a)**2)


class Blinky(Ghost):

    def __init__(self,
                 x: int,
                 y: int,
                 speed: float,
                 rng: random.Random,
                 pacman: Pacman
                 ) -> None:
        super().__init__(x, y, speed, rng, pacman)

    def _chase(self, maze: Map) -> None:
        self._head_towards_position(maze, self.pacman.position)


class Pinky(Ghost):

    def __init__(self,
                 x: int,
                 y: int,
                 speed: float,
                 rng: random.Random,
                 pacman: Pacman
                 ) -> None:
        super().__init__(x, y, speed, rng, pacman)

    def _chase(self, maze: Map) -> None:
        self._head_towards_position(
            maze, self._four_tiles_ahead_pacman(self.pacman)
        )

    @staticmethod
    def _four_tiles_ahead_pacman(pacman: Pacman) -> tuple[int, int]:
        if pacman.direction:
            c_direction = pacman.direction
        else:
            c_direction = pacman.last_direction

        match c_direction:
            case Direction.UP:
                return (pacman.x - 4, pacman.y - 4)
            case _:
                return (pacman.x + c_direction.value[0] * 4,
                        pacman.y + c_direction.value[1] * 4)


class Inky(Ghost):

    def __init__(self,
                 x: int,
                 y: int,
                 speed: float,
                 rng: random.Random,
                 pacman: Pacman,
                 blinky: Blinky
                 ) -> None:
        self.blinky = blinky
        super().__init__(x, y, speed, rng, pacman)

    def _chase(self, maze: Map) -> None:
        plus_two = self._two_tiles_ahead_pacman(self.pacman)
        v_blinky = (
            plus_two[0] - self.blinky.x,
            plus_two[1] - self.blinky.y
        )
        to_target = (
            plus_two[0] + v_blinky[0],
            plus_two[1] + v_blinky[1]
        )
        self._head_towards_position(maze, to_target)

    @staticmethod
    def _two_tiles_ahead_pacman(pacman: Pacman) -> tuple[int, int]:
        if pacman.direction:
            c_direction = pacman.direction
        else:
            c_direction = pacman.last_direction

        return (pacman.x + c_direction.value[0] * 2,
                pacman.y + c_direction.value[1] * 2)


class Clyde(Ghost):

    def __init__(self,
                 x: int,
                 y: int,
                 speed: float,
                 rng: random.Random,
                 pacman: Pacman
                 ) -> None:
        super().__init__(x, y, speed, rng, pacman)

    def _chase(self, maze: Map) -> None:
        if self._distance(self.position, self.pacman.position) > 8.0:
            self._head_towards_position(maze, self.pacman.position)
        else:
            self._scatter(maze)
