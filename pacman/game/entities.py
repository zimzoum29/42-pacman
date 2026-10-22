import random
from typing import Optional

from .maze import Direction, Map


class Entity:

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

    def _choose_direction(self, maze: Map) -> None:
        raise NotImplementedError


class Pacman(Entity):

    def __init__(self, x: int, y: int, speed: float) -> None:
        super().__init__(x, y, speed)
        self.wanted: Optional[Direction] = None

    def place(self, x: int, y: int) -> None:
        super().place(x, y)
        self.wanted = None

    def update(self, dt: float, maze: Map) -> list[tuple[int, int]]:
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


class Ghost(Entity):

    def __init__(self, x: int, y: int, speed: float, rng: random.Random) -> None:
        super().__init__(x, y, speed)
        self.home = (x, y)
        self.respawn_time = 0.0
        self._rng = rng

    @property
    def is_active(self) -> bool:
        return self.respawn_time <= 0.0

    def go_home(self) -> None:
        self.place(*self.home)

    def _choose_direction(self, maze: Map) -> None:
        options = [d for d in Direction if maze.can_move(self.x, self.y, d)]
        if self.direction is not None and len(options) > 1:
            options = [d for d in options if d is not self.direction.opposite]
        self.direction = self._rng.choice(options) if options else None